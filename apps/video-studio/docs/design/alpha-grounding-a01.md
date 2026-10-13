# Transparent PNG alpha grounding A01

Status: grounding complete. This document traces the current runtime before independent alpha candidates. It selects no API or implementation shape.

The inspection was read-only. It changed no runtime, metadata, fixture, proof, media, GPU, Resolve, or film state.

## Overview

The editor can decode eight-bit PNG samples into RGBA, but it accepts only pixels with alpha 255. Two later checks enforce the same opaque contract. The layer sampler rejects non-opaque source BGRA, and the compositor rejects non-opaque rasters.

The current path is:

```text
Project::commit
  -> Studio::stage
  -> media::probe
  -> image::probe / image::decode
  -> Snapshot 1
  -> plan::compile
  -> ExportPlan 2..6
  -> movie::write
  -> layers::decode for plans 4..6
  -> Mapping::rasterize_bounds_cancellable
  -> blend_layer_cancellable
  -> opaque Pixels canvas
  -> CVPixelBuffer 32BGRA
  -> AVAssetWriter
  -> ArtifactReceipt and native readback
```

A transparent-PNG unit can stay inside the existing Rust compositor and native writer path. The difficult part is the pixel contract. PNG supplies straight alpha, while correct bilinear filtering requires premultiplied color contributions. The final movie is currently an opaque composition, regardless of whether the profile uses H.264 or ProRes 4444.

The existing working-color string is `source-sample-values-unmanaged`. The runtime validates only that this string is nonempty. It performs no ICC, gamma, transfer, primaries, or linear-light conversion. Alpha work must preserve that explicit limitation.

## Key concepts

- **Straight alpha** stores color independently from coverage. A fully transparent pixel may retain nonzero hidden RGB values.
- **Premultiplied alpha** stores each color contribution after multiplication by alpha. A zero-alpha pixel therefore contributes zero color.
- **Source alpha** is intrinsic to the decoded PNG pixel. It is separate from clip opacity and mask coverage.
- **Raster alpha** is the sampled source coverage after crop, fit, placement, and bilinear filtering.
- **Output alpha** is the alpha written to the final canvas and native pixel buffer. The current canvas is always opaque.
- **Structural source coverage** means a clip is active at a timeline frame. It is not proof that any pixel contributes visible coverage.
- **Presentation lineage** binds a frame to its clip, asset, source ordinal, and optional source PTS. Visibility must not erase this lineage.

The [PNG specification](https://www.w3.org/TR/png/#6AlphaRep) defines PNG alpha as unassociated, or non-premultiplied. It also defines alpha as a linear fraction of opacity. The editor must not treat decoded PNG color bytes as premultiplied bytes.

Apple documents [`kCVPixelFormatType_32BGRA`](https://developer.apple.com/documentation/CoreVideo/kCVPixelFormatType_32BGRA) only as a 32-bit BGRA layout. That constant does not encode this editor's straight or premultiplied ownership rule. The Rust types must carry that rule explicitly or keep the representation private to the owning module.

## Current import and measurement path

### File ownership and bounded decode

`crates/editor/src/project.rs:159-238` stages an import into a content-addressed blob. It hashes every byte, verifies the expected byte count, creates a read-only hard link, syncs the blob directory, and probes the staged blob.

Image probing dispatches through `media::probe` at `crates/editor/src/media.rs:39-46`. Images do not enter AVFoundation. `media::with_track_cancellable` rejects `MediaKind::Image` because static images have no native media track.

`image::read_file` at `crates/editor/src/image.rs:14-29` uses `O_NOFOLLOW` and `O_CLOEXEC`. It requires a regular file and rejects input above `MAX_FILE_BYTES`, currently 129 MiB.

`image::decode` at `image.rs:53-135` applies these rules:

1. The PNG must end exactly at a zero-length `IEND` chunk.
2. Critical and ancillary CRC failures are errors.
3. APNG control records are rejected.
4. Original 16-bit samples are rejected.
5. The decoded owned frame must fit within 128 MiB.
6. `png::Transformations::EXPAND` expands palettes, sub-eight-bit grayscale, and `tRNS` transparency.
7. The final output must have eight-bit samples and the original dimensions.

The decoder converts RGB, RGBA, grayscale, and grayscale-alpha output into straight RGBA. Palette and `tRNS` forms can reach those expanded forms. It then rejects any alpha byte below 255 with `unsupported_image_alpha`.

For accepted opaque images, `rgba_sha256` hashes the straight RGBA bytes before red and blue are swapped. The returned `Pixels` bytes use BGRA order. This hash order is an existing provenance contract.

`image::decode_asset` rechecks the compressed asset hash and byte count. It then requires exact equality between the fresh descriptor and `StoredAsset.descriptor`. A future alpha descriptor must remain reproducible from the immutable bytes.

`Studio::stage` stores this exact backend string for accepted images:

```text
Rust png 0.17.16 / opaque static PNG decode
```

The descriptor stores this exact warning:

```text
Source sample values only; ICC, gamma, color conversion and creative acceptance remain unverified
```

Both strings are serialized into historical snapshots and plans. Existing opaque imports must keep them unchanged.

### Current type limitations

`MediaDescriptor::Image` at `crates/editor/src/model.rs:284-312` has five fields:

```text
format, width, height, rgba_sha256, warnings
```

It records no alpha presence, alpha encoding, alpha extrema, nonzero bounds, or pixel representation. The descriptor therefore cannot distinguish an opaque PNG from a varying-alpha PNG.

`pixels::Pixels` at `crates/editor/src/pixels.rs:13-17` stores only width, height, and `Vec<u8>`. It cannot distinguish these representations:

- straight RGBA or BGRA;
- premultiplied RGBA or BGRA;
- opaque BGRA;
- an opaque final canvas.

`composition::Raster` also stores untyped four-byte pixels. Its current runtime checks compensate by requiring every alpha byte to equal 255. Removing those checks alone would make the representation ambiguous.

`ImageDecodeEvidence` at `crates/editor/src/plan.rs:108-116` records asset, dimensions, straight `rgba_sha256`, and decoder executable. It records no alpha contract. `movie::verify_inputs` calls `image::decode_asset` and copies this evidence into the plan.

## Snapshot and plan flow

### Authoring model

`Snapshot` remains schema 1. It owns settings, immutable measured assets, source lineage, canonical audio, and ordered timelines.

`VideoClip` owns the selected asset and these picture operations:

- timeline and source spans;
- cadence;
- crop and fit through optional `Framing`;
- destination rectangle and clip opacity through optional `PicturePlacement`;
- independent motion curves through optional `PictureMotion`;
- optional `PictureMask`.

Intrinsic source alpha is absent from `VideoClip`. That is correct ownership in principle because alpha comes from measured asset pixels. The missing information belongs at the decoded-image boundary and its normalized execution contract.

`Snapshot::validate_cancellable` at `model.rs:442-665` validates assets and lineage. It also validates track ordering, clip ranges, same-track non-overlap, image hold cadence, framing, placement, motion, mask, and audio.

Static images must use `Cadence::Hold { ordinal: 0 }`. Their source range is exactly the single image sample. Alpha must not invent a movie clock.

### Plan compilation and validation

`plan::compile` walks video tracks in stored order. It emits one `VideoUse` per clip and repeats image presentation ordinal zero for the clip length.

The current schema selector is cumulative only through masks:

| Condition | Current plan schema |
|---|---:|
| Mask exists | 6 |
| Otherwise, motion exists | 5 |
| Otherwise, layered placement or multiple tracks exist | 4 |
| Otherwise, an image exists | 3 |
| Movie cut only | 2 |

Alpha cannot be inserted into this selector silently. An alpha image can also have placement, motion, and a mask. The next normalized shape must represent those combinations without changing how no-alpha projects select schemas 2–6.

`plan::validate_picture_mapping_cancellable` accepts only schemas 2–6. It reconstructs a Snapshot, revalidates it, and compares each ordered clip with its `VideoUse`. It checks asset, spans, framing, placement, normalized motion, normalized mask, and `presentation_ordinals`.

The validator currently enforces schema-specific motion and mask rules. Schema 6 must contain masks. Schemas 5 and 6 can contain normalized motion. Older plans reject those fields.

`Project::replay_plan` at `crates/editor/src/project.rs:280-320` also accepts only schemas 2–6. It verifies the stored plan document hash and project identity. Any new alpha plan version must be accepted at both boundaries.

`verify_plan_sources` rehashes every compressed blob. It does not decode the image descriptor. Prepare and execution do decode through `image::decode_asset`, which checks exact descriptor equality.

## Current spatial and temporal order

The current execution order is precise:

1. `motion::resolve` evaluates the clip-local destination rectangle and Q16 clip opacity.
2. `Mapping::new` applies normalized crop and the selected fit.
3. `Mapping::new` creates a signed destination-space picture window.
4. Canvas clipping produces unsigned visible bounds.
5. `mask::resolve_mask` evaluates the clip-local mask curve.
6. `mask::effective_bounds` removes mask regions whose combined clip and mask weight is zero.
7. The worker rasterizes source samples inside the remaining bounds.
8. The compositor combines clip opacity and per-pixel mask coverage.
9. Ports are blended in timeline track order, from the first track to the last.

The established interpretation is bottom-to-top track order. Later tracks composite over earlier tracks.

### Crop, fit, and contain bars

`Mapping::new` at `crates/editor/src/composition.rs:134-234` converts normalized crop coordinates into source pixels. It calculates `Contain`, `Cover`, or `Stretch` scale before signed canvas clipping.

For `Contain`, `Mapping` creates bounds only for fitted picture content. It does not create pixels for the unused destination area. Contain bars therefore reveal lower tracks in the layered path.

The legacy `framing::apply` path behaves differently. It allocates a full output canvas and initializes every pixel to opaque black. Its contain bars are black pixels.

This distinction is critical. An alpha-bearing one-track plan must not fall through the legacy schema-3 path. That path would make contain bars opaque and interpolate alpha as an ordinary channel.

### Motion, mask, and opacity

Motion changes the destination rectangle and clip opacity before mapping. It does not change source ordinals or source PTS.

Mask coverage is evaluated in canvas coordinates against the fitted `PictureWindow`. `mask::coverage_q16` returns `0..=65536`. Inversion replaces coverage with `65536 - coverage`.

`mask::effective_weight` currently combines clip opacity and mask coverage once:

```text
(opacity_q16 * coverage_q16 + 32768) / 65536
```

This weight assumes an opaque source. Per-pixel source alpha must become another independent multiplicand. Applying source alpha only to color or only to coverage would be incorrect.

## Why the current sampler cannot accept alpha unchanged

`Mapping::rasterize_bounds_cancellable` at `composition.rs:250-322` currently rejects any non-255 source alpha. It then bilinearly samples only B, G, and R. It sets every raster alpha byte to 255.

The sampler uses pixel-center coordinates. It calculates four source texels, interpolates with `f64`, rounds each color channel, and clamps the result to one byte.

Removing the alpha rejection would produce wrong edge colors. Straight RGB values from transparent texels would enter interpolation before coverage. Hidden colors would bleed into fitted edges.

The required semantic order is:

1. Read straight source `B`, `G`, `R`, and `A`.
2. Convert each contributing texel to premultiplied color contributions.
3. Bilinearly interpolate premultiplied B, G, R, and alpha.
4. Apply clip opacity and mask coverage to both sampled color contributions and sampled alpha.
5. Composite the result over the already opaque lower canvas.
6. Keep final canvas alpha at 255.

In normalized notation, let sampled premultiplied color be `P`, sampled alpha be `A`, and combined clip-mask weight be `Q`.

```text
output_color = P * Q + lower_color * (1 - A * Q)
output_alpha = 1
```

This equation does not require unpremultiplication because the lower canvas is opaque. It also makes zero-alpha hidden RGB contribute exactly zero.

The exact integer precision and rounding points remain a design decision. A candidate must define them before implementation. The decisive rule is that opaque inputs must retain their established bytes, and hidden zero-alpha color must never affect output.

### No color conversion in this unit

The PNG specification recommends compositing intensity samples, not gamma-encoded samples. The current editor does not know the source transfer function or working color space.

The requested bounded unit therefore operates on the decoded sample byte values. Premultiplication prevents alpha fringes, but it does not create linear-light or managed-color correctness.

The stored warning remains truthful. Native pixel fidelity under this contract is technical evidence only. It is not color or creative acceptance.

## Current compositor and output alpha

`composition::blend_with_weights` at `composition.rs:490-532` rejects non-opaque rasters. It blends only B, G, and R with Q16 weight and then writes alpha 255.

`layers::decode` initializes every canvas byte to zero, then sets every alpha byte to 255. A frame with no contributing upper pixels therefore remains opaque black or preserves lower-track pixels.

`Pixels::into_native` copies those four bytes into a `kCVPixelFormatType_32BGRA` buffer. It adds no alpha metadata and performs no premultiplication.

`NativeFormatContract` writes one of two current profiles:

- H.264/AAC in MP4;
- ProRes 4444/PCM24 in QuickTime.

The `ap4h` codec can carry alpha, but the current writer receives an opaque canvas. Codec capability does not prove an output-alpha contract.

Current output verification decodes every video frame as BGRA. It checks frame count, dimensions, PTS, epoch, and EOF. It does not compare pixel bytes or inspect output alpha values.

The bounded alpha unit is therefore source-alpha composition into an opaque movie. Transparent movie export is a separate feature and requires a separate profile, writer contract, and verification policy.

## Zero-alpha pixels, source clocks, and sparse coverage

`layers::run_track` distinguishes `Decision::Gap` from `Decision::Source`. A gap means no clip is active on that track. A source decision carries frame, clip, asset, ordinal, optional PTS, placement observation, and optional raster.

For a PNG clip, every active frame has presentation ordinal zero and no PTS. That source mapping remains truthful even when every sampled alpha value is zero.

A zero-alpha PNG frame must not become a gap. The worker must still decode and verify the asset. The compositor must still validate the clip, asset, ordinal, and resolved operations.

The current preflight coverage bit uses only nonzero geometric raster bytes. It knows about placement, motion, and masks, but it cannot know image alpha.

This creates two requirements for the later design:

- a fully transparent source must not falsely satisfy visible picture coverage;
- that same source must retain its structural source decision and presentation lineage.

An alpha-bearing sparse overlay may contribute on only part of the canvas. The lower track still supplies the output frame. Temporal union coverage must remain separate from per-pixel alpha coverage.

If a candidate adds alpha-aware bounds or an all-zero fast path, the optimization may remove a raster. It must not remove the source observation or its clock checks.

Movie clocks remain unchanged. A movie layer continues to compare each copied sample PTS with the immutable source index, even when another alpha layer hides it.

## Ownership, admission, backpressure, and cancellation

### Existing ownership

`layers::decode` creates one worker for each nonempty video track. The hard limit is four workers. Each worker owns a capacity-one request channel and a capacity-one response channel.

PNG decoding remains Rust-owned. One shared mutex serializes PNG decode across track workers. A static image is decoded once and cached for its clip interval.

Movie readers remain inside their AVFoundation completion callback and autorelease pool. Only copied Rust `Pixels`, scalar observations, rasters, and permits cross product channels.

The compositor owns one current canvas. The output channel has capacity one. `encode_frames` may retain one pending canvas until the native writer becomes ready.

### Existing logical admission

Every owned BGRA source or canvas must fit within 128 MiB. Preflight rejects more than four tracks or a logical estimate above 512 MiB.

The current estimate includes:

- three canvas extents;
- peak active source extents;
- peak effective raster extents;
- one serialized PNG temporary allowance.

The PNG temporary allowance is:

```text
decoded source extent + compressed asset bytes + 128 MiB
```

At runtime, `image::decode_asset` can retain the compressed file bytes, the decoder output buffer, and the constructed RGBA buffer simultaneously. The PNG reader can also allocate within its configured limit. Vector capacity and allocator overhead are separate.

The existing admission value is a conservative application-owned estimate. It is not a whole-process, allocator, decoder, AVFoundation, or encoder peak-memory guarantee.

Alpha does not inherently require more than four bytes per source pixel or raster pixel. A separate straight buffer, premultiplied buffer, alpha plane, coverage map, or cached alpha bounds would add ownership. Any such payload must enter both preflight and live `Budget` permits.

An in-place representation change can avoid another full frame. That possibility is an implementation choice, not a grounded guarantee.

### Cancellation barriers

Channel send and receive loops poll cancellation. PNG mutex acquisition also polls cancellation. Raster and blend operations check once per output row.

`Workers::Drop` sets the stopped flag, closes channels, and joins every remaining worker. Native reader objects stay callback-confined and cancel through their guards.

Alpha scanning, premultiplication, alpha-aware bounds, and blending must keep row-level checks. They must not add an uninterruptible full-frame pass.

Permits must remain alive until their payload is retired. A zero-alpha fast path must release raster permits while preserving the worker response barrier.

## Compatibility surface

### Strict historical documents

`crates/editor/tests/legacy_hashes.rs` deserializes and reserializes every listed document. It requires exact byte equality and exact SHA-256 equality.

| Document | Bytes | SHA-256 |
|---|---:|---|
| `snapshot-schema1.json` | 3,064 | `a4afc9237cdc477ddc0c62023b7e0ed185a9f39bd3f72fd3f6596964d1c82423` |
| `plan-schema2.json` | 369,279 | `97fdd9f63d48ee3b600ee37a845c302e79815bd1870b20dae376f9c4a957e025` |
| `plan-schema3.json` | 4,983 | `4e5a89b00e7b5fabaafb4bf1335c1a5c3538c593765b4f5e5c818ff6bcede219` |
| `snapshot-schema1-placement.json` | 409,983 | `00d8a0eb3bbf0cd6290e68fffaa8c4d8b5a654446fb2220f5d084da17944e1ea` |
| `plan-schema4.json` | 413,967 | `5cf0320f82bfc19839c5a06ffec15449fcdb80b97be15e2b4fb4105517ef0687` |
| `snapshot-schema1-motion.json` | 410,865 | `1947fcb6939dbec40f13ae23b87a156f5d6e1758fa18e058aaa1f810abc313d3` |
| `plan-schema5.json` | 415,912 | `8ca51e03d048971a86cb598990fabd2f93f839c98b1b6c5fda3eb7aa90c3ee06` |
| `receipt-schema2.json` | 1,418 | `44c0c27ad1a58f22746011673d8e4d4a211c5b5cdeffcb18172d6cc73fc73be2` |
| `plan-schema6-masks-synthetic.json` | 417,605 | `5f9556fa7085bcd668d45cbc0564ff905adaf9b7f3d2e23b7fbed21ea65c5b28` |
| `plan-schema6-masks-canonical.json` | 417,888 | `507038af46a4b5c970734a0c3738f034038b8228674c2058f9c1cb41b8ea7eb0` |
| `snapshot-schema1-masks.json` | 411,721 | `a7bc52df330b5a9d7e0ef8e8fe71b47963d308be393eeefa0e00d0cfbbfc24dd` |

The focused command passed during this grounding:

```text
cargo test -p video-studio --test legacy_hashes
1 passed; 0 failed
```

Historical image descriptors contain no alpha field. They also contain the opaque backend and warning strings shown above. A new required descriptor field would break deserialization.

An absent optional field can preserve old bytes only when all of these remain true:

1. It deserializes with a default.
2. It skips serialization when absent.
3. Old opaque descriptors remain absent after readback.
4. Old plan compilation keeps schemas 2–6.
5. Old plan execution keeps its existing arithmetic path.

Snapshot schema 1 can remain compatible with an additive absent field. That fact does not decide the eventual field or type.

ArtifactReceipt schema depends on the output profile, not picture-plan schema. H.264 currently uses receipt schema 2. Native Color Master uses receipt schema 3. Source alpha does not itself require a receipt schema change, unless a candidate adds persisted pixel evidence.

### Hard-coded execution seams

The following sites require deliberate treatment in any candidate:

| Site | Current alpha-relevant rule |
|---|---|
| `image.rs` | Rejects alpha below 255; returns untyped BGRA. |
| `project.rs` | Stores an opaque PNG backend string. |
| `model.rs` | Image descriptor has no alpha contract. |
| `plan.rs` | Selects schemas 2–6 and validates only those schemas. |
| `project.rs::replay_plan` | Accepts only schemas 2–6. |
| `movie.rs::write_inner` | Routes only schemas 4–6 through `layers::decode`. |
| `movie.rs::decode_timeline` | Uses opaque full-canvas `framing::apply` for schemas 2–3. |
| `framing.rs` | Makes contain bars opaque black and interpolates four straight channels. |
| `composition.rs::Mapping` | Rejects non-opaque source pixels and discards sampled alpha. |
| `composition.rs::blend_with_weights` | Rejects non-opaque rasters and forces canvas alpha 255. |
| `composition.rs::preflight_cancellable` | Has no alpha-aware visible-coverage rule. |
| `layers.rs` | Owns image caching, source observations, track order, and opaque canvas creation. |
| `mask.rs` | Combines only clip opacity and mask coverage. |
| `pixels.rs` | Carries untyped BGRA across Rust and Core Video boundaries. |
| `native_format.rs` | Requests 32BGRA input but declares no editor alpha representation. |
| `movie.rs::verify_inner` | Checks decoded clocks and dimensions, but not pixels or alpha. |

Changing only `image.rs` would therefore be unsafe. The remaining opaque checks would reject the asset, or a bypass would filter and blend it incorrectly.

## Decisive pure-pixel proof needed next

The later implementation needs an independent vector file. The reference must use exact integer or rational arithmetic and fixed expected BGRA bytes. It must not call production sampling or blending helpers.

The minimum vectors are:

1. **Hidden-color fringe.** Stretch a two-pixel source into one destination pixel. Use straight RGBA transparent red beside opaque blue. Composite over opaque black. Correct premultiplied sampling produces blue only. Straight interpolation produces a visible red component and must fail.
2. **Zero alpha.** Use nonzero hidden BGR with alpha zero. Verify the lower pixel remains byte-exact for every clip opacity and mask endpoint.
3. **Independent weights.** Use white with alpha 128, clip opacity Q16 32768, and mask coverage Q16 32768 over black. The chosen rounding contract must freeze the exact result. With byte-premultiplied white and nearest rounding, each output color is 32.
4. **Opaque equivalence.** Run all existing placement, motion, mask, and order vectors with alpha 255. Their expected bytes must remain unchanged.
5. **Contain transparency.** Place a contained alpha source over a colored lower track. Both contain bars and zero-alpha source pixels must reveal the lower bytes.
6. **Crop exclusion.** Put vivid hidden colors outside the retained crop. Scaling must never bleed excluded texels into visible output.
7. **Signed clipping.** Move the alpha source partly off-screen. Visible coordinates must retain the existing pixel-center mapping.
8. **Track order.** Composite opaque lower red and half-alpha upper blue. Reversing track order must produce a different expected vector.
9. **Mask edge.** Combine fractional source alpha with fractional mask coverage at the picture-window edge. Inversion must use the complementary Q16 coverage.
10. **Zero-alpha lineage.** A fully transparent active PNG must still produce a source observation with ordinal zero and no PTS. It must not satisfy visible coverage by itself.

The hidden-color vector should include the source's straight RGBA hash. This catches an implementation that hashes premultiplied pixels and loses hidden source data.

The vector set must cover explicit RGBA, grayscale-alpha, palette plus `tRNS`, and RGB with `tRNS`. APNG and 16-bit PNG must remain rejected.

## Decisive actual native proof needed next

The native fixture must use a real alpha PNG and a real movie simultaneously. A PNG-only unit would miss track ordering, source PTS, and native decode interactions.

The preserved native movie fixture is:

```text
crates/editor/tests/fixtures/native/h264-source-a14.mp4
bytes: 1,319,960
sha256: 097dd9a1a59c02a8967db82463e8b43fc6ffc42a5294c997a77280967b1174df
```

Its manifest says it is an exact preserved H.264 input from the accepted A14 proof. A new alpha proof must probe it again and bind the fresh descriptor. It must not rely only on the old prose report.

Create a new small RGBA PNG fixture during implementation. Use large asymmetric regions with opaque, partial, and zero alpha. Give zero-alpha pixels vivid hidden RGB. Record compressed bytes, content hash, dimensions, straight RGBA hash, and alpha classification.

The native timeline should include:

- the H.264 movie on a lower track;
- the alpha PNG on an upper sparse interval;
- contain fit, signed placement, crop, motion, clip opacity, and a mask;
- frames before, during, and after the overlay;
- one 48 kHz stereo unity-gain audio interval.

The proof needs two observation layers:

1. Exact pre-encode BGRA comparisons against the independent pure reference.
2. A separate native executable that decodes the written movie and compares every declared region.

The separate observer must bind source files, Snapshot, plan, producer, receipt, output hash, output bytes, and output profile. It must read every output frame to EOF.

The observer must record every output PTS with epoch zero. It must also check the selected movie ordinals and source PTS. The held PNG remains ordinal zero with no invented PTS.

Decoded H.264 and ProRes pixels need predeclared profile-specific thresholds. Exact compressed or decoded color equality is not assumed. The regions must separate correct premultiplied output from incorrect straight-alpha output by a wide margin.

Required negative controls are:

- straight-alpha bilinear interpolation;
- ignored source alpha;
- reversed track order;
- opaque black contain bars;
- source alpha applied to color but not coverage;
- mask or clip opacity applied to coverage but not premultiplied color;
- missing zero-alpha source observations;
- a forged descriptor alpha claim;
- a forged plan schema or normalized use;
- changed PNG bytes with preserved descriptor text.

The product `verify_export` remains useful for codec, clock, dimensions, EOF, audio, and receipt readback. It does not independently prove alpha pixels. The separate observer supplies that evidence.

This native proof establishes technical pixel behavior only. It does not establish managed color, maximum throughput, total process memory, normal-speed review, hearing, or creative acceptance.

## Where the behavior lives

- `crates/editor/src/image.rs`: bounded PNG decode, straight RGBA hash, and the first alpha rejection.
- `crates/editor/src/media.rs`: image dispatch and native movie decode boundaries.
- `crates/editor/src/model.rs`: measured image shape, authored clips, tracks, and Snapshot validation.
- `crates/editor/src/plan.rs`: normalized uses, schema selection, source ordinals, and central tamper checks.
- `crates/editor/src/framing.rs`: legacy full-canvas fitting and opaque contain bars.
- `crates/editor/src/composition.rs`: placement mapping, bilinear sampling, blending, coverage, and admission.
- `crates/editor/src/mask.rs`: canvas-space Q16 mask coverage and opacity combination.
- `crates/editor/src/layers.rs`: bounded track workers, image caching, source observations, and bottom-to-top composition.
- `crates/editor/src/pixels.rs`: Rust-owned BGRA and Core Video copies.
- `crates/editor/src/movie.rs`: plan-path dispatch, native writer pump, input evidence, and output readback.
- `crates/editor/src/native_format.rs`: container, codec, audio, and 32BGRA writer settings.
- `crates/editor/src/project.rs`: import measurement, plan replay, and source-blob verification.
- `crates/editor/tests/legacy_hashes.rs`: exact historical serialization guard.

## Grounded risks for candidate design

- Untyped four-byte pixels make straight and premultiplied alpha easy to confuse.
- Removing only the import rejection leaves two opaque runtime checks and incorrect sampling.
- Routing alpha through schema 3 creates opaque contain bars.
- A new schema must compose with placement, motion, and masks, not replace their semantics.
- Fully transparent assets can create a false preflight coverage claim unless visibility is alpha-aware.
- Alpha-aware pruning can erase truthful source observations if optimization and lineage share one decision.
- Premultiplying before the straight RGBA hash would collapse distinct source data.
- Premultiplying in eight-bit storage can add avoidable rounding before bilinear filtering.
- A changed arithmetic path can alter opaque legacy pixels even when serialized fields remain absent.
- `kCVPixelFormatType_32BGRA` alone does not define the editor's alpha association.
- ProRes 4444 capability does not prove preserved output alpha or correct input association.
- Product native verification currently proves clocks and extents, not pixel composition.
- PNG admission is a logical payload estimate, not a total-memory bound.
- Source-sample arithmetic is deterministic technical behavior, not managed-color fidelity.

## Questions the independent candidates must resolve

1. Which type boundary separates straight decoded pixels, premultiplied sampled pixels, and the opaque canvas?
2. Which fixed precision and rounding order preserves opaque behavior and defines fractional alpha exactly?
3. Which measured alpha facts belong in `MediaDescriptor::Image` and `ImageDecodeEvidence`?
4. How does preflight determine whether an alpha source can satisfy visible temporal coverage?
5. How does a zero-alpha fast path preserve `Decision::Source` and presentation lineage?
6. Which new plan schema represents alpha together with motion and masks?
7. Does new pixel evidence remain test-only, or does it require an optional persisted receipt field?
8. How will both H.264 and ProRes outputs prove opaque flattening without claiming managed color?

Candidate drafting should begin only after these questions are answered from the same caller-visible behavior.
