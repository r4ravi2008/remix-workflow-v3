use std::fs::OpenOptions;
use std::path::Path;

use objc2::rc::{Retained, autoreleasepool};
use objc2::runtime::AnyObject;
use objc2_av_foundation::{
    AVAsset, AVAssetReader, AVAssetReaderStatus, AVAssetReaderTrackOutput, AVMediaTypeVideo,
};
use objc2_core_video::{
    CVPixelBufferGetBaseAddress, CVPixelBufferGetBytesPerRow, CVPixelBufferGetHeight,
    CVPixelBufferGetPixelFormatType, CVPixelBufferGetWidth, CVPixelBufferLockBaseAddress,
    CVPixelBufferLockFlags, CVPixelBufferUnlockBaseAddress, kCVPixelFormatType_32BGRA,
};
use objc2_foundation::{NSDictionary, NSNumber, NSString, NSURL};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

mod clock;
mod encode;
mod pcm;

fn probe(
    input: &Path,
    output: &Path,
    limit: usize,
    sequence: Option<&Path>,
    selected: Option<usize>,
) -> Result<Value, Box<dyn std::error::Error>> {
    let maximum = 100000;
    if !input.is_file() || output.exists() || !(1..=maximum).contains(&limit) {
        return Err("Existing input, fresh output, and bounded frame limit are required".into());
    }
    let input = input.canonicalize()?;
    let input_text = input.to_str().ok_or("Input path is not UTF-8")?;
    let url = NSURL::fileURLWithPath(&NSString::from_str(input_text));
    let asset = unsafe { AVAsset::assetWithURL(&url) };
    let duration = unsafe { asset.duration() };
    let video_type = unsafe { AVMediaTypeVideo }.ok_or("Native video media type is unavailable")?;
    #[expect(
        deprecated,
        reason = "Synchronous loading isolates this bounded codec experiment; production will use asynchronous loading"
    )]
    let tracks = unsafe { asset.tracksWithMediaType(video_type) };
    let track = tracks.firstObject().ok_or("No native video track")?;
    let rate = unsafe { track.nominalFrameRate() };
    let reader = unsafe { AVAssetReader::assetReaderWithAsset_error(&asset) }?;
    let key = NSString::from_str("PixelFormatType");
    let value: Retained<AnyObject> =
        unsafe { Retained::cast_unchecked(NSNumber::new_u32(kCVPixelFormatType_32BGRA)) };
    let settings = NSDictionary::from_slices(&[&*key], &[&*value]);
    let track_output = unsafe {
        AVAssetReaderTrackOutput::assetReaderTrackOutputWithTrack_outputSettings(
            &track,
            Some(&settings),
        )
    };
    if !unsafe { reader.canAddOutput(&track_output) } {
        return Err("Native reader rejected BGRA output".into());
    }
    unsafe { reader.addOutput(&track_output) };
    if !unsafe { reader.startReading() } {
        return Err(format!("Native reader failed: {:?}", unsafe { reader.error() }).into());
    }
    let mut frames = Vec::new();
    let deadline = std::time::Instant::now() + std::time::Duration::from_secs(60);
    for index in 0..limit {
        if std::time::Instant::now() > deadline {
            return Err("Independent frame decode deadline expired".into());
        }
        let Some(sample) = (unsafe { track_output.copyNextSampleBuffer() }) else {
            break;
        };
        if selected.is_some_and(|target| target != index) {
            continue;
        }
        let pts = unsafe { sample.presentation_time_stamp() };
        let image = unsafe { sample.image_buffer() }.ok_or("Sample has no pixel buffer")?;
        let width = CVPixelBufferGetWidth(&image);
        let height = CVPixelBufferGetHeight(&image);
        let stride = CVPixelBufferGetBytesPerRow(&image);
        let pixel_format = CVPixelBufferGetPixelFormatType(&image);
        let row_bytes = width.checked_mul(4).ok_or("Pixel width overflow")?;
        let size = row_bytes
            .checked_mul(height)
            .ok_or("Pixel buffer overflow")?;
        if pixel_format != kCVPixelFormatType_32BGRA
            || stride < row_bytes
            || size > 128 * 1024 * 1024
        {
            return Err("Unsupported decoded pixel layout".into());
        }
        let flags = CVPixelBufferLockFlags::ReadOnly;
        if unsafe { CVPixelBufferLockBaseAddress(&image, flags) } != 0 {
            return Err("Could not lock native pixel buffer".into());
        }
        let address = CVPixelBufferGetBaseAddress(&image).cast::<u8>();
        if address.is_null() {
            unsafe { CVPixelBufferUnlockBaseAddress(&image, flags) };
            return Err("Native pixel buffer has no base address".into());
        }
        let mut rgba = vec![0; size];
        for row in 0..height {
            let source =
                unsafe { std::slice::from_raw_parts(address.add(row * stride), row_bytes) };
            for (bgra, target) in source
                .chunks_exact(4)
                .zip(rgba[row * row_bytes..(row + 1) * row_bytes].chunks_exact_mut(4))
            {
                target.copy_from_slice(&[bgra[2], bgra[1], bgra[0], bgra[3]]);
            }
        }
        if unsafe { CVPixelBufferUnlockBaseAddress(&image, flags) } != 0 {
            return Err("Could not unlock native pixel buffer".into());
        }
        if index == 0 || sequence.is_some() || selected.is_some() {
            let frame_path = sequence
                .map(|root| root.join(format!("frame-{index:06}.png")))
                .unwrap_or_else(|| output.to_path_buf());
            let file = OpenOptions::new()
                .write(true)
                .create_new(true)
                .open(frame_path)?;
            let mut encoder =
                png::Encoder::new(file, u32::try_from(width)?, u32::try_from(height)?);
            encoder.set_color(png::ColorType::Rgba);
            encoder.set_depth(png::BitDepth::Eight);
            encoder.write_header()?.write_image_data(&rgba)?;
        }
        let pts_value = pts.value;
        let pts_timescale = pts.timescale;
        let pts_epoch = pts.epoch;
        frames.push(json!({
            "index": index, "width": width, "height": height,
            "pts": {"value": pts_value, "timescale": pts_timescale, "epoch": pts_epoch},
            "rgbaSha256": format!("{:x}", Sha256::digest(&rgba)),
        }));
    }
    let reader_status = unsafe { reader.status() };
    let full_decode = reader_status == AVAssetReaderStatus::Completed;
    let status = format!("{reader_status:?}");
    let error = unsafe { reader.error() }.map(|value| format!("{value:?}"));
    unsafe { reader.cancelReading() };
    if error.is_some() || frames.is_empty() {
        return Err(format!("Native decode failed: {error:?}").into());
    }
    let duration_value = duration.value;
    let duration_timescale = duration.timescale;
    Ok(json!({
        "state": "technical-probe", "backend": "AVFoundation via Rust objc2",
        "input": input, "duration": {"value": duration_value, "timescale": duration_timescale},
        "nominalFrameRate": rate, "decodedFrames": frames, "readerStatusAtStop": status,
        "firstFramePng": output, "fullDecode": full_decode,
        "fullDecodeScope": "Primary video reader reached EOF; excludes other streams, playback, hearing and creative acceptance",
        "watched": false, "heard": false,
    }))
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() == 5 && args[1] == "frame" {
        let result = args[4]
            .parse::<usize>()
            .map_err(|error| error.to_string())
            .and_then(|ordinal| {
                if ordinal >= 100000 {
                    return Err("Ordinal exceeds independent frame bound".into());
                }
                autoreleasepool(|_| {
                    probe(
                        Path::new(&args[2]),
                        Path::new(&args[3]),
                        ordinal + 1,
                        None,
                        Some(ordinal),
                    )
                    .map_err(|error| error.to_string())
                })
            });
        print_result(result);
        return;
    }
    if args.len() == 3 && args[1] == "clock" {
        let result = autoreleasepool(|_| {
            clock::inspect(Path::new(&args[2]), 8).map_err(|error| error.to_string())
        });
        print_result(result);
        return;
    }
    if args.len() == 5 && args[1] == "sequence" {
        let result = args[4]
            .parse::<usize>()
            .map_err(|e| e.to_string())
            .and_then(|limit| {
                let root = Path::new(&args[3]);
                std::fs::create_dir(root).map_err(|e| e.to_string())?;
                autoreleasepool(|_| {
                    probe(
                        Path::new(&args[2]),
                        &root.join("frame-000000.png"),
                        limit,
                        Some(root),
                        None,
                    )
                    .map_err(|e| e.to_string())
                })
            });
        print_result(result);
        return;
    }
    if args.len() == 5 && args[1] == "pcm" {
        let result = args[4]
            .parse::<usize>()
            .map_err(|error| error.to_string())
            .and_then(|limit| {
                autoreleasepool(|_| {
                    pcm::decode(Path::new(&args[2]), Path::new(&args[3]), limit)
                        .map_err(|error| error.to_string())
                })
            });
        print_result(result);
        return;
    }
    if args.len() == 6 && args[1] == "encode" {
        let result = args[5]
            .parse::<usize>()
            .map_err(|error| error.to_string())
            .and_then(|frames| {
                autoreleasepool(|_| {
                    encode::encode(
                        Path::new(&args[2]),
                        Path::new(&args[3]),
                        Path::new(&args[4]),
                        frames,
                    )
                    .map_err(|error| error.to_string())
                })
            });
        print_result(result);
        return;
    }
    if args.len() != 4 {
        eprintln!("usage: studio-native-media-experiment INPUT NEW_FIRST_FRAME.png FRAME_LIMIT");
        std::process::exit(64);
    }
    let result = args[3]
        .parse::<usize>()
        .map_err(|error| error.to_string())
        .and_then(|limit| {
            autoreleasepool(|_| {
                probe(Path::new(&args[1]), Path::new(&args[2]), limit, None, None)
                    .map_err(|error| error.to_string())
            })
        });
    print_result(result);
}

fn print_result(result: Result<Value, String>) {
    match result {
        Ok(value) => println!("{value}"),
        Err(error) => {
            println!("{}", json!({"state": "failed", "error": error}));
            std::process::exit(1);
        }
    }
}
