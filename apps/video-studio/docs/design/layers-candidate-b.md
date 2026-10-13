# Layered native picture composition — Candidate B

## Usage (caller's view)

The caller commits layer intent and then exports an immutable revision. The caller never opens AVFoundation readers or coordinates decode, blend, audio, and encode stages. Tracks are listed bottom to top. Clips on one track cannot overlap; clips on different tracks may overlap. The union of all clip spans must cover every output frame.

```json
{
  "schema": 1,
  "project": "panja",
  "base_revision": "sha256:8b6e...",
  "timeline": {
    "id": "main", "frame_count": 240,
    "video_tracks": [
      {"id":"background","clips":[{
        "id":"shot-0001","timeline_frames":{"start":0,"length":240},
        "asset":"sha256:av1-or-native-representation...",
        "source_samples":{"start":120,"length":240},
        "cadence":{"kind":"source_presentation_time"},
        "destination":{"x":0,"y":0,"width":1920,"height":1080},
        "opacity":1.0,
        "framing":{"fit":"contain","crop":{"x":0.0,"y":0.0,"width":1.0,"height":1.0}}
      }]},
      {"id":"anime-overlay","clips":[
        {"id":"overlay-a","timeline_frames":{"start":24,"length":36},
         "asset":"sha256:generated-movie...","source_samples":{"start":0,"length":36},
         "cadence":{"kind":"source_presentation_time"},
         "destination":{"x":50,"y":50,"width":640,"height":360},"opacity":0.72},
        {"id":"overlay-b","timeline_frames":{"start":144,"length":48},
         "asset":"sha256:generated-png...","source_samples":{"start":0,"length":1},
         "cadence":{"kind":"hold","ordinal":0},
         "destination":{"x":50,"y":50,"width":640,"height":360},"opacity":0.55}
      ]}
    ],
    "audio":{"asset":"sha256:canonical-48k-stereo...","source_samples":{"start":0,"length":480000},
      "source_rate":48000,"channel_order":["L","R"],"gain":1.0,"pan":0.0},
    "opaque_background":{"rgba":[0,0,0,255]}
  }
}
```

The compiler expands each movie selection into `(asset, ordinal, PTS)` from the stored native presentation-sample index. A PNG has ordinal zero and no media PTS. The export request names only the immutable revision and intent:

```json
{"intent":"panja-full-film","revision":"sha256:revision...","timeline":"main",
 "profile":{"kind":"h264_aac_mp4","video_bitrate":16000000,"audio_bitrate":192000}}
```

```rust
let prepared = project.prepare_export(export_request)?;
let result = project.execute_plan(prepared.plan_id.clone())?;
assert_eq!(result.plan_id(), prepared.plan_id);
// project.export(export_request) is the one-call equivalent.
```

Effect adapters and tenant/GPU orchestration stay outside the native library. They import accepted, content-addressed movie/PNG representations with generation and transfer receipts. An uncertain local-GPU submission is reconciled before retry. The native export consumes the accepted source and cannot manufacture Panja review acceptance.

## Problem

The current plan has native source timing, framing, per-track overlap checks, and one identity 48 kHz stereo path, but `movie.rs` still sorts one adjacent picture track and uses a worker channel. Layers need semantic bottom-to-top order, sparse overlays, integer placement, opacity, and several source sessions at one frame. The design must keep AVFoundation lifetimes valid and preserve historical schema 2/3 hashes.

Candidate B makes the validated immutable evaluation plan the only input to native composition. Candidate A's persistent project aggregate remains the public owner of revisions, lineage, intents, and recovery; this plan is the private export execution boundary.

## Shape

```rust
pub struct DestinationRect { pub x: i32, pub y: i32, pub width: u32, pub height: u32 }
impl DestinationRect {
    pub fn new(x: i32, y: i32, width: u32, height: u32) -> Result<Self> { not_implemented!() }
    pub fn intersection(self, canvas: PixelExtent) -> Option<ClippedRect> { not_implemented!() }
}

#[serde(try_from = "f32")]
pub struct Opacity(f32); // constructor rejects NaN, infinity, and values outside 0..=1
pub struct PixelExtent { pub width: u32, pub height: u32 }
pub struct SourceSampleRef { pub asset: ContentHash, pub ordinal: u64, pub pts: Option<MediaTime> }
pub struct PictureUse {
    pub clip: EntityId, pub track: EntityId, pub track_index: u32,
    pub timeline_frames: Span, pub source: Vec<SourceSampleRef>,
    pub framing: Option<crate::Framing>, pub destination: DestinationRect,
    pub opacity: Opacity,
}
pub struct LayeredPicturePlan {
    pub canvas: PixelExtent,
    pub bottom_to_top: Vec<EntityId>,
    pub union_coverage: Vec<Span>,
    pub opaque_background: [u8; 4],
    pub picture: Vec<PictureUse>,
    pub budget: PictureBudget,
}
pub struct PictureBudget {
    pub max_open_decoders: u32, pub peak_required_decoders: u32,
    pub max_owned_picture_bytes: u64, pub peak_owned_picture_bytes: u64,
    pub inflight_frames: u32, // one initially
}
pub struct IdentityAudioPlan {
    pub asset: ContentHash, pub source_samples: Span, pub timeline_samples: Span,
    pub source_rate: u32, pub channels: u32, pub channel_order: Vec<String>,
    pub gain: f32, pub pan: f32,
}
pub enum OpaqueOutput { H264AacMp4 { video_bitrate: u32, audio_bitrate: u32 }, Png { frame: u64 } }
pub struct LayeredEvaluationPlan {
    pub project: EntityId, pub revision: ContentHash, pub timeline: EntityId,
    pub settings: crate::Settings, pub picture: LayeredPicturePlan,
    pub audio: Option<IdentityAudioPlan>, pub output: OpaqueOutput,
    pub source_closure: BTreeMap<ContentHash, StoredAsset>, pub renderer: BuildIdentity,
}
```

`DestinationRect` uses signed coordinates, positive bounded dimensions, checked `i64` ends, and canvas clipping. `Opacity` is clip-local and finite. The background alpha must be 255. The canvas is opaque, but a layer's `contain` bars are transparent coverage, so they reveal lower layers or the opaque background; `framing::apply`'s legacy black-bar behavior must not be reused for a sparse overlay. Initial sources are native movie representations and PNG; initial outputs are opaque H.264/AAC MP4 and opaque PNG. PNG alpha, alpha video, masks, color transforms, motion curves, typography, and audio effects are explicit unsupported capabilities here, not implicit fallbacks.

The plan compiler requires one complete identity audio use for movie output: measured 48,000 Hz, two channels, bound canonical range, unity gain, zero pan, and no resampling or mixing. PNG diagnostic output has no audio. Movie source codec support is selected through a native registry. Current evidence makes H.264 viable, AV1 conditional on complete indexing, and VP9 explicitly unsupported; a derived native representation must have its own hash and source mapping. There is no FFmpeg, libav, renderer subprocess, or old runtime fallback.

```rust
pub struct LayerCompileLimits { pub max_open_decoders: u32, pub max_owned_picture_bytes: u64 }
pub struct NativeCapabilitySnapshot { pub codec_registry: CodecRegistry, pub renderer: BuildIdentity }
pub fn compile_layered_plan(
    snapshot: Snapshot, request: &ExportRequest,
    host: &NativeCapabilitySnapshot, limits: LayerCompileLimits,
) -> Result<PreparedExport> { not_implemented!() }
```

Compilation validates the revision hash, lineage closure, track order, per-track non-overlap, union coverage, rectangle/opacity bounds, exact source ordinal/PTS maps, selected codec representation, PNG probe, and identity audio. An interval sweep computes peak active clip sessions. The compiler rejects a plan above decoder count or aggregate owned-picture bytes before opening media. The estimate includes copied movie/PNG pixels, PNG compressed and expanded bytes, destination scratch, one opaque canvas, and one handoff frame. It is a conservative owned-buffer estimate, not a claim about AVFoundation or encoder process memory.

### Lazy sessions and native lifetime

```rust
pub struct ClipSessionHandle { id: ClipSessionId, commands: SyncSender<SessionCommand> }
enum SessionCommand {
    Pull { expected: SourceSampleRef, reply: SyncSender<Result<OwnedPictureSample>> },
    Close { reply: SyncSender<Result<()>> }, Cancel,
}
pub struct OwnedPictureSample { pub observed: SourceSampleRef, pub pixels: crate::pixels::Pixels }
pub struct LayerEvaluator { plan: LayeredEvaluationPlan, sessions: BTreeMap<ClipSessionId, ClipSessionHandle>, control: ExportControl }
impl LayerEvaluator { pub fn render_frame(&mut self, frame: u64) -> Result<crate::pixels::Pixels> { not_implemented!() } }
```

The evaluator opens a session only when an active clip first needs a frame. It pulls one sample, checks ordinal and native PTS, places only the source content into the clipped destination rectangle, blends bottom to top, and releases the source lease before returning. A repeated hold reuses one owned sample. Session and reply channels have capacity one; the writer waits for readiness before pulling, so there is no per-track fanout or unbounded lookahead.

Each session owns a serial native queue. `AVURLAsset.loadTracksWithMediaType_completionHandler` is used as in the current `objc2_av_foundation` experiment. Its completion block captures only an owned session token, cancellation state, and queue handle. The callback retains the selected track and dispatches queue-owned initialization; the queue owns `AVAsset`, `AVAssetTrack`, `AVAssetReader`, and `AVAssetReaderTrackOutput` until reader termination. `CMSampleBuffer` and `CVPixelBuffer` are copied to `OwnedPictureSample` before any reply.

No raw pointer, borrowed track, sample buffer, or framework object enters a Rust channel. No `unsafe impl Send` is permitted for an AVFoundation object. If the binding cannot move `Retained<T>` through the dispatch block, initialization must complete synchronously while the callback borrow is valid, then return only a queue-local state token. `Close` cancels and drains the queue before dropping it; a generation token discards late callbacks. This is feasible with the current `objc2` reader, BGRA output, native PTS, and pixel-copy primitives, but the queue handoff and late-callback test are a blocking experiment.

Cancellation checks precede session open, every pull, every writer wait, every layer, and every audio block. Cancellation sends `Cancel` on each queue, calls `AVAssetReader.cancelReading()` there, then cancels `AVAssetWriter`; a staged output is not promoted. Export fencing and `PromotedUnreceipted` recovery remain project/exports responsibilities.

### Module map and interface depth

| Module | Ownership |
| --- | --- |
| `model` / `framing` | Immutable intent, lineage, source clocks, framing, integer placement and transparent coverage |
| `plan::layers` | Resolved order, source ordinal/PTS map, union, codec choice, audio, decoder/memory preflight |
| `platform::macos::codec` | Explicit AVFoundation capability and representation registry |
| `platform::macos::session` | Queue-confined AVFoundation sessions and cancellation |
| `render::layers` / `movie` | Opaque composition, bounded pull, native H.264/AAC writer, reopen verification |
| `project` / `exports` | Stable intents, staging, fencing, promotion, recovery and review evidence |
| Effect adapter boundary | Typed masks, color, motion, text, GPU and generated representations; no string parameters |

`Project::export`, `prepare_export`, and `execute_plan` are the only public operations needed. They hide decoder lifecycle, memory, backpressure, writer policy, and receipts. This avoids a shallow `open/read/blend/write` API, information leakage of AVFoundation types, temporal decomposition by public stages, and pass-through methods. The plan itself is content-addressed and immutable.

### Receipts and compatibility

Append `layered_picture: Option<LayeredPicturePlan>` and optional placement/opacity fields after existing `ExportPlan` fields, with `#[serde(default, skip_serializing_if = "Option::is_none")]`. When absent, schema 2/3 plans serialize identically and keep their hashes. New layered plans may use a new plan number, but do not rewrite old bodies. Keep the existing artifact receipt schema; append an optional `layered` evidence object only because it detects correctness that old receipts cannot: ordered track IDs, source ordinal/PTS observations, placement/opacity, union coverage, selected representation, and decoder/owned-buffer limits. Omit it for legacy exports. Do not add a second trace or a receipt version without a verifier need.

The receipt also binds plan, revision, output, renderer, source closure, audio identity, and cancellation/promotion state. It records owned-buffer estimates as estimates, never total process memory. Review records remain separate and exact-file bound; measurements cannot set watched, heard, playback, continuity, listening, or creative acceptance.

## Verification and first experiment

Compile tests cover bottom-to-top order independent of IDs, within-track overlap rejection, sparse union gaps, 50-pixel reposition, offscreen clipping, transparent contain bars, opacity boundaries, exact movie PTS mismatch, PNG ordinal zero, AV1 registry gating, VP9 rejection, identity audio, decoder bound, owned-memory bound, and schema 2/3 fixture hashes.

The first executable experiment composes a 24 fps H.264 or fully indexed supported AV1 background, sparse generated movie and PNG overlays, a 50-pixel offset, nontrivial opacity, and the canonical 48 kHz stereo PCM through the same Rust/AVFoundation writer. The preserved R23 export remains the H.264/AAC profile. A VP9 MP4 is a negative fixture. Independent readback must verify H.264/AAC, exact `n/24` PTS, 48,000 stereo presentation samples, encoded AAC trim, layer geometry/opacity, alpha 255 output, source ordinal/PTS equality, and no decoder or owned-memory budget exceedance. Cancel during a pull and during writer backpressure; verify queue termination, no promotion, and idempotent retry from the plan. Normal-speed playback and listening still remain required for full Panja hybrid acceptance.

## Synthesis decision

Use Candidate A's persistent aggregate for revisions, lineage, intent fencing, recovery, and review. Graft this Candidate B plan into export. Retain the native presentation-sample index and explicit representation map; retain generated receipts, canonical audio, and promoted-but-unreceipted recovery. Reject dangling graph roots, stringly typed effects, proxy substitution, nominal-rate source authority, and caller-coordinated renderer stages.

## Tradeoffs, alternatives, and risks

- We accept one-frame backpressure and bounded active sessions for auditable cancellation and memory.
- We accept rejection above explicit decoder or owned-buffer limits instead of promising an unmeasured native peak.
- One worker per track loses sparse union/order ownership and exposes stage coordination; eager all-clip readers waste memory. Both lose to lazy per-clip sessions.
- Passing framework objects through channels is rejected because lifetime and thread affinity become unverifiable.
- Can the pinned `objc2` bindings prove retained-track queue handoff without `unsafe Send`? Can target macOS fully index the required AV1 representation? These decide the next implementation gate.
- If alpha-bearing overlays are required, define an explicit alpha capability and flattening receipt before extending this unit.

## Next implementation step

Build only the isolated queue/session experiment and its independent MP4/PNG/audio readback; do not change runtime code until the lifetime, PTS, budget, cancellation, and review-boundary checks pass.
