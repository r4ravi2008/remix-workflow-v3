# Native text design judgment A01

## Result and review boundary

Select **Candidate A** as the whole-shape base. Candidate A scores **24/25**. Candidate B scores **17/25**.

Candidate A supplies the stronger immutable identity, coordinate policy, cache ownership, admission model, schema gate, and proof plan. Its explicit layout box is the safer first native text contract. Candidate B has useful guard and baseline-anchor ideas, but its execution and memory descriptions contradict each other.

This is a design judgment. No CoreText or CoreGraphics probe ran during this review. Neither candidate has proved Indic shaping, fallback observation, alpha pixels, row orientation, or native output fidelity. Product integration must remain blocked until the selected isolated feasibility probe passes.

The review read the task, rubric, grounding, and both candidates end to end. The reviewed candidate identities are:

- Candidate A: `6851884d8a76ce5a44181eab1d5c7991f61b323754907b4aaeb4ef69c9c6198e`
- Candidate B: `5d2bba28c4faea686c03e099977d434376769e20131b07f8b766121158af9da0`

All reviewers available for this unit share one model family. This is task and artifact separation, not cross-family or blind model independence.

## Scores

| Criterion | Candidate A | Candidate B | Judgment |
| --- | ---: | ---: | --- |
| 1. Caller depth and ordering | 5 | 5 | Both retain the existing `Project` workflow, untimed font storage, track-vector order, and private native work. |
| 2. Identity and typography | 5 | 4 | Both bind exact font and shaping facts. A also defines a complete face-table record, full affine matrices, closed language rules, and measurement refresh. |
| 3. Geometry and ownership | 4 | 1 | A has one exact box, baseline, row transform, alpha policy, admitted cache, and permit. Two lifetime and accounting statements need repair. B has a guard-coordinate ambiguity, a definite budget underestimate, and no coherent reusable raster owner. |
| 4. Compatibility and integration | 5 | 4 | Both propose omitted append-only fields and Plan8. A specifies closed wire types, exact legacy fixtures, direct-use selection, and every central admission path more completely. |
| 5. Verifiability and extension | 5 | 3 | A provides a decisive stop-before-integration probe and separate pure, native, tamper, output, and lifecycle proofs. B proposes similar evidence, but its proof target is not yet a coherent executable contract. |
| **Total** | **24/25** | **17/25** | **Candidate A is the base.** |

## Whole-shape choice

Use Candidate A's following shape:

- `FontResourceImport` and `StoredFontResource` are untimed project resources in the existing blob CAS.
- `VideoTrack::text_clips` appends text without rewriting existing `VideoClip` bytes.
- A caller supplies an exact integer `TextLayoutBox`, local integer baseline, fixed Q16 size, RGBA8 style, language, and LTR direction.
- Plan8 binds directly used font closure, exact source text, complete shaping evidence, layout, motion, mask, backend, and raster policy.
- One text policy owner performs preparation and execution observations.
- Execution reshapes once per active text source, compares all immutable evidence, rasterizes once, and caches Rust-owned premultiplied pixels.
- The existing worker count, capacity-one ports, bottom-to-top compositor, writer, receipt schemas, cancellation, fencing, and publication remain authoritative.

The explicit box makes clipping an author decision. Coverage outside `[0,width) x [0,height)` is intentionally discarded. CoreText image bounds remain observations and never resize the raster. This policy is more stable than deriving allocation and placement from unproved native bounds.

Candidate A's caller examples fit the current `Project::commit`, `head`, `prepare_export`, `export`, `verify_export`, `cancel_export`, and reconciliation APIs. Its generic `PropertyCurve` usage also matches the current motion contract.

## Required repairs to Candidate A

### P2: make final-response cache retirement executable

Candidate A says the worker retires its cache after the final response is consumed, while adding no acknowledgement channel. A worker cannot observe consumer completion under that channel contract.

Use the existing request-response barrier precisely:

1. The worker owns one cached `Arc<AdmittedTextRaster>`.
2. Each response owns another `Arc` to the same raster and permit.
3. Before sending the final response, the worker drops its cache reference.
4. The response retains the raster through compositor validation and blending.
5. The compositor drops the response before requesting the next frame from that track.

No raster bytes are cloned. The single permit remains alive until the last `Arc` drops. Cancellation and disconnected-channel paths must drop both references before another text source allocates.

### P2: account for every simultaneously retained application-owned copy

Candidate A's temporary formula is conservative for native construction, but it does not explicitly separate retained Plan8 evidence from the fresh execution observation used for comparison.

The synthesis must name and charge each concurrent category:

- the persistent eight-byte premultiplied raster for every temporally active text source;
- the shared immutable Plan8 string, font closure, tables, runs, glyph arrays, positions, advances, and indices;
- the fresh execution-side UTF-8, UTF-16, run, glyph, table-fingerprint, and alpha8 allocations;
- the Rust font read, copied `CFData`, and maximum copied table;
- any serialization buffer retained while another text allocation is live;
- the existing canvas, writer, movie, PNG, response, and source reservations.

The plan and execution observations may be compared incrementally to reduce this charge. If both complete observations coexist, the estimate must charge both. Reservations must precede their owned allocations. Native framework internals remain an explicit unmeasured limit.

These repairs are mandatory before implementation. They do not require changing Candidate A's public caller shape.

## Candidate B blockers

### P1: its cache and response types cannot implement its stated execution

Candidate B's pseudocode reshapes and rerasterizes during each frame request. `TextDecision` owns `AlphaRaster16` by value and has no admitted permit or shared cache handle. The document also claims one raster per active source.

Those statements cannot all hold. Moving the raster into the first response leaves nothing for later frames. Cloning it duplicates up to 64 MiB per response. Rerasterizing performs native shaping on every frame. Candidate A's admitted `Arc` design resolves this conflict.

### P1: the 96 MiB estimate is arithmetically too small

Candidate B allows a 64 MiB premultiplied raster, an 8 MiB guarded coverage buffer, and two 16 MiB font copies. Those values already total 104 MiB. UTF-8, UTF-16, observations, table copies, and response retention add more.

The fixed 96 MiB estimate therefore cannot satisfy admission-before-allocation. Candidate B also does not place a permit inside `TextDecision`, so the stated runtime lifetime is unenforceable.

### P1: the guarded raster coordinate contract is incomplete

Candidate B allocates a one-pixel outer guard, but its row formula does not define whether `h` is the inner or guarded height. It also omits the inner `+1` guard-space offset. For inner row `y`, the exact native guarded row would need a formula equivalent to `(inner_height + 2 - 1) - (y + 1)`.

The draft also lacks a subpixel-quantization field and setter contract. Q16 evidence does not disable CoreGraphics subpixel quantization. The native `Allows` and `Should` settings are independent raster state.

### P2: shaping and wire evidence remain under-specified

`TextMatrixIdentity` stores only `a`, `b`, `c`, and `d`. It cannot bind or reject `tx` and `ty`. The language grammar does not define canonical script and region forms or enumerate rejected line and bidi controls. The sketched nested wire types omit `deny_unknown_fields`.

Candidate B also lacks Candidate A's guarded font-measurement refresh identity. Its font observation may be deterministic, but the commit and replacement rules are not defined.

These are design defects, not missing native proof alone. Candidate B should not become the implementation base.

## Selective grafts from Candidate B

Graft three ideas without adopting Candidate B's runtime shape:

1. Rename Candidate A's Plan8 font map to `font_closure`. This distinguishes directly used plan resources from the larger snapshot resource map.
2. Add Candidate B's outer-guard concept to the isolated probe. Render controlled, generously sized fixtures into a guarded buffer and require an untouched guard. This detects transform and padding mistakes without changing author-declared clipping.
3. Preserve a baseline-anchor convenience as future authoring sugar. A future constructor may derive an explicit layout box after a proven measurement pass. The normalized plan must still store Candidate A's fixed box and baseline.

Do not graft B's tight native-bounds surface into the first unit. It makes allocation, placement, and clipping depend on the very native geometry that the probe still needs to establish.

## Concrete rejected choices

- Reject per-frame shaping or rasterization. Shape, compare, and rasterize once per active text source.
- Reject a by-value full raster in each frame response. Use one admitted shared raster with one permit.
- Reject the 96 MiB lump estimate. Use checked component estimates and the temporal sweep.
- Reject native-bounds-derived production surfaces for unit one.
- Reject a partial four-value text matrix. Bind the complete affine tuple, including translation.
- Reject Q16 geometry as a substitute for native subpixel switch control.
- Reject system-family lookup, process font registration, automatic fallback, collections, variable fonts, color fonts, and CFF for this unit.
- Reject putting font resources into `MediaKind`, `MediaDescriptor`, or timed `SourceRange` lineage.
- Reject a new receipt schema, output profile, public executor, text-specific export call, or dense per-frame plan trace.

## Mandatory synthesized contract

The selected design must satisfy these requirements before runtime work begins:

1. Freeze the current real Plan7 document and all existing Snapshot1, Plan2 through Plan7, and Receipt2 through Receipt4 identities.
2. Keep all new Snapshot1 and commit fields append-only with both `default` and `skip_serializing_if`.
3. Select Plan8 only for text directly used by the requested timeline.
4. Admit Plan8 through one central validator used by prepare replay, render, verification, and recovery.
5. Store only directly used fonts in `font_closure`, in deterministic key order.
6. Bind exact UTF-8, UTF-16BE, normalization-none, language, LTR direction, style, layout, complete ranges, glyphs, positions, advances, indices, full matrices, run fonts, backend, and alpha hash.
7. Recompute each run font's table identity from the actual shaped run. Reject any mismatch and glyph zero.
8. Use Candidate A's exact alpha-only context, identity matrices, baseline transform, row reversal, and closed antialias, smoothing, subpixel-positioning, and subpixel-quantization switches.
9. Apply style alpha, premultiplication, clip opacity, and mask coverage with the declared integer rounding order.
10. Keep all Core Foundation, CoreText, CoreGraphics, and borrowed bitmap objects inside the native text operation.
11. Reserve persistent and temporary application-owned allocations before allocation. Retire sequential caches at the proven request-response barrier.
12. Retain the bounded-call cancellation limitation. Check cancellation before and after native calls, during copies, before response, and before append.

## Proof gate

The first implementation action must be the isolated native feasibility probe. It must use the exact committed Telugu and Devanagari font bytes. It must prove byte-owned construction, complete ranges, fallback visibility, full matrices, row orientation, closed raster switches, guard behavior, repeated alpha hashes, and backend versions.

If that probe disagrees with the selected coordinate, fallback, or raster contract, stop and redesign. Do not adapt the product around an unexplained discrepancy.

After the probe passes, require:

- an independent native shaping and raster producer;
- pure integer vectors for alpha, premultiplication, opacity, masks, clipping, and track order;
- single-fact plan and font tamper controls;
- legacy byte and recovery readbacks;
- one ordinary `NativeColorMasterV2` Plan8 output with Telugu and Devanagari;
- exact pre-writer frame comparison, decoded output and ROI checks, source and audio clocks, cancellation, fencing, and staging recovery.

Those checks establish a bounded technical unit only. They do not establish normal-speed playback, hearing, creative acceptance, film lyrics, or completion of the user film.

## Verdict

Candidate A can proceed to a corrected synthesis and isolated feasibility probe after the two P2 repairs above. No Candidate A design P1 remains in this review. Native feasibility and output acceptance remain unproved.
