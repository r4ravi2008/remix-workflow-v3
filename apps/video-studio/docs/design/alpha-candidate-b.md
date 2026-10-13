# Transparent PNG alpha — Candidate B

## Usage (caller's view)

The caller imports an image through the existing AssetImport path. The caller
does not author alpha facts, choose premultiplication, or construct a pixel
pipeline. Measurement derives those facts from the staged PNG bytes.

An overlay caller commits the existing snapshot shape. The overlay can use the
existing crop, fit, signed placement, motion, clip opacity, and mask fields.
Tracks remain stored bottom to top.

~~~rust
let revision = project.commit(CommitProject {
    intent: EntityId::parse("alpha-overlay-a01")?,
    base_revision: head.revision.clone(),
    imports: vec![
        AssetImport {
            path: PathBuf::from("h264-source-a14.mp4"),
            expected_hash: h264_hash,
            expected_bytes: h264_bytes,
            media_kind: MediaKind::Movie,
            origin: Origin::Imported,
            previous_measurement: None,
        },
        AssetImport {
            path: PathBuf::from("sparse-overlay-a01.png"),
            expected_hash: png_hash,
            expected_bytes: png_bytes,
            media_kind: MediaKind::Image,
            origin: Origin::Imported,
            previous_measurement: None,
        },
    ],
    canonical_audio: Some(canonical_audio),
    timelines: vec![timeline_with_movie_and_png_overlay],
})?;

let request = ExportRequest {
    intent: EntityId::parse("alpha-export-a01")?,
    revision: revision.revision.clone(),
    timeline: EntityId::parse("main")?,
    profile: MovieProfile::NativeColorMasterV1,
};
let prepared = project.prepare_export(request.clone())?;
let exported = project.export(request.clone())?;
let verified = project.verify_export(request.intent.clone())?;
assert_eq!(prepared.plan_id, exported.plan_id);
assert_eq!(verified.plan_id, prepared.plan_id);
~~~

The caller can also make an opaque project with the same existing request
shape. No alpha member is authored, schema 2 through 6 selection is unchanged,
and the historical document bytes remain the acceptance target.

~~~rust
let prepared = project.prepare_export(opaque_request.clone())?;
let result = project.export(opaque_request.clone())?;
let replay = project.export(opaque_request)?;
assert_eq!(result.receipt_id(), replay.receipt_id());
project.verify_export(EntityId::parse("opaque-export-a01")?)?;
~~~

Cancellation remains an aggregate operation. The caller does not cancel a
reader, worker, alpha scan, or native callback directly.

~~~rust
let prepared = project.prepare_export(request.clone())?;
let running = project.export_async(request)?;
let cancelled = project.cancel_export(running.intent.clone())?;
assert!(matches!(cancelled.state.as_str(), "cancelled" | "fenced"));
assert!(project.verify_export(running.intent).is_err());
~~~

Direct CLI callers map to these same five Project methods. Effect, GPU, and
Resolve adapters remain outside the editor boundary. An accepted PNG and its
source receipt can enter the project, but this unit does not claim managed
color, normal-speed watching, listening, or full Panja hybrid acceptance.

## Problem

The current image path measures straight RGBA only long enough to reject every
alpha value below 255. Removing that rejection leaves untyped BGRA buffers,
straight-alpha interpolation, opaque contain bars, and a preflight bit that
cannot distinguish active structure from visible contribution. Candidate B puts
the complete alpha decision inside one image/composition execution kernel. The
kernel owns measured intrinsic-alpha semantics, transformed sampling, opaque
canvas composition, visibility observations, and alpha-specific admission.
The caller keeps the existing project operations and never sees a pixel
representation.

## Shape

### Measured image facts

The staging boundary expands RGB, RGBA, grayscale-alpha, indexed transparency,
and RGB tRNS into straight eight-bit RGBA. It keeps strict PNG terminal, CRC,
APNG, 16-bit, regular-file, and byte-limit validation. The existing opaque
backend string remains unchanged for old descriptors.

New alpha-bearing imports use a separate backend string:

~~~text
Rust png 0.17.16 / straight RGBA static PNG decode
~~~

The existing warning remains truthful:

~~~text
Source sample values only; ICC, gamma, color conversion and creative acceptance remain unverified
~~~

The public model adds measured metadata, not pixel storage:

~~~rust
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ImageAlphaClass {
    Opaque,
    Sparse,
    FullyTransparent,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AlphaBounds {
    pub x: u32,
    pub y: u32,
    pub width: u32,
    pub height: u32,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct ImageAlphaFacts {
    pub class: ImageAlphaClass,
    pub min: u8,
    pub max: u8,
    pub zero_samples: u64,
    pub nonzero_samples: u64,
    pub non_opaque_samples: u64,
    pub nonzero_bounds: Option<AlphaBounds>,
    pub alpha_sha256: ContentHash,
}

// Existing Image fields remain in the same order. This field is absent for
// historical opaque descriptors and therefore does not change their bytes.
pub enum MediaDescriptor {
    Image {
        format: String,
        width: u32,
        height: u32,
        rgba_sha256: ContentHash,
        warnings: Vec<String>,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        alpha: Option<ImageAlphaFacts>,
    },
    // Movie and Audio are unchanged.
}
~~~

alpha_sha256 hashes only the row-major alpha bytes. rgba_sha256 continues to
hash straight RGBA bytes before channel-order conversion or premultiplication.
nonzero_bounds is a conservative source-space bound. It does not claim that
every pixel in the rectangle contributes.

Opaque is represented by alpha: None for old and newly authored opaque
imports. A newly measured varying-alpha PNG uses Some(Sparse) or
Some(FullyTransparent). The summary is regenerated at every prepare and
execution source check. A caller cannot provide or override it.

### Schema 7 binds the execution policy

Opaque plans keep the existing cumulative schema selector:

| Condition | Schema |
|---|---:|
| Movie cuts only | 2 |
| Image with no layered placement | 3 |
| Layered placement or multiple tracks | 4 |
| Motion | 5 |
| Mask | 6 |

If any selected image has ImageAlphaFacts, the compiler selects schema 7.
Schema 7 contains the same normalized VideoUse fields as schema 2 through 6,
including placement, motion, mask, and presentation_ordinals. It adds one
policy value and extends existing image decode evidence:

~~~rust
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum AlphaPolicyId {
    StraightRgbaPremulQ16V1,
}

pub struct ExportPlan {
    pub schema: u32,
    // Existing fields remain unchanged.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub alpha_policy: Option<AlphaPolicyId>,
    pub image_decode_evidence: Vec<ImageDecodeEvidence>,
}

pub struct ImageDecodeEvidence {
    pub asset: ContentHash,
    pub width: u32,
    pub height: u32,
    pub rgba_sha256: ContentHash,
    pub decoder_executable_sha256: ContentHash,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub alpha: Option<ImageAlphaFacts>,
}
~~~

Schema 7 requires alpha_policy and one matching alpha evidence entry for each
alpha-bearing image in the source closure. The evidence list is the one
per-asset execution binding; VideoUse does not duplicate an alpha trace.
Entries are sorted by asset hash. Schema 7 is rejected when no image has alpha,
when a schema 2 through 6 plan contains alpha, or when an alpha asset lacks
matching evidence.

plan::validate_picture_mapping_cancellable reconstructs the snapshot,
rechecks all uses, and compares the schema-7 policy and evidence with the
measured source descriptors. Project::replay_plan accepts schema 7 only after
the same checks. The plan document hash therefore binds source hash, straight
RGBA hash, alpha facts, source ordinals, PTS, crop, fit, placement, motion,
mask, and the selected math policy.

No receipt field is added. ArtifactReceipt schema 2 and schema 3 remain bound
to the unchanged output profile and the schema-7 plan hash. Alpha pixel
evidence is an execution and independent-observer concern, not a second
receipt trace.

### Private image/composition kernel

The caller-visible library exports no alpha pixel type, premultiplied raster,
coverage map, or native reader. These types stay private to image, composition,
and layers.

~~~rust
struct StraightRgba8 {
    width: u32,
    height: u32,
    bytes: Vec<u8>, // RGBA, straight, source-owned
}

struct OpaqueBgra8 {
    width: u32,
    height: u32,
    bytes: Vec<u8>, // BGRA, alpha is always 255
}

enum SourcePayload {
    OpaqueMovie(OpaqueBgra8),
    OpaqueImage(OpaqueBgra8),
    AlphaImage(StraightRgba8, ImageAlphaFacts),
}

struct SourceFrame {
    lineage: SourceLineage,
    payload: SourcePayload,
    permit: PicturePermit,
}

struct SourceLineage {
    clip: EntityId,
    track: EntityId,
    asset: ContentHash,
    timeline_frame: u64,
    presentation_ordinal: u64,
    source_pts: Option<MediaTime>,
}

struct OpaqueCanvas {
    width: u32,
    height: u32,
    bgra: Vec<u8>,
}

struct VisibilityObservation {
    structurally_active: bool,
    geometric_visible: bool,
    potential_alpha_visible: bool,
    effective_nonzero_pixels: u64,
    max_effective_alpha_q16: u16,
}

struct ComposedFrame {
    canvas: OpaqueCanvas,
    sources: Vec<SourceLineage>,
    visibility: Vec<VisibilityObservation>,
}

struct AlphaCompositionKernel {
    policy: AlphaPolicyId,
    admission: AlphaAdmission,
}

impl AlphaCompositionKernel {
    fn preflight(
        plan: &ExportPlan,
        source_closure: &BTreeMap<ContentHash, StoredAsset>,
        limits: AlphaLimits,
    ) -> Result<AlphaAdmission> { not_implemented!() }

    fn compose_frame(
        &mut self,
        frame: u64,
        workers: &mut TrackWorkers,
        cancel: &Cancellation,
    ) -> Result<ComposedFrame> { not_implemented!() }
}
~~~

TrackWorkers remains the existing maximum-four worker set with capacity-one
request and response channels. Each worker returns one copied SourceFrame for
the requested frame. The kernel pulls tracks in stored bottom-to-top order,
checks lineage, maps the source, blends into its one opaque canvas, and releases
the source permit before pulling the next frame. A static image cache can hold
one Rust-owned StraightRgba8 buffer for its clip interval; the cache never
contains an AVFoundation object.

The kernel is deep because it owns the policy that currently leaks across
image, framing, composition, mask, layers, and movie: association, sampling,
transformed coverage, source lineage, visibility, admission, and opaque output.
Project remains a five-operation surface. A caller does not learn any of those
internal choices.

### Exact sampling and composition

Opaque movie frames and OpaqueImage use the historical sampler and blend path
without entering the new alpha arithmetic. This preserves all 115 current
baselines, including opaque placement, motion, mask, contain-bar, and ordering
bytes. A schema-7 project may contain opaque uses; each such use still takes
this exact fast path.

AlphaImage uses an independent integer path. Existing pixel-center mapping and
signed clipping produce four source taps. The alpha kernel converts the
horizontal and vertical fractions to Q16 with round-half-up. The four
bilinear weights are Q32 products and sum exactly to 2^32.

For a source channel c and source alpha a, both in 0..=255:

~~~text
alpha_q16(a) = round_half_up(a * 65536 / 255)
premul_q16(c, a) = round_half_up(c * a * 65536 / 255)
sample_q16(v) = round_half_up(sum(v_i * weight_i) / 2^32)
q16_mul(x, y) = round_half_up(x * y / 65536)
clip_mask_q16 = q16_mul(clip_opacity_q16, mask_coverage_q16)
effective_alpha_q16 = q16_mul(sample_alpha_q16, clip_mask_q16)
effective_color_q16 = q16_mul(sample_premul_q16, clip_mask_q16)
output = round_half_up(
    (effective_color_q16
      + q16_mul(lower_channel * 65536, 65536 - effective_alpha_q16))
    / 65536
)
output alpha = 255
~~~

All products use u128. Round-half-up means floor((n + d/2) / d) for positive
integers. Every result is clamped to its declared range. A zero-alpha tap
produces zero premultiplied color before bilinear filtering, so vivid hidden
RGB cannot create a fringe. Clip opacity and mask coverage multiply both color
contribution and coverage.

The alpha kernel samples only the fitted picture window. It does not allocate
opaque black contain bars. Unused contain space leaves the lower canvas
untouched. Crop exclusion, signed off-screen placement, and mask inversion
therefore retain the current spatial semantics.

The final canvas is always opaque BGRA. kCVPixelFormatType_32BGRA is treated
as a byte layout, not as an alpha-association declaration. H.264/AAC and
NativeColorMasterV1 outputs both receive alpha 255 for every pixel. Transparent
movie output and alpha-preserving export are outside this plan.

### Visibility and source lineage

Preflight derives two separate unions:

- active_union: an active clip and its source ordinal exist;
- potential_visible_union: geometry, opacity, mask, and measured alpha facts
  make a contribution possible.

FullyTransparent never advances potential_visible_union. A sparse source
advances it only when its nonzero source bounds can intersect the transformed
picture window, canvas, and effective mask. This is a conservative possibility,
not an observation. If opacity is zero, the destination is fully clipped, or
the mask has no effective coverage, the possibility is false.

At runtime the kernel scans alpha-bearing taps and records
effective_nonzero_pixels and max_effective_alpha_q16. A zero result does not
become Decision::Gap. The worker still returns SourceLineage with image ordinal
zero and no PTS. The kernel only advances observed_visible_union for positive
effective coverage. An alpha-only source that is fully transparent cannot
satisfy required source coverage. A lower opaque movie or declared opaque
background can satisfy output coverage independently.

Movie workers retain every source ordinal and measured PTS check even when an
upper alpha layer hides their pixels. PNG sources never receive an invented
movie clock. The observer records active, potential, and observed visibility
separately, so a structural source record cannot masquerade as visible pixels.

### Admission, backpressure, and cancellation

~~~rust
struct AlphaLimits {
    max_workers: u8,              // 4
    max_owned_picture_bytes: u64, // existing 512 MiB logical cap
    max_source_bytes: u64,        // existing 128 MiB per owned picture
}

struct AlphaAdmission {
    workers: u8,
    canvas_bytes: u64,
    pending_canvas_bytes: u64,
    peak_source_bytes: u64,
    png_temporary_bytes: u64,
    tap_scratch_bytes: u64,
    total_owned_bytes: u64,
}
~~~

The admission calculation includes one current canvas, one pending handoff
canvas, one copied source lease per active worker, the compressed PNG plus
decoder allowance, and fixed four-tap scratch for each worker. The direct kernel
retains no premultiplied frame raster and no alpha plane. It still records
those fixed tap bytes in AlphaAdmission; no logical payload is free.

The existing 128 MiB per-source and 512 MiB aggregate limits remain
application-owned estimates. They do not claim total allocator, PNG decoder,
AVFoundation, Core Video, or encoder peak memory. A PicturePermit remains held
until its source bytes are blended or a cancelled response is dropped. There
are never more than four native source readers or one response per worker in
flight.

Cancellation is checked before each worker pull, native-ready wait, source
decode, and output row. compose_frame drops the source permit before returning
export_interrupted. Worker shutdown cancels and joins its callback-confined
reader. The native callback may return only copied Rust bytes, scalar timing,
and lineage; no AVAsset, AVAssetTrack, AVAssetReader, CMSampleBuffer,
CVPixelBuffer, or raw pointer crosses a channel or outlives its callback-owned
lifetime.

### Central validation and compatibility

Project::commit derives ImageAlphaFacts from immutable staged bytes. It
rejects a caller-provided descriptor mismatch before storing the revision.
prepare_export reopens the source closure, recomputes the straight RGBA and
alpha hashes, and compares dimensions, counts, bounds, backend, and facts.
movie::verify_inputs writes the matching schema-7 image evidence and its
producer identity before the plan hash is persisted.

Central plan validation rejects:

- a schema 7 plan without StraightRgbaPremulQ16V1;
- an alpha descriptor missing from image decode evidence;
- evidence whose asset, dimensions, RGBA hash, alpha hash, or facts differ;
- a changed PNG whose content hash no longer matches the source closure;
- schema 2 through 6 carrying alpha semantics;
- duplicate or unsorted alpha evidence;
- a FullyTransparent claim with a nonzero count or bounds;
- an Opaque claim that changes historical absent-field behavior.

Old Snapshot 1, Plan 2 through 6, Receipt 2/3, and store 4 documents are
deserialized with absent defaults and reserialized byte-for-byte unchanged.
No old descriptor gains alpha, no old plan gains alpha_policy, and no old
execution enters the kernel. legacy_hashes.rs remains a required guard.

### Module map

| Module | Ownership |
| --- | --- |
| project / model | Stage immutable bytes, store optional measured facts, and preserve Snapshot 1 |
| image | Strict PNG parsing, straight RGBA hash, alpha summary, and Rust-owned source bytes |
| plan | Schema 7 selection, alpha policy/evidence, source ordinals, and tamper checks |
| alpha_kernel inside composition | Private source association, Q16/Q32 sampling, alpha visibility, direct blend, and admission |
| framing / mask | Existing crop, fit, signed clipping, Q16 opacity, and mask semantics supplied to the kernel |
| layers | Four bounded workers, source requests, source lineage, permits, track order, and cancellation |
| movie | Native writer/readback, profile selection, plan dispatch, audio, and EOF evidence |
| native_format | Existing 32BGRA, H.264/AAC, ProRes/PCM24 contracts |
| independent observer | Separate executable for source-bound pixels, clocks, alpha=255 output, and receipt evidence |

This groups code by ownership rather than by load/transform/save execution
stages. layers schedules sources, but it does not reimplement alpha policy.
alpha_kernel is the single owner of association, transformed coverage, and
composition.

## Synthesis decision

This standalone Candidate B chooses a private image/composition execution
kernel. Its decisive boundary is the kernel's SourcePayload and opaque
OpaqueCanvas; no generalized pixel pipeline crosses the public project API.
The plan carries only measured, source-bound alpha facts and one named math
policy. The kernel carries every representation needed to execute those facts.

The shape concentrates the hard decisions behind the smallest caller surface:
the caller still commits a timeline and calls the existing prepare/export,
cancel, and verify operations. It also keeps old opaque paths byte-identical
by selecting the historical arithmetic per source, even inside a schema-7
project.

## Tradeoffs accepted

- We accept direct per-pixel alpha sampling in exchange for no retained
  premultiplied raster or alpha plane.
- We accept one schema-7 policy and evidence binding in exchange for keeping
  schemas 2 through 6 and all old hashes unchanged.
- We accept an application-owned memory estimate in exchange for the existing
  bounded permits; it does not promise total process memory.
- We accept runtime visibility observations instead of persisted pixel receipts
  in exchange for unchanged ArtifactReceipt schemas.
- We accept source-sample-value arithmetic in exchange for truthful
  source-sample-values-unmanaged limits and no false managed-color claim.
- We accept the same four-worker scheduling boundary in exchange for
  callback-confined AVFoundation lifetimes and bounded backpressure.

## Alternatives considered

- A public PixelPipeline with straight, premultiplied, and canvas types lost on
  interface depth. It makes every caller and adapter learn association,
  coverage, and memory rules.
- Adding an alpha byte to the existing public Raster lost on information
  leakage and opaque drift. It leaves hidden-color filtering and contain-bar
  policy scattered across image, composition, and framing.
- A dense per-asset alpha plane or per-frame raster cache lost on ownership.
  Transformed crops and masks make cached visibility stale, and the cache adds
  large permits without improving the public contract.
- Reusing schema 6 with optional alpha fields lost on durable validation.
  Historical readers would see a mask-shaped document with an unversioned
  arithmetic policy, and no-alpha hashes would become easier to perturb.
- Switching all output to ProRes 4444 lost on scope. Codec capability does not
  prove alpha composition, and this unit still writes an opaque canvas.

## Open questions and risks

These are implementation checks with chosen resolutions. They do not request a
human design checkpoint or defer the shape below.

- Can the existing objc2 AVFoundation binding retain a reader through its
  callback queue without a borrowed object escaping? The implementation must
  prove queue ownership and late-callback cancellation before enabling the
  path; a pointer escape is a rejected implementation.
- Does the fixed Q16 tap quantization remain stable on every supported host?
  The pure vector suite must compare exact bytes and freeze the mapping
  conversion before native proof.
- Does direct sampling meet the required throughput for large sparse PNGs?
  Measure it after correctness. A slower kernel does not justify a second
  unbounded raster cache.
- What is the whole-process PNG peak? It remains unclaimed until measured;
  logical admission must continue to name only owned buffers and allowances.
- The A11 source archive is still pending. The native fixture must bind a fresh
  measured movie and PNG before the proof is called complete.

## Decisive proof plan

The pure reference is separate from alpha_kernel and uses exact integer vectors
for hidden-color fringes, zero-alpha hidden RGB, independent source
alpha/clip/mask weights, opaque equivalence, contain transparency, crop
exclusion, signed clipping, bottom-to-top order, fractional mask edges, and a
fully transparent active source. It covers RGBA, grayscale-alpha, indexed
transparency, and RGB tRNS expansion. It keeps strict terminal-boundary and
CRC negatives.

The native fixture uses the freshly measured preserved H.264 movie
h264-source-a14.mp4 on a lower track and a new asymmetric RGBA PNG on an upper
sparse interval. It exercises frames before, during, and after the overlay,
crop, contain fit, signed placement, motion, clip opacity, mask coverage,
movie source ordinals/PTS, PNG ordinal zero with no PTS, and one 48-kHz stereo
unity audio interval.

The NativeColorMasterV1 path remains the strict pixel proof: native readback
uses the existing 34 dB every-ROI/exact-PCM policy. The preserved H.264 path
is a technical opaque-output control and does not pass the NativeMaster region
gate or establish managed color. Both outputs must explicitly observe alpha
255 on every decoded canvas pixel.

A separate observer binds fresh source bytes, Snapshot, schema-7 plan,
producer, receipt, output hash/bytes, every output frame and PTS, EOF, source
ordinals, PCM codes, and profile. It is independently built from the product
verifier. Negative controls are declared before execution for straight-alpha
interpolation, ignored alpha, reversed order, opaque contain bars, asymmetric
weight application, missing zero-alpha lineage, forged alpha facts, forged
schema/evidence, and changed PNG bytes with preserved text. Technical proof
remains separate from watching, hearing, managed-color review, and creative
approval.

## Red-flag screen

- Shallow module: rejected. The kernel hides sampling, association,
  visibility, admission, and blend policy behind two private operations.
- Information leakage: rejected. Only measured facts and a policy identifier
  cross the plan boundary. Straight, premultiplied, native, and canvas storage
  stay private.
- Temporal decomposition: rejected. image owns measurement and source bytes;
  alpha_kernel owns alpha semantics; layers owns worker scheduling. The modules
  are separated by knowledge, not by sequential stages.
- Pass-through methods: rejected. Existing Project methods remain the aggregate
  boundary. No public alpha executor or secondary trace is added.
- False visibility: rejected. Active, potential, and observed unions are
  separate, and a fully transparent source never advances visible coverage.
- Native lifetime escape: rejected. Channels carry copied Rust payloads and
  scalar lineage only; framework objects remain callback-confined.

## Next implementation step

Implement ImageAlphaFacts and the private StraightRgba8/OpaqueBgra8 boundary
first, add schema-7 serde and central validation, then lock the pure integer
vectors before wiring the row-cancellable kernel into layers.
