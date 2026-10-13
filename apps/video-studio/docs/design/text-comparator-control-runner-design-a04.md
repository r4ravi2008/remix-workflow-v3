# Comparator A11 control runner A04

## Caller usage

The wrapper has two allowlisted modes. The mode selects the control source and
the output namespace. The caller cannot select another Python file, package,
or control.

```text
UNIT=/Users/aira/projects/remix-gpt-coding-agent/artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01
PY=/Users/aira/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3.12
RUNNER=$UNIT/run_comparator_controls_a04.py

$PY $RUNNER \
  --mode required-evidence \
  --attempt required-evidence-a04-001

$PY $RUNNER \
  --mode actual-comparator \
  --attempt actual-comparator-a04-001
```

The first call runs `text-report-comparator-a11/required-evidence-control-a11.py`.
It writes only under `comparator-control-a04/required-evidence-a04-001/`.

The second call runs `text-report-comparator-a11/actual-comparator-control-a11.py`.
It writes only under `comparator-control-a04/actual-comparator-a04-001/`.

Each attempt contains a mode-specific request, preflight, raw stdout, raw
stderr, parsed control report, failure record when needed, and publication
seal. An existing attempt directory is an error. The wrapper never overwrites
an attempt or reuses a prior control report.

The wrapper must use the resolved `PY` above. The repository virtualenv points
to a different Python 3.12.8 installation and is not this evidence runtime.

## Authority and runtime snapshot

The A11 package is frozen at manifest SHA-256
`d95e76834d427d8b44000cc35995808d975a0be8273fadcd8658de18bd824872`.
The wrapper verifies every manifest row before launch and after capture:

| Relative file | Bytes | SHA-256 |
| --- | ---: | --- |
| `compare_text_reports_a11.py` | 302746 | `e94b6ea3fb671ba66d413594060959bb5ec86f7e4fcffb8e774ababaeb438520` |
| `actual-comparator-control-a11.py` | 35197 | `3e1d293a57e1b617f39702d4d599f8520f6828860daba3fe59cd781f0b7c49a2` |
| `required-evidence-control-a11.py` | 10626 | `69c8c96d60b7b8842d6e5f55a564ea23e6853d66c8d06b006e9738e203be809c` |
| `README-a11.md` | 6682 | `1eb295208fd4cbc65215e796cedefa32261edb227427951cb7aaf6ad08441555` |
| `output-schema-a11.md` | 2917 | `a44039d6b8d58275a27304dc3d1fd542df37e2e66092b8ffed69fa712e021312` |
| `source-rationale-a11.md` | 4121 | `5fcce694107fe8ff0857d6997ebc5c0b3f349fb7a9a96ad93f416fe66f49f06d` |

The wrapper also verifies the six A11 input rows used by the comparator:

| Relative file | Bytes | SHA-256 |
| --- | ---: | --- |
| `synthetic-text-cases-a02.json` | 14706 | `a461e07c803793baa688b18452287ca73f3ba0e6d0f8c172458a0158e4ab513d` |
| `font-fixtures-a01/manifest.json` | 9673 | `04916451ea952d8ada2e5ca2d1171deaa0e1e6c0acd4652cf2bba0a77c057947` |
| `input-authority-a01.json` | 18506 | `6d2b0397a67837ab3a35151a951b9c8b11ba2f031185379d63d046a8cb697b13` |
| `font-fixtures-a01/OFL.txt` | 4377 | `0dab92d0544f7b233403f14b84a663bdbfa746982eda629e7f4f9ffe1b036feb` |
| `font-fixtures-a01/NotoSansTelugu-Regular.ttf` | 197228 | `2c05072e8018a9be1cb0582953d9edf9a0cf129cdfb74e611de763b09c411f7f` |
| `font-fixtures-a01/NotoSansDevanagari-Regular.ttf` | 219212 | `385e78e6359a9d88a0f243d53b1209d7548361ba2194e2b9ec779bcaa7e8949d` |

The actual control independently joins the frozen Swift A15 manifest. The
wrapper binds that manifest path and SHA `0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e`.
The child control remains responsible for checking all 21 rows. The wrapper
rechecks the manifest and the package rows after the child closes.

The preserved A03 observer binding names Python 3.12.14 at 18,041,888 bytes,
SHA `ac60cfe0268614638d0ffa35f3b0284fc7b3a11482723793455e17eeb278509e`.
The current resolved executable is 18,058,560 bytes, SHA
`4158f03e1bae2b759f25a1ba1fbdab8bfb7161eba4caf22e28f0915986625bbc`.
The current file is therefore runtime drift, even though its reported Python
version remains 3.12.14.

The preserved closure has Pillow 12.3.0 with 141 files and NumPy 2.3.5 with
901 files. All 1,042 paths still exist. Forty-five compiled Pillow or NumPy
files differ in bytes or hash. The old closure SHA is
`8ca43d6b5f7340de7fcdbc22642239719f32e0201a957849d4a1d26474540c6e`.

The wrapper must not use the old closure as current evidence. Before any A11
control run, create and seal these new snapshots, leaving A03 unchanged:

```text
observer-runtime-binding-a04.json
observer-runtime-closure-a04.json
native-observer-source-closure-a04.json
```

The A04 runtime binding records the current executable path, dev/inode/mode,
18,058,560 bytes, the requested SHA, CPython 3.12.14, and optimize level 0.
The A04 dependency closure records the current Pillow and NumPy metadata and
all 1,042 installed file identities and hashes. The A04 source closure records
the future wrapper source, the A11 package rows, the two A11 controls, the
three A04 runtime snapshots, and the reviewed Runner A03 capture source.

The snapshots are path-and-file evidence. They do not attest already-loaded
interpreter memory or process RSS. A mismatch before or after launch rejects
the attempt and prevents a success seal.

## Public and private shapes

```python
class ControlMode(Enum):
    REQUIRED_EVIDENCE = "required-evidence"
    ACTUAL_COMPARATOR = "actual-comparator"

@dataclass(frozen=True)
class RunRequest:
    mode: ControlMode
    attempt: str                 # [A-Za-z0-9][A-Za-z0-9._-]{0,63}
    unit_root: Path              # fixed native-text-unit-a01 root
    python: Path                 # fixed current A04 runtime path
    timeout_s: float = 30.0
    stdout_cap: int = 1 * 1024 * 1024
    stderr_cap: int = 128 * 1024

@dataclass(frozen=True)
class ByteObservation:
    path: str
    bytes: int                   # retained prefix length when capped
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
    stdout: ByteObservation
    stderr: ByteObservation
    direct_child_reaped: bool
    descendants_reaped_attested: bool  # always false
    cleanup_errors: tuple[str, ...]

@dataclass(frozen=True)
class RunReceipt:
    request_sha256: str
    mode: ControlMode
    attempt_root: Path
    capture: CaptureOutcome
    control_report_sha256: str | None
    publication_seal_sha256: str

def run_control(request: RunRequest) -> RunReceipt: ...
```

`run_control` accepts only the two fixed A11 controls. It rejects a mode,
attempt name, path, timeout, or cap outside the declared bounds. The caller
does not pass a comparator module, input report, shell command, or output path.

The child argv is exact and distinct:

```text
required-evidence:
[PY, "-I", "-B", UNIT/text-report-comparator-a11/required-evidence-control-a11.py]

actual-comparator:
[PY, "-I", "-B", UNIT/text-report-comparator-a11/actual-comparator-control-a11.py]
```

`-I` and `-B` disable user site imports and bytecode writes. The child gets a
small fixed environment: `LANG=C`, `LC_ALL=C`, `PYTHONHASHSEED=0`, and a fixed
system `PATH`. It receives no stdin and no shell. The wrapper records argv,
cwd, environment names and values, executable identity, and source identities.

## Module ownership and capture sequence

| Module | Owns |
| --- | --- |
| `run_comparator_controls_a04.py` | CLI, fixed mode map, preflight, publication, and final report state |
| reviewed Runner A03 `CaptureBackend` | nonblocking pipes, selector drain, deadlines, process-group signals, and direct-child reap |
| A04 package observer | descriptor reads, package/runtime/source identity checks, and before/after joins |
| A04 parent readback | independent seal verification and no-native boundary check |
| A11 required control | fifteen-case evidence contract and relation mutations |
| A11 actual control | comparator source join, allocation boundaries, parser, gate, failure-prefix, and Rust stability controls |

The wrapper uses the reviewed Runner A03 `CaptureBackend` contract. It does
not introduce a second `subprocess.run` or postprocess-only log reader. If the
future source cannot import the A03 backend without running its main path, a
mechanical extraction may move that backend into one shared module. The
selector, caps, signal order, and cleanup behavior must remain identical.

The capture order is:

1. Create the mode-specific attempt directory with exclusive creation and mode
   `0700`.
2. Read and hash all package, input, A15 manifest, and A04 runtime files through
   bounded descriptors. Record dev, inode, size, mode, mtime, ctime, and hash.
3. Write and sync `request.json` and `preflight.json` exclusively.
4. Start the exact child with `start_new_session=True`, `close_fds=True`, and
   nonblocking stdout and stderr pipes.
5. Drain both pipes with a selector while the child runs. Keep at most the
   declared prefix for each stream. Hash retained bytes as they arrive.
6. On cancellation, deadline, or cap breach, send `SIGTERM` to the process
   group. After the grace deadline, send `SIGKILL`. If group signaling fails,
   record the failure and signal the direct child. Do not claim descendants
   were reaped.
7. Close selector registrations and pipe descriptors. Reap the direct child
   in a bounded wait even when launch, capture, parsing, or write code fails.
8. Reobserve every bound input and runtime file. Any identity, size, metadata,
   or hash drift changes the result to a structured failure.
9. Parse the retained stdout only after capture. Require one bounded JSON
   document, exact top-level keys, exact schema, unique result names, and the
   mode-specific expected result set. A nonzero child or incomplete stream
   cannot publish a passing control report.
10. Publish the parsed report and seal only after all checks pass.

The backend records `launch_attempted` separately from `process_started`.
Every post-launch exception enters the same termination, stream-close, and
direct-child-reap path. A descendant holding a pipe cannot extend the deadline.
The wrapper records `descendants_reaped_attested=false` even when the child
normally exits.

## Control result obligations

The required control must produce schema 2 with the frozen fifteen-case order.
Its report must contain the nine evidence and relation results from the A11
source. The wrapper checks that each result has one of the expected statuses,
that all mutation cases are rejected, and that the positive case is accepted.

The actual control must produce schema 1, state `executed`, and its source-bound
result names. The wrapper checks unique names and the frozen schedule digest,
not a duplicated hand-written copy of every control implementation. It must
observe the allocation boundary controls, parser and active-gate controls,
causal partial prefixes, zero coverage, observation-only non-font failures,
outer causal failure, source-manifest join, and Rust decoded-hash stability.

Neither control may be marked as native evidence. The wrapper records
`nativeExecution=false`, `nativeAcceptance=false`, `nativePixelDecode=false`,
`gpuUsed=false`, and `resolveUsed=false` in every report and seal.

## Attempt files and publication seal

The mode-specific attempt layout is:

```text
comparator-control-a04/<mode>-<attempt>/
  request.json
  preflight.json
  <mode>.stdout.bin
  <mode>.stderr.bin
  <mode>-control-report.json
  <mode>-failure.json                 # only when publication cannot complete
  <mode>-publication-seal.json
```

Raw stream files are the observed bytes. The parsed JSON report is a separate
file. The seal never substitutes parsed bytes for raw stream evidence.

```python
@dataclass(frozen=True)
class PublicationSeal:
    schema: int
    mode: str
    attempt: str
    state: str                       # passed, rejected, or structured_failure
    request_sha256: str
    runner_sha256: str
    package_manifest_sha256: str
    package_file_identities: tuple[FileIdentity, ...]
    runtime_binding_sha256: str
    runtime_closure_sha256: str
    source_closure_sha256: str
    capture: CaptureOutcome
    raw_stdout_sha256: str
    raw_stderr_sha256: str
    control_report_sha256: str | None
    control_result_digest: str | None
    native_execution: bool
    native_acceptance: bool
```

The wrapper writes the report with an exclusive descriptor, syncs it, reopens
the same descriptor, hashes the exact bytes, then writes and syncs the seal.
It syncs the attempt directory after each publication step. It makes no claim
of atomicity across the filesystem and the JSON seal. A crash can leave a
partial attempt. A parent readback must reject an incomplete or mismatched
seal and must never promote it.

## Independent parent readback

The parent reads the attempt without importing the comparator or either control.
It requires the attempt directory, request, preflight, raw streams, report,
and seal to be regular files with the sealed identities. It recomputes every
hash, checks the mode-specific argv, verifies the runtime A04 snapshot, and
checks package and input rows before and after the child. It verifies that the
control report's result names and result digest match the seal.

The parent writes a separate `comparator-control-parent-readback-a04.json` only
after those checks. The readback includes `source_only=true`,
`native_execution=false`, `native_acceptance=false`, `descendants_reaped_attested=false`,
and the exact limitation that Python package files are path-and-byte evidence.
The readback is required for qualification. A control exit code alone is not
qualification.

## Rejected alternatives and limits

`run_comparator_controls_a03.py` is not reused as an executor. It is hardwired
to rejected A05, merges streams, and applies its cap after the child exits.
Those choices cannot provide a live deadline or a bounded pipe.

`subprocess.run(timeout=...)` is rejected because a descendant can retain a
pipe after the direct child exits. Merging stderr into stdout is rejected
because it destroys the two stream identities and their separate caps.

The repository Python 3.12.8 virtualenv is rejected because it is not the
current bundled interpreter. The stale A03 runtime and dependency snapshots
remain historical evidence and are never silently relabeled.

The wrapper does not run the Rust producer, Swift producer, CoreText,
CoreGraphics, ImageIO, a decoder, a GPU, Resolve, or the A11 comparator main
entry point. The actual control only loads the frozen A11 validator source and
calls its pure validation functions. Passing these controls proves bounded
source-contract behavior. It does not prove native text rendering, PNG
orientation, media support, playback, listening, or creative acceptance.
