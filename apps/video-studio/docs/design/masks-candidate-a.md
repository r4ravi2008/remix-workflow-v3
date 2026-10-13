# Native picture masks — Candidate A

## Usage (caller view)

One commit creates two usable mask timelines through the current `Project` aggregate.
The first reveals one measured movie over another.
The second removes a moving PNG overlay while preserving transparent contain bars.

The only proposed caller field is `VideoClip.mask`.
All hashes below are complete values from the current preserved project head.

```json
{
  "intent": "commit-mask-axis-reveals-a01",
  "base_revision": "1bd422f2175ce5468fe4efc24593677897570c5c04cbe0767bbac5a3f6234572",
  "imports": [],
  "canonical_audio": {
    "asset": "cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8",
    "source_samples": { "start": 0, "length": 13104000 },
    "source_rate": 48000,
    "channel_order": ["left", "right"],
    "channel_order_basis": "Explicit stereo interpretation; labels are not measured"
  },
  "timelines": [
    {
      "id": "masked-movie-reveal",
      "frame_count": 72,
      "video_tracks": [
        {
          "id": "real-base",
          "clips": [{
            "id": "real",
            "timeline_frames": { "start": 0, "length": 72 },
            "asset": "a2247e96ab4335eb6b365ef52b6203e53377c6cf317ebb2e156789e6bd470b7f",
            "source_samples": { "start": 0, "length": 72 },
            "cadence": { "kind": "source_presentation_time" },
            "framing": {
              "fit": "cover",
              "crop": { "x": 0.0, "y": 0.0, "width": 1.0, "height": 1.0 }
            },
            "placement": {
              "destination": { "x": 0, "y": 0, "width": 2560, "height": 1440 },
              "opacity": 1.0
            }
          }]
        },
        {
          "id": "generated-reveal",
          "clips": [{
            "id": "generated",
            "timeline_frames": { "start": 0, "length": 72 },
            "asset": "c925cc9f66b64516e8b90549fbba80d3c4d01e00a637c083b13ba9c0cddcc76a",
            "source_samples": { "start": 0, "length": 72 },
            "cadence": { "kind": "source_presentation_time" },
            "framing": {
              "fit": "cover",
              "crop": { "x": 0.0, "y": 0.0, "width": 1.0, "height": 1.0 }
            },
            "placement": {
              "destination": { "x": 0, "y": 0, "width": 2560, "height": 1440 },
              "opacity": 1.0
            },
            "mask": {
              "kind": "axis_reveal",
              "axis": "horizontal",
              "progress": { "keys": [
                { "frame": 0, "value": 0.0, "to_next": "linear" },
                { "frame": 71, "value": 1.0 }
              ] },
              "inverted": false
            }
          }]
        }
      ],
      "audio_tracks": [{
        "id": "canonical-audio",
        "clips": [{
          "id": "master-prefix",
          "timeline_samples": { "start": 0, "length": 144000 },
          "asset": "cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8",
          "source_samples": { "start": 0, "length": 144000 },
          "source_rate": 48000,
          "gain": 1.0,
          "pan": 0.0
        }]
      }]
    },
    {
      "id": "masked-png-exit",
      "frame_count": 72,
      "video_tracks": [
        {
          "id": "generated-base",
          "clips": [{
            "id": "generated-base-clip",
            "timeline_frames": { "start": 0, "length": 72 },
            "asset": "c925cc9f66b64516e8b90549fbba80d3c4d01e00a637c083b13ba9c0cddcc76a",
            "source_samples": { "start": 0, "length": 72 },
            "cadence": { "kind": "source_presentation_time" },
            "framing": {
              "fit": "cover",
              "crop": { "x": 0.0, "y": 0.0, "width": 1.0, "height": 1.0 }
            },
            "placement": {
              "destination": { "x": 0, "y": 0, "width": 2560, "height": 1440 },
              "opacity": 1.0
            }
          }]
        },
        {
          "id": "png-exit",
          "clips": [{
            "id": "anchor",
            "timeline_frames": { "start": 8, "length": 56 },
            "asset": "a03eacfe29ac98847657121bd341fc1c02b32e6a51212d4c97885fd5fd38e175",
            "source_samples": { "start": 0, "length": 1 },
            "cadence": { "kind": "hold", "ordinal": 0 },
            "framing": {
              "fit": "contain",
              "crop": { "x": 0.0, "y": 0.0, "width": 1.0, "height": 1.0 }
            },
            "placement": {
              "destination": { "x": -100, "y": 270, "width": 1600, "height": 900 },
              "opacity": 0.75
            },
            "motion": {
              "x": { "keys": [
                { "frame": 0, "value": -100, "to_next": "linear" },
                { "frame": 55, "value": -50 }
              ] }
            },
            "mask": {
              "kind": "axis_reveal",
              "axis": "vertical",
              "progress": { "keys": [
                { "frame": 0, "value": 0.0, "to_next": "linear" },
                { "frame": 55, "value": 1.0 }
              ] },
              "inverted": true
            }
          }]
        }
      ],
      "audio_tracks": [{
        "id": "canonical-audio",
        "clips": [{
          "id": "master-prefix",
          "timeline_samples": { "start": 0, "length": 144000 },
          "asset": "cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8",
          "source_samples": { "start": 0, "length": 144000 },
          "source_rate": 48000,
          "gain": 1.0,
          "pan": 0.0
        }]
      }]
    }
  ]
}
```

Both cases use the unchanged direct public methods:

```rust
let command: CommitProject = serde_json::from_str(COMMIT_JSON)?;
let revision = project.commit(command)?;

for (timeline, intent) in [
    ("masked-movie-reveal", "export-masked-movie-reveal-a01"),
    ("masked-png-exit", "export-masked-png-exit-a01"),
] {
    let request = ExportRequest {
        intent: EntityId::parse(intent)?,
        revision: revision.revision.clone(),
        timeline: EntityId::parse(timeline)?,
        profile: MovieProfile::H264AacMp4 {
            video_bitrate: 12_000_000,
            audio_bitrate: 192_000,
        },
    };
    let prepared = project.prepare_export(request.clone())?;
    assert_eq!(prepared.plan.schema, 6);
    let _exported = project.export(request)?;
    let _verified = project.verify_export(EntityId::parse(intent)?)?;
}
```

`cancel_export` remains the concurrent cancellation call for an active export intent.
Callers do not coordinate readers, mask evaluation, workers, composition, or writer shutdown.

## Problem

The A14 runtime already owns opaque movie and PNG layers, motion, exact source clocks, and bounded composition.
A mask must add partial coverage without turning source alpha into a second meaning.
It must also preserve sparse tracks, transparent contain bars, signed placement, receipt identity, and worker ownership.

Candidate A starts with one analytic family: an animated horizontal or vertical axis reveal.
This family supports useful real-to-generated reveals and exits without adding a mask file decoder.
The plan stores a sparse progress curve, and execution derives Q16 coverage from the fitted picture window.
The mask is owned by one `VideoClip`, so it cannot drift into a track-wide or free canvas effect.

## Shape

### Authoring types

`VideoClip` receives one final optional field.
Absent fields retain current Snapshot 1 bytes.

```rust
pub struct VideoClip {
    // Existing fields remain in their existing order.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub mask: Option<PictureMask>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum PictureMask {
    AxisReveal {
        axis: MaskAxis,
        progress: PropertyCurve<MaskProgress>,
        inverted: bool,
    },
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MaskAxis {
    Horizontal,
    Vertical,
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
#[serde(try_from = "f64", into = "f64")]
pub struct MaskProgress(f64); // finite, 0.0..=1.0

impl MaskProgress {
    pub fn new(value: f64) -> Result<Self> { unimplemented!() }
    pub fn value(self) -> f64 { unimplemented!() }
}
```

The progress curve uses A14's current clip-local integer-frame grammar.
It must contain one to `clip_frames` keys and start at frame zero.
Frames increase strictly and remain inside the clip.
Every nonfinal key declares `step` or `linear`; the final key declares neither.
The final value holds through the clip's last frame.
One-key and constant masks are valid and still select the mask plan schema.

This reuses the public curve grammar without making `Opacity` mean mask position.
The private curve evaluator moves from `motion.rs` to `curve.rs` so motion and masks share one rule.
Crate-root reexports keep existing caller paths stable.

### Normalized plan types

```rust
pub struct VideoUse {
    // Existing fields remain in their existing order.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub mask: Option<PlannedPictureMask>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum PlannedPictureMask {
    AxisReveal {
        axis: MaskAxis,
        progress_q16: PlannedCurve<MaskProgressQ16>,
        inverted: bool,
    },
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(try_from = "u32", into = "u32")]
pub struct MaskProgressQ16(u32); // checked 0..=65536

impl MaskProgressQ16 {
    pub fn new(value: u32) -> Result<Self> { unimplemented!() }
    pub fn value(self) -> u32 { unimplemented!() }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct CoverageQ16(u32); // checked 0..=65536

impl CoverageQ16 {
    pub(crate) fn new(value: u32) -> Result<Self> { unimplemented!() }
    pub(crate) fn value(self) -> u32 { unimplemented!() }
}
```

Compilation quantizes every progress key once with `round(value * 65536)`.
It then normalizes constant keys to `PlannedCurve::Constant`.
Linear planned curves use the existing signed `i128` complete-value interpolation.
Nearest rounding uses half ties away from zero.
Step holds the left key until the next key frame.

Any authored mask selects `ExportPlan.schema == 6`.
Schema 6 may also contain existing picture motion.
Each use still has exactly one static placement or normalized motion program.
Its optional normalized mask must exactly match the authored clip mask.

When no mask exists, the current selector remains byte-for-byte unchanged:

- Plan 5 for declared motion.
- Plan 4 for static layers or explicit placement.
- Plan 3 for the remaining image path.
- Plan 2 for the remaining movie cut path.

`presentation_ordinals` remains the only picture source map.
A mask adds no ordinal, source clock, asset, or dense frame table.
The existing `source_closure` retains full imported, extracted, and generated lineage.
ArtifactReceipt stays schema 2 because its `plan_id` binds the schema-6 behavior.

### Resolved scalar observation

```rust
#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct ResolvedPictureMask {
    pub axis: MaskAxis,
    pub progress_q16: MaskProgressQ16,
    pub inverted: bool,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct PictureWindow {
    pub x: i64,
    pub y: i64,
    pub width: u32,
    pub height: u32,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct LayerObservation {
    pub placement: ResolvedPlacement,
    pub mask: Option<ResolvedPictureMask>,
    pub picture_window: Option<PictureWindow>,
    pub effective_bounds: Option<Bounds>,
}
```

`LayerFrame` carries this scalar observation beside the existing owned raster.
`check_decision` recomputes it from the plan, local frame, framing, and measured source extent.
The compositor rejects a correct source sample paired with the wrong mask frame or bounds.
The observation is ephemeral and does not enter a plan, receipt, or evidence trace.

### Coordinate and edge contract

The mask uses destination picture-window coordinates.
The picture window is the fitted retained-crop content intersected with the destination rectangle before canvas clipping.
It excludes contain bars.
It is absent when no integer output pixel center lies inside that source-bearing region.

The existing mapping produces its integer window with the current pixel-center rule:

```text
start = ceil(max(fitted_content_start, destination_start) - 0.5)
end   = ceil(min(fitted_content_end,   destination_end)   - 0.5)
```

Cover and stretch therefore use the destination's source-bearing pixel window.
Contain uses the smaller fitted-content window.
Crop changes the fitted content before this window is calculated.
Motion resolves the destination first, so the window travels and resizes with the clip.

Canvas clipping happens after the window is fixed.
A negative destination keeps the same off-canvas origin and does not renormalize visible progress.
Contain bars never become mask pixels and never obscure a lower track.

For an axis window of `D` pixels, let `j` be a pixel's integer offset from its unclipped window origin.
For progress `P` in Q16, non-inverted coverage is:

```text
base_coverage_q16 = clamp(P * D - j * 65536, 0, 65536)
coverage_q16 = inverted ? 65536 - base_coverage_q16 : base_coverage_q16
```

All products use checked `i128` arithmetic.
The formula is exact box coverage for a subpixel axis edge.
It creates at most one fractional column or row and needs no floating-point sampling.
Progress zero is empty; progress 65536 is full.
Inversion is applied before clip opacity.

There is no configurable feather in this unit.
The one-pixel box edge is the complete antialiasing rule.

### Opacity, alpha, and blend order

Coverage and clip opacity are separate Q16 values.
Their effective weight is rounded once:

```text
effective_q16 = (opacity_q16 * coverage_q16 + 32768) / 65536
output = (source * effective_q16
        + destination * (65536 - effective_q16)
        + 32768) / 65536
```

The first calculation uses `u64`; RGB blending uses checked integers.
Inversion happens before the first calculation.
Each RGB channel blends independently in current unmanaged coded sample values.
Raster and canvas alpha remain exactly 255.

The mask is not written into BGRA alpha and is not premultiplied color.
Opaque picture inputs remain mandatory.
No existing PNG alpha is reinterpreted as coverage.

### Fully masked frames, sparse tracks, and coverage

A track gap remains `Decision::Gap`.
An active but fully masked clip remains `Decision::Source` with its ordinal, PTS, observation, and no raster.
This distinction preserves source-clock checks and track ownership.

The visible union uses pixels whose final `effective_q16` is nonzero.
A fully masked frame is valid when another lower or upper track covers it.
It is rejected before decoding when the whole canvas has no contributing track.
The same rule covers zero opacity, offscreen motion, clipping, and sparse overlays.

`mask::effective_bounds` intersects the source-bearing mapping bounds with the monotonic reveal.
It uses a checked binary search for the first or last pixel whose effective weight is nonzero.
This includes a fractional boundary pixel only when opacity combination survives Q16 rounding.
The worker rasterizes exactly those bounds.

## Signatures and flow

```rust
pub(crate) fn normalize_mask_cancellable(
    author: &PictureMask,
    clip_frames: u64,
    check: impl FnMut() -> Result<()>,
) -> Result<PlannedPictureMask>;

pub(crate) fn resolve_mask(
    use_: &VideoUse,
    local_frame: u64,
) -> Result<Option<ResolvedPictureMask>>;

pub(crate) fn coverage_q16(
    mask: &ResolvedPictureMask,
    window: &PictureWindow,
    canvas_x: u32,
    canvas_y: u32,
) -> Result<CoverageQ16>;

pub(crate) fn effective_weight(
    opacity: OpacityQ16,
    coverage: CoverageQ16,
) -> Result<OpacityQ16>;

pub(crate) fn evaluate_layer(
    plan: &ExportPlan,
    use_: &VideoUse,
    local_frame: u64,
    source_width: u32,
    source_height: u32,
) -> Result<(Mapping, LayerObservation)>;

impl Mapping {
    pub(crate) fn rasterize_bounds_cancellable(
        &self,
        source: &Pixels,
        bounds: Option<&Bounds>,
        check: impl FnMut() -> Result<()>,
    ) -> Result<Option<Raster>>;
}

pub(crate) fn blend_layer_cancellable(
    canvas: &mut Pixels,
    raster: &Raster,
    observation: &LayerObservation,
    check: impl FnMut() -> Result<()>,
) -> Result<()>;
```

`evaluate_layer` is the single source of truth for runtime, preflight, and response validation.
It hides crop, fit, placement, motion, mask progress, inversion, clipping, and effective bounds.
The public surface remains the existing five `Project` operations.
`rasterize_bounds_cancellable` performs the current complete opaque-alpha check before returning `None` for empty bounds.

## Module map

| Module | Owns |
| --- | --- |
| `curve.rs` | Existing generic key validation, step/linear evaluation, and signed rational rounding |
| new `mask.rs` | Mask author types, Q16 normalization, resolution, coverage, inversion, and effective bounds |
| `model.rs` | Optional clip mask, Snapshot 1 boundary validation, and absent-field serialization |
| `plan.rs` | Schema-6 selection, normalized `VideoUse.mask`, source closure, and central tamper checks |
| `composition.rs` | Picture window, shared layer evaluation, bounded rasterization, blend, coverage, and admission |
| `layers.rs` | Existing track actors, scalar observations, ordered composition, barriers, and joins |
| `media.rs` / `image.rs` | Existing opaque source decoding; no mask decoder in this unit |
| `movie.rs` | Existing H.264/AAC writer and output clocks; route schema 6 through layers |
| `project.rs` / `exports.rs` | Existing intents, fencing, plan storage, cancellation, promotion, and product verification |
| Effect and provider adapters | Separate application orchestration; no native framework ownership |

The module screen has no new public execution stage.
The mask policy lives in one domain module instead of leaking into readers or callers.
`evaluate_layer` adds policy rather than forwarding arguments.
The organization follows ownership, not load-transform-save order.

The red-flag screen passes for four reasons:

- **Shallow module:** no new public execution methods expose internal mask stages.
- **Information leakage:** only `mask.rs` owns coverage and inversion arithmetic.
- **Temporal decomposition:** validation and runtime evaluation share domain functions instead of separate stage models.
- **Pass-through methods:** `evaluate_layer` performs normalization-dependent mapping and bounds policy before returning an observation.

## Bounded scope

This unit supports at most one axis-reveal mask per picture clip.
It supports horizontal or vertical orientation, inversion, and one sparse clip-local progress curve.

It defers configurable feather widths, rectangles, ellipses, paths, bitmap or movie masks, multiple-mask Boolean operations, tracking, rotation, and independent mask transforms.
It also defers alpha-bearing picture inputs, text, managed color, audio changes, and general transforms.
Those capabilities require explicit typed fields and later plan versions.

The implementation remains in-process Rust and AVFoundation.
It adds no FFmpeg, libav, renderer subprocess, GPU operation, or Resolve operation.

## Admission, ownership, barriers, and cancellation

Schema-6 preflight evaluates every active use at every output frame.
It uses the same `evaluate_layer` call as the worker.
The 100,000-frame and four-track limits bound the scan.

Each frame charge contains the existing application-owned payloads:

1. Every active movie source copy or held PNG cache.
2. Each effective masked BGRA raster held in a capacity-one response channel.
3. Three canvases across compositor-to-writer backpressure.
4. The existing conservative serialized PNG temporary allowance.

The analytic mask has no decoded bytes, coverage plane, cache, native object, or extra worker.
Its observation is fixed-size scalar metadata.
Future bitmap masks require a new plan version and explicit source, cache, raster, and decoder admission.

Source payload remains charged on fully masked frames.
The worker still decodes the selected sample, verifies PTS, copies opaque pixels, and then emits no raster.
Preflight charges the smaller effective raster bounds and the unchanged source schedule.
It rejects estimates above 512 MiB before source decode.

The admission value remains a conservative application-owned estimate.
It excludes `Vec` capacity, allocator state, PNG internals, Core Video, AVFoundation, encoder buffers, and process peak memory.

Track count and channel capacities do not change.
The compositor requests one frame from every nonempty track, receives bottom-to-top, consumes all rasters, and sends one canvas.
It does not request the next frame until the bounded output send succeeds.

Cancellation checks curve normalization, per-frame preflight, native sample pulls, raster rows, blend rows, budget waits, and channel polls.
The first failure preserves its cause.
Teardown closes request and response ports, cancels guarded native work, and joins every Rust worker.
Epoch ownership is rechecked before artifact promotion, so a cancelled or superseded attempt cannot publish a receipt.

AVFoundation assets, readers, outputs, sample buffers, and pixel buffers remain inside their current completion callbacks.
Only copied Rust pixels, rasters, permits, PTS values, ordinals, and scalar observations cross channels.

## Schema compatibility and tamper checks

Snapshot schema remains 1, and ArtifactReceipt remains 2.
Optional mask fields serialize last and disappear when absent.
The implementation must preserve these exact files before any mask proof:

| Document | Bytes | SHA-256 |
| --- | ---: | --- |
| Snapshot 1 motion | 410865 | `1947fcb6939dbec40f13ae23b87a156f5d6e1758fa18e058aaa1f810abc313d3` |
| Plan 2 | 369279 | `97fdd9f63d48ee3b600ee37a845c302e79815bd1870b20dae376f9c4a957e025` |
| Plan 3 | 4983 | `4e5a89b00e7b5fabaafb4bf1335c1a5c3538c593765b4f5e5c818ff6bcede219` |
| Plan 4 | 413967 | `5cf0320f82bfc19839c5a06ffec15449fcdb80b97be15e2b4fb4105517ef0687` |
| Plan 5 | 415912 | `8ca51e03d048971a86cb598990fabd2f93f839c98b1b6c5fda3eb7aa90c3ee06` |
| Receipt 2 | 1418 | `44c0c27ad1a58f22746011673d8e4d4a211c5b5cdeffcb18172d6cc73fc73be2` |

The preservation manifest remains `cf3ccb32ea68a58532a312c921024107fcc3773b9f2cc68dd7ddab5ba0b6695f`.
Focused roundtrip tests compare bytes, not reconstructed semantic values.

Central plan validation rebuilds Snapshot 1 from the plan timeline and source closure.
It reruns author validation, mask normalization, motion normalization, source lineage, audio binding, and timeline checks.
It then compares every ordered clip/use pair, normalized mask, placement or motion, range, framing, and `presentation_ordinals` entry.
Movie ordinals are checked against measured sample PTS; held PNGs remain ordinal zero without a movie clock.

Schema 6 requires at least one authored mask.
Schemas 2 through 5 reject mask fields.
Schema 6 rejects a missing, added, reordered, or changed normalized mask.
Axis, progress key, interpolation, inversion, effective type bounds, and Q16 values are all hash-bound and rechecked.

No mask trace is added to `PictureExecutionEvidence` or the receipt.
The existing `plan_id` remains the persisted execution binding.

## Verification contract

### Independent pure vectors

The golden vector for a four-pixel horizontal window is fixed before implementation:

| Progress Q16 | Coverage Q16, left to right |
| ---: | --- |
| 0 | `[0, 0, 0, 0]` |
| 8192 | `[32768, 0, 0, 0]` |
| 24576 | `[65536, 32768, 0, 0]` |
| 32768 | `[65536, 65536, 0, 0]` |
| 65536 | `[65536, 65536, 65536, 65536]` |

Inversion must equal `65536 - coverage` for every entry.
A window at `x = -1`, width four, progress 24576 exposes visible canvas coverage `[32768, 0, 0]`.
This proves canvas clipping does not renormalize the mask.

Additional vectors cover vertical axes, one-pixel windows, step and linear progress, final holds, and Q16 key ties.
They cover `opacity=32768, coverage=32768 -> effective=16384`.
They also cover `opacity=1` with coverage 32767 and 32768, which produce effective weights zero and one.

Separate scalar code must reproduce picture windows for contain, cover, stretch, normalized crop, motion, and signed placement.
Pure pre-encode BGRA must match every independent expected byte exactly.
Tests include transparent contain bars, full and empty masks, zero opacity, overlap order, sparse gaps, and covered or uncovered fully masked frames.

### Actual native proof

The proof starts from the accepted A14 source set and records every expected hash before execution.
It uses four tracks, two simultaneous movie readers, and both opaque PNG sources for 72 frames at 320 by 180.
It adds horizontal and vertical masks, inversion, constant and linear progress, motion, signed clipping, contain bars, sparse intervals, and fully masked overlay frames.

The predecessor bindings are mandatory:

- A14 producer `d8ae6b396206a2dc684183dbebb20fb410f6ecd48a84f0e26882ec5ea4be16e3`.
- A14 build manifest `054c25b639a27a0de5e6ce5f5f3f56c3b59943682b33b7fe547e1614628a00e2`.
- A14 verifier A02 `8c323c743aed8c185f5720afb64b433999e2db365a7c1897bddcb7bdbddcf41a` and report `40f650818cea1e7687a2cdd174fef02ede95add80bbb62fccda9ba72a868c562`.
- A14 verifier A03 `1b28e53a695b06d44efbd2a6d9c22d9918a4abe8b3080c0bf199a9e34bd17d36` and report `6225fbd6200d0249583203e51fa4489ce2361eaac84bebc756b93c7733b91179`.
- Explicit-epoch observer `1885e2ba4df470d806b51fed8a8e5238464f71ff70641e28a6ea3eecd4318b20`.
- Completed negative controls `956180e83fe5b1ee0f865ecbd34dba9ca1c56823aee5d90dfaf1f07f26478d0f`.
- Synthetic receipt/output `505847160c4b16355af75199cc3775a7064219359086f543a062929819c053d7` / `097dd9a1a59c02a8967db82463e8b43fc6ffc42a5294c997a77280967b1174df`.
- Canonical receipt/output `69b692a1cd7940a5a93f8f4112efefaf70d85871044b5f0a432cd63bcb9b5b28` / `c4a94f3981bcb6a222aebca2d214b3c1f18972251ddddbfe460dac98b17928c3`.

The new producer and manifest are frozen and hashed before the first mask export.
The new verifier independently binds the exact revision, plan, source-closure keyset, every source byte count, descriptor, measurement schema, producer identity, output, receipt document, receipt CAS bytes, and fresh product reverify result.

The required source bytes are fixed:

| Role | Bytes | SHA-256 |
| --- | ---: | --- |
| generated movie | 2543644 | `c925cc9f66b64516e8b90549fbba80d3c4d01e00a637c083b13ba9c0cddcc76a` |
| real movie | 11620016 | `a2247e96ab4335eb6b365ef52b6203e53377c6cf317ebb2e156789e6bd470b7f` |
| extracted still | 929656 | `0e38532679abfb53386659762888dba87dcad8ff7d3377f0ffe9eccb355fe8d3` |
| generated anchor | 1648175 | `a03eacfe29ac98847657121bd341fc1c02b32e6a51212d4c97885fd5fd38e175` |
| synthetic PCM | 2496044 | `5da985961720761f773e0aae2e72ba056abe2f83b11ed5c7eecd653b3d7269ff` |
| canonical 24-bit PCM | 78624044 | `cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8` |

Separate Python code resolves every motion pose, picture window, mask coverage, effective weight, source selection, and bottom-to-top blend.
Every pre-encode frame must match its pure reference exactly.
Every decoded H.264 full frame and nonempty mask, placement, contain-bar, and overlap region must meet the predeclared 34 dB PSNR threshold.

Every selected movie ordinal and measured source PTS is checked with an explicit epoch field.
Every output PTS must contain epoch zero and equal `n/24` through frame 71, followed by video EOF.
PNG ordinals remain zero and carry no invented PTS.

The synthetic audio comparison uses exact WAV interval `[8191,152191)`.
The canonical comparison uses exact 24-bit interval `[0,144000)` from the 78,624,044-byte master.
Each output must decode 144,000 stereo frames in 18 positive contiguous chunks and reach audio EOF.
Every chunk must record epoch zero explicitly; a missing epoch is failure, not zero.

Fresh PCM captures are each hashed and compared to the selected WAV interval under a predeclared channel-cosine threshold of 0.999.
AAC f32 captures are not required to equal each other byte-for-byte.
Observed variation is retained and reported.
Any overwritten or missing capture is marked unverifiable rather than assigned a quality result.

Deliberately corrupt controls change the mask axis, inversion, progress Q16, plan schema, source hash, measurement producer, receipt bytes, epoch presence, epoch value, PTS continuity, EOF flag, and selected PCM interval.
Every relevant helper must reject its control.
Unsuccessful native attempts and partial files remain preserved with their failure state.

An active schema-6 cancellation must record the owning epoch and observed stage bytes.
It must return the exact cancellation cause, join all workers, remove or retain the stage according to recorded ownership, and create no receipt.
Reconciliation evidence must distinguish its own cleanup from RAII cleanup.

Historical product readback reopens schemas 2, 3, 4, and 5 without rewriting them.
Technical proof does not establish watching, hearing, musical fit, story quality, or full Panja hybrid acceptance.

## Candidate decision

Candidate A recommends a destination picture-window axis reveal with sparse Q16 progress curves.
It is useful for the immediate real/generated handoff and preserves the deep `Project` interface.
The analytic family avoids new media kinds, mask clocks, decoder callbacks, cache ownership, and source-lineage branches.

## Tradeoffs accepted

- We accept one horizontal or vertical family in exchange for an exact and bounded first mask unit.
- We accept one-pixel box antialiasing in exchange for deterministic endpoints without a feather parameter.
- We accept destination picture-window coordinates in exchange for masks that follow crop, fit, placement, and motion automatically.
- We accept decoding fully masked sources in exchange for unchanged ordinal, PTS, alpha, and worker evidence.
- We accept per-frame schema-6 preflight in exchange for exact dynamic coverage and raster admission.

## Alternatives considered

**Grayscale PNG or movie masks.** Arbitrary artwork is deeper long-term capability, but the first unit would add media kinds, probes, lineage, mask clocks, caches, decoder memory, and another native ownership path.

**Canvas-space geometry.** This keeps the edge independent from each clip, but callers must coordinate canvas coordinates with crop, placement, and motion. That leaks compositor rules through the public model.

**Source-normalized geometry.** This follows coded pixels, but it makes visible reveal behavior depend on crop and cover regions outside the destination. Picture-window coordinates match the pixels the compositor can actually show.

**Store coverage in raster alpha or a Q16 plane.** Alpha storage weakens the opaque BGRA invariant, while a coverage plane adds two or four bytes per pixel and another admitted handoff. An analytic scalar computes the same result without either payload.

**Dense frame tables.** They simplify workers but enlarge plans and duplicate an execution trace. Sparse normalized curves keep the plan hash reviewable.

## Open questions and risks

- Does the first film transition need a wider feather before this bounded axis family is useful?
- Can independent code reproduce the existing fitted-window rounding at every contain and cover boundary?
- Will per-frame schema-6 window evaluation remain acceptable near the 100,000-frame limit?
- Can binary-searched effective bounds be proven identical to per-pixel effective-weight tests at Q16 thresholds?
- Does the 512 MiB logical policy leave enough headroom after measured native and allocator peaks are observed?
- What maximum cancellation latency will AVFoundation show during a stalled native call?

## Next implementation step

Implement `mask.rs` pure normalization, coverage, effective-weight, window, and bounds vectors before adding schema 6 or changing worker execution.
