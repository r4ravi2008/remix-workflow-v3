use std::path::Path;
use std::ptr::NonNull;
use std::sync::mpsc;
use std::time::{Duration, Instant};

use block2::RcBlock;
use objc2::rc::Retained;
use objc2::runtime::AnyObject;
use objc2_av_foundation::{
    AVAsset, AVAssetReader, AVAssetReaderTrackOutput, AVAssetWriter, AVAssetWriterInput,
    AVAssetWriterInputPixelBufferAdaptor, AVAssetWriterStatus, AVFileTypeMPEG4, AVMediaTypeAudio,
    AVMediaTypeVideo,
};
use objc2_core_foundation::{CFRange, CFRetained};
use objc2_core_media::{
    CMAudioFormatDescriptionGetStreamBasicDescription, CMSampleBuffer, CMTime, CMTimeRange,
};
use objc2_core_video::kCVPixelFormatType_32BGRA;
use objc2_foundation::{NSDictionary, NSNumber, NSString, NSURL};
use serde_json::{Value, json};

fn number(value: u32) -> Retained<AnyObject> {
    unsafe { Retained::cast_unchecked(NSNumber::new_u32(value)) }
}

fn text(value: &str) -> Retained<AnyObject> {
    unsafe { Retained::cast_unchecked(NSString::from_str(value)) }
}

fn settings(
    values: Vec<(&str, Retained<AnyObject>)>,
) -> Retained<NSDictionary<NSString, AnyObject>> {
    let keys: Vec<_> = values
        .iter()
        .map(|(key, _)| NSString::from_str(key))
        .collect();
    let key_refs: Vec<_> = keys.iter().map(|key| &**key).collect();
    let value_refs: Vec<_> = values.iter().map(|(_, value)| &**value).collect();
    NSDictionary::from_slices(&key_refs, &value_refs)
}

fn asset(path: &Path) -> Result<Retained<AVAsset>, Box<dyn std::error::Error>> {
    let canonical = path.canonicalize()?;
    let url = NSURL::fileURLWithPath(&NSString::from_str(
        canonical.to_str().ok_or("Non-UTF-8 media path")?,
    ));
    Ok(unsafe { AVAsset::assetWithURL(&url) })
}

fn wait_ready(
    input: &AVAssetWriterInput,
    writer: &AVAssetWriter,
    deadline: Instant,
) -> Result<(), Box<dyn std::error::Error>> {
    while !unsafe { input.isReadyForMoreMediaData() } {
        if unsafe { writer.status() } != AVAssetWriterStatus::Writing {
            return Err(format!("Native writer stopped: {:?}", unsafe { writer.error() }).into());
        }
        if Instant::now() > deadline {
            unsafe { writer.cancelWriting() };
            return Err("Native writer readiness deadline expired".into());
        }
        std::thread::sleep(Duration::from_millis(2));
    }
    Ok(())
}

fn clipped_audio(
    sample: &CMSampleBuffer,
    frames: i64,
) -> Result<CFRetained<CMSampleBuffer>, Box<dyn std::error::Error>> {
    let mut output = std::ptr::null_mut();
    let status = unsafe {
        CMSampleBuffer::copy_sample_buffer_for_range(
            None,
            sample,
            CFRange::new(0, isize::try_from(frames)?),
            NonNull::from(&mut output),
        )
    };
    if status != 0 {
        return Err(format!("Native PCM sample clipping failed: {status}").into());
    }
    let pointer = NonNull::new(output).ok_or("Native PCM clipping returned no buffer")?;
    Ok(unsafe { CFRetained::from_raw(pointer) })
}

fn validate_pcm(sample: &CMSampleBuffer) -> Result<(), Box<dyn std::error::Error>> {
    let description =
        unsafe { sample.format_description() }.ok_or("Audio sample has no format description")?;
    let layout = unsafe { CMAudioFormatDescriptionGetStreamBasicDescription(&description) };
    let layout = NonNull::new(layout.cast_mut()).ok_or("Audio sample is not PCM")?;
    let layout = unsafe { layout.as_ref() };
    if layout.mFormatID != 0x6c70636d
        || layout.mSampleRate != 48000.0
        || layout.mChannelsPerFrame != 2
        || layout.mFormatFlags & 32 != 0
    {
        return Err("Experiment requires interleaved stereo 48kHz linear PCM input".into());
    }
    Ok(())
}

#[expect(
    deprecated,
    reason = "Synchronous track discovery isolates the codec experiment; production will load tracks asynchronously"
)]
pub fn encode(
    video: &Path,
    audio: &Path,
    output: &Path,
    frames: usize,
) -> Result<Value, Box<dyn std::error::Error>> {
    if output.exists() || !(1..=240).contains(&frames) {
        return Err("Fresh output and 1..240 frames are required".into());
    }
    let video_type = unsafe { AVMediaTypeVideo }.ok_or("Native video media type unavailable")?;
    let audio_type = unsafe { AVMediaTypeAudio }.ok_or("Native audio media type unavailable")?;
    let file_type = unsafe { AVFileTypeMPEG4 }.ok_or("Native MP4 container unavailable")?;
    let video_asset = asset(video)?;
    let audio_asset = asset(audio)?;
    let video_track = unsafe { video_asset.tracksWithMediaType(video_type) }
        .firstObject()
        .ok_or("No video track")?;
    let audio_track = unsafe { audio_asset.tracksWithMediaType(audio_type) }
        .firstObject()
        .ok_or("No audio track")?;
    let dimensions = unsafe { video_track.naturalSize() };
    if !dimensions.width.is_finite()
        || !dimensions.height.is_finite()
        || dimensions.width < 1.0
        || dimensions.height < 1.0
        || dimensions.width > 8192.0
        || dimensions.height > 8192.0
    {
        return Err("Video dimensions exceed experiment limits".into());
    }
    let pixels = settings(vec![("PixelFormatType", number(kCVPixelFormatType_32BGRA))]);
    let video_reader = unsafe { AVAssetReader::assetReaderWithAsset_error(&video_asset) }?;
    let video_output = unsafe {
        AVAssetReaderTrackOutput::assetReaderTrackOutputWithTrack_outputSettings(
            &video_track,
            Some(&pixels),
        )
    };
    let audio_reader = unsafe { AVAssetReader::assetReaderWithAsset_error(&audio_asset) }?;
    let audio_output = unsafe {
        AVAssetReaderTrackOutput::assetReaderTrackOutputWithTrack_outputSettings(&audio_track, None)
    };
    let end = unsafe { CMTime::new(i64::try_from(frames)?, 24) };
    unsafe { audio_reader.setTimeRange(CMTimeRange::new(CMTime::new(0, 24), end)) };
    if !unsafe {
        video_reader.canAddOutput(&video_output) && audio_reader.canAddOutput(&audio_output)
    } {
        return Err("Native reader rejected the input representation".into());
    }
    unsafe {
        video_reader.addOutput(&video_output);
        audio_reader.addOutput(&audio_output);
    }
    let output_path = output
        .parent()
        .ok_or("Output parent is missing")?
        .canonicalize()?
        .join(output.file_name().ok_or("Output filename is missing")?);
    let output_url = NSURL::fileURLWithPath(&NSString::from_str(
        output_path.to_str().ok_or("Non-UTF-8 output path")?,
    ));
    let writer =
        unsafe { AVAssetWriter::assetWriterWithURL_fileType_error(&output_url, file_type) }?;
    let video_settings = settings(vec![
        ("AVVideoCodecKey", text("avc1")),
        ("AVVideoWidthKey", number(dimensions.width as u32)),
        ("AVVideoHeightKey", number(dimensions.height as u32)),
    ]);
    let audio_settings = settings(vec![
        ("AVFormatIDKey", number(0x61616320)),
        ("AVSampleRateKey", number(48000)),
        ("AVNumberOfChannelsKey", number(2)),
        ("AVEncoderBitRateKey", number(192000)),
    ]);
    let video_input = unsafe {
        AVAssetWriterInput::assetWriterInputWithMediaType_outputSettings(
            video_type,
            Some(&video_settings),
        )
    };
    let audio_input = unsafe {
        AVAssetWriterInput::assetWriterInputWithMediaType_outputSettings(
            audio_type,
            Some(&audio_settings),
        )
    };
    let adaptor = unsafe {
        AVAssetWriterInputPixelBufferAdaptor::assetWriterInputPixelBufferAdaptorWithAssetWriterInput_sourcePixelBufferAttributes(&video_input, Some(&pixels))
    };
    if !unsafe { writer.canAddInput(&video_input) && writer.canAddInput(&audio_input) } {
        return Err("Native writer rejected H.264/AAC output".into());
    }
    unsafe {
        writer.addInput(&video_input);
        writer.addInput(&audio_input);
    }
    if !unsafe {
        video_reader.startReading() && audio_reader.startReading() && writer.startWriting()
    } {
        return Err(format!(
            "Native media start failed: video {:?}, audio {:?}, writer {:?}",
            unsafe { video_reader.error() },
            unsafe { audio_reader.error() },
            unsafe { writer.error() }
        )
        .into());
    }
    unsafe { writer.startSessionAtSourceTime(CMTime::new(0, 24)) };
    let deadline = Instant::now() + Duration::from_secs(30);
    let mut audio_pending = unsafe { audio_output.copyNextSampleBuffer() };
    let mut audio_samples = 0_i64;
    let expected_audio_samples = i64::try_from(frames)?
        .checked_mul(2000)
        .ok_or("Audio range overflow")?;
    for index in 0..frames {
        let sample =
            unsafe { video_output.copyNextSampleBuffer() }.ok_or("Video range ended early")?;
        let image = unsafe { sample.image_buffer() }.ok_or("Video sample has no pixel buffer")?;
        let video_pts = unsafe { sample.presentation_time_stamp() };
        if video_pts.timescale <= 0
            || video_pts.epoch != 0
            || i128::from(video_pts.value) * 24
                != i128::try_from(index)? * i128::from(video_pts.timescale)
        {
            return Err(
                "Experiment requires the actual source sample clock to be 24fps from zero".into(),
            );
        }
        wait_ready(&video_input, &writer, deadline)?;
        if !unsafe { adaptor.appendPixelBuffer_withPresentationTime(&image, video_pts) } {
            return Err(format!("Native video append failed: {:?}", unsafe {
                writer.error()
            })
            .into());
        }
        while let Some(sample) = audio_pending.as_ref() {
            validate_pcm(sample)?;
            let pts = unsafe { sample.presentation_time_stamp() };
            if pts.timescale <= 0
                || pts.epoch != 0
                || i128::from(pts.value) * 48000
                    != i128::from(audio_samples) * i128::from(pts.timescale)
            {
                return Err("PCM sample timing is not contiguous from zero".into());
            }
            if i128::from(pts.value) * 24 >= i128::try_from(index + 1)? * i128::from(pts.timescale)
            {
                break;
            }
            wait_ready(&audio_input, &writer, deadline)?;
            let count = i64::try_from(unsafe { sample.num_samples() })?;
            let remaining = expected_audio_samples - audio_samples;
            let keep = count.min(remaining);
            if keep <= 0 {
                return Err("PCM sample range is empty".into());
            }
            let clipped = clipped_audio(sample, keep)?;
            if !unsafe { audio_input.appendSampleBuffer(&clipped) } {
                return Err(format!("Native audio append failed: {:?}", unsafe {
                    writer.error()
                })
                .into());
            }
            audio_samples += keep;
            if audio_samples == expected_audio_samples {
                audio_pending = None;
                unsafe { audio_reader.cancelReading() };
                break;
            }
            audio_pending = unsafe { audio_output.copyNextSampleBuffer() };
        }
    }
    if audio_samples != expected_audio_samples
        || unsafe { audio_reader.error() }.is_some()
        || unsafe { video_reader.error() }.is_some()
    {
        return Err("Input range did not finish cleanly".into());
    }
    unsafe {
        video_input.markAsFinished();
        audio_input.markAsFinished();
        writer.endSessionAtSourceTime(end);
        video_reader.cancelReading();
    }
    let (send, receive) = mpsc::channel();
    let finished = RcBlock::new(move || {
        let _ = send.send(());
    });
    unsafe { writer.finishWritingWithCompletionHandler(&finished) };
    receive.recv_timeout(Duration::from_secs(30))?;
    if unsafe { writer.status() } != AVAssetWriterStatus::Completed {
        return Err(format!("Native writing failed: {:?}", unsafe { writer.error() }).into());
    }
    Ok(json!({
        "state": "encoded-unreviewed", "backend": "Rust AVFoundation H.264/AAC",
        "videoSource": video, "audioSource": audio, "output": output_path,
        "videoFramesAppended": frames, "outputFrameRate": {"numerator": 24, "denominator": 1},
        "audioSamplesAppended": audio_samples, "canonicalAudioRate": 48000,
        "canonicalAudioChannels": 2, "watched": false, "heard": false,
    }))
}
