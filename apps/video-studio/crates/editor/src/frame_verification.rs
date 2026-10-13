use std::fs::{self, OpenOptions};
use std::io::{Cursor, Read};
use std::os::unix::fs::{MetadataExt, OpenOptionsExt};
use std::path::{Path, PathBuf};

use serde::{Deserialize, Serialize};

use crate::{
    BuildIdentity, ContentHash, EntityId, FrameInspectionReceipt, FrameInspectionRequest,
    MediaDescriptor, Project, Result, StudioError, pixels, verified_source::VerifiedSource,
};

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FrameInspectionVerificationRequest {
    pub directory: PathBuf,
    pub receipt_id: ContentHash,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum FrameInspectionVerificationState {
    CompleteVerified,
    PartialRetained,
    ForeignRetained,
    CorruptRetained,
    UnverifiableRetained,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FrameInspectionVerification {
    pub schema: u32,
    pub project: EntityId,
    pub request: FrameInspectionVerificationRequest,
    pub verifier: BuildIdentity,
    pub state: FrameInspectionVerificationState,
    pub observed_receipt_id: Option<ContentHash>,
    pub png_sha256: Option<ContentHash>,
    pub rgba_sha256: Option<ContentHash>,
    pub reasons: Vec<String>,
    pub scope: String,
}

impl FrameInspectionVerification {
    fn unavailable(mut self, error: impl std::fmt::Display) -> Self {
        self.state = FrameInspectionVerificationState::UnverifiableRetained;
        self.reasons.push(error.to_string());
        self
    }
}

fn invalid(detail: impl Into<String>) -> StudioError {
    StudioError::new("frame_inspection_invalid", detail)
}

fn read_bounded(path: &Path, maximum: u64) -> Result<Vec<u8>> {
    let mut file = OpenOptions::new()
        .read(true)
        .custom_flags(libc::O_NOFOLLOW | libc::O_CLOEXEC)
        .open(path)?;
    let before = file.metadata()?;
    if !before.is_file() || before.len() > maximum {
        return Err(invalid("Frame record exceeds its declared read bound"));
    }
    let mut bytes = Vec::with_capacity(before.len() as usize);
    (&mut file).take(maximum + 1).read_to_end(&mut bytes)?;
    let after = file.metadata()?;
    let entry = fs::symlink_metadata(path)?;
    if bytes.len() as u64 != before.len()
        || after.len() != before.len()
        || before.mtime() != after.mtime()
        || before.mtime_nsec() != after.mtime_nsec()
        || !entry.is_file()
        || entry.dev() != after.dev()
        || entry.ino() != after.ino()
    {
        return Err(invalid("Frame record changed during read"));
    }
    Ok(bytes)
}

fn check_png(receipt: &FrameInspectionReceipt, bytes: &[u8]) -> Result<()> {
    let extent = pixels::extent(receipt.width, receipt.height)?;
    if bytes.len() as u64 != receipt.png_bytes || ContentHash::bytes(bytes) != receipt.png_sha256 {
        return Err(invalid("PNG bytes differ from the bound frame receipt"));
    }
    let mut decoder = png::Decoder::new(Cursor::new(bytes));
    decoder.set_limits(png::Limits {
        bytes: pixels::MAX_OWNED_FRAME_BYTES as usize,
    });
    let mut reader = decoder.read_info().map_err(|e| invalid(e.to_string()))?;
    let info = reader.info();
    if info.width != receipt.width
        || info.height != receipt.height
        || info.color_type != png::ColorType::Rgba
        || info.bit_depth != png::BitDepth::Eight
        || info.animation_control.is_some()
        || reader.output_buffer_size() != extent
    {
        return Err(invalid(
            "PNG format or coded dimensions differ from the frame receipt",
        ));
    }
    let mut rgba = vec![0; extent];
    let info = reader
        .next_frame(&mut rgba)
        .map_err(|e| invalid(e.to_string()))?;
    if info.buffer_size() != extent || ContentHash::bytes(&rgba) != receipt.rgba_sha256 {
        return Err(invalid(
            "Decoded PNG pixels differ from the bound frame receipt",
        ));
    }
    reader.finish().map_err(|e| invalid(e.to_string()))?;
    Ok(())
}

impl Project {
    fn check_frame_receipt(&self, receipt: &FrameInspectionReceipt) -> Result<()> {
        if receipt.project != self.id {
            return Err(StudioError::new(
                "frame_inspection_foreign",
                "Frame receipt belongs to another project",
            ));
        }
        if receipt.schema != 1 {
            return Err(StudioError::new(
                "frame_inspection_unsupported",
                "Frame receipt schema is unsupported",
            ));
        }
        let inspection = self.inspect(receipt.request.revision.clone())?;
        let asset = inspection
            .snapshot
            .assets
            .get(&receipt.request.asset)
            .ok_or_else(|| invalid("Frame asset is absent from its revision"))?;
        if inspection.asset_measurements[&asset.hash] != receipt.request.source_measurement
            || asset.bytes != receipt.source_bytes
            || asset.measurement != receipt.source_probe
        {
            return Err(invalid(
                "Frame receipt differs from its stored source measurement",
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
            return Err(invalid("Frame receipt does not select a movie"));
        };
        let index = usize::try_from(receipt.request.presentation_ordinal)
            .map_err(|_| invalid("Frame ordinal exceeds the host address range"))?;
        let sample = samples
            .get(index)
            .ok_or_else(|| invalid("Frame ordinal exceeds its source index"))?;
        if !native_decode
            || *width != receipt.width
            || *height != receipt.height
            || receipt.decoded_prefix_frames != receipt.request.presentation_ordinal + 1
            || sample.pts != receipt.presentation_time
        {
            return Err(invalid(
                "Frame geometry, ordinal or clock differs from its source index",
            ));
        }
        pixels::extent(*width, *height)?;
        Ok(())
    }

    pub fn verify_frame_inspection(
        &self,
        request: FrameInspectionVerificationRequest,
    ) -> Result<FrameInspectionVerification> {
        let mut result = FrameInspectionVerification {
            schema: 1, project: self.id.clone(), request, verifier: BuildIdentity::current()?,
            state: FrameInspectionVerificationState::PartialRetained,
            observed_receipt_id: None, png_sha256: None, rgba_sha256: None, reasons: Vec::new(),
            scope: "Read-only directory classification. Complete verification checks the expected semantic receipt ID, request equality, PNG bytes and decoded RGBA, stored revision relationship and current source bytes. It does not freshly decode the movie or establish producer attestation, playback, hearing or creative acceptance. All files remain retained. Path observations do not exclude changes between observations.".into(),
        };
        let directory = match result.request.directory.canonicalize() {
            Ok(value) => value,
            Err(error) => return Ok(result.unavailable(error)),
        };
        let before = match fs::symlink_metadata(&directory) {
            Ok(value) => value,
            Err(error) => return Ok(result.unavailable(error)),
        };
        if !before.is_dir() {
            result.state = FrameInspectionVerificationState::ForeignRetained;
            result
                .reasons
                .push("Frame inspection target is not a directory".into());
            return Ok(result);
        }
        let entries = match fs::read_dir(&directory) {
            Ok(value) => value,
            Err(error) => return Ok(result.unavailable(error)),
        };
        let mut names = Vec::new();
        for entry in entries {
            let entry = match entry {
                Ok(value) => value,
                Err(error) => return Ok(result.unavailable(error)),
            };
            let filename = entry.file_name();
            let file_type = match entry.file_type() {
                Ok(value) => value,
                Err(error) => return Ok(result.unavailable(error)),
            };
            if !file_type.is_file()
                || !matches!(
                    filename.to_str(),
                    Some("request.json" | "source-frame.png" | "receipt.json")
                )
            {
                result.state = FrameInspectionVerificationState::ForeignRetained;
                result
                    .reasons
                    .push("Directory contains an unknown entry or non-regular file".into());
                return Ok(result);
            }
            names.push(filename);
        }
        if names.len() != 3 {
            result
                .reasons
                .push("One or more required files are absent; ownership is unproven".into());
            return Ok(result);
        }
        let verify = (|| -> Result<()> {
            let receipt: FrameInspectionReceipt = serde_json::from_slice(&read_bounded(
                &directory.join("receipt.json"),
                1024 * 1024,
            )?)?;
            let observed = ContentHash::document(&receipt)?;
            result.observed_receipt_id = Some(observed.clone());
            if observed != result.request.receipt_id {
                return Err(invalid("Receipt differs from the expected receipt ID"));
            }
            let request: FrameInspectionRequest = serde_json::from_slice(&read_bounded(
                &directory.join("request.json"),
                1024 * 1024,
            )?)?;
            if ContentHash::document(&request)? != ContentHash::document(&receipt.request)? {
                return Err(invalid("Saved request differs from the receipt request"));
            }
            self.check_frame_receipt(&receipt)?;
            let asset = self
                .studio
                .root
                .join("blobs")
                .join(receipt.request.asset.as_str());
            let mut source =
                VerifiedSource::open(&asset, &receipt.request.asset, receipt.source_bytes)?;
            let png = read_bounded(
                &directory.join("source-frame.png"),
                pixels::MAX_OWNED_FRAME_BYTES + 2 * 1024 * 1024,
            )?;
            check_png(&receipt, &png)?;
            source.verify()?;
            result.png_sha256 = Some(receipt.png_sha256);
            result.rgba_sha256 = Some(receipt.rgba_sha256);
            let after = fs::symlink_metadata(&directory)?;
            if before.dev() != after.dev() || before.ino() != after.ino() || !after.is_dir() {
                return Err(invalid(
                    "Frame directory identity changed during verification",
                ));
            }
            Ok(())
        })();
        match verify {
            Ok(()) => result.state = FrameInspectionVerificationState::CompleteVerified,
            Err(error) => {
                result.state = match error.code.as_str() {
                    "frame_inspection_foreign" => FrameInspectionVerificationState::ForeignRetained,
                    "frame_inspection_invalid" | "invalid_json" => {
                        FrameInspectionVerificationState::CorruptRetained
                    }
                    _ => FrameInspectionVerificationState::UnverifiableRetained,
                };
                result.reasons.push(error.to_string());
            }
        }
        Ok(result)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::MediaTime;

    fn receipt() -> (FrameInspectionReceipt, Vec<u8>) {
        let rgba = [20, 30, 40, 255];
        let mut bytes = Vec::new();
        {
            let mut encoder = png::Encoder::new(&mut bytes, 1, 1);
            encoder.set_color(png::ColorType::Rgba);
            encoder.set_depth(png::BitDepth::Eight);
            encoder
                .write_header()
                .unwrap()
                .write_image_data(&rgba)
                .unwrap();
        }
        let hash = ContentHash::bytes(b"fixture");
        (
            FrameInspectionReceipt {
                schema: 1,
                project: EntityId::parse("test").unwrap(),
                request: FrameInspectionRequest {
                    revision: hash.clone(),
                    asset: hash.clone(),
                    source_measurement: hash,
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
                rgba_sha256: ContentHash::bytes(&rgba),
                png_sha256: ContentHash::bytes(&bytes),
                png_bytes: bytes.len() as u64,
                scope: "PNG integrity fixture only".into(),
            },
            bytes,
        )
    }

    #[test]
    fn png_verification_rejects_changed_bytes_and_pixel_claims() {
        let (mut receipt, mut bytes) = receipt();
        check_png(&receipt, &bytes).unwrap();
        receipt.rgba_sha256 = ContentHash::bytes(b"different pixels");
        assert!(check_png(&receipt, &bytes).is_err());
        bytes[0] ^= 1;
        assert!(check_png(&receipt, &bytes).is_err());
    }

    #[test]
    fn png_dimensions_are_checked_before_raster_allocation() {
        let (mut receipt, bytes) = receipt();
        receipt.width = 2;
        assert!(check_png(&receipt, &bytes).is_err());
        receipt.width = u32::MAX;
        assert_eq!(
            check_png(&receipt, &bytes).unwrap_err().code,
            "unsupported_pixel_extent"
        );
    }

    #[test]
    fn oversized_documents_are_rejected_without_changing_the_file() {
        let path =
            std::env::temp_dir().join(format!("studio-frame-read-bound-{}", std::process::id()));
        fs::write(&path, b"preserved").unwrap();
        assert!(read_bounded(&path, 4).is_err());
        assert_eq!(fs::read(&path).unwrap(), b"preserved");
        fs::remove_file(path).unwrap();
    }
}
