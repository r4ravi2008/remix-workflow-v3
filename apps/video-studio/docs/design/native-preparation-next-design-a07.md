# Native text preparation next design A07

## Status

This is a narrow design-only successor to A06.
A06, its parent review, and its peer review remain unchanged.

| Bound document | SHA-256 |
| --- | --- |
| `native-preparation-next-design-a06.md` | `260e83d2b5fb8474b3ef04801b5f28f764ee08e4e94ea648352679cedc2b6eb5` |
| `native-preparation-parent-review-a06.md` | `40f4cc5163fa17b62555fb0f139454218eed8b07a5af0cc5e9014a380e6e808b` |
| `native-preparation-next-design-review-a06.md` | `e59a580fd030bbb3f5b40a51a70051df183532ecedc39aa5a2b9886b2b60cbbd` |
| `verify_orientation_a06.py` | `a9e71c86b36217cb15ed154768ecfdbb614dd7a97cabd023d60cc77b1dd8c9d7` |

A07 changes only two A06 contracts:

1. it assigns every nested V2 wire tag;
2. it states the observer's exact direct and exception stdout objects.

All A06 types, adapter counts, trust rules, stage boundaries, and limits remain unchanged.

No source, helper, gate, trust record, permission record, authorization, or run directory was created or changed.
No compiler, control, producer, observer, comparator, native, GPU, or Resolve process ran.

## Canonical nested tags

Every nested enum uses one unsigned byte.
Tag zero is invalid for every nested enum.
Any unlisted tag fails before role-index aggregate construction.

### `ScalarKindV2`

| Tag | Variant | Payload rule |
| ---: | --- | --- |
| `1` | `Boolean` | exactly one byte, `0` or `1` |
| `2` | `Unsigned64` | exactly eight big-endian bytes |
| `3` | `Signed64` | exactly eight big-endian two's-complement bytes |
| `4` | `Utf8` | length-prefixed valid UTF-8 without NUL |
| `5` | `PathBytes` | length-prefixed absolute NUL-free path bytes |
| `6` | `RelativePathBytes` | length-prefixed validated relative path bytes |
| `7` | `Sha256` | exactly 32 raw bytes |

The accepted tag range is exactly `1..=7`.
Every scalar tag is followed by `u32 value_byte_count` and then the exact payload bytes.
The fixed-width rows require byte counts of 1, 8, 8, and 32 respectively.

### `DirectoryAuthorityModeV2`

| Tag | Variant |
| ---: | --- |
| `1` | `PathnameOnly` |
| `2` | `HeldDescriptorAndPathname` |

The accepted tag range is exactly `1..=2`.

`PathnameOnly` requires these option tags:

```text
held_identity             = 0
require_mode_0700         = 0
pathname_matched_held     = 0
pathname_stable           = 0
```

`HeldDescriptorAndPathname` requires every listed option tag to equal `1`.

### `DirectoryIdentityV2`

| Tag | Variant | Payload order |
| ---: | --- | --- |
| `1` | `Endpoint` | `u64 device`, `u64 inode`, `u32 mode` |
| `2` | `FullStat` | the six `StableIdentityV2` fields in declaration order |

The accepted tag range is exactly `1..=2`.

`FullStat` encodes:

```text
u64 device
u64 inode
u32 mode
u64 size
i128 modified_ns
i128 changed_ns
```

All integers use big-endian order.

### `AliasRelationV2`

| Tag | Variant |
| ---: | --- |
| `1` | `DescriptorMatchesPathname` |
| `2` | `LocatedUnderDirectory` |
| `3` | `SameObservedObject` |

The accepted tag range is exactly `1..=3`.
The alias then encodes `left` and `right` role references in declaration order.

### Complete accepted tag sets

The complete V2 encoder accepts only these tag sets:

```text
ObservationV2                {1,2,3,4,5,6,7}
Option                        {0,1}
ScalarKindV2                 {1,2,3,4,5,6,7}
DirectoryAuthorityModeV2     {1,2}
DirectoryIdentityV2          {1,2}
AliasRelationV2              {1,2,3}
```

Declaration order does not assign a wire value.
An implementation must use these literal mappings.

## Canonical encoding controls

The encoder and an independently authored decoder must share no enum constants.
Their fixture must contain at least:

- every seven top-level observation kinds;
- every seven scalar kinds;
- both directory-authority modes;
- both directory-identity variants;
- every three alias relations;
- both option tags;
- one empty ordered list;
- one nonempty ordered list;
- one derived boolean with more than 64 dependencies.

The fixture records the complete encoded bytes, byte count, and SHA-256.
Those three values become reviewed evidence before loader implementation can qualify.

The negative matrix mutates each accepted tag to zero and to the first value above its range.
It also swaps two assigned values in only one implementation.
Every mutation must fail before aggregate construction or fail cross-implementation equality.

No canonical vector exists today.
Therefore A07 still creates no accepted loader.

## Exact observer stdout contract

The A06 child remains the sole writer of `orientation-report-a06.json`.
The command, filenames, source hash, and output inventory remain unchanged.

The runner parses stdout as exactly one UTF-8 JSON object followed by optional ASCII whitespace.
Duplicate keys, unknown keys, a second value, invalid UTF-8, or trailing non-whitespace fail classification.

There are two disjoint stdout schemas.

### Normal-return publication object

When `run(args)` returns normally, `main` prints only `result["report"]`.
It does not print the in-memory observation report.
It does not nest the publication object under a `report` key.

The stdout object has exactly three keys:

```json
{
  "bytes": 123,
  "path": "/absolute/run/root/orientation-report-a06.json",
  "sha256": "64-lowercase-hex-characters"
}
```

The numeric value above is illustrative.
The actual value must be positive and at most 1 MiB.

The runner requires:

1. the path equals the exact report path byte-for-byte;
2. the byte count equals the independently opened report;
3. the SHA-256 equals the independently opened report;
4. the on-disk report contains no top-level `report` member.

The on-disk state and child status define the outcome:

| On-disk `state` | Child status | Classification |
| --- | ---: | --- |
| `passed` | `0` | `ObservedPassed` |
| `failed` after complete pixel checks | `1` | `ObservedPixelFailed` |

Every other state and status pairing fails the observer stage.
`ObservedPixelFailed` is retained failure evidence and cannot construct observer acceptance.

### Exception envelope

A caught `ValidationFailure` or bounded unexpected error prints exactly the following object when failure publication itself returns:

```json
{
  "state": "failed",
  "error": {
    "code": "bounded-code",
    "detail": "bounded-detail"
  },
  "report": {}
}
```

The top-level keys are exactly `state`, `error`, and `report`.
The error keys are exactly `code` and `detail`.
The child status must equal `1`.

The nested `report` value has one of three exact shapes.

#### Exception report published

```json
{
  "path": "/absolute/run/root/orientation-report-a06.json",
  "bytes": 123,
  "sha256": "64-lowercase-hex-characters"
}
```

The runner independently opens the report.
It requires matching path, bytes, SHA-256, state, error code, and error detail.

#### Safe-path publication failed

```json
{
  "path": "/absolute/run/root/orientation-report-a06.json",
  "bytes": null,
  "sha256": null,
  "written": false
}
```

The runner records retained publication failure.
It accepts no report bytes from another path.
Any existing colliding entry remains unknown or foreign evidence.

#### Unsafe actual-proof path rejected

```json
{
  "path": "/absolute/unsafe/path",
  "bytes": null,
  "sha256": null,
  "written": false,
  "reason": "unsafe actual-proof report path"
}
```

The exact A07 command cannot reach this branch.
The runner still recognizes it for negative controls and classifies it as precondition failure.

If failure publication itself raises, stdout can be absent or incomplete.
The runner preserves stdout, stderr, status, and the output inventory.
It classifies that attempt as `ContractViolation` or `PublicationFailed` and creates no accepted observation.

### Outcome classifier

```rust,ignore
enum A06ObserverOutcome {
    ObservedPassed(MeasuredObserverReport),
    ObservedPixelFailed(MeasuredObserverReport),
    ObserverException {
        error: BoundedObserverError,
        report: Option<MeasuredObserverReport>,
    },
    PublicationFailed {
        error: BoundedObserverError,
        retained_entry: Option<ForeignEntry>,
    },
    ContractViolation(ClosedObserverContractError),
}
```

Only `ObservedPassed` may proceed to later technical review.
It does not itself create accepted authority.

The runner never reconstructs the omitted in-memory full report from stdout.
The on-disk child report remains the sole full observation document.

## Observer controls

1. Feed the direct three-key object with a passed disk report and status zero.
2. Feed the same object with a parsed pixel-failed disk report and status one.
3. Add `state` or `report` to the direct object and require rejection.
4. Nest the direct object under `report` and require rejection.
5. Feed the exception envelope with a matching written failure report.
6. Feed the four-key `written: false` result and retain publication failure.
7. Feed the five-key unsafe-path result and require precondition failure.
8. Change one disk byte while retaining stdout and require authority drift.
9. Swap status zero and one for each normal state and require rejection.
10. Add a second JSON value or trailing non-whitespace and require rejection.

These are planned source-level and parser controls.
No observer or control ran while authoring A07.

## Compatibility and remaining gates

A07 preserves the A06 adapter counts:

- 76 rows per Swift build closure;
- 169 rows per Swift pure-control input set;
- 89 rows for the saved Rust toolchain observation.

The A06 embedded trust-root design remains unchanged.
No trust manifest, pin, accepted value, or bootstrap authorization exists.

Rust, Swift, observer, and comparator qualifications remain separate.
Comparator authority remains uninhabited.

A07 changes no product, producer, observer, comparator, media, project, or saved evidence bytes.

This design establishes no native execution, native text feasibility, output correctness, product integration, playback, hearing, lyrics, film quality, or creative acceptance.
All reviews remain same-model-family unless separate evidence states otherwise.
No cross-family review is claimed.
