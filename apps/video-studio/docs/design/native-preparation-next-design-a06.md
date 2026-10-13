# Native text preparation next design A06

## Status

This is a design-only successor to A05.
A05 and both A05 reviews remain unchanged.

| Bound document | SHA-256 |
| --- | --- |
| `native-preparation-next-design-a05.md` | `336e19dd491ac04843e31cb4b93b189e5cfb982c0312e55cf123fc182a0ad1d0` |
| `native-preparation-parent-review-a05.md` | `7aa0fc0a50059b74063486497c95dc07459a2023b68543987e9fc8709061f564` |
| `native-preparation-next-design-review-a05.md` | `55ad0e2f55a67e41346c5d6c82b3093049e5ba7aaf84b07cbc00ea9eb034146c` |

A06 replaces three A05 contracts:

1. `MeasuredArtifact` becomes a closed heterogeneous observation model.
2. acceptance requires one noncyclic, source-pinned trust root.
3. the A06 observer uses its actual child-owned publication contract.

All other A05 stage boundaries, commands, limits, and unavailable states remain in force.
Comparator authority remains uninhabited.

No helper, gate, permission record, trust manifest, authorization, or run directory was created.
No compiler, producer, observer, comparator, test, GPU process, or Resolve process ran.

## Caller usage first

The caller cannot choose an acceptance-record path.
The reviewed loader owns the pinned trust root and selects one exact subject row.

```rust,ignore
let trust = AcceptanceTrustRootV1::open_pinned()?;

let rust_qualification = RustProducerQualificationV2::load(
    &trust,
    AcceptedSubjectKey::RustProducerSourceV1,
    AcceptedSubjectKey::RustProducerRunnerV1,
)?;
```

`open_pinned` accepts no path, digest, review, or disposition argument.
The stage still receives a caller-selected output parent for a later attempt.
The output parent does not affect qualification evidence.

Observer construction selects one closed source contract.

```rust,ignore
let observer = ObserverStage::new(
    trust.require::<A06ChildPublishedOrientationV1>()?,
)?;
```

This type does not exist as an accepted value today.
The code shape defines the future boundary without authorizing execution.

## Closed observation model

The role index uses typed facts instead of pretending every fact is a regular file.

```rust,ignore
enum ObservationV2 {
    RegularFile(RegularFileObservationV2),
    InvocationSymlink(InvocationSymlinkObservationV2),
    DirectoryAuthority(DirectoryAuthorityObservationV2),
    Scalar(ScalarObservationV2),
    OrderedList(OrderedListObservationV2),
    Alias(AliasObservationV2),
    DerivedBoolean(DerivedBooleanObservationV2),
}
```

Every observation has one unique `ClosedRole`.
Every reference names another role in the same index.
The complete reference graph must be acyclic.

### Stable identity

```rust,ignore
struct StableIdentityV2 {
    device: u64,
    inode: u64,
    mode: u32,
    size: u64,
    modified_ns: i128,
    changed_ns: i128,
}

struct MachOIdentityV2 {
    cpu_type: u32,
    file_type: u32,
    load_command_count: u32,
    load_command_bytes: u32,
    uuid: [u8; 16],
}
```

Every regular-file row records both `content_bytes` and `identity.size`.
The loader requires those values to be equal.
This closes the missing `StableIdentity.size` authority noted in the A05 review.

### Regular files

```rust,ignore
struct RegularFileObservationV2 {
    role: ClosedRole,
    absolute_path_bytes: BoundedBytes<1, 4096>,
    content_bytes: u64,
    sha256: Sha256,
    identity: StableIdentityV2,
    macho: Option<MachOIdentityV2>,
}
```

The loader opens the path once without following the final link.
It records matching `fstat` values before and after the bounded full read.
It then checks the pathname still names the observed device and inode.

### Invocation symlinks

```rust,ignore
struct InvocationSymlinkObservationV2 {
    role: ClosedRole,
    invocation_path_bytes: BoundedBytes<1, 4096>,
    link_identity: StableIdentityV2,
    raw_link_target_bytes: BoundedBytes<1, 4096>,
    resolved_target_role: ClosedRole,
}
```

The loader uses `lstat` and a bounded `readlink` loop.
It records the exact link bytes before resolving the target.
It requires `link_identity.size` to equal the raw link-target byte count.
The target role must be a regular file or directory row.
Retargeting a link changes the row even when target bytes remain equal.

### Directories

```rust,ignore
enum DirectoryAuthorityModeV2 {
    PathnameOnly,
    HeldDescriptorAndPathname,
}

enum DirectoryIdentityV2 {
    Endpoint {
        device: u64,
        inode: u64,
        mode: u32,
    },
    FullStat(StableIdentityV2),
}

struct DirectoryAuthorityObservationV2 {
    role: ClosedRole,
    absolute_path_bytes: BoundedBytes<1, 4096>,
    mode: DirectoryAuthorityModeV2,
    held_identity: Option<DirectoryIdentityV2>,
    pathname_identity: DirectoryIdentityV2,
    require_mode_0700: Option<bool>,
    pathname_matched_held: Option<bool>,
    pathname_stable: Option<bool>,
}
```

`PathnameOnly` forbids held-only and held-relation fields.
`HeldDescriptorAndPathname` requires every held and held-relation field.
The loader rejects non-directory modes.

Build-closure directories require `FullStat` because their saved identities contain every field.
Pure-control held roots and log authorities use `Endpoint` because their saved identities contain only device, inode, and mode.
A fresh richer `stat` cannot silently strengthen a historical `Endpoint` fact.

This row establishes only the endpoint identity.
It does not recursively attest directory contents.

### Scalars

```rust,ignore
enum ScalarKindV2 {
    Boolean,
    Unsigned64,
    Signed64,
    Utf8,
    PathBytes,
    RelativePathBytes,
    Sha256,
}

struct ScalarObservationV2 {
    role: ClosedRole,
    kind: ScalarKindV2,
    encoded_value: BoundedBytes<1, 65536>,
}
```

Booleans encode as one byte, `0` or `1`.
Integers use fixed-width big-endian two's-complement rules.
UTF-8 rejects invalid bytes and NUL.
Path bytes are absolute, bounded, and NUL-free.
Relative-path bytes are nonempty, nonabsolute, NUL-free, and contain no `.` or `..` component.
SHA-256 values are exactly 32 raw bytes.

Scalar path text does not claim directory or file identity.

### Ordered lists

```rust,ignore
struct OrderedListObservationV2 {
    role: ClosedRole,
    members: BoundedVec<ClosedRole, 0, 4096>,
}
```

The list records exact member order and count.
Each member must exist exactly once in the same role index.
A list cannot include itself directly or indirectly.

Nested report arrays always produce one list row plus their element rows.
The loader never substitutes the array's top-level key count.

### Aliases and derived booleans

```rust,ignore
enum AliasRelationV2 {
    DescriptorMatchesPathname,
    LocatedUnderDirectory,
    SameObservedObject,
}

struct AliasObservationV2 {
    role: ClosedRole,
    relation: AliasRelationV2,
    left: ClosedRole,
    right: ClosedRole,
}

struct DerivedBooleanObservationV2 {
    role: ClosedRole,
    value: bool,
    dependencies: BoundedVec<ClosedRole, 1, 4096>,
}
```

An alias references two complete observed rows.
It does not replace either row.

A derived boolean names every measured input used by its derivation.
The loader recomputes the boolean and rejects a copied mismatch.

## Canonical role-index V2

V2 starts with these exact bytes:

```text
native-text-role-index-v2\0
```

The next fields are `u32 schema = 2` and `u32 row_count`.
Rows sort by role bytes.
Each row encodes:

```text
u16 role_byte_count
role ASCII bytes
u8 observation_kind
kind-specific fields
```

Variable byte strings use `u32 byte_count` followed by exact bytes.
Role references use the same `u16 + role bytes` form.
List and dependency counts use `u32`.
Integers use big-endian order.
Signed integers use two's-complement encoding.

Observation kind tags are fixed:

| Tag | Kind |
| ---: | --- |
| `1` | regular file |
| `2` | invocation symlink |
| `3` | directory authority |
| `4` | scalar |
| `5` | ordered list |
| `6` | alias |
| `7` | derived boolean |

Kind-specific fields encode in their struct declaration order.
Option values use a one-byte `0` or `1` tag before any payload.
Enum values use the closed tags declared by this schema.

The schema fixes every nested tag and optional-field tag.
Unknown tags fail before aggregate construction.

The role grammar remains `[a-z][a-z0-9_.:-]{0,127}`.
The maximum role count remains 4,096.
The maximum encoded index remains 4 MiB.

The aggregate is SHA-256 over the complete V2 bytes.
No JSON serialization contributes to that aggregate.

## Exact saved-report adapters

An adapter is source code for one exact report schema.
It cannot discover fields or versions from caller data.

The adapter first measures the report JSON as one regular-file row.
It then parses strict JSON and emits the typed rows below.
Unknown, missing, or duplicate fields fail qualification.

### Swift build closure V1

Each `closureBefore` and `closureAfter` expands to 76 rows.

| Report field | Typed expansion | Rows |
| --- | --- | ---: |
| `compilerExecutable` | regular file | 1 |
| `compilerInvocation` | invocation symlink to `compilerExecutable` | 1 |
| `helper` | regular file | 1 |
| `manifest` | regular file | 1 |
| `pythonExecutable` | regular file | 1 |
| `pythonInvocation` | invocation symlink to `pythonExecutable` | 1 |
| `pythonInvocationText` | path scalar | 1 |
| `pythonResolvedTarget` | path scalar | 1 |
| `sdkDirectory` | pathname-only directory | 1 |
| `sdkInvocation` | invocation symlink to `sdkDirectory` | 1 |
| `sdkSettings` | regular file | 1 |
| `sourceDirectory` | pathname-only directory | 1 |
| `sourceRows` | ordered list | 1 |
| each of 21 source rows | regular file, relative-path scalar, declared-role scalar | 63 |

The exact total is `12 + 1 + 21 * 3 = 76`.
The two closure lists therefore contribute 152 typed rows.

One derived-boolean row records their exact equality result.
The build role schema replaces `swift.build.input:NN` with:

```text
swift.build.input.before:*  76 rows
swift.build.input.after:*   76 rows
swift.build.input.equal     1 row
```

### Swift pure-control inputs V1

Each `inputsBefore` and `inputsAfter` expands to 169 rows.

| Report field | Typed expansion | Rows |
| --- | --- | ---: |
| `allBinaries` | ordered list plus six Mach-O regular files | 7 |
| five top-level `*Matched` fields | derived booleans | 5 |
| `attemptRoot`, `buildRoot`, `packageRoot` | held-descriptor directory authorities | 3 |
| `buildClosure` | one Swift build closure | 76 |
| seven `files` entries | descriptor file, pathname file, alias, two derived booleans | 35 |
| `logs` | ordered list plus seven groups of file, relative-name scalar, and `LocatedUnderDirectory` alias | 22 |
| `selectedHeldBinaries` | ordered list plus four groups of two files, alias, two booleans | 21 |

The exact total is `7 + 5 + 3 + 76 + 35 + 22 + 21 = 169`.
The before and after inputs contribute 338 typed rows.

One derived-boolean row records complete before/after equality.
The role schema replaces `swift.pure.input:NN` with:

```text
swift.pure.input.before:*  169 rows
swift.pure.input.after:*   169 rows
swift.pure.input.equal     1 row
```

The adapter binds every descriptor-relative log name.
Each log alias requires its repeated raw directory identity to equal the referenced root role.

### Rust toolchain observation V1

The saved toolchain report expands to exactly 89 typed rows.

| Report family | Typed expansion | Rows |
| --- | --- | ---: |
| top-level scalar facts | scalar | 11 |
| seven fixed artifacts | regular file | 7 |
| `observations` | list header | 1 |
| nine observation argument vectors | list headers | 9 |
| 24 observed argument tokens | scalar | 24 |
| nine return codes | scalar | 9 |
| nine output logs | regular file | 9 |
| `frameworks` | list header | 1 |
| three framework records | five scalars and one `Info.plist` file each | 18 |

The exact total is `11 + 7 + 1 + 9 + 24 + 9 + 9 + 1 + 18 = 89`.
The seven report file objects lack saved stable identities.
The loader obtains those identities through fresh descriptor observations.

`sdkPath` and framework paths remain path scalars.
They do not become directory authority without a source successor that measures directories.

The saved Cargo and Rust invocation tokens also remain path scalars.
They do not establish contemporaneous invocation-symlink identity.

### Adapter cardinality rules

Every current adapter exposes a compile-time `EXPECTED_ROWS` value.
Qualification requires the emitted count to equal that value.

Before/after copies use separate role prefixes.
Aliases reference those exact prefixed roles.
No field can be counted only because its parent dictionary has one key.

Changing a saved report schema requires a new adapter type and role-schema version.

## Noncyclic acceptance trust root

A06 separates an acceptance claim from the authority that trusts it.

```rust,ignore
struct AcceptanceRootPinV1 {
    schema: ExactU32<1>,
    manifest_byte_count: u64,
    manifest_sha256: Sha256,
}

struct AcceptanceTrustManifestV1 {
    schema: ExactU32<1>,
    operation: ExactString<"native_text_acceptance_trust_root">,
    entries: BoundedVec<TrustedAcceptanceEntryV1, 1, 256>,
}

struct TrustedAcceptanceEntryV1 {
    key: AcceptedSubjectKey,
    acceptance_record: ArtifactRef,
    subject_role_index: RoleIndexRef,
    peer_review: ArtifactRef,
    parent_review: ArtifactRef,
    disposition: ExactString<"accepted_no_p1_or_p2">,
}
```

The reviewed loader source contains one exact `AcceptanceRootPinV1` value.
It also includes the exact manifest bytes with `include_bytes!`.
The caller cannot replace or extend that value.

The loader hashes the embedded manifest bytes.
It requires the compiled byte count and SHA-256 from the pin.
It parses strict JSON with no duplicate or unknown fields.

The manifest entries sort by the closed subject-key tag.
Every key is unique.
Peer and parent review roles must differ.
Their artifact identities and SHA-256 values must also differ.

The loader selects the entry by closed subject key.
It then opens the exact acceptance record and reviews named by that entry.
Every descriptor must equal the trusted entry.

The acceptance record must still bind the same subject aggregate and reviews.
Agreement between two untrusted files is insufficient.

### Trust graph

The trust graph is intentionally one-way:

```text
reviewed loader source
  -> compiled AcceptanceRootPinV1
  -> exact trust-manifest bytes
  -> exact acceptance-record bytes
  -> exact subject aggregate and two review files
  -> private Accepted<T>
```

The trust manifest cannot contain entries for itself, its pin source, or its loader.
The acceptance record cannot include the trust manifest in its subject index.
The subject index excludes all acceptance and review artifacts.

This prohibition prevents a review record from authenticating its own trust root.
The loader source and binary form the explicit bootstrap base case.
Root-owned stage code must bind their exact source and binary hashes before use.
That bootstrap authorization cannot come from a record opened by this loader.

The loader source and build need separate source and build review before use.

No trust manifest or pin value exists for A06.
Therefore no A06 acceptance value can be constructed today.

## Exact current A06 observer contract

A06 chooses child-owned report publication for the current observer source.
It does not silently impose the A05 runner-owned report model.

The bound source is:

```text
verify_orientation_a06.py
SHA-256 a9e71c86b36217cb15ed154768ecfdbb614dd7a97cabd023d60cc77b1dd8c9d7
```

This source remains unaccepted.
The contract below matches its current command, filename, and writer behavior.
Any source change requires a new observer contract version.

### Exact command

```text
PYTHON_EXECUTABLE
-I
-B
VERIFY_ORIENTATION_A06
--producer-run PRODUCER_ORIENTATION_SIDECAR_A06
--runtime-binding OBSERVER_RUNTIME_BINDING
--report RUN_ROOT/orientation-report-a06.json
--actual-proof
```

The runner supplies every argument in this order.
The caller supplies none of the suffix.

The producer-sidecar basename must contain `a06`.
The report basename is exactly `orientation-report-a06.json`.
It contains `a06` and excludes `a01` through `a05`.

### Report writer ownership

The child exclusively creates `orientation-report-a06.json`.
The runner must not precreate, replace, or rewrite that file.

The runner exclusively creates:

- `stdout.log`;
- `stderr.log`;
- optional zero-byte `cancel-marker`.

The fresh run root starts empty with mode `0700`.
The runner retains its directory descriptor through child closure and readback.
It checks pathname identity before launch and after child closure.

The child writes by pathname, not relative to the retained descriptor.
A06 therefore claims pathname identity checks around publication.
It does not claim descriptor-relative child publication.

Any future descriptor-relative or runner-owned report model requires a new observer source and contract.

### Current success shape

The child first encodes the report without a `report` member.
It exclusively writes those bytes.
It then adds an in-memory `report` observation and prints that object to standard output.

Therefore:

- the on-disk report must not contain its own publication observation;
- the terminal standard-output object must contain that observation;
- the observation's byte count and hash must equal the on-disk report;
- exit status zero requires on-disk state `passed`.

The runner independently measures the report after child closure.
It compares those bytes with the printed publication observation.

### Current failure shapes

If all parsing completes but one pixel check is false, the child writes the full observation report with state `failed`.
Its standard-output object includes the same post-write publication observation as the success shape.
The child exits nonzero.

If a `ValidationFailure` or bounded unexpected error interrupts the run, the child attempts to create the same report path.
That file contains the bounded failure report when creation succeeds.

The terminal standard-output object contains:

- state `failed`;
- the bounded error code and detail;
- the child publication result.

If exclusive report creation fails, the terminal object records `written: false`.
No runner fallback report is allowed.

The runner preserves every created file.
It classifies a missing child report from the terminal object and nonzero status.
It does not convert that result into observer acceptance.

### Output inventory

The maximum regular-file count remains four:

1. `stdout.log`;
2. `stderr.log`;
3. optional `orientation-report-a06.json`;
4. optional `cancel-marker`.

The maximum subdirectory count is zero.
The maximum entry count is four.

The existing A05 byte caps remain unchanged.
The child report cap is 1 MiB.
Each runner log cap is 64 KiB.

Exit zero without one report fails qualification.
More than one report-like file fails qualification.
An unknown entry or any subdirectory fails qualification.

## Updated module boundaries

| Future module | A06 responsibility |
| --- | --- |
| `artifact_observation_v2` | Seven typed observation variants and one-descriptor file reads. |
| `role_index_v2` | Exact V2 binary encoding, acyclic references, bounds, and aggregate. |
| `saved_report_adapters_v1` | Exact Swift and Rust typed expansions and cardinalities. |
| `acceptance_trust_root_v1` | Compiled pin, strict trust-manifest load, and subject-key lookup. |
| `acceptance_v2` | Three-way record, trust-entry, and measured-artifact agreement. |
| `observer_runner_a06_v1` | Exact child-owned report command, inventory, and terminal classification. |

No module accepts a generic JSON path or caller-supplied role list.
No adapter dispatches on a version string read from an untrusted directory.

## Verification plan

### Observation controls

1. Retarget one invocation symlink while retaining resolved file bytes.
2. Replace one directory endpoint while retaining descendant path text.
3. Change `StableIdentity.size` while retaining the copied byte count.
4. Mutate one source-row relative path.
5. Mutate one source-row declared role.
6. Reorder two ordered-list members.
7. Swap one held descriptor and pathname observation.
8. Change one derived boolean without changing its dependencies.
9. Add an unreferenced row.
10. Add one reference cycle.

Every mutation must fail before process launch.

### Adapter controls

1. Require exactly 76 rows from each Swift build closure.
2. Require exactly 169 rows from each Swift pure-control input set.
3. Require exactly 89 rows from the saved Rust toolchain observation.
4. Remove one nested source row and require failure.
5. Replace a fixed object with a scalar and require failure.
6. Change one list cardinality while retaining its members and require failure.
7. Replay the typed expansion in an independently authored decoder.

### Trust-root controls

1. Supply a fabricated acceptance record absent from the root manifest.
2. Swap peer and parent reviews.
3. Change one review while retaining the acceptance record.
4. Change the subject aggregate.
5. Change the trusted manifest without changing the compiled pin.
6. Add a trust entry for the trust manifest itself.
7. Attempt caller construction of `Accepted<T>`.

All seven controls must leave the private accepted type unavailable.

### Observer controls

1. Use `report.json` and require prelaunch rejection.
2. Use a report name containing `a05` and require prelaunch rejection.
3. Use a sidecar name without `a06` and require prelaunch rejection.
4. Precreate the child report and require preserved child failure.
5. Validate the success report against its printed publication observation.
6. Validate the bounded failure report when child publication succeeds.
7. Preserve the no-report failure when child publication fails.
8. Add one unknown file or subdirectory and require failure.
9. Replace the run root during the child lifetime and require failure.
10. Rehash every producer input after observer closure.

These are planned controls.
No control ran while authoring A06.

## Compatibility and current boundary

A06 changes no producer, observer, comparator, product, media, or project bytes.
It creates no authorization or acceptance record.

The A05 Rust-first stage separation remains unchanged.
Rust qualification still does not wait for Swift, observer, or comparator evidence.

The A05 fixed process limits, environment, cancellation sequence, and direct-child reap rules remain unchanged.
The comparator accepted enum remains empty.

Current saved Swift build and pure-control records remain bounded historical evidence.
The new adapters do not upgrade them into native execution proof.

The current A06 observer source remains unaccepted.
This design binds its actual filename and writer behavior for later source qualification.

A06 establishes no native execution, native text feasibility, output correctness, product integration, playback, hearing, lyrics, film quality, or creative acceptance.
All reviews remain same-model-family unless separate evidence states otherwise.
No cross-family review is claimed.
