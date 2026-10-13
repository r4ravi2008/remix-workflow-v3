# Parent Swift probe source review A01

The parent read all 1,379 source lines, output schema and rationale end to end.
Source SHA is `5bcc98a643c70e2e590f7dda00ddba22faaf0e10966e2b3267ddcf5c12142d6f`.
The source remains unbuilt and unexecuted. Preserve it and author a separate A02 repair package.

## Execution blockers

1. **Face fingerprint contract differs.** The code uses `video-studio-text-face-v1`, a four-byte table count and eight-byte table lengths. Selected A requires `video-studio-font-face-v1`, a two-byte count and four-byte lengths. Use exact selected bytes. A `head` table version is not an observed SFNT container scalar. Separate bound container facts from actual native table observations. Native tables have no source offsets/checksums; do not label copied expected values as independently observed native values.
2. **Logical admission omits live copies.** `renderLine` allocates raw Array, `Data(raw)` and a whole canonical Data while charging only the raw Array. It releases that charge before returning the canonical buffer. Main/guard buffers then coexist uncharged. Glyph arrays, source encoding, parsed/retained observations and several copies also bypass the ledger. Give every retained allocation an enforceable lifetime and charge before allocation. Reserve the structured-observation budget before construction and release mask buffers before the large RGB glyph image. Publish a checked worst-case ledger under16MiB.
3. **Native image lifetime crosses pointer scope.** Both ImageIO helpers assign CGImage outside `withUnsafeMutableBytes`. A snapshot may share bitmap backing. Keep snapshot/write/drops inside that pointer scope or use explicit stable allocated memory and release all native objects before freeing it.
4. **Some required comparisons do not fail.** Main/guard inequality and outside coverage are recorded without rejection. The same is true for the clip/reference comparison. Repeated shape and guard hashes are not included in `allSupportedRepeatsEqual`; fewer than three repeats can report equality. Gate all declared comparisons and require exactly three complete supported repetitions.
5. **Failure evidence is discarded.** Orientation mismatch throws before its JSON or raw/canonical bytes are saved. Font-fallback errors omit the actual differing inventory/name/metrics. Save causal records before rejecting. Preserve all alpha raw/canonical masks with path/size/hash descriptors, including repeats and controls, so the parent can independently inspect and compare pixels.

## Required source/schema corrections

- Verify exact A02 and manifest hashes before native calls, not only their shape/count. The driver will independently rehash them too.
- Observe round-tripped native attributed text/CFString bytes and UTF-16 units before shaping.
- Read actual CGContext CTM and text matrix where public getters exist. Do not emit a fictitious `CGContextSetCTM` call. Check full identity tuples for selected font and run text/font matrices.
- Set fill text mode explicitly. Setter traces must name actual executed APIs.
- Treat nil or an empty variation dictionary as empty. Reject actual nonempty variation state.
- Handle zero-glyph runs without force-unwrapping zero-length buffer base addresses.
- Check Q16 values strictly below the positive2^63 boundary after rounding. `Double(Int64.max)` rounds to2^63 and cannot be an inclusive guard.
- Represent a native null/empty image bound explicitly. Do not normalize arbitrary nonfinite geometry or infer ink from ideal bounds.
- Sort ranges for the full-source partition check while preserving original visual run order and legitimate nonmonotonic indices.
- Reject mismatch between declared glyph count and copied arrays before any native buffer copy.
- Use actual exclusive file creation and enforce the total256MiB file budget.
- Preserve input policy classes and observed failures. No native state getter claim or pixel interpretation may be added after execution.

## Boundary

These are source defects found before execution, not failing native observations.
API import/typechecking remains unverified. Source repair and schema review must close before build or run.
The selected row reversal remains a hypothesis. Preserve any contradiction to the separate native ImageIO image.
Product support, native output, hearing, playback and creative acceptance remain false.
