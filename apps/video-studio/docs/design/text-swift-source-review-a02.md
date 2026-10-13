# Swift native text probe source review A02

## Disposition

The A02 Swift package is **not green for build or typecheck freeze**.

I found three P1 blockers and four P2 source defects. The source remains unbuilt and unexecuted. These findings are source defects, not native observations.

Preserve A01 and A02. Repair a separate successor, then repeat source, schema, and rationale review. A green source successor would authorize build and typecheck only.

## P1 — the frozen source contains an evident mutation of a `let` value

`orientationControl` declares `rawData` with `let` at line 1482. Line 1497 calls the mutating `removeAll(keepingCapacity:)` method on that value.

This is an evident Swift compile blocker. Change the owner to `var`, then clear it before releasing its permit.

Other compiler and SDK compatibility remains unverified until an authorized build. This review did not run a compiler.

## P1 — the reported executable is not bound to the loaded vnode

`loadedMainImage` reads the dyld path and in-memory `LC_UUID`. `run` then resolves that pathname, calls pathname-based `lstat`, and reads it through a separate `Data(contentsOf:)` open.

No opened file descriptor is compared with the vnode that backs the loaded dyld image. A same-UUID pathname replacement before the first `lstat` can therefore pass. The caller can hash the replacement while the process continues executing the earlier image.

The successor must hold one executable file descriptor through metadata capture and hashing. It must compare that descriptor's device and inode with the loaded executable region. It must also compare the in-memory and file `LC_UUID` values. Stable size, modification time, and change time must bracket the descriptor read.

Darwin `proc_pidinfo(PROC_PIDREGIONPATHINFO)` can establish the loaded region's vnode. A separately proved descriptor-based launch route is also acceptable. Path equality and UUID equality alone do not prove the running image's bytes.

The schema and rationale currently overclaim loaded-image authority. Update both documents with the implemented evidence boundary.

## P1 — the 4 MiB and 16 MiB ownership claims omit live representations

The fixed envelopes do not enforce the stated logical payload bound. These concrete overlaps remain outside the derivation:

1. `CaseFile`, `FontManifest`, `InputAuthority`, parsed font records, hashes, and ledger records are constructed before the structured reservation. Their decoded owners are separate from the retained input `Data`.
2. The first complete `ShapeRecord` remains in `shape`. Repetitions two and three each construct another complete shape while the first remains retained. One 262,144-byte case envelope accounts for only one run, face, table, and glyph tree.
3. `shapeDigest` allocates an encoded shape `Data` without a reservation while the retained and working shapes coexist.
4. `AllocationLedger.records` retains every event globally. Each `CaseResult` also copies its case slice. The 20,480-byte miscellaneous component does not cover both owners. At the declared 64-run cap, native table reservations alone can create thousands of records per case.
5. `CGFontCopyTableForTag` returns a retained `CFData`. Bridging it to Swift `Data` can create a second table owner. The derivation charges one table copy and does not prove zero-copy bridging.
6. Every report fixed-point iteration retains the old `reportData` while `encoder.encode(report)` creates `next`. One 4 MiB report reservation does not cover both buffers.

The source also releases several logical permits before it explicitly clears the corresponding owner:

- orientation raw, raw-`Data`, and canonical owners at lines 1493–1498;
- every returned canonical mask through `releaseMask`, before replacement with empty `Data`;
- loaded image bytes at lines 1786–1787;
- case-result and final-report buffers while their values remain in scope;
- the structured envelope while `results`, `orientation`, and `report` remain owned.

`loadBounded` also reserves a pathname metadata size before `Data(contentsOf:)`. A growing file can allocate beyond that reservation before the count check rejects it.

The successor needs a checked component derivation for every coexisting owner. Reserve a separate fresh-execution shape and digest buffer. Count one authoritative allocation log, or include both retained copies. Charge every possible native-table bridge copy.

Use one bounded descriptor read for each input. Clear or end each owner before releasing its permit. Re-encode reports without retaining two maximum-sized buffers. Require the final encoded report's `writtenFilesBytes` value to equal the actual reserved report write, rather than assuming three iterations converge.

These changes must keep the 4 MiB structured, 4 MiB report, and 16 MiB logical payload limits. A larger unexplained blanket allowance would not close this finding.

## P2 — evidence writes are neither exclusive nor admitted before every write

`writeExclusive` checks `fileExists` and then calls `FileManager.createFile`. That sequence is not an atomic create-new operation.

The ImageIO path also checks `fileExists` before `CGImageDestinationCreateWithURL`. ImageIO finalizes the PNG before `reserveFileWrite` checks the 256 MiB file budget.

Create the output directory and ordinary files with descriptor-relative create-new operations. Use `O_CREAT | O_EXCL | O_NOFOLLOW` and retain the directory descriptor. Encode PNG output into a pre-admitted bounded owner, then write it through an exclusive file descriptor.

Keep successful partial files after later failures. Do not relabel the current paths as exclusive evidence.

## P2 — several native disagreements still lose their causal observation

The source improves failure preservation, but these paths remain incomplete:

- `renderLine` rejects a nonidentity context or changed padding before it saves the raw and canonical bytes.
- Q16, line-bound, image-bound, and glyph conversion helpers can throw with `shape: nil` after native observations exist.
- A later repetition keeps the first successful `shape`; its catch path discards a differing `error.shape` from the failed repetition.
- Missing native tables and table-length mismatches omit the observed tag inventory, actual length, and already copied table facts.
- `observedImageBounds` reports `CGRectNull` as `empty`, merging null and finite empty states.

Persist the raw mask before validating its context and padding. Retain the complete causal shape or face record for each failed repetition. Keep null, finite empty, present, infinite, and nonfinite geometry states distinct.

All mismatches must remain nonqualifying. The repair must not infer successful native behavior from ideal bounds or earlier repetitions.

## P2 — the face and text records do not fully describe the exact native inputs

The shared protocol requires each selected face to expose its raw byte count and SHA-256. `BoundFaceRecord` omits both fields, and `shape` explicitly discards its `fontHash` argument.

`BoundFaceRecord` is documented as raw-container authority. Its PostScript name and variation state are instead copied from the initial `CTFont`. These are native observations, not raw SFNT parser facts.

`nativeTextRoundTrip` verifies one temporary `NSAttributedString`. `makeLine` then creates a different attributed string from the original Swift text. The record therefore does not identify the exact attributed object used to create the line.

Add raw font bytes and SHA-256 to the bound face authority. Separate raw authority from initial native-face observations. Build the line from the checked round-tripped string and attributed owner, or record the exact attributed owner used by `CTLineCreateWithAttributedString`.

Cap or charge actual copied native PostScript names and framework strings before retaining them. A foreign fallback face cannot inherit a source-font string bound.

## P2 — the required cancellation boundary is absent

The shared protocol requires cancellation checks before and after native calls and during bounded copies. The A02 source has no cancellation owner or check.

Add one predeclared cancellation mechanism. Check it around each bounded native operation and copy loop. Keep the truthful limitation that cancellation cannot interrupt a CoreText, CoreGraphics, or ImageIO call already in progress.

External process termination alone does not satisfy the probe's structured cancellation contract.

## Confirmed repairs

The following A01 findings are closed in source:

- The face fingerprint uses the selected NUL-terminated domain, big-endian scalar, two-byte table count, and four-byte table lengths.
- Raw table offsets and checksums remain separate from native table observations.
- Exact cases, manifest, and authority hashes are checked before CoreText construction.
- Q16 rejects the positive `2^63` boundary.
- Zero-glyph runs avoid null base-address force unwraps.
- Sorted ranges prove source partition while visual run order remains intact.
- Full matrix tuples, requested setter calls, actual CTM, and actual text-matrix getters are recorded.
- Main/guard equality and outside coverage gate every completed repetition.
- Both clipped and reference hashes must remain stable across exactly three repetitions.
- The antialias-disabled control must be binary and differ. Other toggle results remain observations.
- Orientation raw and canonical files survive a failed row hypothesis.
- The native rectangle and glyph image paths keep the allocation, context, snapshot, ImageIO destination, and file read within the stable backing-memory scope.

These repairs do not override the blockers above.

## Reviewed identities

| File | SHA-256 |
| --- | --- |
| `feasibility-swift-a02/probe.swift` | `96b453e1db3b3c6a8903b3bad1a4080e50bb62fe9791acbbf88ed3d9a1fd6dbf` |
| `feasibility-swift-a02/output-schema.md` | `22c66cc497d3bee9dffd19761f4e762ecf26685889cae217234cf8515cc0a61f` |
| `feasibility-swift-a02/source-rationale.md` | `12762a2d0bdc9a998ab87b9b3f973581fc194480e9ddb2d239d3b8470cc4a181` |
| `text-swift-source-review-a01.md` | `48dd75e0fec217f375bf7c390d76b2923b56435ad238a54d77ec2b883a4e3b90` |
| `text-rust-source-review-a01.md` | `cf55cc3b301668c6e353d20d162007985e527f8f7fdc51b42a160cd130aae01b` |
| `text-rust-parent-source-review-a01.md` | `5e035ca1fdb9bb0cea75c47816efcf505633b83e183204ad2daec38182e16dfe` |
| `text-synthesis-a01.md` | `d497f472b0d5162e61fab482e2f720a89192645b88b1430b1b61577f0330c323` |
| `text-probe-protocol-a01.md` | `4e4e399072372f6dbc02bb16f55d80fd1ca7cf1690ac8643d34055a1cae31d89` |

## Proof-build verdict

Do not build or typecheck this frozen A02 package as the proof producer. Preserve it as reviewed source evidence.

Close all three P1 and four P2 findings in a new version. Re-review the complete source, schema, rationale, and component arithmetic before authorizing a build freeze.

Even a green build would not establish native feasibility, product text support, rendered output, playback, hearing, lyrics, or creative acceptance.

This is a same-model-family review. No cross-family review was available.
