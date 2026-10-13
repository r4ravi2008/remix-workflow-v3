# Pure Swift control runner design A02

## Result and status

This design defines one runner for the four reviewed pure Swift controls.

The runner starts only after an independent readback accepts one A04 build attempt.
It never starts the native producer or the separately compiled duplicate PNG control.

This document is design-only. No runner, control binary, producer, or native framework was executed.

The runner policy binds the frozen Swift A15 package and the accepted A04 helper source.

The design read these current source-only identities:

| Grounding file | SHA-256 |
| --- | --- |
| A01 runner design | `1a06ba7c5a9c32daabbf6fe48f0dfeb84a9067159039c12fb2fb63625b3d38b7` |
| A01 parent design review | `4e1613cbe335d5d5d0e071b6bda22b1452e38e5c1f641bf44dfdfb15d0957d40` |
| `prepare_swift_build_a04.py` | `ba632ed73005d8c3f870d4b7886c3057ae80405071c4f2154469fe090c195886` |
| A04 helper review | `890665f27625de3ef77a71841a60ec026c5fc21ccfb72f58f1b80f43ab20ddd7` |
| A15 `source-manifest-a15.json` | `0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e` |
| A15 source review | `d19d5708636bd4fa2451d5d4fa1b863165c36476ff28442d0350d877bdc81f01` |
| `png-consumer-control.swift` | `0be8296ca50746f1a4828453568c9bed2646010e46e42e322ac9aa355b408727` |
| `png-consumer-shared.swift` | `22c66166890efc6dfd2e2076d1117139e1b7481f71a4e63df676ab9b2e185866` |
| `failed-publication-control.swift` | `753cd0d4b9f57b5157bc5af299a3839b47d6858bf70a1c643a0de6787d649284` |
| `persisted-output-budget-control.swift` | `a1586e82c51d3aca668eef39437e2132d3c46868346dc153cb87b20d81d6e80c` |
| `persisted-output-budget-shared.swift` | `8c678f77f0aabf2b7072be39d72c9fd9bae7926461c98d211e103bc305428838` |
| `terminal-publication-control.swift` | `5562f922005da7b7811c566b2f93e09e9f24422971cae32587bb9c5bc628e9d2` |

These hashes identify the design inputs. They do not authorize a build or control run.

## Caller usage first

The future runner has no default package, build attempt, or evidence file.

```text
run_swift_controls_a02.py \
  --package feasibility-swift-a15 \
  --manifest source-manifest-a15.json \
  --manifest-sha256 0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e \
  --build-attempt swift-build-aNN \
  --build-report report.json \
  --build-report-sha256 <reviewed-build-report-sha256> \
  --build-seal publication-seal.json \
  --build-seal-sha256 <reviewed-build-seal-sha256> \
  --build-readback build-parent-readback-aNN.json \
  --build-readback-sha256 <reviewed-readback-sha256> \
  --authorization pure-control-authorization-aNN.json \
  --authorization-sha256 <reviewed-authorization-sha256> \
  --attempt swift-control-run-aNN
```

The caller supplies safe direct-child names and lowercase SHA-256 values.
The runner derives every source and executable from the accepted manifest and A04 build map.

The authorization has these minimum facts:

```json
{
  "schema": 1,
  "state": "swift_build_readback_accepted_for_pure_controls",
  "allow_pure_control_execution": true,
  "allow_native_producer_execution": false,
  "build_helper_operation": "manifest_authorized_swift_build_preparation_a04",
  "build_helper_source_sha256": "ba632ed73005d8c3f870d4b7886c3057ae80405071c4f2154469fe090c195886",
  "manifest_sha256": "0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e",
  "build_report_sha256": "<exact>",
  "build_seal_sha256": "<exact>",
  "build_parent_readback_sha256": "<exact>",
  "runner_source_sha256": "<exact after implementation review>",
  "scope": "four source-control binaries only"
}
```

The runner rejects a missing, false, unknown, or mismatched field before any child starts.

## Closed control set

The A15 manifest contains this exact ordered `sourceControls` list.

| Order | Primary source | Report schema | Selected A04 binary |
| ---: | --- | ---: | --- |
| 0 | `png-consumer-control.swift` | 3 | `binaries/source-control-00` |
| 1 | `failed-publication-control.swift` | 1 | `binaries/source-control-01` |
| 2 | `persisted-output-budget-control.swift` | 2 | `binaries/source-control-02` |
| 3 | `terminal-publication-control.swift` | 1 | `binaries/source-control-03` |

The runner requires identical keys in `sourceControlCompileUnits` and `sourceControlReportSchemas`.
Every schema must be a positive JSON integer, excluding booleans.

Every `*ControlSource` caller binding must name one control exactly once.
The A15 `callerBindings.sourceSha256` equals the first producer Swift filename.

The A15 manifest satisfies these bindings and uses this exact A14 report policy:

- `swift-bounded-png-consumer-control-a14`;
- `swift-failed-publication-evidence-control-a14`;
- `swift-persisted-output-budget-control-a14`;
- `swift-terminal-publication-control-a14`.

The A15 manifest producer remains `independent-swift-coretext-a14`.
The package name and report producer strings are intentionally versioned independently.

An accepted A04 build map also contains `producer` and `png-control` binaries.
The runner verifies their parent evidence but never launches either binary.

## Authority chain

The runner accepts a build only when all following joins hold.

1. The explicit manifest hash matches before JSON parsing.
2. The manifest source rows match path, bytes, hash, device, inode, and mode.
3. The build report binds A04 source SHA-256 `ba632ed73005d8c3f870d4b7886c3057ae80405071c4f2154469fe090c195886`.
4. The report uses operation `manifest_authorized_swift_build_preparation_a04`.
5. The A04 report state is `swift_builds_complete_binaries_unexecuted`.
6. A04 reports all identity, preflight, root, binary, log, and contract checks as true.
7. A04 still reports every compiled binary as unexecuted.
8. The A04 publication seal binds the exact report observation and held build root.
9. The parent readback independently matches the manifest, report, seal, sources, logs, and binaries.
10. The authorization hashes the accepted parent readback and permits only pure controls.
11. The ordered authorized and observed binary maps are byte-for-byte equal.

The runner selects the four entries whose `kind` is `source_control`.
It requires the exact filename, schema, compile-unit order, label, and binary path above.

For every selected build step, the runner requires one final Mach-O observation with:

- a regular executable file;
- a thin arm64 `MH_EXECUTE` header;
- exactly one `LC_UUID`;
- exact bytes, SHA-256, device, inode, mode, and UUID from build readback;
- unchanged bounded load-command count and byte span.

The runner opens the build root, its `binaries` directory, and each binary without following symlinks.
It keeps those descriptors through the corresponding child lifetime.

## Typed contract

```text
RunnerRequest {
  package: SafeComponent,
  manifest: SafeComponent,
  manifest_sha256: Sha256,
  build_attempt: SafeComponent,
  build_report: SafeComponent,
  build_report_sha256: Sha256,
  build_seal: SafeComponent,
  build_seal_sha256: Sha256,
  build_readback: SafeComponent,
  build_readback_sha256: Sha256,
  authorization: SafeComponent,
  authorization_sha256: Sha256,
  attempt: SafeComponent,
}

ControlBinding {
  ordinal: 0..3,
  label: String,
  primary_source: String,
  compile_units: [String],
  report_schema: PositiveInt,
  binary_relative_path: String,
  source_observations: [FileObservation],
  build_binary_observation: MachOObservation,
}

ProcessCapture {
  argv: [String],
  cwd: String,
  environment: Map<String, String>,
  started: Bool,
  pid: Optional<Int>,
  exit_code: Optional<Int>,
  timed_out: Bool,
  output_limit_exceeded: Bool,
  termination: Optional<TerminationRecord>,
  stdout: FileObservation,
  stderr: FileObservation,
}

ControlResult {
  binding: ControlBinding,
  binary_before: MachOObservation,
  binary_after: MachOObservation,
  binary_path_after: MachOObservation,
  process: ProcessCapture,
  parsed_schema: Optional<Int>,
  assertion_results: [AssertionResult],
  passed: Bool,
}

EvidenceBoundaries {
  native_producer_started: Bool,
  duplicate_png_control_started: Bool,
  control_reports_image_io_used_false: Optional<Bool>,
  non_png_control_reports_native_calls_false: Optional<Bool>,
  loaded_control_image_attested: Bool,
  native_framework_call_trace_attested: Bool,
  gpu_used: Bool,
  resolve_used: Bool,
  creative_acceptance_claimed: Bool,
}

RunnerReport {
  schema: 1,
  state: RunnerState,
  request: RunnerRequest,
  parent_build_evidence: ParentBuildEvidence,
  attempt_root: DirectoryBinding,
  inputs_before: InputClosure,
  controls: [ControlResult],
  inputs_after: InputClosure,
  all_inputs_matched: Bool,
  all_four_controls_started: Bool,
  all_four_controls_passed: Bool,
  boundaries: EvidenceBoundaries,
}
```

The implementation surface stays small:

```text
preflight(request) -> PreparedControlRun
select_control_bindings(manifest, build_report) -> [ControlBinding; 4]
observe_held_binary(fd, expected_path) -> MachOObservation
run_one_control(prepared, binding) -> ControlResult
parse_control_json(binding, stdout_bytes) -> ParsedControlReport
validate_control(binding, parsed) -> [AssertionResult]
finalize(prepared, results) -> PublishedRunnerReport
```

No function receives an arbitrary executable path.

## Execution transaction

1. Create one fresh direct-child attempt directory with mode `0700`.
2. Hold its directory descriptor until final publication completes.
3. Publish `preflight.json` with descriptor-relative `O_EXCL` creation.
4. Open and validate the complete authority chain before launching any child.
5. Seal all four source and binary observations before the first launch.
6. Execute the four controls sequentially in manifest order.
7. Recheck the held attempt root before and after every child.
8. Recheck the selected binary descriptor and pathname after every child.
9. Stop future launches on authority drift, timeout, cancellation, or output overflow.
10. Continue after a semantic control failure when all authority remains stable.
11. Reobserve every input after the last permitted child.
12. Publish `report.json` and a report seal through the held attempt descriptor.

The runner passes no arguments to a control binary.
It uses an explicit environment and removes all `DYLD_*` variables.

The runner uses `stdin=/dev/null`, one new process group, and one child at a time.
The working directory and `TMPDIR` are fresh children of the held attempt root.

## Bounded process handling

Each control has these fixed limits:

| Resource | Limit |
| --- | ---: |
| wall-clock time | 15 seconds |
| termination grace | 2 seconds |
| stdout retained bytes | 1,048,576 |
| stderr retained bytes | 131,072 |
| serialized runner report bytes | 8,388,608 |

The runner drains stdout and stderr concurrently with nonblocking pipes.
It never waits for process exit while either pipe can block the child.

An output crossing fails before another byte enters the retained buffer.
The runner then sends `SIGTERM`, waits two seconds, sends `SIGKILL` if needed, and reaps the group.

The runner writes captured bytes once through descriptor-relative exclusive files.
It releases each in-memory capture after its file observation is sealed.

The stdout cap bounds parser input bytes, not the parser's decoded object graph.
The first implementation has no checked parser-heap admission and makes no parser-memory bound.

The other limits bound retained capture and persisted serialized report bytes only.
The report cap rejects oversized encoded bytes before publication; it does not bound encoder heap.
These limits do not bound Swift, Python, JSON parsing, Foundation, CryptoKit, Dispatch, or dynamic-loader memory.

`SIGINT` or `SIGTERM` requests cancellation.
Cancellation terminates and reaps the active group, preserves bounded captures, and starts no later control.

## Strict JSON rules

The parser accepts UTF-8 containing exactly one JSON object and one optional final newline.
It rejects duplicate keys, trailing data, missing fields, extra fields, type substitutions, and non-finite numbers.

It parses stdout after the process is reaped, even when the exit code is nonzero.
Qualification still requires exit code zero, empty stderr, and every explicit assertion below.

Missing, empty, `null`, and false remain distinct observations.
The runner performs no report normalization.

The runner requires the four exact A14 `producer` literals frozen inside A15.
No earlier package or generic producer suffix is an accepted fallback.

## PNG callback control assertions

Top-level requirements are schema `3`, producer `swift-bounded-png-consumer-control-a14`,
`imageIOUsed=false`, and `callbackThrows=false`.
`sharedSource` must equal `png-consumer-shared.swift`.

The synchronization string must equal:

```text
NSRecursiveLock serializes callback state; nested entry fails before copy; seal waits for active copy and rejects later writes
```

The report must contain these five cases in order, with `passed=true` and `allPassed=true`.

| Case | Capacity | Returns | Bytes | Failure | Entries | Max active | Reentrant | SHA-256 |
| --- | ---: | --- | ---: | --- | ---: | ---: | ---: | --- |
| `exact-boundary` | 8 | `[8]` | 8 | `none` | 1 | 1 | 0 | `66840dda154e8a113c31dd0ad32f7f3a366a80e8136979d8f5a101d3d29d6f72` |
| `one-byte-overflow` | 8 | `[7,0]` | 7 | `capacity` | 2 | 1 | 0 | `32bbe378a25091502b2baf9f7258c19444e7a43ee4593b08030acd790bd66e6a` |
| `cancel-before-copy` | 8 | `[0]` | 0 | `cancelled` | 1 | 1 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `reentrant-rejected` | 8 | `[0,0]` | 0 | `reentrant` | 1 | 1 | 1 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `concurrent-serialized` | 16 | `[8,8]` | 16 | `none` | 2 | 1 | 0 | `5dfbabeedf318bf33c0927c43d7630f51b82f351740301354fa3d7fc51f0132e` |

Every case must report `releaseObserved=true` and `sealed=true`.
The table SHA-256 must equal both `sha256` and `expectedSha256` for that case.

This control invokes the shared callback directly.
It does not establish ImageIO scheduling or native PNG publication.

## Failed-publication shape assertions

Top-level requirements are schema `1`, producer `swift-failed-publication-evidence-control-a14`,
`nativeCalls=false`, `fileIO=false`, and `maximumEvidenceEntries=23`.

The report contains exactly these ordered cases:

1. `failed-partial-file-publication`;
2. `failed-complete-file-publication`.

Each case requires `expectedEvidenceEntries=23`, `observedEvidenceEntries=23`, no missing keys, and `passed=true`.

Both cases require the thirteen base keys and six failed-prefix keys.
They also require `releaseObservedAfterDestroy` and `callbackStatusAfterDestroy`.

The ordered base keys are:

```text
partialBytes, partialSha256, intendedBytes, intendedSha256,
callbackStatus, releaseObserved, callbackSealed, callbackEntries,
maximumActiveCallbacks, reentrantAttempts, finalizeResult, partialStatus,
capturePhase
```

The ordered prefix keys are:

```text
requestedWriteBytes, failedFilePrefixBytes, failedFilePrefixSha256,
failedFilePrefixIdentity, failedFilePrefixStatus,
failedFilePrefixReadComplete
```

The partial branch adds `partialPath` and `partialWriteError`.
The complete branch adds `partialPath` and `completePathObservation`.

The exact arrays are `base + branch + prefix + post-destroy` in that order.

The exact ordered key arrays must match the source-frozen policy.
Top-level `allPassed` must be true.

This report proves only the pure 23-entry shape calculation.
It does not prove either native failure path occurred.

## Persisted-budget and table assertions

Top-level requirements are schema `2`, producer `swift-persisted-output-budget-control-a14`,
`nativeCalls=false`, and `fileIO=false`.

The runner requires these exact values:

| Field | Value |
| --- | ---: |
| `persistedOutputCapBytes` | 536,870,912 |
| `completeQualificationBoundBytes` | 396,071,265 |
| `allocationEventLogCapBytes` | 16,777,216 |
| `reservationTableOwnerBytes` | 1,056,000 |
| `reservationTableSlotCount` | 256 |
| `reservationTableKeyBytes` | 4,096 |
| `reservationTableInitialReplayBaselineBytes` | 1,081,600 |
| `reservationTableObservedPeakSlots` | 256 |

The report contains exactly five ordered cases:

| Case | Exact `expected` | Exact `observed` |
| --- | --- | --- |
| `persisted-bound-exact` | `cap >= completeQualificationBoundBytes` | `cap=396071265; bound=396071265` |
| `persisted-bound-one-byte-under` | `cap < completeQualificationBoundBytes rejects` | `cap=396071264; bound=396071265` |
| `event-exact-boundary-with-cleanup-and-terminal-reserves` | `ordinary bytes plus cleanup and terminal reservations consume exactly 100 bytes` | `used=100; cleanup=0; terminal=0` |
| `event-one-byte-under-rejects-before-consumption` | `ordinary admission rejects when protected cleanup and terminal reservations leave one byte too little` | `used=0; cleanup=0; terminal=30` |
| `reservation-table-exact-capacity-peak-and-recycle` | `the shared fixed table admits 256 slots, rejects the 257th, reports peak 256, and recycles one slot` | `owner=1056000; slots=256; keyBytes=4096; occupied=256; peak=256; baseline=1081600` |

Every source-frozen `expected` string must match exactly.
Every case and top-level `allPassed` must be true.

These checks cover the shared Swift admission logic.
They do not prove process RSS, native allocation, or producer publication.

## Terminal-publication assertions

Top-level requirements are schema `1`, producer `swift-terminal-publication-control-a14`,
`nativeCalls=false`, and `fileIO=false`.

The report must repeat the 536,870,912-byte persisted cap and 16,777,216-byte event cap.
It contains exactly four ordered cases:

| Case | Exact `expected` | Exact `observed` |
| --- | --- | --- |
| `exact-boundary-update-append-and-no-post-terminal-event` | `pre-admit, update before append, finish at 100 bytes, then reject a second terminal event` | `prepared=true; appended=true; file=70; eventBefore=20; terminalEvent=10; finished=true` |
| `persisted-one-byte-under-rejects-terminal-event` | `report bytes plus prior and terminal event bytes cannot exceed the persisted cap` | `prepared=true; appended=false; file=70; eventBefore=20; terminalEvent=0; finished=false` |
| `event-log-one-byte-under-rejects-terminal-event` | `prior and terminal event bytes cannot exceed the aggregate event-log cap` | `prepared=true; appended=false; file=70; eventBefore=20; terminalEvent=0; finished=false` |
| `terminal-event-requires-preparation` | `append and finish reject before the terminal file is pre-admitted` | `prepared=false; appended=false; finished=false` |

Every source-frozen `expected` string must match exactly.
Every case and top-level `allPassed` must be true.

This control checks the shared state machine only.
It does not write a report or prove terminal publication.

## Evidence boundaries

The A04 helper attests pathname observations before and after compilation.
It explicitly does not attest already loaded helper, Python, compiler, or SDK bytes.

The runner preserves those false boundaries inside `parent_build_evidence`.
Later control execution does not upgrade the historical compiler evidence.

The runner holds and hashes each control binary descriptor before and after execution.
It also reopens the pathname and requires the same file identity and Mach-O facts.

The first runner does not prove which exact bytes the kernel mapped.
macOS has no accepted descriptor-exec route in this unit, and the controls lack a launch handshake.

The report therefore sets `loadedControlImageAttested=false`.
It describes each success as a path-bound control execution observation.

A future suspended-launch and mapped-vnode measurement may add loaded-image evidence.
That extension is outside this runner contract.

The runner reports these fixed boundaries:

```text
nativeProducerStarted = false
duplicatePngControlStarted = false
loadedControlImageAttested = false
nativeFrameworkCallTraceAttested = false
gpuUsed = false
resolveUsed = false
creativeAcceptanceClaimed = false
```

Two report-derived fields are tri-state `Optional<Bool>` observations:

```text
controlReportsImageIOUsedFalse = null | true | false
nonPngControlReportsNativeCallsFalse = null | true | false
```

`null` means a required report is absent, truncated, malformed, or lacks the typed field.
The PNG value becomes true only after structural validation observes `imageIOUsed=false`.
It becomes false only after a structurally valid report observes `imageIOUsed=true`.

The non-PNG value remains null until all three structurally valid reports expose typed `nativeCalls` fields.
It becomes true when all three values are false, and false when any value is true.
Qualification requires both derived observations to be true.

The reviewed control sources contain no ImageIO, CoreText, or CoreGraphics call.
The runner does not trace framework calls inside an unattested loaded image.

The controls still load their ordinary Swift and system dependencies.
This runner does not close or attest the complete dynamic-library graph.

## Failure states

| State | Meaning | Later controls |
| --- | --- | --- |
| `preflight_rejected_no_controls_started` | Authority, map, schema, or identity failed before launch. | None start. |
| `control_identity_drift_preserved` | A source, binary, build record, or held root changed. | Stop. |
| `control_timeout_preserved` | One child exceeded 15 seconds. | Stop. |
| `control_output_limit_preserved` | Stdout or stderr crossed its cap. | Stop. |
| `control_cancelled_preserved` | A signal requested cancellation. | Stop. |
| `control_process_failure_preserved` | Spawn, signal, exit, or JSON framing failed. | Continue only when common authority remains stable. |
| `control_assertion_failure_preserved` | Parsed JSON violated an explicit control assertion. | Continue for diagnostics. |
| `four_pure_controls_passed` | All four exact controls passed and all inputs matched after execution. | Complete. |
| `report_publication_failure_preserved` | Final report or seal could not publish. | Complete but unqualified. |

Exit zero requires `four_pure_controls_passed` and a stable publication seal.

## Verification plan

Before any accepted Swift execution, reviewers must inspect the runner source and final policy completely.

Source-level negative controls must cover:

- wrong A04 helper hash, operation, or A15 manifest hash;
- reordered, missing, duplicated, and extra control mappings;
- zero, negative, boolean, or mismatched report schemas;
- forged source, report, seal, binary hash, inode, or Mach-O UUID;
- a producer or duplicate PNG executable substituted into the run set;
- duplicate JSON keys, trailing bytes, missing fields, and extra fields;
- every false `passed` or `allPassed` value;
- every wrong exact case value listed above;
- nonempty success stderr, nonzero exit, timeout, cancellation, and output overflow;
- null report-derived observations before launch and after missing or malformed JSON;
- true and false report-derived observations from structurally valid typed fields;
- attempt-root and binary-path replacement before and after a child.

After the final build readback is accepted, one fresh run must execute exactly four controls.
An independent readback must recompute every persisted output hash and identity.

The accepted result remains pure source-control evidence.
It grants no native text, PNG, publication, playback, film, hearing, or creative acceptance.

## Rationale and rejected alternatives

The manifest and A04 map own selection because they already bind source order, compile units, schemas, and binaries.
This avoids caller-selected executable paths.

The runner parses every field instead of trusting exit status.
A control can emit structurally wrong JSON and still exit zero after an implementation defect.

The runner executes the four `source_control` binaries only.
Running `png-control` again would duplicate one source program without adding an independent assertion.

The runner does not copy binaries into its attempt.
A copy would create a second executable identity and weaken the build-to-run join.

The runner does not parse Swift source to discover expected results.
Its reviewed policy freezes exact assertions only after the final package freezes.

The runner does not claim loaded-image identity from pathname hashes.
That claim needs a separate accepted macOS loaded-image measurement.

## Material risks before implementation

1. A04 has not produced an independently accepted build and readback for A15.
2. Active pipe draining, timeout, and process-group cleanup need independent source review.
3. Parser heap amplification remains outside the logical capture limits.
4. The first runner leaves loaded control-image bytes unattested.
5. Pure control success cannot substitute for actual native producer and failure-path proof.
