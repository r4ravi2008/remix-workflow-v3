# Comparator A11 control runner A05

This is a narrow successor to the preserved A04 design. It corrects the
stdout contract, source-closure order, source-row ownership, environment
claim, and directory evidence. It does not authorize an executable yet.

## Caller usage

The caller selects one fixed A11 control and one fresh private attempt. The
caller cannot select a Python module, report, output directory, timeout, or
environment.

```text
UNIT=/Users/aira/projects/remix-gpt-coding-agent/artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01
PY=/Users/aira/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3.12
RUNNER=$UNIT/run_comparator_controls_a05.py

$PY $RUNNER --mode required-evidence --attempt required-evidence-a05-001
$PY $RUNNER --mode actual-comparator --attempt actual-comparator-a05-001
```

The runner writes only under `comparator-control-a05/<mode>-<attempt>/`.
Attempts are exclusive. A reused attempt fails before child launch.

The runner remains source-only. Passing a control reports bounded Python
contract behavior. It does not prove native text, PNG, media, GPU, Resolve,
playback, listening, or creative acceptance.

## Frozen authorities

The runner binds the current A11 package manifest
`d95e76834d427d8b44000cc35995808d975a0be8273fadcd8658de18bd824872`, the
current A11 package rows, the six A11 input rows, and the Swift A15 manifest
`0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e`.

The wrapper independently reads every one of the A15 manifest's 21 rows
before launch and after capture. The child source join remains a second check.
The wrapper rejects a missing, extra, reordered, changed, or duplicated row.
It compares each row's relative path, byte count, mode, device, inode, and
SHA-256. A child-only source check is insufficient because the wrapper owns
the input boundary around the child process.

The preserved A03 runtime binding is historical. Its Python identity was
18,041,888 bytes with SHA `ac60cfe0268614638d0ffa35f3b0284fc7b3a11482723793455e17eeb278509e`.
The current resolved executable is 18,058,560 bytes with SHA
`4158f03e1bae2b759f25a1ba1fbdab8bfb7161eba4caf22e28f0915986625bbc`.
The current runtime is therefore a new snapshot, even though both report
Python 3.12.14. Forty-five of the 1,042 preserved Pillow and NumPy closure
files also differ.

## Authority creation without a hash cycle

The runner does not embed its own source-closure hash. An external preparation
step creates these files in this order:

1. `observer-runtime-binding-a05.json` records the current executable path,
   descriptor identity, size, mode, SHA-256, Python version, and optimize
   level.
2. `observer-runtime-closure-a05.json` records the current Pillow and NumPy
   metadata and all 1,042 bounded file identities and hashes.
3. The finalized A05 runner, reviewed A03 capture source, A11 package rows,
   A11 input rows, A15 manifest rows, and the two runtime snapshots are hashed
   into `native-observer-source-closure-a05.json`.

The source closure contains no row for itself. It may contain the finalized
runner's own source row, because that row is available before the closure is
written. It never contains its own hash. The external source authorization
then seals the source-closure hash, runner hash, runtime snapshot hashes, and
package rows together. The runner verifies that authorization and its rows,
but does not hardcode an authorization or closure hash derived from itself.

The parent readback verifies the authorization as a separate regular file and
checks all referenced files again. A failed snapshot or authorization cannot
be silently relabeled as A04 evidence. The preserved A03 binding and closure
remain unchanged historical files.

## Exact A11 child stdout

The schema 2 value created by `required-evidence-control-a11.py` is an
internal fixture. It is not the child output schema and has no `schema` or
`caseOrder` output field.

The required control's stdout is exactly one bounded JSON object with these
top-level keys and no others:

```python
{
    "obligation": list[Result],
    "relations": list[Result],
}
```

The wrapper requires these exact ordered result names and outcomes:

```text
obligation:
positive=accepted/ok
missing-repeat=rejected/repeat_count
missing-toggle=rejected/toggle_schedule
missing-clip=rejected/clip_reference
missing-native-image=rejected/native_image
bad-rejection-code=rejected/rejection_code
missing-alpha-raw=rejected/alpha_raw
ledger-mismatch=rejected/ledger
oversized-mask=rejected/mask_dimension_cap

relations:
positive=accepted/ok
false-guard=rejected/raster_relation_guard
false-control=rejected/raster_relation_control
```

The wrapper checks exact key sets, list order, result object keys, names,
status, and code. It also checks the child's bounded byte count and raw-byte
SHA-256. It does not require the internal schema 2 fixture fields.

The actual control's current stdout is exactly one JSON object with these
top-level keys and no others:

```python
{
    "schema": 1,
    "state": "executed",
    "results": list[Result],
}
```

The wrapper checks `schema == 1`, `state == "executed"`, unique result names,
and the source-defined result name, status, and code sets. It does not require
a comparator hash because A11 does not emit one. The wrapper records the
loaded comparator source identity separately from the child stdout.

An A12 successor may add source-defined loaded-source provenance containing
the loaded path, byte count, and SHA-256. The wrapper must not guess those
field names or require them from A11. After A12 is frozen, its manifest,
output schema, and exact fields become a new explicit binding.

## Types and module ownership

```python
class ControlMode(Enum):
    REQUIRED_EVIDENCE = "required-evidence"
    ACTUAL_COMPARATOR = "actual-comparator"

@dataclass(frozen=True)
class RunRequest:
    mode: ControlMode
    attempt: str
    unit_root: Path                 # fixed native-text-unit-a01 root
    python: Path                    # fixed current runtime path

@dataclass(frozen=True)
class Identity:
    path: str
    kind: Literal["regular_file", "directory"]
    dev: int
    inode: int
    mode: int
    size: int | None                # files only
    sha256: str | None              # files only

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
    direct_child_reaped: bool
    descendants_reaped_attested: bool  # always false
    cleanup_errors: tuple[str, ...]

def run_control(request: RunRequest) -> RunReceipt: ...
```

`run_comparator_controls_a05.py` owns the fixed CLI, authority preflight,
child argv, publication, and final report. The reviewed A03 `CaptureBackend`
owns nonblocking pipes, selector draining, live caps, deadlines, process-group
signals, and bounded direct-child reaping. The package observer owns bounded
descriptor reads and all before/after row comparisons. The parent readback
owns independent seal verification. Neither control owns publication.

The child argv remains:

```text
[PY, "-I", "-B", FIXED_CONTROL_PATH]
```

The environment contains only fixed locale and system path values needed by
the control. It does not claim `PYTHONHASHSEED=0`: isolated mode `-I` ignores
Python environment variables. Deterministic child JSON comes from the
source-defined sorted serialization and exact result checks, not hash-seed
claims.

## Capture, cleanup, and publication

The runner creates the attempt directory with exclusive `mkdir`, mode 0700,
and a directory `Identity`. It records `launch_attempted` before spawning and
`process_started` only after `Popen` returns with a valid PID.

It starts a new process group with closed file descriptors and nonblocking
stdout and stderr. The selector drains both streams continuously. The runner
keeps separate 1 MiB stdout and 128 KiB stderr prefixes, hashes retained bytes,
and records cap hits. A deadline, cancellation, or cap breach sends SIGTERM to
the group, waits through the reviewed grace period, then sends SIGKILL. It
always closes descriptors and reaps the direct child. It records no descendant
reap attestation.

The runner rechecks package rows, six input rows, all 21 A15 rows, runtime
snapshots, source authorization, and the source closure after child cleanup.
Any drift produces a structured failure and prevents a passing report.

Only after capture and postchecks does it parse one bounded JSON document. It
uses the exact mode-specific stdout contract above. It writes raw streams,
parsed report, and seal through exclusive regular-file descriptors, syncs and
reopens each file, then syncs the attempt directory. The seal records whether
the child report is present, its exact bytes and hash, and all input/source
identities. The filesystem and seal are not treated as one atomic store.

The parent readback distinguishes the attempt directory and its parent as
directories from request, preflight, stream, report, failure, and seal files.
It checks directory device, inode, mode, and expected entries separately. It
checks file device, inode, mode, size, and SHA-256 as regular-file facts. It
never labels a directory a regular file or assigns a file size/hash to a
directory.

## Required verification before execution

The source review must freeze the A11 package rows and exact stdout result
sets. The preparation step must freeze the current runtime and dependency
snapshots, then the source closure and external authorization. The executable
review must verify all 21 A15 rows in both wrapper observations, exact child
argv, absence of `PYTHONHASHSEED` claims, separate directory/file evidence,
bounded capture, direct-child reaping, and no-native boundary fields.

The A11 control package remains blocked by the two P1 findings in
`text-report-comparator-source-review-a11.md`. A runner implementation or
execution must wait for repaired controls and a rehashed package manifest.
