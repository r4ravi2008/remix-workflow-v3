# Native picture masks — Candidate B

## Usage (caller's view)

The caller adds one optional `mask` member to an existing picture clip. The mask is a destination-local procedural rectangle, so it adds no imported asset or native reader. The caller still uses only the existing `Project` aggregate and public export operations.

```json
{
  "intent": "commit-mask-reveal-v1",
  "base_revision": "1947fcb6939dbec40f13ae23b87a156f5d6e1758fa18e058aaa1f810abc313d3",
  "imports": [],
  "canonical_audio": {
    "asset": "5da985961720761f773e0aae2e72ba056abe2f83b11ed5c7eecd653b3d7269ff5",
    "source_samples": {"start": 8191, "length": 144000},
    "source_rate": 48000,
    "channel_order": ["left", "right"],
    "channel_order_basis": "explicit-stereo-interpretation"
  },
  "timelines": [{
    "id": "picture-motion", "frame_count": 72,
    "video_tracks": [
      {"id":"base","clips":[{
        "id":"base-motion","timeline_frames":{"start":0,"length":72},
        "asset":"c925cc9f66b64516e8b90549fbba80d3c4d01e00a637c083b13ba9c0cddcc76a",
        "source_samples":{"start":0,"length":72},
        "cadence":{"kind":"source_presentation_time"},
        "framing":{"fit":"contain","crop":{"x":0.0,"y":0.0,"width":1.0,"height":1.0}},
        "placement":{"destination":{"x":0,"y":0,"width":320,"height":180},"opacity":1.0}
      }]},
      {"id":"anchor","clips":[{
        "id":"masked-anchor","timeline_frames":{"start":0,"length":72},
        "asset":"a03eacfe29ac98847657121bd341fc1c02b32e6a51212d4c97885fd5fd38e175",
        "source_samples":{"start":0,"length":1},
        "cadence":{"kind":"hold","ordinal":0},
        "framing":{"fit":"contain","crop":{"x":0.0,"y":0.0,"width":1.0,"height":1.0}},
        "placement":{"destination":{"x":80,"y":40,"width":160,"height":120},"opacity":1.0},
        "mask":{"family":"rectangle","coordinates":"destination_local_pixels",
          "edge":{"kind":"feather","radius_px":8.0},"inverted":false,
          "keyframes":[
            {"frame":0,"pose":{"rect":{"x":-160,"y":0,"width":1,"height":120},"opacity":1.0},"to_next":"linear"},
            {"frame":71,"pose":{"rect":{"x":0,"y":0,"width":160,"height":120},"opacity":1.0}}
          ]}
      }]}
    ],
    "audio_tracks":[{"id":"audio","clips":[{
      "id":"prefix","timeline_samples":{"start":0,"length":144000},
      "asset":"5da985961720761f773e0aae2e72ba056abe2f83b11ed5c7eecd653b3d7269ff5",
      "source_samples":{"start":8191,"length":144000},"source_rate":48000,"gain":1.0,"pan":0.0
    }]}]
  }]
}
```

The first call commits this static-placement reveal, prepares the plan, exports H.264/AAC, then verifies the stored receipt:

```rust
let revision = project.commit(mask_reveal_commit)?;
let request = ExportRequest { intent: id("export-mask-reveal-v1"), revision: revision.revision.clone(), timeline: id("picture-motion"), profile: MovieProfile::H264AacMp4 { video_bitrate: 12_000_000, audio_bitrate: 192_000 } };
let prepared = project.prepare_export(request.clone())?;
let exported = project.export(request.clone())?;
let verified = project.verify_export(request.intent.clone())?;
```

A moving clip uses the same call sequence. Its existing `PictureMotion` resolves the destination rectangle first; the mask rectangle remains local to that resolved destination, so the reveal follows the clip without a second public animation API:

```rust
let revision = project.commit(masked_motion_commit)?;
let request = ExportRequest { intent: id("export-moving-mask-v1"), revision: revision.revision.clone(), timeline: id("picture-motion"), profile: MovieProfile::H264AacMp4 { video_bitrate: 12_000_000, audio_bitrate: 192_000 } };
project.prepare_export(request.clone())?;
project.export(request.clone())?;
project.verify_export(request.intent)?;
```

Cancellation uses the same owner and fencing path. `project.cancel_export(intent)` interrupts preparation, decoding, channels, native loading, verification, or promotion; a cancelled attempt has no promoted receipt. Effect and GPU adapters remain outside this aggregate. This unit has no external mask file, FFmpeg/libav path, renderer subprocess, audio edit, PNG alpha input, rotation, text, color transform, or creative acceptance claim.

## Problem

A14 already owns source ordinals, measured source PTS, independent picture motion, sparse track coverage, opaque BGRA input, Q16 layer opacity, four bounded workers, and a receipt-2 recovery path. A mask must add coverage without changing any of those authorities. Candidate B chooses a destination-local analytic rectangle program rather than a decoded mask asset or a dense per-frame bitmap. That makes crop/fit, signed clipping, contain bars, motion, and memory ownership explicit while keeping the public surface at `Project::commit`, `prepare_export`, `export`, `cancel_export`, and `verify_export`.

## Shape

```rust
#[serde(rename_all = "snake_case")]
pub enum MaskFamily { Rectangle }
#[serde(rename_all = "snake_case")]
pub enum MaskCoordinates { DestinationLocalPixels }
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum MaskEdgeWire { Hard, Feather { radius_px: f64 } }
pub enum MaskEdge {
    Hard,
    Feather { radius_q16: u32 }, // 1..=512 pixels after normalization
}
pub struct MaskPose {
    pub rect: PixelRect,          // signed local x/y; positive width/height
    pub opacity_q16: OpacityQ16,  // 0..=65536
}
pub struct MaskKey { pub frame: u64, pub pose: MaskPose, pub to_next: Option<CurveInterpolation> }
pub struct MaskProgram { pub keys: Vec<MaskKey> } // no dense frame table
pub struct MaskWire {
    pub family: MaskFamily, pub coordinates: MaskCoordinates, pub edge: MaskEdgeWire,
    pub inverted: bool, pub keyframes: Vec<MaskKeyWire>,
}
pub struct MaskKeyWire { pub frame: u64, pub pose: MaskPoseWire, pub to_next: Option<CurveInterpolation> }
pub struct MaskPoseWire { pub rect: PixelRect, pub opacity: f64 }
pub struct PlannedMask {
    pub coordinates: MaskCoordinates,
    pub edge: MaskEdge,
    pub inverted: bool,
    pub program: MaskProgram,
}
pub struct MaskCoverage { pub bounds: Bounds, pub q16: Vec<u32> } // 0..=65536 per pixel
pub struct MaskObservation { pub pose: MaskPose, pub has_visible_coverage: bool }

pub fn normalize_mask(input: &MaskWire, clip_frames: u64) -> Result<PlannedMask> { not_implemented!() }
pub fn resolve_mask(mask: &PlannedMask, local_frame: u64) -> Result<MaskPose> { not_implemented!() }
pub fn sample_mask(
    mask: &PlannedMask, pose: &MaskPose, placement: &ResolvedPlacement,
    bounds: &Bounds, check: impl FnMut() -> Result<()>,
) -> Result<Option<MaskCoverage>> { not_implemented!() }
pub fn blend_masked_cancellable(
    canvas: &mut Pixels, layer: &Raster, coverage: &MaskCoverage,
    layer_opacity_q16: OpacityQ16, check: impl FnMut() -> Result<()>,
) -> Result<()> { not_implemented!() }
```

The wire type accepts decimal `opacity` and `radius_px`; commit maps it once to `OpacityQ16` and Q16 pixels. Stored `RectangleMask` and schema-6 `VideoUse.mask` serialize integers and complete mask keys. No stored integer is parsed as a decimal opacity. `normalize_mask` requires one to `MAX_MASK_KEYS` keys, the first at local frame zero, strictly increasing frames below `clip_frames`, interpolation only on nonfinal keys, positive checked rectangles, finite radius, and no unknown family or coordinate value. The final pose holds through the clip's last frame. A one-key mask is valid.

The rectangle is attached to the resolved placement's top-left. At each local frame, existing `motion::resolve` first produces the signed destination and layer opacity. For a visible raster pixel at canvas integer `(px, py)`, the mask sample center is

```text
cx_q16 = ((px << 16) + 32768) - (placement.destination.x << 16)
cy_q16 = ((py << 16) + 32768) - (placement.destination.y << 16)
```

The mask rectangle edges are `left = rect.x<<16`, `right = (rect.x+width)<<16`, and equivalent top/bottom values. All intermediate coordinates use `i128`; signed clipping happens after mapping. Crop is applied in source coordinates, `Contain` or `Cover` determines the fitted content, and the mask samples the fitted destination. `Stretch` uses the same destination sample rule with its independent scales. A placement resize does not resize the mask rectangle; a canvas-fixed mask is deferred.

`Hard` coverage is `65536` when the center lies in the half-open rectangle and `0` otherwise. `Feather` uses signed L-infinity edge distance `d = min(cx-left, right-cx, cy-top, bottom-cy)` in Q16. With radius `r`, coverage is `clamp(round_half_up((d+r)*65536/(2*r)), 0, 65536)`. The edge is zero at `d <= -r`, full at `d >= r`, and one center sample is taken per destination pixel. Inversion changes `m` to `65536-m` before opacity. The final Q16 blend weight is one rounded product:

```text
w = round_half_up(m * mask_pose.opacity_q16 * layer_opacity_q16 / 65536^2)
```

`blend_masked_cancellable` uses the existing RGB equation `(input*w + canvas*(65536-w) + 32768)/65536`. Source and raster alpha must remain 255. The mask supplies coverage, not a source alpha plane; output alpha remains 255. A zero weight pixel is skipped. A fully zero `MaskCoverage` returns no layer payload after its scalar observation is checked.

`MaskCoverage` owns Q16 `u32` samples with the same sparse `Bounds` as the opaque `Raster`; `u16` cannot represent the exact `65536` endpoint. A response carries owned raster and coverage permits plus scalar `ResolvedPlacement`, `MaskObservation`, source ordinal, and source PTS. `check_decision` recomputes both placement and mask pose from the immutable `VideoUse`, rejects any scalar mismatch, and verifies that a `Gap` occurs only outside an active use. It does not persist a second per-frame trace.

| Module | Owns |
| --- | --- |
| `model.rs` | Optional authoring `mask`; snapshot-1 validation and absent-field byte compatibility |
| `mask.rs` | Wire normalization, rectangle program evaluation, Q16 edge sampling, inversion, coverage raster and mask-specific limits |
| `motion.rs` | Existing placement and layer-opacity resolution; no mask defaults leak into it |
| `plan.rs` | Schema-6 choice, normalized mask copy, source/PTS map, central tamper comparison |
| `composition.rs` | Sparse mapping bounds, frame-local admission, mask/raster/canvas permits, ordered masked blend |
| `layers.rs` | Bounded workers, callback-confined readers, raster plus mask coverage responses, scalar response checks |
| `movie.rs` / `exports.rs` | Existing H.264/AAC writer, epoch fencing, receipt-2 storage, cancellation and product reverify |
| CLI / Effect / GPU adapters | Mask authoring and review orchestration only; no native object or worker ownership |

This is a deep public boundary: one project operation hides normalization, schema choice, source closure, mask sampling, workers, backpressure, native callback lifetime, receipt fencing, and verification. No caller coordinates readers, frame stages, mask buffers, or executor state. The domain program remains the single source of truth; transient coverage is derived at the response boundary.

### Coverage, sparse tracks, and admission

`Mapping` produces bounds only for fitted content that intersects the canvas and has nonzero layer opacity. Contain bars therefore never receive mask samples or become opaque mask pixels. A negative placement is clipped by the existing mapping bounds, while the local mask coordinates still subtract the signed placement origin. A mask outside those bounds contributes no pixels. A sparse track may return `Gap`; an active, fully masked clip returns `Source` with no payload. Preflight rejects a timeline frame only when the union of all active mappings and nonzero mask coverage is empty. A lower track can cover a fully masked overlay frame.

Preflight runs central validation first, then evaluates every local motion and mask pose before workers start. It rejects more than four nonempty tracks and computes per-frame charges for one source copy per active worker, the sparse BGRA raster, a Q16 coverage plane (`4 * visible_pixels`), response overhead, three canvas charges, active PNG cache, compressed PNG bytes, decoded PNG/RGBA samples, and the configured decoder allowance. It uses checked `u128` arithmetic, the existing 512 MiB logical limit, and `pixels::extent` per owned allocation. It admits only the conservative application-owned estimate; AVFoundation, Core Video, allocator, encoder, and total process peak remain unmeasured.

Each worker reserves source, raster, and coverage permits before ownership crosses its capacity-one response channel. The compositor consumes the raster and coverage before requesting the next frame and before sending the canvas to the capacity-one writer channel. `MaskCoverage` never retains framework memory. Cancellation checks during preflight, pose evaluation, each coverage row, channel waits, blending, writer readiness, and native loading. Dropped ports set the stopped flag, close both channel sides, cancel guarded readers, and join every worker before export returns. Epoch and cancellation checks prevent promotion after a lost lease.

### Schema and central tamper boundary

Snapshot remains schema 1. `VideoClip.mask` is appended with `serde(default, skip_serializing_if = "Option::is_none")`, so absent masks preserve Snapshot 1 bytes. A mask-bearing timeline selects private plan schema 6. A no-mask plan retains its existing schema 2, 3, 4, or 5 selector and exact serialized bytes. `VideoUse.mask` is appended similarly; schema 6 stores normalized Q16 mask programs, never a dense coverage table. Receipt schema 2 and `PictureExecutionEvidence` remain unchanged. The preserved mask fixture manifest is `cf3ccb32ea68a58532a312c921024107fcc3773b9f2cc68dd7ddab5ba0b6695f`. Existing fixtures must retain their exact hashes: Snapshot motion `1947fcb6939dbec40f13ae23b87a156f5d6e1758fa18e058aaa1f810abc313d3`, Plan 5 `8ca51e03d048971a86cb598990fabd2f93f839c98b1b6c5fda3eb7aa90c3ee06`, Plan 2 `97fdd9f63d48ee3b600ee37a845c302e79815bd1870b20dae376f9c4a957e025`, Plan 3 `4e5a89b00e7b5fabaafb4bf1335c1a5c3538c593765b4f5e5c818ff6bcede219`, Plan 4 `5cf0320f82bfc19839c5a06ffec15449fcdb80b97be15e2b4fb4105517ef0687`, and Receipt 2 `44c0c27ad1a58f22746011673d8e4d4a211c5b5cdeffcb18172d6cc73fc73be2`.

`plan::validate_picture_mapping_cancellable` rebuilds the Snapshot from the plan closure, validates schema 2..6, recompiles the mask from the timeline clip, and compares mask family, coordinate space, edge, inversion, complete normalized keys, placement/motion, ordered tracks, source ranges, ordinals, framing, and audio uses. Snapshot validation retains per-track non-overlap; a mask has no independent timeline span. It checks every movie ordinal against `source_closure[asset].descriptor.samples[ordinal].pts`, preserves held-image ordinal zero, and requires schema 6 whenever any mask exists. A plan field checked only inside `layers.rs` is rejected as tampering. Mask data adds no closure asset in this unit; future external masks must add an explicitly measured closure entry.

### Native ownership and feasibility

The actual source path remains Rust-owned pixels plus AVFoundation. `media::with_track_cancellable` loads the selected track asynchronously and runs the reader operation inside its Objective-C callback and autorelease pool. `AVAssetTrack`, `AVAssetReader`, outputs, `CMSampleBuffer`, and `CVPixelBuffer` never cross a Rust channel. The worker copies BGRA, computes CPU mask coverage from scalar Q16 poses, and sends only owned `Pixels`, `Raster`, `MaskCoverage`, permits, and scalar observations. PNG decode remains serialized. No native mask object or pointer escapes its callback lifetime.

The writer still creates H.264 video and AAC audio with AVAssetWriter. Video PTS remains `n/24` from the plan frame clock. The single audio clip remains measured 48 kHz stereo, unity gain and zero pan. Masks do not touch PCM, audio timestamps, output PTS, source PTS, or canonical source bindings.

## Synthesis decision

Candidate B chooses destination-local analytic coverage because it keeps masks attached to the moving destination while leaving source crop and native decoding untouched. It adds one domain program and one schema boundary, not a mask asset pipeline. A full-frame coverage table, source-space raster decoder, and canvas-fixed public coordinate mode are rejected from this unit.

## Alternatives considered

- A source-space mask would follow crop and fit, but callers would need to reason about source pixels, crop windows, and cover trimming. Destination-local coordinates keep placement and reveal behavior inspectable.
- A decoded grayscale or alpha movie would add source measurement, codec support, callback lifetime, and mask-cache ownership. The first rectangle family proves the compositor seam before that payload exists.
- A dense per-frame mask bitmap would make random access simple but would inflate plans, hashes, admission, and tamper surface. The keyed program derives one bounded coverage plane at each requested frame.
- A canvas-space mask would expose an additional transform relationship and would not follow `PictureMotion`. It remains a future explicit coordinate family rather than an implicit default.

## Verification and first experiment

Pure vectors use exact integer reference code independent of Rust `mask.rs`. They cover hard half-open edges, feather distances at `-r`, `0`, and `+r`, inversion, Q16 opacity-product ties, one-key final holds, keyed rectangle interpolation, negative placement, signed clipping, crop/contain/cover/stretch, contain-bar transparency, zero layer opacity, fully masked sparse frames, lower-layer visibility, overlap order, opaque-alpha rejection, unknown fields, and overflow limits. They assert mask coordinates never change source ordinals or PTS.

Before the native run, hash and bind the exact A14-grade producer `d8ae6b396206a2dc684183dbebb20fb410f6ecd48a84f0e26882ec5ea4be16e3`, lock `e1499a56b2de8f306dd29bddd44a72a4d2d420e1b3591cff8ba777b5eb123448`, build record `054c25b639a27a0de5e6ce5f5f3f56c3b59943682b33b7fe547e1614628a00e2`, native backend `objc2 0.3.2 / AVFoundation bundle 2360.79.5.2`, host `Version 26.0.1 (Build 25A362)`, and the five measured closure assets from Plan 5: `c925cc9f66b64516e8b90549fbba80d3c4d01e00a637c083b13ba9c0cddcc76a`, `a2247e96ab4335eb6b365ef52b6203e53377c6cf317ebb2e156789e6bd470b7f`, `0e38532679abfb53386659762888dba87dcad8ff7d3377f0ffe9eccb355fe8d3`, `a03eacfe29ac98847657121bd341fc1c02b32e6a51212d4c97885fd5fd38e175`, and `5da985961720761f773e0aae2e72ba056abe2f83b11ed5c7eecd653b3d7269ff5`. Bind their measured descriptors too: AVFoundation `avc1` 1536x640 and `av01` 1920x1080 movies, two opaque PNGs, and measured 48 kHz stereo LPCM.

Run a new schema-6 72-frame plan with the same four-track structure: two simultaneous movie readers, two PNG sources, a signed moving placement, a feathered reveal, contain bars, sparse intervals, and overlap. Anchor the predecessor synthetic receipt `505847160c4b16355af75199cc3775a7064219359086f543a062929819c053d7` and output `097dd9a1a59c02a8967db82463e8b43fc6ffc42a5294c997a77280967b1174df`; anchor the canonical receipt `69b692a1cd7940a5a93f8f4112efefaf70d85871044b5f0a432cd63bcb9b5b28` and output `c4a94f3981bcb6a222aebca2d214b3c1f18972251ddddbfe460dac98b17928c3`. Create a new receipt for the mask plan. Bind each source measurement, selected ordinal, source PTS and closure hash before export. Bind the fresh receipt document, receipt CAS bytes, plan hash, revision, output hash, output bytes, producer, and export epoch. The independent pixel observer must compare every frame and visible/overlap region against its own mask evaluator. It must confirm output PTS epoch zero and `n/24`, video EOF at 72 frames, and source movie/held-image clock evidence.

Use the separate A14 observers: verifier A02 `8c323c743aed8c185f5720afb64b433999e2db365a7c1897bddcb7bdbddcf41a` with report `40f650818cea1e7687a2cdd174fef02ede95add80bbb62fccda9ba72a868c562`, epoch observer `1885e2ba4df470d806b51fed8a8e5238464f71ff70641e28a6ea3eecd4318b20`, and A03 audio verifier `1b28e53a695b06d44efbd2a6d9c22d9918a4abe8b3080c0bf199a9e34bd17d36` with report `6225fbd6200d0249583203e51fa4489ce2361eaac84bebc756b93c7733b91179`. Compare fresh synthetic PCM to the actual selected WAV interval `[8191,152191)` and canonical 24-bit master prefix `[0,144000)` under the declared policy. Record every chunk's epoch, offset, positive length and EOF. Retain f32 decode variation and do not claim bit-stable AAC output.

Run deliberate negative controls against independent validators. The A14 control manifest is negative-controls report `956180e83fe5b1ee0f865ecbd34dba9ca1c56823aee5d90dfaf1f07f26478d0f`; preserve its 21 source/receipt controls and eight epoch/PTS/EOF controls, then add mask-key, edge-radius, and inversion mutations. Each must fail at the boundary named by the mutation. Preserve unsuccessful attempts and any lost bytes as unverifiable. Reverify the unchanged historical schema 2/3/4/5 fixtures and Receipt 2 before and after the new run. This is bounded native technical evidence only; it does not establish normal-speed playback, listening, creative quality, or full Panja acceptance.

## Interface depth and red-flag screen

The public interface remains small while `mask.rs`, `plan.rs`, `composition.rs`, and `layers.rs` hide normalization, coordinate conversion, edge math, permits, response checks, cancellation, and native lifetime. No transport type, native pointer, callback, worker, or coverage buffer reaches the caller. A public `open_mask`, `sample_mask`, or `blend_mask` sequence would be shallow and would leak temporal ownership. The design groups modules by mask and composition knowledge rather than by load/validate/render timing.

## Tradeoffs, open questions, and risks

- We accept destination-local pixel coordinates in exchange for predictable placement-following reveals. Source-space and canvas-space masks remain explicit future families.
- We accept a Q16 coverage plane per visible raster in exchange for independently observable, deterministic edge math. Preflight rejects the plan when that plane exceeds the logical budget.
- We accept one center sample per output pixel in exchange for bounded CPU work. Supersampling, blur and Euclidean feather edges are deferred.
- We accept procedural rectangles with no mask asset in exchange for avoiding a new decoder and source-closure family. External grayscale or alpha masks require a separate measured representation.
- Will the L-infinity feather edge meet the creative reveal requirement? If not, add a new edge family without changing hard-rectangle bytes.
- Can a future macOS target preserve the measured AVFoundation reader behavior for both A14 movie sources? If not, preparation must return structured unsupported-source evidence.
- What is the maximum native cancellation latency inside a framework call? The design checks cooperatively and makes no stronger timing claim.

## Next implementation step

Implement `mask.rs` pure normalization and coverage vectors first, then add schema-6 central validation and frame-local admission before adapting the bounded worker response and ordered compositor; run the separate A14-grade native proof only after those runtime boundaries exist.
