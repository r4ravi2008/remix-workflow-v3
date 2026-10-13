use crate::*;
use std::fs::{self, File, OpenOptions};
use std::io::Write;
use std::path::Path;

#[derive(Clone, Debug, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ArtifactReceipt {
    pub receipt_version: u8,
    pub project_id: ProjectId,
    pub artifact_id: ArtifactId,
    pub project_sha256: String,
    pub revision: Revision,
    pub intent_id: IntentId,
    pub renderer_version: String,
    pub binary_sha256: String,
    pub bytes: u64,
    pub sha256: String,
    pub width: u32,
    pub height: u32,
    pub pixel_format: FrameFormat,
    pub frame: FrameIndex,
    pub path: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub receipt_sha256: Option<String>,
}
#[derive(Clone, Debug, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Verification {
    pub receipt: ArtifactReceipt,
    pub measured_sha256: String,
    pub measured_bytes: u64,
    pub verified: bool,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct Pending {
    pub input: RenderFrame,
    pub project_sha256: String,
    pub binary_sha256: String,
    pub renderer_version: String,
    pub artifact_id: ArtifactId,
}
impl Pending {
    pub fn receipt(
        &self,
        snapshot: &Snapshot,
        bytes: &[u8],
    ) -> Result<ArtifactReceipt, EditorError> {
        let mut receipt = ArtifactReceipt {
            receipt_version: 1,
            project_id: self.input.project_id.clone(),
            artifact_id: self.artifact_id.clone(),
            project_sha256: self.project_sha256.clone(),
            revision: self.input.revision,
            intent_id: self.input.intent_id.clone(),
            renderer_version: self.renderer_version.clone(),
            binary_sha256: self.binary_sha256.clone(),
            bytes: bytes.len() as u64,
            sha256: sha256(bytes),
            width: snapshot.timeline.canvas.width,
            height: snapshot.timeline.canvas.height,
            pixel_format: self.input.format,
            frame: self.input.frame,
            path: format!("artifacts/{}.png", self.artifact_id.as_str()),
            receipt_sha256: None,
        };
        receipt.receipt_sha256 = Some(structured_hash(&receipt)?);
        Ok(receipt)
    }
}
pub(crate) fn encode(snapshot: &Snapshot, frame: FrameIndex) -> Result<Vec<u8>, EditorError> {
    if frame.get() >= snapshot.timeline.duration_frames.get() {
        return Err(EditorError::invalid("Frame is outside the timeline."));
    }
    let mut rgba = [0, 0, 0, 0];
    for clip in &snapshot.clips {
        if clip.start_frame <= frame && frame.get() < clip.interval().end()? {
            let VisualSource::Solid { rgba: color } = clip.source;
            rgba = color;
            break;
        }
    }
    let canvas = snapshot.timeline.canvas;
    let mut pixels = Vec::with_capacity(canvas.width as usize * canvas.height as usize * 4);
    for _ in 0..u64::from(canvas.width) * u64::from(canvas.height) {
        pixels.extend_from_slice(&rgba);
    }
    let mut bytes = Vec::new();
    {
        let mut encoder = png::Encoder::new(&mut bytes, canvas.width, canvas.height);
        encoder.set_color(png::ColorType::Rgba);
        encoder.set_depth(png::BitDepth::Eight);
        encoder.set_filter(png::FilterType::NoFilter);
        encoder.set_compression(png::Compression::Fast);
        let mut writer = encoder
            .write_header()
            .map_err(|e| EditorError::new(ErrorCode::InternalFailure, e.to_string()))?;
        writer
            .write_image_data(&pixels)
            .map_err(|e| EditorError::new(ErrorCode::InternalFailure, e.to_string()))?;
        writer
            .finish()
            .map_err(|e| EditorError::new(ErrorCode::InternalFailure, e.to_string()))?;
    }
    Ok(bytes)
}
pub(crate) fn promote(
    directory: &Path,
    pending: &Pending,
    bytes: &[u8],
) -> Result<(), EditorError> {
    let artifacts = directory.join("artifacts");
    crate::store::check_path(&artifacts)?;
    fs::create_dir_all(&artifacts)?;
    let target = artifacts.join(format!("{}.png", pending.artifact_id.as_str()));
    let staging = artifacts.join(format!("{}.staging", pending.artifact_id.as_str()));
    crate::store::check_path(&target)?;
    crate::store::check_path(&staging)?;
    // A pending file is adoptable only when regeneration proves every byte for this build.
    if target.exists() {
        if fs::read(&target)? != bytes {
            return Err(integrity(
                "Pending promoted bytes differ from deterministic output.",
            ));
        }
        File::open(&target)?.sync_all()?;
        File::open(&artifacts)?.sync_all()?;
        return Ok(());
    }
    if staging.exists() && fs::read(&staging)? == bytes {
        File::open(&staging)?.sync_all()?;
    } else {
        let mut file = OpenOptions::new()
            .write(true)
            .create(true)
            .truncate(true)
            .open(&staging)?;
        let halfway = bytes.len() / 2;
        file.write_all(&bytes[..halfway])?;
        crate::checkpoint("during-file-write");
        file.write_all(&bytes[halfway..])?;
        file.sync_all()?;
    }
    crate::checkpoint("after-file-flush");
    fs::rename(&staging, &target)?;
    File::open(&artifacts)?.sync_all()?;
    crate::checkpoint("after-promotion");
    Ok(())
}
pub(crate) fn verify(
    directory: &Path,
    snapshot: &Snapshot,
    receipt: &ArtifactReceipt,
) -> Result<Verification, EditorError> {
    let mut unsigned = receipt.clone();
    unsigned.receipt_sha256 = None;
    if receipt.receipt_version != 1
        || receipt.receipt_sha256.as_deref() != Some(structured_hash(&unsigned)?.as_str())
        || receipt.project_id != snapshot.project_id
        || receipt.revision != snapshot.revision
        || receipt.project_sha256 != structured_hash(snapshot)?
        || receipt.width != snapshot.timeline.canvas.width
        || receipt.height != snapshot.timeline.canvas.height
        || receipt.path != format!("artifacts/{}.png", receipt.artifact_id.as_str())
    {
        return Err(integrity(
            "The authoritative receipt binding is inconsistent.",
        ));
    }
    let path = directory.join(&receipt.path);
    crate::store::check_path(&path)?;
    let metadata = fs::metadata(&path).map_err(|_| integrity("Registered artifact is missing."))?;
    if !metadata.is_file() || metadata.len() != receipt.bytes || metadata.len() > 20_000_000 {
        return Err(integrity("Artifact byte count differs from its receipt."));
    }
    let bytes = fs::read(path)?;
    let measured_sha256 = sha256(&bytes);
    if measured_sha256 != receipt.sha256 {
        return Err(integrity("Artifact SHA-256 differs from its receipt."));
    }
    let decoder = png::Decoder::new(std::io::Cursor::new(&bytes));
    let mut reader = decoder
        .read_info()
        .map_err(|_| integrity("Artifact PNG cannot be decoded."))?;
    let mut pixels = vec![0; reader.output_buffer_size()];
    let info = reader
        .next_frame(&mut pixels)
        .map_err(|_| integrity("Artifact PNG pixels cannot be decoded."))?;
    if info.width != receipt.width
        || info.height != receipt.height
        || info.color_type != png::ColorType::Rgba
        || info.bit_depth != png::BitDepth::Eight
    {
        return Err(integrity(
            "Artifact dimensions or pixel format differ from its receipt.",
        ));
    }
    Ok(Verification {
        receipt: receipt.clone(),
        measured_sha256,
        measured_bytes: bytes.len() as u64,
        verified: true,
    })
}
pub(crate) fn integrity(message: &str) -> EditorError {
    EditorError::new(ErrorCode::ArtifactIntegrityMismatch, message)
}
