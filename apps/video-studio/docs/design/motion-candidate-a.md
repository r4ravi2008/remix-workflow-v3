# Native picture motion — Candidate A

## Caller usage

This is the current `Project::commit` shape with one proposed optional `motion` member on `VideoClip`.
The base revision and asset hashes are complete values from the preserved native project.
The two video tracks are ordered bottom-to-top.

```json
{
  "intent": "commit-motion-curves-a01",
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
      "id": "motion-curves-a01",
      "frame_count": 48,
      "video_tracks": [
        {
          "id": "base-movie",
          "clips": [
            {
              "id": "base",
              "timeline_frames": { "start": 0, "length": 48 },
              "asset": "a2247e96ab4335eb6b365ef52b6203e53377c6cf317ebb2e156789e6bd470b7f",
              "source_samples": { "start": 0, "length": 48 },
              "cadence": { "kind": "source_presentation_time" },
              "framing": {
                "fit": "cover",
                "crop": { "x": 0.0, "y": 0.0, "width": 1.0, "height": 1.0 }
              },
              "placement": {
                "destination": { "x": 0, "y": 0, "width": 2560, "height": 1440 },
                "opacity": 1.0
              }
            }
          ]
        },
        {
          "id": "png-overlay",
          "clips": [
            {
              "id": "moving-anchor",
              "timeline_frames": { "start": 8, "length": 32 },
              "asset": "a03eacfe29ac98847657121bd341fc1c02b32e6a51212d4c97885fd5fd38e175",
              "source_samples": { "start": 0, "length": 1 },
              "cadence": { "kind": "hold", "ordinal": 0 },
              "framing": {
                "fit": "contain",
                "crop": { "x": 0.0, "y": 0.0, "width": 1.0, "height": 1.0 }
              },
              "placement": {
                "destination": { "x": 160, "y": 90, "width": 1600, "height": 900 },
                "opacity": 1.0
              },
              "motion": {
                "x": {
                  "keys": [
                    { "frame": 0, "value": 160, "to_next": "linear" },
                    { "frame": 15, "value": 210, "to_next": "linear" },
                    { "frame": 31, "value": 160 }
                  ]
                },
                "y": {
                  "keys": [
                    { "frame": 0, "value": 90, "to_next": "step" },
                    { "frame": 16, "value": 120, "to_next": "step" },
                    { "frame": 31, "value": 120 }
                  ]
                },
                "width": {
                  "keys": [
                    { "frame": 0, "value": 1600, "to_next": "linear" },
                    { "frame": 31, "value": 1400 }
                  ]
                },
                "height": {
                  "keys": [
                    { "frame": 0, "value": 900, "to_next": "linear" },
                    { "frame": 31, "value": 788 }
                  ]
                },
                "opacity": {
                  "keys": [
                    { "frame": 0, "value": 0.0, "to_next": "linear" },
                    { "frame": 7, "value": 1.0, "to_next": "step" },
                    { "frame": 23, "value": 1.0, "to_next": "linear" },
                    { "frame": 31, "value": 0.0 }
                  ]
                }
              }
            }
          ]
        }
      ],
      "audio_tracks": [
        {
          "id": "canonical-audio",
          "clips": [
            {
              "id": "master-prefix",
              "timeline_samples": { "start": 0, "length": 96000 },
              "asset": "cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8",
              "source_samples": { "start": 0, "length": 96000 },
              "source_rate": 48000,
              "gain": 1.0,
              "pan": 0.0
            }
          ]
        }
      ]
    }
  ]
}
```

The caller then uses the existing operations only:

```rust
let revision = project.commit(command)?;
let request = ExportRequest {
    intent: EntityId::parse("export-motion-curves-a01")?,
    revision: revision.revision.clone(),
    timeline: EntityId::parse("motion-curves-a01")?,
    profile: MovieProfile::H264AacMp4 {
        video_bitrate: 12_000_000,
        audio_bitrate: 192_000,
    },
};
let prepared = project.prepare_export(request.clone())?;
let result = project.export(request)?;
project.verify_export(EntityId::parse("export-motion-curves-a01")?)?;
```

`commit`, `prepare_export`, `export`, `cancel_export`, and `verify_export` remain the public aggregate boundary.
An owner may call `cancel_export` with the active export intent while `export` is running.
No caller opens a reader, worker, compositor, pixel buffer, or writer.

## Problem

A13 supplies static opaque movie and PNG layers through bounded track workers.
This unit must animate destination geometry and opacity without changing source selection or audio.
The behavior must remain exact after plan persistence, replay, cancellation, and native callback execution.

Candidate A gives each picture property its own typed curve.
Independent curves let a fade, vertical step, resize, and 50-pixel move use different key frames.
The compiler replaces all authoring defaults and floating opacity values with an immutable execution program.

## Domain types

`VideoClip` receives one optional final field.
It is absent from every historical snapshot.

```rust
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VideoClip {
    pub id: EntityId,
    pub timeline_frames: Span,
    pub asset: ContentHash,
    pub source_samples: Span,
    pub cadence: Cadence,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub framing: Option<Framing>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub placement: Option<PicturePlacement>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub motion: Option<PictureMotion>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PictureMotion {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub x: Option<PropertyCurve<i32>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub y: Option<PropertyCurve<i32>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub width: Option<PropertyCurve<u32>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub height: Option<PropertyCurve<u32>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub opacity: Option<PropertyCurve<Opacity>>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PropertyCurve<T> {
    pub keys: Vec<CurveKey<T>>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CurveKey<T> {
    pub frame: u64,
    pub value: T,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub to_next: Option<CurveInterpolation>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CurveInterpolation {
    Step,
    Linear,
}
```

The generic curve is an internal Rust helper.
The five typed fields prevent assigning opacity values to geometry or signed values to extents.

### Clock and endpoint rules

For a clip starting at output frame `S`, local frame `f` is `output_frame - S`.
A clip with length `L` owns local frames `0..L`; its final displayed frame is `L - 1`.
Curves never use source PTS, nominal frame rate, or audio samples.

Every present curve has at least two keys.
Its first key is frame zero, and its last key is frame `L - 1`.
Key frames are strictly increasing and less than `L`.
Every nonfinal key has `to_next`; the final key omits it.
There is no extrapolation or implicit hold outside those endpoints.

`Step` returns the left value on `[left.frame, right.frame)`.
The right key becomes effective exactly at `right.frame`.
`Linear` returns each stored endpoint exactly.

A missing property inherits the clip's static `placement` value.
An absent placement first becomes the existing full-canvas, opacity-one default.
An empty `PictureMotion`, a one-frame motion clip, or a motion that resolves to one pose is invalid.
This rule ensures that only actual animation selects the new plan schema.

### Exact interpolation

Geometry interpolation uses `i128` intermediates.
For endpoints `(fa, a)` and `(fb, b)`, frame `f` evaluates this exact rational:

```text
N = a * (fb - fa) + (b - a) * (f - fa)
D = fb - fa
value = round_nearest_ties_away_from_zero(N / D)
```

The rounding function operates on the complete signed rational.
Therefore `-1/2` becomes `-1`, and `1/2` becomes `1`.
The result must fit its property type.
Every evaluated width and height must be positive and pass the existing 128 MiB pixel-extent limit.
Signed `x` and `y` may place all or part of a rectangle off canvas.

Author opacity keys remain finite decimals in `[0,1]`.
Compilation first maps every key to `round(value * 65536)` in `0..=65536`.
Linear opacity then interpolates those integers with the same rational rounding rule.
Execution never interpolates a float.
Blend stays `(src*w + dst*(65536-w) + 32768) >> 16`, with output alpha 255.

## Immutable plan

Animation selects `ExportPlan.schema == 5`.
Static inputs continue selecting schemas 2, 3, or 4 under the current rules.
Schema 5 still uses `VideoUse.presentation_ordinals`; it adds no `source_ordinals` field.

```rust
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VideoUse {
    pub clip: EntityId,
    pub track: EntityId,
    pub timeline_frames: Span,
    pub asset: ContentHash,
    pub allowed_source_samples: Span,
    pub presentation_ordinals: Vec<u64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub framing: Option<Framing>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub placement: Option<PicturePlacement>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub motion: Option<PlannedPictureMotion>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PlannedPictureMotion {
    pub x: PlannedCurve<i32>,
    pub y: PlannedCurve<i32>,
    pub width: PlannedCurve<u32>,
    pub height: PlannedCurve<u32>,
    pub opacity_q16: PlannedCurve<OpacityQ16>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum PlannedCurve<T> {
    Constant { value: T },
    Keyed { keys: Vec<PlannedKey<T>> },
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PlannedKey<T> {
    pub frame: u64,
    pub value: T,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub to_next: Option<CurveInterpolation>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(transparent)]
pub struct OpacityQ16(u32);
```

For an animated use, compilation resolves all five properties.
Missing author curves become `Constant` values from normalized static placement.
Semantically constant author curves also become `Constant`.
Opacity keys become Q16 values before the plan is hashed.

An animated schema-5 use has `motion: Some` and `placement: None`.
A static schema-5 use has normalized `placement: Some` and `motion: None`.
Exactly one is present for every schema-5 picture use.
Schemas 2 and 3 have neither; schema 4 has placement only.

The existing `ExportPlan.timeline` retains the authored clip.
`VideoUse.motion` is the normalized execution form, not a per-frame trace.
Its duplication detects changed defaults or opacity quantization during replay validation.
No plan or receipt gains another timeline, evaluated-frame list, or source trace.

`plan::validate_picture_mapping` recompiles each authored motion and compares it with `VideoUse.motion`.
It also retains all current one-to-one clip, track, range, ordinal, cadence, and source-PTS checks.
The stored sample table remains the PTS authority, including the AV1 source's `512/12288` sample steps.
The existing `source_closure` retains each asset's complete `Origin` lineage.
Motion never rewrites generated-attempt or transfer-receipt recovery data.

## Pure signatures

```rust
pub(crate) fn normalize_motion(
    author: &PictureMotion,
    base: &PicturePlacement,
    clip_frames: u64,
) -> Result<PlannedPictureMotion>;

impl PlannedPictureMotion {
    pub(crate) fn evaluate(&self, local_frame: u64) -> Result<ResolvedPlacement>;
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct ResolvedPlacement {
    pub destination: PixelRect,
    pub opacity_q16: OpacityQ16,
}

pub(crate) fn round_ratio_nearest_away(numerator: i128, denominator: u64)
    -> Result<i128>;

impl Mapping {
    pub(crate) fn new_resolved(
        source_width: u32,
        source_height: u32,
        framing: Option<&Framing>,
        placement: &ResolvedPlacement,
        canvas_width: u32,
        canvas_height: u32,
    ) -> Result<Self>;

    pub(crate) fn rasterize_cancellable(
        &self,
        source: &Pixels,
        check: impl FnMut() -> Result<()>,
    ) -> Result<Option<Raster>>;
}

pub(crate) fn preflight(
    plan: &ExportPlan,
    check: impl FnMut() -> Result<()>,
) -> Result<Admission>;
```

`ResolvedPlacement` is ephemeral Rust data.
It is not persisted as an execution log.

## Ownership and execution

| Module | Ownership |
| --- | --- |
| `model.rs` | Author curves, snapshot-1 validation, and absent-field serialization |
| new private `motion.rs` | Curve normalization, Q16 conversion, signed rational rounding, and frame evaluation |
| `plan.rs` | Schema-5 selection, complete normalized motion, and replay validation |
| `composition.rs` | Resolved mapping, transparent contain bars, Q16 blend, coverage, and admission |
| `layers.rs` | Bounded track workers, per-frame evaluation, raster handoff, and ordered composition |
| `media.rs` / `movie.rs` | Callback-scoped AVFoundation readers and the existing H.264/AAC writer clocks |
| `project.rs` / `exports.rs` | Existing operation boundary, fencing, cancellation, persistence, and receipt-2 verification |
| Effect adapters | Separate typed application orchestration; no native framework ownership |

Each nonempty track keeps one worker, with at most four workers total.
The compositor requests each frame and consumes responses in declared bottom-to-top order.
Request, response, and composed-frame channels retain capacity one.

For frame `n`, a worker finds the active `VideoUse` and computes local frame `f`.
It evaluates the resolved placement independently from `presentation_ordinals[f]`.
The ordinal chooses the source sample; the resolved placement chooses only raster geometry and weight.

`LayerFrame` carries the owned raster and its scalar `ResolvedPlacement`.
`check_decision` reevaluates the plan at `f` and compares that scalar before blending.
This catches a worker response tagged with the right source but the wrong motion frame.
It does not create stored evidence or a second animation trace.

Movie reading remains inside `media::with_track_cancellable`.
`AVAsset`, reader, output, sample buffer, and pixel buffer stay inside the native callback.
Only copied Rust pixels, ordinals, PTS values, and resolved scalar values cross channels.
No retained framework object crosses a thread or callback boundary.

PNG sources remain serialized during decode and cached only for their clip lifetime.
Opaque PNG and opaque movie BGRA remain the only inputs.
Transparent contain bars are an absent raster region, so lower tracks remain visible.

### Dynamic admission and sparse coverage

Schema-5 preflight evaluates every active use at every output frame before source decoding.
The existing 100,000-frame and four-track limits bound this work.
Each resolved rectangle passes type, overflow, and pixel-extent validation.

For each output frame, preflight sums these logical Rust payloads:

1. One source BGRA allocation for every active movie worker.
2. Each active PNG cache allocation.
3. One visible raster per active use, held in its capacity-one response path.
4. The existing three canvas allocations.
5. The largest serialized PNG decode allowance whose clip starts on that frame.

Preflight takes the maximum frame charge and rejects values above 512 MiB.
Runtime `Budget` permits reserve the same payload classes.
Motion can therefore enlarge admission when a rectangle grows or enters the canvas.

Coverage is also evaluated per frame.
A contribution requires nonempty fitted source content, canvas intersection, and nonzero Q16 opacity.
Sparse overlays may disappear, move offscreen, or reach zero opacity when lower tracks cover those frames.
The union across tracks must cover every output frame.

The admission value remains a conservative application-owned estimate.
It is not a guarantee for total Rust or native memory.
It excludes allocator capacity, PNG metadata and decompressor internals, Core Video, AVFoundation, and encoder buffers.

### Cancellation and failure

Plan validation checks cancellation between bounded frame batches during export.
Workers check before motion evaluation, source pulls, budget reservation, raster rows, and channel waits.
The compositor checks before each request and response.
Native reads remain cooperative between AVFoundation calls.

The first failure preserves the original export cause.
Teardown sets the shared stop flag, closes ports, cancels guarded readers and writers, and joins every Rust worker.
A cancelled or lease-lost export cannot promote a movie or receipt.

## Compatibility

Snapshot schema stays 1.
When `motion` is absent, `skip_serializing_if` preserves exact historical bytes.
The focused fixtures must retain these SHA-256 values:

| Fixture | Exact hash |
| --- | --- |
| snapshot 1 | `a4afc9237cdc477ddc0c62023b7e0ed185a9f39bd3f72fd3f6596964d1c82423` |
| snapshot 1 with static placement | `00d8a0eb3bbf0cd6290e68fffaa8c4d8b5a654446fb2220f5d084da17944e1ea` |
| plan 2 | `97fdd9f63d48ee3b600ee37a845c302e79815bd1870b20dae376f9c4a957e025` |
| plan 3 | `4e5a89b00e7b5fabaafb4bf1335c1a5c3538c593765b4f5e5c818ff6bcede219` |
| plan 4 | `5cf0320f82bfc19839c5a06ffec15449fcdb80b97be15e2b4fb4105517ef0687` |
| receipt 2 | `44c0c27ad1a58f22746011673d8e4d4a211c5b5cdeffcb18172d6cc73fc73be2` |

Artifact receipts remain schema 2.
Their existing `plan_id` binds every schema-5 curve and normalized constant.
`PictureExecutionEvidence` retains only its admission and live logical-counter scope.
It gains no pose list, source list, or receipt field.

Audio remains one complete 48 kHz stereo clip at unity gain and zero pan.
This unit adds no audio fades, resampling, mixing, masks, rotation, alpha input, or color expansion.
It adds no FFmpeg, libav, renderer subprocess, GPU work, or Resolve work.

## Verification contract

Pure tests cover strict key ordering, endpoint presence, segment modes, and no extrapolation.
They cover signed half ties, integer overflow, positive extents, and Q16 zero, midpoint, and one.
They also cover absent-property constants, no-op rejection, offscreen motion, transparent contain bars, and coverage handoffs.
Malformed schema-5 plans must fail when normalized motion, placement exclusivity, or `presentation_ordinals` are changed.

The native proof uses the actual AV1 movie and opaque PNG from the caller example simultaneously.
It exports 48 frames at 24 fps, with the overlay active on `[8,40)`.
The source authority is the plan's `presentation_ordinals`, not nominal frame-rate metadata.
The movie proof checks ordinals `0..47` and PTS values advancing by `512/12288`.
The PNG proof checks held ordinal zero on all 32 local frames.

Separate Python code reads the plan JSON without calling the Rust evaluator.
It evaluates every property, signed rounding case, rectangle, Q16 weight, source selection, and track order.
It creates an independent Pillow composition for all 48 frames using source-edge mapping.
It compares every full frame and every nonempty placement, contain-bar, and overlap region.

Thresholds are declared before execution:

- Pure pre-encode BGRA bytes must equal the scalar reference exactly.
- Every H.264 decoded full frame and nonempty comparison region must reach at least 34 dB PSNR.
- Every output video PTS must equal `n/24`, in order, followed by reader EOF.
- Every independent expected rectangle and Q16 weight must equal the plan result exactly.

The first audio proof selects the exact synthetic interval `[8191,104191)`.
It must decode exactly 96,000 stereo sample frames with contiguous PTS and EOF.
The second proof selects canonical interval `[0,96000)` from the 78,624,044-byte master.
That source is 24-bit PCM, 48 kHz stereo, and 13,104,000 frames long.
Both proofs keep unity gain, zero pan, no resampling, and independent zero-offset channel comparisons.

Cancellation is forced during curve preflight, PNG decode wait, movie callback reads, raster rows, response backpressure, and writer readiness.
Each case must preserve its cause, join workers, and leave no promoted receipt.

Historical verification reopens the schema-2 receipt above without rewriting it.
The associated 206-frame movie must remain `e487e36c6927916428085f262d530d8abdafc8a8e6f3edc5bfdf80ecaa617e94`.
Plans 2, 3, and 4 must still take their established execution paths.

These checks establish technical curve, clock, pixel, audio, and recovery behavior.
They do not establish maximum throughput, total native memory, watching, hearing, story quality, or full Panja hybrid acceptance.

## Rationale and red-flag screen

The project aggregate remains a deep boundary.
One commit hides validation, curve compilation, immutable planning, source probing, bounded execution, encoding, recovery, and receipt verification.
There are no public temporal stages such as `open_reader`, `evaluate_frame`, or `append_canvas`.

The design does not leak AVFoundation objects or callback lifetime rules.
`VideoUse` carries domain values and the existing measured presentation map.
Effect adapters remain separate from native movie ownership.

The work stays with the modules that own each invariant.
`motion.rs` owns curve meaning; `plan.rs` owns normalization; `composition.rs` owns pixels; `layers.rs` owns coordination.
No pass-through public service mirrors private worker calls.

## Alternatives inside the property-curve design

**Dense resolved poses in `VideoUse`.** This makes frame evaluation trivial.
It also grows plan JSON with every output frame and creates the prohibited second execution trace.
Sparse normalized curves keep the plan reviewable and hash the same semantics.

**One interpolation mode per property.** This shortens each key.
It cannot express a step hold followed by a fade or move within one property.
Per-segment `to_next` keeps that distinction explicit at the left endpoint.

**Interpolate floating opacity, then quantize every frame.** This resembles author input.
It risks runtime and independent-reference drift.
Quantizing keys once and interpolating Q16 integers gives one portable rule.

**Permit partial curve endpoints with implicit holds.** This reduces author keys.
It hides behavior before the first key and after the last key.
Required clip endpoints make every animated property locally complete.

Future picture properties may reuse this curve grammar only after receiving their own typed field and plan version.
This design does not add string-valued property maps or placeholder APIs for rotation, masks, alpha, or color.

## Material risks

- Every independent implementation must match signed tie rounding and Q16 interpolation exactly.
- Per-frame mapping adds CPU work; maximum 100,000-frame throughput remains unmeasured.
- Sparse curve plans can still grow when callers author many keys.
- The 512 MiB result remains a logical admission estimate, not total-memory proof.
- AVFoundation cancellation remains cooperative during a stalled framework call.
- Existing orientation, aperture, sample-aspect, and color-metadata limits remain.

## Next implementation step

After design judgment, implement the pure curve validator, normalizer, evaluator, and schema-5 tamper tests first.
Then extend dynamic preflight before changing native workers.
Run the simultaneous movie/PNG proof before accepting the runtime unit.
