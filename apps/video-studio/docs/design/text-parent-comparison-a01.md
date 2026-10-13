# Parent text comparison A01

The parent read both complete candidates and the grounding end to end before scoring.
This is a design comparison. No CoreText behavior or raster result has been observed yet.

| Criterion | A: explicit box | B: tight surface |
| --- | ---: | ---: |
| Caller depth and ordering | 4 | 5 |
| Identity and typography | 5 | 4 |
| Geometry and ownership | 4 | 3 |
| Compatibility and integration | 4 | 3 |
| Verifiability and extension | 5 | 4 |
| Total | 22 | 19 |

Candidate A SHA: `6851884d8a76ce5a44181eab1d5c7991f61b323754907b4aaeb4ef69c9c6198e`.
Candidate B SHA: `5d2bba28c4faea686c03e099977d434376769e20131b07f8b766121158af9da0`.

## Proposed base

A has the clearer first-unit execution contract. Its explicit box is an authored clip boundary.
The box gives stable dimensions without relying on ideal glyph bounds as raster allocation authority.
The caller must choose the box and baseline. Those values control intended layout and clipping.
B hides more geometry behind a baseline anchor, but its two-pixel pad still needs native evidence.
A also specifies once-per-active-source raster caching, exact native switch pairs, run-font size and matrix checks, and a fuller admission formula.

Both candidates preserve one picture-track ordering authority and keep fonts outside timed SourceRange values.
Both use the existing Project operations and private native objects. Neither exposes a renderer subprocess.

## Required synthesis corrections

1. Keep the existing text-free compiler and Plan2–7 admission behavior intact. Exact new feature derivation applies to Plan8. Do not silently tighten historical plan admission during a shared-validator refactor.
2. Use A's intentional box clipping as the public contract. Native proof must distinguish an intentionally clipped small box from an unclipped generous box. Image bounds alone cannot establish either observation.
3. Measure row orientation with a separate native implementation. Do not accept the stated row reversal merely because both callers copied the same formula.
4. Charge all application-owned buffers that coexist, including row conversion. A fresh native mask plus a copied canonical mask needs two mask charges, or an explicitly in-place row reversal.
5. Keep one cached Rust raster per active text item. Native reshaping happens once when the execution cache starts, after preparation shaping. It must not run once per output frame.
6. Keep A's LTR embedding attribute, complete six-component matrix evidence, actual run-font size/matrix checks, and unknown-status rejection.
7. Use one closed named raster policy rather than freely configurable boolean policy fields. The native setter tuple is fixed.
8. Limit the initial font size to 512 pixels, matching the maximum synthetic mark cases. A later extension may raise that measured boundary.
9. Reopening an exact historical output validates saved structure and media. It must not require reshaping on a newer host. A fresh render requires the saved backend tuple and exact execution comparison.
10. Repair qualitative probe inputs before execution. Bind byte hashes and UTF-16 ranges; make unsupported ASCII letters, emoji and unassigned scalars explicit whole-item rejection cases. Add a supported digits-only ASCII control.

## Selective grafts

Use B's explicit outer-guard experiment as a probe control on generous boxes.
The guard experiment tests fixture completeness; it does not change the authored box or become a universal two-pixel padding promise.
Use B's explicit surface coverage hash and nonzero-bounds comparison, already compatible with A's evidence.
Defer automatic tight-surface allocation and baseline-derived destination geometry to a separate extension.

## Limits

Independent judging is still pending. Selection is provisional until its complete findings are read.
The same model family supplies the parent and review agents.
No runtime edit, native probe, text output, font fallback proof or creative acceptance is claimed.
