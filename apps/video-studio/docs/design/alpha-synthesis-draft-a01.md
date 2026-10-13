# Transparent PNG synthesis draft A01

Status: proposed implementation contract. Independent design judgment remains pending.
No runtime, existing proof, provider, Resolve, GPU, or film project changed for this draft.

## Problem and caller usage

The existing editor imports opaque static PNGs. Its image decoder, sampled raster and blender reject intrinsic transparency.
The new unit must reveal lower tracks through PNG alpha while preserving historical opaque bytes and pixels.

The caller uses the existing Project operations and VideoClip fields. Import measurement determines alpha semantics.
`alpha_import` below binds the caller's real PNG hash and byte count. It is an AssetImport with MediaKind::Image.
The caller does not construct alpha facts, sampled pixels or a new execution API.

```rust
let committed = project.commit(CommitProject {
    intent: EntityId::parse("alpha-commit-a01")?,
    base_revision: head.revision,
    imports: vec![movie_import, alpha_import, canonical_audio_import],
    canonical_audio: Some(canonical_audio_binding),
    timelines: vec![timeline_with_lower_movie_and_upper_png],
})?;
let request = ExportRequest {
    intent: EntityId::parse("alpha-export-a01")?,
    revision: committed.revision,
    timeline: EntityId::parse("alpha-native-proof")?,
    profile: MovieProfile::NativeColorMasterV1,
};
let prepared = project.prepare_export(request.clone())?;
let result = project.export(request.clone())?;
assert_eq!(prepared.plan_id, result.receipt.artifact.plan_id);
let reopened = project.verify_export(request.intent.clone())?;
assert_eq!(result.receipt.receipt_id, reopened.receipt.receipt_id);
```

An opaque project uses those same calls. Its plan schema and serialized document bytes remain unchanged.
Cancellation remains synchronous `cancel_export` against a concurrently running synchronous `export` owner.
`cancellation_requested` acknowledges the flag. The caller waits for that exporter to exit before treating cancellation as terminal.

The overlay uses existing crop, fit, signed placement, motion, opacity and mask fields. Track order remains bottom to top.
PNG lineage has presentation ordinal zero and no PTS, including a fully transparent active image.

## Base and graft

Proposed base: Candidate A's copied premultiplied UNORM16 raster.
The existing workers finish sampling before sending owned rasters. The compositor alone owns the output canvas.
This preserves opaque sampling, native movie-reader ownership and current bounded channel behavior.

Graft Candidate B's single plan policy and per-asset alpha binding. Do not duplicate alpha identities on VideoUse.
The VideoUse asset key already selects a measured source and its evidence. Central validation checks that relationship.

Do not adopt B's new source-response protocol, acknowledgement channels, H.264-only registry or native callback redesign.
Those changes are unnecessary for copied rasters and restrict existing measured movie support.
Remove Candidate A's external use of crate-private StudioError::new. Project already owns asset-kind validation.

## Persisted contract

Snapshot remains schema 1. Store remains schema 4. ArtifactReceipt remains schema 2 or 3 according to output profile.
VideoClip and VideoUse authoring fields remain unchanged.

MediaDescriptor::Image gains one final skipped optional field:

```rust
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ImageAlphaV1 {
    pub schema: u32, // exactly 1
    pub alpha_sha256: ContentHash,
    pub minimum: u8,
    pub maximum: u8,
    pub nonzero_pixels: u64,
    pub nonopaque_pixels: u64,
}
// On MediaDescriptor::Image:
#[serde(default, skip_serializing_if = "Option::is_none")]
alpha: Option<ImageAlphaV1>
```

The decoder hashes expanded straight RGBA8 before channel swapping or premultiplication.
It also hashes row-major alpha bytes with an incremental hasher, without allocating a separate alpha plane.
Measured facts are present exactly when any alpha byte is below 255. All-255 images keep the old descriptor and backend bytes.
New alpha images use `Rust png 0.17.16 / straight RGBA8 alpha v1`.
The existing unmanaged-source warning remains exact.

Facts require schema 1, ordered extrema, bounded counts, a positive nonopaque count and coherent zero/full-alpha extrema.
Decoding recomputes all facts from immutable source bytes. Structural checks never substitute for that equality.

ExportPlan gains one final skipped optional policy:

```rust
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AlphaPolicy { StraightRgbaPremulUnorm16Q16V1 }
// On ExportPlan:
#[serde(default, skip_serializing_if = "Option::is_none")]
pub alpha_policy: Option<AlphaPolicy>
// On ImageDecodeEvidence:
#[serde(default, skip_serializing_if = "Option::is_none")]
pub source_alpha_id: Option<ContentHash>
```

Private SourceAlphaIdentityV1 serializes schema 1, compressed asset hash, straight rgba_sha256 and measured ImageAlphaV1.
ContentHash::document hashes that exact private document. Its identity excludes producer identity; the evidence already binds its decoder build.

The compiler selects Plan7 exactly when a directly used image has measured alpha.
An unused alpha ancestor in the source closure cannot select Plan7 by itself.
Plan7 supports current placement, motion and mask normalization, whether each optional field is present or absent.
Without directly used alpha, retain the exact current Plan2–6 selection rules, evidence ordering and serialization.

For Plan7, image evidence is sorted and unique by used image asset hash.
Each alpha image has the recomputed source_alpha_id. Opaque image evidence has None.
An alpha binding on a movie, missing binding, wrong identity, wrong policy or noncanonical schema fails central validation.
Plan2–6 cannot directly use alpha or carry alpha policy/evidence semantics.
Plan7 with no directly used alpha is invalid.

## Private representation and ownership

```rust
pub(crate) enum DecodedPicture {
    LegacyOpaque(Pixels), // owned BGRA8, alpha=255
    StraightAlpha(StraightRgba8),
}
pub(crate) struct StraightRgba8 {
    width: u32,
    height: u32,
    rgba: Vec<u8>,
}
#[derive(Clone, Copy)]
pub(crate) struct PremulBgra16 {
    b: u16,
    g: u16,
    r: u16,
    coverage: u16,
}
pub(crate) struct AlphaRaster16 {
    bounds: Bounds,
    pixels: Vec<PremulBgra16>,
}
pub(crate) enum SampledLayer {
    NoGeometry,
    ZeroAlpha { bounds: Bounds },
    LegacyOpaque { raster: Raster, permit: Permit },
    AlphaV1 { raster: AlphaRaster16, permit: Permit },
}
```

StraightRgba8 constructors validate extent and keep fields private to the alpha representation owner.
PremulBgra16 occupies exactly eight bytes; compile-time or unit checks guard the representation charge.
Sampling checks that each premultiplied channel does not exceed its coverage.
The opaque native writer receives only Pixels with alpha 255.

The image worker owns exactly one source cache and source permit for a clip use.
Each sampled response owns copied raster pixels and its raster permit. Source bytes never cross its channel.
The worker releases the source cache only after completing the last owned raster. It can then send that raster safely.
A zero-alpha response retains Source lineage and drops its unused raster permit after sampling establishes zero coverage.
No source-response acknowledgement or shared mutable pixel storage is needed.

Movie workers retain the existing callback-confined reader, frame-copy, source PTS and sampled-raster ownership.
AVFoundation objects and raw pointers do not cross channels. No codec representation is silently substituted.

## Exact arithmetic

Use unmanaged encoded sample values. PNG alpha represents opacity; this unit performs no gamma, ICC or transfer conversion.
For nonnegative integers define `round(n/d) = (n + d/2) / d`.

For straight color C8 and alpha A8:

```text
C16 = C8 * 257
A16 = A8 * 257
P16 = round(C16 * A16 / 65535)
```

The existing Mapping determines crop-clamped x0/x1/y0/y1 and f64 fractions fx/fy with current pixel-center geometry.
The alpha branch alone quantizes fractions:

```text
fxq = clamp(round(fx * 65536), 0, 65536)
fyq = clamp(round(fy * 65536), 0, 65536)
w00 = (65536-fxq)*(65536-fyq)
w10 = fxq*(65536-fyq)
w01 = (65536-fxq)*fyq
w11 = fxq*fyq
sample16 = round(sum(wij * Vij) / 2^32)
```

The four weights sum exactly to 2^32. Sample both premultiplied color and coverage with those weights.
Do not interpolate hidden straight RGB. Crop clamp occurs before tap selection. Contain bars produce no raster pixels.

Current motion resolves clip-local opacity O in [0,65536]. Current mask resolves canvas-space coverage M in that range.
Without a mask M=65536. Combine once: `Q = round(O*M/65536)`.

For lower canvas channel L8 and sampled P16/A16:

```text
D = 65535 * 65536
N = 255 * P16 * Q + L8 * (D - A16 * Q)
out8 = round(N / D)
output alpha = 255
```

Use checked u128 intermediates and validate A16*Q <= D.
The positive contribution predicate is A16*Q > 0, before final color-byte rounding.
It measures positive coverage, not a difference between equal foreground/background colors.
All-255 source images and movies keep the historical opaque sampling and byte blend arithmetic exactly.

## Coverage, admission and execution

Preflight separates active source intervals from potential contributing coverage.
For Plan7, evaluate every local frame because motion and masks may change bounds.
An image with zero measured nonzero_pixels cannot provide potential coverage.
An alpha image with nonempty effective geometry can provide conservative potential coverage.
Do not add a support bitmap or claim that the chosen crop samples nonzero alpha.
A cropped transparent hole can pass conservative prepare, then fail exact runtime coverage.

Workers always return Source for an active PNG, even with NoGeometry or ZeroAlpha.
The compositor checks lineage before examining its sampled payload.
The existing opaque blend loop keeps its byte arithmetic and additionally counts positive effective weights.
The alpha blender counts pixels with A16*Q > 0.
Require at least one positive contribution from all sources combined before sending each output frame.
Fail `video_coverage` before writer admission if the frame has none. Export teardown prevents receipt publication and completed job state.

Logical charges remain explicit:

| Allocation | Charge |
| --- | ---: |
| Straight or opaque source | width*height*4 |
| Alpha raster | bounds.width*bounds.height*8 |
| Legacy raster | bounds.width*bounds.height*4 |
| Opaque canvas | width*height*4 |

Each source/canvas retains the existing 128 MiB extent limit.
Alpha raster allocation also must fit a declared 128 MiB owned-buffer limit; reject before allocation when it exceeds that limit.
Preflight and sampling use the same checked alpha-raster charge function.
Keep the existing three-canvas admission allowance, serialized PNG allowance, four workers and capacity-one request/response channels.
All application-owned allocations hold permits before allocation and until retirement. Keep the existing 512 MiB aggregate logical bound.
The bound excludes native/allocator/whole-process peaks. Do not rename it as measured process memory.
Hashing/scanning alpha, sampling and blending check cancellation per row. Existing native readiness, lease, epoch and deadline checks remain authoritative.

## Module ownership and signatures

`alpha_picture.rs` owns straight source construction, source alpha identity, UNORM16 raster, exact arithmetic and contribution counting.
`image.rs` owns strict PNG expansion and authoritative source hashes/facts. Its legacy opaque decode wrapper remains opaque-only.
`composition.rs` owns shared Mapping geometry, legacy sampler/blender, checked bounds and preflight charges.
Expose one private tap-footprint operation on Mapping; do not reproduce crop/fit calculations in alpha_picture.
`layers.rs` owns bounded scheduling, Source lineage, copied raster permits and bottom-to-top coverage enforcement.
`plan.rs` owns Plan7 policy selection and central normalization/evidence validation.
`project.rs` owns import backend choice and verified replay acceptance through Plan7.
`movie.rs` owns Plan7 dispatch and explicit decoded output opacity checks.
`pixels.rs` owns native pixel-buffer layout/locking and an allocation-free row scan for output alpha=255.
Publication, audio, stage ownership and codec/profile settings remain unchanged.

```rust
fn decode_picture_asset(path: &Path, asset: &StoredAsset) -> Result<DecodedPicture>;
fn source_alpha_id(asset: &ContentHash, rgba: &ContentHash, alpha: &ImageAlphaV1) -> Result<ContentHash>;
fn raster_bytes(bounds: &Bounds) -> Result<u64>;
fn sample_alpha_cancellable(source: &StraightRgba8, mapping: &Mapping, bounds: Option<&Bounds>, check: impl FnMut() -> Result<()>) -> Result<Option<AlphaRaster16>>;
fn blend_alpha_cancellable(canvas: &mut Pixels, raster: &AlphaRaster16, observation: &LayerObservation, check: impl FnMut() -> Result<()>) -> Result<u64>;
fn require_opaque_native(image: &CVPixelBuffer, check: impl FnMut() -> Result<()>) -> Result<()>;
```

Function names can follow existing private naming conventions. Representation, math, ownership and validation remain the binding contract.

## Verification and limits

Keep all 115 current runtime baselines, strict legacy raw hashes and both receipt schemas.
Freeze independent integer/rational vectors for hidden RGB, zero alpha, opacity/mask, contain, crop, signed clipping, order and fractional edges.
Exercise RGBA, grayscale-alpha, indexed tRNS and RGB tRNS expansion. Keep CRC/IEND, APNG and 16-bit negatives.
Test source/cache/raster retirement, cancellation, forged facts/policy/evidence and zero-alpha Source lineage.
Test conservative prepare followed by runtime crop-hole rejection before writer publication.

Before native execution, freeze source PNG bytes/facts, movie decode evidence, 72-frame timeline, producer, exact arithmetic and proof policy.
Use a freshly inspected preserved H.264 lower source and sparse asymmetric PNG overlay with vivid hidden RGB.
Exercise before/during/after intervals, crop, contain, signed motion, opacity, mask and overlapping order.
Use canonical Panja PCM24 stereo48k source [0,144000), unity gain and zero pan.
NativeColorMasterV1 requires every output frame/PTS/epoch/EOF, every predeclared nonempty ROI >=34 dB, every selected PCM24 code exact, and every decoded alpha byte 255.
Compare pre-encoding product canvases with the independent evaluator byte for byte through a test-only capture boundary.
An independent executable decodes actual written media. Disclose shared AVFoundation and bind all code, source, plan, receipt and output identities.
Declare negative controls before execution and require their specific false outcomes after a passing baseline.
H.264 remains a technical clock/opaque-output control. Its preserved failed ROI reports remain failures.

## Tradeoffs and alternatives

Accept an eight-byte sampled alpha raster in exchange for preserving the existing worker and copied-response ownership boundary.
Accept declared UNORM16/Q16 quantization in exchange for reproducible premultiplied filtering with small bounded payloads.
Accept conservative prepare in exchange for runtime coverage enforcement without a dense support bitmap.
Accept one policy and per-asset binding in exchange for avoiding a second alpha trace on every use.

Direct source-to-canvas composition was viable but changes more ownership and opaque sampling behavior in this unit.
Straight-RGB filtering fails the hidden-color fringe requirement. Flattening during import loses composability.
Routing every opaque source through alpha arithmetic risks historical byte changes.
Persisting a dense support map duplicates transformed sampling and increases durable state.

Managed color, APNG, sixteen-bit PNG, movie alpha, transparent export, throughput maxima and whole-process memory remain unverified.
This unit does not establish normal-speed watching, hearing, creative acceptance or completion of the full Panja film.

## Next step

Resolve independent design findings, save the selected contract, then implement its measured image and private raster boundaries.
