# Native text preparation next design A04

## Status

This is a design-only successor to Native Run Preparation A03.
A03 and its three source helpers remain byte-for-byte preserved.

No native gate, stage authorization, run directory, helper, control, producer, observer, or comparator was created or executed.
Comparator A11 currently has source bytes only.
Its source reviews, control results, result readbacks, and accepted runtime closure are absent.

## Caller usage first

The future caller supplies accepted qualification envelopes.
It does not supply individual hashes or choose internal role names.

```rust,ignore
let preparation = NativePreparationA04::assemble(
    accepted_rust_a05,
    accepted_swift_a15,
    accepted_comparator_a11,
    accepted_observer_closures,
)?;

// Each call writes one authorization for one stage and one attempt.
let rust_primary = preparation.authorize_producer(ProducerAttempt {
    implementation: ProducerImplementation::RustA05,
    repetition: Repetition::Primary,
})?;

let rust_fresh = preparation.authorize_producer(ProducerAttempt {
    implementation: ProducerImplementation::RustA05,
    repetition: Repetition::Fresh,
})?;

let swift_primary = preparation.authorize_producer(ProducerAttempt {
    implementation: ProducerImplementation::SwiftA15,
    repetition: Repetition::Primary,
})?;

let swift_fresh = preparation.authorize_producer(ProducerAttempt {
    implementation: ProducerImplementation::SwiftA15,
    repetition: Repetition::Fresh,
})?;

let observed = preparation.authorize_observers([
    rust_primary.closed_run(),
    rust_fresh.closed_run(),
    swift_primary.closed_run(),
    swift_fresh.closed_run(),
])?;

let comparison = preparation.authorize_comparator(ComparatorInputs {
    producer_runs: observed.closed_runs(),
    observer_reports: observed.passed_reports(),
})?;
```

These signatures are sketches.
Every body remains `not implemented`.

If one prerequisite is missing, `assemble` returns `IncompletePreparation`.
That value is diagnostic only and cannot serialize an execution authorization.

The first implementation unit should authorize only the two Rust producer attempts.
Swift producer, observer, and comparator authorizations remain separate later units.

## Problem

A03 binds four source-package roles for a versioned comparator.
It omits the control that imports the real comparator.
It also omits that control's result, runtime closure, source closure, and accepted reviews.

The next design must close that proof graph without granting one document authority over every later process.
It must also bind the actual Swift pure-control evidence and its exact compiler build.

Comparator A11 needs four native reports: Rust primary, Rust fresh, Swift primary, and Swift fresh.
The existing Swift runner executed only four pure controls.
It did not execute the Swift producer.

## Shape

### Accepted evidence cannot contain placeholders

```rust,ignore
struct AcceptedArtifact {
    role: ClosedRole,
    path: AbsolutePath,
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

struct AcceptedReviewSet {
    subject: AcceptedArtifact,
    peer_review: AcceptedArtifact,
    parent_review: AcceptedArtifact,
    parent_disposition: AcceptedDisposition,
}

enum AcceptedDisposition {
    AcceptedNoP1OrP2,
}

enum EvidenceSlot<T> {
    Missing { role: ClosedRole, reason: MissingReason },
    Accepted(T),
}

struct IncompletePreparation {
    missing: Vec<MissingEvidence>,
}
```

`EvidenceSlot::Missing` is an in-memory diagnostic.
It never appears in an execution gate.

The gate builder accepts only `AcceptedArtifact` values.
It rejects null hashes, empty review paths, provisional versions, and unreviewed source bytes.

### Comparator source and qualification are separate

```rust,ignore
struct ComparatorSourcePackageA11 {
    package_manifest: AcceptedArtifact,
    comparator_main: AcceptedArtifact,
    required_evidence_control: AcceptedArtifact,
    actual_comparator_control: AcceptedArtifact,
    output_schema: AcceptedArtifact,
    rationale: AcceptedArtifact,
    readme: AcceptedArtifact,
}

struct ComparatorControlRun {
    authorization: AcceptedArtifact,
    report: AcceptedArtifact,
    seal: AcceptedArtifact,
    stdout: AcceptedArtifact,
    stderr: AcceptedArtifact,
    parent_readback_source: AcceptedArtifact,
    parent_readback_result: AcceptedArtifact,
}

struct ComparatorQualificationA11 {
    source: ComparatorSourcePackageA11,
    source_closure: AcceptedArtifact,
    runtime_closure: AcceptedArtifact,
    required_control: ComparatorControlRun,
    actual_control: ComparatorControlRun,
    source_reviews: AcceptedReviewSet,
    control_source_reviews: AcceptedReviewSet,
    control_result_reviews: AcceptedReviewSet,
    root_acceptance: AcceptedArtifact,
}
```

The A11 package manifest owns source identities only.
A separate immutable qualification envelope owns runtime evidence, control results, reviews, and root acceptance.

The native gate flattens both objects into one closed role list.
The runner independently reconstructs that same list.

### Swift qualification binds source, compiler, and actual controls

```rust,ignore
struct SwiftQualificationA15 {
    source_manifest: AcceptedArtifact,
    source_rows: Vec<AcceptedArtifact>,
    build_helper: AcceptedArtifact,
    build_report: AcceptedArtifact,
    build_seal: AcceptedArtifact,
    build_readback_source: AcceptedArtifact,
    build_readback_result: AcceptedArtifact,
    build_reviews: AcceptedReviewSet,
    binaries: [AcceptedArtifact; 6],
    build_logs: [AcceptedArtifact; 7],
    runner_source: AcceptedArtifact,
    runner_contract: AcceptedArtifact,
    runner_reviews: AcceptedReviewSet,
    no_child_control_result: AcceptedArtifact,
    no_child_parent_readback: AcceptedArtifact,
    pure_control_authorization: AcceptedArtifact,
    pure_control_report: AcceptedArtifact,
    pure_control_seal: AcceptedArtifact,
    pure_control_streams: [AcceptedArtifact; 8],
    pure_readback_source: AcceptedArtifact,
    pure_readback_result: AcceptedArtifact,
    pure_result_reviews: AcceptedReviewSet,
}
```

The type distinguishes compiler evidence from process evidence.
The compiler build proves six recorded Mach-O files exist.
The pure-control run proves only four source-control binaries ran.

The Swift producer binary remains unexecuted.
The duplicate PNG binary remains unexecuted.

### One deterministic role index

Each accepted envelope expands into `AcceptedArtifact` rows.
Rows are sorted by semantic role, then canonical path.

The role aggregate is:

```text
SHA-256(
  "native-text-preparation-a04-role-index\0" ||
  canonical-json(role rows)
)
```

Two roles may name one file.
Their path, bytes, SHA-256, and identity must be identical.

One path cannot carry conflicting observations.
An extra, missing, renamed, or duplicated semantic role rejects preparation before any authorization file is created.

### Stage authorizations remain separate

```rust,ignore
enum ProducerImplementation {
    RustA05,
    SwiftA15,
}

enum Repetition {
    Primary,
    Fresh,
}

struct ProducerAuthorization {
    schema: ProducerAuthorizationSchema,
    attempt: ProducerAttempt,
    executable: AcceptedArtifact,
    prerequisites_aggregate: Sha256,
    environment: ClosedEnvironment,
    limits: ProducerLimits,
    authorized_stage: ProducerStageOnly,
}

struct ObserverAuthorization {
    schema: ObserverAuthorizationSchema,
    closed_run: AcceptedArtifact,
    sidecar: AcceptedArtifact,
    observer_source: AcceptedArtifact,
    observer_runtime: AcceptedArtifact,
    limits: ObserverLimits,
    authorized_stage: ObserverStageOnly,
}

struct ComparatorAuthorization {
    schema: ComparatorAuthorizationSchema,
    qualification: ComparatorQualificationA11,
    producer_reports: [AcceptedArtifact; 4],
    observer_reports: [AcceptedArtifact; 4],
    limits: ComparatorLimits,
    authorized_stage: ComparatorStageOnly,
}
```

One authorization launches one direct child.
It cannot authorize a later stage.

The comparator authorization requires four closed producer reports and four passed observer reports.
It also requires the accepted A11 actual-control result.

## Comparator A11 bindings

### Current source observations are pending

The current A11 source package is authored and unqualified.
These identities are observations, not accepted gate rows:

| Role | Current SHA-256 |
| --- | --- |
| Package manifest | `d95e76834d427d8b44000cc35995808d975a0be8273fadcd8658de18bd824872` |
| Comparator main | `e94b6ea3fb671ba66d413594060959bb5ec86f7e4fcffb8e774ababaeb438520` |
| Actual-comparator control | `3e1d293a57e1b617f39702d4d599f8520f6828860daba3fe59cd781f0b7c49a2` |
| Required-evidence control | `69c8c96d60b7b8842d6e5f55a564ea23e6853d66c8d06b006e9738e203be809c` |
| README | `1eb295208fd4cbc65215e796cedefa32261edb227427951cb7aaf6ad08441555` |
| Output schema | `a44039d6b8d58275a27304dc3d1fd542df37e2e66092b8ffed69fa712e021312` |
| Source rationale | `5fcce694107fe8ff0857d6997ebc5c0b3f349fb7a9a96ad93f416fe66f49f06d` |

The package manifest reports `authored_unbuilt_unexecuted_unqualified`.
That state cannot satisfy `ComparatorQualificationA11`.

If review changes one byte, the final qualification must bind the reviewed successor identity.
It must not silently reuse this table.

### Required accepted A11 roles

The qualification envelope must contain these semantic roles:

1. `comparator.package_manifest`
2. `comparator.main_source`
3. `comparator.output_schema`
4. `comparator.source_rationale`
5. `comparator.readme`
6. `comparator.required_control_source`
7. `comparator.actual_control_source`
8. `comparator.source_closure`
9. `comparator.runtime_closure`
10. `comparator.source_peer_review`
11. `comparator.source_parent_review`
12. `comparator.control_peer_review`
13. `comparator.control_parent_review`
14. `comparator.required_control_authorization`
15. `comparator.required_control_report`
16. `comparator.required_control_seal`
17. `comparator.required_control_stdout`
18. `comparator.required_control_stderr`
19. `comparator.required_control_readback_source`
20. `comparator.required_control_readback_result`
21. `comparator.actual_control_authorization`
22. `comparator.actual_control_report`
23. `comparator.actual_control_seal`
24. `comparator.actual_control_stdout`
25. `comparator.actual_control_stderr`
26. `comparator.actual_control_readback_source`
27. `comparator.actual_control_readback_result`
28. `comparator.result_peer_review`
29. `comparator.result_parent_review`
30. `comparator.root_acceptance`

The actual-control report must state the exact loaded comparator source hash.
Its closure must bind the same package manifest and interpreter.

The required-evidence control may remain independent of the comparator implementation.
Its report must preserve the exact fifteen-case schedule.

The actual control must call the real A11 validators.
It must cover the four A10 review defects and their boundary controls.

The actual control must include these decisive observations:

- current allocation above 256 MiB and below 512 MiB;
- Rust stored evidence at 256 MiB and one byte over;
- Swift stored evidence at 396,071,265 bytes and one byte over;
- accepted, exact-zero, observation-only, expected-rejection, and outer-failure states;
- failed prefixes after zero, one, and two completed repeats;
- partial fractional-control prefixes;
- actual reservation-table peak bindings;
- unchanged decoded content at different paths and changed decoded hash.

## Accepted Swift evidence bindings

### Source and build chain

These accepted identities are inputs to the successor design:

| Role | SHA-256 |
| --- | --- |
| Swift A15 source manifest | `0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e` |
| Build helper A04 | `ba632ed73005d8c3f870d4b7886c3057ae80405071c4f2154469fe090c195886` |
| Build-helper peer review | `890665f27625de3ef77a71841a60ec026c5fc21ccfb72f58f1b80f43ab20ddd7` |
| Build-helper parent review | `6156b2de60feea48879ae25329e643a9324821522fe063fc5a3f3f77e8763d21` |
| Build preflight A02 | `5f4f3c0a1e1ea417e969e4aeff8770a96e8616ce46c4961cbff440e8294f9d92` |
| Build report A02 | `214864e3d4bc7af8e7698dc3c6ad78f409147a5fffaeabfc8c9898c356fcc3ea` |
| Build seal A02 | `23cd14ae2a46f5990831cb34e7de9b2dfa959cd642d3aec81381d804c63a97ae` |
| Build readback source | `d4c89a176660127e68d0113c0b0582f702a13cf3380bc9e05ed5de466c44df29` |
| Build parent readback | `cfc3aa29d7825a1d4d843a297df55e95651dcc0eef76cbbf94f0528f62a2f63a` |
| Build readback peer review | `fdd6580c2528c0aee4e5f19a7b9085ee7e6c1be01dd79b1e4a0129b6360052d9` |
| Build parent acceptance | `77e13e9677ab1758d3eefca1b94cc3d6645033f4a2c5334a29a619a45962d095` |

The gate expands all 21 manifest source rows.
It also expands the six binaries and seven build logs from the accepted readback.

### Exact compiler outputs

| Binary | Bytes | SHA-256 | Mach-O UUID |
| --- | ---: | --- | --- |
| `producer` | 2,570,328 | `73a690570b65fa9ae035646ef9602f03e93b5eabf90cff14361d490a1359e99f` | `3d73f2c916343502b0c8d4a894d6f21a` |
| `png-control` | 188,888 | `fc4a2cbedd011fb7f516062f08bd06460eb729891f794287eb4d0116f036b274` | `d944eaffdee13c44baf52c68e62f09f6` |
| `source-control-00` | 188,896 | `cfdaa2b417e4245bedadaa12132a53b676c7f6e53743f0d02cf616e0db2eec6a` | `e14c85e70d7c30acbfcaffe76ca66fb5` |
| `source-control-01` | 120,576 | `e216fa4a50549948efaf24f472c5df88ae3a5d964add9c8590b39bd86afd814b` | `8c30f8ceacf53343975910f4960fccff` |
| `source-control-02` | 161,536 | `e0bd48b727f7d05cae75c15d9692d13889fc39e1ec50f897e60b22a4044dc901` | `19f942d2c14b36709f988847096d4521` |
| `source-control-03` | 161,120 | `5a6f9152426c8140e20a4ef52ee44dd7066207c0ce6c8b7f9d0b28f5651bd826` | `34b6291c96b03603b2b15bcf9927c263` |

The compiler-version log is 129 bytes with SHA-256
`0e1b0165906a3b7b60a5655fcc54daf66e40a344996365578f689045679470e8`.

The producer log is 535 bytes with SHA-256
`5a86cfe69fc22805843edc97e87e7049b64b42b9004ddfb6b0836488d52fd719`.

The PNG and four source-control build logs are empty.
Their SHA-256 is
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

### Runner and source-control qualification

| Role | SHA-256 |
| --- | --- |
| Runner A03 | `d0d89138412caa6760a72ceb41bea24d61ca2b5a74eb9dc00e83b8eadc3e990c` |
| Runner wire schema A03 | `8882a32a98742b8275c84bcbeab37de40ca5268467e603d2c2a7f00d7d59b791` |
| Runner rationale A03 | `43cd99304f3b1c3ccab984c80bd83fb231679e1620777b9dbefa5319b02d3560` |
| Runner peer source review | `64759569592acaec3957426d9a3ac9321e948fef4f76e8c6ba9f73add2788a00` |
| Runner parent source review | `9e7af49c074cc65495c6896e7b01ebfa80be8bb216033435e1f88064e536be99` |
| No-child controls A04 | `9f6c3391c6bb2717a92049749959c77525627308bd80a9343bedd161d4f02028` |
| No-child rationale A04 | `7c3b898522627472361e6657e28ee9c5360430c216c8f848226fff503c8ebce3` |
| No-child peer review | `c1c5be61b5d27f994eead56ad63c29221f39a7ccf5bd7fd7837f749a1e195c40` |
| No-child parent review | `48d70f74a642aaa447dcb1baeb847f5e0256b63d05e0f4be520043c74e9f8222` |
| No-child readiness A04 | `a49877ffcd8ffcfb4adc8c22759daa9c168980c20e62612a5c6fb64651cdc3` |
| No-child result A04 | `3bc886782705a3402ba22537752bb7495d692185a9fd2ac72e0e494941ee6110` |
| No-child parent readback A04 | `f6e7f8abfb0c1b7bd5d2144a3cf9165e34478ab0f3d736e7df1f59c57f595711` |

### Actual four-control result

| Role | SHA-256 |
| --- | --- |
| Authorization | `4d271cab075562b761653b3497311cd74defc3fbe515cd79253d1d4b4bd11125` |
| Preflight | `1a1be83109b2caf9be8fff24ee9b6b2a0d06be5f1025095852e5026555f87786` |
| Report | `43a58d030bc7d4f2d6ddb799871472517e68bece09f70b675bd8e1f0f07c6632` |
| Publication seal | `b6e7ab47467e1dca3243e0ac096176e93f6230025a7778663daf62d91b10dcad` |
| Parent readback source | `4a4775efa0274198e3483416a31e358860826bac3f49d44533970850c97ed40d` |
| Parent readback result | `7f7312a84190033b7e76743b28dee9c550b04bff9b1f20622613d23ff568a10d` |
| Peer readback review | `c34e8031a3ddf52eea6e0d0399e65bb6ef376a33096092b9ef06e0ec27ce6cab` |
| Parent acceptance | `08a311b2de7b9ecf67d3085bfe90512f079091fc6e5eef872b8077c8d8e09fcd` |

The four stdout hashes are:

```text
7b61b70a43a960a538bdb8aa47df378dce3120a299ddebe07ed1d4c53e3cb5e8
02c02b020fb10d99eb9ef90a5ede50e801c9881939f405047f798a4545393e37
b9d1e0aac2bc30620fce5b7e32ab3cd34be47147abb60e7bc81048d848eac210
7d8c86443de1344c7ca59f62ec1f00e57b3ab9d884bf46d19dcd33a6d2bbcb56
```

All four stderr streams are empty.
The gate binds each stream as a distinct role despite their shared digest.

## Required cross-joins

The successor preparation validates these relationships before creating any stage authorization:

1. The A11 manifest's Swift authority equals the accepted A15 manifest, producer source, shared callback source, and C bridge.
2. The A11 package rows equal the exact reviewed source files.
3. The actual control's embedded comparator hash equals the accepted main source hash.
4. The actual control result records that same loaded source hash and package manifest.
5. The actual and required control results bind one accepted interpreter and runtime closure.
6. Both control result readbacks reobserve every source, result, log, and runtime file.
7. A11 source and control reviews name those exact identities.
8. Root acceptance names both result readbacks and both review sets.
9. Swift build rows equal the accepted A15 source manifest and compile-unit schedules.
10. The four executed control binaries equal `source-control-00` through `source-control-03` from build A02.
11. Each control report binding equals its build binary observation and source compile units.
12. The actual control report, seal, stdout, stderr, and parent readback form one exact join.
13. The Swift pure-control report records the producer and duplicate PNG binary as unexecuted.
14. The future Swift producer authorization selects only the exact `producer` binary.
15. The future Swift producer authorization cannot select `png-control` or a source-control binary.
16. Rust A05 source, lock, dependency closure, build manifest, executable, and reviews retain every A03 join.
17. Every producer attempt uses a fresh output root and a unique attempt identity.
18. Every observer authorization names exactly one closed producer attempt.
19. Comparator authorization names all four producer reports and all four observer reports.
20. Comparator output records the exact four report identities and the A11 qualification aggregate.

## Stage authorization and limits

### Producer stage

The producer stage has four separate attempts.
Each attempt authorizes one direct child and one exact executable.

The child environment is exactly:

```json
{
  "LANG": "C",
  "LC_ALL": "C",
  "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
  "TZ": "UTC"
}
```

| Limit | Rust A05 | Swift A15 |
| --- | ---: | ---: |
| Wall time | 300 seconds | 300 seconds |
| Merged stdout/stderr | 4 MiB | 4 MiB |
| Output bytes | 256 MiB | 512 MiB |
| Regular output files | 2,048 | 512 |
| Output directories | 512 | 512 |
| Total output entries | 2,560 | 1,024 |
| Terminal attempt report | 16 MiB | 16 MiB |
| Causal fallback | 64 KiB | 64 KiB |
| Direct-child reap wait | 1 second | 1 second |
| TERM-to-KILL grace | 2 seconds | 2 seconds |

The Swift successful qualification schedule currently declares 201 files.
The 512-file external cap leaves bounded failure residue while matching the comparator's evidence-file cap.

The Rust runner retains A03's descriptor-relative traversal and exclusive publication rules.
A future Swift native runner must implement the same ownership guarantees before review.

Timeout, cancellation, log overflow, inventory overflow, or reap failure closes the attempt as failed.
No later stage may reinterpret such an attempt as a successful producer run.

### Observer stage

One observer authorization reads one sealed producer attempt.
It does not launch a producer or comparator.

| Limit | Bound |
| --- | ---: |
| Wall time | 60 seconds |
| Stdout | 64 KiB |
| Stderr | 64 KiB |
| Observer report | 1 MiB |
| Failure report | 64 KiB |
| Producer sidecar | 128 KiB |
| Producer source or closure document | 16 MiB each |
| Producer executable | 128 MiB |
| Observer runtime executable | 256 MiB |
| Native orientation PNG | 1 MiB |
| Raw alpha | exactly 272 bytes |
| Canonical alpha | exactly 221 bytes |
| Direct-child reap wait | 1 second |
| TERM-to-KILL grace | 2 seconds |

The existing observer runtime binding records an older Python executable hash.
It cannot authorize the next observer stage.

The observer needs a refreshed runtime closure and accepted source successor.
The source successor must close the pathname-label and provenance findings from the A03 observer review.

Rust and Swift observer sources may differ.
Each source must still emit the same closed orientation observation contract.

### Comparator qualification controls

The required-evidence and actual-comparator controls run before any comparator authorization.

| Limit | Required control | Actual control |
| --- | ---: | ---: |
| Wall time | 60 seconds | 120 seconds |
| Stdout | 64 KiB | 4 MiB |
| Stderr | 128 KiB | 128 KiB |
| Result report | 1 MiB | 4 MiB |
| Direct-child reap wait | 1 second | 1 second |
| TERM-to-KILL grace | 2 seconds | 2 seconds |

These are pure control limits.
They do not authorize native producers or native frameworks.

### Comparator stage

The comparator stage launches one exact accepted A11 main source with one exact interpreter.
It receives four closed producer reports and four passed observer reports.

| Limit | Bound |
| --- | ---: |
| Wall time | 300 seconds |
| Stdout | 4 MiB |
| Stderr | 128 KiB |
| Each producer report | 4 MiB |
| Comparator output | 4 MiB |
| Rust stored evidence per run | 256 MiB |
| Swift stored evidence per run | 396,071,265 bytes |
| Decoded evidence per run | 512 MiB |
| Evidence files per run | 512 |
| Retained differences | 2,048 |
| Cases | 15 |
| Repeats per case | 3 |
| String field | 64 KiB |
| Path field | 4,096 bytes |
| Direct-child reap wait | 1 second |
| TERM-to-KILL grace | 2 seconds |

These are logical file and decoded-byte admissions.
They are not process RSS, allocator, or framework-memory measurements.

The comparator creates one output exclusively.
It preserves a bounded failure result when possible.
It cannot mutate producer or observer evidence.

## Ownership and cancellation

Each stage runner owns its fresh output directory and retains that directory descriptor.
It opens authority inputs before launch and rechecks them after child closure.

The runner drains child pipes while the child runs.
It never waits for process exit before servicing full pipes.

Cancellation writes only the stage-owned cancellation marker.
The runner sends `SIGTERM`, waits two seconds, sends `SIGKILL`, and performs a one-second direct-child reap.

The runner records process-group delivery separately from direct-child delivery.
It keeps descendant-reaping attestation false.

A cancelled or timed-out stage cannot publish a passed authorization result.
Partial outputs remain causal evidence under the stage's byte and entry caps.

## Module map for a later implementation

| Future module | Ownership |
| --- | --- |
| `native_preparation_a04` | Parse accepted envelopes, expand roles, validate joins, and materialize producer authorizations. |
| `comparator_qualification_a11` | Validate the A11 source package, controls, runtime closure, reviews, and root acceptance. |
| `swift_qualification_a15` | Validate the A15 manifest, exact compiler build, pure-control execution, readbacks, and reviews. |
| `producer_runner_rust` | Preserve the A03 Rust process, output, and publication policy. |
| `producer_runner_swift` | Run only the exact Swift producer with equivalent ownership and bounded publication. |
| `observer_authorization` | Bind one closed producer attempt to one reviewed observer and runtime. |
| `comparator_authorization` | Bind four closed runs, four observer results, and accepted A11 qualification. |
| `role_index` | Canonicalize semantic rows and compute the domain-separated aggregate. |

Callers see `assemble`, `authorize_producer`, `authorize_observers`, and `authorize_comparator`.
The modules hide role expansion, manifest parsing, cross-joins, and descriptor policy.

## Rationale

### Synthesis decision

The design retains A03's closed role index and per-file rechecks.
It adds one comparator qualification envelope and separate stage authorizations.

This closes the parent review's exact defect.
It avoids turning one source-package manifest into proof of control execution.

### Tradeoffs accepted

- We accept more bound artifacts in exchange for reproducible actual-validator evidence.
- We accept separate stage gates in exchange for narrow execution authority.
- We accept exact A11 coupling in exchange for rejecting silent comparator upgrades.
- We accept repeated closure observations in exchange for clear before-and-after ownership.
- We accept a refreshed observer closure in exchange for rejecting the stale interpreter identity.

### Alternatives considered

**Add two comparator paths to A03.**
This still leaves control results, runtime closure, reviews, and root acceptance outside the gate.

**Trust the A11 package manifest.**
The manifest owns source bytes only.
It cannot prove either control ran or passed.

**Use one omnibus authorization for every stage.**
That document could launch future processes before their inputs exist.
It would also mix producer ownership with observer and comparator policy.

**Run the comparator controls inside the native gate builder.**
Gate preparation would then execute code while deciding whether execution is allowed.
That collapses review and authorization into one step.

### Red-flag screen

The caller surface remains four operations.
Role and schema details stay inside deep qualification modules.

The design does not expose package wire records as public caller types.
It parses them into accepted domain values.

Stage modules exist because they own different authority and output policies.
They are not load, validate, and save wrappers around one shared record.

No module forwards an unchanged argument list to another module.
Every boundary adds qualification, ownership, or execution policy.

## Open questions and risks

1. Will A11 source review accept the currently observed seven source files unchanged?
2. What exact filenames and schemas will the two accepted A11 control result packages use?
3. Will the actual-control runtime closure use the current `4158f03e...` Python executable?
4. Which reviewed Swift native runner will execute the exact A15 producer binary twice?
5. Which Swift observer source will establish orientation without reusing Rust-only sidecar assumptions?
6. Do 512 Swift output files and 512 directories admit every causal failure path?
7. Will the observer successor close both remaining A03 provenance findings before execution?
8. Can a later reviewer provide independent-source-origin evidence, or only another same-family review?

These questions block the affected authorization only.
They do not weaken the preserved A03 source or accepted Swift pure-control evidence.

## Next implementation step

After A11 source and controls receive accepted exact evidence, author the qualification-envelope validator before changing any producer runner.

## Acceptance boundary

This design does not authorize native execution.
It does not accept Comparator A11, the observer, or the Swift producer.

The actual Swift controls are prerequisite evidence only.
Their `nativeCalls` and `imageIOUsed` fields are source-defined observations.

The reviews remain same-family and nonblind unless later evidence says otherwise.
This design does not claim full independent-source-origin qualification.

Native text feasibility, integration, playback, hearing, lyrics, film quality, and creative acceptance remain unverified.
