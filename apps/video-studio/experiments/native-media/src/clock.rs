use std::path::Path;

use objc2::rc::Retained;
use objc2::runtime::AnyObject;
use objc2_av_foundation::{AVAsset, AVAssetReader, AVAssetReaderTrackOutput, AVMediaTypeVideo};
use objc2_core_media::CMTime;
use objc2_core_video::kCVPixelFormatType_32BGRA;
use objc2_foundation::{NSDictionary, NSNumber, NSString, NSURL};
use serde_json::{Value, json};

fn time(value: CMTime) -> Value {
    let (ticks, timescale, epoch, flags) = (
        value.value,
        value.timescale,
        value.epoch,
        value.flags.bits(),
    );
    json!({"ticks":ticks,"timescale":timescale,"epoch":epoch,"flags":flags})
}

pub fn inspect(input: &Path, limit: usize) -> Result<Value, Box<dyn std::error::Error>> {
    if !(1..=32).contains(&limit) {
        return Err("Clock diagnostic is bounded to1..32 sample buffers".into());
    }
    let input = input.canonicalize()?;
    let url = NSURL::fileURLWithPath(&NSString::from_str(
        input.to_str().ok_or("Input is not UTF-8")?,
    ));
    let asset = unsafe { AVAsset::assetWithURL(&url) };
    #[expect(deprecated, reason = "Bounded independent source clock diagnostic")]
    let tracks =
        unsafe { asset.tracksWithMediaType(AVMediaTypeVideo.ok_or("Video media type missing")?) };
    if tracks.count() != 1 {
        return Err("Clock diagnostic requires one video track".into());
    }
    let track = tracks.firstObject().ok_or("Video track missing")?;
    let key = NSString::from_str("PixelFormatType");
    let value: Retained<AnyObject> =
        unsafe { Retained::cast_unchecked(NSNumber::new_u32(kCVPixelFormatType_32BGRA)) };
    let settings = NSDictionary::from_slices(&[&*key], &[&*value]);
    let mut readings = Vec::new();
    for (mode, settings) in [("compressed", None), ("decoded", Some(&*settings))] {
        let reader = unsafe { AVAssetReader::assetReaderWithAsset_error(&asset) }?;
        let output = unsafe {
            AVAssetReaderTrackOutput::assetReaderTrackOutputWithTrack_outputSettings(
                &track, settings,
            )
        };
        if !unsafe { reader.canAddOutput(&output) } {
            return Err("Reader rejected clock output".into());
        }
        unsafe { reader.addOutput(&output) };
        if !unsafe { reader.startReading() } {
            return Err(format!("Reader did not start:{:?}", unsafe { reader.error() }).into());
        }
        let mut samples = Vec::new();
        for index in 0..limit {
            let Some(sample) = (unsafe { output.copyNextSampleBuffer() }) else {
                break;
            };
            samples.push(json!({"readerOrdinal":index,"sampleCount":unsafe {sample.num_samples()},"pts":time(unsafe {sample.presentation_time_stamp()}),"outputPts":time(unsafe {sample.output_presentation_time_stamp()}),"dts":time(unsafe {sample.decode_time_stamp()}),"outputDts":time(unsafe {sample.output_decode_time_stamp()}),"duration":time(unsafe {sample.duration()}),"outputDuration":time(unsafe {sample.output_duration()})}));
        }
        let status = format!("{:?}", unsafe { reader.status() });
        let error = unsafe { reader.error() }.map(|error| format!("{error:?}"));
        unsafe { reader.cancelReading() };
        readings.push(json!({"mode":mode,"samples":samples,"status":status,"error":error}));
    }
    Ok(
        json!({"schema":1,"input":input,"readings":readings,"fullDecode":false,"watched":false,"heard":false,"creativeAccepted":false}),
    )
}
