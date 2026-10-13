# Native text preparation next design A05

## Status

This is a design-only successor to A04.
A04 and its review remain preserved.

No helper, gate, authorization, run directory, control, producer, observer, or comparator was created or executed.
No product source, project state, media, GPU process, or Resolve state changed.

Comparator A11 is rejected.
Its current README no longer agrees with its frozen manifest observation.
The separate drift evidence remains outside this design.

Comparator A12 is pending.
A05 does not bind A11 or A12 as accepted evidence.

A05 does not claim that it closes the A03 comparator defect.
It defines the authority needed by a future accepted comparator.

## Caller usage first

There is no global `assemble` call.
Each stage accepts only the evidence needed for that stage.

```rust,ignore
// First implementation unit.
let rust_qualification = RustProducerQualificationV1::load(
    rust_acceptance_record,
    rust_runner_acceptance_record,
)?;

let rust_stage = RustProducerStage::new(rust_qualification)?;

let rust_primary = rust_stage.authorize(ProducerAttempt {
    repetition: Repetition::Primary,
    output_parent: rust_output_parent,
})?;

let rust_fresh = rust_stage.authorize(ProducerAttempt {
    repetition: Repetition::Fresh,
    output_parent: rust_output_parent,
})?;
```

The Rust stage does not accept Swift, observer, or comparator inputs.
Missing later evidence cannot block Rust authorization.

Swift remains a separate stage.

```rust,ignore
let swift_qualification = SwiftProducerQualificationV1::load(
    swift_acceptance_record,
    swift_runner_acceptance_record,
)?;

let swift_stage = SwiftProducerStage::new(swift_qualification)?;
```

The current Swift source, build, and pure controls are prerequisite evidence.
They do not include an accepted native producer runner.
`SwiftProducerQualificationV1::load` therefore remains unavailable until that runner qualifies.

Observers consume typed closed producer runs.

```rust,ignore
let rust_observer = ObserverStage::new(accepted_rust_observer)?;
let rust_primary_observation = rust_observer.authorize(rust_primary_closed)?;
```

The comparator has no accepted variant.

```rust,ignore
enum AcceptedComparatorVariant {
    // Intentionally empty in A05.
}
```

The future caller cannot construct or serialize comparator authority.
Adding a variant requires a new reviewed source change.

## Design rules

1. A stage receives only its own accepted qualification.
2. A qualification has one exact role schema.
3. The caller supplies acceptance-record paths, not hashes or role names.
4. The loader measures every file through one descriptor.
5. A machine-readable acceptance record supplies the disposition.
6. Markdown reviews remain evidence bytes, not executable verdict parsers.
7. A stage authorization grants one direct child one attempt.
8. A later stage consumes a typed closed result from the earlier stage.
9. Pending evidence can produce diagnostics only.
10. No pending value can serialize an execution authorization.

## Artifact observations

```rust,ignore
struct MeasuredArtifact {
    role: ClosedRole,
    resolved_path_bytes: Vec<u8>,
    display_path: String,
    bytes: u64,
    sha256: Sha256,
    identity: StableIdentity,
    macho: Option<MachOIdentity>,
}

struct StableIdentity {
    device: u64,
    inode: u64,
    mode: u32,
    size: u64,
    modified_ns: i128,
    changed_ns: i128,
}

struct MachOIdentity {
    architecture: Architecture,
    uuid: [u8; 16],
}
```

The loader resolves the path once before opening it.
It retains that resolved byte string as the observation label.

The loader opens a regular file without following the final link.
It records `fstat` before reading.
It hashes the complete bounded bytes from that descriptor.
It records `fstat` again before closing.

The two descriptor observations must match exactly.
The loader then verifies the pathname still names that device and inode.

This is local path and descriptor evidence.
It is not privileged-filesystem attestation.

## Canonical role-index encoding

Role-index authority uses a binary encoding.
Display JSON is diagnostic only.

The binary starts with these bytes:

```text
native-text-role-index-v1\0
```

The remaining fields use big-endian integers.

```text
u32 schema = 1
u32 row_count
repeated row_count times:
  u16 role_byte_count
  role ASCII bytes
  u32 resolved_path_byte_count
  resolved path bytes
  u64 file_byte_count
  32 raw SHA-256 bytes
  u64 device
  u64 inode
  u32 mode
  i128 modified_ns
  i128 changed_ns
  u8 macho_tag
  if macho_tag == 1:
    u8 architecture_tag
    16 raw Mach-O UUID bytes
```

The role grammar is `[a-z][a-z0-9_.:-]{0,127}`.
The path must be absolute and contain no NUL byte.
Each role is unique.

Rows sort by role bytes, then resolved path bytes.
The encoder rejects any input that is not already in that order.

Two roles may name one file.
All file fields for that path must then match exactly.
One path cannot carry conflicting observations.

`macho_tag` is either zero or one.
The architecture tags are closed by the role schema.

The maximum role count is 4,096.
The maximum encoded role index is 4 MiB.

The aggregate is:

```text
SHA-256(the complete role-index bytes)
```

The gate stores the role-index file descriptor and aggregate.
The runner reconstructs the bytes independently before launch.
The runner repeats the reconstruction after child closure.

## Machine-readable acceptance

Review disposition does not come from a caller enum.
It comes from one exact acceptance record.

```rust,ignore
struct AcceptanceRecordV1 {
    schema: ExactU32<1>,
    operation: ExactString<"native_text_qualification_acceptance">,
    subject_kind: AcceptedSubjectKind,
    subject_version: ClosedVersion,
    role_schema: ClosedRoleSchema,
    subject_role_index: RoleIndexRef,
    peer_review: ArtifactRef,
    parent_review: ArtifactRef,
    disposition: ExactString<"accepted_no_p1_or_p2">,
    scope: ClosedAcceptanceScope,
    limitations: BoundedVec<ClosedLimitation, 0, 64>,
    execution_authorized_by_record: ExactBool<false>,
}

struct RoleIndexRef {
    rows: u32,
    bytes: u64,
    sha256: Sha256,
}
```

The JSON parser rejects duplicate keys, floats, unknown fields, and invalid UTF-8.
Every integer must fit its declared domain.
Every string has a field-specific byte cap.
Each limitation is a closed enum value with a 256-byte canonical label.

The loader measures the peer review and parent review from their descriptors.
Those descriptors must equal the acceptance record.

The subject role index excludes the acceptance record and its two reviews.
This prevents a self-reference.

The final qualification role index contains:

- every subject row;
- the peer-review artifact;
- the parent-review artifact;
- the acceptance-record artifact.

Only a private loader can construct `Accepted<T>`.

```rust,ignore
struct Accepted<T> {
    value: T,
    final_role_index: RoleIndex,
    _private: PrivateConstructor,
}
```

The caller cannot fabricate `Accepted<T>` or its disposition.

Each independent evidence class has its own acceptance record.
Examples include source, build, input authority, control result, and runner source.

## Rust producer qualification V1

The Rust first unit excludes every observer and comparator role.
It also excludes all Swift roles.

### Rust role schema

The current A05 records define these exact manifest expansions.
The loader derives every row from the measured manifest bytes.

| Role family | Current cardinality | Authority |
| --- | ---: | --- |
| `rust.source.bundle_manifest` | 1 | Source-bundle manifest |
| `rust.source.freeze` | 1 | Pre-build source freeze |
| `rust.source.file:NNNN` | 15 | Sorted source-bundle `files` |
| `rust.source.freeze_file:NNNN` | 14 | Sorted source-freeze `files` |
| `rust.source.freeze_attachment:NAME` | 4 | Authored manifest and three preserved transfer records |
| `rust.dependency.closure` | 1 | Dependency closure |
| `rust.dependency.helper` | 1 | Dependency-closure helper |
| `rust.dependency.metadata` | 1 | Cargo metadata record |
| `rust.dependency.lock` | 1 | Generated `Cargo.lock` |
| `rust.dependency.file:NNNN` | 1,847 | Sorted dependency files |
| `rust.dependency.archive:NNNN` | 35 | Sorted package archives |
| `rust.build.source_gate` | 1 | Compile source gate |
| `rust.build.source_gate_binding:NNNN` | 10 | Sorted source-gate bindings |
| `rust.build.attempt` | 1 | Release build attempt |
| `rust.build.helper` | 1 | Release build helper |
| `rust.build.log` | 1 | Release build log |
| `rust.build.manifest` | 1 | Schema-2 native build manifest |
| `rust.build.manifest_helper` | 1 | Manifest helper |
| `rust.binary.producer` | 1 | A05 release executable |
| `rust.toolchain.observation` | 1 | Toolchain report |
| `rust.toolchain.fixed_artifact:NAME` | 6 | Cargo, rustc, launchers, SDK settings, and helper |
| `rust.toolchain.framework:NAME` | 3 | Framework `Info.plist` observations |
| `rust.toolchain.log:NAME` | 9 | Exact toolchain logs |
| `rust.input.authority` | 1 | Current raw input authority |
| `rust.input.preserved_authority` | 1 | Preserved authority baseline |
| `rust.input.raw_bridge` | 1 | Preserved-to-current bridge |
| `rust.input.raw_bridge_helper` | 1 | Bridge helper |
| `rust.input.pure_control_report` | 1 | Twenty-one-control report |
| `rust.input.pure_control_source_closure` | 1 | Pure-control source closure |
| `rust.input.pure_control_file:NNNN` | 8 | Bridge-declared control files |
| `rust.input.synthetic_cases` | 1 | Exact case document |
| `rust.input.font_manifest` | 1 | Font fixture manifest |
| `rust.input.font_repository` | 1 | Repository record |
| `rust.input.font_license` | 1 | Actual license bytes |
| `rust.input.font:SCRIPT` | 2 | Telugu and Devanagari font bytes |
| `rust.input.authority_helper` | 1 | Input-authority helper |
| `rust.input.authority_runtime_binding` | 1 | Input-authority runtime binding |
| `rust.input.pure_orientation_helper` | 1 | Pure orientation helper |
| `rust.input.pure_runtime_binding` | 1 | Pure-control runtime binding |
| `rust.input.pure_runtime_closure` | 1 | Pure-control runtime closure |
| `rust.png_control.helper` | 1 | Callback-control helper |
| `rust.png_control.report` | 1 | Passed selected-test report |
| `rust.png_control.build_record` | 1 | Test build record |
| `rust.png_control.build_log` | 1 | Test build log |
| `rust.png_control.callback_record` | 1 | Selected callback record |
| `rust.png_control.callback_log` | 1 | Selected callback log |
| `rust.png_control.test_executable` | 1 | Exact test executable |
| `rust.png_control.release_build_record` | 1 | Release-build closure record |
| `rust.policy.document:NAME` | 5 | Probe, synthesis, admission, PNG, and A05 preparation contracts |
| `rust.acceptance:NAME` | 5 | Source, build, input, PNG control, and runner acceptance records |
| `rust.review:NAME` | 10 | Peer and parent review for each acceptance record |
| `rust.runner.source` | 1 | Future stage-specific runner source |
| `rust.runner.contract` | 1 | Future runner wire contract |

The cardinalities above belong to `RustProducerRoleSchemaV1`.
A changed count requires a new role-schema version and new acceptance.

Package manifests already present in `rust.dependency.file:NNNN` are aliases.
The loader does not create a second file observation for those manifests.
It verifies that each package manifest descriptor equals its dependency-file row.

### Rust cross-joins

The Rust loader validates every relationship before authorizing an attempt.

1. The source bundle contains exactly 15 unique sorted source paths.
2. Its domain-separated source aggregate recomputes from those exact bytes.
3. The source freeze contains exactly 14 files and four named attachments.
4. Every freeze descriptor equals its measured file.
5. The dependency closure names the measured lock, metadata, helper, files, and archives.
6. The 35 package manifests alias exact dependency-file rows.
7. Direct dependency policies equal the build manifest's dependency list.
8. The source gate contains exactly ten accepted bindings.
9. The build attempt names that gate, lock, toolchain, helper, log, and binary.
10. The build command, target, SDK, deployment target, and environment match the build manifest.
11. The build manifest names the source aggregate, lock hash, binary hash, and binary UUID.
12. The measured executable bytes and UUID equal the build manifest.
13. Input authority binds both font files, license, repository, case document, and table facts.
14. The raw bridge binds preserved authority, current authority, and all 21 controls.
15. The pure-control before and after identities agree for the six declared inputs.
16. The PNG control uses the same release build, source freeze, dependency closure, and toolchain.
17. The selected callback test passes alone with no after-identity error.
18. Source, build, input, PNG-control, and runner acceptances bind their exact subject aggregates.
19. No observer, comparator, or Swift role appears in the Rust role index.

### Rust runner prerequisite

The preserved A03/A04 runner source remains historical grounding.
It is not accepted for A05 because its gate schema includes comparator and observer authority.

A future Rust V1 runner must receive its own source and result acceptance.
The first Rust authorization remains unavailable until that runner qualifies.

This requirement is local to Rust.
It does not wait for Swift, observer, or comparator evidence.

## Swift producer qualification V1

Swift qualification remains separate from Rust qualification.
The current evidence proves compilation and four pure controls only.

### Swift role schema

| Role family | Current cardinality | Authority |
| --- | ---: | --- |
| `swift.source.manifest` | 1 | A15 source manifest |
| `swift.source.file:NNNN` | 21 | Manifest `files` in manifest order |
| `swift.build.helper` | 1 | Accepted A04 build helper |
| `swift.build.preflight` | 1 | A02 preflight |
| `swift.build.report` | 1 | A02 build report |
| `swift.build.seal` | 1 | A02 publication seal |
| `swift.build.readback_source` | 1 | Parent readback source |
| `swift.build.readback_result` | 1 | Parent readback result |
| `swift.build.input:NN` | 13 | Build report's exact before-and-after closure set |
| `swift.build.binary:NAME` | 6 | Producer, PNG control, and four source controls |
| `swift.build.log:NAME` | 7 | Compiler version plus six build logs |
| `swift.pure_runner.source` | 1 | Four-control runner source |
| `swift.pure_runner.schema` | 1 | Runner wire schema |
| `swift.pure_runner.rationale` | 1 | Runner rationale |
| `swift.no_child.source` | 1 | No-child control source |
| `swift.no_child.rationale` | 1 | No-child rationale |
| `swift.no_child.readiness` | 1 | Corrected readiness record |
| `swift.no_child.result` | 1 | Source-only no-child result |
| `swift.no_child.readback` | 1 | Parent no-child readback |
| `swift.pure.authorization` | 1 | Four-control authorization |
| `swift.pure.preflight` | 1 | Four-control preflight |
| `swift.pure.report` | 1 | Four-control report |
| `swift.pure.seal` | 1 | Four-control publication seal |
| `swift.pure.input:NN` | 13 | Pure-control report's exact before-and-after input set |
| `swift.pure.stdout:NN` | 4 | One stream per control |
| `swift.pure.stderr:NN` | 4 | One stream per control |
| `swift.pure.readback_source` | 1 | Independent readback source |
| `swift.pure.readback_result` | 1 | Independent readback result |
| `swift.input:NAME` | 7 | Cases, authority, font manifest, two fonts, license, and repository |
| `swift.policy.document:NAME` | 4 | Probe, synthesis, admission, and A05 contracts |
| `swift.acceptance:NAME` | 4 | Source, build, pure control, and runner acceptance records |
| `swift.review:NAME` | 8 | Peer and parent review for each acceptance record |
| `swift.runner.source` | 1 | Future native producer runner |
| `swift.runner.contract` | 1 | Future runner wire contract |

The no-child readiness file must measure as:

```text
a49877ffcd8ffcfcbf4adc8c22759daa9c168980c20e62612a5c6fb64651cdc3
```

The loader obtains that value from the file descriptor.
The value above corrects the truncated A04 observation.

### Swift cross-joins

1. The source manifest contains exactly 21 unique file rows.
2. Its producer, control, and source-control compile units name only those rows.
3. Its four semantic caller bindings point to exact filenames.
4. The PNG primary control and duplicate PNG declaration use one exact schema and compile unit.
5. The build helper binds that exact manifest before compilation.
6. The build report, preflight, and seal bind one attempt root and one compiler schedule.
7. Six binary observations and seven log observations match the parent readback.
8. The producer binary is distinct from the PNG and four source-control binaries.
9. The no-child source result keeps process and native execution false.
10. The four-control authorization selects only the four source-control binaries.
11. The four-control report records all four as started, passed, and reaped.
12. The report records the producer and duplicate PNG binary as unexecuted.
13. All thirteen before and after control inputs match.
14. Source, build, and pure-control acceptance records bind their exact aggregates.
15. The future producer runner selects only the producer executable.
16. The future producer runner has its own accepted source and contract.

Swift native authorization remains unavailable until item 16 exists.

## Producer authorizations

Rust and Swift authorizations share one wire shape.
Their qualification types remain distinct.

```rust,ignore
struct ProducerAuthorizationV1 {
    schema: ExactU32<1>,
    operation: ExactString<"native_text_producer_attempt">,
    state: ExactString<"authorized_not_started">,
    implementation: ProducerImplementation,
    repetition: Repetition,
    attempt_id: AttemptId,
    qualification_role_index: ArtifactRef,
    qualification_aggregate: Sha256,
    executable: ArtifactRef,
    command: ClosedCommand,
    environment: ClosedEnvironment,
    process: ProcessPolicy,
    output: ProducerOutputPolicy,
    cancellation: CancellationPolicy,
    native_result_accepted: ExactBool<false>,
    product_integration_allowed: ExactBool<false>,
}
```

The attempt identifier is domain-separated from:

- the qualification aggregate;
- implementation;
- repetition;
- resolved output-parent path;
- fresh exclusive run-directory name.

The authorization writer retains the parent directory descriptor.
It creates one authorization file with exclusive descriptor-relative creation.
The maximum authorization size is 4 MiB.

The writer syncs the file.
It makes no parent-directory power-loss durability claim.

## Exact producer commands

### Rust A05

The Rust command has this exact argument order:

```text
RUST_BINARY
--unit-root UNIT_ROOT
--source-root RUST_SOURCE_ROOT
--build-manifest RUST_BUILD_MANIFEST
--output RUN_ROOT/probe-output
--cancel-marker RUN_ROOT/cancel-marker
```

Every path is absolute.
The command accepts no extra argument.

### Swift A15

The future Swift command has this exact argument order:

```text
SWIFT_PRODUCER_BINARY
--cases CASES_JSON
--manifest FONT_MANIFEST_JSON
--authority INPUT_AUTHORITY_JSON
--out RUN_ROOT/probe-output
--source-sha256 PROBE_SWIFT_SHA256
--shared-source-sha256 PNG_CONSUMER_SHARED_SHA256
--image-sha256 SWIFT_PRODUCER_BINARY_SHA256
--cancel-file RUN_ROOT/cancel-marker
```

The three hashes come from measured accepted role rows.
The caller cannot supply them independently.

### Native producer process policy

Both native producers use this exact environment:

```json
{
  "LANG": "C",
  "LC_ALL": "C",
  "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
  "TZ": "UTC"
}
```

The working directory is the resolved bounded unit root.
Standard input is `/dev/null`.
Standard output and standard error merge into one pipe.
The runner drains that pipe while the child runs.

All unrelated file descriptors close before execution.
The runner creates a new session before executing the child.
The recorded process-group identifier must equal the direct child's PID.

The runner never invokes a shell.
It executes the measured Mach-O path directly.

## Producer output policy

The runner creates one fresh run directory with mode `0700`.
It retains that directory descriptor until terminal publication ends.

Before launch, these entries must be absent:

- `producer.log`;
- `probe-output`;
- `cancel-marker`;
- `report.json`;
- `report-failure.json`.

The runner creates `producer.log` exclusively.
The child creates only `probe-output` contents.

After closure, the run root may contain:

- `producer.log`;
- `probe-output/`;
- optional zero-byte `cancel-marker`;
- exactly one of `report.json` or `report-failure.json`.

No other run-root entry is valid.

| Limit | Rust A05 | Swift A15 |
| --- | ---: | ---: |
| Wall time | 300 seconds | 300 seconds |
| Merged child log | 4 MiB | 4 MiB |
| Child-output bytes | 256 MiB | 512 MiB |
| Child-output regular files | 2,048 | 512 |
| Child-output directories | 512 | 512 |
| Child-output total entries | 2,560 | 1,024 |
| Directory depth | 64 | 64 |
| Relative-path bytes | 4,096 | 4,096 |
| Terminal report | 16 MiB | 16 MiB |
| Causal fallback | 64 KiB | 64 KiB |
| Run-root entries | 4 | 4 |
| TERM grace | 2 seconds | 2 seconds |
| Direct-child reap wait | 1 second | 1 second |

The child-output totals exclude runner-owned log and terminal files.
Those files have their own bounds in the table.

Traversal is descriptor-relative and does not follow links.
It rejects devices, sockets, links, and other non-regular entries.

The runner records every output file's path bytes, size, hash, and stable identity.
It rechecks the output root before and after traversal.

## Closed producer results

Only the runner can construct a typed closed run.

```rust,ignore
struct ClosedProducerRun<I, R> {
    authorization: ArtifactRef,
    authorization_sha256: Sha256,
    qualification_aggregate: Sha256,
    implementation: I,
    repetition: R,
    process: ClosedProcess,
    output_inventory: ClosedInventory,
    terminal_report: ArtifactRef,
    authority_before: Sha256,
    authority_after: Sha256,
    completion: ProducerCompletion,
    native_result_accepted: ExactBool<false>,
}
```

`ProducerCompletion` distinguishes completed, cancelled, timed out, overflowed, failed, and terminal-publication failure.

A zero exit means only `completed_external_qualification_pending`.
It does not mean native acceptance.

## Observer qualification variants

Observer source and runtime authority are separate from producer authority.

```rust,ignore
enum AcceptedObserverVariant {
    RustOrientationV1(Accepted<RustObserverQualificationV1>),
    SwiftOrientationV1(Accepted<SwiftObserverQualificationV1>),
}
```

Neither variant exists as an accepted value today.
The enum shape reserves two explicit implementations without accepting their bytes.

Each observer role schema contains:

| Role family | Cardinality |
| --- | ---: |
| `observer.source.manifest` | 1 |
| `observer.source.file:NNNN` | exact manifest count |
| `observer.source.closure` | 1 |
| `observer.runtime.binding` | 1 |
| `observer.runtime.closure` | 1 |
| `observer.runtime.python` | 1 |
| `observer.runtime.package:NAME` | exact closure set |
| `observer.runtime.file:NNNN` | exact closure set |
| `observer.output_schema` | 1 |
| `observer.policy` | 1 |
| `observer.acceptance:NAME` | 3: source, runtime, runner |
| `observer.review:NAME` | 6: peer and parent review for each acceptance |

The source successor must close the A03 pathname-label and provenance findings.
The runtime successor must replace the stale Python executable observation.

The acceptance record must state these exact facts:

- path identity established by the observer;
- producer-binary execution established elsewhere;
- exclusive producer run established elsewhere;
- source lifetime not established by the observer;
- native result acceptance remains external.

### Observer authorization

An observer authorization combines one accepted observer variant with one typed closed producer run.

It cross-joins:

1. producer implementation;
2. repetition;
3. producer authorization hash;
4. producer executable identity;
5. producer terminal report;
6. producer output inventory;
7. orientation sidecar;
8. exact three orientation artifact descriptors;
9. observer source and runtime aggregates.

The orientation sidecar must bind that same producer run.
It cannot be supplied as an unrelated artifact.

### Exact observer command

The command is:

```text
PYTHON_EXECUTABLE
-I
-B
OBSERVER_SOURCE
--producer-run PRODUCER_SIDECAR
--runtime-binding OBSERVER_RUNTIME_BINDING
--report RUN_ROOT/report.json
--actual-proof
```

The interpreter, source, sidecar, and runtime binding come from accepted rows.
The caller cannot add arguments.

The working directory is the fresh observer run root.
Standard input is `/dev/null`.
Standard output and standard error use separate drained pipes.

The environment is the same four-entry closed environment used by native producers.
`-I` and `-B` remain part of the accepted command.

The runner creates a new session and records its process group.

### Observer output policy

The observer may create no subdirectory.
The runner owns all output files.

The final root contains:

- `stdout.log` up to 64 KiB;
- `stderr.log` up to 64 KiB;
- exactly one of `report.json` up to 1 MiB or `report-failure.json` up to 64 KiB;
- optional zero-byte `cancel-marker`.

The maximum regular-file count is four.
The maximum directory count is zero.
The maximum entry count is four.

The observer reads, but cannot mutate, producer evidence.
Every producer input rehashes after observer closure.

## Comparator remains nonconstructible

A05 does not define `ComparatorQualificationA11` or `ComparatorQualificationA12`.
It defines only the requirements for a future source change.

```rust,ignore
trait AcceptedComparatorSpec: private::Sealed {
    type ProducerReport;
    type ObserverReport;

    fn exact_role_schema() -> &'static ComparatorRoleSchema;
    fn exact_command() -> &'static CommandSchema;
    fn exact_output_policy() -> &'static OutputPolicy;
}
```

No type implements this trait in A05.
The serializer has no comparator schema tag.

A future accepted version must add one explicit implementation.
It must not discover a version from a path or manifest field.

The future comparator qualification must include:

- exact package manifest and every source row;
- exact main source and output schema;
- required-evidence control source and result;
- actual-validator control source and result;
- runtime and source closures for both controls;
- control authorizations, logs, seals, and parent readbacks;
- source, control-source, and result acceptance records;
- the exact Swift and Rust report schemas it accepts;
- one final root acceptance record.

The required control must preserve its full case schedule.
The actual control must invoke the real accepted comparator functions.

The future accepted variant must reconstruct all role rows independently.
It must bind producer and observer reports by implementation and repetition.

No A11 role, hash, or manifest row can qualify a later version by inheritance.
No A12 file can qualify before its exact acceptance records exist.

## Comparator and control process policy

This policy is inert until an accepted comparator variant implements it.

Each Python command must use:

- one accepted absolute Python executable;
- `-I` and `-B`;
- one accepted absolute source path;
- an exact closed argument vector;
- the four-entry closed environment;
- a fresh stage-owned working directory;
- `/dev/null` standard input;
- separate drained standard output and standard error;
- a new session with recorded process group.

No shell or environment-based module path is allowed.

### Required-control output limits

| Output | Bound |
| --- | ---: |
| Stdout | 64 KiB |
| Stderr | 128 KiB |
| Result | 1 MiB |
| Failure result | 64 KiB |
| Seal | 128 KiB |
| Regular files | 5 |
| Directories | 0 |
| Entries | 5 |
| Wall time | 60 seconds |

### Actual-control output limits

| Output | Bound |
| --- | ---: |
| Stdout | 4 MiB |
| Stderr | 128 KiB |
| Result | 4 MiB |
| Failure result | 64 KiB |
| Seal | 128 KiB |
| Regular files | 5 |
| Directories | 0 |
| Entries | 5 |
| Wall time | 120 seconds |

The allowed files are stdout, stderr, one result, one seal, and an optional cancellation marker.

### Comparator output limits

| Limit | Bound |
| --- | ---: |
| Stdout | 4 MiB |
| Stderr | 128 KiB |
| Result | 4 MiB |
| Failure result | 64 KiB |
| Regular files | 4 |
| Directories | 0 |
| Entries | 4 |
| Wall time | 300 seconds |
| Producer reports | exactly 4 |
| Observer reports | exactly 4 |
| Report bytes each | 4 MiB |
| Rust stored evidence per run | 256 MiB |
| Swift stored evidence per run | version-specific accepted bound |
| Decoded evidence per run | 512 MiB |
| Evidence files per run | 512 |
| Retained differences | 2,048 |
| Cases | exact accepted schedule |
| Repeats per case | exact accepted schedule |

The output files are stdout, stderr, one result or failure result, and an optional cancellation marker.

These are logical evidence limits.
They are not RSS, allocator, framework-memory, or power-loss guarantees.

## Cancellation and process closure

Every stage uses the same process lifecycle.

1. Create the fresh output root and retain its descriptor.
2. Reconstruct and recheck the stage role index.
3. Create the authorization and logs exclusively.
4. Launch the direct child in a new session.
5. Drain every pipe while the child runs.
6. On cancellation, create a zero-byte marker exclusively.
7. Send `SIGTERM` to the recorded process group.
8. Wait at most two seconds.
9. Send `SIGKILL` to the same process group when needed.
10. Wait at most one second for the direct child.
11. Inventory bounded outputs.
12. Reconstruct and recheck the stage role index.
13. Save one terminal report or bounded causal fallback.

Timeout, log overflow, inventory overflow, signal failure, or reap failure closes the stage as failed.

The runner records direct-child and process-group delivery separately.
It does not claim to reap escaped descendants.

A cancelled stage cannot publish a passed closed result.
A later stage accepts only the typed completed state required by its contract.

## Error model

```rust,ignore
enum PreparationError {
    MissingAcceptance { subject: AcceptedSubjectKind },
    RejectedVersion { subject: AcceptedSubjectKind, version: String },
    RoleSchemaMismatch { expected: ClosedRoleSchema },
    ArtifactDrift { role: ClosedRole },
    ManifestJoin { role: ClosedRole, relation: ClosedRelation },
    AcceptanceJoin { subject: AcceptedSubjectKind },
    AuthorizationExists { attempt: AttemptId },
    OutputRootExists { attempt: AttemptId },
}

enum RunFailure {
    Launch,
    Cancelled,
    Timeout,
    LogOverflow,
    OutputOverflow,
    InvalidEntry,
    NonzeroExit,
    AuthorityDrift,
    TerminalPublication,
    ReapFailure,
}
```

Every error code is closed and bounded.
Arbitrary `Display` output does not enter a gate or terminal report.

## Module map

| Future module | Ownership |
| --- | --- |
| `artifact_observation` | One-descriptor reads, stable identity, bounded hashing, and Mach-O UUID parsing. |
| `role_index_v1` | Closed roles, exact binary encoding, sorting, duplicate checks, and aggregate. |
| `acceptance_v1` | Strict acceptance-record parsing and private `Accepted<T>` construction. |
| `rust_qualification_v1` | Rust manifest expansion, cross-joins, and Rust-only final role index. |
| `swift_qualification_v1` | Swift manifest expansion, build and pure-control joins, and runner prerequisite. |
| `producer_authorization_v1` | Stage-local authorization serialization and exclusive publication. |
| `producer_runner_rust_v1` | Exact Rust command, process lifecycle, inventory, and closed-run result. |
| `producer_runner_swift_v1` | Exact Swift command, process lifecycle, inventory, and closed-run result. |
| `observer_qualification_v1` | Versioned source and runtime closure with explicit provenance facts. |
| `observer_runner_v1` | Exact Python command, bounded output, and typed observation result. |
| `comparator_pending` | Uninhabited accepted variant and diagnostic missing-evidence state. |
| `stage_output` | Descriptor-owned roots, exclusive files, caps, cancellation marker, and cleanup policy. |

The public surface is stage-specific.
Callers do not choose role names, hashes, commands, environments, or limits.

## Verification plan for a later implementation

### Pure role-index controls

1. Reorder two rows and require rejection.
2. Duplicate one role and require rejection.
3. Reuse one path with conflicting identity and require rejection.
4. Change one path byte and require a new aggregate.
5. Change one timestamp field and require a new aggregate.
6. Add one unknown Mach-O tag and require rejection.
7. Round-trip the exact binary encoding across two independent implementations.

### Acceptance controls

1. Replace the subject aggregate and require rejection.
2. Replace either review descriptor and require rejection.
3. Use a provisional disposition and require rejection.
4. Add an unknown JSON key and require rejection.
5. Duplicate a JSON key and require rejection.
6. Attempt caller construction of `Accepted<T>` and require a compile-time failure.

### Rust qualification controls

1. Remove one source row.
2. Add one dependency file.
3. Swap one package archive.
4. Change one source-gate binding.
5. Change the binary while retaining the old UUID.
6. Change the binary UUID while retaining the old hash field.
7. Replace one font, license, case, or control artifact.
8. Add one observer, comparator, or Swift role and require rejection.

### Swift qualification controls

1. Change one of the 21 source rows.
2. Change a caller-binding filename.
3. Change one compile-unit order.
4. Swap the producer and PNG binary roles.
5. Omit one pure-control stream.
6. Mark the producer as executed in the pure-control report.
7. Use the truncated no-child readiness hash and require rejection.
8. Omit the future native-runner acceptance and require no authorization.

### Stage controls

1. Attempt Rust authorization while Swift, observer, and comparator evidence is absent.
2. Require that Rust authorization succeeds only when Rust evidence is complete.
3. Attempt Swift authorization without its runner acceptance and require rejection.
4. Attempt observer authorization with a run from the wrong implementation or repetition.
5. Attempt comparator serialization and require that no schema tag exists.
6. Overflow each log and output limit.
7. Substitute the output directory during a run and require failure.
8. Cancel each stage while the direct child owns its process group.

These are future controls.
No control ran while authoring A05.

## Rationale

### Synthesis decision

A05 replaces one whole-pipeline preparation with four stage-owned qualifications.
The Rust producer becomes the first independent unit.

The role-index moves from unspecified canonical JSON to one exact binary encoding.
Acceptance moves from a caller enum to a machine-readable root record.

Observer authority becomes a versioned qualification.
Comparator authority remains uninhabited until one exact successor qualifies.

### Why the comparator is not generically versioned

A generic version string would move authority back to the caller.
A directory suffix would permit silent source upgrades.

The closed variant requires a source change for every accepted comparator.
That source change exposes the exact schema, controls, and limits to review.

### Why manifests still drive row expansion

Thousands of dependency rows cannot be copied safely into prose.
The versioned adapter defines the manifest field, sorting rule, cardinality, and cross-joins.

The acceptance record binds the measured aggregate.
Any byte or count change invalidates that acceptance.

### Red-flag screen

No public call forwards an untyped file list.
No caller supplies a hash, command, role, environment, or limit.

Qualification modules hide large evidence graphs behind one accepted type.
Stage modules own distinct authority and failure policy.

The design has no load-validate-save wrapper chain.
Each boundary either qualifies evidence, grants one process, or closes one process result.

## Current evidence boundary

The Rust and Swift source, build, and pure-control artifacts remain saved evidence.
A05 does not reclassify them.

The current Rust runner needs a stage-specific successor.
The current Swift producer runner does not exist as accepted evidence.

The observer needs a refreshed runtime closure and accepted source successor.
The comparator needs an exact accepted successor and actual-function control closure.

The A11 source drift and A12 authoring state cannot enter a role index.

## Next design and implementation units

1. Independently review A05 as design only.
2. Author the strict role-index and acceptance parsers without process execution.
3. Author the Rust-only qualification loader.
4. Author and review the Rust-only runner successor.
5. Generate machine-readable acceptance records after those exact reviews.
6. Author one Rust primary authorization and review it before execution.
7. Keep Swift, observer, and comparator work in separate later units.

## Acceptance boundary

A05 does not authorize native execution.
It does not accept a Rust runner, Swift runner, observer, or comparator.

It does not establish native text feasibility, output correctness, product integration, playback, hearing, lyrics, film quality, or creative acceptance.

All reviews remain same-model-family unless separate evidence states otherwise.
No cross-family review is claimed.
