# Candidate A. Feature intent with observed CLI outcomes

This document records a design candidate. The candidate proposes no changes to runtime behavior, capability state, or acceptance promotion.
The configured GPT agent produced this candidate. It does not claim Cursor, Claude, or Grok review.

## Caller experience

The creator sees what each feature promises and which observable outcomes the current build demonstrates.
The maintainer extends the current CLI acceptance suite. The maintainer does not operate another scenario runner.

The current commands remain the entry points, from `apps/release-kit-studio/native-editor`.

```sh
	cargo build --locked -p editor-devcheck --bin native-editor-check
	target/debug/native-editor-check architecture
	target/debug/native-editor-check full
```

Architecture mode produces structural intent coverage. Every runtime case says `not-run`.
Full mode runs the current default and test-hook CLI tests and audits their saved observations.
Both modes save `.runs/verification/<run-id>/intent-coverage.json` beside `report.json`.
The stdout summary adds `intentCoveragePath` and `intentSummary`.

An illustrative full summary reads as follows. These numbers describe the proposed report. They are not measured results.

```json
{
  "implementedFeatures": 8,
  "plannedFeatures": 73,
  "implementedIntent": {"measured": 8, "failed": 0, "incomplete": 0},
  "plannedIntent": {"notImplemented": 73},
  "claim": "Declared observable P0 outcomes only",
  "capabilityPromotionPerformed": false
}
```

The report includes purpose, scenario, expected outcome, actual observation, and evidence paths for each case.
It reports required human review separately. A measured outcome cannot imply creative approval.

## Grounding and scope

Feature intent means the creator's purpose and the result a feature promises.
The runtime `intentId` identifies a retryable command in a project.
CORE-03 tests that retry mechanism. The new contract contains no field named `intentId` for feature purpose.

The current flow is `VerificationMode::plan` → `Verifier::run` → `ProcessRunner` → Cargo acceptance tests.
`Run::raw` saves requests, responses, and exits under `tests/<profile>/<case>-<pid>-<sequence>`.
`evidence::suite` audits their hashes, discovery identities, and named P0 coverage.

It does not re-evaluate feature outcomes. A valid response with incorrect pixels can satisfy its current checks of evidence records.
`evidence::demo` independently checks demo pixels, but that one fixture does not cover all creator scenarios.
`docs/features/check.mjs` checks sections, names, links, and case presence. Its receipt explicitly limits assurance to document structure.

This design adds one declarative contract and one outcome auditor inside `editor-devcheck`.
Current acceptance tests continue to execute actual default and hook CLI binaries.
`process.rs` remains the development crate's only process owner. The outcome auditor cannot spawn processes.
Runtime crates do not import the contract, verifier, or test helpers.
FFmpeg, Lua, Effect, a new runtime, and capability promotion remain outside this change.

## Contract shape

Add `docs/features/intent.json` with one entry for each of the 81 feature IDs.
The contract states purpose, scenario, preconditions, action, observable outcomes, non-goals, and review requirements.
It links the current human-readable contract. It does not replace the feature guide.

The author must use judgment to write these statements. Structural checks cannot prove that a purpose accurately represents a creator's needs.

These proposed types live privately in `crates/editor-devcheck/src/intent.rs`.
All contract and observation structs use strict Serde deserialization with `deny_unknown_fields`.
ID constructors and relative-path constructors validate syntax, uniqueness, scope, and traversal before use.

```rust
	struct IntentDocument {
		version: u16,
		features: Vec<FeatureIntent>,
	}
	struct FeatureIntent {
		feature_id: FeatureId,
		behavior_contract: RunRelativePath,
		purpose: String,
		scenario: String,
		non_goals: Vec<String>,
		review_requirements: Vec<ReviewRequirement>,
		cases: Vec<IntentCase>,
	}
	struct IntentCase {
		case_id: CaseId,
		given: Vec<String>,
		action: String,
		outcomes: NonEmpty<ExpectedOutcome>,
		binding: CaseBinding,
	}
	struct ExpectedOutcome {
		id: OutcomeId,
		description: String,
		check: Option<OutcomeCheck>,
	}
	#[serde(tag = "kind", rename_all = "kebab-case")]
	enum CaseBinding {
		Executable { test_name: String, evidence_case: String,
			required_profiles: NonEmpty<RuntimeProfile> },
		Planned,
	}
	struct ReviewRequirement {
		kind: ReviewKind,
		criteria: String,
	}
	enum ReviewKind { PurposeAndContract, Playback, Listening, CreativeApproval }
	struct JsonObservation {
		label: ObservationLabel,
		pointer: JsonPointer,
	}
	#[serde(tag = "kind", rename_all = "kebab-case")]
	enum OutcomeCheck {
		JsonEquals { actual: JsonObservation, expected: serde_json::Value },
		JsonEqualsObservation { left: JsonObservation, right: JsonObservation },
		SnapshotHash { snapshot: JsonObservation, hash: JsonObservation },
		SchemaHash { schemas: ObservationLabel, discovery: ObservationLabel },
		PngSolid { artifact: ObservationLabel, width: u32, height: u32, rgba: [u8; 4] },
		FileHashMatches { artifact: ObservationLabel, hash: JsonObservation },
		FileUnchanged { before: ObservationLabel, after: ObservationLabel },
		PathAbsent { observation: ObservationLabel },
		ProcessResponse { observation: ObservationLabel, exit: i32,
			request_id: Option<String>, empty_stderr: bool },
		ElapsedBelow { observation: ObservationLabel, limit_ms: u64 },
		CapabilityStates { progress: ObservationLabel, discovery: ObservationLabel },
	}
```

`RunRelativePath` means a validated relative path, relative to the root that owns the path.
The behavior contract uses the native-editor root. Evidence paths use the case directory.

`OutcomeCheck` is a bounded comparison vocabulary, not a scripting language.
The contract has no expressions, regular-expression assertions, shell commands, or arbitrary evaluator plugins.
Each implemented case requires checks for every expected outcome. Planned cases have no executable checks.
Architecture validation rejects mismatched binding kinds and capability states.

For example, CORE-05-A describes the creator's background preview.
Its purpose is to inspect an exact project revision before the creator adds footage.
Its given state is revision one, a 64-by-64 canvas, and a clip with `[12,25,48,255]`.
Its action is `frame.render` for frame zero.

The PNG outcome uses `PngSolid` with those literal dimensions and channels.
The expected RGBA value comes from the contract, never from the produced PNG or receipt.
The case also compares JSON and hashes to check the saved request, revision, and artifact bindings.
Movie playback, captions, motion review, and creative approval are explicit non-goals.

Simple constants and pairwise JSON comparisons cover most outcomes.
`SnapshotHash`, `SchemaHash`, and `PngSolid` reuse current independent canonicalization and PNG helpers.
`CapabilityStates` compares all unique ledger IDs with discovery and requires empty evidence and unchanged implemented/planned states.
It does not trust a reported family count alone.

## Observation shape and proof rules

Extend the private acceptance-test `Run` helper with labeled observation capture.
Store `observations.json` after each capture. Use exclusive creation for each captured file.
Each observation records exact file references and hashes, not an authored `passed: true` assertion.

```rust
	struct CaseObservations {
		version: u16,
		run_id: String,
		profile: RuntimeProfile,
		test_name: String,
		evidence_case: String,
		binary_sha256: String,
		schema_sha256: String,
		observations: BTreeMap<ObservationLabel, Observation>,
	}
	#[serde(tag = "kind", rename_all = "kebab-case")]
	enum Observation {
		Process { request: Option<HashedFile>, stdout: HashedFile,
			stderr: HashedFile, argv: Vec<String>, exit: ProcessExit,
			duration_ms: u128 },
		File { file: HashedFile },
		AbsentPath { path: RunRelativePath },
	}
	struct CaseCompletion {
		run_id: String,
		profile: RuntimeProfile,
		test_name: String,
		evidence_case: String,
		observations_sha256: String,
	}
```

Pass the current run ID and profile through new `NATIVE_EDITOR_VERIFICATION_RUN_ID` and `NATIVE_EDITOR_VERIFICATION_PROFILE` overrides.
Keep `NATIVE_EDITOR_EVIDENCE_DIR` and isolated Cargo targets unchanged.

Tests write `completion.json` only after their assertions pass.
Capture labeled evidence before each assertion. A failed pixel assertion therefore preserves the incorrect PNG.
The verifier audits available observations even when Cargo reports failure.
There is no second execution of successful acceptance cases.

Capture direct `tools`, `schema`, `progress`, slow-reader, and hook-child commands as well as `Run::raw` calls.
Expected hook termination records a signal, saved request, checkpoint, and later recovery observations.
A deliberate external kill does not require a JSON response from the killed child.
`ProcessResponse` does require one complete JSON document for commands expected to return a response.

The auditor checks these conditions before it can report a measured case.

1. Match the contract's exact case, test name, required profile, and labels.
2. Require successful suite execution and a current-run completion record for that case.
3. Match the measured profile binary and schema with discovery and every case identity.
4. Make sure that all evidence paths remain inside the fresh run. Reject unexpected symlinks.
5. Recompute referenced file hashes and parse exact saved requests and responses.
6. Evaluate every declared outcome against those bytes or current filesystem observations.
7. Require unchanged source identity. This identity includes the contract and acceptance test sources.

Request checks establish given state and action. Outcome checks establish observable results.
For negative cases, check both the error response and the unchanged project or artifact.
A rejected edit alone cannot prove rollback.
For expected mutations such as file tampering, save immutable byte copies before later operations. Save both the original and changed bytes.

Only `AbsentPath` observes nonexistence. The auditor does not confuse missing required evidence with expected absence.
Each absent path must come from a validated case-owned target, not an arbitrary author-selected path.

This is local development evidence. Self-hashed files do not authenticate reviewers or defend against a malicious checkout.

## Initial case bindings

Use the current `CORE-xx-A/B` documentation IDs as intent case IDs.
Keep P0 test names as execution bindings. Do not rename or change capability-ledger acceptance IDs.
One current test can supply observations for multiple documented cases.

| Intent case | Actual acceptance test | Required observable outcomes |
| --- | --- | --- |
| CORE-01-A | `p0_discovery` | Exact six tools, independent binary hash, no state directory, unknown and planned command errors |
| CORE-01-B | `p0_schema` | Independently computed schema hash, invalid unknown field, no storage |
| CORE-02-A | New `p0_creator_background_workflow` | Fresh-process reads of revisions zero and one, exact snapshots, independent snapshot hashes |
| CORE-02-B | `p0_rational_rate` | Normalized rate, equivalent-input replay, zero denominator rejected without project directory |
| CORE-03-A | `p0_replay` | Original result, replay flag, latest revision two, latest snapshot hash |
| CORE-03-B | `p0_intent_conflict` | Changed intent rejected, before and after inspected snapshot and hash equal |
| CORE-04-A | New `p0_creator_background_workflow` | Exact 0–47 and 48–95 clips, frame 47 blue and frame 48 gold, all decoded pixels |
| CORE-04-B | `p0_transaction` | Mixed valid put and missing removal rejected, before and after result equal |
| CORE-05-A | New `p0_creator_background_workflow`, plus `p0_native_pixels` | Exact opaque 64-by-64 preview, current alpha preservation and uncovered-frame transparency |
| CORE-05-B | `p0_pending_render_recovery`, plus `p0_clip_bounds` | Every named render checkpoint, exact recovered pixels, one PNG, matching replay receipt, out-of-range rejection |
| CORE-06-A | `p0_receipt_binding` | Actual file hash and decoded dimensions equal stored receipt and verification measurements |
| CORE-06-B | `p0_tamper` | Verify and replay reject altered PNG, final bytes equal saved altered bytes |
| CORE-07-A | `p0_protocol` | Valid envelope returns one document, matching request ID, empty stderr, exit zero, duplicate-key rejection |
| CORE-07-B | `very_short_deadline_has_one_terminal_response`, `deadline_terminates_work_and_same_intent_recovers`, `slow_reader_does_not_truncate_a_selected_response` | Bounded blocked stdin, hook timeout and recovery, complete large response after draining |
| CORE-08-A | `p0_progress_authority`, current `RuntimeDefault` | Exact eight compiled CORE IDs, remaining planned, empty evidence, independent binary identity |
| CORE-08-B | `p0_progress_authority` | Forged ledger and receipt saved, progress unchanged, future command still unsupported |

Represent multi-test bindings as separate contract subcases with stable suffixes, such as `CORE-05-B-recovery` and `CORE-05-B-bounds`.
The parent `CORE-05-B` passes only when every subcase passes in every required profile.
Document the suffixes in the Verification section and require their exact presence.

Ordinary subcases require default and test-hooks profiles. Hook-only subcases require test-hooks explicitly.
Missing platform support stays incomplete. It is not silently omitted.

CORE-05 currently lists `P0-CRASH-RECOVERY` in the ledger.
That test exercises project create and commit recovery.
The actual pending-render test is `p0_pending_render_recovery`, with `P0-RENDER-RECOVERY-<hook>` evidence directories.
Intent coverage must bind that actual render test instead of the ledger's label alone.
Keep current ledger checks in place during this bounded addition.

## Smallest scenario additions

Add one creator test, `p0_creator_background_workflow`, with `P0-CREATOR-BACKGROUND` evidence.

The test creates the documented 96-frame, 24-fps, 64-by-64 project.
Revision one contains the opaque `[12,25,48,255]` background and produces the exact frame-zero PNG.
Fresh CLI processes inspect revisions zero and one and independently recompute both snapshot hashes.

Revision two replaces the timeline with blue and gold clips, each 48 frames.
Inspect exact clip positions. Decode every pixel at frames 47 and 48.
The test checks that revision zero remains empty and revision one retains its original clip after revision two.
It covers CORE-02-A, CORE-04-A, and the exact numeric creator fixture for CORE-05-A.

Instrument current tests for the other named cases.
Add a valid-envelope call to `p0_protocol` with request-ID, diagnostics, and framing assertions.
Extend `p0_receipt_binding` to assert decoded dimensions and fresh verification measurements explicitly.
Save slow-reader and hook-child observations that currently bypass `Run::raw`.
No new renderer, timeline semantics, fixture codec, or execution framework is necessary.

## Module and report ownership

| Proposed path | Responsibility |
| --- | --- |
| `docs/features/intent.json` | All 81 purposes, cases, expectations, non-goals, and review requirements |
| `docs/features/check.mjs` | Required intent fields, exact ledger IDs, documentation case links, structure-only receipt |
| `crates/editor-cli/tests/acceptance.rs` | current real CLI scenarios, labeled captures, one new creator fixture |
| `crates/editor-devcheck/src/intent.rs` | Strict contract validation, independent comparisons, case aggregation, intent report |
| `crates/editor-devcheck/src/model.rs` | New `IntentContract` and `IntentOutcomes` check IDs and report link |
| `crates/editor-devcheck/src/run.rs` | Fixed plan integration and writing the intent report before evidence inventory |
| `crates/editor-devcheck/src/evidence.rs` | current hashes, canonicalization, independent PNG decoding, inventory |
| `crates/editor-devcheck/src/process.rs` | current subprocess ownership and bounded execution |
| `docs/VERIFICATION.md` | Report meaning, commands, and proof limits |

`IntentContract` is required in both modes.
`IntentOutcomes` is required only in full mode, after both profiles and the current evidence audit.
Architecture emits `not-run` runtime rows. These rows do not make its structural run incomplete.

Full requires all implemented cases to pass. Planned cases remain visible and do not block bounded P0 completion.
Every full report names its scope as `implemented-feature-observable-outcomes`, never `all-feature-intent-verified`.

The private module has only two public functions for its callers.

```rust
	fn contract(root: &Path, ledger: &serde_json::Value)
		-> Result<IntentContract, NonEmpty<Violation>>;
	fn report(contract: &IntentContract, run: &Path,
		mode: VerificationMode, identities: &[RuntimeIdentity],
		checks: &[CheckRecord]) -> io::Result<IntentCoverageReport>;
```

Both signatures are sketches. Their bodies are not implemented.
`report` hides evidence resolution, independent comparisons, profile aggregation, and review separation.
The caller supplies the current run context and receives one report. The module coordinates individual outcomes.

Each report feature retains the compiled capability state and has separate coverage fields.

```rust
	struct FeatureCoverage {
		feature_id: FeatureId,
		capability_state: CapabilityState,
		purpose: String,
		scenario: String,
		contract_state: ContractState,
		measurement: MeasurementState,
		reviews: Vec<ReviewCoverage>,
		cases: Vec<CaseCoverage>,
	}
	enum MeasurementState { Measured, Failed, Incomplete, NotRun, NotImplemented }
	enum ContractState { Valid, Invalid }
	enum ReviewState { Pending, Reviewed, NotRequired }
```

The full report also carries current run ID, source identity, contract hash, both runtime identities, and assurance limitations.
Each outcome row retains its predicate, independently derived actual value, result, and hashed evidence paths.
Failed comparison rows explain the difference, for example `expected [12,25,48,255], observed [0,0,0,255]`.
Missing, stale, truncated, malformed, or unfinished observations cannot become `Measured`.
An observed mismatch takes priority over incompleteness for the affected outcome.
Aggregation retains both failed and incomplete counts.

Planned features show their purpose, named cases, required review, and `NotImplemented` measurement.
Their measurement denominator stays separate from the eight implemented features.
Valid planned documentation cannot count as runtime coverage.
No feature changes from `implemented` to `verified`.

Keep the current 0, 1, 2, and 64 exit meanings for the development verifier.
Required mismatches exit 1. Missing observations without observed mismatches exit 2.

Required human review remains unreviewed until an explicit reviewer records the review against the exact contract and source hashes.
For output review, also bind the exact artifact hash and required coverage.
This change does not introduce a review-authentication or approval system.
The initial report therefore cannot manufacture `Reviewed` from a test or old approval file.

Measured CORE behavior can pass full mode while purpose review remains unreviewed.
The human-readable report must say so. It cannot label the complete creator purpose as verified.

## Failure probes

Add meaningful auditor regressions with copies of a genuine fresh run.
Each probe changes one observation and keeps the other valid evidence.

| Probe | Expected report result |
| --- | --- |
| Remove a PNG or referenced response | Incomplete outcome, nonzero full result |
| Copy a passing case from a previous run | Stale run ID rejected, no measured case |
| Substitute the hook binary identity into default evidence | Profile mismatch rejected |
| Change request RGBA but retain a matching output | Declared given/action mismatch fails |
| Forge `completion.json` without observations | Incomplete case, never measured |
| Preserve a successful exit and replace the response with wrong revision | Observable comparison fails |
| Use an unexpected symlink for the artifact | Evidence-path rejection |
| Delete an outcome from an implemented contract | Contract validation fails |
| Mark a planned case executable | Contract-state failure, no promotion |
| Change source or contract during the run | current workspace-stability failure and no current-build measurement |

The decisive end-to-end negative probe uses a compiler-successful wrong-pixels build.

1. Copy the bounded native workspace into a run-owned scratch directory.
2. Change only the solid-pixel calculation in the scratch directory to emit black.
3. Preserve normal receipt hashing and artifact verification.
4. Build the ordinary Rust CLI successfully, with unchanged discovery and schemas.
5. Run full checks against the scratch checkout through the current verifier and process owner.

Requests and project inspection still specify the expected creator color.

The generated PNG and its genuine receipt consistently contain black pixels.
The saved outcome auditor must report a pixel mismatch. Full must exit nonzero.

Before the acceptance assertion, capture the PNG. This capture lets the report explain the failure even when Cargo fails.

This probe demonstrates that compile success, schema identity, receipt integrity, and exit zero cannot replace expected-pixel proof.
After you save the failure evidence, discard the scratch code.
Never change the user's runtime or production project for the probe.

## Maintaining the contract

1. Write the feature purpose and creator scenario in the current feature document.
2. Add the declarative intent entry that matches the contract and has stable named cases.
3. State observable outcomes and required human review separately.
4. Bind current real CLI tests when they exercise the exact cases.
5. Add the smallest scenario test for any unobserved case.
6. Capture labeled raw evidence before assertions.
7. Add a failure probe that breaks the intended outcome. Where possible, preserve successful execution.
8. Run architecture mode for structure.
9. Run full mode for implemented outcomes.
10. Review the saved report and purpose contract independently.

When a planned feature becomes implemented in a later authorized change, its executable bindings become mandatory.
A state change with planned bindings fails contract validation.
Do not add a broad interpreter or arbitrary checks merely to express one new outcome.
Add a bounded comparison only when current comparisons cannot independently inspect the outcome.

## Rationale and alternatives

Laziness Protocol drove reuse of acceptance tests and the fixed verification commands.
It removes a second scenario executor and keeps process ownership unchanged.
Prove It Works drove independent reads of requests, snapshots, PNGs, and unchanged evidence after rejection.
Tests name the creator cases, while the verifier re-evaluates actual observations against declared expectations.

The design rejects a documentation-only purpose checker because it cannot distinguish correct pixels from wrong pixels.
The design rejects a separate devcheck scenario executor because it duplicates established CLI fixtures and process control.
The design rejects assertion-success records as the only evidence. Such a report only repeats a test's claim.

This design accepts some duplication between test assertions and independent outcome comparisons.
That duplication produces a report that a maintainer can inspect without a successful Cargo log.
It also accepts explicit observation labels in tests to avoid brittle numeric request indexes.
Human review remains necessary for whether the contract expresses the right creator purpose.
Mechanical comparisons prove only the outcomes the contract makes observable.

The parent arena selects or rejects this candidate. No synthesis decision is claimed here.
First, encode the eight CORE contracts. Then, run structure-only validation before you add observation capture.
