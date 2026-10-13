# Candidate A: bounded track workers and ordered canvas composition

## Usage (caller's view)

The caller still commits one timeline and requests one movie export.
`video_tracks` defines picture order from bottom to top.
Clips may overlap across tracks.
Clips within one track cannot overlap.

This request shifts the base movie 50 pixels right.
The canvas clips the movie's right edge.
The PNG overlay is sparse and uses a shared 1600 by 900 picture window.

```json
{
  "intent": "commit-layered-main-v1",
  "base_revision": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "imports": [],
  "canonical_audio": {
    "asset": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
    "source_samples": { "start": 0, "length": 480000 },
    "source_rate": 48000,
    "channel_order": ["left", "right"],
    "channel_order_basis": "measured-stereo"
  },
  "timelines": [{
      "id": "main",
      "frame_count": 240,
      "video_tracks": [
        {
          "id": "base-picture",
          "clips": [{
              "id": "base-movie",
              "timeline_frames": { "start": 0, "length": 240 },
              "asset": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
              "source_samples": { "start": 0, "length": 240 },
              "cadence": { "kind": "source_presentation_time" },
              "framing": {
                "fit": "cover",
                "crop": { "x": 0.0, "y": 0.0, "width": 1.0, "height": 1.0 }
              },
              "placement": {
                "destination": { "x": 50, "y": 0, "width": 1920, "height": 1080 },
                "opacity": 1.0
              }
          }]
        },
        {
          "id": "sparse-overlay",
          "clips": [{
              "id": "conditioned-anchor",
              "timeline_frames": { "start": 72, "length": 48 },
              "asset": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
              "source_samples": { "start": 0, "length": 1 },
              "cadence": { "kind": "hold", "ordinal": 0 },
              "framing": {
                "fit": "contain",
                "crop": { "x": 0.0, "y": 0.0, "width": 1.0, "height": 1.0 }
              },
              "placement": {
                "destination": { "x": 160, "y": 90, "width": 1600, "height": 900 },
                "opacity": 0.75
              }
          }]
        }
      ],
      "audio_tracks": [{
          "id": "canonical-audio",
          "clips": [{
              "id": "song",
              "timeline_samples": { "start": 0, "length": 480000 },
              "asset": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
              "source_samples": { "start": 0, "length": 480000 },
              "source_rate": 48000,
              "gain": 1.0,
              "pan": 0.0
          }]
      }]
  }]
}
```

The source assets already exist in the committed revision.
New imports use the current immutable import and origin fields.

Callers create a common picture window by reusing one destination rectangle.
Changing `x` from `160` to `210` repositions one clip 50 pixels right.
Sampling stays relative to the full destination rectangle before canvas clipping.

The export request is unchanged.

```json
{
  "intent": "export-layered-main-v1",
  "revision": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
  "timeline": "main",
  "profile": {
    "kind": "h264_aac_mp4",
    "video_bitrate": 12000000,
    "audio_bitrate": 192000
  }
}
```

```sh
video-studio project.commit ./state panja layered-commit.json
video-studio project.export ./state panja layered-export.json
video-studio project.verify-export ./state panja export-layered-main-v1
```

The artifact receipt remains schema 2.
Its existing `plan_id` binds the output to the schema 4 layered plan.
Its technical fields cannot claim watched, heard, or creative approval.

## Problem

The native writer currently accepts adjacent clips on one picture track.
Layers add concurrent readers, ordered blending, sparse tracks, and more memory pressure.
The design retains exact timing, lineage, historical hashes, and one unity 48 kHz stereo clip.
This unit supports opaque PNG and natively decoded movies.
It uses no FFmpeg, libav, subprocess, GPU job, or Resolve mutation.

## Typed sketch

### Stored model and plan

```rust
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PixelRect {
    pub x: i32,
    pub y: i32,
    pub width: u32,
    pub height: u32,
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
#[serde(try_from = "f32", into = "f32")]
pub struct Opacity(f32);

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PicturePlacement {
    pub destination: PixelRect,
    pub opacity: Opacity,
}

pub struct VideoClip {
    // Existing id, timing, asset, cadence, and framing fields stay unchanged.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub placement: Option<PicturePlacement>,
}

pub struct VideoUse {
    // Existing clip, track, timing, asset, ordinal, and framing fields stay unchanged.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub placement: Option<PicturePlacement>,
}
```

`x` and `y` are signed integers.
Width and height must be positive and fit the existing 128 MiB BGRA extent limit.
Checked endpoints allow canvas clipping on every edge.

`Opacity` accepts only finite values in the closed interval `0..=1`.
The compiler rounds it once to an unsigned 16-bit blend weight.

`placement` is optional only for stored compatibility.
A schema 4 timeline requires placement on every picture clip.
One legacy track with all placements absent retains schema 2 or 3 behavior.
Mixed explicit and absent placement is invalid.

Track vector order is the only z-order.
Existing validation continues to reject same-track overlap.

### Private execution types

```rust
const MAX_TRACK_WORKERS: usize = 4;
const MAX_ADMISSION_ESTIMATE: u64 = 512 * 1024 * 1024;
const CHANNEL_CAPACITY: usize = 1;

struct CompiledPicturePlan {
    tracks_bottom_to_top: Vec<TrackProgram>,
    union_temporal_coverage: Vec<Span>,
    admission: PictureAdmissionEstimate,
}

struct TrackProgram {
    ordinal: u16,
    id: EntityId,
    clips_by_start: Vec<LayerProgram>,
}

struct LayerProgram {
    clip: EntityId,
    timeline_frames: Span,
    asset: ContentHash,
    selected_presentations: Vec<SourcePresentation>,
    framing: Option<Framing>,
    destination: PixelRect,
    opacity_u16: u16,
}

enum SourcePresentation { Movie { ordinal: u64, pts: MediaTime }, ImageHold { ordinal: u64 } }

struct PictureAdmissionEstimate {
    worker_count: u16,
    spawned_picture_threads: u16,
    estimated_bytes: u64,
}

struct AccountedOpaquePixels {
    pixels: OpaquePixels,
    _permit: PictureMemoryPermit,
}

enum TrackDecision { Empty { timeline_frame: u64, track_ordinal: u16 }, Layer(LayerRaster) }

struct LayerRaster {
    timeline_frame: u64,
    track_ordinal: u16,
    source: SourcePresentation,
    bounds: CanvasRect,
    pixels: AccountedOpaquePixels,
    opacity_u16: u16,
}

struct ComposedFrame { timeline_frame: u64, pixels: AccountedOpaquePixels }
```

`OpaquePixels` verifies that every decoded input alpha byte is 255.
PNG import already checks this; movie execution checks each selected BGRA frame.

`LayerRaster` contains only covered source pixels.
For `contain`, unused bars produce no pixels and reveal lower tracks.
This differs intentionally from the legacy single-track black matte.
`cover` and `stretch` fill the destination rectangle.
All modes rasterize only the canvas intersection and apply opacity only to covered pixels.

## Signatures and data flow

The public `Project` interface does not change.

```rust
impl Project {
    pub fn commit(&self, request: CommitProject) -> Result<RevisionReceipt>;
    pub fn prepare_export(&self, request: ExportRequest) -> Result<PreparedExport>;
    pub fn export(&self, request: ExportRequest) -> Result<StoredArtifact>;
    pub fn cancel_export(&self, intent: EntityId) -> Result<CancelExportReceipt>;
    pub fn verify_export(&self, intent: EntityId) -> Result<VerifiedArtifact>;
}
```

Planning and execution gain private functions.

```rust
// model.rs
impl PixelRect { fn validate(&self) -> Result<()>; }
impl PicturePlacement { fn validate(&self) -> Result<()>; }

// plan.rs
fn compile_picture(plan: &ExportPlan) -> Result<CompiledPicturePlan>;
fn union_visible_coverage(tracks: &[TrackProgram], frame_count: u64) -> Result<Vec<Span>>;

// framing.rs
fn rasterize_layer(
    source: &AccountedOpaquePixels,
    framing: Option<&Framing>,
    destination: PixelRect,
    canvas: CanvasExtent,
) -> Result<Option<(CanvasRect, AccountedOpaquePixels)>>;

// pixels.rs
fn blend_opaque_bgra(canvas: &mut AccountedOpaquePixels, layer: LayerRaster) -> Result<()>;

// movie.rs
fn preflight_picture(plan: &ExportPlan) -> Result<CompiledPicturePlan>;
fn start_picture_pipeline(program: CompiledPicturePlan, blobs: &Path, control: ExportControl)
    -> Result<PicturePipeline>;
fn run_track_worker(
    program: TrackProgram,
    requests: CancellableReceiver<FrameRequest>,
    responses: CancellableSender<Result<TrackDecision>>,
    image_decode_permit: Arc<Semaphore>,
    control: ExportControl,
) -> Result<()>;
fn run_compositor(tracks: Vec<TrackWorkerPort>, output: CancellableSender<Result<ComposedFrame>>,
    control: ExportControl) -> Result<()>;

impl PicturePipeline {
    fn try_next(&mut self) -> Result<Option<ComposedFrame>>;
    fn finish(self) -> Result<()>;
    fn cancel_and_join(self, cause: StudioError) -> StudioError;
}
```

`plan::compile` selects schema 4 for two nonempty picture tracks.
Any explicit placement also selects schema 4.
The compiler rejects more than four contributing tracks before decoding.

The plan preserves exact output and source presentation lineage:

```text
output frame and exact n / frame-rate PTS
  -> timeline track order and active VideoUse
  -> presentation_ordinals[clip-local frame]
  -> stored source sample ordinal and exact PTS
  -> source asset hash, Origin ranges, framing, placement, and opacity
```

No second execution trace duplicates this mapping.
Workers return their frame, track, ordinal, and PTS with each raster.
The compositor checks those values against the compiled plan before blending.

The coverage function merges visible clip spans across every track.
Sparse overlay gaps are valid when another layer covers those times.
Effective zero opacity and an empty canvas intersection contribute no coverage.
The union must equal `[0, timeline.frame_count)` for this unit.

The compositor starts with opaque black, requests one frame per track, and consumes bottom-to-top.

For each covered BGRA channel, it uses this operation:

```text
out = (source * weight + destination * (65535 - weight) + 32767) / 65535
alpha = 255
```

The plan also requires one complete 48 kHz stereo clip at unity gain and zero pan.

## Native ownership, cancellation, and backpressure

Each contributing track gets one dedicated Rust worker.
The worker owns its clip cursor, one active `AVAssetReader`, and one active held PNG.

The worker creates and cancels readers on its thread.
It copies `CVPixelBuffer` bytes before channel delivery.
Objective-C reader and pixel-buffer objects do not cross worker boundaries.

The compositor owns z-order and canvas mutation.
The existing writer pump receives composed BGRA through its pixel-buffer adaptor.

At most four workers and one compositor thread are spawned.
This bound covers Rust-created picture threads.
AVFoundation may use private framework threads.

Every channel has capacity one, so writer readiness propagates backpressure to each worker.
No worker decodes more than one requested frame ahead.

Preflight computes a conservative admission estimate before any reader opens:

```text
three canvas BGRA payloads
+ one maximum source BGRA payload per track
+ one maximum visible layer payload per track
+ one maximum compressed PNG file
+ one maximum expanded PNG sample buffer
+ the configured 128 MiB PNG decoder allowance
```

Checked arithmetic rejects estimates above 512 MiB.
Application-created picture payloads require a `PictureMemoryPermit` before allocation.
One semaphore serializes PNG decoding across workers.

The estimate is not a total process-memory guarantee.
Allocator overhead and vector capacity can differ from payload length.
The PNG crate can retain internal metadata and decompressor storage.
AVFoundation and Core Video own native memory outside this estimate.

Channel timeout loops check `ExportControl`.
Workers also check before opening sources and copying samples.

The first error interrupts the shared control and stops new requests.
Reader guards call `cancelReading` for active movie readers.
The pipeline closes channels and joins every worker before stage cleanup.

Cancellation, lease loss, timeout, and writer failure use this path.
No failed attempt promotes a receipt; same-intent retry uses fenced recovery.

A stalled native framework call cannot be forcibly stopped by Rust.
The existing native operation deadline remains necessary.

## Module map

| Module | Ownership |
|---|---|
| `model.rs` | Rectangle and opacity types; placement validation; same-track overlap |
| `plan.rs` | Schema selection; exact samples; track order; union coverage; admission estimate |
| `framing.rs` | Crop, fit, signed placement, and transparent `contain` bars |
| `pixels.rs` | Opaque BGRA values, memory permits, and deterministic blend arithmetic |
| `image.rs` | Complete opaque PNG decoding and decoder limits |
| `movie.rs` | Bounded workers, ordered compositor, AVFoundation readers, and writer pump |
| `exports.rs` | Fencing, cancellation, promotion, existing receipt, and replay verification |
| `project.rs` | Persistent aggregate, immutable revisions, and plan lookup |
| CLI | JSON, signals, deadlines, and exit codes |
| Effect adapter | Tenant authorization and external GPU job reconciliation |

Generated assets retain their existing `Origin::Generated` ancestry.
This unit never submits or retries a local GPU job.
The Effect adapter reconciles its attempt before importing an output.

## Schema and receipt compatibility

New compatibility fields appear last.
Both use `default` and `skip_serializing_if = "Option::is_none"`.
Existing fields keep their order and representation.

- Snapshot schema 1 has no `VideoClip.placement`.
- Layered revisions use snapshot schema 2.
- Export plan schemas 2 and 3 have no `VideoUse.placement`.
- Layered exports use plan schema 4 with placement on every `VideoUse`.
- Artifact receipts remain schema 2 for every plan schema.
- `ArtifactReceipt.plan_id` binds the exact schema 4 plan.
- `NativeMeasurements` remains unchanged.

Old snapshots, schema 2 plans, schema 3 plans, and schema 2 receipts reserialize identically.
Their content hashes therefore remain unchanged.
The legacy schema 2 and 3 render path also remains unchanged.

A second trace or new receipt schema would only repeat producer-owned plan facts.
It would not independently prove the blended pixels.
Exact compositor fixtures and reopened-output checks provide the useful independent evidence.

## Verification required before completion

### Pure model, plan, and pixel checks

- Reject same-track overlap and allow cross-track overlap.
- Preserve bottom-to-top track order through compilation.
- Reject missing placement, invalid rectangles, and non-finite opacity in schema 4.
- Prove signed clipping and a 50-pixel reposition without rescaling.
- Prove transparent `contain` bars preserve the lower track.
- Prove common-window placement with exact synthetic pixels.
- Prove opacity weights 0, midpoint, and 65535 with exact bytes.
- Compare pre-encode frames with an independent scalar reference compositor.
- Merge sparse coverage without double-counting overlapping tracks.
- Reject incomplete union coverage before decoding.
- Reject non-opaque selected movie frames.

### Scheduling, native media, and recovery

- Observe no more than five Rust picture threads and capacity-one channels.
- Reject an oversized admission estimate before PNG or movie decoding.
- Cancel workers at each wait boundary; confirm joins and no completed receipt.
- Retry the same intent through fenced recovery.
- Reject `native_decode: false` without another codec or representation fallback.
- Exercise concurrent independent `AVAssetReader` instances on the target macOS build.

Use two overlapping movie tracks, one sparse PNG, and canonical audio.
Reopen the H.264/AAC MP4 through AVFoundation.
Check every PTS, frame count, dimensions, complete decode, and 48 kHz stereo audio correlation.

Keep golden schema 2 movie plans, schema 3 image plans, and schema 2 receipts.
Reserialize them byte-for-byte and preserve their current hashes.
Audit the implementation for FFmpeg, libav, and subprocess calls.

These bounded fixtures do not establish maximum throughput or total Rust and native memory.
They also exclude color, orientation, aperture, sample aspect, and full Panja hybrid acceptance.

The exact Panja artifact needs complete technical verification, normal-speed playback, listening, and creative review.
Those reviews remain bound to exact revision, plan, renderer, and output hashes.

## Rationale

### Shape

The persistent `Project` aggregate remains the only public editing authority.
One export call hides native stages, recovery, and verification.

Workers own sequential track state; the compositor merges in timeline order.
This follows `separate-before-serializing-shared-state`.

The model validates geometry and opacity; the executor trusts checked types.
This follows `boundary-discipline` and `encode-lessons-in-structure`.

Track order, ordinals, PTS, and origins remain single sources of truth.
Coverage is derived, keeping the interface deep and small.

The timeline models any ordered track count.
Four workers is an executor limit, not a wire-level editor limit.

### Synthesis decision

This is Candidate A for the layered-picture arena.
It recommends bounded per-track readers and one ordered compositor.
Parent synthesis remains pending.

### Tradeoffs accepted

- We accept four active tracks in exchange for a fixed Rust thread bound.
- We accept a 512 MiB estimate ceiling in exchange for rejection before decoding.
- We accept serialized PNG decoding in exchange for one decoder allowance.
- We accept fixed-point opacity in exchange for deterministic blend rounding.
- We accept opaque inputs in exchange for avoiding alpha representation ambiguity.
- We accept transparent schema 4 `contain` bars in exchange for correct lower-layer visibility.
- We accept coded BGRA arithmetic in exchange for a bounded first composition unit.

### Alternatives considered

**One serial decoder for all tracks.**
It couples decode order to composition order and stalls unrelated sources.

**One unrestricted worker per clip.**
It makes thread and memory growth follow edit size.

**AVMutableVideoComposition or Core Animation.**
They add another timeline model and weaken sample assertions and backpressure control.

**Public decode, blend, and encode stages.**
That surface leaks native execution details; the aggregate is deeper.

### Red-flag screen

- **Shallow module:** `Project::export` completes the operation behind one call.
- **Information leakage:** Readers, channels, permits, and blend weights remain private.
- **Temporal decomposition:** Modules follow timing, pixels, framing, framework, or persistence knowledge.
- **Pass-through method:** The CLI adds process policy and exposes no renderer stages.

### Open questions and risks

- Do concurrent independent AVAssetReader instances behave reliably on every supported macOS build?
- Which measured fixtures should justify higher worker or estimate limits?
- Which color and orientation contract should replace coded BGRA composition?
- What native-memory telemetry is required before long Panja renders?
- Should a later alpha unit start with straight alpha, premultiplied alpha, or explicit masks?

### Next implementation step

Add placement types, hash-compatibility fixtures, and pure transparent-compositor tests first.
