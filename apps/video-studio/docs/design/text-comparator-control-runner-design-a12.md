# Comparator control runner A12

A12 is a source-only design successor to the preserved A10 and A11 designs.
It repairs the A11 identity and canonical-encoding gaps while retaining the
finite capture, publication, and readback contract from A10. It does not
authorize a comparator, control, compiler, child process, native call, media
operation, GPU operation, Resolve operation, or creative review.

## Caller usage

The root caller selects a fixed mode and a fresh private attempt. The runner
selects every source path, runtime authority, child command, limit, and
environment. The caller cannot substitute a report, package, interpreter, or
child script.

```text
UNIT=/Users/aira/projects/remix-gpt-coding-agent/artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01
PY=/Users/aira/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
RUNNER=$UNIT/run_comparator_controls_a12.py

$PY -I -B $RUNNER --mode required-evidence --attempt required-evidence-a12-001
$PY -I -B $RUNNER --mode actual-comparator --attempt actual-comparator-a12-001
$PY -I -B $RUNNER --readback-attempt actual-comparator-a12-001
```

The public library boundary remains small and typed:

```python
class ControlMode(Enum):
    REQUIRED_EVIDENCE = "required-evidence"
    ACTUAL_COMPARATOR = "actual-comparator"

@dataclass(frozen=True)
class AttemptName:
    value: str                         # fresh, bounded, path-component only

@dataclass(frozen=True)
class RunRequest:
    mode: ControlMode
    attempt: AttemptName

def run_control(request: RunRequest) -> RunReport: ...
def readback_attempt(attempt: AttemptName) -> ParentReadback: ...
```

`RunRequest` has no path, digest, report, deadline, cap, environment, or
child-argument field. `readback_attempt` accepts only the runner's own fresh
attempt name. A reused name fails before any existing file is opened.

The root performs source-only preflight before either command. A root-created
readback launch receipt binds the fixed A03 reader source, interpreter bytes,
exact argument vectors, and current A03 preflight raw bytes. The root reopens
and rechecks those values before launching A03, and rechecks them after its
readback. The receipt is external evidence. It contains no loaded-code claim
and does not enter a self-hashing closure. A12 uses an accepted A03 readback
only when that external receipt and its post-readback checks are present.

## Authority and compatibility

A12 preserves these accepted or pending source authorities as distinct facts:

| Authority | Bound identity or status |
| --- | --- |
| A09 runtime report | schema 4, state `current_runtime_filesystem_snapshot_complete_unqualified`, 2,837,530 bytes, SHA `7a43e5606a49bab8d949444707a132b102326cb86d6236e512e0160ac5dd29e8` |
| A09 snapshot helper | `freeze_observer_runtime_a09.py`, SHA `c2ac751a7acdc9327112fad719dab751ba844162b346ff78e296e3eba3783dc4` |
| A09 contract | `observer-runtime-snapshot-contract-a09.md`, SHA `bb03fddb685b5a935a2a5f789ed12bcfb42c9252e8395b85e9c6054418e1341a` |
| A09 rationale | `observer-runtime-snapshot-rationale-a09.md`, SHA `01683726ff727636ac6ef28d1cf894036045cd5dcac8bc911949ea0eae815603` |
| A09 overlay | schema 1, 45 rows, SHA `975e9dbb05e45718c363ebac762c868cd3c85bc952757c4d3aff017dce11b22a` |
| root diagnostic | 1,379,634 bytes, SHA `094c49dc02a1933782dba58fb75eb838587b9a6e7ab357a7c45cf0c61e7405d2` |
| A11 comparator | `compare_text_reports_a11.py`, SHA `e94b6ea3fb671ba66d413594060959bb5ec86f7e4fcffb8e774ababaeb438520` |
| A14 actual control package | manifest SHA `b8e0422d8c2737009978c7fe2a71c6d5a59430ae116afc399b0bf9c69cad7d31`; control SHA `b43e3ada668f150a52ce7c77c7028fdf91b0447a7f15fc08cb040d0ea98617c1` |
| child output | A14 schema 3, ordered 59 results, integer loader bytes |

The A09 report, overlay, diagnostic, A11 comparator, A14 package manifest,
and all A15 source rows are reopened through bounded descriptors before any
child launch. Their raw bytes are compared with their bound identities before
JSON parsing. A12 never treats the overlay as generic RECORD permission.

The A14 child output is structural contract evidence. It does not prove that
CoreText, CoreGraphics, ImageIO, a native font, or a loaded image was used.
The output keeps `native_qualification=false` and its observation-only
qualification fields separate from the structural case gate.

## Typed private model

The public operation delegates to one private kernel. Wire objects stay
private so callers cannot bypass admission or provide alternate observations.

```python
Digest = NewType("Digest", str)       # exactly 64 lower-case hex characters
PathString = NewType("PathString", str)

@dataclass(frozen=True)
class ObservationChecks:
    pathname_before_matched_descriptor: bool
    descriptor_after_matched_before: bool
    pathname_after_read_matched_before: bool
    pathname_final_matched_before: bool

@dataclass(frozen=True)
class ObservedFile:
    path: PathString
    device: int
    inode: int
    mode: int
    links: int
    uid: int
    gid: int
    bytes: int
    mtime_ns: int
    ctime_ns: int
    sha256: Digest
    checks: ObservationChecks

@dataclass(frozen=True)
class ObservedSymlink:
    path: PathString
    target: str
    device: int
    inode: int
    mode: int
    links: int
    uid: int
    gid: int
    bytes: int
    mtime_ns: int
    ctime_ns: int
    pathname_after_read_matched_before: bool
    pathname_final_matched_before: bool

@dataclass(frozen=True)
class RootEndpoint:
    path: PathString
    device: int
    inode: int
    mode: int
    descriptor_matched_path_before: bool
    descriptor_matched_path_final: bool

@dataclass(frozen=True)
class ParentConfinement:
    root: PathString
    runtime_relative_path: PathString
    parent_components_opened: int
    opened_with_no_follow: bool
    parent_chain_matched_after_read: bool
    final_path_matched_descriptor: bool

@dataclass(frozen=True)
class RuntimeRow:
    package: Literal["Pillow", "NumPy"]
    runtime_relative_path: PathString
    record_path: PathString
    record_bytes: int | None
    record_sha256: Digest | None
    bytes_match_observed: bool | None
    sha256_matches_observed: bool | None
    disposition: Literal[
        "strict_declared_match",
        "independently_observed_undeclared",
        "fixed_measured_divergence",
    ]
    observed: ObservedFile
    parent_confinement: ParentConfinement

@dataclass(frozen=True)
class RuntimeDomainIdentity:
    manifest: ObservedFile
    entry: ObservedSymlink
    executable: ObservedFile
    runtime_home: RootEndpoint
    python_root: RootEndpoint
    site_packages: RootEndpoint
    pillow_metadata: ObservedFile
    pillow_record: ObservedFile
    numpy_metadata: ObservedFile
    numpy_record: ObservedFile
    source_diagnostic: ObservedFile
    overlay_file: ObservedFile
    policy: str
    total_rows: int
    total_installed_file_bytes: int
    strict_non_overlay_rows: int
    strict_declared_match_rows: int
    independently_observed_undeclared_rows: int
    fixed_measured_divergence_rows: int
    unexpected_divergence_rows: int
    overlay_consumed_exactly: bool
    overlay_is_wheel_or_record_trust: bool
    provider_origin_attestation: bool
    divergence_cause_verified: bool
    ordered_row_digest: Digest
    overlay_digest: Digest

@dataclass(frozen=True)
class PhaseCounters:
    opened_inputs: int
    read_bytes: int
    path_bytes: int

@dataclass(frozen=True)
class RuntimeDomainObservation:
    phase: Literal["preflight", "prelaunch", "post_child", "parent_readback"]
    identity: RuntimeDomainIdentity
    rows: tuple[RuntimeRow, ...]             # exactly 1,548
    counters: PhaseCounters
    identity_digest: Digest

@dataclass(frozen=True)
class RuntimeSnapshotEvidence:
    variant: Literal["a09-record-overlay-v4"]
    report: ObservedFile
    schema: Literal[4]
    state: Literal["current_runtime_filesystem_snapshot_complete_unqualified"]
    report_ordered_row_digest: Digest
    report_overlay_digest: Digest
    report_domain_identity_digest: Digest

@dataclass(frozen=True)
class DivergenceRow:
    package: Literal["Pillow", "NumPy"]
    path: PathString
    runtime_relative_path: PathString
    declared_bytes: int
    declared_sha256: Digest
    current_bytes: int
    current_sha256: Digest

@dataclass(frozen=True)
class CapturedLoaderRecord:
    path: PathString
    bytes: int
    sha256: Digest

@dataclass(frozen=True)
class StreamObservation:
    bytes: int
    sha256: Digest
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
    pipe_residue_after_final_drain: bool
    cleanup_errors: tuple[str, ...]

@dataclass(frozen=True)
class RunReport:
    schema: Literal[12]
    state: Literal["passed", "rejected", "structured_failure"]
    mode: ControlMode
    attempt: AttemptName
    request_sha256: Digest
    preflight_sha256: Digest
    external_authorization_sha256: Digest
    capture: CaptureOutcome
    child_schema: int | None
    loaded_comparator_source: CapturedLoaderRecord | None
    wrapper_observed_source: ObservedFile | None
    runtime_snapshot: RuntimeSnapshotEvidence
    runtime_preflight: RuntimeDomainObservation
    runtime_prelaunch: RuntimeDomainObservation
    runtime_after: RuntimeDomainObservation | None
    control_report_sha256: Digest | None
    control_result_digest: Digest | None
    output_files: tuple[str, ...]
    output_bytes: int
    source_only: bool
    native_execution: bool
    native_acceptance: bool
    gpu_used: bool
    resolve_used: bool

@dataclass(frozen=True)
class PublicationSeal:
    schema: Literal[12]
    mode: ControlMode
    attempt: AttemptName
    state: str
    request_sha256: Digest
    runner_sha256: Digest
    package_manifest_sha256: Digest
    source_closure_sha256: Digest
    external_authorization_sha256: Digest
    runtime_snapshot: RuntimeSnapshotEvidence
    runtime_preflight_digest: Digest
    runtime_prelaunch: RuntimeDomainObservation
    runtime_after: RuntimeDomainObservation
    capture: CaptureOutcome
    output_files: tuple[ObservedFile, ...]
    raw_stdout_sha256: Digest
    raw_stderr_sha256: Digest
    control_report_sha256: Digest | None
    control_result_digest: Digest | None
    loaded_comparator_source: CapturedLoaderRecord | None
    wrapper_observed_source: ObservedFile | None
    child_schema: int | None
    source_only: bool
    native_execution: bool
    native_acceptance: bool
    gpu_used: bool
    resolve_used: bool

@dataclass(frozen=True)
class ExternalAuthorization:
    schema: Literal[1]
    source_closure_sha256: Digest
    runner_sha256: Digest
    report_facets: tuple[Digest, Digest, Digest]
    mode_map_sha256: Digest
    limits_sha256: Digest

@dataclass(frozen=True)
class ParentReadback:
    schema: Literal[12]
    state: Literal["accepted", "rejected"]
    attempt_directory: DirectoryIdentity
    parent_directory: DirectoryIdentity
    preflight_runtime: RuntimeDomainObservation
    prelaunch_runtime: RuntimeDomainObservation
    sealed_runtime: RuntimeDomainObservation
    reread_runtime: RuntimeDomainObservation
    report_sha256: Digest
    seal_sha256: Digest
    external_authorization: ExternalAuthorization
    source_only: bool
    native_execution: bool
    native_acceptance: bool

Phase = Literal["preflight", "prelaunch", "post_child", "parent_readback"]
JsonValue = object  # private validated JSON value, never caller supplied
FixedAuthorities = object
OverlayEvidence = object
DirectoryIdentity = object
FixedChildCommand = object
Cancellation = object
ChildResult = object
PublicationInputs = object
PublicationResult = object

def observe_runtime_domain(
    phase: Literal["preflight", "prelaunch", "post_child", "parent_readback"],
) -> RuntimeDomainObservation: ...
```

`ObservedSymlink` now carries bytes, `mtime_ns`, and `ctime_ns`. These values
are actual A09 entry identity fields. A symlink target and mode alone cannot
detect the metadata drift that the parent review identified. `CapturedLoaderRecord`
intentionally carries only the child-reported path, byte count, and SHA. The
runner never fabricates device, inode, mode, or loaded-image facts for code
loaded inside another process.

The `PublicationSeal` retains the A10 `external_authorization_sha256` field.
The root creates `ExternalAuthorization` last among the source-authority
files, before the runner starts. The authorization pins the source closure,
runner, report facets, mode map, and finite limits. It does not pin the future
publication seal. The seal may therefore reference the authorization without
creating an `authorization -> seal -> authorization` cycle. The authorization
is outside the seven attempt entries.

## A09 report and overlay validation

`bind_runtime_snapshot` first reopens the fixed report, overlay, diagnostic,
helper, contract, and rationale with bounded descriptor reads. It checks the
raw bytes, file identity, and fixed SHA before parsing. The report must have
exact root keys:

```text
schema, state, workspaceBundle, invocation, runtime, distributions,
recordDeclarationComparison, historicalPathSetComparison, limits, scope
```

The validator requires schema 4, the exact unqualified state, 1,548 rows,
1,503 strict non-overlay rows, 995 declared matches, 508 independently
observed undeclared rows, 45 fixed divergences, zero unexpected divergences,
and `totalInstalledFileBytes=45567887`. It requires the exact Pillow-then-
NumPy order, unique runtime-relative paths, historical path-set hashes, and
all A09 limit fields.

The separate overlay has root keys `schema`, `state`, `sourceDiagnostic`,
`rowCount`, `scope`, and `rows`. It must have schema 1, the fixed state, 45
rows, exact seven-field rows, and the exact diagnostic identity. The validator
rejects a changed, duplicated, removed, added, or reordered overlay row. The
diagnostic explains exactly those 45 fixed rows. It does not waive any other
RECORD mismatch.

Each phase rereads the current runtime through descriptor-relative, no-follow
opens. It observes the interpreter entry and target, executable, runtime home,
Python root, site-packages root, both package metadata files, both RECORD
files, all 1,548 installed rows, the diagnostic, and the overlay. Strict rows
must match their declarations and the report. Undeclared rows must match the
report with null declaration fields. Fixed divergence rows must match the
report and the exact overlay. Any additional mismatch fails closed.

Four `RuntimeDomainObservation` values are retained: `preflight`, `prelaunch`,
`post_child`, and `parent_readback`. Domain identity excludes only the phase
label. It includes all fields, rows, roots, flags, counts, ordered row digest,
and overlay digest. Counters are checked against caps but are not required to
be equal between phases.

## Closed digest encoding

The runner uses binary SHA-256 facets. It does not depend on Python mapping
order or a JSON serializer.

```text
U8(x)       = one unsigned byte
U32(x)      = four-byte big-endian unsigned integer
U64(x)      = eight-byte big-endian unsigned integer
I64(x)      = eight-byte big-endian two's-complement integer
BOOL(x)     = U8(1) for true, U8(0) for false
S(x)        = U32(len(UTF8(x))) || UTF8(x)
RAW32(x)    = 32 bytes after lower-case hexadecimal validation
OPTION(x)   = U8(0) for null, or U8(1) || encoded value
```

Strings are strict UTF-8, contain no NUL, and contain no surrogate scalar.
Paths use the A09 path grammar. Integers fit their declared widths. JSON
booleans never accept integer `0` or `1` as a substitute.

The row separator is `video-studio/runtime-rows/v1` plus one NUL byte. The
overlay separator is `video-studio/runtime-overlay/v1` plus one NUL byte. Row
order is the fixed Pillow rows followed by the fixed NumPy rows. An installed
row encodes package, runtime path, RECORD path, optional declaration fields,
disposition, all regular-file identity fields, four regular-file checks, and
all parent-confinement fields.

The corrected symlink encoding is:

```text
S(path) S(target)
U64(device) U64(inode) U32(mode)
U64(links) U64(uid) U64(gid) U64(bytes)
I64(mtime_ns) I64(ctime_ns)
BOOL(pathname_after_read_matched_before)
BOOL(pathname_final_matched_before)
```

Root endpoints encode path, device, inode, mode, and both endpoint checks.
The phase-independent domain encoding includes all twelve fixed authority
objects, policy, all seven comparison counts, all four policy flags, row
digest, and overlay digest. It does not encode the phase label or counters.

The canonical JSON writer used for new attempt files has one exact escape
algorithm:

* Encode UTF-8 without a trailing newline.
* Sort object keys by their UTF-8 bytes.
* Preserve array order.
* Use `,` and `:` without spaces.
* Emit integers in base ten without leading zeroes or exponent notation.
* Emit `true`, `false`, and `null` as JSON literals.
* Escape `"` as `\\"` and `\\` as `\\\\`.
* Escape controls U+0008, U+0009, U+000A, U+000C, and U+000D as `\\b`,
  `\\t`, `\\n`, `\\f`, and `\\r`.
* Escape every other U+0000 through U+001F as `\\u00XX`, with uppercase
  hexadecimal digits.
* Do not escape `/` or non-ASCII scalar values.
* Reject duplicate keys, NaN, infinity, floats, invalid UTF-8, NUL strings,
  and surrogate scalars before writing.

The quotation escape is one U+005C byte followed by a quotation mark. The
reverse-solidus escape is two U+005C bytes. Each named control escape uses one
U+005C byte followed by its lower-case JSON letter. Each `u00XX` escape uses
one U+005C byte, the lower-case letter `u`, and four upper-case hex digits.

The existing writer vector remains a required control:

```text
{"a":1,"b":true,"n":null,"s":"é"}
```

It is 34 UTF-8 bytes with SHA-256
`75a5e1754766234964e2cc913129d7dbdc36e806b6e4346fc2412794490e74ca`.

The previous A11 `domain-one` hash is retired. Its logical fixture omitted
the corrected symlink fields, so its old 1,368-byte value cannot be reused.
Before implementation, a vector artifact must freeze one complete domain
fixture, generated bytes, byte count, and SHA. The complete fixture is:

```text
policy = "strict RECORD declarations except the exact fixed measured divergence overlay"
counts = (total_rows=1, total_installed_file_bytes=2,
          strict_non_overlay_rows=3, strict_declared_match_rows=4,
          independently_observed_undeclared_rows=5,
          fixed_measured_divergence_rows=6, unexpected_divergence_rows=7)
flags = (overlay_consumed_exactly=true,
         overlay_is_wheel_or_record_trust=false,
         provider_origin_attestation=false,
         divergence_cause_verified=false)

manifest       = file("/m", 1, 2, 33188, 1, 501, 20, 3, 4, 5, 00*32, true×4)
entry          = symlink("/e", "python3.12", 6, 7, 41471, 1, 501, 20, 9, 10, 11, true, true)
executable     = file("/x", 12, 13, 33188, 1, 501, 20, 14, 15, 16, 11*32, true×4)
runtime_home   = endpoint("/h", 17, 18, 16877, true, true)
python_root    = endpoint("/p", 19, 20, 16877, true, true)
site_packages  = endpoint("/s", 21, 22, 16877, true, true)
pillow_meta    = file("/pm", 23, 24, 33188, 1, 501, 20, 25, 26, 27, 22*32, true×4)
pillow_record  = file("/pr", 28, 29, 33188, 1, 501, 20, 30, 31, 32, 33*32, true×4)
numpy_meta     = file("/nm", 34, 35, 33188, 1, 501, 20, 36, 37, 38, 44*32, true×4)
numpy_record   = file("/nr", 39, 40, 33188, 1, 501, 20, 41, 42, 43, 55*32, true×4)
diagnostic     = file("/d", 45, 46, 33188, 1, 501, 20, 47, 48, 49, 66*32, true×4)
overlay_file   = file("/o", 50, 51, 33188, 1, 501, 20, 52, 53, 54, 77*32, true×4)
```

Here `file(path, device, inode, mode, links, uid, gid, bytes, mtime_ns,
ctime_ns, sha, checks)` and `symlink(...)` are fixture constructors, not
runtime APIs. `00*32` means thirty-two zero digest bytes, and each `NN*32`
means thirty-two repetitions of that byte. The vector artifact must expand
these values, include the fixed one-row and one-overlay facets, and record the
exact resulting bytes and digest before implementation. A stale A11 digest or
an implementation-generated expected value is invalid.

## Source closure and authorization

The source closure is a canonical, bounded list of external inputs. It binds
the A14 package manifest and every A14 source row, all 21 A15 source rows, the
A11 comparator source, the A14 source, schema, and rationale, the A09 helper,
contract, rationale, report, diagnostic, overlay, the A03 reader source and
its accepted root launch receipt, the canonical-vector artifact, the capture
policy, the exact A14 schema-3 result schedule, and the A12 runner source and
contract. Every item has a descriptor identity, byte count, and raw SHA.

The closure also binds the A09 report row, overlay, and domain facet digests,
the complete A10 limits table, the fixed mode map, and the exact child argv.
It excludes its own output, the external authorization, and any loaded-image
or provider-origin assertion. The root computes the closure from fixed ordered
records. It rejects duplicate paths, path aliases, and a record whose bytes
changed after the source hash.

`ExternalAuthorization` is created last after the source closure is complete.
The root reopens every closure item, the A03 receipt, and the A09 report before
writing it. It then writes and fsyncs the authorization outside the attempt
directory. The runner verifies its raw identity and every field before the
preflight scan. The authorization pins the closure SHA, runner SHA, three A09
facet digests, mode map, and limits. It does not pin the future publication
seal, so the later seal can carry `external_authorization_sha256` without a
hash cycle.

## Finite limits retained from A10

A12 inherits these values without reduction:

| Limit | Value |
| --- | ---: |
| child deadline | 15 seconds |
| SIGTERM grace | 2 seconds |
| final pipe drain | 1 second |
| direct-child reap | 1 second |
| stdout retained prefix | 1 MiB |
| stderr retained prefix | 128 KiB |
| request JSON | 256 KiB |
| preflight JSON | 4 MiB |
| control or failure report | 1 MiB |
| publication seal | 4 MiB |
| aggregate attempt output | 16 MiB |
| maximum attempt entries | 7 |
| maximum one runtime file | 128 MiB |
| maximum runtime read per scan | 1 GiB |
| maximum input opens per scan | 65,536 |
| maximum RECORD rows per package | 4,096 |
| maximum total RECORD rows | 8,192 |
| maximum path bytes | 4,096 |
| maximum total path bytes | 32 MiB |
| expected installed rows | 1,548 |
| expected overlay rows | 45 |
| maximum diagnostic bytes | 2 MiB |

The attempt allowlist remains exactly:

```text
request.json
preflight.json
<mode>.stdout.bin
<mode>.stderr.bin
<mode>-control-report.json
<mode>-failure.json
<mode>-publication-seal.json
```

The failure file is optional and is emitted only for a structured failure. A
rejection still has a bounded control report when enough context exists. The
runner must account for every file before creation and reject an entry or
aggregate overflow before copying bytes. It does not claim to bound Python
allocator capacity, RSS, native framework allocation, or operating-system
memory.

## Execution and cleanup pseudocode

The implementation owns one ordered state machine. Every phase records its
completed or failed transition in memory. No later phase can promote a
partial result to accepted evidence.

```text
run_control(request):
  validate_mode_and_attempt(request)
  create_attempt_exclusive()
  bind_package_a15_a09_a14_and_external_authorities()
  bind_raw_report_overlay_diagnostic_before_parse()
  validate_a09_schema_overlay_diagnostic_and_all_facets()
  require_external_authorization_is_present_and_matches()
  observe_runtime_domain(preflight)
  write_sync_reopen_and_verify(request.json, preflight.json)
  observe_runtime_domain(prelaunch)
  require(prelaunch.identity == preflight.identity == report_identity)
  capture = capture_fixed_child_with_bounded_cleanup()
  observe_runtime_domain(post_child)
  parse_child_schema3_and_require_exact_59_result_order()
  write_sync_reopen_and_verify_streams_report_and_seal()
  require_output_allowlist_and_aggregate_caps()
  require_seal_external_authorization_hash_matches()
  return bounded_report
```

`capture_fixed_child_with_bounded_cleanup` distinguishes
`launch_attempted` from `process_started`. It checks cancellation before
`Popen`, records an attempted launch only after the call boundary, and records
`process_started` only after a process object and PID exist. Every exception
after successful `Popen`, including a non-`OSError` setup exception, enters the
same cleanup path.

The capture backend starts a new process session, uses the fixed interpreter,
`-I`, `-B`, fixed child path, fixed working directory, no shell, and
`close_fds=True`. It drains stdout and stderr continuously with a selector.
At 15 seconds it sends SIGTERM, waits at most 2 seconds, then sends SIGKILL
when the direct child remains. It drains for at most 1 additional second and
waits for the direct child for at most 1 second. Parent pipe descriptors then
close unconditionally. A descendant that keeps a pipe open is recorded as
`pipe_residue_after_final_drain=true`; the runner never claims descendants
were reaped unless it has an explicit bounded attestation. It never waits
forever for a descendant-held pipe.

The stream observer retains only the allowed prefixes, hashes every accepted
byte, records total bytes and limit hits, and stops accepting bytes at the
prefix cap. It checks cancellation and the aggregate cap during every read.
It records timeout, cancellation, termination, direct-child wait, pipe
residue, and cleanup errors in the capture object.

The runner reobserves the complete runtime domain after cleanup even when the
child rejects, times out, or exits nonzero. A failure to perform that
observation is a structured failure, not a successful control rejection.
The parent readback independently rereads every output, the attempt and
parent directories, the A09 authorities, and a fourth runtime domain scan.

## Publication and external seal

New JSON is encoded into bounded application-owned bytes before exclusive file
creation. The writer checks the exact file budget, writes through one owned
descriptor, flushes, calls `fsync`, reopens the same file, and compares exact
bytes, size, and SHA. The parent directory is reopened and fsynced after the
file publication when the platform permits it. A failed write retains the
bounded written prefix, byte count, SHA, flush status, fsync status, and the
failure code in the structured failure record.

`PublicationSeal` contains the complete preflight, prelaunch, and post-child
observations, capture facts, output identities, report digests, source
closure digest, external authorization SHA, and all no-native flags. The root
creates `ExternalAuthorization` in a separate private root-owned location
after the source closure is frozen and before the runner starts. The
authorization pins:

```text
source closure SHA
runner SHA
report row/overlay/domain facet digests
mode-map SHA
finite-limit SHA
```

The root reopens all pinned inputs while creating authorization, then the
runner writes the authorization SHA into the later seal. Parent readback
reopens authorization, seal, and all pinned inputs. This order is acyclic:

```text
fixed sources + runtime report + A03 receipt
  -> source closure
  -> external authorization
  -> runner preflight and publication seal
  -> parent readback acceptance
```

The authorization is not included in the attempt allowlist. Its SHA is copied
into `request.json`, `preflight.json`, and the publication seal. The complete
authorization remains a final external root fact and is required for accepted
readback.

## Module ownership and signatures

```python
def bind_fixed_authorities() -> FixedAuthorities: ...
def validate_a09_report(raw: bytes, expected: FixedAuthorities) -> RuntimeSnapshotEvidence: ...
def validate_overlay(raw: bytes, diagnostic: ObservedFile) -> OverlayEvidence: ...
def observe_runtime_domain(phase: Phase) -> RuntimeDomainObservation: ...
def encode_rows(rows: tuple[RuntimeRow, ...]) -> bytes: ...
def encode_overlay(rows: tuple[DivergenceRow, ...]) -> bytes: ...
def encode_domain(identity: RuntimeDomainIdentity) -> bytes: ...
def canonical_json(value: JsonValue) -> bytes: ...
def capture_child(command: FixedChildCommand, cancel: Cancellation) -> CaptureOutcome: ...
def validate_child(raw: bytes, mode: ControlMode) -> ChildResult: ...
def write_publication(files: PublicationInputs) -> PublicationResult: ...
def readback_attempt(attempt: AttemptName) -> ParentReadback: ...
```

| Module | Owns |
| --- | --- |
| CLI/admission | modes, fresh names, fixed environment selection |
| authority binder | package, A15, A09, A14, A03 receipt, and raw identity checks |
| A09 verifier | schema 4, overlay, diagnostic, report facets, and fixed counts |
| runtime observer | descriptor traversal, no-follow opens, rows, limits, and phase facts |
| canonical digest | row, overlay, domain, and JSON writer bytes |
| capture backend | selector drain, deadlines, signals, direct-child reap, and cleanup |
| child verifier | A14 schema 3, exact 59 result names, typed fields, and loader facts |
| publication writer | bounded JSON, exclusive files, sync, reopen, allowlist, and totals |
| external seal | root-created source/seal authorization, outside attempt directory |
| parent readback | independent directory, file, authority, output, and fourth-domain checks |

No module accepts caller-provided runtime paths, report paths, digest strings,
child arguments, or cap values. The runtime observer and A09 verifier share
typed values only. They do not maintain a second package model.

## Required controls before implementation

Pure controls must freeze the exact byte count and SHA for the complete domain
vector described above. They must also retain the known rows-empty, rows-one,
overlay-one, and canonical JSON vectors. Every control compares generated
bytes, length, and SHA. A one-byte change in a row, symlink metadata, overlay,
root endpoint, policy, count, flag, or digest must change the corresponding
facet. A phase-label change must not change domain identity. A counter change
must not change domain identity but must be checked against that phase's cap.

The shared parser and gate path must be exercised by full-path controls. The
controls must reject, before child launch:

* A07, A08, schema-3, missing, stale, or arbitrary runtime reports;
* changed A09 root keys, state, counts, policy, historical hashes, or scope;
* omitted, duplicated, added, reordered, or changed overlay rows;
* a changed symlink byte count, mtime, ctime, target, identity, or check flag;
* a changed runtime root, executable, METADATA, RECORD, or installed row;
* an extra RECORD mismatch outside the fixed 45 overlay rows;
* a diagnostic that no longer produces exactly the fixed overlay;
* a child report with schema other than 3, non-integer loader bytes, unknown
  fields, wrong result order, missing result, or fabricated loader metadata;
* a report, stream, preflight, seal, row-read, entry, or aggregate overflow.

The capture state machine needs pure transitions for pre-launch cancellation,
Popen failure, post-Popen setup failure, child timeout, descendant-held pipes,
SIGTERM, SIGKILL, final drain, direct-child reap, and cleanup failure. The
publication control must exercise an exact-boundary file and one-byte overflow.
The parent readback control must mutate one output byte and one directory
identity while retaining the seal, and must reject both.

No control may call a reduced allocation projection, count-only report parser,
or separate digest implementation. A source-only control result remains a
control result. It does not establish native text support or creative quality.

## Rationale

A11 corrected the report authority and binary facet structure, but its
symlink type omitted three actual identity fields and its JSON escape rule
allowed multiple RFC spellings. A12 makes those fields and bytes explicit.
The complete logical domain fixture prevents an implementation from silently
reusing the stale A11 domain hash. The final vector hash is frozen by a
separate pre-implementation artifact, so this design does not invent a
measurement.

The runner remains one deep module because the caller should not assemble
observer, digest, capture, and publication fragments. Private phase types
prevent a preflight digest from being mistaken for a post-child observation.
The same central validator is reused for the runner and full-path controls.

The external authorization is deliberately separate from the publication
seal. Creating it last among the source authorities gives the root a final
source binding before execution. The seal records that fixed authorization
SHA, so no seal-to-authorization hash cycle exists. The attempt stays within
seven entries and the root can independently read both records.

## Alternatives rejected

### Trust the saved A09 report and two facet digests

This would miss changes to current executable and package files. Every phase
must reread the 1,548-row domain and compare it with the report.

### Add a synthetic overlay digest field to the A09 report

That would mutate a frozen report schema. A12 derives the overlay digest from
the separately pinned overlay and compares its exact rows.

### Create authorization after the publication seal

That would force the seal to be rewritten or create a seal-to-authorization
cycle. A12 creates authorization after source closure but before execution,
then records its fixed SHA in the later seal.

### Claim the child loaded the observed source

The child loader payload proves only its reported path, byte count, and SHA.
It does not prove a loaded image, and the design retains that limitation.

### Copy the runtime into a staging tree

Copying would change the runtime under test and introduce an unproved staging
equivalence. A12 records the residual path-replacement race explicitly.

## Verification boundary and risks

The root receipt can bind a reader source, interpreter, exact argv, and raw
preflight bytes. It cannot attest that the interpreter loaded a particular
image. A12 therefore keeps loaded-image, provider-origin, native-execution,
playback, hearing, and creative-acceptance fields false.

Four domain scans reduce ordinary drift but do not create an atomic operating-
system snapshot across the final scan and a path-based child launch. A
descendant can retain a pipe after the direct child exits; A12 records that
condition and closes parent descriptors after the bounded drain.

Logical read and output caps do not prove process RSS or native framework
memory limits. The A09 overlay remains a fixed local measured classification,
not a generic RECORD waiver or provider attestation. The A03 readback and A14
control remain unexecuted until their own source, build, and root-authority
reviews complete.

## Next checkpoint

Freeze the A12 full-domain vector artifact and verify its bytes and hash before
implementation. Then review the shared runtime observer, canonical writer,
capture state machine, publication writer, and parent readback independently.
Only after those reviews may a root-created authorization and child run be
considered.
