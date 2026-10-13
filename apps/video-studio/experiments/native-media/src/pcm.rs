use std::fs::OpenOptions;
use std::io::Write;
use std::path::Path;
use std::ptr::NonNull;

use objc2::rc::Retained;
use objc2::runtime::AnyObject;
use objc2_av_foundation::{AVAsset, AVAssetReader, AVAssetReaderTrackOutput, AVMediaTypeAudio};
use objc2_core_media::CMAudioFormatDescriptionGetStreamBasicDescription;
use objc2_foundation::{NSDictionary, NSNumber, NSString, NSURL};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

#[expect(
    deprecated,
    reason = "Bounded codec experiment; production uses asynchronous track loading"
)]
pub fn decode(
    input: &Path,
    output: &Path,
    limit: usize,
) -> Result<Value, Box<dyn std::error::Error>> {
    if output.exists() || !(1..=1_000_000).contains(&limit) {
        return Err("Fresh PCM output and 1..1000000 sample frames are required".into());
    }
    let canonical = input.canonicalize()?;
    let url = NSURL::fileURLWithPath(&NSString::from_str(
        canonical.to_str().ok_or("Non-UTF-8 input")?,
    ));
    let asset = unsafe { AVAsset::assetWithURL(&url) };
    let kind = unsafe { AVMediaTypeAudio }.ok_or("Audio media type unavailable")?;
    let track = unsafe { asset.tracksWithMediaType(kind) }
        .firstObject()
        .ok_or("No audio track")?;
    let keys = [
        "AVFormatIDKey",
        "AVSampleRateKey",
        "AVNumberOfChannelsKey",
        "AVLinearPCMBitDepthKey",
        "AVLinearPCMIsFloatKey",
        "AVLinearPCMIsBigEndianKey",
        "AVLinearPCMIsNonInterleaved",
    ];
    let values = [0x6c70636d, 48000, 2, 32, 1, 0, 0];
    let keys: Vec<_> = keys.iter().map(|key| NSString::from_str(key)).collect();
    let values: Vec<Retained<AnyObject>> = values
        .into_iter()
        .map(|v| unsafe { Retained::cast_unchecked(NSNumber::new_u32(v)) })
        .collect();
    let key_refs: Vec<_> = keys.iter().map(|key| &**key).collect();
    let value_refs: Vec<_> = values.iter().map(|value| &**value).collect();
    let settings = NSDictionary::from_slices(&key_refs, &value_refs);
    let reader = unsafe { AVAssetReader::assetReaderWithAsset_error(&asset) }?;
    let track_output = unsafe {
        AVAssetReaderTrackOutput::assetReaderTrackOutputWithTrack_outputSettings(
            &track,
            Some(&settings),
        )
    };
    if !unsafe { reader.canAddOutput(&track_output) } {
        return Err("Reader rejected float PCM output".into());
    }
    unsafe { reader.addOutput(&track_output) };
    if !unsafe { reader.startReading() } {
        return Err(format!("PCM reader start failed: {:?}", unsafe { reader.error() }).into());
    }
    let mut pcm = Vec::with_capacity(limit * 8);
    let mut chunks = Vec::new();
    let mut count = 0_usize;
    let mut markers = 0;
    let mut reached_end = false;
    while count < limit {
        let Some(sample) = (unsafe { track_output.copyNextSampleBuffer() }) else {
            reached_end = true;
            break;
        };
        let frames = usize::try_from(unsafe { sample.num_samples() })?;
        if frames == 0 {
            markers += 1;
            continue;
        }
        let format = unsafe { sample.format_description() }.ok_or("PCM has no description")?;
        let asbd = NonNull::new(
            unsafe { CMAudioFormatDescriptionGetStreamBasicDescription(&format) }.cast_mut(),
        )
        .ok_or("PCM description missing")?;
        let asbd = unsafe { asbd.as_ref() };
        if asbd.mFormatID != 0x6c70636d
            || asbd.mSampleRate != 48000.0
            || asbd.mChannelsPerFrame != 2
            || asbd.mBitsPerChannel != 32
            || asbd.mBytesPerFrame != 8
            || asbd.mFormatFlags & 1 == 0
            || asbd.mFormatFlags & 34 != 0
        {
            return Err(format!("Unexpected PCM layout: {asbd:?}").into());
        }
        let pts = unsafe { sample.presentation_time_stamp() };
        let value = pts.value;
        let timescale = pts.timescale;
        if timescale <= 0
            || pts.epoch != 0
            || i128::from(value) * 48000 != i128::try_from(count)? * i128::from(timescale)
        {
            return Err(format!("PCM discontinuity at sample {count}: {value}/{timescale}").into());
        }
        let block = unsafe { sample.data_buffer() }.ok_or("PCM sample has no block buffer")?;
        let keep = frames.min(limit - count);
        let bytes = keep.checked_mul(8).ok_or("PCM buffer overflow")?;
        if unsafe { block.data_length() } < frames.checked_mul(8).ok_or("PCM chunk overflow")? {
            return Err("PCM block is shorter than its declared sample count".into());
        }
        let start = pcm.len();
        pcm.resize(start + bytes, 0);
        let destination = NonNull::new(pcm[start..].as_mut_ptr())
            .ok_or("Empty PCM destination")?
            .cast();
        let status = unsafe { block.copy_data_bytes(0, bytes, destination) };
        if status != 0 {
            return Err(format!("PCM byte copy failed: {status}").into());
        }
        chunks.push(json!({"pts": {"value": value,"timescale": timescale},"decodedSampleFrames": frames,"savedSampleFrames": keep}));
        count += keep;
    }
    let status = format!("{:?}", unsafe { reader.status() });
    if let Some(error) = unsafe { reader.error() } {
        return Err(format!("PCM decode failed: {error:?}").into());
    }
    unsafe { reader.cancelReading() };
    if count == 0 {
        return Err("PCM decoder returned no samples".into());
    }
    let mut file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(output)?;
    file.write_all(&pcm)?;
    file.sync_all()?;
    Ok(
        json!({"state":"decoded-unheard","input": canonical,"pcmFile":output,"sampleFrames":count,"sampleRate":48000,"channels":2,"sampleFormat":"interleaved-f32le","bytes":pcm.len(),"sha256":format!("{:x}",Sha256::digest(&pcm)),"readerStatusAtStop":status,"reachedEnd":reached_end,"markerBuffers":markers,"chunks":chunks,"heard":false}),
    )
}
