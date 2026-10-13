# Rust native text probe source review A01

## Disposition

The source is **not yet green for the frozen proof build**.

I found two P1 proof blockers and seven P2 source defects. The P1 findings affect the probe's declared producer and 16 MiB authorities.

The geometry, text-call schedule, shaping fields, fallback gate, three-repeat gate, mask storage, and native backing lifetimes match the selected protocol. Those parts may remain unchanged.

No package build, typecheck, native call, GPU operation, Resolve operation, or product-state change was performed.

The current package has no `Cargo.lock`. A later lock and executable require a new exact source/build freeze after these findings close.

## P1: the 4 MiB observation reservation does not enforce its payload

`main.rs` reserves one 4 MiB permit before parsing and shaping. The source then allocates strings, maps, vectors, run fonts, tables, glyphs, points, advances, indices, and every retained repetition without consuming a checked component ledger.

The declared caps do not prove that 4 MiB is conservative. One matching run can retain up to 128 copied `TableIdentity` records. One repetition permits 64 runs and 1,024 glyphs. The report retains three repetitions across fifteen cases.

Those allowed shapes can exceed 4 MiB before report serialization detects anything. The budget can still report the fixed 4 MiB reservation and a compliant peak.

This violates the protocol requirement to reserve checked component sums before allocation. It also invalidates the rationale's claim that the 16 MiB logical payload is enforced.

Before the proof build:

1. Define a checked retained-payload component formula for every owned representation.
2. Charge actual lengths or safe finite bounds before each allocation can grow.
3. Include `Vec` backing elements and owned string bytes.
4. Include parsed inputs, repeated run-font evidence, setter traces, checks, errors, and report descriptors.
5. Reject before allocation when the retained observation envelope cannot hold the next component.
6. Preserve the existing 16 MiB limit and current buffer lifetimes.

Deduplicating immutable selected-face table identities is acceptable. Each run must still retain fresh proof that its native face matched the selected identity.

The fix needs a checked component derivation. A larger unexplained blanket permit would not close this finding.

## P1: the executable hash does not identify the running image

`producer_identity` hashes `env::current_exe()` by pathname. A pathname replacement can make the report identify different bytes from the loaded process.

The frozen build manifest can then match the replacement while the old process executes. An independent report rehash cannot recover the loaded image identity.

The protocol requires the exact executable identity. Before proof use, bind the opened executable to the running image.

On macOS, compare the opened file's device and inode with the loaded executable region. Also bind the Mach-O UUID and stable file metadata while hashing. Reject replacement or in-place modification.

A driver-held executable file description may provide equivalent atomic launch provenance if Darwin supports that exact launch route. Record what it proves. A Mach-O UUID alone is not a whole-image byte hash.

If the probe keeps only pathname evidence, rename the field and qualification boundary. It cannot claim exact producer-binary authority.

## P2: reported input identities can differ from used bytes

The probe parses admitted case, manifest, authority, license, build-manifest, and font bytes. It later rereads their paths for report identities.

A same-length replacement after parsing can produce this contradiction:

- native work used the first byte sequence;
- the complete report names the second byte sequence;
- `frozen_input_hashes` remains true from the first check.

`source_bundle_identity` also reads metadata and content through separate pathname operations.

Return the identity with each admitted byte owner. Compute that identity from the exact bytes which were parsed or passed to native construction. Reopen or rehash at completion only as an additional unchanged-input check.

Use one opened file description and stable before/after metadata for file hashing. Do not compose a byte count and digest from separate pathname observations.

## P2: several allocation paths allocate before their exact bound

The logical ledger has these concrete underchecks:

1. `sha256_file_raw` owns a 64 KiB `BufReader` buffer and a separate 64 KiB stack buffer. The ledger charges 64 KiB.
2. `read_admitted` reserves the metadata length, then calls `fs::read`. A growing file can allocate past the reserved length before the post-read check.
3. `EventLog::append` calls `serde_json::to_vec` before it checks the 64 KiB event limit.
4. Native PostScript names and framework metadata become owned Rust strings without an actual-length charge or a predeclared finite bound.

Use one hash buffer or charge both buffers. Read admitted files through a bounded opened-file reader. Serialize events through a bounded writer or validate a finite encoded bound before allocation.

The known frozen events are small. That fact does not make the current general claim exact.

## P2: case-event write failures are discarded

`run_case` ignores the results from start, completion, and failure event appends. A complete report can therefore coexist with a silently incomplete event log.

Event persistence is part of the declared failure record. Return event-log errors as fatal output failures. Keep native repetition failures as structured repetition evidence.

`failure.json` should also use a bounded writer. Its current 64 KiB output reservation does not cap the streaming serializer.

## P2: native rejection can discard its causal observation

`run_repetition` creates a complete `ShapingObservation`, then validates it before placing it in `RepetitionObservation`.

A range, image-bound, RTL, matrix, status, or array-shape rejection therefore keeps only an error string. The complete run evidence is dropped.

Table-copy failures can similarly lose the already observed native face inventory. This prevents a reviewer from distinguishing the precise native disagreement from a wrapper defect.

Preserve the causal shape or face observation alongside the failure. Keep rejection nonqualifying. `CGRectNull`, empty, and infinite states must remain distinct observations.

## P2: repeat stability omits the clip-reference mask

`StabilityObservation.clipped_masks_identical` compares only the 48-by-48 clipped mask.

The 176-by-176 reference can change outside the clip while every current repeat gate remains true. The reference is a complete supported draw and must be stable across all three repetitions.

Add an explicit reference-mask stability field and gate. Keep the separate native ImageIO PNG comparison unchanged.

## P2: the orientation-copy permit ends before its owner

`run_orientation` drops `canonical_permit` while the 221-byte canonical vector remains in scope through the RGBA snapshot.

The payload is small, but the recorded permit lifetime is false. Drop the vector before its permit, or retain the permit through the vector's actual destruction.

## P2: the native face tuple overstates scaler observation

`copy_matching_face_identity` emits `scaler_type_hex = "00010000"` as a constant. Core Graphics did not expose or read that native SFNT header field.

The constant is valid source authority because the exact raw container was parsed first. It is not an independent native observation.

Mark the scalar as source-derived when forming the native face fingerprint. Alternatively, split raw `FaceIdentity` from the observable native tuple.

`native_cgfont_matches_raw_tables` may remain true only if its documentation lists the source-bound scalar separately from observed name, units, glyph count, tags, table lengths, and table hashes.

## Confirmed protocol matches

The source correctly implements these reviewed properties:

- The face fingerprint uses the NUL-terminated domain, big-endian TrueType scalar, table count, sorted raw tags, lengths, and raw table SHA-256 values.
- Both expected face IDs are hard-bound.
- Raw font bytes remain alive while copied `CFData`, provider, `CGFont`, `CTFont`, and `CTLine` objects are used.
- Each Core Foundation object retains its dependency. The font-copy permit drops after the native chain.
- Each bitmap context drops before its boxed Rust backing buffer.
- ImageIO finalizes and drops the image graph while the source surface remains alive.
- Main, guard, clipped, reference, and asymmetric 13-by-17 coordinate equations match the protocol.
- Alpha padding uses `0xA5` and is checked unchanged.
- The current source executes exactly twelve declared text setter calls. There is no duplicate setter call in the reviewed `native.rs`.
- Requested setter traces remain distinct from unavailable native getter evidence.
- The antialias-disabled control must be binary and differ from the policy mask.
- Smoothing and subpixel controls remain observations.
- Attributed UTF-8 and UTF-16BE identities, complete line range, sorted run partition, visual order, all run-status fields, full matrices, glyphs, positions, advances, and source indices are recorded.
- Nonmonotonic indices are preserved. RTL, nonidentity matrices, unknown status bits, glyph zero, and fallback are gated as selected.
- The native face quick guard runs before table payload copying.
- Foreign table payloads are not copied.
- Every case attempts exactly three fresh shapes. Complete qualification requires three completed repetitions.
- Rejection cases never publish rasters.
- Main/guard and clip/reference comparisons operate on the full declared regions.
- RLE storage is two-pass, lossless, bounded by an exact stored-byte reservation, and does not allocate a canonical frame copy.
- Every ordinary output file uses create-new semantics. Partial files remain after later failures.
- The 256 MiB output tracker covers mask, PNG, event, report, and failure reservations. Its reservations are conservative when writes fail.

## Required checks after repair

A repaired source version may proceed to lock generation and build/typecheck review only after:

1. all P1 and P2 findings above close in source, schema, and rationale;
2. the exact 16 MiB component derivation is saved and independently recalculated;
3. `Cargo.lock` is generated and reviewed without a native run;
4. compiler, Cargo, SDK, deployment target, dependency graph, source bundle, and executable identities are frozen;
5. the production executable identity is tied to its loaded image;
6. build/typecheck failures are preserved under a new source version.

Native execution remains a later gate. It still requires the independent Swift probe, external ImageIO PNG decode, fresh-process comparison, negative controls, and exact output closure.

No result here establishes native feasibility, product integration, encoded output, playback, hearing, lyrics, film completion, or creative acceptance.

## Exact reviewed identities

Shared contracts:

| File | SHA-256 |
| --- | --- |
| `text-synthesis-a01.md` | `d497f472b0d5162e61fab482e2f720a89192645b88b1430b1b61577f0330c323` |
| `text-probe-protocol-a01.md` | `4e4e399072372f6dbc02bb16f55d80fd1ca7cf1690ac8643d34055a1cae31d89` |
| `text-admission-contract-a03.md` | `704efeb86033c0dedbca0165ab13f84ee99c1a00602ca6f0a99ead6506b4ed9f` |

Frozen authoring package, 6,229 lines total:

| File | SHA-256 |
| --- | --- |
| `Cargo.toml` | `b583b0dcb72cf01826f1c448f48b71b16d873f09100d77f6246c0fcad3a11dde` |
| `output-schema.md` | `bc9853ff411a9c237d7491d3db0b99cedf45d8be9f4812e0e3ad1d91475f6a8d` |
| `source-rationale.md` | `fb7144a59b65ccda187ba50c973b6aa3a19ed47f5e88d874ff6904a43cb3d8eb` |
| `src/budget.rs` | `f377d876d2baf9a3866faf90397240cf30ab4736ea09c41c9d74fa93043bc585` |
| `src/error.rs` | `5a9f68446c2ad39d4e03e8dd3edc20a5d7af928a209176e7908259e0b6d3beae` |
| `src/main.rs` | `274b41389f7f15d6e17a087649b3f0025bbefe8d65bad025aa8ffda75b72c5d5` |
| `src/model.rs` | `056b050626df38dfa7ac466c2f3348752f0e69bb06de71f06bc4e5351e83035a` |
| `src/native.rs` | `2d9aba9bc46db2f1a212f345d6c71c50649f50d79ecbe9e63187f4520bf58fdd` |
| `src/probe.rs` | `f456629e5a6a735856d7eba56b9e9f302b446ac09beeb105a3db34ae17fc75c2` |
| `src/sfnt.rs` | `39df5bbdc7ab549d46a72393fc74175c76fdf27b3bb10712684f664e0440520d` |
| `src/util.rs` | `5d0660955ef3d3b124fcedd25f0e65182ce2f59c29dac781c3a36bb3ecf7d8ba` |

`Cargo.lock` was absent. The package was not compiled or executed.

This is an artifact-separated review within the same model family. No cross-family review was available.

## Verdict

The native ownership and evidence shape are credible. The source cannot yet support its exact producer or bounded-logical-payload claims.

Close both P1 findings and all seven P2 findings before freezing a proof build. A green successor would authorize build and typecheck only. It would not authorize native execution or product integration.
