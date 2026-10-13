# Rust producer subject adapter A01 peer source review

## Disposition

The frozen A01 source is not ready for compilation or control execution.

I found one P1 and six P2 findings. The P1 changes canonical RoleIndex V2 scalar meaning.

This was a read-only, separate-author review. It is same-model-family and nonblind.

I did not compile, import, assemble, or execute the adapter or its controls. I started no child or native process.

## Reviewed authority

The frozen package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-subject-adapter-a01`

The self-excluding manifest is 5,739 bytes with SHA-256:

`ed49aac898d921b9a55601e398439ce7c412d544a0642592ce075b3da68b8e18`

All eight source rows match their declared byte counts and SHA-256 values. All ten external-binding rows also match current bytes.

The fixed fixture is 9,033 bytes with SHA-256:

`548721bcb1805bf9e11be285d1be4c0edfbbd90341e0ed5a5dbe7111cd61db61`

All twenty fixed document descriptors match current path bytes, byte counts, and SHA-256 values.

The manifest's two aggregate values were not independently verified. Finding P2-4 explains the missing reproduction contract.

## P1 findings

### P1-1: The reused A05 adapter encodes integer scalar payloads in little-endian order

`src/lib.rs:26-27` selects the frozen A05 saved-report adapter. `rust_producer_subject_adapter_v1.rs:986-995` inserts its 89 toolchain rows unchanged.

The selected adapter uses `to_le_bytes()` for `Unsigned64` and `Signed64` values at `native-preparation-implementation-a05/src/saved_report_adapters_v1.rs:1016-1024`.

RoleIndex V2 requires fixed-width big-endian integer scalar payloads. The requirement appears in `native-preparation-next-design-a06.md:196-197` and the independent field map.

For example, toolchain schema value `1` becomes `01 00 00 00 00 00 00 00`. Canonical V2 requires `00 00 00 00 00 00 00 01`.

The generic validator checks only the eight-byte length. It therefore accepts the wrong semantic value.

The repair needs a new saved-report adapter successor. The frozen A05 adapter must remain unchanged.

The successor needs exact big-endian scalar controls. An independent decoder comparison must cover positive and negative integer values.

## P2 findings

### P2-1: A fixed path replaced by a FIFO can block either measurement reader

`subject_observation.rs:93-107` and `subject_observation.rs:259-273` open each path for reading before checking the file type.

Both open calls use `O_CLOEXEC | O_NOFOLLOW`. Neither call uses `O_NONBLOCK`.

Opening a FIFO read-only can wait indefinitely for a writer. Canonicalization and the later `is_file()` check do not prevent that wait.

Add `O_NONBLOCK` on the supported Unix path. Reject the nonregular descriptor immediately after `fstat`.

Add one source control for each measurement session. Each control must reject a FIFO without waiting for a writer.

### P2-2: The candidate labels a hybrid row set as `RustProducerRoleSchemaV1`

The package fixes `ROLE_SCHEMA` to `RustProducerRoleSchemaV1` at `rust_producer_subject_adapter_v1.rs:25`.

A05 defines the original V1 role families. A06 replaces the Rust toolchain report with 89 typed rows under `RustProducerQualificationV2`.

The candidate inserts only `adapted.rows` at `rust_producer_subject_adapter_v1.rs:995`. It omits the adapter's `authority_rows` and ignores its encoded 90-row authority value.

The candidate then adds the report again as `rust.toolchain.observation` at lines 996-999. The reviewed A05 adapter names its report and authority roles differently.

The candidate also adds unlisted list and scalar roles. Examples include `rust.source.files`, `rust.dependency.files`, and `rust.build.source_gate_bindings`.

No contract states the complete effective row schedule or exact total. No fixture control compares every emitted role and kind against a frozen schedule.

Define a distinct diagnostic candidate role schema. Freeze every role, observation kind, family count, and exact total.

Alternatively, align the candidate with one reviewed A06 adapter projection. Explain the report and authority-row treatment explicitly.

This repair must remain candidate-only. It must not add `Accepted<T>`, a pin, a trust root, or loader authority.

### P2-3: The PNG callback command is not joined to `controlExecutable`

`validate_png_callback_step` checks callback arguments 1 through 4 at `rust_producer_subject_adapter_v1.rs:1721-1733`.

The function never compares `argv[0]` with `pngControlReport.controlExecutable.path`.

The frozen report currently contains equal paths. The adapter does not prove that relationship or reject its mutation.

Pass the measured executable descriptor into the callback-step validator. Require exact path-byte equality with `argv[0]`.

Add a one-field mutation control that changes only `argv[0]` and expects a closed join error.

### P2-4: The manifest aggregate values have no reproducible encoding contract

`source-manifest-a01.json:52` and line 105 declare source and external aggregate SHA-256 values.

No package document defines the aggregate domain, row order, length encoding, or included fields. The values are therefore ambiguous to an independent reviewer.

Define one domain-separated, length-prefixed recipe for each aggregate. Bind the recipe in the package contract.

The manifest must retain its self-excluding rule. This repair does not require a runtime trust manifest.

### P2-5: The stated retained-payload limit omits duplicate byte and JSON owners

`subject-contract-a01.md:37` says the limits cover requested and retained adapter payload.

`MeasurementSession::measure_json` clones cached file bytes at `subject_observation.rs:182-195`. `MeasuredDocument` retains that clone and a parsed JSON tree.

The cache retains the original bytes. Fixture controls then clone all measured documents at `fixture_controls.rs:39-42`.

The 64 MiB counter covers unique measured file bytes only. It does not cover these duplicate byte vectors or parsed JSON owners.

Either add checked aggregate owner admission before each clone, or narrow the contract to its actual unique-source-byte scope.

Do not describe this counter as process RSS, allocator metadata, or native memory authority.

### P2-6: Every returned candidate permanently claims that its source is uncompiled

`SubjectLimitation::SourceOnlyUncompiled` is declared at `rust_producer_subject_adapter_v1.rs:85`.

`build_candidate` appends this limitation unconditionally at line 360. Any successful invocation already requires a compiled adapter binary.

A later compiled control result would therefore retain a false source-state claim. The limitation should describe the evidence boundary instead.

Use a neutral limitation such as `CompilationAndControlsRequireSeparateEvidence`. Keep compilation and control evidence in their measured result fields.

`FixtureControlSummary.source_only` can continue to describe the control's scope. Its `compiler_executed` field describes that control method only.

Add one source control for the returned limitation set. The control must prevent a compiled candidate from claiming that its source remains uncompiled.

## Confirmed bounded properties

The public result is `RustProducerSubjectCandidateV1`. It cannot construct `Accepted<T>`.

The package creates no active pin, trust manifest, acceptance record, or execution authorization.

The emitted role guard rejects Swift, observer, comparator, acceptance, and authorization role names.

All fixture scope fields retain false native execution and product integration claims.

The package binds no Swift producer, observer, comparator, media, GPU, or Resolve authority.

These properties do not offset the P1 wire-format failure or the P2 source-readiness gaps.
