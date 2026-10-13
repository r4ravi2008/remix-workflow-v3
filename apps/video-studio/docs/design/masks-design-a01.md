# Native picture masks selected design A01

Status: selected for implementation. Native mask output remains unverified.

## Caller use

The caller adds one optional domain field to an existing picture clip:

```json
"mask": {
  "kind": "axis_reveal",
  "axis": "horizontal",
  "progress": {"keys": [
    {"frame": 0, "value": 0.0, "to_next": "linear"},
    {"frame": 71, "value": 1.0}
  ]},
  "inverted": false
}
```

The caller uses the existing `Project::commit`, `prepare_export`, `export`,
`cancel_export` and `verify_export` operations. Candidate A contains two complete,
validated caller documents: a movie reveal and a moving PNG exit.
Native proof creates separate diagnostic projects. It does not commit those examples
to the Panja film head. The canonical master keeps its complete binding while the
diagnostic audio clip selects its prefix.

## Domain and persisted shapes

Append `VideoClip.mask: Option<PictureMask>` and `VideoUse.mask:
Option<PlannedPictureMask>` after their current fields. Both use serde default and
skip absent values. Existing Snapshot 1 and Plan 2/3/4/5 bytes remain unchanged.

```rust
pub enum PictureMask {
    AxisReveal {
        axis: MaskAxis,
        progress: PropertyCurve<MaskProgress>,
        inverted: bool,
    },
}
pub enum MaskAxis { Horizontal, Vertical }
pub struct MaskProgress(f64); // finite 0..=1; checked serde conversion
pub struct MaskProgressQ16(u32); // checked 0..=65536
pub enum PlannedPictureMask {
    AxisReveal {
        axis: MaskAxis,
        progress_q16: PlannedCurve<MaskProgressQ16>,
        inverted: bool,
    },
}
pub(crate) struct CoverageQ16(u32); // checked 0..=65536
pub(crate) struct ResolvedPictureMask {
    axis: MaskAxis,
    progress_q16: MaskProgressQ16,
    inverted: bool,
}
pub(crate) struct PictureWindow {
    x: i64, y: i64, width: u32, height: u32,
}
pub(crate) struct LayerObservation {
    placement: ResolvedPlacement,
    mask: Option<ResolvedPictureMask>,
    picture_window: Option<PictureWindow>,
    effective_bounds: Option<Bounds>,
}
```

Enums use tagged snake-case serialization and reject unknown fields.
The source closure contains no new mask asset in this unit.
Receipt schema remains 2. Its plan identity binds mask behavior.

## Curves and schema selection

Move the existing generic curve grammar and integer evaluator into private `curve.rs`.
Preserve crate-root type reexports and exact serialized representations.
Motion and masks share key validation and complete-value signed rational interpolation.

Each curve starts at local frame zero. Keys increase within the clip.
Only nonfinal keys declare step or linear interpolation. The final key holds.
One-key, one-frame and constant programs are valid.
Quantize each authored progress once using nearest-away rounding of `f64 * 65536`.
Normalize constant keys to a constant program. Do not create dense frame tables.

Any authored mask selects Plan 6, including a constant or visually unchanged mask.
Every Plan 6 use has exactly one normalized motion or static placement.
An unmasked use in that plan still receives the existing placement normalization.
Without masks, preserve the current Plan 2/3/4/5 selector and execution routes.

Central validation rebuilds the Snapshot and recompiles each mask.
Compare axis, inversion, complete normalized progress, order, placement/motion,
framing, ranges, source ordinals, source PTS, lineage and audio uses.
Plan 6 requires at least one authored mask. Schemas 2..5 reject masks.

## Coordinates and pixels

The coordinate name is `destination_picture_window` in documentation and tests.
There is one coordinate mode, so no redundant coordinate enum is stored.

Derive the window once from the existing Mapping floating-point geometry.
Intersect fitted retained-crop content with the destination before canvas clipping.
For its half-open continuous interval `[lo, hi)`, integer pixel centers yield:

```text
start = ceil(lo - 0.5)
end = ceil(hi - 0.5)
width = end - start
```

Keep the signed unclipped origin. Empty windows are absent.
Canvas clipping changes visible bounds, never the origin used for mask progress.
Contain bars reveal the lower-track canvas. They stay black where no earlier layer contributes.
Crop and fit affect the window. Placement and motion resolve before the window.

For axis window length D, progress P and offset j from the unclipped origin:

```text
base = clamp(P * D - j * 65536, 0, 65536)
coverage = inverted ? 65536 - base : base
effective = (opacity_q16 * coverage + 32768) / 65536
rgb = (source * effective + canvas * (65536 - effective) + 32768) / 65536
```

Use checked i128 for coordinates and u64 for the opacity product.
The reveal has exact box coverage and at most one fractional row or column.
Progress zero is empty; progress 65536 is full before inversion.
There is no configurable feather or mask opacity in Plan 6.

RGB blends in current unmanaged coded sample values. All BGRA alpha remains 255.
Coverage never becomes source alpha or a premultiplied color payload.
Opaque PNG and movie input checks remain mandatory, including fully hidden frames.

## One execution authority

```rust
fn normalize_mask_cancellable(author: &PictureMask, clip_frames: u64, check: impl FnMut() -> Result<()>) -> Result<PlannedPictureMask>;
fn resolve_mask(use_: &VideoUse, local_frame: u64) -> Result<Option<ResolvedPictureMask>>;
fn coverage_q16(mask: &ResolvedPictureMask, window: &PictureWindow, x: u32, y: u32) -> Result<CoverageQ16>;
fn effective_weight(opacity: OpacityQ16, coverage: CoverageQ16) -> Result<OpacityQ16>;
fn evaluate_layer(plan: &ExportPlan, use_: &VideoUse, local_frame: u64, source_width: u32, source_height: u32) -> Result<(Mapping, LayerObservation)>;
fn rasterize_bounds_cancellable(mapping: &Mapping, source: &Pixels, bounds: Option<&Bounds>, check: impl FnMut() -> Result<()>) -> Result<Option<Raster>>;
fn blend_layer_cancellable(canvas: &mut Pixels, raster: &Raster, observation: &LayerObservation, check: impl FnMut() -> Result<()>) -> Result<()>;
```

These functions remain crate-private. `evaluate_layer` owns geometry and visibility.
Workers, preflight and scalar response checks use that evaluator.
Independent proof code implements the written contract separately.

Effective bounds use monotone binary search over final effective weight greater than zero.
Test the search against exhaustive pixels for both orientations and inversion states.
Include opacity one with coverage 32767 and 32768, producing weights zero and one.

## Source execution and ownership

A gap remains Gap. An active fully hidden clip remains Source with its actual
ordinal, PTS and scalar observation, and no raster.
The worker still decodes, copies and checks the source before emitting that response.
Rasterization checks complete opaque input before returning an empty result.

Add a direct native worker test using a small preserved H.264 fixture.
The direct worker test returns Source with the actual held ordinal/PTS and no raster.
Pure composition tests separately prove that an absent raster leaves lower pixels unchanged.
The forthcoming four-track native proof verifies hidden regions against the composed lower layers.
Inject a wrong measured PTS for the held movie in the private test plan.
The same hidden execution must fail at the reader's source-PTS comparison.
This test guards against an optimization that skips hidden source execution.
No test-only execution API becomes public.

Retain four nonempty track workers and capacity-one picture channels.
Native objects remain callback-confined. Only copied Rust payloads and scalars cross channels.
The compositor consumes all current rasters and sends its canvas before requesting another frame.

Mask evaluation allocates no plane, cache or per-frame table.
Preflight charges active sources, effective rasters, three canvases and the existing
serialized PNG temporary allowance. Fully hidden sources remain charged.
The 512 MiB limit covers logical application-owned payload. It excludes process and native peak memory.

Retain existing cooperative cancellation and stage ownership.
Check normalization, preflight, source pulls, rows, channel waits, verification and promotion.
Close channels and join workers on failure. A retired epoch cannot promote a receipt.

## Module ownership

| Module | Knowledge |
| --- | --- |
| curve.rs | Shared grammar, sparse normalization and exact interpolation |
| mask.rs | Progress, inversion, box coverage and monotone effective bounds |
| composition.rs | One Mapping geometry, picture window, layer evaluation, raster, blend and admission |
| model.rs / plan.rs | Authored mask, schema 6, normalization and central validation |
| layers.rs | Worker schedule, source execution, scalar observations and ordered composition |
| movie.rs / exports.rs / project.rs | Existing native writer, clocks, intents, epochs, receipts and reverify |

## Compatibility and proof

Preserve all eight files listed in masks-judgment-a01.md byte for byte.
Add motion Snapshot 1 and Plan 5 to the existing six-document roundtrip test.
Fresh product readback must reopen historical schemas 2, 3, 4 and 5.
Historical metadata and receipt bytes remain unchanged.

Pure vectors cover curve grammar, quantization ties, signed clipping, full/empty
coverage, inversion, final-weight zero, all fits/crops, moving windows, bars,
sparse gaps, overlap order, opaque input checks and exact pre-encode BGRA.
Mask evaluation and visibility tests allocate no pixel plane.

The actual proof uses the A14 four-track 72-frame source corpus at 320 by 180.
Keep two simultaneous movie readers and both PNGs. Include constant, step and linear masks,
both axes, inversion, motion, signed clipping, sparse intervals and fully hidden overlays.
Use fresh synthetic and canonical diagnostic projects and export intents.
Freeze the new mask-capable producer and build manifest before export.

Bind exact sources, complete closure/measurements, selected ordinals/PTS, revision,
Plan 6, output bytes, immutable receipt, receipt CAS and complete product reverify.
Reopen every output frame with a separate observer. Require exact n/24 PTS, explicit epoch zero and EOF.
Compare fresh PCM with actual synthetic interval [8191,152191) and canonical24 prefix [0,144000).
Require 144000 frames, positive continuous chunks, explicit epochs and audio EOF.
Each retained capture must meet channel cosine 0.999. Preserve observed f32 variation.

Define exact ROI coordinates before export in masks-native-proof-policy-a01.json and its generated ROI manifest.
Full frames, reveal interiors, fractional strips, hidden regions, bars, overlaps and signed-clipping regions are separate checks.
Twelve independent8x8 pure frames prove exact pre-encode BGRA and edge arithmetic.
The72-frame native artifact uses independently constructed reference frames and decoded full-frame/ROI PSNR.
There is no actual raw compositor-buffer dump or72-frame byte-equality claim.
Each nonempty ROI requires sample count, finite MSE and 34 dB PSNR or exact identity.
Empty regions are recorded as empty rather than passed without samples.

Run deliberate source, receipt, mask and clock tampering against actual independent helpers.
Reject boolean clock fields, missing epochs, nonzero epochs, discontinuity and false EOF.
Retain failures and lost bytes honestly. Exercise an active Plan 6 cancel and distinguish cleanup actors.

Technical acceptance does not establish watching, hearing, musical fit or full-film acceptance.

## Synthesis decision

Parent scored A 24/25 and B 16/25. The judge scored A 23/25 and B 12/25.
Both selected A for its complete domain shape and smaller owned execution surface.
Both candidate drafts remain unchanged. Each candidate reported no sibling read before delivery.
Cross-family review was unavailable.

Grafts from B: name the coordinate system explicitly; keep a complete PNG payload inventory;
retain rectangle/feather formulas and four-byte Q16 plane accounting as future-family inputs.
The selected implementation uses the existing global PNG allowance and no mask plane.

Reject B's undefined persisted type, invalid synthetic hash, incomplete interpolation,
raw-coverage visibility and unreserved preflight plane. Reject dense mask tables and source-alpha reinterpretation.
Rectangles, wider feather, paths, bitmap/movie masks, tracking and Boolean combinations remain future units.

For the new producer, clarify the current backend label as objc2 AVFoundation bindings 0.3.2.
The current Cargo.lock has objc2 base crate 0.6.4 and framework bindings 0.3.2.
Keep historical backend strings untouched; binary and lock hashes remain the provenance authority.

Implementation starts with shared curve extraction, pure mask contracts and exact fixtures.
Repeated architectural workarounds return this unit to design.
