# Swift native text probe source review A03

## Disposition

The A03 Swift package is **not green for build or typecheck freeze**.

I found four P1 blockers and four P2 defect groups. The package remains unbuilt and unexecuted. These are source-review findings, not native observations.

Preserve A03 unchanged. Repair a separate successor, then repeat the complete source, schema, and rationale review. A green successor would authorize build and typecheck only.

## P1 — `ShapeRecord.runs` is immutable but the source appends to it

`ShapeRecord.runs` is declared with `let` at `probe.swift:284`. The shaping loop calls `record.runs.append(...)` at line 1629.

That mutation of an immutable stored property is an evident Swift compile error. Make the property mutable, or construct a separate run array before the final record.

This finding comes from source semantics. No compiler was run.

## P1 — mandatory native PNG admission always rejects itself

`finalizeNativePNG` computes `encodedBound = ledger.cap - ledger.outstanding` at `probe.swift:1903`. It then reserves that complete remainder at lines 1905–1906.

Every reservation must encode an allocation event. `appendEvent` requires that event to fit within `cap - nextOutstanding` at lines 865–869.

For this reservation, `nextOutstanding == cap`. The remaining event allowance is therefore zero, while the encoded event is nonempty.

Every call fails before ImageIO creates a destination. The mandatory orientation control reaches this path at line 2123, so no complete A03 run can succeed.

Reserve a derived PNG bound that leaves admitted event headroom. Do not define the bound as every remaining logical byte.

## P1 — the 16 MiB ownership and pre-admission claim remains false

The repaired ledger still omits or admits several owners after allocation:

1. `AllocationEventLog.encoded` creates and appends a `Data` value at lines 802–805. The ledger checks its length only after that allocation at lines 865–869.
2. `copiedNativeString` bridges `CFString` to `String` before measuring, bounding, or reserving it at lines 1283–1292.
3. `actualFace` bridges, maps, and sorts the complete foreign table-tag inventory before any count or storage admission at lines 1301–1308.
4. Each table reservation is released at line 1342 while its copied `CFData` value is still in scope. The temporary `TableIdentity` array is also absent from `shapeOwnerBound`.
5. Native string reservations have no matching release. The later shape reservation separately charges retained shape strings, so the transfer is neither explicit nor balanced.
6. `NSMutableData(capacity:)` at line 1906 establishes an initial capacity. It does not constrain ImageIO growth before the post-finalization size check.
7. The 2,048-by-1,024 glyph image owns an 8 MiB RGBA backing at lines 1989–1994. Its `CGImage` snapshot at line 2017 is another logical copy or copy-on-write owner.
8. `reserveResultOwners` charges only the fixed `CaseResult` struct. Nested masks, toggles, repeats, errors, strings, and arrays are built before their encoded sizes are checked.

The snapshot alone can bring those two owners to 16 MiB. Font, line, result, event, and encoded-image owners remain live around them.

The local CoreGraphics header describes `CGBitmapContextCreateImage` as a copy operation. It allows copy-on-write as an implementation detail, not an ownership exemption.

Use an alpha-eight glyph snapshot, or derive a smaller admitted control. Charge the snapshot and encoded owner before creation.

Preflight native strings with a bounded CFString extent before creating Swift storage. Count the complete tag inventory before materializing it.

End each `CFData`, image, destination, and Swift owner before releasing its charge. Keep the 4 MiB and 16 MiB limits unchanged.

## P1 — `report.json` does not describe the final event log

The environment captures allocation-event count and bytes at line 2586. The fixed point also captures current event bytes and written totals at lines 2596–2603.

The report write suppresses its event at line 2609, despite the schema promising an event for every file write. The source then releases the 4 MiB report budget at line 2614.

That release appends one more allocation event. It changes the authoritative event count, event bytes, written-file total, and final outstanding charge after `report.json` is fixed.

The final report therefore disagrees with the surviving `allocation-events.jsonl`. This contradicts `output-schema.md:188–192` and `source-rationale.md:172–176`.

Design one terminal accounting sequence that does not mutate reported facts afterward. Verify the final report bytes, event bytes, written total, and outstanding charge together.

## P2 — descriptor and cancellation boundaries are incomplete

The loaded-image repair now retains one descriptor. It compares descriptor device and inode with `PROC_PIDREGIONPATHINFO`, then verifies stable metadata, SHA-256, and LC_UUID.

Several bounded-operation requirements remain open:

- `OpenInputFile.open` does not require a regular file at lines 674–684.
- `loadDescriptorData` can request the entire remaining 16 MiB in one `read` call. It performs no one-byte EOF probe.
- `loadedMainImage` constructs a pointer range from `sizeofcmds` before it queries the loaded region at lines 1163–1177.
- The source does not prove that the header range lies within `pri_address`, `pri_size`, and `pri_offset` from that region.
- One-shot hashes, source traversal, RLE scans, mask comparisons, and canonical equality loops lack bounded cancellation checkpoints.
- Setter and getter groups contain several native calls without an immediate before-and-after check.
- Cancellation errors contain the literal text `(phase)` at lines 630 and 633 instead of the actual phase.

Use fixed-size descriptor and hashing chunks. Require a regular file, then prove EOF and stable metadata.

Query the region before spanning its loaded bytes. Validate the complete Mach-O header range against the returned region.

The native call itself remains noninterruptible. The source can still check immediately before and after each call.

## P2 — native face identity and fallback evidence remain partial

A03 now records raw face bytes and SHA-256. It also creates the CTLine from the recorded attributed owner.

The following gaps remain:

- `InitialNativeFaceRecord` claims native glyph and units-per-em facts. `selectedFace` fills both fields from the raw parser at lines 1363–1374.
- `CTFontGetGlyphCount` and `CTFontGetUnitsPerEm` are called only for run faces. They do not establish the initial record.
- Native PostScript strings allocate before admission, as described above. The source does not enforce the selected 128-byte ASCII class.
- Missing-table and length failures stringify `observedTables`. They do not preserve a typed partial face with exact inventory, length, and copied table facts.
- A foreign table inventory is fully bridged before the 128-table guard can reject it.

Keep raw-container facts in `BoundFaceRecord`. Populate every field labeled native from the exact native getter.

Preserve typed partial face evidence on each failure. Avoid copying table payloads after an inventory mismatch.

## P2 — causal shape and geometry evidence is incomplete

The shared protocol requires finite Q16 typographic metrics and image bounds. A03 never calls `CTLineGetTypographicBounds`.

`ShapeRecord` has line and image rectangles. It has no width, ascent, descent, or leading fields.

`MatrixRecord.raw` intentionally retains nonfinite `Double` values at lines 1011–1019. Every encoder uses its default nonconforming-float behavior.

Foundation's local Swift interface exposes the throwing strategy and an explicit string-conversion strategy. A03 selects neither conversion nor a tagged finite representation.

A native NaN or infinity can therefore prevent the promised causal record from being encoded. The raw observation exists in memory but may never reach evidence.

Nonpresent `ImageBoundsRecord` values also discard their raw CGRect components at lines 1027–1034. Later raster context failures throw `shape: nil` at lines 1830–1839.

The repeat catch then stores `error.shape`, also nil, at lines 2337–2358. A later repeat can lose its distinct shape even though raw mask files survive.

Add exact Q16 typographic metrics. Use tagged, encodable scalar observations for every nonfinite or overflow state.

Carry the current repetition's complete shape into every render failure. Preserve typed raw bounds and face facts before rejecting them.

## P2 — the frozen schema rejects an allowed run status

The shared synthesis permits repeated and nonmonotonic cluster indices. It rejects fallback, glyph zero, RTL, nonidentity matrices, and unknown status bits.

The implementation follows that rule. It records `statusNonMonotonic` at lines 1570–1572 without adding a failure.

`output-schema.md:120–123` instead calls nonmonotonic status nonqualifying. A verifier built from the frozen schema can reject a valid producer record.

Remove nonmonotonic from that rejection list. Preserve the status bit and exact source indices as observations.

## A02 finding status

| A02 finding | A03 status |
| --- | --- |
| P1 `let` mutation | Closed in source. `orientationControl` now owns mutable raw data. |
| P1 loaded executable was not bound to its vnode | Core binding closed. Region-range and bounded-reader hardening remain P2. |
| P1 4 MiB and 16 MiB owner accounting | Open. New PNG deadlock, snapshot, event, string, table, and ImageIO gaps remain. |
| P2 exclusive and pre-admitted evidence writes | Exclusive descriptors are repaired. PNG memory admission is still blocking. |
| P2 causal native disagreement preservation | Partly repaired. Raw masks survive, but several shape, face, and nonfinite facts do not. |
| P2 exact native face and text inputs | Partly repaired. Raw identity and line owner are present; native initial metrics and bounded strings remain open. |
| P2 cancellation | Partly repaired. A token exists, but bounded loops and native call boundaries remain incomplete. |

## Confirmed A03 repairs

The following changes are present in source:

- The previous immutable-orientation-buffer mutation is removed.
- One opened executable descriptor stays live through metadata and byte verification.
- Loaded vnode, descriptor vnode, SHA-256, and LC_UUID comparisons are explicit.
- Ordinary evidence files use descriptor-relative create-new operations.
- Raw and canonical alpha files are written before later context and padding gates.
- Null and finite-empty bounds are distinct states.
- A later error can carry a separate `failureShape` when the throwing path supplies one.
- Raw font hashes and face fingerprints remain distinct.
- The exact attributed owner used for CTLine creation is recorded.
- The V1 policy and schema-1 raw authority remain unchanged.
- Nonmonotonic status is observational in code.

These repairs do not override the findings above.

## Local SDK grounding

This review inspected installed SDK declarations without compiling or calling them.

- `CGBitmapContext.h:239–250` defines bitmap-context image creation as a copy. It may use copy-on-write.
- `CGImageDestination.h:80–87` accepts mutable data. It provides no maximum-capacity contract.
- `proc_info.h:166–187` exposes region address, size, and file offset. Lines 331–334 pair that region with vnode facts.
- `CFString.h:355` exposes `CFStringGetMaximumSizeForEncoding` for a preconversion bound.
- Foundation's Swift interface exposes `JSONEncoder.NonConformingFloatEncodingStrategy`.

These declarations support the source findings. They do not establish that the uncompiled Swift bindings typecheck or work at runtime.

## Reviewed identities

| File | SHA-256 |
| --- | --- |
| `feasibility-swift-a03/probe.swift` | `ab8dd6b8b52334ac3a11cd9f81507d8ae0d503ead3aad0dbff4af93ec9023ac6` |
| `feasibility-swift-a03/output-schema.md` | `be44bf8a59d0524f2791c2a976b031c1657daa3141bcd587a0402f1da022fcba` |
| `feasibility-swift-a03/source-rationale.md` | `c29d28e4dcafeb7cc64cfbc18d9988956f7adf220a5dbd7c9e275455632eacc3` |
| `text-swift-source-review-a02.md` | `15155b8414111c4715471e91d5391ce07b3bd4ffea464a9d9185c6e70a5d974e` |

## Proof-build verdict

Do not build or typecheck this frozen A03 package as the proof producer. Preserve it as reviewed source evidence.

Repair the four P1 blockers and four P2 groups in a new version. Re-review all three files and the exact component arithmetic before build authorization.

Even a green build would not establish native feasibility, product text support, encoded output, playback, hearing, lyrics, or creative acceptance.

This is a same-model-family peer review. No cross-family review was performed.
