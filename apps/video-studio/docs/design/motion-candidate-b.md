# Native picture motion — Candidate B

## Usage (caller's view)

This uses the current `Project::commit` envelope. The only new member proposed below is the optional clip-local `pose_keyframes`; all hashes are complete and already measured. The returned revision is then passed to the existing `prepare_export`, `export`, `cancel_export`, and `verify_export` methods.

```json
{
  "intent": "commit-motion-v1",
  "base_revision": "1f36eb734ab558b92e88557c980143b43c72ca5b1349da2ede920d2c8b95eb92",
  "imports": [],
  "canonical_audio": {
    "asset": "cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8",
    "source_samples": { "start": 0, "length": 13104000 },
    "source_rate": 48000,
    "channel_order": ["left", "right"],
    "channel_order_basis": "explicit-stereo-interpretation"
  },
  "timelines": [{
    "id": "main", "frame_count": 48,
    "video_tracks": [
      {"id":"movie","clips":[{
        "id":"background","timeline_frames":{"start":0,"length":48},
        "asset":"a2247e96ab4335eb6b365ef52b6203e53377c6cf317ebb2e156789e6bd470b7f",
        "source_samples":{"start":0,"length":48},
        "cadence":{"kind":"source_presentation_time"},
        "framing":{"fit":"cover","crop":{"x":0.0,"y":0.0,"width":1.0,"height":1.0}},
        "placement":{"destination":{"x":0,"y":0,"width":2560,"height":1440},"opacity":1.0}
      }]},
      {"id":"movie-overlay","clips":[{
        "id":"second-reader","timeline_frames":{"start":0,"length":48},
        "asset":"a2247e96ab4335eb6b365ef52b6203e53377c6cf317ebb2e156789e6bd470b7f",
        "source_samples":{"start":0,"length":48},
        "cadence":{"kind":"source_presentation_time"},
        "framing":{"fit":"cover","crop":{"x":0.0,"y":0.0,"width":1.0,"height":1.0}},
        "placement":{"destination":{"x":-50,"y":50,"width":1600,"height":900},"opacity":0.65}
      }]},
      {"id":"png-overlay","clips":[{
        "id":"anchor","timeline_frames":{"start":0,"length":48},
        "asset":"a03eacfe29ac98847657121bd341fc1c02b32e6a51212d4c97885fd5fd38e175",
        "source_samples":{"start":0,"length":1},
        "cadence":{"kind":"hold","ordinal":0},
        "framing":{"fit":"contain","crop":{"x":0.0,"y":0.0,"width":1.0,"height":1.0}},
        "pose_keyframes":[
          {"frame":0,"pose":{"destination":{"x":160,"y":90,"width":1600,"height":900},"opacity":1.0},"to_next":"linear"},
          {"frame":47,"pose":{"destination":{"x":210,"y":90,"width":1600,"height":900},"opacity":0.0}}
        ]
      }]}
    ],
    "audio_tracks":[{"id":"canonical-audio","clips":[{
      "id":"song-prefix","timeline_samples":{"start":0,"length":96000},
      "asset":"cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8",
      "source_samples":{"start":0,"length":96000},"source_rate":48000,"gain":1.0,"pan":0.0
    }]}]
  }]
}
```

The tracks are bottom-to-top: `movie`, `movie-overlay`, then `png-overlay`. The repeated movie hash intentionally exercises two simultaneous native reader sessions. The audio labels are an explicit left/right interpretation; the imported descriptor has no measured channel labels.

The `pose_keyframes` array is complete: every keyframe carries a destination rectangle and opacity. It uses the clip-local integer frame clock, not the timeline or source clock. A simple fade is authored with `PoseProgram::fade_from_static` or a CLI helper that expands a static placement into complete poses before commit. The stored model never has separate placement and opacity curves.

```rust
let revision = project.commit(motion_commit)?;
let request = ExportRequest {
    intent: EntityId::parse("export-motion-v1")?,
    revision: revision.revision.clone(),
    timeline: EntityId::parse("main")?,
    profile: MovieProfile::H264AacMp4 { video_bitrate: 12_000_000, audio_bitrate: 192_000 },
};
let prepared = project.prepare_export(request.clone())?;
let result = project.export(request)?;
project.cancel_export(EntityId::parse("export-motion-v1")?)?;
project.verify_export(EntityId::parse("export-motion-v1")?)?;
```

The caller does not open workers, readers, pixel buffers, or an executor. Effect/GPU adapters, provider attempts, and review records remain outside the native editor. The path remains in-process AVFoundation with no FFmpeg, libav, or renderer subprocess. This unit has no audio fades, resampling, masks, rotation, alpha inputs, or color changes.

## Problem

A13 accepts static opaque movie/PNG layers through at most four bounded track workers. `VideoUse` already binds `timeline_frames`, `asset`, `allowed_source_samples`, `presentation_ordinals`, `framing`, and normalized `placement`. Motion should change only the evaluated placement, not source selection, source PTS, track order, or the one identity 48 kHz stereo audio path. Independent position and opacity curves would create mismatched endpoints and hidden default rules. Candidate B stores one typed complete pose at every keyframe and evaluates it on the clip-local frame clock.

The actual plan4 artifact records AVFoundation-selected samples, native presentation PTS at 24 fps, and a successful selected-range decode for movie `a2247e96ab4335eb6b365ef52b6203e53377c6cf317ebb2e156789e6bd470b7f` (the measured 1920x1080 AV1 descriptor). That is evidence for this asset and range, not generic AV1 support. A private codec registry binds its explicit supported source representation; preparation rejects an unproved AV1 or VP9 source instead of guessing. Motion never substitutes a VP9 source. The preserved R23 output profile remains H.264/AAC.

## Shape

```rust
pub struct PicturePose {
    pub destination: PixelRect, // signed x/y; positive checked width/height
    #[serde(rename = "opacity_q16")]
    pub opacity: OpacityQ16,   // serialized as integer 0..=65536
}
pub enum PoseInterpolation { Step, Linear }
pub struct PoseKeyframe {
    pub frame: u64,             // local frame, strictly increasing
    pub pose: PicturePose,      // never partial; no inherited fields
    pub to_next: Option<PoseInterpolation>,
}
pub struct PoseProgram { pub keyframes: Vec<PoseKeyframe> }

impl PoseProgram {
    pub fn new(keyframes: Vec<PoseKeyframe>, clip_frames: u64) -> Result<Self> { not_implemented!() }
    pub fn evaluate(&self, local_frame: u64, clip_frames: u64) -> Result<PicturePose> { not_implemented!() }
    pub fn fade_from_static(base: PicturePlacement, from: f64, to: f64, end: u64)
        -> Result<Self> { not_implemented!() }
}

#[serde(transparent)]
pub struct OpacityQ16(u32); // denominator 1<<16; deserialization range-checks 0..=65536
impl OpacityQ16 {
    pub fn from_f64(value: f64) -> Result<Self> { not_implemented!() }
    pub fn value(self) -> u32 { self.0 }
}

// Commit-only input; it is never used to deserialize a stored plan.
pub struct CommitPicturePose { pub destination: PixelRect, pub opacity: f64 }
pub struct CommitPoseKeyframe {
    pub frame: u64, pub pose: CommitPicturePose, pub to_next: Option<PoseInterpolation>
}
// Stored snapshots and schema-5 plans use `opacity_q16` as an integer.
// `PoseProgram` serde never sends 32768 through `OpacityQ16::from_f64`.
```

`new` requires a nonempty list, first `frame == 0`, strict local ordering, every frame `< clip_frames`, valid rectangles, `to_next == None` only on the last keyframe, and a bounded keyframe count. No pose inherits from a prior clip, track, or omitted property. `evaluate(local_frame, clip_frames)` rejects a frame outside the clip. It interpolates between keyframes, then holds the final keyframe through `clip_frames - 1` when the final keyframe is earlier than the clip end; “no extrapolation” means no motion beyond that held pose. If `pose_keyframes` is absent, current A13 static semantics apply: schema 4 normalizes `placement`, and absent placement means full canvas at opacity one. If keyframes are present, `placement` must be absent and the first complete pose is mandatory. This makes defaults explicit without making a simple fade require a second runtime API.

`OpacityQ16::from_f64` rounds once with the signed nearest rule used by the domain constructor. Zero and one map exactly to 0 and 65536. Blend arithmetic retains A13's denominator 65536 and half-up byte rounding. For a linear segment from `a` at `fa` to `b` at `fb`, each signed rectangle component is

```text
round_half_away_from_zero((a * (fb - f) + b * (f - fa)) / (fb - fa))
```

using `i128` intermediates. Width and height are revalidated positive after rounding. Opacity uses the same rational interpolation in Q16 and has exact endpoint values. Step returns the left pose until the next keyframe; both modes return a keyframe's stored pose exactly at its frame. The final pose is held to the clip end, with no extrapolation.

The commit wire accepts decimal opacity for authoring ergonomics through the private `CommitPoseKeyframe` adapter, then quantizes it once at commit. Stored `PoseProgram` serde emits `pose.opacity_q16` as an integer in `0..=65536`; schema-5 plan serde reads that integer directly. Thus `.5` becomes `32768` once, and a stored `32768` is never interpreted as decimal `0..1`. The snapshot and plan contain the same normalized keyframe program at their immutable boundaries, not a per-frame pose trace.

The optional field is appended to both stored `VideoClip` and planned `VideoUse`:

```rust
#[serde(default, skip_serializing_if = "Option::is_none")]
pub pose_keyframes: Option<PoseProgram>,
```

The commit decoder maps `CommitPoseKeyframe` to `PoseKeyframe` before snapshot hashing. `plan::compile` copies that normalized program into `VideoUse`; it does not copy source frames or create a second animation trace. `VideoUse.presentation_ordinals[local]` remains the source authority. The observed movie PTS is checked against `plan.source_closure[&use_.asset].descriptor.samples[ordinal].pts`; PNG remains ordinal zero with no source PTS.

Animation alone selects plan schema 5. In a schema-5 mixed plan, each static `VideoUse` has a concrete `placement` (authored or full-canvas opaque default) and no pose. Each animated `VideoUse` has `placement: None` and a complete `pose_keyframes` program; the evaluated pose is authoritative, with no duplicated static placement or inheritance. `plan::compile` retains A13's no-within-track-overlap and bottom-to-top track-order checks. Static plans retain schema 2, 3, or 4. Snapshot schema 1 is unchanged. Because the new fields are appended and skipped when absent, old snapshot bytes and exact plan 2/3/4 bytes remain unchanged. Only the private schema allowlists and validators extend to 5; public project methods do not change. Artifact receipt schema 2 remains unchanged; its existing `plan_id` binds a schema 5 animated plan. `PictureExecutionEvidence` remains fresh execution data, not a second persisted animation trace.

### Evaluation and dynamic admission

`composition::preflight` evaluates every local pose for every active clip before a worker opens a reader. It calls the existing `Mapping::new` for that pose, so visible coverage excludes zero-Q16 opacity, offscreen intersections, and transparent contain bars. It unions visible contributions across tracks and rejects any timeline frame with no visible layer. An overlay may fade out or be absent while another track remains visible.

The same pure `PoseProgram::evaluate` call runs inside each existing `layers.rs` track worker. For each requested timeline frame it computes local `frame - use.timeline_frames.start`, evaluates the pose, creates a mapping, reads the existing `presentation_ordinals[local]`, checks the descriptor sample PTS, and rasterizes. The worker returns owned pixels plus the scalar evaluated pose; it never blends. `check_decision` recomputes the expected pose and rejects a response mismatch. The ordered compositor then calls `composition::blend` with the response pose's opacity, in declared track order. It does not alter audio or output timestamps.

Admission is dynamic, not a static maximum rectangle: before worker creation it bounds the four decoder sessions and sums each frame's raster bounds, one current source copy per worker, persistent PNG ownership, and the opaque canvas. The PNG term is an explicit conservative ownership estimate for compressed file bytes, decoded samples/RGBA, decoder internals, and one temporary frame. It records only the maximum logical owned payload and rejects above `MAX_ADMITTED_BYTES`. Runtime `Budget` permits still guard every raster/source allocation. This remains an estimate; Core Video, AVFoundation, allocator, and writer memory are not claimed.

### Native ownership and public modules

The A13 worker shape remains: at most four Rust workers, one per nonempty track, capacity-one request/response/composed-frame channels, and one ordered compositor. Each movie worker transfers its `FnOnce` operation into `media::with_track_cancellable`; AVFoundation objects remain inside that completion callback. No `Retained` native object, raw pointer, borrowed track, `CMSampleBuffer`, or `CVPixelBuffer` crosses a channel. Only owned `Pixels` and scalar ordinal/PTS observations cross. Cancellation checks pose evaluation, source pulls, raster admission, channel waits, and writer readiness, then closes channels, cancels guarded readers, and joins workers.

| Module | Owns |
| --- | --- |
| `model.rs` | Optional complete pose program; snapshot-1 validation and absent-field serialization |
| `plan.rs` | Pose validation/copy into `VideoUse`, source ordinal/PTS authority, schema 5 selection |
| `composition.rs` | Q16 interpolation, signed rounding, pose-aware mapping, union coverage and dynamic admission |
| `layers.rs` | Existing bounded track workers, callback-scoped native readers, per-frame pose evaluation and raster-only responses; ordered compositor blending |
| `media.rs` | Private codec registry and explicit source-representation choice; callback-scoped AVFoundation reader lifetime |
| `movie.rs` | Existing H.264/AAC writer, output frame clock, cancellation and reopen path |
| `project.rs` / `exports.rs` | Existing commit, prepare, export, cancel, verify, fencing and receipt-2 storage |
| CLI authoring / Effect adapters | Optional fade expansion, typed external effects, GPU/provider orchestration; never native reader ownership |

The public surface remains `Project::commit`, `prepare_export`, `export`, `cancel_export`, and `verify_export`. It hides pose compilation, dynamic admission, workers, native callbacks, backpressure, and output verification. No public executor or secondary plan object is added.

## Synthesis decision

This candidate keeps A13's accepted worker/callback ownership and exact existing `VideoUse` source map, but changes the motion representation to a complete pose program. The compiler remains the only owner of schema selection and normalized execution inputs. Independent property curves, per-frame plan expansion, and native-object handoff are rejected.

## Verification and first experiment

Pure tests cover first-frame and strict ordering, missing final interpolation, step and linear poses, signed x/y rounding at negative and positive ties, positive width/height rounding, Q16 0/mid/65536 endpoints, no inheritance, placement/keyframe conflict, static default compatibility, zero-opacity/offscreen/bar-only coverage, and dynamic budget rejection.

The first native proof uses two actual simultaneous AVFoundation movie readers for the measured `a224...` range, the PNG overlay, and the exact hashes in the caller example. It renders 48 frames at 24 fps, checks timeline/audio clocks, and checks every `presentation_ordinals` entry against `source_closure[asset].descriptor.samples`. An independent pixel evaluator reproduces the complete pose program and compares every decoded frame, including lower-layer visibility through contain bars, the 50-pixel reposition, and exact opacity endpoints. The writer remains H.264/AAC with synthetic offset PCM, followed by the separate canonical 24-bit master-prefix regression over 96,000 stereo frames.

The proof also reopens historical schema 2, 3, and 4 plans and the preserved schema-2 receipt without rewriting bytes. It runs `verify_export` on the historical 206-frame artifact. Cancellation during pose evaluation and bounded channel backpressure must preserve `export_interrupted`, close workers, and prevent promotion. Technical readback does not claim normal-speed watching, listening, or full Panja hybrid acceptance.

## Interface depth and red-flag screen

The deep boundary is unchanged: one project operation hides storage, immutable plan compilation, curve validation, native readers, dynamic memory admission, composition, encoding, recovery, and reopen verification. A shallow design exposing `set_position_curve`, `set_opacity_curve`, `open_worker`, and `append_frame` would force callers to coordinate clocks and shutdown. Separate property curves also permit one curve to omit a placement or use different endpoints. Complete poses make the invariant local and hashable.

This avoids information leakage because `VideoUse` contains domain poses and existing source ordinals, never framework objects or wire callbacks. It avoids temporal decomposition because pose compilation and picture ownership stay with the plan/composition modules, not public load/animate/render stages. It avoids pass-through methods because the existing project operations retain fencing and receipt policy.

## Tradeoffs, alternatives, and risks

- We accept repeating a destination rectangle in simple fade keyframes in exchange for no hidden property inheritance. The authoring helper expands a static placement for ergonomic fades without weakening the stored type.
- We accept integer-frame motion and Q16 opacity in exchange for deterministic endpoints and reproducible pixels. Subframe motion is a future explicit clock capability.
- Independent property curves lose because they expose mismatched clocks and partial-keyframe defaults. A pre-expanded per-frame pose table loses because it bloats plans and becomes a second animation trace.
- Dynamic preflight can be O(frames × active clips), but the existing 100,000-frame bound keeps the work bounded and prevents unadmitted allocations.
- AVFoundation callback calls remain cooperative. The current no-handoff callback ownership is retained, but a stalled framework call cannot be forcibly interrupted.
- The real AV1 source index and VP9 rejection remain capability facts; this motion unit does not authorize codec substitution, alpha inputs, masks, rotation, color changes, or audio edits.

## Next implementation step

Implement the pure evaluator, Q16 serde roundtrip, and pose-aware preflight first. Then adapt workers to return raster plus pose and adapt the ordered compositor to blend the checked response. Only after that runtime adaptation can the two-reader movie/PNG native proof and independent canonical-audio readback run.
