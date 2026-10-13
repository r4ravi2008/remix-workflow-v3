# Comparator control runner A10

A10 is the complete wire successor to the preserved A09 design. It binds the
frozen A09 schema-4 wire. The report contains
`recordDeclarationComparison`; the exact 45-row divergence content lives in
its separately pinned schema-1 overlay. The runner reobserves the executable,
roots, metadata, RECORD files, and all 1,548 declared files at four boundaries:
preflight, immediate prelaunch, post-child cleanup, and parent readback. A10
does not accept A07, A08, or an arbitrary saved report.

This is a source-only design. It authorizes no comparator, control, compiler,
native, media, GPU, Resolve, or project operation.

## Caller usage

The caller selects only a fixed mode and a fresh private attempt. The runner
selects the future A09 helper, report, package, diagnostic, deadline, caps, and
working directory from its frozen source contract.

```text
UNIT=/Users/aira/projects/remix-gpt-coding-agent/artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01
PY=/Users/aira/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3.12
RUNNER=$UNIT/run_comparator_controls_a09.py

$PY -I -B $RUNNER --mode required-evidence --attempt required-evidence-a09-001
$PY -I -B $RUNNER --mode actual-comparator --attempt actual-comparator-a09-001
```

The source fixes the mode map. A caller cannot supply a runtime-report path,
diagnostic path, child path, deadline, cap, environment, or output name.

```python
# required-evidence-control-a11.py emits only the existing keys.
run("required-evidence", "required-evidence-a09-001")

# actual-comparator-control-a14.py remains the child under test.
run("actual-comparator", "actual-comparator-a09-001")
```

`run` creates the attempt with exclusive `mkdir`. A repeated attempt name
fails before opening or replacing an older attempt.

## A09 snapshot contract handoff

The A09 source, contract, rationale, and overlay are frozen. The successful
A09 report remains pending. The runner has one admissible variant:

```python
class RuntimeSnapshotVariant(Enum):
    A09_RECORD_OVERLAY_V4 = "a09-record-overlay-v4"
```

The external authorization must pin the exact A09 helper, contract, rationale,
report path, report bytes, report SHA-256, and variant. Until those identities
exist, the runner has no runtime authority and cannot start a child.

The report path is the fixed future path
`observer-runtime-snapshot-attempt-a09/runtime-snapshot-a09.json`. The attempt
and report are currently absent, so no report hash is available.

The exact frozen A09 source identities are:

```text
freeze_observer_runtime_a09.py
  c2ac751a7acdc9327112fad719dab751ba844162b346ff78e296e3eba3783dc4
observer-runtime-snapshot-contract-a09.md
  bb03fddb685b5a935a2a5f789ed12bcfb42c9252e8395b85e9c6054418e1341a
observer-runtime-snapshot-rationale-a09.md
  01683726ff727636ac6ef28d1cf894036045cd5dcac8bc911949ea0eae815603
observer-runtime-record-divergence-overlay-a09.json
  975e9dbb05e45718c363ebac762c868cd3c85bc952757c4d3aff017dce11b22a
```

The overlay path is
`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/observer-runtime-record-divergence-overlay-a09.json`.
It is 25,945 bytes. The diagnostic path is
`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/runtime-record-declaration-diagnostic-a01.json`.
It is 1,379,634 bytes.

The A09 report's exact root key set is:

```text
schema, state, workspaceBundle, invocation, runtime, distributions,
recordDeclarationComparison, historicalPathSetComparison, limits, scope
```

The state is the exact literal
`current_runtime_filesystem_snapshot_complete_unqualified`. The report is
schema 4. There is no report-embedded overlay row list, match-flag list, or
derived overlay digest.

```json
{
  "recordDeclarationComparison": {
    "policy": {},
    "sourceDiagnostic": {},
    "fixedMeasuredDivergenceOverlay": {},
    "totalRows": 1548,
    "totalInstalledFileBytes": 45567887,
    "strictNonOverlayRows": 1503,
    "strictDeclaredMatchRows": 995,
    "independentlyObservedUndeclaredRows": 508,
    "fixedMeasuredDivergenceRows": 45,
    "unexpectedDivergenceRows": 0,
    "overlayConsumedExactly": true,
    "overlayIsWheelOrRecordTrust": false,
    "providerOriginAttestation": false,
    "divergenceCauseVerified": false
  }
}
```

The separate overlay's exact root keys are `schema`, `state`, `sourceDiagnostic`,
`rowCount`, `scope`, and `rows`. Its schema is `1`, its state is
`fixed_measured_RECORD_divergence_overlay_unqualified`, and its row count is
45. Each row has exactly `package`, `path`, `runtimeRelativePath`,
`declaredBytes`, `declaredSha256`, `currentBytes`, and `currentSha256`.

The runner performs no case folding, path normalization, RECORD skipping,
wheel-hash substitution, or provider-provenance inference. It reopens and
hashes the separate overlay and diagnostic, then compares the overlay rows to
the diagnostic's exact mismatch projection. The overlay contains no identity,
match flags, or derived digest. Any runner digest is derived after parsing and
is bound separately.

The bound diagnostic is the preserved root independent observation:

```text
path: artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/runtime-record-declaration-diagnostic-a01.json
bytes: 1379634
sha256: 094c49dc02a1933782dba58fb75eb838587b9a6e7ab357a7c45cf0c61e7405d2
rowCount: 1548
mismatchCount: 45
totalFileBytes: 45567887
```

The diagnostic is evidence for the fixed overlay. It is not a generic waiver
for a future mismatch. A09 must reject a report whose overlay differs from
the bound diagnostic or whose current observations differ from the overlay.

## Shape

The public operation is one deep module. It hides fixed paths, source
admission, descriptor traversal, bounded hashing, process capture, runtime
comparison, publication, and readback behind `run_control` and
`readback_attempt`. Wire JSON is private to the runner.

```python
class ControlMode(Enum):
    REQUIRED_EVIDENCE = "required-evidence"
    ACTUAL_COMPARATOR = "actual-comparator"

@dataclass(frozen=True)
class RunRequest:
    mode: ControlMode
    attempt: str
    unit_root: Path
    python_entry: Path

@dataclass(frozen=True)
class FileIdentity:
    path: str
    kind: Literal["regular_file"]
    device: int
    inode: int
    mode: int
    links: int
    uid: int
    gid: int
    bytes: int
    mtime_ns: int
    ctime_ns: int
    sha256: str

@dataclass(frozen=True)
class SymlinkIdentity:
    path: str
    target: str
    device: int
    inode: int
    mode: int
    links: int
    uid: int
    gid: int

@dataclass(frozen=True)
class RootEndpoint:
    path: str
    device: int
    inode: int
    mode: int
    descriptor_matched_path_before: bool
    descriptor_matched_path_final: bool

@dataclass(frozen=True)
class RecordDeclaration:
    record_bytes: int | None
    record_sha256: str | None

@dataclass(frozen=True)
class RuntimeRow:
    package: str
    runtime_relative_path: str
    path: str
    declared: RecordDeclaration
    current: FileIdentity
    bytes_match: bool | None
    hash_matches: bool | None
    disposition: Literal[
        "strict_declared_match",
        "independently_observed_undeclared",
        "fixed_measured_divergence",
    ]

@dataclass(frozen=True)
class DivergenceRow:
    package: str
    runtime_relative_path: str
    path: str
    declared_bytes: int
    declared_sha256: str
    current_bytes: int
    current_sha256: str

@dataclass(frozen=True)
class DivergenceOverlayEvidence:
    file: FileIdentity
    schema: Literal[1]
    state: Literal["fixed_measured_RECORD_divergence_overlay_unqualified"]
    source_diagnostic: FileIdentity
    row_count: Literal[45]
    scope: Mapping[str, bool | str]
    rows: tuple[DivergenceRow, ...]

@dataclass(frozen=True)
class RecordDeclarationComparison:
    policy: Literal[
        "strict RECORD declarations except the exact fixed measured divergence overlay"
    ]
    source_diagnostic: FileIdentity
    fixed_measured_divergence_overlay: FileIdentity
    total_rows: Literal[1548]
    total_installed_file_bytes: Literal[45567887]
    strict_non_overlay_rows: Literal[1503]
    strict_declared_match_rows: Literal[995]
    independently_observed_undeclared_rows: Literal[508]
    fixed_measured_divergence_rows: Literal[45]
    unexpected_divergence_rows: Literal[0]
    overlay_consumed_exactly: bool
    overlay_is_wheel_or_record_trust: bool
    provider_origin_attestation: bool
    divergence_cause_verified: bool

@dataclass(frozen=True)
class RuntimeOverlay:
    comparison: RecordDeclarationComparison
    evidence: DivergenceOverlayEvidence

@dataclass(frozen=True)
class RuntimeDomainObservation:
    phase: Literal["preflight", "prelaunch", "post_child", "parent_readback"]
    manifest: FileIdentity
    entry: SymlinkIdentity
    executable: FileIdentity
    runtime_home: RootEndpoint
    python_root: RootEndpoint
    site_packages: RootEndpoint
    pillow_metadata: FileIdentity
    pillow_record: FileIdentity
    numpy_metadata: FileIdentity
    numpy_record: FileIdentity
    rows: tuple[RuntimeRow, ...]       # exactly 1,548
    row_digest: str
    overlay: RuntimeOverlay
    opened_inputs: int
    read_bytes: int
    path_bytes: int

@dataclass(frozen=True)
class RuntimeSnapshotEvidence:
    variant: RuntimeSnapshotVariant
    report: FileIdentity
    schema: Literal[4]
    state: Literal["current_runtime_filesystem_snapshot_complete_unqualified"]
    comparison: RecordDeclarationComparison
    overlay: DivergenceOverlayEvidence
    report_row_digest: str
    report_facets: tuple[str, str]

@dataclass(frozen=True)
class CapturedLoaderRecord:
    path: str
    bytes: int
    sha256: str

@dataclass(frozen=True)
class StreamObservation:
    bytes: int
    sha256: str
    complete: bool
    limit_hit: bool

@dataclass(frozen=True)
class CaptureOutcome:
    launch_attempted: bool
    process_started: bool
    pid: int | None
    returncode: int | None
    timed_out: bool
    cancelled: bool
    termination: tuple[str, ...]
    stdout: StreamObservation
    stderr: StreamObservation
    direct_child_reaped: bool
    descendants_reaped_attested: bool
    cleanup_errors: tuple[str, ...]

@dataclass(frozen=True)
class RunReport:
    schema: int
    state: Literal["passed", "rejected", "structured_failure"]
    mode: ControlMode
    attempt: str
    request_sha256: str
    preflight_sha256: str
    capture: CaptureOutcome
    child_stdout_schema: int | None
    loaded_comparator_source: CapturedLoaderRecord | None
    wrapper_observed_source: FileIdentity | None
    runtime_snapshot: RuntimeSnapshotEvidence
    runtime_preflight: RuntimeDomainObservation
    runtime_prelaunch: RuntimeDomainObservation
    runtime_after: RuntimeDomainObservation | None
    control_report_sha256: str | None
    control_result_digest: str | None
    output_files: tuple[str, ...]
    output_bytes: int
    source_only: bool
    native_execution: bool
    native_acceptance: bool
    gpu_used: bool
    resolve_used: bool

@dataclass(frozen=True)
class PublicationSeal:
    schema: int
    mode: ControlMode
    attempt: str
    state: str
    request_sha256: str
    runner_sha256: str
    package_manifest_sha256: str
    package_file_identities: tuple[FileIdentity, ...]
    runtime_snapshot: RuntimeSnapshotEvidence
    runtime_preflight_digest: str
    runtime_prelaunch: RuntimeDomainObservation
    runtime_after: RuntimeDomainObservation
    source_closure_sha256: str
    external_authorization_sha256: str
    capture: CaptureOutcome
    output_files: tuple[FileIdentity, ...]
    raw_stdout_sha256: str
    raw_stderr_sha256: str
    control_report_sha256: str | None
    control_result_digest: str | None
    loaded_comparator_source: CapturedLoaderRecord | None
    wrapper_observed_source: FileIdentity | None
    child_stdout_schema: int | None
    source_only: bool
    native_execution: bool
    native_acceptance: bool
    gpu_used: bool
    resolve_used: bool

@dataclass(frozen=True)
class ParentReadback:
    schema: int
    state: Literal["accepted", "rejected"]
    attempt_directory: DirectoryIdentity
    parent_directory: DirectoryIdentity
    preflight_runtime: RuntimeDomainObservation
    prelaunch_runtime: RuntimeDomainObservation
    sealed_runtime: RuntimeDomainObservation
    reread_runtime: RuntimeDomainObservation
    report_sha256: str
    seal_sha256: str
    runtime_snapshot: RuntimeSnapshotEvidence
    source_only: bool
    native_execution: bool
    native_acceptance: bool

def run_control(request: RunRequest) -> RunReport: ...
def observe_runtime_domain(
    snapshot: RuntimeSnapshotEvidence,
    phase: Literal["preflight", "prelaunch", "post_child", "parent_readback"],
) -> RuntimeDomainObservation: ...
def readback_attempt(path: Path) -> ParentReadback: ...
```

`DirectoryIdentity` is the existing A08 type and remains private. A child
loader record carries path, byte count, and SHA-256 only. It never invents
filesystem device or inode facts for a source loaded by the child.

## Runtime authority and overlay validation

`bind_runtime_snapshot` reads the fixed A09 report through bounded
descriptor-relative operations. It requires schema 4, the exact A09 top-level
key set, the exact state literal, the unqualified scope flags, the two A08
runtime facets, 1,548 ordered rows, and `recordDeclarationComparison`.
The comparison's overlay and diagnostic fields must be regular-file
observations for the separately pinned A09 overlay and diagnostic.

The central validator performs these checks before any child launch:

1. The report identity, helper, contract, rationale, and external
   authorization match the pending A09 variant.
2. The report's manifest, roots, entry, executable, METADATA, RECORD, and
   installed-file rows form one closed Pillow/NumPy domain.
3. The comparison has exactly 1,548 total rows, 45 fixed divergences, 995
   strict matches, 508 independently observed undeclared rows, and zero
   unexpected divergences. Its booleans equal the frozen policy.
4. The separate overlay has schema 1, the exact state and scope, 45 unique
   package/path rows, and the exact source-diagnostic binding.
5. Every overlay row exists exactly once among the report's 1,548 rows. The
   runner derives any overlay digest after parsing; it does not require an
   absent report field.
6. Every strict row matches its declared RECORD bytes and SHA-256. Every
   independently observed undeclared row has both declaration fields null and
   both match flags null. The 45 divergence rows use their fixed disposition.
7. The report's current observation is the expected current observation for
   all 1,548 rows, including the 45 known divergent files.
8. The report keeps `loadedImageAttestation=false`, package imports false,
   native execution false, and authorization false.

`observe_runtime_domain` then rereads the current provider through descriptors.
It verifies the fixed interpreter symlink and target, executable, runtime home,
Python root, site-packages root, provider manifest, both METADATA files, both
RECORD files, and every declared row. It computes a current `FileIdentity` for
each row without retaining file contents. It requires exactly 1,548 rows and
the exact report path order.

For a strict row, the live current bytes and SHA-256 must equal both the
report current fields and the declared RECORD fields. For an independently
observed undeclared row, the live current bytes and SHA-256 must equal the
report current fields while the report retains null declaration fields. For a
fixed divergence row, the live current bytes and SHA-256 must equal the report
current fields and the separately pinned overlay row. The live bytes need not
equal declared RECORD fields only for those exact 45 rows. Any additional
mismatch fails closed.

The same observation checks the diagnostic and overlay file identities and
their exact bytes. A changed diagnostic or overlay cannot silently redefine
the comparison. The report's `sourceDiagnostic` and
`fixedMeasuredDivergenceOverlay` observations must equal those files.

## Finite admission and retained evidence

The A08 process and stream limits remain unchanged:

| Limit | Value |
| --- | ---: |
| child deadline | 15 seconds |
| SIGTERM grace | 2 seconds |
| final drain | 1 second |
| direct-child reap | 1 second |
| stdout prefix | 1 MiB |
| stderr prefix | 128 KiB |
| request | 256 KiB |
| preflight | 4 MiB |
| control or failure report | 1 MiB |
| publication seal | 4 MiB |
| aggregate attempt output | 16 MiB |
| attempt entries | 7 maximum |

The A08 runtime domain limits also remain the source-bound admission:

```text
maxSingleFileBytes       = 128 MiB
maxTotalReadBytes        = 1 GiB per domain observation
maxInputOpens            = 65,536
maxRecordRowsPerPackage  = 4,096
maxTotalRecordRows       = 8,192
maxPathBytes             = 4,096
maxTotalPathBytes        = 32 MiB
expectedTotalRows        = 1,548
expectedOverlayRows      = 45
maxDiagnosticBytes       = 2 MiB
```

The 45.6 MB current file set is hashed in bounded chunks. File contents are
not retained as captured input, so the A08 8 MiB retained-input bound remains
separate from the 1 GiB streaming read bound. The preflight and seal each
contain one complete canonical domain observation. A09 rejects before child
launch if either encoded object exceeds its 4 MiB limit.

The attempt allowlist remains exactly:

```text
request.json
preflight.json
<mode>.stdout.bin
<mode>.stderr.bin
<mode>-control-report.json
<mode>-failure.json       # optional, only for structured failure
<mode>-publication-seal.json
```

`preflight.json` carries the full `preflight` observation. The publication
seal carries the full `prelaunch` and `post_child` observations. This avoids an
additional runtime file and preserves the seven-entry cap. Parent readback
rereads the full domain and stores its bounded `parent_readback` observation in
memory; the readback result carries its digest and equality outcome.

The encoded preflight and seal use canonical JSON, preflighted size accounting,
and exclusive files. The runner does not claim that a logical cap bounds Python
object overhead, allocator capacity, process RSS, or operating-system memory.

## Execution order

1. Resolve the fixed mode and validate the attempt name.
2. Create the attempt directory exclusively.
3. Read the A14 package manifest, all package rows, six comparator inputs, the
   A15 manifest, all 21 A15 source rows, and the A09 authorization through
   bounded descriptors.
4. Bind the exact schema-4 A09 report, diagnostic, and overlay. Recompute the
   report facets, overlay digest, and 1,548-row digest.
5. Observe the complete current runtime domain as `preflight`. Compare it to
   the report, comparison, and overlay, then write and sync request and
   preflight.
6. Reobserve the domain as `prelaunch`. If it differs from preflight, reject
   without starting the child. Retain this complete observation for the seal.
7. Start the exact child with `PY`, `-I`, `-B`, fixed source path, no shell,
   `close_fds=True`, and the fixed working directory.
8. Drain stdout and stderr continuously. Enforce the deadline, cancellation,
   prefix caps, and A08 TERM/KILL/reap behavior.
9. Reobserve all package, input, authorization, snapshot, diagnostic, overlay,
   and runtime-domain identities after child cleanup as `post_child`.
10. Parse the bounded child document. Require the existing required-evidence
    keys or A14 schema 3, integer loader bytes, exact 59-row order, statuses,
    codes, optional fields, and loader provenance.
11. Write streams, child report, and the publication seal exclusively. Sync,
    reopen, hash, validate the allowlist, and enforce the aggregate cap.
12. Parent readback independently checks directory identities, all output
    identities, preflight, prelaunch, and post-child observations, then makes
    a fourth fresh `parent_readback` domain observation. It checks report
    facets, overlay, authorization, and no-native flags.

The immediate prelaunch reread closes ordinary preflight drift. A09 does not
claim an operating-system-wide freeze between the final reread and `exec`.
The remaining path replacement race is a material limitation and must remain
visible in the seal. Holding descriptors for the observation does not make a
path-based child import from those descriptors.

## Module ownership

| Module | Owns |
| --- | --- |
| runner CLI | fixed modes, attempt creation, and caller validation |
| package observer | bounded package, A15, input, and source identities |
| snapshot verifier | schema 4, facets, current rows, and overlay adapter |
| runtime domain observer | descriptor traversal and 1,548 current rows |
| diagnostic verifier | fixed root diagnostic and 45-row digest |
| capture backend | selector drain, caps, deadlines, signals, and direct reap |
| child protocol verifier | required-evidence or A14 schema 3 and 59 rows |
| report writer | bounded JSON, sync, reopen, and aggregate cap |
| parent readback | independent output, domain, overlay, and authorization checks |

No module accepts a caller-provided source path or runtime snapshot. The
snapshot verifier and runtime domain observer share only the typed row and
overlay validators. They do not maintain a second runtime package model.

## Source closure and external authorization

The package remains the frozen A14 package manifest, A15 input rows, and exact
child source rows. The source closure additionally binds:

- A09 runner source and wire contract;
- A09 helper, contract, and rationale;
- A09 divergence overlay and its exact schema-1 contract;
- the exact successful A09 report identity;
- the fixed root diagnostic identity and 45-row digest;
- the reviewed A08 capture policy;
- the A14 schema-3 result schedule.

The source closure excludes its own hash and excludes external authorization.
External authorization is created last. It pins the package manifest, source
closure, runner, A09 report, diagnostic, overlay identity and derived digest,
mode map, and finite
limits. No earlier file contains the authorization hash. This preserves the
A08 acyclic direction:

```text
package + runtime + diagnostic authorities
  -> source closure
  -> external authorization
  -> runner admission
```

The pending A09 report cannot be replaced by a caller-selected path or by the
45-row diagnostic alone. A diagnostic without a schema-4 report is not a
runtime authority.

## Verification and negative controls

Before any child process is allowed, pure controls must reject:

- A07, A08, schema-3, missing, and arbitrary report variants;
- an A09 report without `recordDeclarationComparison` or with the wrong
  comparison key set;
- an overlay without schema 1, the fixed state, exact 45 rows, or exact row
  keys;
- one changed declared or current fact in the separately pinned overlay;
- one added, removed, duplicated, or reordered runtime row;
- a changed entry symlink, executable, root, METADATA, RECORD, or installed
  file before launch;
- the same changes after the child while keeping the report bytes unchanged;
- an additional RECORD mismatch outside the 45 bound rows;
- a changed root diagnostic with an unchanged report;
- a count-only 59-row child, wrong schema, string loader bytes, unknown field,
  wrong result name/order/status/code, or fabricated loader identity;
- a preflight, seal, stream, aggregate, or row-read cap overflow.

The pure controls use saved copies and no comparator imports. The complete-path
runtime controls must invoke the same central A09 validator used by the runner.
They must not call a reduced allocation or report-only projection. A later
source-control review must inspect the control source before execution.

## Rationale

The preserved A08 attempt is empty after its RECORD mismatch, so no A08 report
exists. The future A09 report supplies expected current facts; descriptor
observations supply fresh facts; the separate overlay explains only the 45
known RECORD declaration divergences. This separates declared package metadata
from current executable bytes without pretending the mismatch is a successful
wheel verification.

Keeping the full before and after domain in preflight and seal makes the
publication record reviewable without adding attempt files. The same observer
is reused for parent readback, so a changed row cannot hide behind a digest
calculated by a different implementation. The 1 GiB read cap, exact 1,548-row
domain, path confinement, no-follow opens, and 65,536-open limit remain finite.

The child protocol stays A14 schema 3 with 59 ordered results. Its structural
qualification fields still do not establish native support, loaded images,
visual quality, playback, or creative acceptance. `loadedImageAttestation`
remains false.

## Alternatives considered

### Trust the saved schema-4 report and facet digests

This keeps the smallest implementation. It loses the connection between the
child's current executable/files and the saved report, which is the A08 P2.

### Generate a second runtime report after the child

This duplicates the runtime schema and creates two report authorities. The
typed domain observer keeps one A09 report authority and records fresh before,
after, and parent observations in bounded runner records.

### Ignore all RECORD mismatches

This would turn a known 45-row fact into a generic bypass and would accept new
mismatches. The explicit overlay accepts only the fixed declared/current rows
bound to the root diagnostic.

### Copy the 1,548 files into a private staging tree

This could remove path races but changes the runtime the child executes and
adds large unreviewed storage and copy semantics. A09 records the residual
path race instead of claiming an unproved staging equivalence.

## Tradeoffs accepted

- We accept four bounded domain scans in exchange for preflight, prelaunch,
  post-child, and parent-readback evidence.
- We accept duplicated row identities in preflight and seal in exchange for a
  reviewable seven-entry attempt with no hidden sidecar.
- We accept the fixed 45-row overlay in exchange for preserving the exact
  declared/current facts without generic RECORD suppression.
- We accept a residual path replacement race in exchange for using the same
  fixed Python entry and source paths that the child actually receives.
- We accept a pending snapshot hash in the design in exchange for forbidding
  arbitrary report substitution before A09 completes.

## Material risks and limits

- The A09 report does not exist yet. No runtime, comparator, or text result is
  qualified by this document.
- The root diagnostic is an independent local observation. It is not provider
  provenance and does not prove native loading or image behavior.
- Descriptor rereads detect ordinary file drift but cannot create an atomic
  operating-system snapshot across a path-based child launch.
- A 1 GiB logical read cap does not bound allocator overhead, RSS, or native
  framework memory.
- No stage establishes CoreText, CoreGraphics, ImageIO, shaping, raster,
  orientation, audio, media, playback, GPU, Resolve, or creative acceptance.

## Next implementation step

Freeze the A09 snapshot overlay key set and successful report identity, then
implement the shared domain observer and pure validator before any child run.
