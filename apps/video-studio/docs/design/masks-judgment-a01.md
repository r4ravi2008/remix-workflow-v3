# Native picture masks judgment A01

Status: complete design judgment. No runtime, media, project, GPU, or Resolve state changed.

## Decision

Use Candidate A as the whole-shape base.

Candidate A keeps the existing `Project` aggregate deep. It also defines one bounded, useful axis reveal through authoring, storage, planning, execution, and observation.

Its picture-window contract follows crop, fit, placement, and motion without exposing compositor coordination. Its final-weight rule also handles Q16 values that round to zero.

Candidate B contains useful future rectangle and feather ideas. Its delivered shape is not ready for implementation.

Candidate B has an invalid 65-character synthetic-audio hash in three places. `ContentHash::parse` requires 64 lowercase hexadecimal characters.

Candidate B also leaves `RectangleMask` undefined between `MaskWire` and `PlannedMask`. Its planned type omits the family that central validation claims to compare.

No cross-family reviewer was available. This judgment does not claim blind or cross-family review.

## Scores

| Criterion | Candidate A | Candidate B |
| --- | ---: | ---: |
| 1. Caller depth | 5 | 3 |
| 2. Pixel contract | 5 | 2 |
| 3. Bounded ownership | 5 | 3 |
| 4. Durable compatibility | 4 | 2 |
| 5. Verifiable outcome | 4 | 2 |
| **Total** | **23/25** | **12/25** |

### 1. Caller depth

Candidate A uses `commit`, `prepare_export`, `export`, `cancel_export`, and `verify_export`. Callers never coordinate readers, workers, coverage, composition, or writer shutdown.

Candidate A provides a complete path from `PictureMask` to `PlannedPictureMask` and `LayerObservation`. The plan stays source-bound through the existing aggregate.

Candidate B keeps the same public operations. However, its example cannot parse because the synthetic asset hash has 65 characters.

Candidate B also lacks a complete authoring-to-persisted conversion. `MaskWire`, the mentioned `RectangleMask`, and `PlannedMask` do not form one roundtrippable contract.

### 2. Pixel contract

Candidate A defines destination picture-window coordinates, Q16 coverage, inversion, opacity combination, opaque alpha, and bottom-to-top blending.

Its integer-window formula is correct for a half-open source-bearing interval `[lo, hi)`. Pixel centers are at `n + 0.5`.

The resulting integer interval is `[ceil(lo - 0.5), ceil(hi - 0.5))`. Canvas clipping must happen after this interval is fixed.

`lo` and `hi` must come from the existing `Mapping` geometry once. Mask code must not recompute those floating-point edges separately.

For the reveal axis, `j` must use the unclipped interval origin. Negative placement must never rebase reveal progress.

Candidate A's binary search is valid because non-inverted coverage is monotone in `j`. Inversion reverses that monotonicity.

Multiplication by fixed nonnegative opacity preserves monotonicity. The search must test final `effective_q16 > 0`, rather than raw coverage.

Candidate B defines a useful hard edge and an L-infinity feather. However, rectangle pose interpolation lacks exact signed rounding and overflow rules.

Candidate B does not define `MAX_MASK_KEYS`. Its `radius_q16` range also does not distinguish Q16 units from whole pixels precisely.

Candidate B's preflight visibility uses nonzero mask coverage. This is incorrect when positive mask, mask-opacity, and layer-opacity values round final weight to zero.

### 3. Bounded ownership

Candidate A adds no coverage plane, decoder, cache, native object, or worker. It retains capacity-one track responses and the bounded writer channel.

Candidate A charges active source copies, effective raster bounds, three canvases, and the conservative PNG allowance. Fully masked active sources remain charged.

Native objects stay inside AVFoundation completion callbacks. Only copied pixels, rasters, permits, clocks, ordinals, and scalar observations cross channels.

Candidate B accounts for its four-byte Q16 coverage plane and describes the existing channel barriers. That ownership shape is feasible after repair.

However, Candidate B does not define a nonallocating preflight extrema calculation. `sample_mask` returns an owned plane, so preflight allocation order remains ambiguous.

Its runtime must reserve both raster and coverage before allocation. Its preflight must calculate the same final-weight bounds without allocating either payload.

### 4. Durable compatibility

Candidate A correctly keeps Snapshot 1 and Receipt 2. Absent masks keep the existing Plan 2, 3, 4, or 5 selector.

An authored mask selects Plan 6. Central validation recompiles and compares masks, motion or placement, source ranges, ordinals, clocks, lineage, and audio uses.

Candidate A's compatibility table contains six documents. The required historical set contains eight documents.

Implementation must preserve these exact eight files:

| Document | Bytes | SHA-256 |
| --- | ---: | --- |
| `snapshot-schema1.json` | 3064 | `a4afc9237cdc477ddc0c62023b7e0ed185a9f39bd3f72fd3f6596964d1c82423` |
| `snapshot-schema1-placement.json` | 409983 | `00d8a0eb3bbf0cd6290e68fffaa8c4d8b5a654446fb2220f5d084da17944e1ea` |
| `snapshot-schema1-motion.json` | 410865 | `1947fcb6939dbec40f13ae23b87a156f5d6e1758fa18e058aaa1f810abc313d3` |
| `plan-schema2.json` | 369279 | `97fdd9f63d48ee3b600ee37a845c302e79815bd1870b20dae376f9c4a957e025` |
| `plan-schema3.json` | 4983 | `4e5a89b00e7b5fabaafb4bf1335c1a5c3538c593765b4f5e5c818ff6bcede219` |
| `plan-schema4.json` | 413967 | `5cf0320f82bfc19839c5a06ffec15449fcdb80b97be15e2b4fb4105517ef0687` |
| `plan-schema5.json` | 415912 | `8ca51e03d048971a86cb598990fabd2f93f839c98b1b6c5fda3eb7aa90c3ee06` |
| `receipt-schema2.json` | 1418 | `44c0c27ad1a58f22746011673d8e4d4a211c5b5cdeffcb18172d6cc73fc73be2` |

Candidate B states the same schema intent. Its undefined persisted type and absent planned family prevent complete central recompile and comparison.

Candidate B also lists only six compatibility documents. Both candidates omitted the original and placement Snapshot 1 fixtures.

### 5. Verifiable outcome

Candidate A requires independent integer vectors, exact pre-encode BGRA, a fresh mask-capable producer, native decoding, clocks, source binding, audio, cancellation, and retained failures.

Its native phrase “nonempty mask region” is too broad. A fractional edge row or column differs from the full placement window after lossy H.264 encoding.

The proof manifest must name exact per-frame regions before export. It must separate the following regions:

- The full composed frame.
- Fully covered reveal interior.
- The one-pixel fractional transition strip.
- The fully hidden region showing the lower track.
- Contain-bar, overlap, and signed-clipping regions.

Each nonempty region needs coordinates, sample count, metric, and threshold. The transition strip cannot inherit a full-placement PSNR result.

Exact pre-encode comparison remains the authority for Q16 edge placement. Decoded H.264 comparison measures the encoded result within declared tolerances.

Candidate B proposes good pure-vector categories. Its proof cannot start from the stated caller document because the synthetic hash is invalid.

The frozen A14 producer is predecessor evidence only. A native mask run requires a newly frozen, mask-capable producer and matching build manifest.

Candidate B also omits an explicit active schema-6 cancellation experiment from its proof procedure.

## Required Candidate A repairs

1. Define `PictureWindow` as a signed half-open rectangle before canvas clipping.
   Set `width = end - start`, and calculate `j` from the unclipped origin.

2. Use one pure evaluator for runtime, preflight, and response validation.
   Keep the independent verifier separate from product code.

3. Prove effective-bound binary search against exhaustive per-pixel evaluation.
   Cover inverted and non-inverted masks, one-pixel windows, and both canvas clipping directions.

4. Include positive factors that round final weight to zero.
   Required boundaries include `opacity=1` with coverage `32767` and `32768`.

5. Keep one-key, constant, step, and linear progress programs valid.
   A declared constant mask must still select Plan 6.

6. Preserve source authority on a covered, fully masked overlay frame.
   The worker must decode, copy, and validate the selected ordinal and PTS before returning no raster.

7. Prove that fully masked execution directly.
   Use an internal worker observation or fault injection; a plan source map alone is not execution evidence.

8. Keep preflight allocation-free for mask evaluation.
   Charge every active source, effective raster, three canvases, and the existing global PNG allowance.

9. Preserve all eight legacy documents byte for byte.
   Add the motion Snapshot and Plan 5 records to the existing six-document roundtrip test.

10. Freeze the mask-capable producer before the first export.
    Bind its binary, manifest, revision, Plan 6, receipt bytes, output, source closure, and product reverify result.

11. Run the 72-frame four-track proof with two simultaneous movie readers and both PNG sources.
    Include motion, signed clipping, contain bars, sparse intervals, inversion, constant progress, and linear progress.

12. Verify every selected source ordinal and source PTS with explicit epochs.
    Masks must not change `presentation_ordinals`, source closure, measurement identities, or output `n/24` PTS.

13. Run both audio regressions without mask-specific audio behavior.
    Use synthetic `[8191,152191)` and canonical 24-bit `[0,144000)` with explicit chunk clocks and EOF.

14. Exercise active cancellation while Plan 6 owns an epoch and a stage.
    Record cleanup ownership, worker joins, the exact failure, and absence of a promoted receipt.

15. Retain negative controls and failed attempts.
    Mutate schema, mask axis, progress, inversion, plan identity, clocks, receipt bytes, and source bindings.

## Grafts from Candidate B

- Retain `destination_picture_window` as an explicit coordinate-system name in documentation and tests.
  Do not serialize a redundant coordinate enum while only one mode exists.

- Retain Candidate B's future rectangle and L-infinity feather formulas as a later-family design input.
  That family needs complete persisted types, interpolation, limits, and admission before selection.

- Retain Candidate B's coverage-plane accounting rule for future raster masks.
  A Q16 plane needs `u32` samples, a four-byte-per-pixel charge, and reservation before allocation.

- Retain Candidate B's explicit compressed-PNG, decoded-PNG, response, and decoder-temporary inventory.
  Candidate A can satisfy this through the existing conservative global PNG allowance.

## Rejected choices

- Reject Candidate B as the implementation base.
  Its caller fixture, persisted type chain, interpolation, visibility, admission, and producer proof are incomplete.

- Reject a Q16 coverage plane for Candidate A's analytic axis reveal.
  The scalar formula and effective bounds provide the same result without another cross-channel payload.

- Reject source-alpha reinterpretation, dense frame tables, public mask stages, and external mask assets in Plan 6.
  Each choice expands ownership or weakens the current opaque-input contract.

- Reject visibility based on raw mask coverage.
  Coverage, mask opacity, and layer opacity can all be positive while final Q16 weight is zero.

- Reject a vague H.264 “mask region” claim.
  The proof must bind exact regions and keep pure pixel truth separate from lossy decode measurements.

## Interface and red-flag assessment

Candidate A avoids the four architecture red flags. Its public module remains deep, and `evaluate_layer` owns real geometry and admission policy.

Candidate A also avoids temporal decomposition. It does not expose normalize, sample, rasterize, blend, or shutdown stages to callers.

Implementation must not duplicate picture-window or final-weight logic across `mask.rs`, `composition.rs`, `layers.rs`, and preflight. Duplication would reintroduce information leakage.

Candidate B keeps a deep public aggregate. Its internal `MaskWire`/`RectangleMask`/`PlannedMask` split leaks an unresolved representation boundary.

Candidate B's owned plane is not inherently invalid. Its current sampling and preflight seams are incomplete and invite duplicated geometry logic.

## Acceptance boundary

This judgment selects an implementation shape only. It does not accept runtime code or native output.

The bounded unit can establish exact authoring, planning, pixels, ownership, clocks, source binding, audio preservation, cancellation, and replay compatibility.

It cannot establish normal-speed playback, hearing, musical fit, transition motivation, full-film quality, or Panja acceptance.
