# Native text observer admission contract A04

## Status and scope

This document repairs the three P2 conditions in
`text-admission-observer-review-a01.md`. It preserves the A01 helpers and A03 admission
contract. It defines new A02 helper inputs, failure behavior, runtime identity, and producer
provenance. It does not run either helper.

The repaired files are:

- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/verify_input_authority_a02.py`;
- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/verify_orientation_a02.py`.

The current helper source hashes are:

- input helper: `398e9bee32c5db666e92e232b0299fbbf3dd50fc1bb279b9c905cc9d264aab58`;
- orientation helper: `42dea85db77da9a9b4a58df26a82d069e166ae857590708a5cf2f1ecf764ebbd`.

The helpers are separate-code observers. They do not import the editor, CoreText, CoreGraphics,
Rust, or a product renderer. They make no native shaping, raster acceptance, product acceptance,
watch, hearing, or creative claim.

All reports use bounded JSON and exclusive creation. A failed control remains visible in its own
fresh report. An actual-proof invocation cannot target an A01 path or overwrite any existing
report.

## Frozen input authority

The input helper binds these exact values before reading font tables or cases:

| Input | Required binding |
| --- | --- |
| `font-fixtures-a01/manifest.json` | SHA-256 `04916451ea952d8ada2e5ca2d1171deaa0e1e6c0acd4652cf2bba0a77c057947` |
| `synthetic-text-cases-a02.json` | SHA-256 `a461e07c803793baa688b18452287ca73f3ba0e6d0f8c172458a0158e4ab513d` |
| `font-fixtures-a01/repository-commit.json` | SHA-256 `647171c218f322957aa53c355ccf16b46e581f3d0984e57a1ec6a83aa9cde6d6` |
| Manifest repository | `notofonts/noto-fonts` |
| Manifest and repository commit | `ffebf8c1ee449e544955a7e813c54f9b73848eac` |
| `font-fixtures-a01/OFL.txt` | exact source URL `https://raw.githubusercontent.com/notofonts/noto-fonts/ffebf8c1ee449e544955a7e813c54f9b73848eac/LICENSE`; exactly `4,377` bytes, SHA-256 `0dab92d0544f7b233403f14b84a663bdbfa746982eda629e7f4f9ffe1b036feb` |

The repository record must contain the same commit SHA and a URL binding both repository and
commit. The helper reads and hashes the actual OFL bytes. A manifest license record alone is not
license-byte authority.

Font checks remain raw-container checks. They verify exact file bytes, the TrueType scalar,
directory extents, duplicate tags, non-overlap, declared offsets and lengths, table hashes, and
the selected domain-separated face fingerprint. The helper does not claim native face identity,
fallback behavior, shaping, or raster output.

Case checks independently recompute UTF-8, UTF-16BE, line ranges, normalization, direction, and
the integer Q16 font size. The helper uses the selected positive integer range:

```text
65,536 <= fontSizeQ16 <= 33,554,432
```

The input helper records `nativeFaceObserved`, `nativeShapingRun`, and `nativeRasterRun` as false.
It records `watched`, `heard`, and `creativeAccepted` as false.

## Explicit failure and runtime rules

The A02 helpers use a small `ValidationFailure` path and explicit condition checks. They contain
no proof-bearing language-level assertion statements. A malformed file, wrong hash, missing field,
wrong type, over-limit value, or failed comparison becomes a bounded error with a short code and
detail.

Both helpers reject `sys.flags.optimize != 0`. The optimized interpreter must not turn checks off.
The orientation helper additionally binds the exact Pillow and NumPy versions. The input helper
binds Python identity and uses no Pillow or NumPy dependency.

The optional runtime binding has this shape:

```json
{
  "schema": 1,
  "python": {
    "implementation": "CPython",
    "version": "<platform.python_version>",
    "optimize": 0
  },
  "dependencies": {
    "pillow": "<PIL.__version__>",
    "numpy": "<numpy.__version__>"
  }
}
```

Actual-proof mode requires this binding for both helpers and compares every Python value. The
orientation helper also compares Pillow and NumPy. The input helper records its absence of those
external dependencies. A runtime mismatch fails before any observer result is accepted.

Each report is limited to 1 MiB and is written with exclusive creation. The helpers require a
fresh versioned report path. Actual proof requires `a02` in the report name and rejects `a01`.
The report contains the helper path and hash, runtime binding, input bindings, mutation schedule,
scope, and false product/creative fields.

## Orientation producer-run sidecar

Orientation proof requires a separate predeclared sidecar. The observer must not infer producer
lineage from three caller-supplied paths. The sidecar has this shape:

```json
{
  "schema": 1,
  "operation": "native_text_orientation_a02",
  "producer": {
    "source": {"path": "<exact Swift source>", "bytes": 0, "sha256": "<64 hex>"},
    "binary": {"path": "<exact producer binary>", "bytes": 0, "sha256": "<64 hex>"}
  },
  "run": {
    "id": "<fresh run id>",
    "exclusive": true,
    "outputRoot": "<fresh output directory>",
    "artifacts": {
      "rawAlpha": {"path": "<raw file>", "bytes": 272, "sha256": "<64 hex>"},
      "canonicalAlpha": {"path": "<canonical file>", "bytes": 221, "sha256": "<64 hex>"},
      "nativeImagePng": {"path": "<PNG file>", "bytes": 0, "sha256": "<64 hex>"}
    }
  }
}
```

The A02 observer requires `schema`, `operation`, `run.exclusive`, a bounded run ID, and a real
output directory. It verifies the producer source and binary bytes against the sidecar. It verifies
all three artifact paths, byte counts, and hashes. It requires three distinct resolved artifact
paths under the exclusive output root. The producer source and binary may live outside that root.

The observer records:

```text
sourceLifetimeEstablishedHere: false
sourceLifetimeScope: identity-and-exclusive-artifact-path-binding-only
```

These bindings establish which source, binary, and three artifact files the observer read. They
do not prove that the producer wrote the PNG directly from its native bitmap snapshot, that it
did not read the canonical-alpha file, or that no copied row array existed. A separate source
review and one exclusive producer run must establish those facts. The observer never upgrades
this field to true.

## Orientation checks and stride boundary

The raw sample remains 13 by 17 visible pixels with stride 16:

```text
raw bytes       = 17 × 16 = 272
canonical bytes = 17 × 13 = 221
padding bytes   = 17 × 3 = 51
```

The positive stride case is valid and must pass:

```text
width=13, height=17, stride=16, charged_bytes=272
```

The negative undercharge controls must fail before allocation:

```text
charged_bytes=221  # visible bytes only
charged_bytes=271  # one byte below exact stride charge
```

The helper therefore does not describe the valid `2,049×2,047` or 13×17 exact-stride request as
a negative case. A stride charge is accepted only when `stride == align_up(width,16)` and
`charged_bytes == stride × height`.

The observer independently checks:

- every raw padding byte equals `0xA5`;
- canonical visible bytes equal the declared row reversal;
- the canonical bytes equal rectangle `(2,9,4,5)` with value 255;
- the native PNG has a real alpha channel and size 13×17;
- PNG alpha equals the rectangle without converting an RGB image into synthetic alpha;
- canonical alpha equals PNG alpha.

The raw reversal remains `canonical[y,x] = raw[height - 1 - y,x]`. A mismatch stays a failure.
The PNG is opened independently through Pillow and its existing alpha channel is read directly.

## Bounded mutation schedule

The schedule is predeclared in both A02 helpers and appears in every report. Each mutation uses a
fresh control input or report path. It cannot replace a frozen baseline hash or rewrite an A01
report.

| Family | Mutation | Required result |
| --- | --- | --- |
| Runtime | Run with `python -O` | Reject before proof result |
| Runtime | Change Python, Pillow, or NumPy binding | Runtime mismatch |
| Font | Flip one raw font byte | Raw SHA mismatch |
| Font | Flip one declared table byte | Exact table SHA mismatch |
| Text | Change text without its source expectation | UTF-8 or UTF-16 mismatch |
| Range | Change line range | Source expectation mismatch |
| Size | Change `fontSizeQ16` or use nonintegral Q16 | Integer range or equality failure |
| License | Flip one OFL byte or alter byte count | Exact license binding failure |
| Repository | Change repository or commit record | Repository/commit failure |
| Report | Reuse an existing A01 or A02 report path | Exclusive-create or baseline-path failure |
| Producer | Flip producer source or binary | Sidecar identity failure |
| Sidecar | Change one artifact path, byte count, or hash | Exclusive artifact binding failure |
| Stride | Charge visible bytes or one byte below exact stride | Undercharge rejection |
| Raw orientation | Flip one raw visible row | Row-reversal failure |
| Padding | Flip one `0xA5` byte | Padding failure |
| Canonical | Flip one canonical byte | Canonical comparison failure |
| PNG | Flip one alpha byte or change dimensions | PNG comparison or shape failure |

The controls are meaningful only when each negative exits nonzero and writes a bounded failed
report. A failed control is evidence of rejection, not a product acceptance result.

## Required report scope

An input-authority A02 report records the manifest, cases, repository commit record, OFL file,
two font bindings and raw fingerprints, all 15 source facts, runtime identity, helper hash, and
the false native/product fields.

An orientation A02 report records the sidecar, exact producer source and binary bindings, all
three artifact bindings, runtime identity, exact stride controls, raw/canonical/PNG checks,
coverage summaries, helper hash, and the truthful source-lifetime scope. It records no unbounded
pixel payload beyond the fixed 221-byte orientation sample's derived observations.

The report must preserve failure state. A successful report may use `passed` only when every
declared check and the positive/negative stride controls have the expected outcome. A failure
must not be converted into a nominal report by removing a check, changing a frozen expected hash,
or running with optimization.

## Integration boundary

These repaired helpers can establish bounded raw-input authority and bounded orientation checks
after a root-owned source review binds the producer sidecar. They cannot establish CoreText
feasibility, Rust layout sizes, source lifetime, product rendering, native memory, playback,
listening, or creative acceptance.

A03 remains provisional for product integration. The old-media ownership proof, bounded Plan8
deserialization, one-buffer serialization, measured Rust representations, and teardown checks
remain required before runtime admission can rely on A03 or this observer contract.
