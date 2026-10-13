use crate::{evidence, model::*};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::{collections::BTreeSet, fs, io, path::Path};

pub const CORE_CASES: [(&str, &str, RuntimeProfile); 16] = [
    ("CORE-01-A", "discovery", RuntimeProfile::Default),
    ("CORE-01-B", "schema", RuntimeProfile::Default),
    ("CORE-02-A", "historical-revisions", RuntimeProfile::Default),
    ("CORE-02-B", "rate-normalization", RuntimeProfile::Default),
    ("CORE-03-A", "old-replay", RuntimeProfile::Default),
    ("CORE-03-B", "intent-conflict", RuntimeProfile::Default),
    ("CORE-04-A", "adjacent-intervals", RuntimeProfile::Default),
    ("CORE-04-B", "rollback", RuntimeProfile::Default),
    ("CORE-05-A", "all-pixels", RuntimeProfile::Default),
    ("CORE-05-B", "render-recovery", RuntimeProfile::TestHooks),
    ("CORE-06-A", "receipt-measurements", RuntimeProfile::Default),
    ("CORE-06-B", "tamper-preservation", RuntimeProfile::Default),
    ("CORE-07-A", "framing", RuntimeProfile::Default),
    ("CORE-07-B", "deadline-recovery", RuntimeProfile::TestHooks),
    ("CORE-08-A", "progress-authority", RuntimeProfile::Default),
    ("CORE-08-B", "forged-promotion", RuntimeProfile::Default),
];
#[derive(Deserialize, Serialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct IntentContracts {
    pub version: u16,
    pub core_document_sha256: String,
    pub fixture: Fixture,
    pub features: Vec<CoreContract>,
}
#[derive(Deserialize, Serialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Fixture {
    pub duration_frames: u64,
    pub frame_rate: u64,
    pub width: u32,
    pub height: u32,
    pub background: [u8; 4],
    pub blue: [u8; 4],
    pub gold: [u8; 4],
    pub alpha: [u8; 4],
}
#[derive(Deserialize, Serialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct CoreContract {
    pub feature_id: String,
    pub non_goals: Vec<String>,
    pub review_requirements: Vec<String>,
    pub cases: Vec<CaseContract>,
}
#[derive(Deserialize, Serialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct CaseContract {
    pub case_id: String,
    pub check: String,
    pub profile: RuntimeProfile,
    pub expected: Vec<Expected>,
}
#[derive(Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Expected {
    pub id: String,
    pub value: Value,
}
#[derive(Serialize, Debug, PartialEq, Eq, Clone, Copy)]
#[serde(rename_all = "kebab-case")]
pub enum State {
    Passed,
    Failed,
    Incomplete,
    NotRun,
    PlannedUnobserved,
}
#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Observed {
    pub id: String,
    pub actual: Value,
    pub matched: bool,
    pub mismatch: Option<String>,
}
#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct CaseResult {
    pub case_id: String,
    pub profile: Option<RuntimeProfile>,
    pub status: State,
    pub expected: Vec<Expected>,
    pub observed: Vec<Observed>,
    pub evidence: Vec<HashedFile>,
    pub binding: Value,
    pub incomplete_reason: Option<String>,
}
#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct FeatureResult {
    pub feature_id: String,
    pub ledger_state: String,
    pub source_path: String,
    pub section_sha256: String,
    pub purpose: String,
    pub scenario: String,
    pub case_ids: Vec<String>,
    pub status: State,
    pub cases: Vec<CaseResult>,
    pub non_goals: Vec<String>,
    pub review: Value,
}
#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct IntentCoverageReport {
    pub report_version: u16,
    pub run_id: String,
    pub mode: VerificationMode,
    pub source_sha256: String,
    pub contract_file: Option<HashedFile>,
    pub verdict: String,
    pub counts: Value,
    pub contract_issues: Vec<String>,
    pub features: Vec<FeatureResult>,
    pub capability_promotion_performed: bool,
}
pub fn section<'a>(text: &'a str, id: &str) -> io::Result<&'a str> {
    let marker = format!("## {id}. ");
    let start = text
        .match_indices(&marker)
        .filter(|(n, _)| *n == 0 || text.as_bytes()[n - 1] == b'\n')
        .map(|(n, _)| n)
        .collect::<Vec<_>>();
    if start.len() != 1 {
        return Err(io::Error::other(format!(
            "Expected one feature section {id}"
        )));
    }
    let rest = &text[start[0]..];
    let end = rest.find("\n## ").map(|n| n + 1).unwrap_or(rest.len());
    Ok(&rest[..end])
}
fn prose(text: &str, heading: &str) -> io::Result<String> {
    let marker = format!("### {heading}\n");
    if text.matches(&marker).count() != 1 {
        return Err(io::Error::other(format!("Expected one {heading} section")));
    }
    let rest = text.split_once(&marker).unwrap().1;
    let value = rest.split("\n### ").next().unwrap().trim();
    if value.len() < 50 {
        return Err(io::Error::other(format!("Insufficient {heading} text")));
    }
    Ok(value.into())
}
fn case_ids(text: &str, id: &str) -> io::Result<Vec<String>> {
    let verification = prose(text, "Verification")?;
    let prefix = format!("{id}-");
    let mut ids = vec![];
    for (offset, _) in verification.match_indices(&prefix) {
        let rest = &verification[offset + prefix.len()..];
        let Some(suffix) = rest.as_bytes().first().copied() else {
            continue;
        };
        if suffix.is_ascii_uppercase()
            && rest
                .as_bytes()
                .get(1)
                .is_none_or(|c| !c.is_ascii_alphanumeric() && *c != b'-')
            && (offset == 0 || !verification.as_bytes()[offset - 1].is_ascii_alphanumeric())
        {
            let case = format!("{id}-{}", suffix as char);
            if !ids.contains(&case) {
                ids.push(case);
            }
        }
    }
    if ids.len() < 2 || ids.iter().collect::<BTreeSet<_>>().len() != ids.len() {
        return Err(io::Error::other(format!(
            "Missing or duplicate cases in {id}"
        )));
    }
    Ok(ids)
}
pub fn load(root: &Path, ledger: &Value) -> io::Result<(IntentContracts, Vec<FeatureResult>)> {
    let contracts: IntentContracts =
        serde_json::from_slice(&fs::read(root.join("docs/features/intent-contracts.json"))?)
            .map_err(io::Error::other)?;
    validate(&contracts, &fs::read(root.join("docs/features/core.md"))?)?;
    let rows = documents(root, ledger, Some(&contracts))?;
    Ok((contracts, rows))
}
pub fn documents(
    root: &Path,
    ledger: &Value,
    contracts: Option<&IntentContracts>,
) -> io::Result<Vec<FeatureResult>> {
    let mut rows = vec![];
    let features = ledger["capabilities"]
        .as_array()
        .ok_or_else(|| io::Error::other("Missing ledger features"))?;
    for feature in features {
        let id = feature["id"]
            .as_str()
            .ok_or_else(|| io::Error::other("Missing feature ID"))?;
        let path = feature["behaviorContract"]
            .as_str()
            .ok_or_else(|| io::Error::other("Missing contract path"))?;
        if !path.starts_with("docs/features/") || path.contains("..") {
            return Err(io::Error::other("Unsafe contract path"));
        }
        let text = fs::read_to_string(root.join(path))?;
        let body = section(&text, id)?;
        let ids = case_ids(body, id)?;
        let core = contracts.and_then(|c| c.features.iter().find(|c| c.feature_id == id));
        let state = feature["state"].as_str().unwrap_or("");
        if contracts.is_some()
            && ((core.is_some() && state != "implemented")
                || (core.is_none() && state != "planned"))
        {
            return Err(io::Error::other(format!(
                "Invalid implementation state for {id}"
            )));
        }
        if core.is_some_and(|core| {
            core.cases
                .iter()
                .map(|c| c.case_id.clone())
                .collect::<Vec<_>>()
                != ids
        }) {
            return Err(io::Error::other(format!(
                "Contract/document case mismatch for {id}"
            )));
        }
        let cases = ids
            .iter()
            .map(|id| {
                let contract = core.and_then(|c| c.cases.iter().find(|c| c.case_id == *id));
                CaseResult {
                    case_id: id.clone(),
                    profile: contract.map(|c| c.profile),
                    status: if state == "implemented" {
                        State::NotRun
                    } else {
                        State::PlannedUnobserved
                    },
                    expected: contract
                        .map(|c| {
                            c.expected
                                .iter()
                                .map(|e| Expected {
                                    id: e.id.clone(),
                                    value: e.value.clone(),
                                })
                                .collect()
                        })
                        .unwrap_or_default(),
                    observed: vec![],
                    evidence: vec![],
                    binding: Value::Null,
                    incomplete_reason: None,
                }
            })
            .collect();
        rows.push(FeatureResult { feature_id:id.into(), ledger_state:state.into(), source_path:path.into(), section_sha256:evidence::sha(body.as_bytes()), purpose:prose(body,"What it does")?, scenario:prose(body,"Scenario")?, case_ids:ids, status:if state=="implemented" {State::NotRun} else {State::PlannedUnobserved}, cases, non_goals:core.map(|c| c.non_goals.clone()).unwrap_or_default(), review:json!({"oracleAdequacy":"required-unreviewed","creative":if core.is_some() {"not-applicable"} else {"required-unreviewed"},"playback":if core.is_some(){"not-applicable"}else{"required-unreviewed"},"listening":if core.is_some(){"not-applicable"}else{"required-unreviewed"},"requirements":core.map(|c| &c.review_requirements)}) });
    }
    if rows.len() != 81
        || rows
            .iter()
            .map(|r| &r.feature_id)
            .collect::<BTreeSet<_>>()
            .len()
            != 81
    {
        return Err(io::Error::other("Expected exactly 81 unique features"));
    }
    Ok(rows)
}
fn outcome_keys(check: &str) -> &'static str {
    match check {
        "discovery" => "toolNames implementedFeatureIds binaryMatches noState unknownExit unknownError futureExit futureError",
        "schema" => "schemaIdentity schemaHashMatches unknownFieldExit unknownFieldError noState",
        "historical-revisions" => "createExit firstCommitExit secondCommitExit revision0Exact revision1Exact independentHashes historicalAfterNewRevision latestRevision",
        "rate-normalization" => "originalExit equivalentExit equivalentReplay sameResult normalizedRate zeroExit zeroError noZeroProject",
        "old-replay" => "exit originalResult returnedRevision replayed latestRevision latestUnchanged independentHash",
        "intent-conflict" | "rollback" => "exit error beforeAfterEqual independentHashes",
        "adjacent-intervals" => "exactClips frame47 frame48 frame47Binding frame48Binding",
        "all-pixels" => "background alpha uncovered commitExit backgroundBinding",
        "render-recovery" => "checkpoints boundsExit boundsError onePngPerIntent boundsNoOutput",
        "receipt-measurements" => "exit verified receiptUnchanged independentHashMatches independentLengthMatches independentDimensionsMatch snapshotBinding revision frame",
        "tamper-preservation" => "verifyExit verifyError replayExit replayError alteredBytesPreserved",
        "framing" => "validExit oneDocument requestId emptyStderr schemaMatches duplicateExit duplicateError malformedExit malformedError",
        "deadline-recovery" => "blockedExit blockedError blockedBounded blockedComplete checkpoint timeoutExit timeoutError timeoutBounded timeoutRequestId retryExit retryRevision replayExit replayed sameResult latestRevision largeExit largeComplete largeClips largeResponse readerDelayObserved largeEmptyStderr",
        "progress-authority" => "exit compiledProgressMatches independentBinaryMatches implemented planned emptyEvidence",
        "forged-promotion" => "progressExit progressUnchanged futureExit futureError fakeFilesPreserved",
        _ => "",
    }
}
fn expected_structure(case: &CaseContract, f: &Fixture) -> bool {
    let Some(value) = case.expected.first().map(|e| &e.value) else {
        return false;
    };
    let Some(object) = value.as_object() else {
        return false;
    };
    let keys: BTreeSet<_> = object.keys().map(String::as_str).collect();
    if keys != outcome_keys(&case.check).split_whitespace().collect() {
        return false;
    }
    fn pixel(value: &Value, f: &Fixture, rgba: [u8; 4]) -> bool {
        *value
            == json!({"width":f.width,"height":f.height,"expectedRgba":rgba,"firstPixel":rgba,"mismatchCount":0,"firstMismatch":null,"allPixelsMatch":true,"decodedChannels":f.width*f.height*4})
    }
    for (key, value) in object {
        let valid = match key.as_str() {
            "frame47" => pixel(value, f, f.blue),
            "frame48" => pixel(value, f, f.gold),
            "background" => pixel(value, f, f.background),
            "alpha" => pixel(value, f, f.alpha),
            "uncovered" => pixel(value, f, [0, 0, 0, 0]),
            "normalizedRate" => *value == json!({"numerator":30000,"denominator":1001}),
            "toolNames" => {
                *value
                    == json!([
                        "artifact.verify",
                        "engine.capabilities",
                        "frame.render",
                        "project.commit",
                        "project.create",
                        "project.inspect"
                    ])
            }
            "implementedFeatureIds" => {
                *value
                    == json!([
                        "CORE-01", "CORE-02", "CORE-03", "CORE-04", "CORE-05", "CORE-06",
                        "CORE-07", "CORE-08"
                    ])
            }
            "checkpoints" => {
                let expected=["after-pending","during-file-write","after-file-flush","after-promotion","after-receipt-commit"].map(|hook|json!({"hook":hook,"checkpoint":true,"timeoutExit":1,"timeoutError":"process_timeout","bounded":true,"retryExit":0,"pixels":{"width":f.width,"height":f.height,"expectedRgba":f.background,"firstPixel":f.background,"mismatchCount":0,"firstMismatch":null,"allPixelsMatch":true,"decodedChannels":f.width*f.height*4},"replayExit":0,"replayed":true,"sameReceipt":true,"revisionBinding":true,"intentBinding":true,"exactBytesMatchUnpaused":true,"receiptBindings":{"projectId":"project","revision":1,"frame":0,"intentId":hook,"snapshotHashMatches":true,"binaryHashMatches":true,"rendererVersion":"native-rgba-png/0.1.0","artifactIdMatches":true,"generatedPathMatches":true,"measuredHashMatches":true,"measuredLengthMatches":true,"width":f.width,"height":f.height,"format":"png-rgba8"}}));
                *value == json!(expected)
            }
            "error" => {
                *value
                    == if case.case_id == "CORE-03-B" {
                        json!("intent_conflict")
                    } else {
                        json!("invalid_input")
                    }
            }
            "unknownError" => *value == "unknown_tool",
            "futureError" => *value == "unsupported_capability",
            "verifyError" | "replayError" => *value == "artifact_integrity_mismatch",
            "unknownFieldError" | "zeroError" | "boundsError" | "duplicateError"
            | "malformedError" => *value == "invalid_input",
            "blockedError" | "timeoutError" => *value == "process_timeout",
            "requestId" | "timeoutRequestId" => *value == "intent-scenario-request",
            "implemented" => *value == 8,
            "planned" => *value == 73,
            "largeClips" => *value == 4000,
            "frame" => *value == 0,
            "revision" | "returnedRevision" => *value == 1,
            "latestRevision" | "retryRevision" => *value == 2,
            "blockedExit" | "timeoutExit" => *value == 1,
            "unknownExit" | "futureExit" | "unknownFieldExit" | "zeroExit" | "boundsExit"
            | "verifyExit" | "duplicateExit" | "malformedExit" => *value == 2,
            "replayExit" => *value == if case.case_id == "CORE-06-B" { 2 } else { 0 },
            "exit" => {
                *value
                    == if ["CORE-03-B", "CORE-04-B"].contains(&case.case_id.as_str()) {
                        2
                    } else {
                        0
                    }
            }
            "createExit" | "firstCommitExit" | "secondCommitExit" | "originalExit"
            | "equivalentExit" | "commitExit" | "validExit" | "progressExit" | "retryExit"
            | "largeExit" => *value == 0,
            _ => *value == true,
        };
        if !valid {
            return false;
        }
    }
    true
}
pub fn validate(contracts: &IntentContracts, core_bytes: &[u8]) -> io::Result<()> {
    if contracts.version != 1 || contracts.core_document_sha256 != evidence::sha(core_bytes) {
        return Err(io::Error::other(
            "CORE document binding changed; review contract before updating its hash",
        ));
    }
    let f = &contracts.fixture;
    if (f.duration_frames, f.frame_rate, f.width, f.height) != (96, 24, 64, 64)
        || f.background != [12, 25, 48, 255]
        || f.blue != [0, 64, 255, 255]
        || f.gold != [255, 192, 0, 255]
        || f.alpha != [12, 25, 48, 160]
    {
        return Err(io::Error::other(
            "Independent creator fixture differs from fixed CORE oracle",
        ));
    }
    let mut observed = BTreeSet::new();
    if contracts.features.len() != 8 {
        return Err(io::Error::other("Exactly eight CORE contracts required"));
    }
    for (i, feature) in contracts.features.iter().enumerate() {
        if feature.feature_id != format!("CORE-{:02}", i + 1)
            || feature.non_goals.is_empty()
            || feature.non_goals.iter().any(|s| s.trim().is_empty())
            || feature.review_requirements != ["oracle-adequacy-required-unreviewed"]
        {
            return Err(io::Error::other(
                "Invalid CORE source ID, non-goals, or manual review",
            ));
        }
        for case in &feature.cases {
            let Some((_, check, profile)) =
                CORE_CASES.iter().find(|(id, _, _)| *id == case.case_id)
            else {
                return Err(io::Error::other("Unregistered implemented case"));
            };
            if !case
                .case_id
                .starts_with(&format!("{}-", feature.feature_id))
                || case.check != *check
                || case.profile != *profile
                || case.expected.len() != 1
                || case.expected[0].id != *check
                || !expected_structure(case, f)
                || !observed.insert(case.case_id.clone())
            {
                return Err(io::Error::other(format!(
                    "Invalid case binding or expected outcome {}",
                    case.case_id
                )));
            }
        }
    }
    if observed != CORE_CASES.iter().map(|(id, _, _)| id.to_string()).collect() {
        return Err(io::Error::other(
            "All 16 registered implemented cases required",
        ));
    }
    Ok(())
}
pub fn compare(case: &mut CaseResult, actual: Value) {
    if case.expected.len() != 1 || case.status == State::PlannedUnobserved {
        case.status = State::Incomplete;
        case.incomplete_reason = Some("No registered expected outcome".into());
        return;
    }
    case.incomplete_reason = None;
    let matched = case.expected[0].value == actual;
    case.observed = vec![Observed {
        id: case.expected[0].id.clone(),
        actual,
        matched,
        mismatch: if matched {
            None
        } else {
            Some("Observed public CLI outcome differs from independent expected value".into())
        },
    }];
    case.status = if matched {
        State::Passed
    } else {
        State::Failed
    };
}
pub fn aggregate(cases: &[CaseResult]) -> State {
    if cases.iter().any(|c| c.status == State::Failed) {
        State::Failed
    } else if cases.len() != 2
        || cases.iter().any(|c| {
            c.status != State::Passed
                || c.observed.len() != c.expected.len()
                || c.evidence.is_empty()
                || c.binding.is_null()
        })
    {
        State::Incomplete
    } else {
        State::Passed
    }
}
pub fn audit_case(
    case: &mut CaseResult,
    directory: &Path,
    run_id: &str,
    source: &SourceIdentity,
    contract: &HashedFile,
    runtime: &[RuntimeIdentity],
    section_hash: &str,
) {
    if case.status != State::Passed && case.status != State::Failed {
        return;
    }
    let identity = runtime.iter().find(|r| Some(r.profile) == case.profile);
    let current = identity.is_some_and(|r| evidence::file(Path::new(&r.binary.path)).is_ok_and(|actual|actual == r.binary) && case.binding == json!({"runId":run_id,"sourceSha256":source.sha256,"contractSha256":contract.sha256,"featureSectionSha256":section_hash,"profile":r.profile,"binarySha256":r.binary.sha256,"schemaSha256":r.discovery["schemaSha256"]}));
    let files_current = !case.evidence.is_empty()
        && case.evidence.iter().all(|file| {
            let path = Path::new(&file.path);
            path.starts_with(directory)
                && path
                    .components()
                    .all(|c| !matches!(c, std::path::Component::ParentDir))
                && path
                    .ancestors()
                    .take_while(|p| *p != directory)
                    .all(|p| fs::symlink_metadata(p).is_ok_and(|m| !m.file_type().is_symlink()))
                && evidence::file(path).is_ok_and(|actual| actual == *file)
        });
    if !current || !files_current {
        case.status = State::Incomplete;
        case.incomplete_reason =
            Some("Missing, altered, previous-run, or mismatched identity evidence".into());
    }
}
fn complete_core(features: &[FeatureResult]) -> bool {
    let actual: Vec<_> = features
        .iter()
        .filter(|f| f.ledger_state == "implemented")
        .flat_map(|f| &f.cases)
        .collect();
    actual.len() == CORE_CASES.len()
        && CORE_CASES.iter().all(|(id, check, profile)| {
            actual
                .iter()
                .filter(|case| {
                    case.case_id == *id
                        && case.profile == Some(*profile)
                        && case.status == State::Passed
                        && case.expected.len() == 1
                        && case.expected[0].id == *check
                        && case.observed.len() == 1
                        && case.observed[0].id == *check
                        && case.observed[0].matched
                        && case.observed[0].actual == case.expected[0].value
                        && !case.evidence.is_empty()
                        && !case.binding.is_null()
                })
                .count()
                == 1
        })
        && features
            .iter()
            .filter(|f| f.ledger_state == "planned")
            .all(|f| {
                f.status == State::PlannedUnobserved
                    && f.cases.iter().all(|c| {
                        c.status == State::PlannedUnobserved
                            && c.observed.is_empty()
                            && c.evidence.is_empty()
                    })
            })
}
pub fn report(
    run_id: &str,
    mode: VerificationMode,
    source: &SourceIdentity,
    contract_file: Option<HashedFile>,
    features: Vec<FeatureResult>,
    issues: Vec<String>,
) -> IntentCoverageReport {
    let count = |state| features.iter().filter(|f| f.status == state).count();
    let architecture = matches!(mode, VerificationMode::Architecture);
    let passed_cases = features
        .iter()
        .flat_map(|f| &f.cases)
        .filter(|c| c.status == State::Passed)
        .count();
    let verdict = if !issues.is_empty() || count(State::Failed) > 0 {
        "failed"
    } else if architecture {
        "structure-only"
    } else if count(State::Passed) == 8
        && complete_core(&features)
        && count(State::PlannedUnobserved) == 73
    {
        "passed-implemented-scope"
    } else {
        "incomplete"
    };
    IntentCoverageReport {
        report_version: 1,
        run_id: run_id.into(),
        mode,
        source_sha256: source.sha256.clone(),
        contract_file,
        verdict: verdict.into(),
        counts: json!({"features":features.len(),"implemented":8,"planned":73,"passed":count(State::Passed),"failed":count(State::Failed),"incomplete":count(State::Incomplete),"notRun":count(State::NotRun),"plannedUnobserved":count(State::PlannedUnobserved),"passedCases":passed_cases}),
        contract_issues: issues,
        features,
        capability_promotion_performed: false,
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    fn root() -> &'static Path {
        Path::new(env!("CARGO_MANIFEST_DIR"))
            .parent()
            .unwrap()
            .parent()
            .unwrap()
    }
    #[test]
    fn missing_case_changed_document_and_forged_review_fail() {
        let bytes = fs::read(root().join("docs/features/intent-contracts.json")).unwrap();
        let doc = fs::read(root().join("docs/features/core.md")).unwrap();
        let mut c: IntentContracts = serde_json::from_slice(&bytes).unwrap();
        validate(&c, &doc).unwrap();
        c.features[0].cases.pop();
        assert!(validate(&c, &doc).is_err());
        let mut c: IntentContracts = serde_json::from_slice(&bytes).unwrap();
        c.features[0].review_requirements = vec!["accepted".into()];
        assert!(validate(&c, &doc).is_err());
        let c: IntentContracts = serde_json::from_slice(&bytes).unwrap();
        let mut changed = doc.clone();
        changed.extend_from_slice(b"changed");
        assert!(validate(&c, &changed).is_err());
    }
    #[test]
    fn wrong_success_and_missing_observation_cannot_pass() {
        let mut c = CaseResult {
            case_id: "CORE-03-A".into(),
            profile: Some(RuntimeProfile::Default),
            status: State::NotRun,
            expected: vec![Expected {
                id: "old-replay".into(),
                value: json!({"returnedRevision":1,"latestRevision":2,"replayed":true}),
            }],
            observed: vec![],
            evidence: vec![],
            binding: Value::Null,
            incomplete_reason: None,
        };
        compare(
            &mut c,
            json!({"returnedRevision":2,"latestRevision":2,"replayed":true}),
        );
        assert_eq!(c.status, State::Failed);
        compare(
            &mut c,
            json!({"returnedRevision":1,"latestRevision":2,"replayed":true}),
        );
        assert_eq!(aggregate(&[c]), State::Incomplete);
        assert_eq!(aggregate(&[]), State::Incomplete);
    }
    #[test]
    fn altered_response_and_previous_run_evidence_are_incomplete() {
        let directory =
            std::env::temp_dir().join(format!("intent-audit-{}", crate::process::now()));
        fs::create_dir(&directory).unwrap();
        let path = directory.join("response.json");
        fs::write(&path, br#"{"status":"success","revision":1}"#).unwrap();
        let source = SourceIdentity {
            scope: "fixture".into(),
            files: vec![],
            sha256: "source".into(),
        };
        let contract = HashedFile {
            path: "contract".into(),
            bytes: 1,
            sha256: "contract".into(),
        };
        let binary_path = directory.join("binary");
        fs::write(&binary_path, b"current executable fixture").unwrap();
        let runtime = vec![RuntimeIdentity {
            profile: RuntimeProfile::Default,
            binary: evidence::file(&binary_path).unwrap(),
            discovery: json!({"schemaSha256":"schema"}),
        }];
        let binding = json!({"runId":"current","sourceSha256":"source","contractSha256":"contract","featureSectionSha256":"section","profile":"default","binarySha256":runtime[0].binary.sha256,"schemaSha256":"schema"});
        let mut case = CaseResult {
            case_id: "CORE-03-A".into(),
            profile: Some(RuntimeProfile::Default),
            status: State::Passed,
            expected: vec![],
            observed: vec![],
            evidence: vec![evidence::file(&path).unwrap()],
            binding: binding.clone(),
            incomplete_reason: None,
        };
        audit_case(
            &mut case, &directory, "current", &source, &contract, &runtime, "section",
        );
        assert_eq!(case.status, State::Passed);
        fs::write(&path, br#"{"status":"success","revision":2}"#).unwrap();
        audit_case(
            &mut case, &directory, "current", &source, &contract, &runtime, "section",
        );
        assert_eq!(case.status, State::Incomplete);
        case.status = State::Passed;
        case.evidence = vec![evidence::file(&path).unwrap()];
        case.binding["runId"] = "previous".into();
        audit_case(
            &mut case, &directory, "current", &source, &contract, &runtime, "section",
        );
        assert_eq!(case.status, State::Incomplete);
    }
    #[test]
    fn exact_registry_and_expected_fields_are_required() {
        let bytes = fs::read(root().join("docs/features/intent-contracts.json")).unwrap();
        let doc = fs::read(root().join("docs/features/core.md")).unwrap();
        let mut contracts: IntentContracts = serde_json::from_slice(&bytes).unwrap();
        contracts.features[0].cases[0].expected[0].value["inventedAssertion"] = true.into();
        assert!(validate(&contracts, &doc).is_err());
        let ledger = evidence::json(&root().join("capabilities.json")).unwrap();
        let (_, mut rows) = load(root(), &ledger).unwrap();
        rows[0].cases[1].case_id = rows[0].cases[0].case_id.clone();
        assert!(!complete_core(&rows));
        assert!(!complete_core(&[]));
    }
    #[test]
    fn planned_falsely_observed_is_rejected() {
        let ledger = evidence::json(&root().join("capabilities.json")).unwrap();
        let (_, mut rows) = load(root(), &ledger).unwrap();
        compare(&mut rows[8].cases[0], json!({"passed":true}));
        assert_eq!(rows[8].cases[0].status, State::Incomplete);
        let mut ledger = ledger;
        ledger["capabilities"][8]["state"] = "implemented".into();
        assert!(load(root(), &ledger).is_err());
    }
}
