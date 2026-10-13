use std::collections::BTreeSet;
use std::path::Path;
use std::sync::mpsc;
use std::time::{Duration, Instant};

use objc2::rc::Retained;
use objc2::runtime::AnyObject;
use objc2_av_foundation::{AVAssetReader, AVAssetReaderStatus, AVAssetReaderTrackOutput};
use objc2_core_media::{CMAudioFormatDescriptionGetStreamBasicDescription, CMTime};
use objc2_core_video::{CVPixelBufferGetHeight, CVPixelBufferGetWidth, kCVPixelFormatType_32BGRA};
use objc2_foundation::{NSDictionary, NSNumber, NSString};
use serde::{Deserialize, Serialize};

use crate::{ExportPlan, MediaDescriptor, MediaKind, Result, Span, StudioError, media};

#[path = "layers.rs"]
mod layers;

fn error(detail: impl Into<String>) -> StudioError {
    StudioError::new("native_export_error", detail)
}
fn number(value: u32) -> Retained<AnyObject> {
    unsafe { Retained::cast_unchecked(NSNumber::new_u32(value)) }
}
fn dictionary(
    values: Vec<(&str, Retained<AnyObject>)>,
) -> Retained<NSDictionary<NSString, AnyObject>> {
    let keys: Vec<_> = values
        .iter()
        .map(|(key, _)| NSString::from_str(key))
        .collect();
    let keys: Vec<_> = keys.iter().map(|key| &**key).collect();
    let values: Vec<_> = values.iter().map(|(_, value)| &**value).collect();
    NSDictionary::from_slices(&keys, &values)
}
struct ReaderGuard<'a>(&'a AVAssetReader);
impl Drop for ReaderGuard<'_> {
    fn drop(&mut self) {
        unsafe { self.0.cancelReading() };
    }
}
pub(crate) fn validate_pixel_extents(plan: &ExportPlan) -> Result<()> {
    validate_pixel_extents_cancellable(plan, || Ok(()))
}
fn validate_pixel_extents_cancellable(
    plan: &ExportPlan,
    mut check: impl FnMut() -> Result<()>,
) -> Result<()> {
    if matches!(plan.schema, 4..=7) {
        return crate::composition::preflight_cancellable(plan, check).map(|_| ());
    }
    crate::plan::validate_picture_mapping_cancellable(plan, &mut check)?;
    crate::pixels::extent(plan.settings.width, plan.settings.height)?;
    for clip in &plan.video {
        check()?;
        let (width, height) = plan.source_closure[&clip.asset]
            .descriptor
            .picture_extent()?;
        crate::pixels::extent(width, height)?;
    }
    Ok(())
}
pub(crate) fn validate_profile(plan: &ExportPlan) -> Result<()> {
    validate_profile_cancellable(plan, || Ok(()))
}
fn validate_profile_cancellable(
    plan: &ExportPlan,
    check: impl FnMut() -> Result<()>,
) -> Result<()> {
    validate_pixel_extents_cancellable(plan, check)?;
    crate::plan::validate_decode_evidence(plan)?;
    if plan.video.is_empty()
        || plan.audio.len() != 1
        || plan.timeline.frame_count > crate::model::MAX_TIMELINE_FRAMES
        || plan.settings.audio_rate != 48000
        || plan.settings.channels != 2
    {
        return Err(StudioError::new(
            "unsupported_native_composition",
            "Native export requires movie/PNG picture coverage, one measured 48kHz stereo PCM clip and at most 100000 frames",
        ));
    }
    let audio = &plan.audio[0].clip;
    if !matches!(
        plan.source_closure[&audio.asset].descriptor,
        MediaDescriptor::Audio {
            rate: 48000,
            channels: 2,
            ..
        }
    ) {
        return Err(StudioError::new(
            "unsupported_native_audio_layout",
            "Native identity audio requires a measured 48kHz stereo source; downmixing and resampling require explicit operations",
        ));
    }
    if audio.timeline_samples.start != 0
        || audio.timeline_samples.length != plan.timeline_sample_frames
        || audio.gain != 1.0
        || audio.pan != 0.0
    {
        return Err(StudioError::new(
            "unsupported_native_composition",
            "Native export requires complete unity-gain, zero-pan audio coverage",
        ));
    }
    if matches!(plan.schema, 4..=7) {
        return Ok(());
    }
    let mut clips = plan.video.iter().collect::<Vec<_>>();
    clips.sort_by_key(|clip| clip.timeline_frames.start);
    let mut covered = 0;
    for clip in clips {
        if clip.track != plan.video[0].track || clip.timeline_frames.start != covered {
            return Err(StudioError::new(
                "unsupported_native_composition",
                "Native cuts require one picture track with adjacent complete coverage",
            ));
        }
        covered = clip.timeline_frames.end()?;
        let (width, height) = plan.source_closure[&clip.asset]
            .descriptor
            .picture_extent()?;
        if clip.framing.is_none()
            && (width != plan.settings.width || height != plan.settings.height)
        {
            return Err(StudioError::new(
                "unsupported_geometry",
                "Different source and canvas dimensions require explicit framing",
            ));
        }
        if let Some(framing) = &clip.framing {
            framing.validate_source_extent(width, height)?;
        }
    }
    if covered != plan.timeline.frame_count {
        return Err(error("Cut coverage differs from the immutable timeline"));
    }
    Ok(())
}

pub(crate) fn write(
    plan: &ExportPlan,
    blobs: &Path,
    output: &Path,
    control: crate::exports::ExportControl,
) -> Result<Option<crate::PictureExecutionEvidence>> {
    validate_profile_cancellable(plan, || control.check())?;
    if output.exists() {
        return Err(error("Native writer requires a fresh staged file"));
    }
    let caught = objc2::exception::catch(std::panic::AssertUnwindSafe(|| {
        objc2::rc::autoreleasepool(|_| write_inner(plan, blobs, output, &control))
    }));
    caught.unwrap_or_else(|exception| {
        Err(StudioError::new(
            "native_exception",
            format!("{exception:?}"),
        ))
    })
}

fn write_inner(
    plan: &ExportPlan,
    blobs: &Path,
    output: &Path,
    control: &crate::exports::ExportControl,
) -> Result<Option<crate::PictureExecutionEvidence>> {
    let format = crate::native_format::NativeFormatContract::for_profile(&plan.profile)?;
    let writer = format.start_writer(output, &plan.settings, control)?;
    let audio = &plan.audio[0].clip;
    let mut audio_stream = crate::pcm::Stream::open(
        &blobs.join(audio.asset.as_str()),
        Some(audio.source_samples.clone()),
        Some(control.clone()),
    )?;
    let (send, receive) = mpsc::sync_channel(if matches!(plan.schema, 4..=7) { 1 } else { 2 });
    let decode_plan = plan.clone();
    let decode_blobs = blobs.to_path_buf();
    let decode_control = control.clone();
    let worker = std::thread::spawn(move || {
        let decoded = if matches!(decode_plan.schema, 4..=7) {
            layers::decode(&decode_plan, &decode_blobs, &send, &decode_control).map(Some)
        } else {
            decode_timeline(&decode_plan, &decode_blobs, &send, &decode_control).map(|()| None)
        };
        if let Err(error) = &decoded {
            let _ = send.send(Err(error.clone()));
        }
        decoded
    });
    let caught = objc2::exception::catch(std::panic::AssertUnwindSafe(|| {
        encode_frames(plan, &mut audio_stream, &writer, receive, control)
    }));
    let result = caught.unwrap_or_else(|exception| {
        Err(StudioError::new(
            "native_exception",
            format!("{exception:?}"),
        ))
    });
    if result.is_err() {
        control.interrupt();
    }
    let decoded = worker
        .join()
        .map_err(|_| error("Native decoder worker panicked"))?;
    result?;
    decoded
}

struct EvaluatedFrame {
    timeline_frame: u64,
    pixels: crate::pixels::Pixels,
    _picture_permit: Option<crate::composition::Permit>,
}

fn decode_timeline(
    plan: &ExportPlan,
    blobs: &Path,
    send: &mpsc::SyncSender<Result<EvaluatedFrame>>,
    control: &crate::exports::ExportControl,
) -> Result<()> {
    let mut clips = plan.video.clone();
    clips.sort_by_key(|clip| clip.timeline_frames.start);
    for use_ in clips {
        control.check()?;
        let path = blobs.join(use_.asset.as_str());
        let asset = &plan.source_closure[&use_.asset];
        if matches!(asset.descriptor, MediaDescriptor::Image { .. }) {
            let pixels = crate::image::decode_asset(&path, asset)?;
            let pixels = crate::framing::apply(
                pixels,
                use_.framing.as_ref(),
                plan.settings.width,
                plan.settings.height,
            )?;
            for local in 0..use_.timeline_frames.length {
                control.check()?;
                send.send(Ok(EvaluatedFrame {
                    _picture_permit: None,
                    timeline_frame: use_.timeline_frames.start + local,
                    pixels: crate::pixels::Pixels {
                        width: pixels.width,
                        height: pixels.height,
                        bytes: pixels.bytes.clone(),
                    },
                }))
                .map_err(|_| error("Native writer closed the bounded image frame channel"))?;
            }
            continue;
        }
        let send = send.clone();
        let control = control.clone();
        let MediaDescriptor::Movie {
            samples,
            width: source_width,
            height: source_height,
            ..
        } = &plan.source_closure[&use_.asset].descriptor
        else {
            return Err(error("Cut source is not a movie"));
        };
        let samples = samples.clone();
        let (source_width, source_height) = (*source_width, *source_height);
        let (width, height) = (plan.settings.width, plan.settings.height);
        let wait_control = control.clone();
        let abort_control = control.clone();
        media::with_track_cancellable(
            &path,
            &MediaKind::Movie,
            crate::pcm::STREAM_DEADLINE,
            move || wait_control.check(),
            move || abort_control.interrupt(),
            move |track| {
                control.check()?;
                let asset =
                    unsafe { track.asset() }.ok_or_else(|| error("Cut track lost asset"))?;
                let reader = unsafe { AVAssetReader::assetReaderWithAsset_error(&asset) }
                    .map_err(|e| error(format!("{e:?}")))?;
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
                    return Err(error("Cut decoder rejected BGRA"));
                }
                unsafe { reader.addOutput(&output) };
                if !unsafe { reader.startReading() } {
                    return Err(error("Cut decoder did not start"));
                }
                let (mut next, mut current_ordinal, mut current) = (0_u64, None, None);
                let deadline = Instant::now() + crate::pcm::STREAM_DEADLINE;
                for (local, wanted) in use_.presentation_ordinals.iter().copied().enumerate() {
                    control.check()?;
                    while current_ordinal != Some(wanted) {
                        control.check()?;
                        if Instant::now() > deadline {
                            return Err(error("Cut decode deadline expired"));
                        }
                        if next > wanted {
                            return Err(error("Nonmonotonic source cadence is unsupported"));
                        }
                        let sample = unsafe { output.copyNextSampleBuffer() }.ok_or_else(|| {
                            error(format!("Cut decode ended early: {:?}", unsafe {
                                reader.error()
                            }))
                        })?;
                        let pts = unsafe { sample.presentation_time_stamp() };
                        let indexed = &samples
                            .get(next as usize)
                            .ok_or_else(|| error("Cut decoder exceeded source index"))?
                            .pts;
                        if pts.timescale <= 0
                            || pts.epoch != 0
                            || i128::from(pts.value) * i128::from(indexed.timescale)
                                != i128::from(indexed.ticks) * i128::from(pts.timescale)
                        {
                            return Err(error("Cut source PTS differs from its immutable index"));
                        }
                        current = Some(sample);
                        current_ordinal = Some(next);
                        next += 1;
                    }
                    let image = unsafe {
                        current
                            .as_ref()
                            .ok_or_else(|| error("Cut has no frame"))?
                            .image_buffer()
                    }
                    .ok_or_else(|| error("Cut sample has no image"))?;
                    let pixels = crate::pixels::Pixels::copy(&image)?;
                    if pixels.width != source_width || pixels.height != source_height {
                        return Err(error("Cut frame dimensions changed"));
                    }
                    let pixels =
                        crate::framing::apply(pixels, use_.framing.as_ref(), width, height)?;
                    let timeline_frame = use_.timeline_frames.start + local as u64;
                    send.send(Ok(EvaluatedFrame {
                        _picture_permit: None,
                        timeline_frame,
                        pixels,
                    }))
                    .map_err(|_| error("Native writer closed the bounded frame channel"))?;
                }
                Ok(())
            },
        )?;
    }
    Ok(())
}

fn encode_frames(
    plan: &ExportPlan,
    audio_stream: &mut crate::pcm::Stream,
    writer: &crate::native_format::NativeWriterSession,
    receive: mpsc::Receiver<Result<EvaluatedFrame>>,
    control: &crate::exports::ExportControl,
) -> Result<()> {
    let deadline = Instant::now() + crate::pcm::STREAM_DEADLINE;
    let (mut video_frame, mut audio_sample) = (0_u64, 0_u64);
    let mut pending = None;
    while video_frame < plan.timeline.frame_count || audio_sample < plan.timeline_sample_frames {
        control.check()?;
        if Instant::now() > deadline || !writer.writing() {
            return Err(error("Native stream pump stopped or timed out"));
        }
        let mut progressed = false;
        if pending.is_none() && video_frame < plan.timeline.frame_count {
            match receive.try_recv() {
                Ok(frame) => pending = Some(frame?),
                Err(mpsc::TryRecvError::Empty) => {}
                Err(mpsc::TryRecvError::Disconnected) => {
                    return Err(error("Native decoder closed before timeline coverage"));
                }
            }
        }
        if pending.is_some() && writer.video_ready() {
            let evaluated: EvaluatedFrame = pending.take().expect("present frame");
            if evaluated.timeline_frame != video_frame {
                return Err(error(
                    "Native frame channel differs from immutable timeline order",
                ));
            }
            let image = evaluated.pixels.into_native()?;
            let pts = unsafe {
                CMTime::new(
                    i64::try_from(video_frame * u64::from(plan.settings.frame_rate.denominator))
                        .map_err(|_| error("Video PTS overflow"))?,
                    i32::try_from(plan.settings.frame_rate.numerator)
                        .map_err(|_| error("Video time scale overflow"))?,
                )
            };
            writer.append_picture(&image, pts, video_frame + 1 == plan.timeline.frame_count)?;
            video_frame += 1;
            progressed = true;
        }
        if audio_sample < plan.timeline_sample_frames && writer.audio_ready() {
            let chunk = audio_stream
                .next()?
                .ok_or_else(|| error("PCM stream ended before output coverage"))?;
            let end = audio_sample
                .checked_add(chunk.frames())
                .ok_or_else(|| error("Output audio clock overflow"))?;
            if chunk.first_sample != audio_sample
                || chunk.frames() == 0
                || chunk.frames() > crate::pcm::CHUNK_FRAMES
                || end > plan.timeline_sample_frames
            {
                return Err(error("PCM stream differs from the declared output clock"));
            }
            writer.append_audio(
                &chunk.samples,
                audio_sample,
                end == plan.timeline_sample_frames,
            )?;
            audio_sample = end;
            progressed = true;
        }
        if !progressed {
            std::thread::sleep(Duration::from_millis(1));
        }
    }
    if audio_stream.next()?.is_some()
        || audio_stream.evidence()?.sample_frames != plan.timeline_sample_frames
    {
        return Err(error("PCM stream has excess or missing samples"));
    }
    writer.finish(plan.timeline_sample_frames, control)
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NativeTrackEvidence {
    pub codec: String,
    pub sample_buffers: u64,
    pub raw_sample_pts_start: crate::MediaTime,
    pub raw_sample_pts_end: crate::MediaTime,
    pub audio_layout: Option<(u32, u32)>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub pcm_encoding: Option<crate::PcmEncodingEvidence>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NativeColorTupleEvidence {
    pub color_primaries: String,
    pub transfer_function: String,
    pub y_cb_cr_matrix: String,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NativeVideoColorEvidence {
    pub encoded_samples: NativeColorTupleEvidence,
    pub decoded_buffers: NativeColorTupleEvidence,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NativeMeasurements {
    pub video_frames: u64,
    pub audio_sample_frames: u64,
    pub width: u32,
    pub height: u32,
    pub full_video_decode: bool,
    pub audio_correlation: [f64; 2],
    pub video_track: NativeTrackEvidence,
    pub audio_track: NativeTrackEvidence,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub streaming_audio: Option<StreamingAudioEvidence>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub format: Option<crate::NativeFormatEvidence>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub pcm24_comparison: Option<crate::Pcm24Comparison>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub video_color: Option<NativeVideoColorEvidence>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StreamingAudioEvidence {
    pub source: crate::PcmStreamEvidence,
    pub output: crate::PcmStreamEvidence,
}

impl NativeMeasurements {
    pub(crate) fn compare(&self, fresh: &Self) -> Result<()> {
        if let Some(stored) = &self.streaming_audio {
            let observed = fresh
                .streaming_audio
                .as_ref()
                .ok_or_else(|| error("Streaming audio evidence is missing"))?;
            for (stored, observed) in [
                (&stored.source, &observed.source),
                (&stored.output, &observed.output),
            ] {
                if stored.source_start_sample != observed.source_start_sample
                    || stored.source_end_sample != observed.source_end_sample
                    || stored.sample_frames != observed.sample_frames
                    || stored.reader_reached_end != observed.reader_reached_end
                    || observed.maximum_owned_chunk_frames > crate::pcm::CHUNK_FRAMES
                {
                    return Err(StudioError::new(
                        "measurement_changed",
                        "Streaming audio clock or endpoint evidence changed",
                    ));
                }
            }
        }
        if self.video_frames != fresh.video_frames
            || self.audio_sample_frames != fresh.audio_sample_frames
            || self.width != fresh.width
            || self.height != fresh.height
            || self.full_video_decode != fresh.full_video_decode
            || self.video_track != fresh.video_track
            || self.audio_track != fresh.audio_track
            || self.format != fresh.format
            || self.pcm24_comparison != fresh.pcm24_comparison
            || self.video_color != fresh.video_color
            || self
                .audio_correlation
                .iter()
                .zip(fresh.audio_correlation)
                .any(|(stored, observed)| {
                    !stored.is_finite() || !observed.is_finite() || (stored - observed).abs() > 1e-9
                })
        {
            return Err(StudioError::new(
                "measurement_changed",
                "Fresh native measurements differ from the immutable producer receipt",
            ));
        }
        Ok(())
    }
}

struct EncodedTrackInspection {
    evidence: NativeTrackEvidence,
    video_color: Option<NativeColorTupleEvidence>,
}

fn retain_stable_color(
    retained: &mut Option<NativeColorTupleEvidence>,
    observed: Option<NativeColorTupleEvidence>,
    scope: &str,
) -> Result<()> {
    if let Some(observed) = observed {
        if retained
            .as_ref()
            .is_some_and(|retained| retained != &observed)
        {
            return Err(error(format!("{scope} color tuple changes")));
        }
        *retained = Some(observed);
    }
    Ok(())
}

fn inspect_encoded_track(
    path: &Path,
    kind: MediaKind,
    format_contract: crate::native_format::NativeFormatContract,
    control: Option<crate::exports::ExportControl>,
) -> Result<EncodedTrackInspection> {
    let wait_control = control.clone();
    let abort_control = control.clone();
    media::with_track_cancellable_hint(
        path,
        &kind.clone(),
        format_contract.output_mime(),
        crate::pcm::STREAM_DEADLINE,
        move || {
            wait_control
                .as_ref()
                .map_or(Ok(()), |control| control.check())
        },
        move || {
            if let Some(control) = &abort_control {
                control.interrupt();
            }
        },
        move |track| {
            let asset =
                unsafe { track.asset() }.ok_or_else(|| error("Encoded track lost asset"))?;
            let reader = unsafe { AVAssetReader::assetReaderWithAsset_error(&asset) }
                .map_err(|e| error(format!("{e:?}")))?;
            let _guard = ReaderGuard(&reader);
            let output = unsafe {
                AVAssetReaderTrackOutput::assetReaderTrackOutputWithTrack_outputSettings(
                    track, None,
                )
            };
            if !unsafe { reader.canAddOutput(&output) } {
                return Err(error("Encoded track reader rejected output"));
            }
            unsafe { reader.addOutput(&output) };
            if !unsafe { reader.startReading() } {
                return Err(error("Encoded track reader did not start"));
            }
            let mut codec = None;
            let mut audio_layout = None;
            let mut pcm_encoding = None;
            let mut video_color = None;
            let mut sample_buffers = 0_u64;
            let mut start: Option<crate::MediaTime> = None;
            let mut end: Option<crate::MediaTime> = None;
            let deadline = Instant::now() + crate::pcm::STREAM_DEADLINE;
            while let Some(sample) = unsafe { output.copyNextSampleBuffer() } {
                if let Some(control) = &control {
                    control.check()?;
                }
                if Instant::now() > deadline {
                    return Err(error("Encoded track verification deadline expired"));
                }
                if unsafe { sample.num_samples() } == 0 {
                    continue;
                }
                let format = unsafe { sample.format_description() }
                    .ok_or_else(|| error("Encoded sample has no format"))?;
                if kind == MediaKind::Movie {
                    retain_stable_color(
                        &mut video_color,
                        format_contract.observe_encoded_video_color(&format)?,
                        "Encoded sample",
                    )?;
                }
                let subtype = unsafe { format.media_sub_type() };
                let measured_codec = String::from_utf8(subtype.to_be_bytes().to_vec())
                    .map_err(|_| error("Encoded codec is not ASCII"))?;
                crate::FourCc::try_from(measured_codec.clone())?;
                if codec.as_ref().is_some_and(|value| value != &measured_codec) {
                    return Err(error("Encoded track codec changes"));
                }
                codec = Some(measured_codec);
                let pts = unsafe { sample.presentation_time_stamp() };
                let last = unsafe { pts.add(sample.duration()) };
                let first = media::time(pts)?;
                let last = media::time(last)?;
                if start
                    .as_ref()
                    .is_none_or(|value| first.compare(value).is_lt())
                {
                    start = Some(first);
                }
                if end.as_ref().is_none_or(|value| last.compare(value).is_gt()) {
                    end = Some(last);
                }
                if kind == MediaKind::Audio {
                    let pointer =
                        unsafe { CMAudioFormatDescriptionGetStreamBasicDescription(&format) };
                    let layout = unsafe { pointer.as_ref() }
                        .ok_or_else(|| error("Encoded audio has no layout"))?;
                    if !layout.mSampleRate.is_finite() || layout.mSampleRate.fract() != 0.0 {
                        return Err(error("Encoded audio has fractional clock"));
                    }
                    let measured = (layout.mSampleRate as u32, layout.mChannelsPerFrame);
                    if audio_layout.is_some_and(|value| value != measured) {
                        return Err(error("Encoded audio layout changes"));
                    }
                    audio_layout = Some(measured);
                    if format_contract.is_master() {
                        let measured = crate::PcmEncodingEvidence {
                            format_id: layout.mFormatID,
                            format_flags: layout.mFormatFlags,
                            bits_per_channel: layout.mBitsPerChannel,
                            bytes_per_frame: layout.mBytesPerFrame,
                            bytes_per_packet: layout.mBytesPerPacket,
                            frames_per_packet: layout.mFramesPerPacket,
                        };
                        if pcm_encoding
                            .as_ref()
                            .is_some_and(|value| value != &measured)
                        {
                            return Err(error("Encoded PCM layout changes"));
                        }
                        pcm_encoding = Some(measured);
                    }
                }
                sample_buffers += 1;
            }
            if unsafe { reader.status() } != AVAssetReaderStatus::Completed {
                return Err(error("Encoded track verification did not finish"));
            }
            Ok(EncodedTrackInspection {
                evidence: NativeTrackEvidence {
                    codec: codec.ok_or_else(|| error("Encoded track has no samples"))?,
                    sample_buffers,
                    raw_sample_pts_start: start
                        .ok_or_else(|| error("Encoded track has no start"))?,
                    raw_sample_pts_end: end.ok_or_else(|| error("Encoded track has no end"))?,
                    audio_layout,
                    pcm_encoding,
                },
                video_color,
            })
        },
    )
}
pub(crate) struct InputDecodeEvidence {
    pub movie: Vec<crate::plan::SourceDecodeEvidence>,
    pub image: Vec<crate::plan::ImageDecodeEvidence>,
}

pub(crate) fn verify_inputs(plan: &ExportPlan, blobs: &Path) -> Result<InputDecodeEvidence> {
    let mut receipts = Vec::new();
    let mut images = Vec::new();
    let mut plan7_images = BTreeSet::new();
    for use_ in &plan.video {
        let path = blobs.join(use_.asset.as_str());
        let asset = use_.asset.clone();
        let selected = use_.allowed_source_samples.clone();
        let stored = &plan.source_closure[&asset];
        if let MediaDescriptor::Image {
            width,
            height,
            rgba_sha256,
            alpha,
            ..
        } = &stored.descriptor
        {
            if plan.schema == 7 && !plan7_images.insert(asset.clone()) {
                continue;
            }
            crate::image::decode_picture_asset(&path, stored)?;
            images.push(crate::plan::ImageDecodeEvidence {
                source_alpha_id: alpha
                    .as_ref()
                    .map(|alpha| crate::alpha_picture::source_alpha_id(&asset, rgba_sha256, alpha))
                    .transpose()?,
                asset,
                width: *width,
                height: *height,
                rgba_sha256: rgba_sha256.clone(),
                decoder_executable_sha256: plan.renderer.executable_sha256.clone(),
            });
            continue;
        }
        let MediaDescriptor::Movie {
            samples,
            width,
            height,
            ..
        } = &plan.source_closure[&asset].descriptor
        else {
            return Err(error("Selected source is not a movie"));
        };
        let samples = samples.clone();
        let (width, height) = (*width, *height);
        let end = selected.end()?;
        let selected_copy = selected.clone();
        let observed = media::with_track_deadline(
            &path,
            &MediaKind::Movie,
            crate::pcm::STREAM_DEADLINE,
            move |track| {
                let asset = unsafe { track.asset() }
                    .ok_or_else(|| error("Decode-proof track has no asset"))?;
                let reader = unsafe { AVAssetReader::assetReaderWithAsset_error(&asset) }
                    .map_err(|e| error(format!("{e:?}")))?;
                let _guard = ReaderGuard(&reader);
                let pixels =
                    dictionary(vec![("PixelFormatType", number(kCVPixelFormatType_32BGRA))]);
                let output = unsafe {
                    AVAssetReaderTrackOutput::assetReaderTrackOutputWithTrack_outputSettings(
                        track,
                        Some(&pixels),
                    )
                };
                if !unsafe { reader.canAddOutput(&output) } {
                    return Err(error("Selected-range decoder rejected BGRA"));
                }
                unsafe { reader.addOutput(&output) };
                if !unsafe { reader.startReading() } {
                    return Err(error("Selected-range decoder did not start"));
                }
                let mut ordinal = 0_u64;
                let mut observed = 0_u64;
                let deadline = Instant::now() + crate::pcm::STREAM_DEADLINE;
                while ordinal < end {
                    if Instant::now() > deadline {
                        return Err(error("Selected-range decode deadline expired"));
                    }
                    let sample = unsafe { output.copyNextSampleBuffer() }.ok_or_else(|| {
                        error(format!("Selected-range decode ended early: {:?}", unsafe {
                            reader.error()
                        }))
                    })?;
                    let pts = unsafe { sample.presentation_time_stamp() };
                    let expected = &samples
                        .get(ordinal as usize)
                        .ok_or_else(|| error("Decoder exceeded immutable sample index"))?
                        .pts;
                    if pts.timescale <= 0
                        || pts.epoch != 0
                        || i128::from(pts.value) * i128::from(expected.timescale)
                            != i128::from(expected.ticks) * i128::from(pts.timescale)
                    {
                        return Err(error(
                            "Selected-range decode PTS differs from immutable source index",
                        ));
                    }
                    let image = unsafe { sample.image_buffer() }
                        .ok_or_else(|| error("Selected-range sample has no image"))?;
                    if CVPixelBufferGetWidth(&image) != width as usize
                        || CVPixelBufferGetHeight(&image) != height as usize
                    {
                        return Err(error("Selected-range dimensions changed"));
                    }
                    if ordinal >= selected_copy.start {
                        observed += 1;
                    }
                    ordinal += 1;
                }
                Ok(observed)
            },
        )?;
        receipts.push(crate::plan::SourceDecodeEvidence {
            asset,
            source_samples: selected,
            decoded_samples: observed,
            pts_verified: true,
            decoder_executable_sha256: plan.renderer.executable_sha256.clone(),
        });
    }
    if plan.schema == 7 {
        images.sort_by(|a, b| a.asset.cmp(&b.asset));
    }
    Ok(InputDecodeEvidence {
        movie: receipts,
        image: images,
    })
}

fn compare_audio_streams(
    movie: &Path,
    source: &Path,
    selection: Span,
    expected: u64,
    format: crate::native_format::NativeFormatContract,
    control: Option<crate::exports::ExportControl>,
) -> Result<(
    [f64; 2],
    StreamingAudioEvidence,
    Option<crate::Pcm24Comparison>,
)> {
    let mut original = crate::pcm::Stream::open(source, Some(selection), control.clone())?;
    let mut output =
        crate::pcm::Stream::open_with_hint(movie, None, control, format.output_mime())?;
    let mut reference = None;
    let mut reference_offset = 0usize;
    let mut consumed_reference = 0u64;
    let mut consumed_output = 0u64;
    let (mut dot, mut source_power, mut output_power) = ([0.0f64; 2], [0.0f64; 2], [0.0f64; 2]);
    while let Some(chunk) = output.next()? {
        if chunk.first_sample != consumed_output {
            return Err(error("Reopened audio chunks are discontinuous"));
        }
        for values in chunk.samples.chunks_exact(2) {
            if reference
                .as_ref()
                .is_none_or(|chunk: &crate::pcm::PcmChunk| reference_offset == chunk.samples.len())
            {
                let chunk = original
                    .next()?
                    .ok_or_else(|| error("Source audio ended before reopened output"))?;
                if chunk.first_sample != consumed_reference {
                    return Err(error("Source PCM chunks are discontinuous"));
                }
                reference = Some(chunk);
                reference_offset = 0;
            }
            let chunk = reference.as_ref().expect("reference chunk loaded");
            for channel in 0..2 {
                if format.is_master() {
                    let source_code = crate::native_format::pcm24_code(
                        chunk.samples[reference_offset + channel],
                    )?;
                    let output_code = crate::native_format::pcm24_code(values[channel])?;
                    if source_code != output_code
                        || f64::from(values[channel]) != f64::from(output_code) / 8388608.0
                    {
                        return Err(error("Reopened PCM24 code differs from selected source"));
                    }
                }
                let a = f64::from(chunk.samples[reference_offset + channel]);
                let b = f64::from(values[channel]);
                dot[channel] += a * b;
                source_power[channel] += a * a;
                output_power[channel] += b * b;
            }
            reference_offset += 2;
            consumed_reference += 1;
            consumed_output += 1;
            if consumed_output > expected {
                return Err(error("Reopened audio has excess samples"));
            }
        }
    }
    if consumed_output != expected
        || reference
            .as_ref()
            .is_some_and(|chunk| reference_offset != chunk.samples.len())
        || original.next()?.is_some()
    {
        return Err(error(
            "Source and reopened audio do not cover the exact plan clock",
        ));
    }
    let mut correlation = [0.0; 2];
    for channel in 0..2 {
        correlation[channel] = if source_power[channel] == 0.0 && output_power[channel] == 0.0 {
            1.0
        } else if source_power[channel] == 0.0 || output_power[channel] == 0.0 {
            0.0
        } else {
            dot[channel] / (source_power[channel] * output_power[channel]).sqrt()
        };
        if !correlation[channel].is_finite() || correlation[channel] < 0.99 {
            return Err(error(
                "Reopened waveform differs from selected source audio",
            ));
        }
    }
    Ok((
        correlation,
        StreamingAudioEvidence {
            source: original.evidence()?.clone(),
            output: output.evidence()?.clone(),
        },
        format.is_master().then_some(crate::Pcm24Comparison {
            sample_frames: consumed_output,
            maximum_code_delta: 0,
        }),
    ))
}

pub(crate) fn verify(plan: &ExportPlan, blobs: &Path, movie: &Path) -> Result<NativeMeasurements> {
    verify_inner(plan, blobs, movie, None)
}

pub(crate) fn verify_owned(
    plan: &ExportPlan,
    blobs: &Path,
    movie: &Path,
    control: crate::exports::ExportControl,
) -> Result<NativeMeasurements> {
    verify_inner(plan, blobs, movie, Some(control))
}

fn verify_inner(
    plan: &ExportPlan,
    blobs: &Path,
    movie: &Path,
    control: Option<crate::exports::ExportControl>,
) -> Result<NativeMeasurements> {
    let format_contract = crate::native_format::NativeFormatContract::for_profile(&plan.profile)?;
    if let Some(control) = &control {
        control.check()?;
    }
    let format = format_contract.inspect_container(movie)?;
    let video_inspection =
        inspect_encoded_track(movie, MediaKind::Movie, format_contract, control.clone())?;
    let audio_inspection =
        inspect_encoded_track(movie, MediaKind::Audio, format_contract, control.clone())?;
    let encoded_color = video_inspection.video_color;
    let video_track = video_inspection.evidence;
    let audio_track = audio_inspection.evidence;
    let rate = &plan.settings.frame_rate;
    if video_track.sample_buffers != plan.timeline.frame_count
        || (i128::from(video_track.raw_sample_pts_end.ticks)
            * i128::from(video_track.raw_sample_pts_start.timescale)
            - i128::from(video_track.raw_sample_pts_start.ticks)
                * i128::from(video_track.raw_sample_pts_end.timescale))
            * i128::from(rate.numerator)
            != i128::from(plan.timeline.frame_count)
                * i128::from(rate.denominator)
                * i128::from(video_track.raw_sample_pts_start.timescale)
                * i128::from(video_track.raw_sample_pts_end.timescale)
        || audio_track.audio_layout != Some((plan.settings.audio_rate, plan.settings.channels))
    {
        return Err(error(format!(
            "Native encoded tracks differ from the requested profile or duration: video={video_track:?}, audio={audio_track:?}"
        )));
    }
    let plan_copy = plan.clone();
    let video_control = control.clone();
    let wait_control = control.clone();
    let abort_control = control.clone();
    let (frame_count, decoded_color) = media::with_track_cancellable_hint(
        movie,
        &MediaKind::Movie,
        format_contract.output_mime(),
        crate::pcm::STREAM_DEADLINE,
        move || {
            wait_control
                .as_ref()
                .map_or(Ok(()), |control| control.check())
        },
        move || {
            if let Some(control) = &abort_control {
                control.interrupt();
            }
        },
        move |track| {
            let asset =
                unsafe { track.asset() }.ok_or_else(|| error("Verification track has no asset"))?;
            let reader = unsafe { AVAssetReader::assetReaderWithAsset_error(&asset) }
                .map_err(|e| error(format!("{e:?}")))?;
            let _guard = ReaderGuard(&reader);
            let pixels = dictionary(vec![("PixelFormatType", number(kCVPixelFormatType_32BGRA))]);
            let output = unsafe {
                AVAssetReaderTrackOutput::assetReaderTrackOutputWithTrack_outputSettings(
                    track,
                    Some(&pixels),
                )
            };
            if !unsafe { reader.canAddOutput(&output) } {
                return Err(error("Verification reader rejected video decode"));
            }
            unsafe { reader.addOutput(&output) };
            if !unsafe { reader.startReading() } {
                return Err(error("Verification reader did not start"));
            }
            let mut count = 0_u64;
            let mut decoded_color = None;
            let deadline = Instant::now() + crate::pcm::STREAM_DEADLINE;
            while let Some(sample) = unsafe { output.copyNextSampleBuffer() } {
                if let Some(control) = &video_control {
                    control.check()?;
                }
                if Instant::now() > deadline {
                    return Err(error("Output video verification deadline expired"));
                }
                if count >= plan_copy.timeline.frame_count {
                    return Err(error("Export has excess video samples"));
                }
                let pts = unsafe { sample.presentation_time_stamp() };
                let rate = &plan_copy.settings.frame_rate;
                if pts.timescale <= 0
                    || pts.epoch != 0
                    || pts.flags.0 & 1 == 0
                    || pts.flags.0 & 28 != 0
                    || i128::from(pts.value) * i128::from(rate.numerator)
                        != i128::from(count)
                            * i128::from(rate.denominator)
                            * i128::from(pts.timescale)
                {
                    return Err(error("Export video timestamp differs from plan"));
                }
                let image = unsafe { sample.image_buffer() }
                    .ok_or_else(|| error("Verification sample has no pixel buffer"))?;
                retain_stable_color(
                    &mut decoded_color,
                    format_contract.observe_decoded_video_color(&image)?,
                    "Decoded buffer",
                )?;
                if CVPixelBufferGetWidth(&image) != plan_copy.settings.width as usize
                    || CVPixelBufferGetHeight(&image) != plan_copy.settings.height as usize
                {
                    return Err(error("Export picture dimensions differ from plan"));
                }
                crate::pixels::require_opaque_native(&image, || {
                    video_control
                        .as_ref()
                        .map_or(Ok(()), |control| control.check())
                })?;
                count += 1;
            }
            if count != plan_copy.timeline.frame_count
                || unsafe { reader.status() } != AVAssetReaderStatus::Completed
            {
                return Err(error(
                    "Export video decode did not complete with planned coverage",
                ));
            }
            Ok((count, decoded_color))
        },
    )?;
    let (correlation, streaming_audio, pcm24_comparison) = compare_audio_streams(
        movie,
        &blobs.join(plan.audio[0].clip.asset.as_str()),
        plan.audio[0].clip.source_samples.clone(),
        plan.timeline_sample_frames,
        format_contract,
        control,
    )?;
    let video_color = format_contract.finish_video_color(encoded_color, decoded_color)?;
    let measurements = NativeMeasurements {
        video_frames: frame_count,
        audio_sample_frames: plan.timeline_sample_frames,
        width: plan.settings.width,
        height: plan.settings.height,
        full_video_decode: true,
        audio_correlation: correlation,
        video_track,
        audio_track,
        streaming_audio: Some(streaming_audio),
        format,
        pcm24_comparison,
        video_color,
    };
    format_contract.validate_measurements(&measurements)?;
    Ok(measurements)
}

#[cfg(test)]
mod color_tests {
    use super::*;

    fn color(value: &str) -> NativeColorTupleEvidence {
        NativeColorTupleEvidence {
            color_primaries: value.into(),
            transfer_function: value.into(),
            y_cb_cr_matrix: value.into(),
        }
    }

    #[test]
    fn complete_track_observation_rejects_a_changing_middle_tuple() {
        let mut retained = None;
        retain_stable_color(&mut retained, Some(color("ITU_R_709_2")), "encoded").unwrap();
        assert!(retain_stable_color(&mut retained, Some(color("ITU_R_601_4")), "encoded").is_err());
        retain_stable_color(&mut retained, Some(color("ITU_R_709_2")), "encoded").unwrap();
    }
}
