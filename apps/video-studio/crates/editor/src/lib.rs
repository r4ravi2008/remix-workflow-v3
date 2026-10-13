mod alpha_picture;
mod composition;
mod curve;
mod export_stage;
mod exports;
mod frame;
mod frame_verification;
mod framing;
mod identity;
mod image;
mod mask;
mod media;
mod model;
mod motion;
mod movie;
mod native_format;
mod owned_directory;
mod pcm;
mod pixels;
mod plan;
mod project;
mod publication;
mod verified_source;

pub use composition::{Opacity, PictureExecutionEvidence, PicturePlacement, PixelRect};
pub use exports::{
    ArtifactReceipt, ArtifactVerification, ExportCancellation, ExportResult, StagingReconciliation,
    StoredArtifact,
};
pub use frame::{
    FrameInspection, FrameInspectionReceipt, FrameInspectionRequest, SavedFrameInspection,
};
pub use frame_verification::{
    FrameInspectionVerification, FrameInspectionVerificationRequest,
    FrameInspectionVerificationState,
};
pub use framing::{Framing, NormalizedCrop, PictureFit};
pub use identity::BuildIdentity;
pub use mask::{MaskAxis, MaskProgress, MaskProgressQ16, PictureMask, PlannedPictureMask};
pub use model::*;
pub use motion::{
    CurveInterpolation, CurveKey, OpacityQ16, PictureMotion, PlannedCurve, PlannedPictureMotion,
    PropertyCurve,
};
pub use movie::{
    NativeColorTupleEvidence, NativeMeasurements, NativeVideoColorEvidence, StreamingAudioEvidence,
};
pub use native_format::{FourCc, NativeFormatEvidence, Pcm24Comparison, PcmEncodingEvidence};
pub use pcm::PcmStreamEvidence;
pub use plan::{
    AlphaPolicy, AudioUse, ExportPlan, ExportRequest, MovieProfile, PreparedExport, VideoUse,
};
pub use project::{Project, Studio};

pub type Result<T> = std::result::Result<T, StudioError>;

#[derive(Clone, Debug, serde::Serialize)]
pub struct StudioError {
    pub code: String,
    pub detail: String,
}

impl StudioError {
    pub(crate) fn new(code: &str, detail: impl Into<String>) -> Self {
        Self {
            code: code.into(),
            detail: detail.into(),
        }
    }
}

impl std::fmt::Display for StudioError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}: {}", self.code, self.detail)
    }
}
impl std::error::Error for StudioError {}
impl From<std::io::Error> for StudioError {
    fn from(error: std::io::Error) -> Self {
        Self::new("io_error", error.to_string())
    }
}
impl From<rusqlite::Error> for StudioError {
    fn from(error: rusqlite::Error) -> Self {
        Self::new("storage_error", error.to_string())
    }
}
impl From<serde_json::Error> for StudioError {
    fn from(error: serde_json::Error) -> Self {
        Self::new("invalid_json", error.to_string())
    }
}
