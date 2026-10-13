# Comparator control runner A08

A08 is the narrow runner correction for the reviewed A14 control package. It
binds A14's schema 3 and 59 ordered results. It retains A07's finite capture,
termination, output, and readback contracts.

This document is design-only. It authorizes no comparator, control, compiler,
native, media, GPU, Resolve, or project operation.

## Caller usage

The caller selects one fixed mode and one fresh private attempt. The caller
cannot select a source path, runtime report, deadline, cap, environment, or
output name.

```text
UNIT=/Users/aira/projects/remix-gpt-coding-agent/artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01
PY=/Users/aira/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3.12
RUNNER=$UNIT/run_comparator_controls_a08.py

$PY -I -B $RUNNER --mode required-evidence --attempt required-evidence-a08-001
$PY -I -B $RUNNER --mode actual-comparator --attempt actual-comparator-a08-001
```

The fixed mode map is:

| Mode | Child source | SHA-256 | Child output |
| --- | --- | --- | --- |
| `required-evidence` | `text-report-comparator-a11/required-evidence-control-a11.py` | `69c8c96d60b7b8842d6e5f55a564ea23e6853d66c8d06b006e9738e203be809c` | exact top-level keys `obligation`, `relations` |
| `actual-comparator` | `text-report-comparator-a14/actual-comparator-control-a14.py` | `b43e3ada668f150a52ce7c77c7028fdf91b0447a7f15fc08cb040d0ea98617c1` | A14 schema 3, 59 ordered results |

The attempt name must match the fixed mode prefix and an admitted suffix. The
runner creates the attempt directory with exclusive `mkdir`. A repeated name
fails without opening or replacing an older attempt.

## Authority boundary

The accepted package target is A14, not the rejected current A11 or A12
manifest. The package rows come from:

```text
text-report-comparator-a14/package-manifest-a14.json
```

The frozen package manifest SHA-256 is
`b8e0422d8c2737009978c7fe2a71c6d5a59430ae116afc399b0bf9c69cad7d31`.
The runner reads and hashes every package row, all six comparator input rows,
the A15 manifest, all 21 A15 source rows, and every review-authority row.
It rejects missing, extra, duplicate, reordered, changed, or stale rows.

The package remains source-only until a later frozen authorization. The A14
manifest, A14 control, A15 inputs, and current runtime report are not accepted
merely because their paths exist.

## One runtime report with two facets

The A07 helper produces one report, not separate runtime-binding and dependency
closure files:

```text
observer-runtime-snapshot-attempt-a07/runtime-snapshot-a07.json
```

The runtime helper authority is frozen separately from the not-yet-produced
report:

| File | SHA-256 |
| --- | --- |
| `freeze_observer_runtime_a07.py` | `eb0cbd3d68de9ff1d41c12170ab127cc5613cc084c73b8d0ee2de54ae65f5b65` |
| `observer-runtime-snapshot-contract-a07.md` | `4b17e50681c612045b3695fbf5019b76ffb5a59e2ceb42d4697cda44eb34f9bb` |
| `observer-runtime-snapshot-rationale-a07.md` | `bb8e65cd64abfa6ed56ce9b525e1364b1f6d8e174f4ef307e7a0492fa18156bd` |

The later authorization binds these three source documents and the actual A07
report identity together. The report SHA remains unknown until A07 executes.

The runner binds one `FileIdentity` for this exact report. It requires the A07
report's schema 3, exact top-level keys, complete state, and declared scope.
The runner then derives two semantic facets from that same parsed report:

```python
@dataclass(frozen=True)
class RuntimeFacetDigest:
    name: Literal["runtime_binding", "distribution_domain"]
    source_report_sha256: str
    projection: tuple[str, ...]
    canonical_sha256: str

@dataclass(frozen=True)
class RuntimeSnapshotEvidence:
    report: FileIdentity
    schema: Literal[3]
    state: Literal["current_runtime_snapshot_complete_unqualified"]
    facets: tuple[RuntimeFacetDigest, RuntimeFacetDigest]
```

The exact projection pointers are:

| Facet | Canonical JSON pointers |
| --- | --- |
| `runtime_binding` | `/workspaceBundle`, `/invocation`, `/runtime` |
| `distribution_domain` | `/distributions`, `/historicalPathSetComparison`, `/limits`, `/scope/distributionDomain` |

Each projection is canonical JSON over those fields from the exact report
bytes. Both facet records repeat the report SHA-256.

These are two verified views of one saved report. They are not invented files,
separate runtime closures, or independent execution authorities. Parent
readback recomputes both projections from the same report and compares the
report identity and facet digests.

The A07 report's own 32 MiB report cap remains the input observation bound.
The runner does not embed the report bytes in `preflight.json`; it records the
report identity and facet digests there. The report remains outside the
attempt output aggregate cap.

## Caller and output types

```python
class ControlMode(Enum):
    REQUIRED_EVIDENCE = "required-evidence"
    ACTUAL_COMPARATOR = "actual-comparator"

@dataclass(frozen=True)
class RunRequest:
    mode: ControlMode
    attempt: str
    unit_root: Path
    python: Path

@dataclass(frozen=True)
class FileIdentity:
    path: str
    kind: Literal["regular_file"]
    dev: int
    inode: int
    mode: int
    bytes: int
    sha256: str

@dataclass(frozen=True)
class DirectoryIdentity:
    path: str
    kind: Literal["directory"]
    dev: int
    inode: int
    mode: int

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
class CapturedLoaderRecord:
    path: str
    bytes: int
    sha256: str

@dataclass(frozen=True)
class ActualResult:
    name: str
    status: Literal["accepted", "rejected"]
    code: str
    diagnostic: str | dict[str, object] | None
    structural_report_gate: bool | None
    case_contract_gate: bool | None
    declared_qualified: bool | None
    native_qualification: bool | None
    active_structural_gate: str | None
    qualification_boundary: str | None

@dataclass(frozen=True)
class ActualControlReport:
    schema: Literal[3]
    state: Literal["executed"]
    loader: CapturedLoaderRecord
    results: tuple[ActualResult, ...]

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
    output_files: tuple[FileIdentity, ...]
    report_sha256: str
    seal_sha256: str
    runtime_snapshot: RuntimeSnapshotEvidence
    source_only: bool
    native_execution: bool
    native_acceptance: bool
    descendants_reaped_attested: bool
    limitations: tuple[str, ...]

def run_control(request: RunRequest) -> RunReport: ...
def readback_attempt(path: Path) -> ParentReadback: ...
```

All public records use exact key sets. Unknown keys fail. Directory identities
carry device, inode, and mode. Regular-file identities carry device, inode,
mode, byte count, and SHA-256. A child loader record carries only path, byte
count, and SHA-256 because it describes bytes passed to `exec`; it does not
claim filesystem identity for the loaded payload.

## A14 child stdout contract

The actual child must emit exactly:

```json
{
  "schema": 3,
  "state": "executed",
  "loader": {"path": "...", "bytes": 0, "sha256": "..."},
  "results": []
}
```

The runner requires integer `loader.bytes`, the A14 comparator path, the
manifested A11 comparator SHA, exactly 59 result objects, unique result names,
and the ordered result table below. It rejects a schema 1 or 2 child, a string
loader byte count, a missing field, an extra field, an unknown result field,
or a result count that happens to match without matching names and order.

Each result has `name`, `status`, and `code`. The optional fields are exactly
the A14 source-defined fields: `diagnostic`, `structural_report_gate`,
`case_contract_gate`, `declared_qualified`, `native_qualification`,
`active_structural_gate`, and `qualification_boundary`. Allocation diagnostics
must preserve the A14 structured fields and integer types. The runner bounds
the encoded diagnostic and total child report before retaining it.

The required-evidence child remains a separate exact contract with only
`obligation` and `relations` at the top level. A08 does not force A14 fields
onto that child.

The actual result order and expected status/code are:

```text
01 a14-loader-provenance-integer-bytes accepted/ok
02 a15-source-manifest-join accepted/ok
03 a11-allocation-baseline-16m accepted/ok
04 a11-current-allocation-314231808-under-512m accepted/ok
05 a12-complete-parser-current-allocation-314231808 accepted/ok
06 a12-active-gate-current-allocation-314231808 accepted/ok
07 a12-allocation-baseline-binding-mutation rejected/swift_reservation_binding
08 a12-allocation-baseline-range-mutation rejected/swift_reservation_baseline
09 a12-allocation-peak-binding-mutation rejected/swift_reservation_binding
10 a12-allocation-peak-range-mutation rejected/swift_reservation_peak_slots
11 a11-allocation-missing-observed-peak rejected/swift_allocation_keys
12 a11-rust-evidence-exact-bound accepted/ok
13 a11-rust-evidence-one-byte-over rejected/evidence_stored_cap
14 a11-swift-evidence-exact-bound accepted/ok
15 a11-swift-evidence-one-byte-over rejected/evidence_stored_cap
16 a14-current-allocation-event-log-reconcile accepted/ok
17 a11-complete-parser-accepted-16m-512m accepted/ok
18 a11-active-gate-accepted accepted/ok
19 a11-complete-parser-observation-only accepted/ok
20 a11-complete-parser-fractional-controls accepted/ok
21 a11-active-gate-observation-only accepted/ok
22 a11-complete-parser-expected-rejection accepted/ok
23 a11-active-gate-expected-rejection accepted/ok
24 a11-complete-parser-failed-prefix-0 accepted/ok
25 a13-failed-prefix-0-case-gate accepted/qualification_false
26 a11-complete-parser-failed-prefix-1 accepted/ok
27 a13-failed-prefix-1-case-gate accepted/qualification_false
28 a11-complete-parser-failed-prefix-2 accepted/ok
29 a13-failed-prefix-2-case-gate accepted/qualification_false
30 a11-complete-parser-outer-failure-no-repeats accepted/ok
31 a11-negative-omitted-guard-role rejected/swift_case_records
32 a11-negative-omitted-native-image rejected/swift_native_image_obligation
33 a12-negative-omitted-fractional-control rejected/toggle_count
34 a12-negative-fractional-control-order rejected/swift_toggle_schedule
35 a11-negative-disallowed-error rejected/swift_rejection_error
36 a11-negative-comparator-field-in-error rejected/object_keys
37 a11-negative-rejection-native-residue rejected/swift_rejection_residue
38 a11-negative-omitted-clip-reference rejected/swift_clip_reference
39 a11-negative-failed-zero-case-residue rejected/swift_failure_residue
40 a11-negative-failed-prefix-incomplete rejected/swift_failure_prefix
41 a11-negative-failed-prefix-relation rejected/swift_guard_relation
42 a11-complete-parser-exact-zero-coverage accepted/ok
43 a12-complete-parser-fractional-partial-prefix-0 accepted/ok
44 a13-fractional-partial-prefix-0-case-gate accepted/qualification_false
45 a12-complete-parser-fractional-partial-prefix-1 accepted/ok
46 a13-fractional-partial-prefix-1-case-gate accepted/qualification_false
47 a12-complete-parser-fractional-partial-prefix-2 accepted/ok
48 a13-fractional-partial-prefix-2-case-gate accepted/qualification_false
49 a12-complete-parser-observation-only-nonfont-prefix-0 accepted/ok
50 a13-observation-only-nonfont-prefix-0-boundary accepted/qualification_false
51 a12-complete-parser-observation-only-nonfont-prefix-1 accepted/ok
52 a13-observation-only-nonfont-prefix-1-boundary accepted/qualification_false
53 a12-complete-parser-observation-only-nonfont-prefix-2 accepted/ok
54 a13-observation-only-nonfont-prefix-2-boundary accepted/qualification_false
55 a12-complete-parser-outer-failure-causal-shape accepted/ok
56 a13-outer-failure-case-gate accepted/qualification_false
57 a11-rust-control-paths-excluded-only accepted/ok
58 a11-rust-control-active-stability accepted/ok
59 a11-rust-control-decoded-mutation-rejected accepted/ok
```

`qualification_false` is a successful structural observation of an unqualified
case. It does not mean native support or creative acceptance.

## Fixed capture and output limits

A08 retains the reviewed A07 policy:

| Contract | Value |
| --- | ---: |
| child wall-clock deadline | 15 seconds |
| SIGTERM-to-SIGKILL grace | 2 seconds |
| final pipe-drain interval | 1 second |
| direct-child reap timeout | 1 second |
| retained stdout prefix | 1 MiB |
| retained stderr prefix | 128 KiB |
| request file | 256 KiB |
| preflight file | 4 MiB |
| actual control report | 1 MiB |
| structured failure file | 1 MiB |
| publication seal | 4 MiB |
| aggregate attempt bytes | 16 MiB |
| attempt entries | 7 maximum |

The attempt allowlist remains:

```text
request.json
preflight.json
<mode>.stdout.bin
<mode>.stderr.bin
<mode>-control-report.json
<mode>-failure.json       # optional, only for structured failure
<mode>-publication-seal.json
```

The process starts in a new process group. The capture backend drains both
streams with a selector. Deadline, cancellation, or a live cap breach sends
SIGTERM, then SIGKILL after the two-second grace. It always closes pipe
descriptors and waits for the direct child. It records descendant signaling,
but never claims that group signaling reaped descendants.

`launch_attempted` is set before process creation. `process_started` is set
only after a child PID is returned. Every post-launch exception follows the
same termination, pipe-drain, descriptor-close, and direct-child-reap path.

## Source closure and external authorization

The A14 package manifest contains package rows only. It does not contain a
source-closure row or external authorization row.

The runner creates a separate source closure after the following exact files
are frozen:

- A14 package manifest rows, excluding the closure and authorization;
- A14 comparator control and its A11 comparator source;
- required-evidence control;
- A15 manifest and all 21 A15 rows;
- A07 helper, contract, and rationale;
- one A07 runtime report;
- the reviewed capture backend source;
- the A08 runner source and its contract.

The source closure excludes its own hash and excludes external authorization.
It does not include a self-hash row. An external authorization is created last,
outside both the package and source closure. It pins the package manifest
SHA-256, source-closure SHA-256, runner SHA-256, runtime report SHA-256, both
runtime facet digests, mode map, and finite capture contract.

The runner reads the authorization as an independent final seal. The
authorization does not become a package input, and the source closure does not
hash it. This removes the package-to-closure-to-authorization cycle.

## Module ownership and execution order

| Module | Owns |
| --- | --- |
| runner CLI | fixed mode map, attempt creation, request, and preflight |
| package observer | bounded package, A15, input, and runtime-report reads |
| runtime facet verifier | one A07 report schema and two projection digests |
| capture backend | selector drain, caps, deadlines, signals, direct reap |
| child protocol verifier | required-evidence keys or A14 schema 3 and 59 rows |
| report writer | bounded JSON, exclusive files, sync, reopen, aggregate cap |
| parent readback | independent file/dir identities, seal, report, and facets |

The operation order is:

1. Resolve the fixed mode, source, package manifest, and attempt map.
2. Create the attempt directory exclusively.
3. Read and verify the package rows, A15 rows, six inputs, A07 report, and
   external authorization through bounded descriptors.
4. Validate the one A07 report and recompute its two facet digests.
5. Reobserve those authorities before writing a bounded request and preflight.
6. Start the exact child with `PY`, `-I`, `-B`, the fixed source path, no shell,
   `close_fds=True`, and the fixed working directory.
7. Drain both streams continuously while enforcing deadlines and prefix caps.
8. Terminate on cancellation, deadline, or cap breach. Drain, close, and reap.
9. Reobserve every package, input, A15, authorization, and runtime-report
   identity. Any drift creates a bounded structured failure.
10. Parse one bounded child document. Require exact keys, types, mode schema,
    result order, status, codes, and loader provenance.
11. Write raw streams, child report, and publication seal exclusively. Sync,
    reopen, hash, and check the attempt allowlist and aggregate cap.
12. Parent readback independently recomputes file and directory identities,
    report and seal hashes, runtime facets, authorization, and no-native flags.

The runner never imports the comparator. The child loads the accepted source.
Parent readback never imports either source.

## Verification and rejection

Pure source controls should test the exact A14 schema 3, integer loader bytes,
59-row table, unknown-field rejection, one A07 report with both facets, package
and authorization cycle rejection, output allowlist, aggregate cap, stream
limits, and descriptor drift. These controls do not run the comparator or a
native process.

The first execution gate requires: an executed A07 report, a frozen A14
manifest, the exact runtime snapshot identity, the external authorization, and
an independent parent readback plan. A14's source-only status remains visible
until that gate passes.

Rejected alternatives:

- retaining A07's separate `runtime_binding_sha256` and `runtime_closure_sha256`
  as two nonexistent files;
- accepting schema 1 or schema 2 because a legacy loader field parses;
- accepting 59 rows from a count without checking every name, order, status,
  and code;
- placing external authorization inside the package or source closure;
- treating `swift_case_gate_passed` or `qualification_false` as native proof;
- reading child streams only after process exit;
- claiming descendant reaping from process-group signals;
- treating the A07 report as loaded-image, native, visual, or creative proof.

## Material risks and limits

The A07 report is not yet available, so no runtime facet hash can be bound in
this design. A later authorization must record its actual path, bytes, SHA-256,
schema, and facet digests.

The A14 control directly reads its font fixture manifest. The runner must bind
that manifest and all six input rows before child execution and reobserve them
afterward. The control package alone does not provide that filesystem seal.

No stage in A08 establishes CoreText, CoreGraphics, ImageIO, shaping, raster,
PNG orientation, media, playback, listening, GPU, Resolve, or creative
acceptance. A08 remains a bounded source-control runner design.
