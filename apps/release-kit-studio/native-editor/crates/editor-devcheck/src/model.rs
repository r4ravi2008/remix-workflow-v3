use serde::Serialize;
use std::collections::BTreeMap;

#[derive(Clone, Copy, Debug, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum VerificationMode {
    Architecture,
    Full,
}
#[derive(Clone, Copy, Debug, Serialize, serde::Deserialize, PartialEq, Eq)]
#[serde(rename_all = "kebab-case")]
pub enum RuntimeProfile {
    Default,
    TestHooks,
}
#[derive(Clone, Copy, Debug, Serialize, PartialEq, Eq, PartialOrd, Ord)]
#[serde(rename_all = "kebab-case")]
pub enum CheckId {
    WorkspaceInventory,
    WorkspaceOwnership,
    RuntimeSourcePolicy,
    DependencyPolicy,
    SpecificationDocuments,
    FeatureDocumentCoverage,
    IntentContracts,
    IntentScenarios,
    CapabilityState,
    GuardrailNegativeFixtures,
    Toolchain,
    Format,
    ClippyDefault,
    TestDefault,
    BuildDefault,
    RuntimeDefault,
    ClippyTestHooks,
    TestTestHooks,
    BuildTestHooks,
    EvidenceAudit,
    EvidenceInventory,
    WorkspaceStable,
}
impl VerificationMode {
    pub fn plan(self) -> &'static [CheckId] {
        use CheckId::*;
        const ARCH: &[CheckId] = &[
            WorkspaceInventory,
            WorkspaceOwnership,
            RuntimeSourcePolicy,
            DependencyPolicy,
            CapabilityState,
            GuardrailNegativeFixtures,
            SpecificationDocuments,
            FeatureDocumentCoverage,
            IntentContracts,
            WorkspaceStable,
            EvidenceInventory,
        ];
        const FULL: &[CheckId] = &[
            WorkspaceInventory,
            WorkspaceOwnership,
            RuntimeSourcePolicy,
            DependencyPolicy,
            CapabilityState,
            GuardrailNegativeFixtures,
            SpecificationDocuments,
            FeatureDocumentCoverage,
            IntentContracts,
            Toolchain,
            Format,
            ClippyDefault,
            TestDefault,
            BuildDefault,
            RuntimeDefault,
            ClippyTestHooks,
            TestTestHooks,
            BuildTestHooks,
            EvidenceAudit,
            IntentScenarios,
            WorkspaceStable,
            EvidenceInventory,
        ];
        match self {
            Self::Architecture => ARCH,
            Self::Full => FULL,
        }
    }
}
#[derive(Debug, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum RunVerdict {
    Passed,
    Failed,
    Incomplete,
    FailedAndIncomplete,
}
impl RunVerdict {
    pub fn derive(mode: VerificationMode, checks: &[CheckRecord]) -> Self {
        let required: std::collections::BTreeSet<_> = mode.plan().iter().copied().collect();
        let actual: std::collections::BTreeSet<_> = checks.iter().map(|c| c.id).collect();
        let missing = required != actual || checks.len() != required.len();
        let failed = checks
            .iter()
            .any(|c| matches!(c.outcome, CheckOutcome::Failed { .. }));
        let incomplete = missing
            || checks
                .iter()
                .any(|c| matches!(c.outcome, CheckOutcome::Incomplete { .. }));
        match (failed, incomplete) {
            (false, false) => Self::Passed,
            (true, false) => Self::Failed,
            (false, true) => Self::Incomplete,
            (true, true) => Self::FailedAndIncomplete,
        }
    }
    pub fn exit_code(&self) -> u8 {
        match self {
            Self::Passed => 0,
            Self::Incomplete => 2,
            _ => 1,
        }
    }
}
#[derive(Debug, Serialize)]
pub struct NonEmpty<T> {
    pub head: T,
    pub tail: Vec<T>,
}
#[derive(Debug, Serialize)]
pub struct Violation {
    pub code: String,
    pub path: Option<String>,
    pub line: Option<usize>,
    pub message: String,
}
impl Violation {
    pub fn new(code: &str, path: Option<String>, message: impl Into<String>) -> Self {
        Self {
            code: code.into(),
            path,
            line: None,
            message: message.into(),
        }
    }
}
#[derive(Debug, Serialize)]
#[serde(tag = "kind", rename_all = "kebab-case")]
pub enum CheckOutcome {
    Passed,
    Failed { violations: NonEmpty<Violation> },
    Incomplete { reason: IncompleteReason },
}
#[derive(Debug, Serialize)]
#[serde(tag = "kind", rename_all = "kebab-case")]
pub enum IncompleteReason {
    MissingTool {
        tool: String,
    },
    UnsupportedPlatform {
        detail: String,
    },
    TimedOut {
        deadline_ms: u64,
    },
    OutputLimitExceeded {
        limit_bytes: u64,
    },
    MalformedOutput {
        detail: String,
    },
    WorkspaceChanged {
        before_sha256: String,
        after_sha256: String,
    },
    IoFailure {
        detail: String,
    },
}
impl CheckOutcome {
    pub fn violations(mut values: Vec<Violation>) -> Self {
        if values.is_empty() {
            Self::Passed
        } else {
            let head = values.remove(0);
            Self::Failed {
                violations: NonEmpty { head, tail: values },
            }
        }
    }
    pub fn io(error: impl std::fmt::Display) -> Self {
        Self::Incomplete {
            reason: IncompleteReason::IoFailure {
                detail: error.to_string(),
            },
        }
    }
}
#[derive(Debug, Serialize)]
pub struct CheckRecord {
    pub id: CheckId,
    pub outcome: CheckOutcome,
    pub processes: Vec<ProcessRecord>,
    pub evidence: Vec<String>,
}
#[derive(Debug, Serialize)]
#[serde(tag = "kind", rename_all = "kebab-case")]
pub enum ProcessExit {
    Code { code: i32 },
    Signal { signal: i32 },
    TimedOut,
    SpawnFailed { error: String },
    UnsupportedPlatform,
}
#[derive(Debug, Serialize)]
pub struct CapturedStream {
    pub path: String,
    pub observed_bytes: u64,
    pub saved_bytes: u64,
    pub sha256: String,
    pub truncated: bool,
}
#[derive(Debug, Serialize)]
pub struct ProcessRecord {
    pub argv: Vec<String>,
    pub cwd: String,
    pub selected_environment: BTreeMap<String, String>,
    pub started_at: u128,
    pub duration_ms: u128,
    pub exit: ProcessExit,
    pub stdout: CapturedStream,
    pub stderr: CapturedStream,
}
#[derive(Debug, Serialize, PartialEq, Eq, PartialOrd, Ord)]
pub struct HashedFile {
    pub path: String,
    pub bytes: u64,
    pub sha256: String,
}
#[derive(Debug, Serialize, PartialEq, Eq, PartialOrd, Ord)]
pub struct SourceIdentity {
    pub scope: String,
    pub files: Vec<HashedFile>,
    pub sha256: String,
}
#[derive(Debug, Serialize)]
pub struct RuntimeIdentity {
    pub profile: RuntimeProfile,
    pub binary: HashedFile,
    pub discovery: serde_json::Value,
}
#[derive(Debug, Serialize)]
pub struct EvidenceLink {
    pub path: String,
    pub target: String,
    pub target_sha256: String,
    pub scope: String,
}
#[derive(Debug, Serialize)]
pub struct VerificationReport {
    pub report_version: u16,
    pub run_id: String,
    pub mode: VerificationMode,
    pub assurance_scope: String,
    pub started_at: u128,
    pub finished_at: u128,
    pub verdict: RunVerdict,
    pub source: SourceIdentity,
    pub verifier: HashedFile,
    pub runtime: Vec<RuntimeIdentity>,
    pub checks: Vec<CheckRecord>,
    pub artifacts: Vec<HashedFile>,
    pub path_fixtures: Vec<EvidenceLink>,
    pub intent_coverage: Option<HashedFile>,
    pub capability_promotion_performed: bool,
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn compiled_plans_have_unique_ids() {
        for mode in [VerificationMode::Architecture, VerificationMode::Full] {
            let unique: std::collections::BTreeSet<_> = mode.plan().iter().collect();
            assert_eq!(unique.len(), mode.plan().len());
        }
    }
    #[test]
    fn missing_required_plan_is_incomplete() {
        assert!(matches!(
            RunVerdict::derive(VerificationMode::Full, &[]),
            RunVerdict::Incomplete
        ));
    }
}
