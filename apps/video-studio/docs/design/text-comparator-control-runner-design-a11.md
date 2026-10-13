# Comparator control runner A11

A11 is a source-only successor to the frozen A10 design. It closes the A09
report binding and the digest wire before implementation. A10 remains
byte-preserved.

No comparator, control, compiler, child process, native, media, GPU, Resolve,
or project operation is authorized by this document.

## Caller usage

The caller selects one fixed mode and one fresh private attempt. The runner
selects every source path, runtime input, report, limit, environment, and child
command.

```text
UNIT=/Users/aira/projects/remix-gpt-coding-agent/artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01
PY=/Users/aira/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
RUNNER=$UNIT/run_comparator_controls_a11.py

$PY -I -B $RUNNER --mode required-evidence --attempt required-evidence-a11-001
$PY -I -B $RUNNER --mode actual-comparator --attempt actual-comparator-a11-001
```

The public source boundary is:

```python
class ControlMode(Enum):
    REQUIRED_EVIDENCE = "required-evidence"
    ACTUAL_COMPARATOR = "actual-comparator"

@dataclass(frozen=True)
class RunRequest:
    mode: ControlMode
    attempt: str

def run_control(request: RunRequest) -> RunReport: ...
def readback_attempt(attempt_name: str) -> ParentReadback: ...
```

`RunRequest` has no path, digest, report, deadline, cap, environment, or child
argument field. The caller cannot select an older attempt or replace the A09
runtime authority. Attempt creation uses exclusive `mkdir`; a reused name
fails before opening any existing evidence.

## Exact A09 authority

The current A09 report is complete and remains unqualified. A11 binds this
exact raw file before parsing or deriving any digest:

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| `observer-runtime-snapshot-attempt-a09/runtime-snapshot-a09.json` | 2,837,530 | `7a43e5606a49bab8d949444707a132b102326cb86d6236e512e0160ac5dd29e8` |
| `freeze_observer_runtime_a09.py` | — | `c2ac751a7acdc9327112fad719dab751ba844162b346ff78e296e3eba3783dc4` |
| `observer-runtime-snapshot-contract-a09.md` | — | `bb03fddb685b5a935a2a5f789ed12bcfb42c9252e8395b85e9c6054418e1341a` |
| `observer-runtime-snapshot-rationale-a09.md` | — | `01683726ff727636ac6ef28d1cf894036045cd5dcac8bc911949ea0eae815603` |
| `observer-runtime-record-divergence-overlay-a09.json` | 25,945 | `975e9dbb05e45718c363ebac762c868cd3c85bc952757c4d3aff017dce11b22a` |
| `runtime-record-declaration-diagnostic-a01.json` | 1,379,634 | `094c49dc02a1933782dba58fb75eb838587b9a6e7ab357a7c45cf0c61e7405d2` |

The report variant is fixed:

```text
RuntimeSnapshotVariant::A09_RECORD_OVERLAY_V4
schema = 4
state = current_runtime_filesystem_snapshot_complete_unqualified
```

The report path, byte count, and raw SHA are source-bound constants. The
consumer reopens the file through a bounded descriptor, verifies its regular
file identity and complete bytes, then parses strict UTF-8 JSON. It never
serializes the report again before comparing the bound raw identity.

The report root keys are exactly:

```text
schema, state, workspaceBundle, invocation, runtime, distributions,
recordDeclarationComparison, historicalPathSetComparison, limits, scope
```

The validator requires the complete A09 nested key sets and exact literals.
It requires 1,548 installed rows, 1,503 strict non-overlay rows, 995 strict
declared matches, 508 independently observed undeclared rows, 45 fixed
divergences, zero unexpected divergences, and `totalInstalledFileBytes`
`45567887`. The two distributions remain ordered Pillow then NumPy, with 238
and 1,310 rows. Installed rows remain sorted by runtime-relative path within
each distribution, and paths remain unique across the two distributions.

`recordDeclarationComparison.policy` is a string with this exact value:

```text
strict RECORD declarations except the exact fixed measured divergence overlay
```

It is not an object, an empty mapping, or a caller-provided policy. All A09
JSON booleans must decode as JSON booleans. All counts and byte fields must be
JSON integers in their declared nonnegative ranges. Floats, numeric strings,
negative counts, unknown fields, duplicate keys, invalid UTF-8, and trailing
non-whitespace fail before child launch.

The validator also checks the exact A09 `workspaceBundle`, `invocation`,
`runtime`, `distributions`, `historicalPathSetComparison`, `limits`, and
`scope` contracts. Historical path-set hashes use sorted UTF-8
runtime-relative paths, one trailing `0a` byte per path, and SHA-256 over the
complete concatenation. The report's three historical hashes and complete
added/removed lists must match that rule.

The separate overlay has exact root keys `schema`, `state`, `sourceDiagnostic`,
`rowCount`, `scope`, and `rows`; schema is `1`, state is
`fixed_measured_RECORD_divergence_overlay_unqualified`, and row count is `45`.
Every row has exactly `package`, `path`, `runtimeRelativePath`,
`declaredBytes`, `declaredSha256`, `currentBytes`, and `currentSha256`. The
overlay is reopened and hashed independently. It is compared with the
diagnostic's exact mismatch projection. A changed, added, removed, duplicated,
or reordered overlay row fails. The report does not gain a synthetic overlay
digest field.

## Typed boundary

The private runner replaces A10's ambiguous `report_facets` tuple with three
named values: two report facets and one phase-independent domain identity.

```python
Digest = NewType("Digest", str)  # exactly 64 lowercase hex characters

@dataclass(frozen=True)
class ObservationChecks:
    pathname_before_matched_descriptor: bool
    descriptor_after_matched_before: bool
    pathname_after_read_matched_before: bool
    pathname_final_matched_before: bool

@dataclass(frozen=True)
class ObservedFile:
    path: str
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
    path: str
    target: str
    device: int
    inode: int
    mode: int
    links: int
    uid: int
    gid: int
    pathname_after_read_matched_before: bool
    pathname_final_matched_before: bool

@dataclass(frozen=True)
class RootEndpoint:
    path: str
    device: int
    inode: int
    mode: int
    descriptor_matched_path_before: bool
    descriptor_matched_path_final: bool

@dataclass(frozen=True)
class ParentConfinement:
    root: str
    runtime_relative_path: str
    parent_components_opened: int
    opened_with_no_follow: bool
    parent_chain_matched_after_read: bool
    final_path_matched_descriptor: bool

@dataclass(frozen=True)
class RuntimeRow:
    package: str
    runtime_relative_path: str
    record_path: str
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
    comparison_counts: tuple[int, int, int, int, int, int, int]
    comparison_flags: tuple[bool, bool, bool, bool]
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
    counters: PhaseCounters
    domain_identity_digest: Digest

@dataclass(frozen=True)
class RuntimeSnapshotEvidence:
    variant: Literal["a09-record-overlay-v4"]
    report: ObservedFile
    report_schema: Literal[4]
    report_state: Literal["current_runtime_filesystem_snapshot_complete_unqualified"]
    report_ordered_row_digest: Digest
    report_overlay_digest: Digest
    report_domain_identity_digest: Digest

def observe_runtime_domain(
    phase: Literal["preflight", "prelaunch", "post_child", "parent_readback"],
) -> RuntimeDomainObservation: ...
```

`RuntimeRow` includes the complete A09 installed-file observation, including
checks and parent confinement. A phase cannot replace those facts with a
count-only row. The three counters are phase telemetry, not identity. Each is
checked against its own A09 cap and retained in the phase record; counters are
never compared for equality.

`RuntimeDomainIdentity` has no phase field. Four domain observations compare
every identity field and digest. The comparison excludes only the phase label
because it is outside the identity type. It does not ignore a row, overlay,
root, diagnostic, policy, count, flag, or descriptor check.

## Closed digest bytes

The runner uses a fixed binary digest encoding. Digest bytes never depend on
JSON object order, JSON whitespace, Python dictionary order, or a platform
serializer. Each digest is SHA-256 over its complete canonical bytes.

Primitive encodings are:

```text
U8(x)       = one unsigned byte
U32(x)      = four-byte big-endian unsigned integer
U64(x)      = eight-byte big-endian unsigned integer
I64(x)      = eight-byte big-endian two's-complement integer
BOOL(x)     = U8(1) for true, U8(0) for false
S(x)        = U32(len(UTF8(x))) || UTF8(x)
RAW32(x)    = 32 raw digest bytes after lowercase-hex validation
OPTION(x)   = U8(0) for null, or U8(1) || encoded value
```

Strings are strict UTF-8, contain no NUL, and use their exact validated value.
Paths are validated by the A09 contract before this encoding. Digest strings
must be exactly 64 lowercase hexadecimal characters; the digest encoding uses
their 32 decoded bytes, never the hex text. Integers must fit the primitive
width. A09 JSON `null` maps only to `OPTION(0)`. JSON booleans map only to
`BOOL`; integer `0` and `1` are not accepted as booleans.

### Ordered row facet

The exact domain separator is the ASCII byte string
`video-studio/runtime-rows/v1`, followed by one NUL byte. The bytes are:

```text
ROWS_BYTES = b"video-studio/runtime-rows/v1\0"
             || U32(row_count)
             || row_0 || row_1 || ... || row_n
```

Rows use the A09 order: Pillow rows in their required runtime-relative-path
order, followed by NumPy rows in their required order. The runner rejects any
order change before hashing. Each row encodes this exact sequence:

```text
S(package)
S(runtime_relative_path)
S(record_path)
OPTION(U64(record_bytes))
OPTION(RAW32(record_sha256))
OPTION(BOOL(bytes_match_observed))
OPTION(BOOL(sha256_matches_observed))
U8(disposition_tag)                 # 1 strict, 2 undeclared, 3 overlay
U8(1)                                # ObservedFile kind: regular file
S(observed.path)
U64(observed.device) U64(observed.inode) U32(observed.mode)
U64(observed.links) U64(observed.uid) U64(observed.gid)
U64(observed.bytes) I64(observed.mtime_ns) I64(observed.ctime_ns)
RAW32(observed.sha256)
BOOL(pathname_before_matched_descriptor)
BOOL(descriptor_after_matched_before)
BOOL(pathname_after_read_matched_before)
BOOL(pathname_final_matched_before)
S(parent_confinement.root)
S(parent_confinement.runtime_relative_path)
U64(parent_confinement.parent_components_opened)
BOOL(parent_confinement.opened_with_no_follow)
BOOL(parent_confinement.parent_chain_matched_after_read)
BOOL(parent_confinement.final_path_matched_descriptor)
```

`report_ordered_row_digest` is this SHA-256 over the parsed A09 installed
rows. `ordered_row_digest` for each live phase uses the same encoding and must
equal the report facet before phase comparison.

### Overlay facet

The exact separator is the ASCII byte string
`video-studio/runtime-overlay/v1`, followed by one NUL byte:

```text
OVERLAY_BYTES = b"video-studio/runtime-overlay/v1\0"
                || U32(45)
                || overlay_row_0 || ... || overlay_row_44
```

Overlay rows retain the exact order of the bound overlay file. The runner
rejects any order change. Each row encodes:

```text
S(package)
S(path)
S(runtime_relative_path)
U64(declared_bytes)
RAW32(declared_sha256)
U64(current_bytes)
RAW32(current_sha256)
```

`report_overlay_digest` is the SHA-256 over these bytes. The current phase
overlay digest uses the same rows and must equal the report facet. The report's
embedded `fixedMeasuredDivergenceOverlay` observation binds the overlay file;
it is not substituted for these 45 rows.

### Phase-independent domain identity

The exact separator is the ASCII byte string
`video-studio/runtime-domain/v1`, followed by one NUL byte. The binary field
order is:

```text
DOMAIN_BYTES = b"video-studio/runtime-domain/v1\0" || U32(1)
               || U8(1) || encode_observed_file(manifest)
               || U8(2) || encode_observed_symlink(entry)
               || U8(1) || encode_observed_file(executable)
               || U8(3) || encode_root_endpoint(runtime_home)
               || U8(3) || encode_root_endpoint(python_root)
               || U8(3) || encode_root_endpoint(site_packages)
               || U8(1) || encode_observed_file(pillow_metadata)
               || U8(1) || encode_observed_file(pillow_record)
               || U8(1) || encode_observed_file(numpy_metadata)
               || U8(1) || encode_observed_file(numpy_record)
               || U8(1) || encode_observed_file(source_diagnostic)
               || U8(1) || encode_observed_file(overlay_file)
               || S(policy)
               || U64(total_rows) U64(total_installed_file_bytes)
               || U64(strict_non_overlay_rows) U64(strict_declared_match_rows)
               || U64(independently_observed_undeclared_rows)
               || U64(fixed_measured_divergence_rows)
               || U64(unexpected_divergence_rows)
               || BOOL(overlay_consumed_exactly)
               || BOOL(overlay_is_wheel_or_record_trust)
               || BOOL(provider_origin_attestation)
               || BOOL(divergence_cause_verified)
               || RAW32(ordered_row_digest)
               || RAW32(overlay_digest)
```

`encode_observed_file` uses the exact path, identity fields, raw SHA, and four
regular-file check booleans shown in the row encoding. `encode_observed_symlink`
uses path, target, device, inode, mode, links, uid, gid, then its two A09
symlink check booleans. `encode_root_endpoint` uses path, device, inode, mode,
then its two endpoint check booleans. The type tags are fixed in the field
order and are not caller data.

`domain_identity_digest` is SHA-256 over these bytes. It includes all authority
facts needed to compare the four scans. It excludes phase by construction.
The report facet is built from the exact A09 report fields and the separately
bound overlay. Each live phase must equal the report domain identity and the
other live identities. A changed phase counter fails its own cap check, but a
different counter does not create a false domain drift.

## JSON publication rules

The A09 report is hashed as its existing raw bytes. New runner files use one
canonical JSON writer with these rules:

1. Encode UTF-8 without a trailing newline.
2. Sort object keys by their UTF-8 byte sequence. All schema keys are ASCII.
3. Preserve array order. Never sort arrays.
4. Use separators `,` and `:` with no spaces.
5. Emit integers in base ten without leading zeroes or exponent notation.
6. Emit `true`, `false`, and `null` as their JSON literals.
7. Escape quote, reverse solidus, and control bytes using the RFC 8259 JSON
   escapes. Do not escape `/`; non-ASCII scalar values use UTF-8 directly.
8. Reject NaN, infinity, floats, duplicate keys, unknown fields, and invalid
   UTF-8 before writing.

The exact writer self-check vector is the 34-byte UTF-8 sequence:

```text
{"a":1,"b":true,"n":null,"s":"é"}
```

Its SHA-256 is
`75a5e1754766234964e2cc913129d7dbdc36e806b6e4346fc2412794490e74ca`.

## Execution and ownership

The A10 phase order remains, with the exact report facets inserted before the
first child:

1. Validate mode and attempt name. Create the attempt exclusively.
2. Bind the exact package, A15 inputs, source rows, A09 helper identities,
   report bytes, diagnostic, and overlay.
3. Parse the report and derive `report_ordered_row_digest`,
   `report_overlay_digest`, and `report_domain_identity_digest`.
4. Observe the complete 1,548-row domain as `preflight`. Check every row,
   overlay, root, report, policy, and digest. Write bounded request and
   preflight files.
5. Observe `prelaunch`. Compare its domain identity with `preflight` and the
   report. Check counters independently. Reject drift before launch.
6. Launch the fixed A14 child with `PY`, `-I`, `-B`, no shell, fixed working
   directory, and `close_fds=True`. Drain both streams continuously under the
   reviewed deadline, prefix, cancellation, TERM, KILL, and reap rules.
7. Observe `post_child` after cleanup. Require its identity to equal the
   report, preflight, and prelaunch identities. Parse the exact child schema.
8. Write the bounded control report and publication seal. Reopen and recompute
   all raw and canonical digests. Enforce the output allowlist and caps.
9. Parent readback independently reopens the report, seal, streams, control
   report, A09 inputs, and all runtime files. It observes `parent_readback` and
   recomputes the same domain identity. It compares every identity field and
   digest, excluding only the phase label.

The runtime observer owns all descriptor-relative opens, bounded reads, path
confinement, and phase counters. The snapshot verifier owns A09 schema and
report facets. The canonical digest module owns the three binary encodings.
The capture backend owns process liveness and stream limits. The publication
writer owns canonical JSON, sync, reopen, and allowlist checks. Parent readback
owns independent remeasurement and seal verification.

No module accepts a caller-provided runtime path or digest. The four phase
observations are retained as separate typed records. No logical cap is claimed
to bound Python allocator overhead, RSS, or operating-system memory.

## Source closure and authorization

The source closure binds the fixed A14 package, A15 input rows, the A11 runner
source and design contract, the A09 helper/contract/rationale/report,
diagnostic, overlay and their exact digests, the canonical digest version and
test-vector values, the reviewed capture policy, and the A14 child schema.

The source closure excludes itself and excludes the external authorization.
The external authorization is created last and pins the complete source
closure, runner, A09 report facets, diagnostic, overlay, mode map, and finite
limits. The authorization hash is not included in any earlier source closure
file. A report hash or facet digest cannot be replaced by a caller path.

## Required pre-implementation controls

The fixed pure vectors must be frozen before implementation. They include:

| Vector | Exact fixture | Expected result |
| --- | --- | --- |
| `rows-empty` | separator plus `U32(0)` | 33 bytes, SHA-256 `1b47012a24817833a73829cecb438cb29787c2452ba19c87ee4bdf9845b0c8b2` |
| `rows-one` | one undeclared row: package `p`, relative path `r`, record path `r`, `/x`, identity `(device=1,inode=2,mode=33188,links=1,uid=501,gid=20,bytes=1,mtime=0,ctime=0,sha=00*32)`, all four checks true, parent root `/root`, parent count `1`, all confinement booleans true | 188 bytes, SHA-256 `9db3cefd108afa971649fbe505d495a0a0fd708dd6e83328f223842f0243fcb9` |
| `overlay-one` | one row `(p,/x,r,declaredBytes=1,declaredSha=00*32,currentBytes=2,currentSha=11*32)` | 132 bytes, SHA-256 `6a943b3833cde33e4954211700ac5927f85c3635504d81887c222f399e1d63cc` |
| `domain-one` | the fixed `rows-one` and `overlay-one` digests, policy string, one synthetic observed file per field, endpoint and symlink records, counts `1..7`, flags `true,false,false,false` | 1368 bytes, SHA-256 `fc10a17e3b32b00cf0aa217d49efe654ebb31579f3d3de5037b87a6af1cd22fd` |

The vector definitions freeze field values, order, separators, null options,
raw digest bytes, and expected hashes. A control must compare generated bytes,
length, and hash. It must also prove that changing one row byte, overlay row,
identity field, check boolean, count, policy byte, or phase-independent root
changes the corresponding digest. A phase label change alone must not change
`domain_identity_digest`; a counter change alone must not change it and must be
checked only against its phase cap.

Before child authorization, pure controls must reject A07/A08/schema-3 or
arbitrary runtime reports, stale A09 hashes, wrong A09 root key sets, policy
objects, wrong report state, wrong overlay keys/order/count, changed diagnostic
projection, an added or removed runtime row, a changed report row, and every
additional RECORD divergence. Full-path controls must call the same central
validator and digest functions used by the runner. A reduced report-only,
allocation-only, or count-only projection is insufficient.

## Verification boundary and risks

The completed A09 report and parent readback establish a current filesystem
snapshot and RECORD classification only. They do not establish comparator
execution, loaded images, provider origin, native text support, image quality,
playback, hearing, or creative acceptance.

The runner observes the domain at four bounded points. It cannot create an
atomic operating-system snapshot between the final prelaunch read and a
path-based child import. The report and live scans remain separate evidence.

The one-gigabyte read limit is per phase. Per-phase counters are retained and
are never compared for equality. The digest rules do not claim allocator, RSS,
or native-framework bounds. The 45-row overlay remains a fixed measured local
observation, not a wheel, RECORD, provider, or cause attestation.

The next implementation checkpoint is a source review of the canonical digest
module and pure vectors before any child process or comparator control runs.
