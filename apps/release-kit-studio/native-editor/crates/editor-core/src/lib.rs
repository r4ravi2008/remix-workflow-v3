#![forbid(unsafe_code)]

mod frame;
mod project;
mod store;

pub use frame::{ArtifactReceipt, Verification};
pub use project::*;
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::path::{Path, PathBuf};

pub const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const PROTOCOL_VERSION: u8 = 1;
pub const IDENTITY_VERSION: u8 = 1;
pub const IMPLEMENTED_FEATURES: [&str; 8] = [
    "CORE-01", "CORE-02", "CORE-03", "CORE-04", "CORE-05", "CORE-06", "CORE-07", "CORE-08",
];

#[derive(Clone, Debug, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Limits {
    pub input_bytes: usize,
    pub output_bytes: usize,
    pub canvas_axis: u32,
    pub canvas_pixels: u64,
    pub frames: u64,
    pub clips: usize,
    pub deadline_seconds: u32,
}
impl Limits {
    pub fn p0() -> Self {
        Self {
            input_bytes: 1_048_576,
            output_bytes: 4_194_304,
            canvas_axis: 2048,
            canvas_pixels: 4_194_304,
            frames: 10_000_000,
            clips: 10_000,
            deadline_seconds: 30,
        }
    }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ErrorCode {
    InvalidInput,
    UnknownTool,
    UnsupportedCapability,
    ProjectNotFound,
    ProjectExists,
    RevisionNotFound,
    ArtifactNotFound,
    RevisionConflict,
    IntentConflict,
    StoreBusy,
    StorageFailure,
    ArtifactIntegrityMismatch,
    ProtocolMismatch,
    ProcessTimeout,
    ProcessInterrupted,
    InternalFailure,
}
macro_rules! retry_kind {
    ($name:ident, $wire:literal) => {
        #[derive(Clone, Copy, Debug, Serialize, Deserialize, JsonSchema)]
        pub enum $name {
            #[serde(rename = $wire)]
            Required,
        }
    };
}
retry_kind!(CorrectRequest, "correct_request");
retry_kind!(DiscoverTools, "discover_tools");
retry_kind!(InspectFeature, "inspect_feature");
retry_kind!(InspectProject, "inspect_project");
retry_kind!(InspectThenRebase, "inspect_then_rebase");
retry_kind!(PreserveIntent, "preserve_intent");
retry_kind!(SameIntentBoundedBackoff, "same_intent_bounded_backoff");
retry_kind!(DiagnoseStorage, "diagnose_storage");
retry_kind!(PreserveEvidence, "preserve_evidence");
retry_kind!(DiscoverProtocol, "discover_protocol");
retry_kind!(InspectIntent, "inspect_intent");
#[derive(Clone, Debug, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct EmptyDetails {}
#[derive(Clone, Debug, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct RevisionDetails {
    pub current_revision: Revision,
}
#[derive(Clone, Debug, Serialize, Deserialize, JsonSchema)]
#[serde(tag = "code", rename_all = "snake_case", deny_unknown_fields)]
pub enum EditorError {
    InvalidInput {
        message: String,
        retry: CorrectRequest,
        details: EmptyDetails,
    },
    UnknownTool {
        message: String,
        retry: DiscoverTools,
        details: EmptyDetails,
    },
    UnsupportedCapability {
        message: String,
        retry: InspectFeature,
        details: EmptyDetails,
    },
    ProjectNotFound {
        message: String,
        retry: InspectProject,
        details: EmptyDetails,
    },
    ProjectExists {
        message: String,
        retry: InspectProject,
        details: EmptyDetails,
    },
    RevisionNotFound {
        message: String,
        retry: InspectProject,
        details: EmptyDetails,
    },
    ArtifactNotFound {
        message: String,
        retry: InspectProject,
        details: EmptyDetails,
    },
    RevisionConflict {
        message: String,
        retry: InspectThenRebase,
        details: RevisionDetails,
    },
    IntentConflict {
        message: String,
        retry: PreserveIntent,
        details: EmptyDetails,
    },
    StoreBusy {
        message: String,
        retry: SameIntentBoundedBackoff,
        details: EmptyDetails,
    },
    StorageFailure {
        message: String,
        retry: DiagnoseStorage,
        details: EmptyDetails,
    },
    ArtifactIntegrityMismatch {
        message: String,
        retry: PreserveEvidence,
        details: EmptyDetails,
    },
    ProtocolMismatch {
        message: String,
        retry: DiscoverProtocol,
        details: EmptyDetails,
    },
    ProcessTimeout {
        message: String,
        retry: InspectIntent,
        details: EmptyDetails,
    },
    ProcessInterrupted {
        message: String,
        retry: InspectIntent,
        details: EmptyDetails,
    },
    InternalFailure {
        message: String,
        retry: DiagnoseStorage,
        details: EmptyDetails,
    },
}
impl EditorError {
    pub fn new(code: ErrorCode, message: impl Into<String>) -> Self {
        let message = message.into();
        match code {
            ErrorCode::InvalidInput => Self::InvalidInput {
                message,
                retry: CorrectRequest::Required,
                details: EmptyDetails {},
            },
            ErrorCode::UnknownTool => Self::UnknownTool {
                message,
                retry: DiscoverTools::Required,
                details: EmptyDetails {},
            },
            ErrorCode::UnsupportedCapability => Self::UnsupportedCapability {
                message,
                retry: InspectFeature::Required,
                details: EmptyDetails {},
            },
            ErrorCode::ProjectNotFound => Self::ProjectNotFound {
                message,
                retry: InspectProject::Required,
                details: EmptyDetails {},
            },
            ErrorCode::ProjectExists => Self::ProjectExists {
                message,
                retry: InspectProject::Required,
                details: EmptyDetails {},
            },
            ErrorCode::RevisionNotFound => Self::RevisionNotFound {
                message,
                retry: InspectProject::Required,
                details: EmptyDetails {},
            },
            ErrorCode::ArtifactNotFound => Self::ArtifactNotFound {
                message,
                retry: InspectProject::Required,
                details: EmptyDetails {},
            },
            ErrorCode::RevisionConflict => Self::RevisionConflict {
                message,
                retry: InspectThenRebase::Required,
                details: RevisionDetails {
                    current_revision: Revision::new(0).expect("zero revision"),
                },
            },
            ErrorCode::IntentConflict => Self::IntentConflict {
                message,
                retry: PreserveIntent::Required,
                details: EmptyDetails {},
            },
            ErrorCode::StoreBusy => Self::StoreBusy {
                message,
                retry: SameIntentBoundedBackoff::Required,
                details: EmptyDetails {},
            },
            ErrorCode::StorageFailure => Self::StorageFailure {
                message,
                retry: DiagnoseStorage::Required,
                details: EmptyDetails {},
            },
            ErrorCode::ArtifactIntegrityMismatch => Self::ArtifactIntegrityMismatch {
                message,
                retry: PreserveEvidence::Required,
                details: EmptyDetails {},
            },
            ErrorCode::ProtocolMismatch => Self::ProtocolMismatch {
                message,
                retry: DiscoverProtocol::Required,
                details: EmptyDetails {},
            },
            ErrorCode::ProcessTimeout => Self::ProcessTimeout {
                message,
                retry: InspectIntent::Required,
                details: EmptyDetails {},
            },
            ErrorCode::ProcessInterrupted => Self::ProcessInterrupted {
                message,
                retry: InspectIntent::Required,
                details: EmptyDetails {},
            },
            ErrorCode::InternalFailure => Self::InternalFailure {
                message,
                retry: DiagnoseStorage::Required,
                details: EmptyDetails {},
            },
        }
    }
    pub fn revision_conflict(current_revision: Revision) -> Self {
        Self::RevisionConflict {
            message: "The expected revision differs from the current revision.".into(),
            retry: InspectThenRebase::Required,
            details: RevisionDetails { current_revision },
        }
    }
    pub fn invalid(message: impl Into<String>) -> Self {
        Self::new(ErrorCode::InvalidInput, message)
    }
    pub fn code(&self) -> ErrorCode {
        match self {
            Self::InvalidInput { .. } => ErrorCode::InvalidInput,
            Self::UnknownTool { .. } => ErrorCode::UnknownTool,
            Self::UnsupportedCapability { .. } => ErrorCode::UnsupportedCapability,
            Self::ProjectNotFound { .. } => ErrorCode::ProjectNotFound,
            Self::ProjectExists { .. } => ErrorCode::ProjectExists,
            Self::RevisionNotFound { .. } => ErrorCode::RevisionNotFound,
            Self::ArtifactNotFound { .. } => ErrorCode::ArtifactNotFound,
            Self::RevisionConflict { .. } => ErrorCode::RevisionConflict,
            Self::IntentConflict { .. } => ErrorCode::IntentConflict,
            Self::StoreBusy { .. } => ErrorCode::StoreBusy,
            Self::StorageFailure { .. } => ErrorCode::StorageFailure,
            Self::ArtifactIntegrityMismatch { .. } => ErrorCode::ArtifactIntegrityMismatch,
            Self::ProtocolMismatch { .. } => ErrorCode::ProtocolMismatch,
            Self::ProcessTimeout { .. } => ErrorCode::ProcessTimeout,
            Self::ProcessInterrupted { .. } => ErrorCode::ProcessInterrupted,
            Self::InternalFailure { .. } => ErrorCode::InternalFailure,
        }
    }
    pub fn exit_code(&self) -> i32 {
        if matches!(
            self.code(),
            ErrorCode::StorageFailure
                | ErrorCode::InternalFailure
                | ErrorCode::ProtocolMismatch
                | ErrorCode::ProcessTimeout
                | ErrorCode::ProcessInterrupted
        ) {
            1
        } else {
            2
        }
    }
}
impl std::fmt::Display for EditorError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let message = match self {
            Self::InvalidInput { message, .. }
            | Self::UnknownTool { message, .. }
            | Self::UnsupportedCapability { message, .. }
            | Self::ProjectNotFound { message, .. }
            | Self::ProjectExists { message, .. }
            | Self::RevisionNotFound { message, .. }
            | Self::ArtifactNotFound { message, .. }
            | Self::RevisionConflict { message, .. }
            | Self::IntentConflict { message, .. }
            | Self::StoreBusy { message, .. }
            | Self::StorageFailure { message, .. }
            | Self::ArtifactIntegrityMismatch { message, .. }
            | Self::ProtocolMismatch { message, .. }
            | Self::ProcessTimeout { message, .. }
            | Self::ProcessInterrupted { message, .. }
            | Self::InternalFailure { message, .. } => message,
        };
        write!(f, "{message}")
    }
}
impl std::error::Error for EditorError {}
impl From<std::io::Error> for EditorError {
    fn from(e: std::io::Error) -> Self {
        Self::new(ErrorCode::StorageFailure, e.to_string())
    }
}
impl From<rusqlite::Error> for EditorError {
    fn from(e: rusqlite::Error) -> Self {
        let code = match &e {
            rusqlite::Error::SqliteFailure(f, _)
                if matches!(
                    f.code,
                    rusqlite::ErrorCode::DatabaseBusy | rusqlite::ErrorCode::DatabaseLocked
                ) =>
            {
                ErrorCode::StoreBusy
            }
            _ => ErrorCode::StorageFailure,
        };
        Self::new(code, e.to_string())
    }
}
impl From<serde_json::Error> for EditorError {
    fn from(e: serde_json::Error) -> Self {
        Self::new(ErrorCode::StorageFailure, e.to_string())
    }
}
pub fn sha256(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}
pub fn canonical_bytes<T: Serialize>(input: &T) -> Result<Vec<u8>, EditorError> {
    serde_jcs::to_vec(input)
        .map_err(|e| EditorError::new(ErrorCode::InternalFailure, e.to_string()))
}
pub fn structured_hash<T: Serialize>(input: &T) -> Result<String, EditorError> {
    Ok(sha256(&canonical_bytes(input)?))
}

#[derive(Clone, Debug, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ProjectResult {
    pub project_id: ProjectId,
    pub revision: Revision,
    pub project_sha256: String,
}
#[derive(Clone, Debug, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Inspection {
    pub snapshot: Snapshot,
    pub project_sha256: String,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(tag = "kind", content = "result")]
pub enum CommandResult {
    Project(ProjectResult),
    Inspection(Inspection),
    Artifact(ArtifactReceipt),
    Verification(Verification),
}
#[derive(Clone, Debug)]
pub struct Execution {
    pub result: CommandResult,
    pub replayed: bool,
}

pub struct EditorConfig {
    pub limits: Limits,
    pub binary_sha256: String,
}
pub struct Editor {
    root: PathBuf,
    limits: Limits,
    binary_sha256: String,
}
impl Editor {
    pub fn open(root: impl AsRef<Path>, config: EditorConfig) -> Result<Self, EditorError> {
        if config.binary_sha256.len() != 64
            || !config
                .binary_sha256
                .bytes()
                .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
        {
            return Err(EditorError::invalid(
                "The renderer build identity must be lowercase SHA-256.",
            ));
        }
        let root = store::safe_root(root.as_ref())?;
        Ok(Self {
            root,
            limits: config.limits,
            binary_sha256: config.binary_sha256,
        })
    }
    pub fn execute(&self, command: Command) -> Result<Execution, EditorError> {
        match &command {
            Command::CreateProject(input) => {
                input.timeline.validate(&self.limits)?;
                if input.name.is_empty() || input.name.len() > 4096 {
                    return Err(EditorError::invalid(
                        "Project name requires 1..4096 UTF-8 bytes.",
                    ));
                }
            }
            Command::CommitProject(input)
                if input.edits.is_empty() || input.edits.len() > self.limits.clips =>
            {
                return Err(EditorError::invalid(
                    "A transaction requires 1..10000 edits.",
                ))
            }
            _ => {}
        }
        store::execute(self, command)
    }
}

#[cfg(feature = "test-hooks")]
fn checkpoint(name: &str) {
    if std::env::var("NATIVE_EDITOR_TEST_HOOK").as_deref() == Ok(name) {
        if let Ok(path) = std::env::var("NATIVE_EDITOR_TEST_READY") {
            let _ = std::fs::write(path, name);
        }
        loop {
            std::thread::park_timeout(std::time::Duration::from_secs(1));
        }
    }
}
#[cfg(not(feature = "test-hooks"))]
fn checkpoint(_: &str) {}
