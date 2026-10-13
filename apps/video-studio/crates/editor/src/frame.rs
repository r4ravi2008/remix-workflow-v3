use std::path::{Path, PathBuf};
use std::time::{Duration, Instant};

use objc2::rc::Retained;
use objc2::runtime::AnyObject;
use objc2_av_foundation::{AVAssetReader, AVAssetReaderTrackOutput};
use objc2_core_video::kCVPixelFormatType_32BGRA;
use objc2_foundation::{NSDictionary, NSNumber, NSString};
use serde::{Deserialize, Serialize};

use crate::{
    BuildIdentity, ContentHash, EntityId, MediaDescriptor, MediaKind, MediaTime,
    NativeProbeIdentity, Project, Result, StudioError, media, pixels,
    verified_source::VerifiedSource,
};

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FrameInspectionRequest {
    pub revision: ContentHash,
    pub asset: ContentHash,
    pub source_measurement: ContentHash,
    pub presentation_ordinal: u64,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FrameInspectionReceipt {
    pub schema: u32,
    pub project: EntityId,
    pub request: FrameInspectionRequest,
    pub source_bytes: u64,
    pub source_probe: Option<NativeProbeIdentity>,
    pub decoder: BuildIdentity,
    pub presentation_time: MediaTime,
    pub decoded_prefix_frames: u64,
    pub width: u32,
    pub height: u32,
    pub rgba_sha256: ContentHash,
    pub png_sha256: ContentHash,
    pub png_bytes: u64,
    pub scope: String,
}

pub struct FrameInspection {
    receipt: FrameInspectionReceipt,
    png: Vec<u8>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SavedFrameInspection {
    pub receipt_id: ContentHash,
    pub receipt: FrameInspectionReceipt,
    pub png_path: PathBuf,
    pub receipt_path: PathBuf,
}

fn error(detail: impl Into<String>) -> StudioError {
    StudioError::new("source_frame_error", detail)
}

struct ReaderGuard<'a>(&'a AVAssetReader);
impl Drop for ReaderGuard<'_> {
    fn drop(&mut self) {
        unsafe { self.0.cancelReading() };
    }
}

impl Project {
    pub fn inspect_frame(&self, request: FrameInspectionRequest) -> Result<FrameInspection> {
        let inspection = self.inspect(request.revision.clone())?;
        let asset = inspection
            .snapshot
            .assets
            .get(&request.asset)
            .ok_or_else(|| error("Frame asset is absent from the selected revision"))?;
        if inspection.asset_measurements[&request.asset] != request.source_measurement {
            return Err(StudioError::new(
                "measurement_conflict",
                "Frame request has a different source measurement",
            ));
        }
        let MediaDescriptor::Movie {
            width,
            height,
            samples,
            native_decode,
            ..
        } = &asset.descriptor
        else {
            return Err(StudioError::new(
                "wrong_stream",
                "Frame inspection requires a movie stream",
            ));
        };
        pixels::extent(*width, *height)?;
        if !native_decode {
            return Err(error("Movie has no successful native first-frame decode"));
        }
        let ordinal = usize::try_from(request.presentation_ordinal)
            .map_err(|_| error("Frame ordinal exceeds the host address range"))?;
        let presentation_time = samples
            .get(ordinal)
            .ok_or_else(|| error("Frame ordinal exceeds the immutable source index"))?
            .pts
            .clone();
        let path = self.studio.root.join("blobs").join(asset.hash.as_str());
        let mut source = VerifiedSource::open(&path, &asset.hash, asset.bytes)?;
        let decoder = BuildIdentity::current()?;
        let samples = samples[..=ordinal].to_vec();
        let (width, height) = (*width, *height);
        let mut image = media::with_track(&path, &MediaKind::Movie, move |track| {
            let source =
                unsafe { track.asset() }.ok_or_else(|| error("Frame track has no asset"))?;
            let reader = unsafe { AVAssetReader::assetReaderWithAsset_error(&source) }
                .map_err(|value| error(format!("{value:?}")))?;
            let _guard = ReaderGuard(&reader);
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
                return Err(error("Frame reader rejected BGRA output"));
            }
            unsafe { reader.addOutput(&output) };
            if !unsafe { reader.startReading() } {
                return Err(error("Frame reader did not start"));
            }
            let deadline = Instant::now() + Duration::from_secs(90);
            for (index, expected) in samples.iter().enumerate() {
                if Instant::now() > deadline {
                    return Err(error("Frame decode deadline expired"));
                }
                let sample = unsafe { output.copyNextSampleBuffer() }.ok_or_else(|| {
                    error(format!("Frame decode ended early: {:?}", unsafe {
                        reader.error()
                    }))
                })?;
                let pts = media::time(unsafe { sample.output_presentation_time_stamp() })?;
                if i128::from(pts.ticks) * i128::from(expected.pts.timescale)
                    != i128::from(expected.pts.ticks) * i128::from(pts.timescale)
                {
                    return Err(error(
                        "Frame decode PTS differs from the immutable source index",
                    ));
                }
                let pixels = unsafe { sample.image_buffer() }
                    .ok_or_else(|| error("Frame sample has no image"))?;
                if index == ordinal {
                    let image = pixels::Pixels::copy(&pixels)?;
                    if (image.width, image.height) != (width, height) {
                        return Err(error("Frame dimensions differ from the source measurement"));
                    }
                    return Ok(image);
                }
            }
            Err(error("Frame decode produced no selected frame"))
        })?;
        source.verify()?;
        for pixel in image.bytes.chunks_exact_mut(4) {
            pixel.swap(0, 2);
        }
        let rgba_sha256 = ContentHash::bytes(&image.bytes);
        let mut png = Vec::new();
        {
            let mut encoder = png::Encoder::new(&mut png, width, height);
            encoder.set_color(png::ColorType::Rgba);
            encoder.set_depth(png::BitDepth::Eight);
            let mut writer = encoder
                .write_header()
                .map_err(|value| error(value.to_string()))?;
            writer
                .write_image_data(&image.bytes)
                .map_err(|value| error(value.to_string()))?;
            writer.finish().map_err(|value| error(value.to_string()))?;
        }
        let receipt = FrameInspectionReceipt {
            schema: 1, project: self.id.clone(), request,
            source_bytes: asset.bytes, source_probe: asset.measurement.clone(),
            decoder, presentation_time,
            decoded_prefix_frames: ordinal as u64 + 1,
            width, height, rgba_sha256, png_sha256: ContentHash::bytes(&png),
            png_bytes: png.len() as u64,
            scope: "One coded BGRA frame converted losslessly to RGBA PNG. Prefix PTS checked. Source FD hash and pathname identity checked before and after decode; changes between observations are not excluded. Display orientation, aperture, SAR and color metadata unverified. No playback, hearing or creative acceptance.".into(),
        };
        Ok(FrameInspection { receipt, png })
    }
}

impl FrameInspection {
    pub fn receipt(&self) -> &FrameInspectionReceipt {
        &self.receipt
    }

    pub fn png(&self) -> &[u8] {
        &self.png
    }

    pub fn save_new(self, directory: impl AsRef<Path>) -> Result<SavedFrameInspection> {
        let mut directory = crate::owned_directory::OwnedDirectory::create(directory.as_ref())?;
        let receipt_id = ContentHash::document(&self.receipt)?;
        let receipt_path = directory.path().join("receipt.json");
        let png_path = directory.path().join("source-frame.png");
        directory.write("request.json", &serde_json::to_vec(&self.receipt.request)?)?;
        directory.write("source-frame.png", &self.png)?;
        directory.write("receipt.json", &serde_json::to_vec(&self.receipt)?)?;
        directory.finish()?;
        Ok(SavedFrameInspection {
            receipt_id,
            receipt: self.receipt,
            png_path,
            receipt_path,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    fn inspection(png: Vec<u8>) -> FrameInspection {
        let hash = ContentHash::parse("0".repeat(64)).unwrap();
        FrameInspection {
            receipt: FrameInspectionReceipt {
                schema: 1,
                project: EntityId::parse("test").unwrap(),
                request: FrameInspectionRequest {
                    revision: hash.clone(),
                    asset: hash.clone(),
                    source_measurement: hash.clone(),
                    presentation_ordinal: 0,
                },
                source_bytes: 0,
                source_probe: None,
                decoder: BuildIdentity::current().unwrap(),
                presentation_time: MediaTime {
                    ticks: 0,
                    timescale: 24,
                },
                decoded_prefix_frames: 1,
                width: 1,
                height: 1,
                rgba_sha256: hash,
                png_sha256: ContentHash::bytes(&png),
                png_bytes: png.len() as u64,
                scope: "Filesystem ownership test only".into(),
            },
            png,
        }
    }

    #[test]
    fn failed_inspection_save_preserves_a_competing_receipt_file() {
        let root =
            std::env::temp_dir().join(format!("studio-frame-collision-{}", std::process::id()));
        fs::create_dir(&root).unwrap();
        let directory = root.join("new-inspection");
        let watched = directory.clone();
        let (ready, wait) = std::sync::mpsc::channel();
        let actor = std::thread::spawn(move || {
            ready.send(()).unwrap();
            let deadline = Instant::now() + Duration::from_secs(5);
            while !watched.exists() {
                assert!(Instant::now() < deadline);
                std::thread::yield_now();
            }
            use std::io::Write;
            let mut file = fs::OpenOptions::new()
                .create_new(true)
                .write(true)
                .open(watched.join("receipt.json"))
                .unwrap();
            file.write_all(b"foreign-receipt").unwrap();
            file.sync_all().unwrap();
        });
        wait.recv().unwrap();
        let result = inspection(vec![0; 16 * 1024 * 1024]).save_new(&directory);
        actor.join().unwrap();
        assert_eq!(result.unwrap_err().code, "io_error");
        assert_eq!(
            fs::read(directory.join("receipt.json")).unwrap(),
            b"foreign-receipt"
        );
        assert!(directory.join("source-frame.png").is_file());
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn inspection_save_never_overwrites_an_existing_directory() {
        let root = std::env::temp_dir().join(format!("studio-frame-save-{}", std::process::id()));
        fs::create_dir(&root).unwrap();
        {
            let directory = root.join("existing");
            fs::create_dir(&directory).unwrap();
            fs::write(directory.join("source-frame.png"), b"user-owned").unwrap();
            let hash = ContentHash::parse("0".repeat(64)).unwrap();
            let receipt = FrameInspectionReceipt {
                schema: 1,
                project: EntityId::parse("test").unwrap(),
                request: FrameInspectionRequest {
                    revision: hash.clone(),
                    asset: hash.clone(),
                    source_measurement: hash.clone(),
                    presentation_ordinal: 0,
                },
                source_bytes: 0,
                source_probe: None,
                decoder: BuildIdentity::current().unwrap(),
                presentation_time: MediaTime {
                    ticks: 0,
                    timescale: 24,
                },
                decoded_prefix_frames: 1,
                width: 1,
                height: 1,
                rgba_sha256: hash.clone(),
                png_sha256: hash,
                png_bytes: 4,
                scope: "Ownership test only".into(),
            };
            let inspection = FrameInspection {
                receipt,
                png: b"test".to_vec(),
            };
            assert!(inspection.save_new(&directory).is_err());
            assert_eq!(
                fs::read(directory.join("source-frame.png")).unwrap(),
                b"user-owned"
            );
        }
        fs::remove_dir_all(root).unwrap();
    }
}
