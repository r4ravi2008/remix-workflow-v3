# Transparent PNG composition — Candidate A

## Caller usage

The caller keeps the current `Project` API. PNG content determines whether an image has intrinsic alpha.

The caller does not choose straight or premultiplied storage. The editor owns that representation boundary.

### 1. Commit one real movie, one sparse transparent PNG, and canonical audio

This call uses the current `CommitProject` shape. `alpha_import` contains the future fixture's measured hash and byte count.

The fixture does not exist during design. Therefore, this example does not invent its identity.

```rust
fn commit_alpha_fixture(
    project: &Project,
    base_revision: ContentHash,
    alpha_import: AssetImport,
    canonical_wav_path: PathBuf,
) -> Result<RevisionReceipt> {
    let movie_hash = ContentHash::parse(
        "097dd9a1a59c02a8967db82463e8b43fc6ffc42a5294c997a77280967b1174df",
    )?;
    let audio_hash = ContentHash::parse(
        "cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8",
    )?;
    if alpha_import.media_kind != MediaKind::Image {
        return Err(StudioError::new("wrong_stream", "Alpha fixture must be an image"));
    }
    let alpha_hash = alpha_import.expected_hash.clone();

    project.commit(CommitProject {
        intent: EntityId::parse("alpha-commit-a01")?,
        base_revision,
        imports: vec![
            AssetImport {
                path: PathBuf::from(
                    "crates/editor/tests/fixtures/native/h264-source-a14.mp4",
                ),
                expected_hash: movie_hash.clone(),
                expected_bytes: 1_319_960,
                media_kind: MediaKind::Movie,
                origin: Origin::Imported {
                    external_source: "preserved A14 native fixture".into(),
                    role: "lower picture".into(),
                },
                previous_measurement: None,
            },
            alpha_import,
            AssetImport {
                path: canonical_wav_path,
                expected_hash: audio_hash.clone(),
                expected_bytes: 78_624_044,
                media_kind: MediaKind::Audio,
                origin: Origin::Imported {
                    external_source: "canonical Panja 24-bit WAV".into(),
                    role: "canonical audio".into(),
                },
                previous_measurement: None,
            },
        ],
        canonical_audio: Some(AudioBinding {
            asset: audio_hash.clone(),
            source_samples: Span { start: 0, length: 13_104_000 },
            source_rate: 48_000,
            channel_order: vec!["left".into(), "right".into()],
            channel_order_basis: "Explicit stereo interpretation; labels are not measured".into(),
        }),
        timelines: vec![Timeline {
            id: EntityId::parse("alpha-native-proof")?,
            frame_count: 72,
            video_tracks: vec![
                VideoTrack {
                    id: EntityId::parse("movie-lower")?,
                    clips: vec![VideoClip {
                        id: EntityId::parse("movie-lower-clip")?,
                        timeline_frames: Span { start: 0, length: 72 },
                        asset: movie_hash,
                        source_samples: Span { start: 0, length: 72 },
                        cadence: Cadence::SourcePresentationTime,
                        framing: None,
                        placement: None,
                        motion: None,
                        mask: None,
                    }],
                },
                VideoTrack {
                    id: EntityId::parse("alpha-upper")?,
                    clips: vec![VideoClip {
                        id: EntityId::parse("alpha-upper-clip")?,
                        timeline_frames: Span { start: 8, length: 56 },
                        asset: alpha_hash,
                        source_samples: Span { start: 0, length: 1 },
                        cadence: Cadence::Hold { ordinal: 0 },
                        framing: Some(Framing {
                            fit: PictureFit::Contain,
                            crop: NormalizedCrop {
                                x: 0.125,
                                y: 0.0,
                                width: 0.75,
                                height: 1.0,
                            },
                        }),
                        placement: Some(PicturePlacement {
                            destination: PixelRect {
                                x: -24,
                                y: 24,
                                width: 192,
                                height: 108,
                            },
                            opacity: Opacity::new(0.75)?,
                        }),
                        motion: Some(PictureMotion {
                            x: Some(PropertyCurve { keys: vec![
                                CurveKey {
                                    frame: 0,
                                    value: -24,
                                    to_next: Some(CurveInterpolation::Linear),
                                },
                                CurveKey { frame: 55, value: 26, to_next: None },
                            ] }),
                            y: None,
                            width: None,
                            height: None,
                            opacity: None,
                        }),
                        mask: Some(PictureMask::AxisReveal {
                            axis: MaskAxis::Horizontal,
                            progress: PropertyCurve { keys: vec![
                                CurveKey {
                                    frame: 0,
                                    value: MaskProgress::new(0.25)?,
                                    to_next: Some(CurveInterpolation::Linear),
                                },
                                CurveKey {
                                    frame: 55,
                                    value: MaskProgress::new(0.85)?,
                                    to_next: None,
                                },
                            ] },
                            inverted: false,
                        }),
                    }],
                },
            ],
            audio_tracks: vec![AudioTrack {
                id: EntityId::parse("canonical-audio")?,
                clips: vec![AudioClip {
                    id: EntityId::parse("canonical-prefix")?,
                    timeline_samples: Span { start: 0, length: 144_000 },
                    asset: audio_hash,
                    source_samples: Span { start: 0, length: 144_000 },
                    source_rate: 48_000,
                    gain: 1.0,
                    pan: 0.0,
                }],
            }],
        }],
    })
}
```

Tracks remain ordered bottom-to-top. Clips within one track remain non-overlapping.

The PNG stays ordinal zero with no PTS. The movie keeps its selected ordinals and measured PTS.

### 2. Prepare and export the same immutable request

```rust
let request = ExportRequest {
    intent: EntityId::parse("alpha-export-a01")?,
    revision: committed.revision.clone(),
    timeline: EntityId::parse("alpha-native-proof")?,
    profile: MovieProfile::NativeColorMasterV1,
};

let prepared = project.prepare_export(request.clone())?;
assert_eq!(prepared.plan.schema, 7);

let exported = project.export(request.clone())?;
assert_eq!(exported.receipt.artifact.schema, 3);
```

`prepare_export` can conservatively accept an alpha crop whose sampled support is empty.

`export` must reject that uncovered frame before it enters the native writer.

### 3. Reopen the result or cancel the active claim

```rust
let reopened = project.verify_export(request.intent.clone())?;
assert_eq!(reopened.receipt.receipt_id, exported.receipt.receipt_id);

// A concurrent owner uses the unchanged cancellation operation.
let cancellation = project.cancel_export(request.intent.clone())?;
```

Cancellation, replay, lease renewal, epoch fencing, staging, and publication keep their current public behavior.

## Decision

Candidate A keeps decoded PNG data as authoritative straight RGBA8.

Only sampled alpha rasters use premultiplied UNORM16 color and coverage.

The compositor flattens those rasters into the existing opaque BGRA8 canvas.

Opaque assets continue through the current rasterizer and blender. This preserves their exact pixel arithmetic.

`Settings.working_color` remains `source-sample-values-unmanaged`. Alpha adds no managed-color interpretation.

A new plan schema 7 appears only when a used image descriptor has measured non-opaque alpha.

## Persisted authoring and measurement types

`VideoClip` gains no field. Existing framing, placement, motion, opacity, and mask author the complete effect.

`MediaDescriptor::Image` gains one skipped optional measurement:

```rust
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ImageAlphaV1 {
    pub schema: u32,                 // exactly 1
    pub alpha_sha256: ContentHash,   // row-major expanded A bytes
    pub minimum: u8,
    pub maximum: u8,
    pub nonzero_pixels: u64,
    pub nonopaque_pixels: u64,
}

pub enum MediaDescriptor {
    Image {
        format: String,
        width: u32,
        height: u32,
        rgba_sha256: ContentHash,
        warnings: Vec<String>,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        alpha: Option<ImageAlphaV1>,
    },
    // Existing variants remain unchanged.
}
```

`rgba_sha256` remains the hash of expanded straight RGBA8 bytes.

The hash occurs before premultiplication and before the RGBA-to-BGRA channel swap.

`alpha_sha256` hashes one expanded alpha byte per source pixel in row-major order.

`alpha` is present exactly when `nonopaque_pixels > 0`. An all-255 image retains the old descriptor bytes.

The following invariants hold for an alpha record:

- `schema == 1`;
- both counts are at most `width * height`;
- `nonzero_pixels` equals the count of alpha values above zero;
- `nonopaque_pixels` equals the count below 255;
- `minimum` and `maximum` equal the observed extrema;
- `minimum <= maximum`;
- `nonopaque_pixels > 0`;
- a fully transparent image has extrema zero and `nonzero_pixels == 0`.

The decoder recomputes every fact in the same pass that builds straight RGBA.

Transparent imports use backend text `Rust png 0.17.16 / straight RGBA8 alpha v1`.

Opaque imports retain `Rust png 0.17.16 / opaque static PNG decode` exactly.

Both paths retain the current unmanaged-source warning. Neither path claims color conversion.

## Normalized plan types

Plan schema 7 adds an alpha binding only to affected image uses.

```rust
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PlannedAlphaUse {
    pub schema: u32,                 // exactly 1
    pub source_alpha_id: ContentHash,
}

pub struct VideoUse {
    // Existing fields remain in their current order.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub alpha: Option<PlannedAlphaUse>,
}

pub struct ImageDecodeEvidence {
    // Existing fields remain in their current order.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub source_alpha_id: Option<ContentHash>,
}
```

`source_alpha_id` hashes this canonical private document:

```rust
#[derive(Serialize)]
#[serde(deny_unknown_fields)]
struct SourceAlphaIdentityV1<'a> {
    schema: u32,                    // exactly 1
    asset: &'a ContentHash,         // compressed PNG identity
    rgba_sha256: &'a ContentHash,   // straight expanded pixels
    alpha: &'a ImageAlphaV1,        // measured alpha facts
}
```

The identity binds compressed bytes, straight pixels, and alpha facts.

Every alpha `VideoUse` and its decode evidence carry the same identity.

The compiler selects schema 7 if any directly used image has `alpha: Some`.

Without alpha images, the compiler retains its exact schema 2–6 selection rules.

Schema 7 composes all prior layer, motion, and mask fields. It does not replace their semantics.

Artifact receipts remain schema 2 for H.264/AAC and schema 3 for Native Color Master.

No pixel evidence enters the receipt. Pixel proof stays independent and test-owned.

## Private pixel representations

One new deep module owns all alpha-specific representation and arithmetic.

```rust
pub(crate) struct StraightRgba8 {
    pub width: u32,
    pub height: u32,
    pub rgba: Vec<u8>,
    pub alpha: ImageAlphaV1,
}

#[derive(Clone, Copy)]
pub(crate) struct PremulBgra16 {
    pub b: u16,
    pub g: u16,
    pub r: u16,
    pub coverage: u16,
}

pub(crate) struct AlphaRaster16 {
    pub bounds: Bounds,
    pub pixels: Vec<PremulBgra16>,
    pub positive_samples: u64,
}

pub(crate) enum RasterPayload {
    LegacyOpaque(Raster),
    AlphaV1(AlphaRaster16),
}

pub(crate) enum SampledLayer {
    GeometricNone,
    ZeroAlpha { bounds: Bounds },
    Raster { payload: RasterPayload, permit: Permit },
}
```

`StraightRgba8` owns the only expanded alpha source buffer.

Candidate A does not retain a second premultiplied source frame or a separate alpha plane.

Each sampled alpha output pixel retains premultiplied BGR and sampled coverage together.

The values remain together until the ordered compositor consumes them.

`Pixels` remains the opaque BGRA8 canvas and native-writer boundary.

`Raster` remains the opaque BGRA8 legacy sampled representation.

Movie sources remain opaque-only. A decoded movie pixel with alpha below 255 remains unsupported in this unit.

`SampledLayer::ZeroAlpha` is a sampled result. It is not a track gap.

## Exact alpha arithmetic

PNG stores unassociated color. Candidate A calls that representation straight RGBA8.

All arithmetic uses unmanaged encoded sample values. No transfer function or color conversion is implied.

Define `round(n / d)` as `(n + d / 2) / d` for nonnegative integers.

### Source texel conversion

For each straight color byte `C8` and alpha byte `A8`:

```text
C16 = C8 * 257
A16 = A8 * 257
P16 = round(C16 * A16 / 65535)
```

`P16` is the premultiplied contribution for one channel. Conversion happens per sampled texel.

The straight source remains unchanged, including hidden RGB under alpha zero.

### Existing sample geometry

`Mapping` keeps the current crop, pixel-center, clamp, fit, and signed-clipping calculations.

It still chooses `x0`, `x1`, `y0`, `y1`, `fx`, and `fy` with current `f64` geometry.

Only the alpha sampler quantizes each fractional part:

```text
fxq = clamp(round(fx * 65536), 0, 65536)
fyq = clamp(round(fy * 65536), 0, 65536)

w00 = (65536 - fxq) * (65536 - fyq)
w10 = fxq           * (65536 - fyq)
w01 = (65536 - fxq) * fyq
w11 = fxq           * fyq
```

The weights sum exactly to `2^32`.

For premultiplied color or coverage value `V16`:

```text
sample16 = round((w00*V00 + w10*V10 + w01*V01 + w11*V11) / 2^32)
```

The crop clamp happens before texel selection. Excluded texels cannot enter a footprint.

Contain bars produce no raster pixels. They therefore reveal lower tracks.

### Opacity and mask

The current motion evaluator supplies clip-local `OpacityQ16`.

The current mask evaluator supplies canvas-space `CoverageQ16`.

Their effective Q16 weight remains:

```text
Q = round(opacity_q16 * mask_coverage_q16 / 65536)
```

Without a mask, `mask_coverage_q16` is 65536.

This weight scales both sampled premultiplied color and sampled intrinsic coverage.

### Flatten into the opaque canvas

Let `L8` be one lower canvas channel. Let `P16` and `A16` be sampled values.

```text
D   = 65535 * 65536
N   = 255 * P16 * Q + L8 * (D - A16 * Q)
out = round(N / D)
```

The implementation uses checked `u128` intermediates. It verifies `A16 * Q <= D`.

Canvas alpha is always set to 255.

A pixel contributes visible coverage exactly when `A16 * Q > 0`.

The rounding sequence is fixed:

1. Premultiply each source texel to UNORM16.
2. Quantize each spatial fraction to Q16.
3. Bilinearly sample color and coverage to UNORM16.
4. Combine clip opacity and mask coverage to Q16.
5. Composite once and round each canvas channel to eight bits.

Opaque alpha texels produce `P16 = C8 * 257` and `A16 = 65535`.

Even so, old opaque assets use the legacy path. That choice preserves current rounding exactly.

## Observation and coverage model

Candidate A names four different facts:

| Fact | Authority | Meaning |
|---|---|---|
| active source | normalized clip interval | a source must answer this frame |
| geometric bounds | `Mapping` plus placement and mask | canvas pixels that might be sampled |
| potential contribution | preflight | a source could provide a positive weighted pixel |
| actual contribution | ordered compositor | at least one sampled pixel has `A16 * Q > 0` |

These facts never share one Boolean.

### Preflight responsibility

Preflight validates every schema-7 pose, mapping, mask, source, and charge before allocation.

It rejects a frame when no active source has potential contribution.

An alpha source has no potential contribution when any condition holds:

- its measured `nonzero_pixels` is zero;
- its effective geometric bounds are empty;
- its clip opacity is zero throughout those bounds;
- its mask gives zero effective weight throughout those bounds.

Otherwise, preflight treats the alpha source as potentially visible.

A crop can select only transparent holes inside a source with other nonzero pixels.

Candidate A does not serialize a support bitmap to answer that case during prepare.

Therefore, `prepare_export` can accept that conservative potential.

### Runtime responsibility

Runtime sampling is authoritative for actual frame coverage.

Each worker emits `Decision::Source` before the compositor evaluates visibility.

The decision always contains clip, asset, ordinal, optional PTS, and resolved placement observation.

An active PNG records ordinal zero and `pts: None`, including a fully transparent image.

An obscured movie still decodes its selected sample and checks its measured PTS.

An alpha sampler with no positive sampled coverage returns `SampledLayer::ZeroAlpha`.

The response barrier remains satisfied. The worker can release its unused raster permit.

The compositor records a contribution only after applying intrinsic alpha, opacity, and mask.

After all tracks answer, the compositor requires at least one contributing pixel for that frame.

It fails `video_coverage` before sending an uncovered frame to the native writer.

A transparent upper overlay remains a truthful source observation when a lower movie covers the frame.

This split handles cropped holes without suppressing lineage or accepting transparent coverage.

## Typed execution sketch

Public operations stay unchanged:

```rust
impl Project {
    pub fn commit(&self, request: CommitProject) -> Result<RevisionReceipt> {
        unimplemented!()
    }

    pub fn prepare_export(&self, request: ExportRequest) -> Result<PreparedExport> {
        unimplemented!()
    }

    pub fn export(&self, request: ExportRequest) -> Result<ExportResult> {
        unimplemented!()
    }

    pub fn cancel_export(&self, intent: EntityId) -> Result<ExportCancellation> {
        unimplemented!()
    }

    pub fn verify_export(&self, intent: EntityId) -> Result<ExportResult> {
        unimplemented!()
    }
}
```

Private boundaries become explicit:

```rust
pub(crate) enum DecodedPicture {
    LegacyOpaque(Pixels),
    StraightAlpha(StraightRgba8),
}

pub(crate) fn decode_png_cancellable(
    path: &Path,
    asset: &StoredAsset,
    check: impl FnMut() -> Result<()>,
) -> Result<DecodedPicture> {
    unimplemented!()
}

pub(crate) fn source_alpha_id(
    asset: &ContentHash,
    rgba_sha256: &ContentHash,
    alpha: &ImageAlphaV1,
) -> Result<ContentHash> {
    unimplemented!()
}

impl Mapping {
    pub(crate) fn bilinear_footprint_q16(
        &self,
        canvas_x: u32,
        canvas_y: u32,
    ) -> Result<BilinearFootprintQ16> {
        unimplemented!()
    }
}

pub(crate) fn sample_alpha_cancellable(
    source: &StraightRgba8,
    mapping: &Mapping,
    bounds: Option<&Bounds>,
    budget: &Arc<Budget>,
    check: impl FnMut() -> Result<()>,
) -> Result<SampledLayer> {
    unimplemented!()
}

pub(crate) fn composite_alpha_cancellable(
    canvas: &mut Pixels,
    raster: &AlphaRaster16,
    observation: &LayerObservation,
    ledger: &mut FrameContributionLedger,
    check: impl FnMut() -> Result<()>,
) -> Result<()> {
    unimplemented!()
}

pub(crate) fn composite_legacy_counted_cancellable(
    canvas: &mut Pixels,
    raster: &Raster,
    observation: &LayerObservation,
    check: impl FnMut() -> Result<()>,
) -> Result<PixelContribution> {
    // Use the current byte arithmetic unchanged and count weights above zero.
    unimplemented!()
}

pub(crate) struct PixelContribution {
    pub positive_pixels: u64,
}

pub(crate) struct FrameContributionLedger {
    timeline_frame: u64,
    source_observations: usize,
    positive_pixels: u64,
}

impl FrameContributionLedger {
    pub(crate) fn observe_source(&mut self, frame: &LayerFrame) -> Result<()> {
        unimplemented!()
    }

    pub(crate) fn record_positive_pixel(&mut self) -> Result<()> {
        unimplemented!()
    }

    pub(crate) fn require_coverage(self) -> Result<()> {
        unimplemented!()
    }
}
```

The ledger is ephemeral producer evidence. It is not serialized into a plan or receipt.

### Worker pseudocode

```text
for each requested timeline frame on this track:
    poll cancel, lease, epoch, and deadline
    resolve active normalized use
    if no use: send Gap(frame)
    otherwise:
        decode or select source under existing ownership rules
        verify source identity, descriptor, ordinal, and PTS
        resolve placement, motion, mask, picture window, and effective bounds
        if source is legacy opaque:
            run current rasterizer unchanged
        if source is straight alpha:
            reserve 8 bytes per admitted raster pixel
            sample premultiplied color and coverage row by row
            return ZeroAlpha when every sampled coverage value is zero
        send Source(observation, sampled layer)
```

### Ordered compositor pseudocode

```text
for each timeline frame:
    request one answer from every nonempty track worker
    allocate one opaque black BGRA8 canvas under its permit
    create FrameContributionLedger(frame)
    for each track from bottom to top:
        validate Gap or Source against the immutable plan
        for Source, record lineage before inspecting the sampled layer
        blend LegacyOpaque with current byte arithmetic and count positive weights
        blend AlphaV1 with exact premultiplied arithmetic
        treat ZeroAlpha as an observed source with zero contribution
    require ledger.positive_pixels > 0
    send the opaque frame to the existing bounded writer channel
```

An export failure stops the writer pump and releases the owned stage.

Publication cannot create an artifact receipt for a failed coverage check.

## Central validation and tamper rejection

Schema 7 validation belongs in `plan`, not in individual workers.

The validator rebuilds these relationships:

1. Rehash imported compressed bytes and compare the asset key and byte count.
2. Decode straight RGBA8 and recompute `rgba_sha256`.
3. Recompute every `ImageAlphaV1` fact and its `source_alpha_id`.
4. Require `alpha: None` for every all-255 image descriptor.
5. Require `VideoUse.alpha` exactly for non-opaque image descriptors.
6. Reject alpha use on movies, audio, or opaque images.
7. Require matching alpha identities in the source closure, use, and decode evidence.
8. Re-normalize ordinals, framing, placement, motion, masks, and audio.
9. Recompute the plan hash before replay or execution.

An old plan cannot declare alpha. A schema-7 plan cannot omit a required alpha use.

A schema-7 plan with no alpha image is rejected as noncanonical.

Changed PNG bytes fail the asset hash before their descriptor text can be trusted.

Forged descriptor facts fail decode equality. Forged normalized uses fail central plan validation.

## Ownership, memory, backpressure, and cancellation

The current maximum remains four workers. Each nonempty track has one worker.

Request and response channels remain synchronous with capacity one.

The compositor alone mutates the canvas. Workers never share mutable pixel buffers.

Each PNG track worker owns its straight source cache until the held clip retires.

The serialized PNG decoder mutex remains interruptible while waiting for ownership.

The PNG library call itself keeps its current bounded but non-interruptible interior.

The logical admission charges are:

| Payload | Charge |
|---|---:|
| straight alpha source | `width * height * 4` |
| legacy opaque source | `width * height * 4` |
| alpha sampled raster | `bounds.width * bounds.height * 8` |
| legacy sampled raster | `bounds.width * bounds.height * 4` |
| opaque canvas | `canvas.width * canvas.height * 4` |

Preflight evaluates every schema-7 local frame because motion and masks can change bounds.

It computes the largest simultaneous source and raster charge before any worker starts.

It also retains the current canvas and configured PNG temporary allowances.

The admitted application-owned estimate must stay within 512 MiB.

This estimate is not a whole-process peak-memory guarantee.

Compressed bytes, decoder samples, constructed RGBA, PNG internal allocation, vector capacity, native buffers, and allocator overhead can overlap.

Every live source, raster, and canvas holds its `Budget` permit until retirement.

`ZeroAlpha` drops the raster permit only after the worker has constructed its source response.

Alpha scanning, sampling, and blending check cancellation once per output row.

Channel send and receive loops retain current polling. `Workers::Drop` still closes ports and joins all workers.

AVFoundation readers and sample buffers remain inside their native callback.

No retained framework object crosses the callback boundary.

Decode and output remain native Rust and AVFoundation. This unit adds no FFmpeg, libav, or renderer subprocess.

Lease renewal and epoch checks remain part of `ExportControl`. Alpha code receives only its cancellable check closure.

## Module ownership

| Module | Responsibility after this unit |
|---|---|
| `model.rs` | optional measured image alpha facts; unchanged `VideoClip` authoring |
| `image.rs` | strict PNG boundary, expansion to straight RGBA8, hashes, alpha classification |
| `alpha_picture.rs` | source identity, typed alpha pixels, exact sampler, alpha compositor, coverage result |
| `composition.rs` | existing geometry, legacy opaque arithmetic, payload dispatch, admission |
| `framing.rs` | schemas 2–3 legacy full-canvas behavior only |
| `motion.rs` | existing clip-local placement and opacity evaluation |
| `mask.rs` | existing canvas-space Q16 coverage and opacity combination |
| `plan.rs` | schema 7 selection, normalized alpha binding, central cross-field validation |
| `layers.rs` | bounded workers, source observations, bottom-to-top order, per-frame ledger |
| `movie.rs` | schema-7 layer dispatch, writer fence, input evidence, technical readback |
| `pixels.rs` | opaque BGRA8 canvas and native copy boundary |
| `project.rs` | import storage, replay acceptance through schema 7, immutable source verification |
| `native_format.rs` | unchanged opaque 32BGRA writer contract and profile settings |
| `exports.rs` / publication | unchanged claim, stage, receipt, verification, cancellation, and recovery |

`alpha_picture.rs` hides association, precision, and rounding from callers and orchestration modules.

`movie.rs` keeps schemas 2–3 on the legacy path and routes schemas 4–7 through ordered layers.

## Compatibility contract

Snapshot stays schema 1. Store records stay schema 4.

The optional descriptor field is absent after old opaque data is deserialized and reserialized.

Opaque plans retain their current schemas and never enter alpha arithmetic.

The implementation must preserve all 115 current runtime baselines before adding alpha cases.

These strict documents remain byte-identical:

| Document | SHA-256 |
|---|---|
| `snapshot-schema1.json` | `a4afc9237cdc477ddc0c62023b7e0ed185a9f39bd3f72fd3f6596964d1c82423` |
| `plan-schema2.json` | `97fdd9f63d48ee3b600ee37a845c302e79815bd1870b20dae376f9c4a957e025` |
| `plan-schema3.json` | `4e5a89b00e7b5fabaafb4bf1335c1a5c3538c593765b4f5e5c818ff6bcede219` |
| `snapshot-schema1-placement.json` | `00d8a0eb3bbf0cd6290e68fffaa8c4d8b5a654446fb2220f5d084da17944e1ea` |
| `plan-schema4.json` | `5cf0320f82bfc19839c5a06ffec15449fcdb80b97be15e2b4fb4105517ef0687` |
| `snapshot-schema1-motion.json` | `1947fcb6939dbec40f13ae23b87a156f5d6e1758fa18e058aaa1f810abc313d3` |
| `plan-schema5.json` | `8ca51e03d048971a86cb598990fabd2f93f839c98b1b6c5fda3eb7aa90c3ee06` |
| `receipt-schema2.json` | `44c0c27ad1a58f22746011673d8e4d4a211c5b5cdeffcb18172d6cc73fc73be2` |
| `plan-schema6-masks-synthetic.json` | `5f9556fa7085bcd668d45cbc0564ff905adaf9b7f3d2e23b7fbed21ea65c5b28` |
| `plan-schema6-masks-canonical.json` | `507038af46a4b5c970734a0c3738f034038b8228674c2058f9c1cb41b8ea7eb0` |
| `snapshot-schema1-masks.json` | `a7bc52df330b5a9d7e0ef8e8fe71b47963d308be393eeefa0e00d0cfbbfc24dd` |

Receipt schema 3 and existing store schema 4 readback also remain exact.

There is no migration and no reinterpretation of historical descriptors.

## Verification design

### Independent exact pixel vectors

The reference evaluator uses integer or rational arithmetic. It cannot call production sampling or blending helpers.

The vector file freezes source straight RGBA hashes and expected BGRA8 output bytes.

It covers these cases:

1. Transparent red beside opaque blue samples to blue without a red fringe.
2. Hidden nonzero RGB at alpha zero leaves every lower byte unchanged.
3. White at alpha 128, opacity 32768, and mask 32768 produces byte value 32 over black.
4. Alpha 255 preserves all current placement, motion, mask, clipping, and order vectors.
5. Contain bars and transparent source pixels reveal a colored lower track.
6. A crop excludes vivid hidden texels before the bilinear footprint is built.
7. Signed off-screen placement retains current pixel-center coordinates.
8. Half-alpha blue over opaque red differs from reversed track order.
9. Fractional alpha and a fractional mask edge use the stated Q16 multiplication.
10. Inversion uses the exact complementary Q16 mask coverage.
11. A zero-alpha active image above an opaque lower layer records ordinal zero and no PTS.
12. A fully transparent source alone fails conservative preflight coverage.
13. A nonzero image cropped to a transparent hole fails runtime coverage before writer admission.

Decoder cases include RGBA, grayscale-alpha, indexed color with `tRNS`, and RGB with `tRNS`.

Each case verifies strict CRC handling and an exact zero-length terminal `IEND` boundary.

APNG and 16-bit PNG remain negative inputs.

### Actual native proof

Implementation creates one small asymmetric transparent PNG fixture.

The fixture contains opaque, partial, and zero-alpha regions. Zero-alpha pixels contain vivid hidden RGB.

The proof freezes its compressed hash, byte count, dimensions, straight RGBA hash, and alpha facts.

The lower source is freshly probed from this preserved file:

```text
crates/editor/tests/fixtures/native/h264-source-a14.mp4
bytes: 1,319,960
sha256: 097dd9a1a59c02a8967db82463e8b43fc6ffc42a5294c997a77280967b1174df
```

The 72-frame timeline uses separate movie and PNG tracks.

It includes frames before, during, and after the sparse overlay.

It exercises contain, crop, signed placement, motion, opacity, mask, overlap, and transparent holes.

The audio source is the 78,624,044-byte canonical 24-bit stereo 48 kHz WAV.

Its SHA-256 is `cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8`.

The selected source interval is exactly `[0, 144000)`. Gain is one and pan is zero.

The strict output uses `NativeColorMasterV1`.

Product verification must reopen QuickTime, `ap4h`, and `lpcm` tracks.

It checks 72 output frames, epoch zero, exact `n/24` output PTS, dimensions, and video EOF.

It checks every selected movie ordinal and measured source PTS.

It checks image ordinal zero and absence of image PTS on every active overlay frame.

It checks 144,000 stereo PCM frames and maximum PCM24 code delta zero.

It explicitly reads every decoded output alpha byte and requires 255.

Before encoding, production frames are compared byte-for-byte with the independent evaluator.

A separate executable then decodes the written master through AVFoundation.

That observer has separate source code and executable identity. Shared AVFoundation is disclosed.

The observer checks every output frame and every declared nonempty region.

Regions include alpha edges, overlap, contain bars, cropped support, mask edges, and motion endpoints.

The predeclared Native Color Master threshold is at least 34 dB for every required region.

The proof manifest binds source hashes, source descriptors, Snapshot, plan, producer, export intent, and epoch.

It also binds receipt bytes, receipt ID, output path, output hash, output bytes, and output profile.

It binds both observer executable identities, reports, decoded PCM capture, and exact PCM comparison.

The passing baseline must precede each negative control.

Each control changes one behavior and must produce its specific false result:

- interpolate straight RGB;
- ignore intrinsic alpha;
- reverse track order;
- fill contain bars with black;
- scale color but not coverage;
- scale coverage but not premultiplied color;
- omit the zero-alpha source observation;
- forge descriptor alpha facts;
- forge the normalized alpha identity or schema;
- change PNG bytes while retaining descriptor text.

The H.264/AAC profile remains a compatibility and clock smoke path.

Its independent BGRA readback also checks alpha 255 on every decoded pixel.

Preserved H.264 region failures do not pass the Native Color Master 34 dB gate.

No result claims managed color, maximum throughput, whole-process memory, watching, hearing, or creative approval.

## Rationale

### Context

The editor needs transparent static graphics before native text and broader graphics work.

Current image decode expands PNG data but rejects any alpha below 255.

Current sampling and blending also assume opaque BGRA8.

### Forces

- Source hashes must preserve hidden straight RGB.
- Filtering must avoid hidden-color fringes.
- Old serialized bytes and old opaque pixels must remain exact.
- Source observations must survive zero contribution.
- Memory and workers must remain bounded.
- The output profiles currently require an opaque flattened canvas.

### Choice

Keep one authoritative straight RGBA8 source buffer.

Create bounded premultiplied UNORM16 rasters only for measured alpha images.

Keep sampled coverage beside sampled color until ordered composition.

Use conservative preflight potential and exact runtime contribution.

### Consequences accepted

Alpha rasters cost eight bytes per admitted pixel instead of four.

UNORM16 and Q16 add declared quantization points. They avoid eight-bit premultiplication loss.

Prepare can pass a nonzero image whose selected crop contains only transparent pixels.

Export then fails before the uncovered frame reaches the writer.

Schema 7 and the alpha module add one new execution branch.

That branch avoids changing any historical opaque arithmetic.

### Rejected alternatives

**Premultiply and hash the full decoded source.** This loses authoritative hidden RGB and adds a full-frame buffer.

**Filter straight channels, then apply alpha.** This creates colored fringes near transparent texels.

**Route every picture through new alpha arithmetic.** This risks changing opaque legacy output despite unchanged documents.

**Persist a full alpha bitmap or dense per-frame support table.** This enlarges plans and duplicates sampling policy.

**Render every pose during prepare.** This duplicates expensive work and still requires runtime enforcement after source revalidation.

**Flatten transparency during import.** This destroys composability and makes the chosen background part of source identity.

**Infer association from `kCVPixelFormatType_32BGRA`.** That native format does not define the editor's source semantics.

## Red-flag screen

| Red flag | Candidate A response |
|---|---|
| shallow public API | existing `Project` operations hide every alpha representation detail |
| representation leakage | `alpha_picture.rs` alone owns association, precision, and rounding |
| generic dumping module | the module groups one coherent alpha composition invariant |
| pass-through layers | workers create observations and rasters; compositor owns order and coverage |
| shared mutable ownership | each worker owns sources; compositor alone owns the canvas |
| stringly execution policy | schema and typed alpha identities select behavior centrally |
| incompatible optional data | absent fields skip serialization and old paths keep old schemas |
| false temporal coverage | runtime requires a positive weighted alpha sample before writer admission |
| lineage lost by optimization | `ZeroAlpha` remains inside `Decision::Source` |
| hidden unbounded buffer | every retained source, raster, and canvas has a declared charge and permit |
| framework object escape | AVFoundation objects remain callback-confined |
| speculative proof claim | Native Color Master fidelity remains unverified until actual write and independent readback |

## Candidate A position

This shape spends precision and raster memory only where source alpha requires them.

It keeps source truth, execution truth, and output proof as separate records.

The parent can compare this ownership-first shape with the independent candidate before synthesis.

Reviewers use the same model family. This document makes no blind or cross-family review claim.
