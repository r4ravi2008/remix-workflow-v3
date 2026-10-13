use std::sync::{
    Arc, Mutex,
    atomic::{AtomicBool, Ordering},
};
use std::thread::JoinHandle;

use super::*;
use crate::composition::{
    self, Budget, LayerObservation, Permit, PictureExecutionEvidence, Raster,
};
use crate::{ContentHash, EntityId, MediaTime, VideoUse};

#[derive(Clone)]
struct Signal {
    control: crate::exports::ExportControl,
    stopped: Arc<AtomicBool>,
    deadline: Instant,
}
impl Signal {
    fn check(&self) -> Result<()> {
        self.control.check()?;
        if self.stopped.load(Ordering::Acquire) {
            return Err(error("Picture pipeline stopped by its owner"));
        }
        if Instant::now() > self.deadline {
            return Err(error("Picture pipeline deadline expired"));
        }
        Ok(())
    }
}
struct LayerFrame {
    frame: u64,
    clip: EntityId,
    asset: ContentHash,
    ordinal: u64,
    pts: Option<MediaTime>,
    observation: LayerObservation,
    sampled: SampledLayer,
}
enum SampledLayer {
    NoGeometry,
    ZeroAlpha {
        bounds: composition::Bounds,
    },
    LegacyOpaque {
        raster: Raster,
        _permit: Permit,
    },
    AlphaV1 {
        raster: crate::alpha_picture::AlphaRaster16,
        _permit: Permit,
    },
}
impl SampledLayer {
    fn bounds(&self) -> Option<&composition::Bounds> {
        match self {
            Self::NoGeometry => None,
            Self::ZeroAlpha { bounds } => Some(bounds),
            Self::LegacyOpaque { raster, .. } => Some(&raster.bounds),
            Self::AlphaV1 { raster, .. } => Some(&raster.bounds),
        }
    }
}
enum Decision {
    Gap(u64),
    Source(Box<LayerFrame>),
}
struct Port {
    track: EntityId,
    uses: Vec<usize>,
    cursor: usize,
    requests: Option<mpsc::SyncSender<u64>>,
    responses: Option<mpsc::Receiver<Result<Decision>>>,
    worker: Option<JoinHandle<Result<()>>>,
}
struct Workers {
    ports: Vec<Port>,
    signal: Signal,
}
impl Workers {
    fn finish(&mut self) -> Result<()> {
        for port in &mut self.ports {
            port.requests.take();
            port.responses.take();
        }
        let mut first = None;
        for port in &mut self.ports {
            if let Some(worker) = port.worker.take() {
                let result = worker
                    .join()
                    .map_err(|_| error("Picture track worker panicked"))
                    .and_then(|result| result);
                if first.is_none() {
                    first = result.err();
                }
            }
        }
        first.map_or(Ok(()), Err)
    }
}
impl Drop for Workers {
    fn drop(&mut self) {
        self.signal.stopped.store(true, Ordering::Release);
        for port in &mut self.ports {
            port.requests.take();
            port.responses.take();
        }
        for port in &mut self.ports {
            if let Some(worker) = port.worker.take() {
                let _ = worker.join();
            }
        }
    }
}

fn send<T>(sender: &mpsc::SyncSender<T>, mut value: T, signal: &Signal) -> Result<()> {
    loop {
        signal.check()?;
        match sender.try_send(value) {
            Ok(()) => return Ok(()),
            Err(mpsc::TrySendError::Full(returned)) => value = returned,
            Err(mpsc::TrySendError::Disconnected(_)) => {
                return Err(error("Picture channel consumer closed"));
            }
        }
        std::thread::sleep(Duration::from_millis(1));
    }
}
fn receive<T>(receiver: &mpsc::Receiver<T>, signal: &Signal) -> Result<T> {
    loop {
        signal.check()?;
        match receiver.recv_timeout(Duration::from_millis(25)) {
            Ok(value) => return Ok(value),
            Err(mpsc::RecvTimeoutError::Timeout) => {}
            Err(mpsc::RecvTimeoutError::Disconnected) => {
                return Err(error("Picture channel producer closed"));
            }
        }
    }
}
fn request(receiver: &mpsc::Receiver<u64>, expected: u64, signal: &Signal) -> Result<()> {
    if receive(receiver, signal)? != expected {
        return Err(error("Picture request differs from timeline order"));
    }
    Ok(())
}
fn png_lock<'a>(mutex: &'a Mutex<()>, signal: &Signal) -> Result<std::sync::MutexGuard<'a, ()>> {
    loop {
        signal.check()?;
        match mutex.try_lock() {
            Ok(guard) => return Ok(guard),
            Err(std::sync::TryLockError::WouldBlock) => {
                std::thread::sleep(Duration::from_millis(1))
            }
            Err(std::sync::TryLockError::Poisoned(_)) => {
                return Err(error("Serialized PNG decoder lock was poisoned"));
            }
        }
    }
}

enum PictureRef<'a> {
    Opaque(&'a crate::pixels::Pixels),
    Alpha(&'a crate::alpha_picture::StraightRgba8),
}

impl PictureRef<'_> {
    fn width(&self) -> u32 {
        match self {
            Self::Opaque(pixels) => pixels.width,
            Self::Alpha(pixels) => pixels.width(),
        }
    }

    fn height(&self) -> u32 {
        match self {
            Self::Opaque(pixels) => pixels.height,
            Self::Alpha(pixels) => pixels.height(),
        }
    }
}

fn frame(
    use_: &VideoUse,
    local: u64,
    pts: Option<MediaTime>,
    picture: PictureRef<'_>,
    plan: &ExportPlan,
    budget: &Arc<Budget>,
    signal: &Signal,
) -> Result<Decision> {
    signal.check()?;
    let (mapping, observation) =
        composition::evaluate_layer(plan, use_, local, picture.width(), picture.height())?;
    let sampled = match picture {
        PictureRef::Opaque(pixels) => {
            let reserve = observation
                .effective_bounds
                .as_ref()
                .map(|bounds| crate::pixels::extent(bounds.width, bounds.height))
                .transpose()?
                .unwrap_or(0);
            let permit = budget.reserve(reserve as u64)?;
            let raster = if observation.mask.is_some() {
                mapping.rasterize_bounds_cancellable(
                    pixels,
                    observation.effective_bounds.as_ref(),
                    || signal.check(),
                )?
            } else {
                mapping.rasterize_cancellable(pixels, || signal.check())?
            };
            match raster {
                Some(raster) => SampledLayer::LegacyOpaque {
                    raster,
                    _permit: permit,
                },
                None => SampledLayer::NoGeometry,
            }
        }
        PictureRef::Alpha(source) => {
            let reserve = observation
                .effective_bounds
                .as_ref()
                .map(crate::alpha_picture::raster_bytes)
                .transpose()?
                .unwrap_or(0);
            let permit = budget.reserve(reserve)?;
            let raster = crate::alpha_picture::sample_cancellable(
                source,
                &mapping,
                observation.effective_bounds.as_ref(),
                || signal.check(),
            )?;
            match raster {
                None => SampledLayer::NoGeometry,
                Some(raster) if !raster.has_positive_samples() => SampledLayer::ZeroAlpha {
                    bounds: raster.bounds.clone(),
                },
                Some(raster) => SampledLayer::AlphaV1 {
                    raster,
                    _permit: permit,
                },
            }
        }
    };
    Ok(Decision::Source(Box::new(LayerFrame {
        frame: use_.timeline_frames.start + local,
        clip: use_.clip.clone(),
        asset: use_.asset.clone(),
        ordinal: use_.presentation_ordinals[local as usize],
        pts,
        observation,
        sampled,
    })))
}

#[derive(Clone)]
struct Environment {
    plan: Arc<ExportPlan>,
    blobs: std::path::PathBuf,
    signal: Signal,
    budget: Arc<Budget>,
    png_mutex: Arc<Mutex<()>>,
}
fn run_track(
    environment: Environment,
    uses: Vec<usize>,
    mut requests: mpsc::Receiver<u64>,
    responses: mpsc::SyncSender<Result<Decision>>,
) -> Result<()> {
    let Environment {
        plan,
        blobs,
        signal,
        budget,
        png_mutex,
    } = environment;
    let mut cursor = 0;
    let mut timeline_frame = 0;
    while timeline_frame < plan.timeline.frame_count {
        request(&requests, timeline_frame, &signal)?;
        while cursor < uses.len()
            && plan.video[uses[cursor]].timeline_frames.end()? <= timeline_frame
        {
            cursor += 1;
        }
        if cursor == uses.len() || plan.video[uses[cursor]].timeline_frames.start > timeline_frame {
            send(&responses, Ok(Decision::Gap(timeline_frame)), &signal)?;
            timeline_frame += 1;
            continue;
        }
        let use_ = plan.video[uses[cursor]].clone();
        if use_.timeline_frames.start != timeline_frame {
            return Err(error("Track clip did not start at its requested boundary"));
        }
        let asset = &plan.source_closure[&use_.asset];
        let (width, height) = asset.descriptor.picture_extent()?;
        let source_bytes = crate::pixels::extent(width, height)? as u64;
        let path = blobs.join(use_.asset.as_str());
        if matches!(asset.descriptor, MediaDescriptor::Image { .. }) {
            let source_permit = budget.reserve(source_bytes)?;
            let picture = {
                let _lock = png_lock(&png_mutex, &signal)?;
                let temporary = source_bytes
                    .checked_add(asset.bytes)
                    .and_then(|value| value.checked_add(crate::pixels::MAX_OWNED_FRAME_BYTES))
                    .ok_or_else(|| error("PNG reservation overflow"))?;
                let _temporary_permit = budget.reserve(temporary)?;
                crate::image::decode_picture_asset_cancellable(&path, asset, || signal.check())?
            };
            let mut cached = Some((picture, source_permit));
            for local in 0..use_.timeline_frames.length {
                if local != 0 {
                    request(&requests, use_.timeline_frames.start + local, &signal)?;
                }
                let picture = &cached
                    .as_ref()
                    .ok_or_else(|| error("Held image retired before its last frame"))?
                    .0;
                let picture = match picture {
                    crate::alpha_picture::DecodedPicture::LegacyOpaque(pixels) => {
                        PictureRef::Opaque(pixels)
                    }
                    crate::alpha_picture::DecodedPicture::StraightAlpha(pixels) => {
                        PictureRef::Alpha(pixels)
                    }
                };
                let decision = frame(&use_, local, None, picture, &plan, &budget, &signal)?;
                if local + 1 == use_.timeline_frames.length {
                    cached.take();
                }
                send(&responses, Ok(decision), &signal)?;
            }
        } else {
            let callback_plan = plan.clone();
            let callback_signal = signal.clone();
            let callback_responses = responses.clone();
            let callback_budget = budget.clone();
            let wait_signal = signal.clone();
            let end = use_.timeline_frames.end()?;
            requests = media::with_track_cancellable(
                &path,
                &MediaKind::Movie,
                crate::pcm::STREAM_DEADLINE,
                move || wait_signal.check(),
                || {},
                move |track| {
                    let asset =
                        unsafe { track.asset() }.ok_or_else(|| error("Layer track lost asset"))?;
                    let reader = unsafe { AVAssetReader::assetReaderWithAsset_error(&asset) }
                        .map_err(|error_| error(format!("{error_:?}")))?;
                    let _guard = ReaderGuard(&reader);
                    let settings =
                        dictionary(vec![("PixelFormatType", number(kCVPixelFormatType_32BGRA))]);
                    let output = unsafe {
                        AVAssetReaderTrackOutput::assetReaderTrackOutputWithTrack_outputSettings(
                            track,
                            Some(&settings),
                        )
                    };
                    if !unsafe { reader.canAddOutput(&output) } {
                        return Err(error("Layer decoder rejected BGRA"));
                    }
                    unsafe { reader.addOutput(&output) };
                    if !unsafe { reader.startReading() } {
                        return Err(error("Layer decoder did not start"));
                    }
                    let MediaDescriptor::Movie { samples, .. } =
                        &callback_plan.source_closure[&use_.asset].descriptor
                    else {
                        return Err(error("Layer source is not a movie"));
                    };
                    let (mut next, mut current_ordinal, mut current) = (0u64, None, None);
                    for (local, wanted) in use_.presentation_ordinals.iter().copied().enumerate() {
                        if local != 0 {
                            request(
                                &requests,
                                use_.timeline_frames.start + local as u64,
                                &callback_signal,
                            )?;
                        }
                        while current_ordinal != Some(wanted) {
                            callback_signal.check()?;
                            if next > wanted {
                                return Err(error("Layer source cadence is not monotonic"));
                            }
                            let sample =
                                unsafe { output.copyNextSampleBuffer() }.ok_or_else(|| {
                                    error("Layer source ended before selected ordinal")
                                })?;
                            let pts = media::time(unsafe { sample.presentation_time_stamp() })?;
                            let indexed = samples
                                .get(next as usize)
                                .ok_or_else(|| error("Layer decoder exceeded source index"))?;
                            if pts.compare(&indexed.pts) != std::cmp::Ordering::Equal {
                                return Err(error("Layer source PTS differs from immutable index"));
                            }
                            current = Some(sample);
                            current_ordinal = Some(next);
                            next += 1;
                        }
                        let sample = current
                            .as_ref()
                            .ok_or_else(|| error("Layer sample absent"))?;
                        let pts = media::time(unsafe { sample.presentation_time_stamp() })?;
                        let image = unsafe { sample.image_buffer() }
                            .ok_or_else(|| error("Layer sample has no image"))?;
                        if CVPixelBufferGetWidth(&image) != width as usize
                            || CVPixelBufferGetHeight(&image) != height as usize
                        {
                            return Err(error("Layer source dimensions changed"));
                        }
                        let source_permit = callback_budget.reserve(source_bytes)?;
                        let pixels = crate::pixels::Pixels::copy(&image)?;
                        let decision = frame(
                            &use_,
                            local as u64,
                            Some(pts),
                            PictureRef::Opaque(&pixels),
                            &callback_plan,
                            &callback_budget,
                            &callback_signal,
                        )?;
                        drop(pixels);
                        drop(source_permit);
                        send(&callback_responses, Ok(decision), &callback_signal)?;
                    }
                    Ok(requests)
                },
            )?;
            timeline_frame = end;
            continue;
        }
        timeline_frame = use_.timeline_frames.end()?;
    }
    Ok(())
}

fn check_decision<'a>(
    plan: &'a ExportPlan,
    port: &mut Port,
    frame: u64,
    decision: &Decision,
) -> Result<Option<&'a VideoUse>> {
    while port.cursor < port.uses.len()
        && plan.video[port.uses[port.cursor]].timeline_frames.end()? <= frame
    {
        port.cursor += 1;
    }
    let expected = port
        .uses
        .get(port.cursor)
        .map(|index| &plan.video[*index])
        .filter(|use_| use_.timeline_frames.start <= frame);
    match (expected, decision) {
        (None, Decision::Gap(observed)) if *observed == frame => Ok(None),
        (Some(use_), Decision::Source(observed)) => {
            let ordinal = use_.presentation_ordinals[(frame - use_.timeline_frames.start) as usize];
            let expected_pts = match &plan.source_closure[&use_.asset].descriptor {
                MediaDescriptor::Image { .. } => None,
                MediaDescriptor::Movie { samples, .. } => Some(&samples[ordinal as usize].pts),
                MediaDescriptor::Audio { .. } => return Err(error("Layer source is audio")),
            };
            let pts_match = match (&observed.pts, expected_pts) {
                (None, None) => true,
                (Some(a), Some(b)) => a.compare(b) == std::cmp::Ordering::Equal,
                _ => false,
            };
            let (width, height) = plan.source_closure[&use_.asset]
                .descriptor
                .picture_extent()?;
            let (_, expected_observation) = composition::evaluate_layer(
                plan,
                use_,
                frame - use_.timeline_frames.start,
                width,
                height,
            )?;
            if observed.frame != frame
                || observed.clip != use_.clip
                || observed.asset != use_.asset
                || observed.ordinal != ordinal
                || !pts_match
                || observed.observation != expected_observation
                || observed.sampled.bounds() != expected_observation.effective_bounds.as_ref()
            {
                return Err(error(
                    "Layer observation differs from the immutable source map",
                ));
            }
            let alpha_source = matches!(
                &plan.source_closure[&use_.asset].descriptor,
                MediaDescriptor::Image { alpha: Some(_), .. }
            );
            if (alpha_source && matches!(observed.sampled, SampledLayer::LegacyOpaque { .. }))
                || (!alpha_source
                    && matches!(
                        observed.sampled,
                        SampledLayer::ZeroAlpha { .. } | SampledLayer::AlphaV1 { .. }
                    ))
            {
                return Err(error(
                    "Layer payload representation differs from immutable source alpha facts",
                ));
            }
            Ok(Some(use_))
        }
        _ => Err(error("Layer response differs from sparse track coverage")),
    }
}

#[cfg(test)]
struct FrameObserverState {
    token: u64,
    plan_id: ContentHash,
    expected: std::collections::BTreeMap<u64, ContentHash>,
    observed: std::collections::BTreeSet<u64>,
}

#[cfg(test)]
static FRAME_OBSERVER: std::sync::OnceLock<Mutex<Option<FrameObserverState>>> =
    std::sync::OnceLock::new();
#[cfg(test)]
static FRAME_OBSERVER_TOKEN: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(1);

#[cfg(test)]
struct FrameObserverGuard {
    token: u64,
}

#[cfg(test)]
impl FrameObserverGuard {
    fn install(
        plan_id: ContentHash,
        expected: std::collections::BTreeMap<u64, ContentHash>,
    ) -> Result<Self> {
        if expected.is_empty() || expected.len() > 512 {
            return Err(error(
                "Test frame observer requires 1..=512 bounded expectations",
            ));
        }
        let token = FRAME_OBSERVER_TOKEN.fetch_add(1, Ordering::Relaxed);
        let mut slot = FRAME_OBSERVER
            .get_or_init(|| Mutex::new(None))
            .lock()
            .map_err(|_| error("Test frame observer lock was poisoned"))?;
        if slot.is_some() {
            return Err(error("Test frame observer already has an owner"));
        }
        *slot = Some(FrameObserverState {
            token,
            plan_id,
            expected,
            observed: std::collections::BTreeSet::new(),
        });
        Ok(Self { token })
    }

    fn verify_complete(&self) -> Result<()> {
        let slot = FRAME_OBSERVER
            .get_or_init(|| Mutex::new(None))
            .lock()
            .map_err(|_| error("Test frame observer lock was poisoned"))?;
        let state = slot
            .as_ref()
            .filter(|state| state.token == self.token)
            .ok_or_else(|| error("Test frame observer ownership changed"))?;
        let expected: std::collections::BTreeSet<_> = state.expected.keys().copied().collect();
        if state.observed != expected {
            return Err(error(
                "Test frame observer did not see every expected frame",
            ));
        }
        Ok(())
    }
}

#[cfg(test)]
impl Drop for FrameObserverGuard {
    fn drop(&mut self) {
        if let Ok(mut slot) = FRAME_OBSERVER.get_or_init(|| Mutex::new(None)).lock()
            && slot.as_ref().is_some_and(|state| state.token == self.token)
        {
            *slot = None;
        }
    }
}

#[cfg(test)]
fn observe_frame(plan: &ExportPlan, frame: u64, pixels: &crate::pixels::Pixels) -> Result<()> {
    let plan_id = ContentHash::document(plan)?;
    let mut slot = FRAME_OBSERVER
        .get_or_init(|| Mutex::new(None))
        .lock()
        .map_err(|_| error("Test frame observer lock was poisoned"))?;
    let Some(state) = slot.as_mut().filter(|state| state.plan_id == plan_id) else {
        return Ok(());
    };
    let expected = state
        .expected
        .get(&frame)
        .ok_or_else(|| error("Test frame observer received an unexpected frame"))?;
    let actual = ContentHash::bytes(&pixels.bytes);
    if &actual != expected {
        return Err(error(format!(
            "Borrowed prehandoff frame {frame} hash {} differs from {}",
            actual.as_str(),
            expected.as_str()
        )));
    }
    if !state.observed.insert(frame) {
        return Err(error("Test frame observer received a frame twice"));
    }
    Ok(())
}

pub(super) fn decode(
    plan: &ExportPlan,
    blobs: &Path,
    output: &mpsc::SyncSender<Result<EvaluatedFrame>>,
    control: &crate::exports::ExportControl,
) -> Result<PictureExecutionEvidence> {
    let admission = composition::preflight_cancellable(plan, || control.check())?;
    let budget = Budget::new(admission.estimated_bytes);
    let signal = Signal {
        control: control.clone(),
        stopped: Arc::new(AtomicBool::new(false)),
        deadline: Instant::now() + crate::pcm::STREAM_DEADLINE,
    };
    let plan = Arc::new(plan.clone());
    let png_mutex = Arc::new(Mutex::new(()));
    let mut workers = Workers {
        ports: Vec::new(),
        signal: signal.clone(),
    };
    for track in plan
        .timeline
        .video_tracks
        .iter()
        .filter(|track| !track.clips.is_empty())
    {
        let mut uses: Vec<_> = plan
            .video
            .iter()
            .enumerate()
            .filter_map(|(index, use_)| (use_.track == track.id).then_some(index))
            .collect();
        uses.sort_by_key(|index| plan.video[*index].timeline_frames.start);
        let (request_send, request_receive) = mpsc::sync_channel(1);
        let (response_send, response_receive) = mpsc::sync_channel(1);
        let actor_plan = plan.clone();
        let actor_uses = uses.clone();
        let actor_blobs = blobs.to_path_buf();
        let actor_signal = signal.clone();
        let error_signal = signal.clone();
        let error_send = response_send.clone();
        let actor_budget = budget.clone();
        let actor_png = png_mutex.clone();
        let worker = std::thread::Builder::new()
            .name(format!("picture-{}", track.id.as_str()))
            .spawn(move || {
                let result = run_track(
                    Environment {
                        plan: actor_plan,
                        blobs: actor_blobs,
                        signal: actor_signal,
                        budget: actor_budget,
                        png_mutex: actor_png,
                    },
                    actor_uses,
                    request_receive,
                    response_send,
                );
                if let Err(error_) = &result {
                    let _ = send(&error_send, Err(error_.clone()), &error_signal);
                }
                result
            })?;
        workers.ports.push(Port {
            track: track.id.clone(),
            uses,
            cursor: 0,
            requests: Some(request_send),
            responses: Some(response_receive),
            worker: Some(worker),
        });
    }
    let canvas_bytes = crate::pixels::extent(plan.settings.width, plan.settings.height)?;
    for timeline_frame in 0..plan.timeline.frame_count {
        signal.check()?;
        for port in &workers.ports {
            send(
                port.requests
                    .as_ref()
                    .ok_or_else(|| error("Layer request port retired"))?,
                timeline_frame,
                &signal,
            )?;
        }
        let canvas_permit = budget.reserve(canvas_bytes as u64)?;
        let mut canvas = crate::pixels::Pixels {
            width: plan.settings.width,
            height: plan.settings.height,
            bytes: vec![0; canvas_bytes],
        };
        for pixel in canvas.bytes.chunks_exact_mut(4) {
            pixel[3] = 255;
        }
        let mut positive_contributions = 0u64;
        for port in &mut workers.ports {
            let decision = receive(
                port.responses
                    .as_ref()
                    .ok_or_else(|| error("Layer response port retired"))?,
                &signal,
            )??;
            if let Some(use_) = check_decision(&plan, port, timeline_frame, &decision)? {
                if use_.track != port.track {
                    return Err(error("Layer port changed track order"));
                }
                if let Decision::Source(observed) = decision {
                    let positive = match observed.sampled {
                        SampledLayer::NoGeometry | SampledLayer::ZeroAlpha { .. } => 0,
                        SampledLayer::LegacyOpaque { raster, .. } => {
                            composition::blend_layer_cancellable(
                                &mut canvas,
                                &raster,
                                &observed.observation,
                                || signal.check(),
                            )?
                        }
                        SampledLayer::AlphaV1 { raster, .. } => {
                            crate::alpha_picture::blend_cancellable(
                                &mut canvas,
                                &raster,
                                &observed.observation,
                                || signal.check(),
                            )?
                        }
                    };
                    positive_contributions = positive_contributions
                        .checked_add(positive)
                        .ok_or_else(|| error("Visible contribution counter overflow"))?;
                }
            }
        }
        if positive_contributions == 0 {
            return Err(StudioError::new(
                "video_coverage",
                format!("Output frame {timeline_frame} has no positive picture contribution"),
            ));
        }
        #[cfg(test)]
        observe_frame(&plan, timeline_frame, &canvas)?;
        send(
            output,
            Ok(EvaluatedFrame {
                timeline_frame,
                pixels: canvas,
                _picture_permit: Some(canvas_permit),
            }),
            &signal,
        )?;
    }
    workers.finish()?;
    let maximum = budget.maximum();
    if maximum > admission.estimated_bytes {
        return Err(error("Picture reservations exceeded preflight admission"));
    }
    Ok(PictureExecutionEvidence {
        schema: 1, track_workers: admission.tracks, composed_frames: plan.timeline.frame_count,
        peak_active_sources: admission.peak_active_sources, admitted_payload_bytes: admission.estimated_bytes,
        maximum_reserved_payload_bytes: maximum,
        scope: "Producer-only report: preflight track/source/admission estimates plus live logical permit high-water; includes configured PNG allowance; excludes process/native peak memory. Replay/reopen cannot reproduce it.".into(),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn alpha_plan(root: &Path, rgba: &[u8], frames: u64) -> ExportPlan {
        let mut encoded = Vec::new();
        let mut encoder = png::Encoder::new(&mut encoded, 2, 1);
        encoder.set_color(png::ColorType::Rgba);
        encoder.set_depth(png::BitDepth::Eight);
        let mut writer = encoder.write_header().unwrap();
        writer.write_image_data(rgba).unwrap();
        writer.finish().unwrap();
        let hash = ContentHash::bytes(&encoded);
        let path = root.join(hash.as_str());
        std::fs::write(&path, &encoded).unwrap();

        let mut plan: ExportPlan =
            serde_json::from_slice(include_bytes!("../tests/fixtures/legacy/plan-schema3.json"))
                .unwrap();
        let old_hash = plan.video[0].asset.clone();
        let mut asset = plan.source_closure.remove(&old_hash).unwrap();
        asset.hash = hash.clone();
        asset.bytes = encoded.len() as u64;
        asset.descriptor = crate::image::probe(&path).unwrap();
        asset.backend = "Rust png 0.17.16 / straight RGBA8 alpha v1".into();
        plan.source_closure.insert(hash.clone(), asset);
        plan.schema = 7;
        plan.alpha_policy = Some(crate::AlphaPolicy::StraightRgbaPremulUnorm16Q16V1);
        plan.settings.width = 2;
        plan.settings.height = 1;
        plan.timeline.frame_count = frames;
        let samples = frames * 2_000;
        plan.timeline.audio_tracks[0].clips[0]
            .timeline_samples
            .length = samples;
        plan.timeline.audio_tracks[0].clips[0].source_samples.length = samples;
        plan.audio[0].clip = plan.timeline.audio_tracks[0].clips[0].clone();
        plan.timeline_sample_frames = samples;
        let clip = &mut plan.timeline.video_tracks[0].clips[0];
        clip.asset = hash.clone();
        clip.timeline_frames.length = frames;
        clip.framing = None;
        clip.placement = None;
        clip.motion = None;
        clip.mask = None;
        let use_ = &mut plan.video[0];
        use_.asset = hash.clone();
        use_.timeline_frames.length = frames;
        use_.presentation_ordinals = vec![0; frames as usize];
        use_.framing = None;
        use_.placement = Some(crate::PicturePlacement::canvas(2, 1));
        use_.motion = None;
        use_.mask = None;
        let MediaDescriptor::Image {
            width,
            height,
            rgba_sha256,
            alpha: Some(alpha),
            ..
        } = &plan.source_closure[&hash].descriptor
        else {
            panic!("transparent image expected")
        };
        plan.image_decode_evidence = vec![crate::plan::ImageDecodeEvidence {
            asset: hash.clone(),
            width: *width,
            height: *height,
            rgba_sha256: rgba_sha256.clone(),
            decoder_executable_sha256: plan.renderer.executable_sha256.clone(),
            source_alpha_id: Some(
                crate::alpha_picture::source_alpha_id(&hash, rgba_sha256, alpha).unwrap(),
            ),
        }];
        crate::plan::validate_decode_evidence(&plan).unwrap();
        plan
    }

    #[test]
    fn borrowed_frame_observer_binds_the_exact_plan_without_copying_the_canvas() {
        let root = std::env::temp_dir().join(format!(
            "alpha-frame-observer-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        std::fs::create_dir(&root).unwrap();
        let plan = alpha_plan(&root, &[255, 0, 0, 128, 0, 0, 255, 255], 1);
        let plan_id = ContentHash::document(&plan).unwrap();
        let wrong = [(0, ContentHash::bytes(b"deliberately wrong frame"))]
            .into_iter()
            .collect();
        let failing_observer = FrameObserverGuard::install(plan_id.clone(), wrong).unwrap();
        let (send_, _receive) = mpsc::sync_channel(1);
        let failure = decode(
            &plan,
            &root,
            &send_,
            &crate::exports::ExportControl::test_active(),
        )
        .unwrap_err();
        assert!(failure.detail.contains("Borrowed prehandoff frame 0 hash"));
        drop(failing_observer);

        let expected = [(0, ContentHash::bytes(&[0, 0, 128, 255, 255, 0, 0, 255]))]
            .into_iter()
            .collect();
        let observer = FrameObserverGuard::install(plan_id, expected).unwrap();
        let (send_, receive) = mpsc::sync_channel::<Result<EvaluatedFrame>>(1);
        let evidence = decode(
            &plan,
            &root,
            &send_,
            &crate::exports::ExportControl::test_active(),
        )
        .unwrap();
        observer.verify_complete().unwrap();
        let frame = receive.recv().unwrap().unwrap();
        assert_eq!(frame.timeline_frame, 0);
        assert_eq!(frame.pixels.bytes, [0, 0, 128, 255, 255, 0, 0, 255]);
        assert_eq!(evidence.composed_frames, 1);
        std::fs::remove_dir_all(root).unwrap();
    }

    fn run_isolated_native_alpha_canary(
        authored_name: &str,
        authored_sha256: &str,
        expected_profile: crate::MovieProfile,
        intent: &str,
    ) {
        const AUTHORED_A01_SHA256: &str =
            "622822d8a7e59222cf80d81e94d6b706747670110ba27f20f17051e822ae13e0";
        const REFERENCE_SUMMARY_SHA256: &str =
            "e39a9b8c87a8a57260261cb304173db79110e7cead8e565c6eafe72ec8f6765a";
        const PRIMARY_ASSET: &str =
            "444d5540a760aceb2b61063a1bba0b2bfc0982a94036d0eb360d85afd1b5c1e9";
        const TRANSPARENT_ASSET: &str =
            "34208c02258cf71ea72791c568830d1d88ba9b743d44b8d54d539cc05d1462bc";

        let repository = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../..");
        let unit = repository
            .join("artifacts/scratch-video-goal-20261005/native-project-a01/alpha-native-unit-a01");
        let authored_path = unit.join(authored_name);
        let reference_path = unit.join("native-reference-a02/reference-summary-a02.json");
        let authored_bytes = std::fs::read(&authored_path).unwrap();
        assert_eq!(
            ContentHash::bytes(&authored_bytes).as_str(),
            authored_sha256
        );
        let authored: serde_json::Value = serde_json::from_slice(&authored_bytes).unwrap();
        if authored_name == "fixtures-authored-a02.json" {
            assert_eq!(
                authored["predecessorFixture"]["sha256"],
                AUTHORED_A01_SHA256
            );
        }

        let root = std::env::temp_dir().join(format!(
            "alpha-native-observer-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        let studio = crate::Studio::open(root.join("state")).unwrap();
        let create: crate::CreateProject =
            serde_json::from_value(authored["createRequest"].clone()).unwrap();
        let created = studio.create_project(create.clone()).unwrap();
        let mut commit_value = authored["commitWithoutBaseRevision"].clone();
        commit_value
            .as_object_mut()
            .unwrap()
            .insert("base_revision".into(), serde_json::json!(created.revision));
        let commit: crate::CommitProject = serde_json::from_value(commit_value).unwrap();
        let authored_timeline_id = ContentHash::document(&commit.timelines[0]).unwrap();
        let project = studio.project(create.project).unwrap();
        let committed = project.commit(commit).unwrap();
        let profile: crate::MovieProfile =
            serde_json::from_value(authored["strictProfile"].clone()).unwrap();
        assert_eq!(profile, expected_profile);
        let export = crate::ExportRequest {
            intent: EntityId::parse(intent).unwrap(),
            revision: committed.revision,
            timeline: EntityId::parse("alpha-picture").unwrap(),
            profile,
        };
        let prepared = project.prepare_export(export.clone()).unwrap();
        assert_eq!(prepared.plan.schema, 7);
        assert_eq!(
            prepared.plan.alpha_policy,
            Some(crate::AlphaPolicy::StraightRgbaPremulUnorm16Q16V1)
        );
        assert_eq!(
            ContentHash::document(&prepared.plan).unwrap(),
            prepared.plan_id
        );
        assert_eq!(
            ContentHash::document(&prepared.plan.timeline).unwrap(),
            authored_timeline_id
        );
        assert_eq!(prepared.plan.timeline.frame_count, 72);
        assert_eq!(prepared.plan.timeline_sample_frames, 144_000);
        assert_eq!(prepared.plan.video.len(), 4);
        assert_eq!(prepared.plan.audio.len(), 1);

        let source_alpha_ids: std::collections::BTreeSet<_> = prepared
            .plan
            .image_decode_evidence
            .iter()
            .map(|evidence| {
                assert!(matches!(
                    evidence.asset.as_str(),
                    PRIMARY_ASSET | TRANSPARENT_ASSET
                ));
                evidence.source_alpha_id.clone().unwrap()
            })
            .collect();
        assert_eq!(prepared.plan.image_decode_evidence.len(), 2);
        assert_eq!(source_alpha_ids.len(), 2);

        let reference_bytes = std::fs::read(&reference_path).unwrap();
        assert_eq!(
            ContentHash::bytes(&reference_bytes).as_str(),
            REFERENCE_SUMMARY_SHA256
        );
        let reference: serde_json::Value = serde_json::from_slice(&reference_bytes).unwrap();
        assert_eq!(reference["fixture"]["sha256"], AUTHORED_A01_SHA256);
        for (asset, label) in [
            (PRIMARY_ASSET, "primary"),
            (TRANSPARENT_ASSET, "transparent"),
        ] {
            let evidence = prepared
                .plan
                .image_decode_evidence
                .iter()
                .find(|evidence| evidence.asset.as_str() == asset)
                .unwrap();
            assert_eq!(
                evidence.rgba_sha256.as_str(),
                reference["sourceAssets"][label]["rgbaSha256"]
                    .as_str()
                    .unwrap()
            );
        }
        let expected: std::collections::BTreeMap<_, _> = reference["native_refs"]
            .as_array()
            .unwrap()
            .iter()
            .map(|frame| {
                (
                    frame["timelineFrame"].as_u64().unwrap(),
                    ContentHash::parse(frame["expectedBgraSha256"].as_str().unwrap()).unwrap(),
                )
            })
            .collect();
        assert_eq!(expected.len(), 72);

        let observer = FrameObserverGuard::install(prepared.plan_id.clone(), expected).unwrap();
        let exported = project.export(export.clone()).unwrap();
        observer.verify_complete().unwrap();
        match &prepared.plan.profile {
            crate::MovieProfile::NativeColorMasterV1 => {
                assert_eq!(exported.receipt.artifact.schema, 3);
                assert!(exported.receipt.artifact.technical.video_color.is_none());
            }
            crate::MovieProfile::NativeColorMasterV2 => {
                assert_eq!(exported.receipt.artifact.schema, 4);
                let tuple = crate::NativeColorTupleEvidence {
                    color_primaries: "ITU_R_709_2".into(),
                    transfer_function: "ITU_R_709_2".into(),
                    y_cb_cr_matrix: "ITU_R_709_2".into(),
                };
                assert_eq!(
                    exported.receipt.artifact.technical.video_color,
                    Some(crate::NativeVideoColorEvidence {
                        encoded_samples: tuple.clone(),
                        decoded_buffers: tuple,
                    })
                );
            }
            crate::MovieProfile::H264AacMp4 { .. } => panic!("strict master expected"),
        }
        let evidence = exported.picture_execution.as_ref().unwrap();
        assert_eq!(evidence.track_workers, 4);
        assert_eq!(evidence.composed_frames, 72);
        assert!(evidence.maximum_reserved_payload_bytes <= evidence.admitted_payload_bytes);
        let verified = project.verify_export(export.intent.clone()).unwrap();
        assert_eq!(verified.receipt.receipt_id, exported.receipt.receipt_id);
        assert!(verified.picture_execution.is_none());
        let replayed = project.export(export).unwrap();
        assert!(replayed.replayed);
        assert_eq!(replayed.receipt.receipt_id, exported.receipt.receipt_id);
        println!(
            "ALPHA_INSTRUMENTED_PRODUCER {}",
            serde_json::json!({
                "schema": 1,
                "authoredFixtureSha256": authored_sha256,
                "referenceSummarySha256": REFERENCE_SUMMARY_SHA256,
                "planId": prepared.plan_id,
                "timelineId": authored_timeline_id,
                "renderer": prepared.plan.renderer,
                "profile": prepared.plan.profile,
                "observedFrames": evidence.composed_frames,
                "receiptId": exported.receipt.receipt_id,
                "receiptSchema": exported.receipt.artifact.schema,
                "videoColor": exported.receipt.artifact.technical.video_color,
                "verificationId": verified.verification_id,
                "claims": {
                    "ordinaryCliProducer": false,
                    "encodedOutput": true,
                    "publicVerification": true,
                    "completedReplay": true,
                    "watched": false,
                    "heard": false,
                    "creativeAccepted": false
                }
            })
        );
        std::fs::remove_dir_all(root).unwrap();
    }

    #[test]
    #[ignore = "requires the frozen independent 72-frame alpha reference and Panja PCM master"]
    fn isolated_prepared_plan_matches_every_independent_native_alpha_frame() {
        run_isolated_native_alpha_canary(
            "fixtures-authored-a01.json",
            "622822d8a7e59222cf80d81e94d6b706747670110ba27f20f17051e822ae13e0",
            crate::MovieProfile::NativeColorMasterV1,
            "prepare-alpha-observer-a01",
        );
    }

    #[test]
    #[ignore = "requires the frozen independent 72-frame alpha reference and Panja PCM master"]
    fn isolated_rec709_prepared_plan_matches_every_independent_native_alpha_frame() {
        run_isolated_native_alpha_canary(
            "fixtures-authored-a02.json",
            "4e1e1c8bde98c40506f3d2f68333f92c42d7c6a93f300d874be96cf05670f753",
            crate::MovieProfile::NativeColorMasterV2,
            "prepare-alpha-rec709-observer-a01",
        );
    }

    #[test]
    fn the_last_alpha_cache_retires_before_its_raster_response_is_observable() {
        let root = std::env::temp_dir().join(format!(
            "alpha-picture-cache-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        std::fs::create_dir(&root).unwrap();
        let plan = alpha_plan(&root, &[1, 2, 3, 0, 40, 50, 60, 128], 1);
        let budget = Budget::new(composition::MAX_ADMITTED_BYTES);
        let (send_request, requests) = mpsc::sync_channel(1);
        let (responses, receiver) = mpsc::sync_channel(1);
        let environment = Environment {
            plan: Arc::new(plan),
            blobs: root.clone(),
            signal: signal(),
            budget: budget.clone(),
            png_mutex: Arc::new(Mutex::new(())),
        };
        let worker =
            std::thread::spawn(move || run_track(environment, vec![0], requests, responses));
        send_request.send(0).unwrap();
        let decision = receiver
            .recv_timeout(Duration::from_secs(5))
            .unwrap()
            .unwrap();
        let Decision::Source(ref observed) = decision else {
            panic!("alpha source expected")
        };
        assert_eq!(budget.current(), 16);
        assert!(matches!(observed.sampled, SampledLayer::AlphaV1 { .. }));
        drop(decision);
        assert_eq!(budget.current(), 0);
        worker.join().unwrap().unwrap();
        std::fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn a_fully_transparent_active_image_remains_a_source_observation() {
        let root = std::env::temp_dir().join(format!(
            "zero-alpha-source-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        std::fs::create_dir(&root).unwrap();
        let plan = alpha_plan(&root, &[200, 1, 2, 0, 3, 240, 4, 0], 1);
        let budget = Budget::new(composition::MAX_ADMITTED_BYTES);
        let (send_request, requests) = mpsc::sync_channel(1);
        let (responses, receiver) = mpsc::sync_channel(1);
        let environment = Environment {
            plan: Arc::new(plan),
            blobs: root.clone(),
            signal: signal(),
            budget: budget.clone(),
            png_mutex: Arc::new(Mutex::new(())),
        };
        let worker =
            std::thread::spawn(move || run_track(environment, vec![0], requests, responses));
        send_request.send(0).unwrap();
        let decision = receiver
            .recv_timeout(Duration::from_secs(5))
            .unwrap()
            .unwrap();
        let Decision::Source(observed) = decision else {
            panic!("active transparent image must retain Source lineage")
        };
        assert_eq!(observed.ordinal, 0);
        assert!(observed.pts.is_none());
        assert!(matches!(observed.sampled, SampledLayer::ZeroAlpha { .. }));
        assert!(observed.observation.effective_bounds.is_some());
        assert_eq!(budget.current(), 0);
        worker.join().unwrap().unwrap();
        std::fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn fully_hidden_movie_worker_still_copies_source_and_checks_its_pts() {
        let root = std::env::temp_dir().join(format!(
            "masked-native-worker-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        std::fs::create_dir(&root).unwrap();
        let bytes = include_bytes!("../tests/fixtures/native/h264-source-a14.mp4");
        let hash = ContentHash::bytes(bytes);
        assert_eq!(
            hash.as_str(),
            "097dd9a1a59c02a8967db82463e8b43fc6ffc42a5294c997a77280967b1174df"
        );
        let path = root.join(hash.as_str());
        std::fs::write(&path, bytes).unwrap();
        let descriptor = media::probe(&path, &MediaKind::Movie).unwrap();
        let mut baseline: ExportPlan =
            serde_json::from_slice(include_bytes!("../tests/fixtures/legacy/plan-schema5.json"))
                .unwrap();
        let mut asset = baseline
            .source_closure
            .remove(&baseline.video[0].asset)
            .unwrap();
        asset.hash = hash.clone();
        asset.bytes = bytes.len() as u64;
        asset.descriptor = descriptor;
        baseline.source_closure.insert(hash.clone(), asset);
        baseline.timeline.frame_count = 1;
        let use_ = &mut baseline.video[0];
        use_.asset = hash.clone();
        use_.timeline_frames = Span {
            start: 0,
            length: 1,
        };
        use_.allowed_source_samples = Span {
            start: 1,
            length: 1,
        };
        use_.presentation_ordinals = vec![1];
        use_.placement = Some(crate::PicturePlacement::canvas(320, 180));
        use_.motion = None;
        use_.framing = None;
        use_.mask = Some(crate::mask::normalize_mask_cancellable(&serde_json::from_value(serde_json::json!({"kind":"axis_reveal","axis":"horizontal","progress":{"keys":[{"frame":0,"value":0.0}]},"inverted":false})).unwrap(),1,||Ok(())).unwrap());
        for inject_bad_pts in [false, true] {
            // This private worker harness tests execution, not a prepared-plan or receipt claim.
            let mut plan = baseline.clone();
            if inject_bad_pts {
                let MediaDescriptor::Movie { samples, .. } =
                    &mut plan.source_closure.get_mut(&hash).unwrap().descriptor
                else {
                    panic!("movie required")
                };
                samples[1].pts.ticks += 1;
            }
            let expected_pts = match &plan.source_closure[&hash].descriptor {
                MediaDescriptor::Movie { samples, .. } => samples[1].pts.clone(),
                _ => unreachable!(),
            };
            let budget = Budget::new(composition::MAX_ADMITTED_BYTES);
            let (request_send, requests) = mpsc::sync_channel(1);
            let (responses, receive) = mpsc::sync_channel(1);
            let mut signal = signal();
            signal.deadline = Instant::now() + Duration::from_secs(30);
            let environment = Environment {
                plan: Arc::new(plan),
                blobs: root.clone(),
                signal,
                budget: budget.clone(),
                png_mutex: Arc::new(Mutex::new(())),
            };
            let worker =
                std::thread::spawn(move || run_track(environment, vec![0], requests, responses));
            request_send.send(0).unwrap();
            if inject_bad_pts {
                let failure = worker.join().unwrap().unwrap_err();
                assert!(
                    failure
                        .detail
                        .contains("Layer source PTS differs from immutable index"),
                    "{failure}"
                );
            } else {
                let decision = receive
                    .recv_timeout(Duration::from_secs(30))
                    .unwrap()
                    .unwrap();
                let Decision::Source(observed) = decision else {
                    panic!("hidden active source must remain Source")
                };
                assert_eq!(observed.ordinal, 1);
                assert_eq!(observed.pts, Some(expected_pts));
                assert!(matches!(observed.sampled, SampledLayer::NoGeometry));
                assert!(observed.observation.effective_bounds.is_none());
                worker.join().unwrap().unwrap();
                assert_eq!(budget.maximum(), 320 * 180 * 4);
            }
            assert_eq!(budget.current(), 0);
        }
        std::fs::remove_dir_all(root).unwrap();
    }

    fn signal() -> Signal {
        Signal {
            control: crate::exports::ExportControl::test_active(),
            stopped: Arc::new(AtomicBool::new(false)),
            deadline: Instant::now() + Duration::from_secs(5),
        }
    }
    #[test]
    fn channel_backpressure_stops_and_preserves_the_export_cause() {
        let signal = signal();
        let (send_, _receive) = mpsc::sync_channel(1);
        send_.send(0u64).unwrap();
        let worker_signal = signal.clone();
        let worker = std::thread::spawn(move || send(&send_, 1, &worker_signal));
        std::thread::sleep(Duration::from_millis(30));
        signal.control.interrupt();
        signal.stopped.store(true, Ordering::Release);
        assert_eq!(
            worker.join().unwrap().unwrap_err().code,
            "export_interrupted"
        );
        assert_eq!(signal.check().unwrap_err().code, "export_interrupted");
    }
    #[test]
    fn pipeline_drop_closes_full_response_ports_and_joins_every_worker() {
        let signal = signal();
        let completed = Arc::new(std::sync::atomic::AtomicUsize::new(0));
        let mut workers = Workers {
            ports: Vec::new(),
            signal: signal.clone(),
        };
        for n in 0..4 {
            let (requests, _request_receiver) = mpsc::sync_channel(1);
            let (responses, receiver) = mpsc::sync_channel(1);
            responses.send(Ok(Decision::Gap(0))).unwrap();
            let worker_signal = signal.clone();
            let completed = completed.clone();
            let worker = std::thread::spawn(move || {
                let result = send(&responses, Ok(Decision::Gap(1)), &worker_signal);
                completed.fetch_add(1, Ordering::AcqRel);
                result
            });
            workers.ports.push(Port {
                track: EntityId::parse(format!("track-{n}")).unwrap(),
                uses: Vec::new(),
                cursor: 0,
                requests: Some(requests),
                responses: Some(receiver),
                worker: Some(worker),
            });
        }
        drop(workers);
        assert_eq!(completed.load(Ordering::Acquire), 4);
    }
    #[test]
    fn a_serialized_png_wait_observes_owner_stop() {
        let signal = signal();
        let mutex = Arc::new(Mutex::new(()));
        let lock = mutex.lock().unwrap();
        let worker_mutex = mutex.clone();
        let worker_signal = signal.clone();
        let worker =
            std::thread::spawn(move || png_lock(&worker_mutex, &worker_signal).map(|_| ()));
        std::thread::sleep(Duration::from_millis(30));
        signal.stopped.store(true, Ordering::Release);
        assert!(worker.join().unwrap().is_err());
        drop(lock);
    }

    #[test]
    fn the_last_image_cache_retires_before_its_response_is_observable() {
        let root = std::env::temp_dir().join(format!(
            "picture-cache-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        std::fs::create_dir(&root).unwrap();
        let mut encoded = Vec::new();
        let mut encoder = png::Encoder::new(&mut encoded, 2, 1);
        encoder.set_color(png::ColorType::Rgb);
        encoder.set_depth(png::BitDepth::Eight);
        let mut writer = encoder.write_header().unwrap();
        writer.write_image_data(&[240, 20, 0, 240, 20, 0]).unwrap();
        writer.finish().unwrap();
        let hash = ContentHash::bytes(&encoded);
        let path = root.join(hash.as_str());
        std::fs::write(&path, &encoded).unwrap();
        let mut plan: ExportPlan =
            serde_json::from_slice(include_bytes!("../tests/fixtures/legacy/plan-schema3.json"))
                .unwrap();
        let old_hash = plan.video[0].asset.clone();
        let mut asset = plan.source_closure.remove(&old_hash).unwrap();
        asset.hash = hash.clone();
        asset.bytes = encoded.len() as u64;
        asset.descriptor = crate::image::probe(&path).unwrap();
        plan.source_closure.insert(hash.clone(), asset);
        plan.timeline.frame_count = 2;
        plan.video[0].asset = hash;
        plan.video[0].timeline_frames = Span {
            start: 0,
            length: 1,
        };
        plan.video[0].presentation_ordinals = vec![0];
        plan.video[0].placement = Some(crate::PicturePlacement::canvas(320, 180));
        let budget = Budget::new(composition::MAX_ADMITTED_BYTES);
        let (send_request, requests) = mpsc::sync_channel(1);
        let (responses, receiver) = mpsc::sync_channel(1);
        let environment = Environment {
            plan: Arc::new(plan),
            blobs: root.clone(),
            signal: signal(),
            budget: budget.clone(),
            png_mutex: Arc::new(Mutex::new(())),
        };
        let worker =
            std::thread::spawn(move || run_track(environment, vec![0], requests, responses));
        send_request.send(0).unwrap();
        let first = receiver
            .recv_timeout(Duration::from_secs(5))
            .unwrap()
            .unwrap();
        let Decision::Source(ref observed) = first else {
            panic!("source expected")
        };
        assert_eq!(
            budget.current(),
            match &observed.sampled {
                SampledLayer::LegacyOpaque { raster, .. } => raster.bytes.len() as u64,
                _ => panic!("opaque raster expected"),
            }
        );
        drop(first);
        assert_eq!(budget.current(), 0);
        send_request.send(1).unwrap();
        assert!(matches!(
            receiver
                .recv_timeout(Duration::from_secs(5))
                .unwrap()
                .unwrap(),
            Decision::Gap(1)
        ));
        worker.join().unwrap().unwrap();
        std::fs::remove_dir_all(root).unwrap();
    }
}
