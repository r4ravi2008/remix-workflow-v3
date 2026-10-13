# Candidate B: document-bound CLI intent scenarios

## Result

Add one development-only intent check to `native-editor-check full`.
It runs fixed CORE scenarios through fresh public CLI binaries.
It compares actual results with documented observable outcomes.

`architecture` validates contract structure and document bindings.
It does not execute scenarios or claim behavior proof.

This design changes no runtime command, schema, crate ownership, or capability state.
It adds no FFmpeg, Lua, Effect, UI, or hosted dependency.

## Caller usage

The public development commands stay unchanged.

```sh
cd apps/release-kit-studio/native-editor
cargo build --locked -p editor-devcheck --bin native-editor-check
target/debug/native-editor-check architecture
target/debug/native-editor-check full
```

`architecture` can pass when each intent contract is complete and current.
Its summary must still state that the check did not observe behavior.

`full` must build fresh default and `test-hooks` CLI binaries.
It must then run the implemented CORE scenarios against those binaries.

Each run writes:

```text
.runs/verification/<run-id>/intent-coverage.json
.runs/verification/<run-id>/intent/<case-id>/request-*.json
.runs/verification/<run-id>/intent/<case-id>/response-*.json
.runs/verification/<run-id>/intent/<case-id>/process-*.json
```

The top-level summary keeps the current shape.
Its `reportPath` points to the full development report.
That report links and hashes `intent-coverage.json`.

## Problem

The current document check proves that 81 feature sections exist.
It checks headings, names, implementation pieces, and named verification cases.

The current full check proves compilation, tests, runtime identity, and bounded P0 behavior.
Its evidence audit trusts acceptance-test directories whose names match ledger case IDs.

Neither check starts from a feature's stated purpose and creator scenario.
Neither check reports expected and observed outcomes together.

An exit code of zero is insufficient evidence.
A mapped test name is also insufficient evidence.

The new check must answer a narrower question:

> Did the current public CLI produce the documented observable outcomes for every implemented CORE intent case?

The answer covers bounded P0 behavior only.
It does not prove full product intent, creative quality, or future capabilities.

## Contract source

Add one file:

```text
apps/release-kit-studio/native-editor/docs/features/intent-contracts.json
```

This file contains one contract for each current capability ID.
It does not replace the seven feature documents.

Each contract names its feature section and binds its exact normalized bytes.
`docs/features/check.mjs` already splits documents by feature heading.
This candidate recommends that the checker supply the same normalized section bytes for hash calculation.

The source binding prevents silent drift between prose and executable cases.
A changed feature section invalidates its intent contract until a reviewer completes the review of the change.

```rust
pub struct FeatureIntentContract {
    pub contract_version: u16,
    pub feature_id: FeatureId,
    pub source: FeatureSectionRef,
    pub purpose: String,
    pub scenario: String,
    pub given: NonEmpty<String>,
    pub action: IntentAction,
    pub observable_expected_outcomes: NonEmpty<ExpectedOutcome>,
    pub non_goals: Vec<String>,
    pub review_requirements: NonEmpty<ReviewRequirement>,
    pub named_cases: NonEmpty<IntentCaseContract>,
}

pub struct FeatureSectionRef {
    pub path: String,
    pub heading: String,
    pub section_sha256: Sha256,
}

pub struct IntentAction {
    pub command: String,
    pub execution: IntentExecution,
}

pub enum IntentExecution {
    Implemented,
    Planned,
}

pub struct ExpectedOutcome {
    pub id: OutcomeId,
    pub statement: String,
    pub observation_kind: ObservationKind,
}

pub enum ObservationKind {
    JsonValue,
    ProcessExit,
    FileBytes,
    PngPixels,
    StateSnapshot,
    NoMutation,
}

pub struct ReviewRequirement {
    pub kind: ReviewKind,
    pub statement: String,
}

pub enum ReviewKind {
    OracleAdequacy,
    TechnicalArtifact,
    Playback,
    Listening,
    Creative,
}

pub struct IntentCaseContract {
    pub case_id: IntentCaseId,
    pub title: String,
    pub profiles: NonEmpty<RuntimeProfile>,
    pub expected_outcome_ids: NonEmpty<OutcomeId>,
    pub supporting_acceptance_case_ids: Vec<String>,
}
```

`FeatureId`, `IntentCaseId`, `OutcomeId`, and `Sha256` are validated newtypes.
They serialize as strings.

The contract uses current document case IDs such as `CORE-03-A`.
Current IDs such as `P0-REPLAY` remain support acceptance cases.
Support cases cannot satisfy an intent case by name alone.

The contract fields have distinct purposes:

| Field | Meaning |
| --- | --- |
| `purpose` | The creator-facing result from `What it does`. |
| `scenario` | The concrete creator story from `Scenario`. |
| `given` | Preconditions and fixtures required before the action. |
| `action` | The public CLI boundary exercised or planned. |
| `observableExpectedOutcomes` | Results measurable outside runtime internals. |
| `nonGoals` | Claims the case must not imply. |
| `reviewRequirements` | Human or technical review still required. |

The structured text can quote or sharpen the current prose.
The feature-section hash makes that judgment reviewable after document changes.

## Purpose is not `intentId`

Feature intent describes why a capability exists and what a creator observes.
It lives in `intent-contracts.json` and the linked feature document.

Runtime `intentId` identifies one retryable command in one project.
It participates in replay and conflict resolution under CORE-03.

The evaluator must use fresh runtime `intentId` values inside scenarios.
It must not treat those values as feature-intent identifiers.

## Small implementation shape

Use the current `editor-devcheck` modules.
Do not add a general evaluator framework or assertion language.

### `docs/features/check.mjs`

Extend the current structure check to load `intent-contracts.json`.
Validate these rules:

1. Exactly 81 contracts exist.
2. Every ledger feature has exactly one contract.
3. Every contract points to the ledger's `behaviorContract` file.
4. Every section heading and section hash match current document bytes.
5. Every required field is nonempty.
6. Every document verification case appears in `namedCases`.
7. Every contract action command matches the ledger command.
8. The eight CORE contracts use `implemented` execution.
9. The remaining 73 contracts use `planned` execution.
10. Planned contracts contain no executable probe binding.

The current `feature-document-coverage` receipt can include the intent file hash.
Its scope remains document structure only.

### `crates/editor-devcheck/src/model.rs`

Add two check IDs.

```rust
pub enum CheckId {
    // existing values
    IntentContracts,
    IntentScenarios,
}
```

`IntentContracts` belongs in both plans.
`IntentScenarios` belongs only in `VerificationMode::Full`.

Add report types without changes to runtime types.

```rust
pub struct IntentCoverageReport {
    pub report_version: u16,
    pub run_id: String,
    pub mode: VerificationMode,
    pub generated_at: u128,
    pub contract_file: HashedFile,
    pub source_sha256: String,
    pub verdict: IntentCoverageVerdict,
    pub counts: IntentCoverageCounts,
    pub features: Vec<FeatureIntentResult>,
    pub capability_promotion_performed: bool,
}

pub struct IntentCoverageCounts {
    pub contracted: u16,
    pub implemented: u16,
    pub planned: u16,
    pub observed_pass: u16,
    pub observed_fail: u16,
    pub missing: u16,
    pub stale: u16,
}

pub enum IntentCoverageVerdict {
    StructureOnly,
    PassedImplementedScope,
    Failed,
    Incomplete,
}

pub struct FeatureIntentResult {
    pub feature_id: String,
    pub ledger_state: LedgerState,
    pub source: FeatureSectionRef,
    pub contract_status: ContractStatus,
    pub behavior_status: BehaviorStatus,
    pub cases: Vec<IntentCaseResult>,
    pub review: FeatureReviewState,
}

pub enum BehaviorStatus {
    ObservedPass,
    ObservedFail,
    Missing,
    Stale,
    NotRunArchitecture,
    PlannedUnobserved,
}

pub struct IntentCaseResult {
    pub case_id: String,
    pub profiles: Vec<RuntimeProfile>,
    pub expected: Vec<ExpectedOutcome>,
    pub observed: Vec<ObservedOutcome>,
    pub status: CaseStatus,
    pub evidence: Vec<HashedFile>,
}

pub struct ObservedOutcome {
    pub outcome_id: String,
    pub actual: serde_json::Value,
    pub matched: bool,
    pub evidence_paths: NonEmpty<String>,
}

pub struct FeatureReviewState {
    pub oracle_adequacy: ManualReviewState,
    pub creative: ManualReviewState,
}

pub enum ManualReviewState {
    NotApplicable,
    RequiredUnreviewed,
    AcceptedOutsideVerifier,
    RejectedOutsideVerifier,
}
```

The verifier does not write either `AcceptedOutsideVerifier` value itself.
Those variants reserve report vocabulary for a future authenticated review record.

Current CORE reports use `RequiredUnreviewed` for oracle adequacy.
They use `NotApplicable` for creative review.

Planned visual, audio, and delivery features retain their declared review needs.
Their report state remains `PlannedUnobserved`.

### `crates/editor-devcheck/src/run.rs`

Add one private method:

```rust
fn run_intent_scenarios(
    &mut self,
    record: &mut CheckRecord,
    contracts: &IntentContracts,
    runtime: &[RuntimeIdentity],
) -> io::Result<Vec<IntentCaseResult>>;
```

The method runs after both fresh binaries exist.
It uses the current `ProcessRunner` through `Verifier`.

Only `src/process.rs` owns subprocess execution.
No scenario code calls `std::process`.

Add a narrow invocation result for expected negative exits.

```rust
struct CliObservation {
    profile: RuntimeProfile,
    process: ProcessRecord,
    stdout_json: Option<serde_json::Value>,
    request: Option<HashedFile>,
    response: HashedFile,
}
```

The current `command` helper assumes exit zero.
The intent method needs a separate helper that records raw process outcomes.
Case-specific code decides whether a nonzero exit is expected.

The method contains a direct match over the 16 CORE document cases.
It does not interpret an assertion DSL.
An unknown implemented case produces an incomplete result.

### `crates/editor-devcheck/src/evidence.rs`

Reuse `sha`, `file`, `write_new`, `canonical`, and `png_pixels`.

1. Add the contract loader.
2. Add section-hash validation.
3. Add the report writer.

This candidate recommends that case assertions compare only these external observations:

- response JSON.
- process exit and stderr.
- independently read state through `project.inspect`.
- independently hashed files.
- independently decoded PNG pixels.
- before and after state equality.

Do not inspect private Rust values or call `editor-core` functions.

### `crates/editor-devcheck/src/main.rs`

Keep `architecture|full` as the only modes.
The intent work does not earn another public mode.

## Executable CORE cases

The first implementation covers all 16 cases named in `core.md`.
Several cases can share one fresh scenario state.
Each case still receives separate expected and observed outcomes.

| Case | Profile | Required observation |
| --- | --- | --- |
| `CORE-01-A` | default | `tools` exposes exactly six tools, eight CORE IDs, measured binary hash, and no state directory. |
| `CORE-01-B` | default | Every `schema` response reconstructs the discovery hash. Unknown input fails before storage. |
| `CORE-02-A` | default | Fresh CLI processes create, commit, and read both immutable revisions with independently recomputed hashes. |
| `CORE-02-B` | default | Equivalent rates replay. Zero denominator exits with `invalid_input` and creates no project. |
| `CORE-03-A` | default | An old identical commit returns its original result with `replayed: true`. Current revision remains two. |
| `CORE-03-B` | default | Changed content under the old intent exits two with `intent_conflict`. Inspection is unchanged. |
| `CORE-04-A` | default | Adjacent clips persist at exact intervals. Decoded frames 47 and 48 have expected colors. |
| `CORE-04-B` | default | Mixed valid and invalid edits fail atomically. Before and after snapshots and hashes match. |
| `CORE-05-A` | default | Every decoded RGBA channel matches the fixture. Uncovered pixels are transparent. |
| `CORE-05-B` | test-hooks | A timed-out `during-file-write` call recovers under the same runtime intent. Bounds fail without completed output. |
| `CORE-06-A` | default | Fresh verification measurements match independent file hash, length, dimensions, and receipt bindings. |
| `CORE-06-B` | default | A flipped byte causes verify and replay failure. The changed bytes remain unchanged. |
| `CORE-07-A` | default | Valid file calls return one matching JSON response. Malformed and duplicate-key input exits two. |
| `CORE-07-B` | test-hooks | Runtime deadline returns one complete timeout response. Same intent later completes without duplication. |
| `CORE-08-A` | default | `progress` reports eight implemented and 73 planned features with empty promotion evidence. |
| `CORE-08-B` | default | Forged state files cannot change progress or make a planned command callable. |

The hook cases invoke the test-hook binary through its normal public CLI.
Only the environment activates a development checkpoint.

Example hook sequence:

```text
native-editor call frame.render <request> --deadline-ms 100 --state <case-state>
NATIVE_EDITOR_TEST_HOOK=during-file-write
NATIVE_EDITOR_TEST_READY=<case-evidence>/ready
```

The first response must exit one with `process_timeout`.
The evaluator then invokes the same request without the hook.
The retry must produce one correct artifact.
The next identical retry must report `replayed: true`.

## Freshness and pass rules

Only evidence created in the current verifier run can satisfy a case.
The evaluator does not import a previous `.runs/verification` directory.

Each observed result binds these values:

- current run ID.
- source inventory hash.
- feature-section hash.
- intent-contract file hash.
- runtime profile.
- runtime binary hash.
- runtime schema hash.
- request and response hashes.
- process record hash.

A mismatch produces `Stale`.
A missing process, request, response, or required measurement produces `Missing`.
An expected-outcome mismatch produces `ObservedFail`.

`PassedImplementedScope` requires all these conditions:

1. All 81 contracts are current and structurally valid.
2. All 16 implemented CORE cases ran in their required profiles.
3. Each expected outcome has a current-run observation that matches.
4. No implemented result is missing, stale, failed, or unreviewable by evidence.
5. The workspace source hash is unchanged at run completion.

A map from a document to a test cannot produce `ObservedPass`.
A support test cannot produce `ObservedPass`.
A subprocess exit of zero cannot produce `ObservedPass` by itself.

Architecture mode writes `StructureOnly`.
Its eight CORE features use `NotRunArchitecture`.
Its 73 future features use `PlannedUnobserved`.

Full mode can write `PassedImplementedScope`.
That verdict covers the eight implemented CORE feature intents only.
It does not describe the 73 planned features as passed.

The parent `VerificationReport.capability_promotion_performed` remains `false`.
The intent report carries the same field with `false`.

## Human-readable report

Write pretty JSON with features ordered by `capabilities.json`.
Order cases by their appearance in each feature document.

Example excerpt:

```json
{
  "reportVersion": 1,
  "mode": "full",
  "verdict": "passed-implemented-scope",
  "counts": {
    "contracted": 81,
    "implemented": 8,
    "planned": 73,
    "observedPass": 8,
    "observedFail": 0,
    "missing": 0,
    "stale": 0
  },
  "features": [
    {
      "featureId": "CORE-03",
      "ledgerState": "implemented",
      "contractStatus": "current",
      "behaviorStatus": "observed-pass",
      "cases": [
        {
          "caseId": "CORE-03-A",
          "status": "observed-pass",
          "expected": [
            {
              "id": "old-result-replayed",
              "statement": "The original result returns and the current revision remains two."
            }
          ],
          "observed": [
            {
              "outcomeId": "old-result-replayed",
              "actual": {
                "replayed": true,
                "returnedRevision": 1,
                "currentRevision": 2
              },
              "matched": true,
              "evidencePaths": [
                "intent/CORE-03-A/response-3.json",
                "intent/CORE-03-A/response-4.json"
              ]
            }
          ]
        }
      ],
      "review": {
        "oracleAdequacy": "required-unreviewed",
        "creative": "not-applicable"
      }
    },
    {
      "featureId": "MEDIA-01",
      "ledgerState": "planned",
      "contractStatus": "current",
      "behaviorStatus": "planned-unobserved",
      "cases": [],
      "review": {
        "oracleAdequacy": "required-unreviewed",
        "creative": "required-unreviewed"
      }
    }
  ],
  "capabilityPromotionPerformed": false
}
```

`oracleAdequacy` remains visible because source hashes prove alignment, not sufficiency.
A human must still judge whether each oracle captures the stated creator outcome.

Creative review remains separate from automated observation.
No technical case can set creative review to accepted.

## Negative probes

The implementation must include verifier regressions for these failures:

1. Change a feature section. Keep its section hash unchanged.

   Architecture must fail `IntentContracts`.
2. Remove one implemented named case.

   Full must become incomplete, not passed.
3. Replace an expected response with different bytes after execution.

   The case must become stale or failed through hash mismatch.
4. Return exit zero with a wrong JSON value.

   The case must fail its observable outcome.
5. Return the expected error with a change to project state.

   The case must fail its no-mutation outcome.
6. Point evidence at a previous run directory.

   The case must become stale.
7. Mark a planned feature as observed without a compiled implementation.

   Contract validation must fail.
8. Add a new implemented contract case without evaluator code.

   Full must report the case missing.
9. Forge a manual or creative acceptance value.

   The development verifier must reject the untrusted value.

These tests belong in `editor-devcheck` unit tests.
The actual scenario outcomes still require fresh public CLI processes.

## Extension procedure

To implement another feature family, use this procedure.

1. Update the current feature document with the exact purpose and scenario.
2. Name observable verification cases in that feature's `Verification` section.
3. Update its structured contract and current section hash.
4. Change the ledger state only when the runtime implementation exists.
5. Add direct case logic in `run_intent_scenarios`.
6. Use public CLI inputs and external observations only.
7. Add at least one failure or no-mutation probe.
8. Declare playback, listening, creative, or oracle review requirements explicitly.
9. Run `architecture` .
   Inspect the structure-only report.
10. Run `full` .
    Compare expected and observed outcomes.

If the case needs a new assertion kind, add one concrete Rust comparison.
Do not create a general expression language.

If the case needs a runtime capability, implement that capability first.
The verifier must not add fallback behavior.

## Tradeoffs accepted

- We accept a small amount of duplicated contract prose for explicit, reviewable intent fields.
- We accept direct Rust case code for strong types and simple failure diagnosis.
- We accept manual case additions because the implemented interface currently covers eight families.
- We accept incomplete oracle review because automated source binding cannot prove oracle adequacy.
- We accept planned features without runtime observations to avoid false verification claims.

## Alternatives considered

If we select a general JSON scenario DSL, we reduce Rust edits.
The DSL adds an interpreter, assertion language, and another public contract.
That interface is too large for eight implemented feature families.

If we reuse acceptance-test pass records, the implementation is smaller.
That alternative keeps the current gap between creator intent and observed outcome.

If we parse intent from prose alone, we avoid a sidecar.
That alternative makes `given`, non-goals, and review requirements heuristic and unstable.

## Review boundaries

This design can prove current-build P0 observations against current documented cases.
It cannot prove that the cases fully express human intent.

The report must keep these states separate:

- contract structure.
- source freshness.
- automated observable outcomes.
- oracle-adequacy review.
- playback and listening review.
- creative acceptance.
- capability promotion.

No current step performs trusted capability promotion.

## First implementation step

Define `intent-contracts.json` for CORE-01 through CORE-08 and one planned feature.
Add structure tests that fail before you complete the 81-feature contract migration.
