use std::io::Read;
use std::path::Path;
use std::sync::mpsc;
use std::sync::{
    Arc, Mutex,
    atomic::{AtomicBool, Ordering},
};
use std::time::{Duration, Instant};

use block2::RcBlock;
use objc2::rc::{Retained, autoreleasepool};
use objc2::runtime::AnyObject;
use objc2_av_foundation::{
    AVAssetReader, AVAssetReaderStatus, AVAssetReaderTrackOutput, AVAssetReferenceRestrictions,
    AVAssetTrack, AVMediaTypeAudio, AVMediaTypeVideo, AVURLAsset, AVURLAssetOverrideMIMETypeKey,
    AVURLAssetReferenceRestrictionsKey,
};
use objc2_core_media::{CMAudioFormatDescriptionGetStreamBasicDescription, CMTime};
use objc2_core_video::{CVPixelBufferGetHeight, CVPixelBufferGetWidth, kCVPixelFormatType_32BGRA};
use objc2_foundation::{NSArray, NSDictionary, NSError, NSNumber, NSString, NSURL};

use crate::{MediaDescriptor, MediaKind, MediaTime, Result, SampleTiming, StudioError};

fn native_error(detail: impl Into<String>) -> StudioError {
    StudioError::new("native_media_error", detail)
}
pub(crate) fn time(value: CMTime) -> Result<MediaTime> {
    let ticks = value.value;
    let timescale = value.timescale;
    if timescale <= 0 || value.epoch != 0 || value.flags.0 & 1 == 0 || value.flags.0 & 28 != 0 {
        return Err(native_error("Non-numeric or unsupported media clock"));
    }
    Ok(MediaTime {
        ticks,
        timescale: timescale as u32,
    })
}

pub(crate) fn probe(path: &Path, kind: &MediaKind) -> Result<MediaDescriptor> {
    if *kind == MediaKind::Image {
        return crate::image::probe(path);
    }
    let kind = kind.clone();
    let selected = kind.clone();
    with_track(path, &selected, move |track| inspect_track(track, &kind))
}

pub(crate) fn with_track<T: Send + 'static>(
    path: &Path,
    kind: &MediaKind,
    operation: impl FnOnce(&AVAssetTrack) -> Result<T> + Send + 'static,
) -> Result<T> {
    with_track_deadline(path, kind, Duration::from_secs(120), operation)
}

pub(crate) fn with_track_deadline<T: Send + 'static>(
    path: &Path,
    kind: &MediaKind,
    deadline: Duration,
    operation: impl FnOnce(&AVAssetTrack) -> Result<T> + Send + 'static,
) -> Result<T> {
    with_track_cancellable(path, kind, deadline, || Ok(()), || {}, operation)
}

pub(crate) fn with_track_cancellable<T: Send + 'static>(
    path: &Path,
    kind: &MediaKind,
    deadline: Duration,
    check: impl Fn() -> Result<()> + Send + Sync + 'static,
    cancel: impl Fn(),
    operation: impl FnOnce(&AVAssetTrack) -> Result<T> + Send + 'static,
) -> Result<T> {
    with_track_cancellable_hint(path, kind, None, deadline, check, cancel, operation)
}

pub(crate) fn with_track_cancellable_hint<T: Send + 'static>(
    path: &Path,
    kind: &MediaKind,
    mime_hint: Option<&'static str>,
    deadline: Duration,
    check: impl Fn() -> Result<()> + Send + Sync + 'static,
    cancel: impl Fn(),
    operation: impl FnOnce(&AVAssetTrack) -> Result<T> + Send + 'static,
) -> Result<T> {
    check()?;
    let check = Arc::new(check);
    let cancelled = Arc::new(AtomicBool::new(false));
    let canonical = path.canonicalize()?;
    let url = NSURL::fileURLWithPath(&NSString::from_str(
        canonical
            .to_str()
            .ok_or_else(|| native_error("Non-UTF-8 media path"))?,
    ));
    let mut header = [0; 12];
    std::fs::File::open(&canonical)?.read_exact(&mut header)?;
    let mime = if let Some(mime) = mime_hint {
        mime
    } else if &header[..4] == b"RIFF" && &header[8..12] == b"WAVE" {
        "audio/wav"
    } else if &header[4..8] == b"ftyp" {
        "video/mp4"
    } else if matches!(&header[4..8], b"moov" | b"mdat" | b"wide" | b"free") {
        "video/quicktime"
    } else {
        return Err(StudioError::new(
            "unsupported_container",
            "Owned media container is not recognized by its header",
        ));
    };
    let mime_value: Retained<AnyObject> =
        unsafe { Retained::cast_unchecked(NSString::from_str(mime)) };
    let restrictions: Retained<AnyObject> = unsafe {
        Retained::cast_unchecked(NSNumber::new_usize(
            AVAssetReferenceRestrictions::ForbidAll.0,
        ))
    };
    let options = NSDictionary::from_slices(
        &[unsafe { AVURLAssetOverrideMIMETypeKey }, unsafe {
            AVURLAssetReferenceRestrictionsKey
        }],
        &[&*mime_value, &*restrictions],
    );
    let asset = unsafe { AVURLAsset::URLAssetWithURL_options(&url, Some(&options)) };
    let media_type = match kind {
        MediaKind::Movie => unsafe { AVMediaTypeVideo },
        MediaKind::Audio => unsafe { AVMediaTypeAudio },
        MediaKind::Image => {
            return Err(StudioError::new(
                "wrong_stream",
                "Static images do not have an AVFoundation media track",
            ));
        }
    }
    .ok_or_else(|| native_error("Native media type unavailable"))?;
    let (send, receive) = mpsc::channel();
    let callback_check = check.clone();
    let callback_cancelled = cancelled.clone();
    let operation = Mutex::new(Some(operation));
    // The callback captures only Send-owned Rust values. Framework objects stay on
    // the callback thread and never enter the channel or the domain layer.
    let callback = RcBlock::new(
        move |tracks: *mut NSArray<AVAssetTrack>, error: *mut NSError| {
            let caught = objc2::exception::catch(std::panic::AssertUnwindSafe(|| {
                autoreleasepool(|_| {
                    if callback_cancelled.load(Ordering::Acquire) {
                        return Err(native_error(
                            "Native track operation was cancelled before it started",
                        ));
                    }
                    callback_check()?;
                    if let Some(error) = unsafe { error.as_ref() } {
                        return Err(native_error(format!("Track load failed: {error:?}")));
                    }
                    let tracks = unsafe { tracks.as_ref() }
                        .ok_or_else(|| native_error("Track loading returned no array"))?;
                    if tracks.count() != 1 {
                        return Err(StudioError::new(
                            "unsupported_tracks",
                            "Import requires exactly one selected media track",
                        ));
                    }
                    let track = tracks
                        .firstObject()
                        .ok_or_else(|| native_error("No selected media track"))?;
                    let operation = operation
                        .lock()
                        .map_err(|_| native_error("Native track operation ownership was poisoned"))?
                        .take()
                        .ok_or_else(|| native_error("Native track operation already started"))?;
                    operation(&track)
                })
            }));
            let result = match caught {
                Ok(result) => result,
                Err(exception) => Err(StudioError::new(
                    "native_exception",
                    format!("{exception:?}"),
                )),
            };
            let _ = send.send(result);
        },
    );
    unsafe { asset.loadTracksWithMediaType_completionHandler(media_type, &callback) };
    wait_for_result(
        &receive,
        deadline,
        || check(),
        || {
            cancelled.store(true, Ordering::Release);
            cancel();
            unsafe { asset.cancelLoading() };
        },
    )
}

fn wait_for_result<T>(
    receive: &mpsc::Receiver<Result<T>>,
    duration: Duration,
    check: impl Fn() -> Result<()>,
    cancel: impl Fn(),
) -> Result<T> {
    let deadline = Instant::now() + duration;
    loop {
        if let Err(error) = check() {
            cancel();
            return Err(error);
        }
        if Instant::now() >= deadline {
            cancel();
            return Err(native_error("Native operation deadline expired"));
        }
        match receive.recv_timeout(
            Duration::from_millis(25).min(deadline.saturating_duration_since(Instant::now())),
        ) {
            Ok(result) => return result,
            Err(mpsc::RecvTimeoutError::Timeout) => {}
            Err(mpsc::RecvTimeoutError::Disconnected) => {
                cancel();
                return Err(native_error("Native operation closed without a result"));
            }
        }
    }
}

pub(crate) fn host_identity() -> (String, String) {
    use objc2_foundation::{NSBundle, NSProcessInfo};
    let host = NSProcessInfo::processInfo()
        .operatingSystemVersionString()
        .to_string();
    let framework = {
        NSBundle::bundleWithPath(&NSString::from_str(
            "/System/Library/Frameworks/AVFoundation.framework",
        ))
    }
    .and_then(|bundle| bundle.objectForInfoDictionaryKey(&NSString::from_str("CFBundleVersion")))
    .and_then(|value| {
        value
            .downcast_ref::<NSString>()
            .map(|string| string.to_string())
    })
    .unwrap_or_else(|| "unavailable".into());
    (
        host,
        format!("objc2 AVFoundation bindings 0.3.2 / AVFoundation bundle {framework}"),
    )
}

fn inspect_track(track: &AVAssetTrack, kind: &MediaKind) -> Result<MediaDescriptor> {
    let asset =
        unsafe { track.asset() }.ok_or_else(|| native_error("Loaded track lost its asset"))?;
    let reader = unsafe { AVAssetReader::assetReaderWithAsset_error(&asset) }
        .map_err(|e| native_error(format!("{e:?}")))?;
    let output = unsafe {
        AVAssetReaderTrackOutput::assetReaderTrackOutputWithTrack_outputSettings(track, None)
    };
    if !unsafe { reader.canAddOutput(&output) } {
        return Err(native_error("Reader rejected original sample output"));
    }
    unsafe { reader.addOutput(&output) };
    if !unsafe { reader.startReading() } {
        return Err(native_error(format!(
            "Sample index start failed: {:?}",
            unsafe { reader.error() }
        )));
    }
    let mut samples = Vec::new();
    let mut codec = None;
    let mut audio_layout = None;
    let mut audio_frames = 0_u64;
    while let Some(sample) = unsafe { output.copyNextSampleBuffer() } {
        let count = unsafe { sample.num_samples() };
        if count == 0 {
            continue;
        }
        let description = unsafe { sample.format_description() }
            .ok_or_else(|| native_error("Sample description is absent"))?;
        let subtype = unsafe { description.media_sub_type() };
        let measured_codec = String::from_utf8_lossy(&subtype.to_be_bytes()).into_owned();
        if codec.as_ref().is_some_and(|v| v != &measured_codec) {
            return Err(StudioError::new(
                "unsupported_format_change",
                "Track changes codec within one asset",
            ));
        }
        codec = Some(measured_codec);
        match kind {
            MediaKind::Movie => {
                if count != 1 || samples.len() >= 100000 {
                    return Err(StudioError::new(
                        "unsupported_sample_index",
                        "Movie sample packing or count exceeds supported index",
                    ));
                }
                let encoded_pts = time(unsafe { sample.presentation_time_stamp() })?;
                let pts = time(unsafe { sample.output_presentation_time_stamp() })?;
                let encoded_dts = time(unsafe { sample.decode_time_stamp() }).ok();
                let dts = time(unsafe { sample.output_decode_time_stamp() }).ok();
                let encoded_duration = time(unsafe { sample.duration() })?;
                let duration = time(unsafe { sample.output_duration() })?;
                if duration.ticks <= 0 {
                    return Err(native_error("Movie sample has a nonpositive duration"));
                }
                let encoded_time =
                    if encoded_pts != pts || encoded_dts != dts || encoded_duration != duration {
                        Some(crate::EncodedTiming {
                            pts: encoded_pts,
                            duration: encoded_duration,
                            dts: encoded_dts,
                        })
                    } else {
                        None
                    };
                samples.push(SampleTiming {
                    ordinal: 0,
                    pts,
                    dts,
                    duration,
                    sync_sample: None,
                    encoded_time,
                });
            }
            MediaKind::Audio => {
                let pointer =
                    unsafe { CMAudioFormatDescriptionGetStreamBasicDescription(&description) };
                let layout = unsafe { pointer.as_ref() }
                    .ok_or_else(|| native_error("Audio layout absent"))?;
                if layout.mFormatID != 0x6c70636d
                    || layout.mSampleRate.fract() != 0.0
                    || !(1.0..=192000.0).contains(&layout.mSampleRate)
                    || !(1..=8).contains(&layout.mChannelsPerFrame)
                {
                    return Err(StudioError::new(
                        "unsupported_audio_import",
                        "Current audio import requires original linear PCM with an integer sample clock",
                    ));
                }
                let current = (
                    layout.mSampleRate as u32,
                    layout.mChannelsPerFrame,
                    layout.mBitsPerChannel,
                    layout.mFormatFlags,
                );
                if audio_layout.is_some_and(|value| value != current) {
                    return Err(StudioError::new(
                        "unsupported_format_change",
                        "Audio layout changes within source",
                    ));
                }
                audio_layout = Some(current);
                let pts = time(unsafe { sample.presentation_time_stamp() })?;
                if i128::from(pts.ticks) * i128::from(current.0)
                    != i128::from(audio_frames) * i128::from(pts.timescale)
                {
                    return Err(native_error(
                        "PCM source sample timing is discontinuous from zero",
                    ));
                }
                audio_frames = audio_frames
                    .checked_add(
                        u64::try_from(count)
                            .map_err(|_| native_error("Negative audio sample count"))?,
                    )
                    .ok_or_else(|| native_error("Audio sample count overflow"))?;
            }
            MediaKind::Image => {
                return Err(native_error(
                    "Static image cannot be indexed as a timed media track",
                ));
            }
        }
    }
    if unsafe { reader.status() } != AVAssetReaderStatus::Completed {
        return Err(native_error(format!(
            "Sample indexing did not complete: {:?}",
            unsafe { reader.error() }
        )));
    }
    let codec = codec.ok_or_else(|| native_error("Native reader returned no samples"))?;
    match kind {
        MediaKind::Audio => {
            let (rate, channels, bits, format_flags) =
                audio_layout.ok_or_else(|| native_error("No PCM layout"))?;
            Ok(MediaDescriptor::Audio {
                codec,
                rate,
                channels,
                sample_frames: audio_frames,
                bits,
                format_flags,
                measured_channel_labels: None,
            })
        }
        MediaKind::Movie => {
            samples.sort_by(|a, b| a.pts.compare(&b.pts));
            for index in 0..samples.len() {
                samples[index].ordinal = index as u64;
                if index > 0
                    && samples[index - 1].pts.compare(&samples[index].pts)
                        != std::cmp::Ordering::Less
                {
                    return Err(native_error("Movie presentation timestamps are not unique"));
                }
            }
            let (width, height, native_decode, decode_error) = decode_first(track)?;
            Ok(MediaDescriptor::Movie { codec,width,height,samples,native_decode,decode_error,warnings:vec!["Source sync flags, aperture, orientation and color metadata are not verified yet".into(),"Native decode observation covers only the first sample; full decode remains separate".into()] })
        }
        MediaKind::Image => Err(native_error(
            "Static image cannot be measured as a timed media track",
        )),
    }
}

fn decode_first(track: &AVAssetTrack) -> Result<(u32, u32, bool, Option<String>)> {
    let asset = unsafe { track.asset() }.ok_or_else(|| native_error("Track has no asset"))?;
    let reader = unsafe { AVAssetReader::assetReaderWithAsset_error(&asset) }
        .map_err(|e| native_error(format!("{e:?}")))?;
    let key = NSString::from_str("PixelFormatType");
    let value: Retained<AnyObject> =
        unsafe { Retained::cast_unchecked(NSNumber::new_u32(kCVPixelFormatType_32BGRA)) };
    let settings = NSDictionary::from_slices(&[&*key], &[&*value]);
    let output = unsafe {
        AVAssetReaderTrackOutput::assetReaderTrackOutputWithTrack_outputSettings(
            track,
            Some(&settings),
        )
    };
    if !unsafe { reader.canAddOutput(&output) } {
        return Ok((
            0,
            0,
            false,
            Some("Native reader rejected BGRA decoding".into()),
        ));
    }
    unsafe { reader.addOutput(&output) };
    let sample = if unsafe { reader.startReading() } {
        unsafe { output.copyNextSampleBuffer() }
    } else {
        None
    };
    let result = match sample.and_then(|sample| unsafe { sample.image_buffer() }) {
        Some(image) => (
            u32::try_from(CVPixelBufferGetWidth(&image))
                .map_err(|_| native_error("Image width overflow"))?,
            u32::try_from(CVPixelBufferGetHeight(&image))
                .map_err(|_| native_error("Image height overflow"))?,
            true,
            None,
        ),
        None => (
            0,
            0,
            false,
            Some(format!("Native first-sample decode failed: {:?}", unsafe {
                reader.error()
            })),
        ),
    };
    unsafe { reader.cancelReading() };
    Ok(result)
}

#[cfg(test)]
mod wait_tests {
    use super::*;

    #[test]
    fn a_live_track_wait_observes_cancellation_before_the_operation_starts() {
        let (_sender, receiver) = mpsc::channel::<Result<()>>();
        let cancelled = Arc::new(AtomicBool::new(false));
        let setter = cancelled.clone();
        let worker = std::thread::spawn(move || {
            std::thread::sleep(Duration::from_millis(10));
            setter.store(true, Ordering::Release);
        });
        let aborted = AtomicBool::new(false);
        let started = Instant::now();
        let result = wait_for_result(
            &receiver,
            Duration::from_secs(1800),
            || {
                if cancelled.load(Ordering::Acquire) {
                    Err(StudioError::new("export_interrupted", "test cancellation"))
                } else {
                    Ok(())
                }
            },
            || aborted.store(true, Ordering::Release),
        );
        worker.join().unwrap();
        assert_eq!(result.unwrap_err().code, "export_interrupted");
        assert!(aborted.load(Ordering::Acquire));
        assert!(started.elapsed() < Duration::from_secs(1));
    }

    #[test]
    fn a_track_wait_deadline_aborts_a_still_live_request() {
        let (_sender, receiver) = mpsc::channel::<Result<()>>();
        let aborted = AtomicBool::new(false);
        assert_eq!(
            wait_for_result(
                &receiver,
                Duration::from_millis(5),
                || Ok(()),
                || aborted.store(true, Ordering::Release)
            )
            .unwrap_err()
            .code,
            "native_media_error"
        );
        assert!(aborted.load(Ordering::Acquire));
    }
}
