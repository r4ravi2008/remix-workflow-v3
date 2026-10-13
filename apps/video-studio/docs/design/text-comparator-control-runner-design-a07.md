# Comparator control runner A07

A07 is a narrow correction to the preserved A06 design. It removes a
source-closure hash cycle, separates child loader evidence from filesystem
identity, and makes the timeout policy explicit. It does not authorize an
executable, a comparator, a control, a compiler, or a native process.

## Caller usage

The caller chooses one fixed control mode and one new private attempt. It cannot
choose source paths, reports, output paths, deadlines, caps, or environment
values.

~~~text
UNIT=/Users/aira/projects/remix-gpt-coding-agent/artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01
PY=/Users/aira/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3.12
RUNNER=$UNIT/run_comparator_controls_a07.py

$PY -I -B $RUNNER --mode required-evidence --attempt required-evidence-a07-001
$PY -I -B $RUNNER --mode actual-comparator --attempt actual-comparator-a07-001
~~~

The paths above are caller illustration only. No such A07 runner exists in
this design artifact. A future implementation must reject every mode and
attempt outside its fixed map and must create each attempt directory
exclusively.

The runner reports bounded Python contract checks. It does not establish
CoreText, CoreGraphics, ImageIO, native text, PNG orientation, media support,
GPU, Resolve, playback, listening, or creative acceptance.

## Final authority boundary

A07 does not bind the current A11 package manifest or the current A12 package
manifest. Both are rejected package authorities. The current A11 README row
records 6,682 bytes while the current README is 6,802 bytes. A12 inherits that
manifest.

The future accepted package is an external, separately frozen manifest
successor. It must bind:

- the unchanged comparator source, or a separately reviewed direct-source
  successor;
- the required-evidence control;
- the reviewed A12 control successor;
- each contract and output-schema file;
- every A11 input authority;
- the Swift A15 source manifest;
- the runtime snapshots;
- the source-closure authorization.

The runner verifies every row through a regular-file descriptor before launch
and after cleanup. It rejects missing, extra, duplicate, reordered, changed,
or stale rows. The package manifest cannot hash the source-closure file that
contains the manifest's own row. An external authorization seals the complete
closure after all rows exist.

The A12 control remains pending until its three peer findings are repaired:

1. The current-allocation report must replay a current-bound event stream.
2. Observation controls must assert the actual 'swift_case_gate_passed' result,
   rather than trust a declared 'qualified: false' field.
3. The predecessor package mismatch must be replaced by a corrected manifest.

A runner implementation must bind the corrected successor. It must never
silently treat the current A11 or A12 manifest as accepted.

## Caller and output types

~~~python
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
    runtime_binding_sha256: str
    runtime_closure_sha256: str
    source_closure_sha256: str
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
    source_only: bool
    native_execution: bool
    native_acceptance: bool
    descendants_reaped_attested: bool
    limitations: tuple[str, ...]

def run_control(request: RunRequest) -> RunReport: ...
def readback_attempt(path: Path) -> ParentReadback: ...
~~~

The public report, seal, and parent readback have exact key sets matching these
shapes. Unknown fields fail. Directories carry device, inode, and mode only.
Regular files carry device, inode, mode, byte count, and SHA-256.

## Fixed capture and output limits

A07 uses one fixed capture policy for both modes. A04's earlier public
RunRequest default was 30 seconds. A07 removes that caller-controlled default
and selects 15 seconds from the reviewed A03 CaptureBackend policy. The
selection is new A07 policy; it is not an A04 inherited value.

| Contract | Value |
| --- | ---: |
| Wall-clock child deadline | 15 seconds |
| SIGTERM-to-SIGKILL grace | 2 seconds |
| Final pipe-drain interval | 1 second |
| Direct-child reap timeout | 1 second |
| Retained stdout prefix | 1 MiB |
| Retained stderr prefix | 128 KiB |

The runner starts the child in a new process group. It drains both pipes with a
selector. Cancellation, deadline, or a live cap breach sends SIGTERM, then
SIGKILL after two seconds. It always closes descriptors and performs the
one-second direct-child wait, including after post-launch exceptions. It never
claims that group signaling reaped descendants.

The attempt output allowlist is exact:

~~~text
request.json
preflight.json
<mode>.stdout.bin
<mode>.stderr.bin
<mode>-control-report.json
<mode>-failure.json       # optional, only for a structured failure
<mode>-publication-seal.json
~~~

The caps are part of the A07 wire contract:

| File | Maximum |
| --- | ---: |
| request.json | 256 KiB |
| preflight.json | 4 MiB |
| each raw stream | its retained prefix cap |
| control report | 1 MiB |
| failure record | 1 MiB |
| publication seal | 4 MiB |
| all listed attempt files | 16 MiB |
| file entries | 7 maximum |

The aggregate cap includes runner-owned records. A structured failure cannot
publish an unbounded error detail. The failure record has a 64 KiB detail cap
inside its 1 MiB file cap. The runner rejects an unexpected file, duplicate
name, oversized file, or aggregate overrun before accepting a seal.

## Exact child stdout contracts

The required-evidence child has exactly two top-level keys:

~~~python
{"obligation": list[Result], "relations": list[Result]}
~~~

The wrapper checks exact list order, result key sets, names, statuses, and
codes. It does not require internal schema-2 fixture fields.

The current A12 control has this source-defined shape:

~~~python
{
    "schema": 1,                 # integer
    "state": "executed",        # exact string
    "loader": {
        "path": string,
        "bytes": string,         # decimal string in current A12
        "sha256": string,         # lowercase 64-hex
    },
    "results": list[Result],
}
~~~

No other top-level key is allowed. A result normally has exactly
'name', 'status', and 'code'. A gate-false row may add string
'diagnostic'. An observation-unqualified row may add string 'diagnostic' and
'active_structural_gate'. The final successor must freeze this choice in its
output schema. If it changes 'loader.bytes' to an integer, the manifest,
schema, runner, and parent readback change together.

The runner requires unique result names and the final successor's complete
ordered result table. It checks accepted 'ok' rows, rejected error codes,
qualification-false rows, parser-only rows, and the Rust stability rows. It
does not infer obligations from a result count.

The accepted A13 successor must use an integer loader byte count:

~~~python
{
    "schema": 1,
    "state": "executed",
    "loader": {"path": string, "bytes": int, "sha256": string},
    "results": list[Result],
}
~~~

This is a deliberate wire correction. The current A12 string field remains a
historical source observation and cannot satisfy the A13 integer contract. A13
must freeze the complete result-name and result-code table in its manifest and
output contract. A07 does not invent that table while A13 is still pending.

The child loader record is the only source identity that describes bytes passed
to 'exec'. The runner records it as 'loaded_comparator_source' using the
three-field CapturedLoaderRecord. It compares the loader path, integer byte
count, and hash with the accepted package row, but does not invent device,
inode, mode, or timestamps for those executed bytes. 'wrapper_observed_source'
remains a separate FileIdentity descriptor observation. A loader mismatch
fails the run.

## Module ownership and execution order

| Module | Owns |
| --- | --- |
| runner CLI | fixed mode map, attempt creation, request, preflight, publication |
| package observer | bounded descriptor reads and all before/after source joins |
| reviewed capture backend | selector drain, caps, deadlines, signals, direct reap |
| child control | pure comparator/control assertions and loader payload |
| report writer | bounded JSON, exclusive files, sync, reopen, aggregate cap |
| parent readback | independent file/dir identities, seal and report verification |

The runner order is:

1. Create the attempt directory exclusively with mode 0700.
2. Read the accepted successor manifest, runtime snapshots, A15 rows, and all
   inputs through descriptors. Reject any authority mismatch.
3. Write and sync bounded request and preflight files.
4. Start the exact child with [PY, "-I", "-B", fixed_control_path],
   close_fds=True, no shell, and a fixed working directory.
5. Drain stdout and stderr continuously. Hash retained prefixes as they arrive.
6. Apply the 15-second deadline and the two-second termination grace.
7. Close pipes and reap the direct child with the one-second bound.
8. Reobserve every authority row and runtime snapshot. Any drift creates a
   structured failure.
9. Parse one bounded child JSON document. Require exact top-level keys, field
   types, result order, status, codes, and loader record.
10. Write raw streams, parsed report, and seal through exclusive descriptors.
    Sync and reopen every file. Sync the attempt directory.
11. Parent readback independently recomputes all identities and verifies the
    seal, report, output allowlist, aggregate bytes, and no-native fields.

The runner never imports the comparator in its own process. The child loads the
accepted comparator source through the reviewed A12 loader. The parent
readback never imports the comparator or either control.

## Runtime and source closure

The current runtime snapshot is produced by A's independent helper. A03
runtime and dependency closure remain historical. The runner binds A's fresh
runtime binding and closure by exact path, byte count, and SHA-256.

The source closure records the accepted successor manifest, comparator source,
required control, A12 control, contract files, A15 manifest, A15 input rows,
runtime snapshots, capture backend source, and runner source. It excludes its
own hash row and excludes the external authorization. The authorization is
created only after the source closure exists. It separately pins the source
closure hash, runner hash, accepted manifest hash, runtime binding hash, and
runtime closure hash. The runner verifies the closure and authorization as
independent records. The runtime snapshot's loaded-image limitation remains
explicit.

## Rejections and verification

Rejected designs include post-exit stream reads, subprocess.run(timeout=...),
merged stderr, descendant-reap claims, current A11/A12 package manifests,
source-path identity as loaded-source proof, and a self-hashing source closure.

Pure source controls may test exact file boundaries, output allowlist and
aggregate accounting, A12 stdout type/framing, loader/path distinction,
result-table rejection, and descriptor drift. These controls require no
compiler, native, media, GPU, Resolve, or comparator execution.

Runtime snapshot preparation and its filesystem controls can proceed before
the final comparator package is accepted. The package manifest closure, child
control execution, publication seal, and parent readback must wait for the
corrected successor manifest and final A12 control contract.

A07 remains design-only. It makes no runtime, native, media, or acceptance
claim.

