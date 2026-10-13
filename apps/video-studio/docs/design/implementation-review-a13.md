# Implementation review A13

## Result

Accept the bounded layered-picture behavior unit. No P1 or P2 finding remains in the reviewed code and saved evidence.

The reviewed producer is `video-studio-producer-release-a02`, SHA-256 `5e2a0d6f7f284f56b0cd654077db04a68fe19942dce310e193272f4fc00a1820`.
Its manifest binds every reviewed Rust source and `Cargo.lock`. Current files match that manifest.

This acceptance covers native technical behavior only. It does not accept playback, hearing, story, creative quality, or the full film.
No cross-family reviewer was available.

## Repaired findings

The following review findings were repaired before the A02 producer was frozen:

1. `plan::validate_picture_mapping` now validates the complete snapshot and plan relationship before indexing or worker creation.
2. Validation checks ordered one-to-one timeline uses, normalized placement, source ranges, ordinals, cadence, and indexed source PTS.
3. Schema 2 and 3 plans reject placement. Schema 4 plans require normalized placement on every planned video use.
4. A held PNG releases its source cache and permit before its final response becomes observable.
5. `PictureExecutionEvidence.scope` distinguishes preflight estimates from the live logical permit high-water mark.

The first independent Pillow reference used pixel-center values where `EXTENT` requires source-edge coordinates.
That failed report and script remain preserved. The corrected reference uses derived edge coordinates and clamped edge padding.

The first canonical helper reused source observations without binding their complete evidence chain.
The final helper binds the exact corrected A01 report, source observers, source sequences, held-frame records, and source files.
The incomplete helper, report, and input-hash record remain preserved with `before-source-binding` names.

## Immutable model and compatibility

Snapshot schema remains 1. Optional placement fields omit absent values, preserving historical snapshot bytes.

Layered timelines use plan schema 4. Missing placement becomes the full canvas at opacity 1 during plan compilation.
The normalized placement is stored in each `VideoUse` and covered by the plan hash.

Artifact receipts remain schema 2. `PictureExecutionEvidence` is fresh-result data and is absent from replay or reopening.
It does not alter artifact receipts, native measurements, or their hashes.

The legacy fixture tests preserve exact Snapshot 1, Plan 2, Plan 3, and Receipt 2 hashes.
The current producer also reverified the historical 206-frame schema 2 artifact.
Its receipt remains `44c0c27ad1a58f22746011673d8e4d4a211c5b5cdeffcb18172d6cc73fc73be2`.
Its movie remains `e487e36c6927916428085f262d530d8abdafc8a8e6f3edc5bfdf80ecaa617e94`.

## Ownership, shutdown, and errors

Execution creates one Rust worker for each nonempty picture track, with a maximum of four.
One compositor requests each timeline frame in declared bottom-to-top track order.
Request, response, and composed-frame channels have capacity one.

Each movie worker transfers one `FnOnce` native track operation into the completion callback.
Reader, output, sample-buffer, and pixel-buffer objects remain within that callback operation.
Only owned Rust pixels and scalar observations cross picture channels.

Pipeline teardown sets the shared stop signal, closes every port, and joins every Rust worker.
Backpressure and PNG-lock waits repeatedly check the owned export control.
They preserve `export_interrupted` when the fenced export owner cancels or loses its epoch.

Native exceptions become structured `native_exception` failures. Decoder, source-map, channel, and deadline failures remain structured export errors.

AVFoundation calls are cooperative between calls. The library cannot forcibly interrupt one stalled framework call.
This limitation is stated in the product inventory and is outside this bounded unit's proof.

## Raster and temporal behavior

The compositor accepts opaque BGRA sources and produces opaque BGRA output.
A layer raster covers only fitted source content intersected with its destination and the canvas.
Contain bars contribute no raster pixels, so lower layers remain visible.

Signed destinations retain the original sampling transform before canvas clipping.
Contain, cover, stretch, normalized crop, bilinear sampling, and coded source dimensions use one pure mapping implementation.

Opacity becomes a fixed-point weight with denominator 65,536.
Values 0, 0.5, and 1 have exact endpoint or midpoint behavior.
Tracks blend in the timeline vector's declared bottom-to-top order.

Temporal coverage uses the visible content rectangle and nonzero quantized opacity.
Sparse overlay gaps are valid. The visible union must cover every output frame.

## Admission and observed schedule

Preflight uses a half-open interval sweep over every active source and raster charge.
It adds three canvas payloads and the maximum serialized PNG temporary allowance.
The policy rejects estimates above 512 MiB before source decoding.

Runtime permits bound the same logical application-owned payload classes.
They do not measure allocator capacity, process resident memory, PNG internals, or native framework buffers.

The A02 fixture admitted 171,230,016 bytes. Its live logical permit high-water mark was 169,675,807 bytes.
The plan exercised four worker paths and overlapping movie tracks.
PNG decoding remained serialized.

`peak_active_sources` and `admitted_payload_bytes` are preflight values.
`maximum_reserved_payload_bytes` is the live logical observation.

## Fresh A02 technical proof

The current producer created a 72-frame, 320-by-180 H.264/AAC output.
The exact movie is `25373581534d7422236cd4ca6255ad9b048436bb8d85957d1a259e3a5fe52c2d`, 1,023,669 bytes.

The independent A02 report is `f48188c7496714620b263d8fc61c72025eb4ec4c7b462510551bb248a15dac24`.
Its helper is `b627c55fa1a9bea10bdbf826f7a53afc1ed41b75d76958edbc073b6bd56e39fd`.
The frozen observer is `42b5b162c31320b6e981958c88458ab1de7fff9e8faf825edb7cb0f2293b2b2f`.

The observer decoded all 72 frames and 144,000 stereo PCM frames to EOF.
Every output RGBA hash and PTS equals the separately compared corrected A01 output.
The corrected A01 reference passed every frame, 176 placement regions, and 112 overlap regions.
Its minimum full-frame PSNR is 36.12058809956287 dB against the separate Pillow reference.

The A02 PCM bytes equal the independently decoded A01 PCM bytes.
Zero-offset channel correlations against source samples are 0.9999910976162789 and 0.9999782032912562.

The helper rehashed all five imported source files.
It checked semantic plan equality, H.264/AAC tables, frame counts, dimensions, timing duration, and reader EOF.

## Canonical-audio regression

The current producer also created a separate 48-frame canonical-audio fixture.
The movie is `d76f15a795198ebc126e2a932ebc8b29e173fb41c58587eab59bbe194bdcab92`, 659,353 bytes.

The final canonical report is `9558541f8fa06a195a609d058e97f6992d88e56529cb1f5a3d2aade092063212`.
Its helper is `5f548f25f380e4988c55088d89ffddc149165dcd740233f5b29ddd04f4c7d835`.

The helper binds all imported bytes, the plan, receipt, producer, observer, and corrected A01 reference.
It checks all 48 generated-source ordinals and PTS values against the plan.
It also checks held OG ordinal 1560, its PTS, decoded RGBA, and extracted-image descriptor.

Every output frame binds its saved PNG to the observer's RGBA, index, dimensions, epoch, and 24 fps PTS.
All 48 full-frame comparisons pass. The minimum PSNR is 36.12058809956287 dB.
All 128 placement regions and eight overlap regions pass the 34 dB gate.

The audio source is the exact 78,624,044-byte canonical WAV.
Its SHA-256 is `cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8`.
It contains 13,104,000 interleaved stereo PCM frames at 48 kHz and 24 bits, exactly 273 seconds.

The canonical binding covers `[0, 13104000)`. This fixture selects `[0, 96000)` at unity gain and zero pan.
The observer decoded exactly 96,000 stereo frames to EOF.
Its chunk PTS values are contiguous from sample zero through sample 96,000.

Zero-offset correlations against the selected 24-bit samples are 0.9999705560560942 and 0.9999708586933912.
This proves the two-second selected prefix only. It does not prove the remaining canonical master or the full film.

## Verification boundary

I independently ran the 69 tests, formatting check, and Clippy with warnings denied. All passed.
The current source and lockfile still match the frozen A02 build manifest.

The product verifier rechecks exact receipt, output bytes, decoded frame clock, dimensions, audio extent, and audio correlation.
The separate observer and Pillow helper provide the whole-output pixel comparison for this unit.
Both native implementations use AVFoundation, while the picture, RIFF, and MP4 comparisons use separate Python code.

The unit does not support alpha-bearing picture inputs, masks, rotation, animated placement, fades, text, or managed color.
It does not verify display orientation, aperture, sample aspect ratio, or color metadata.
Audio remains one measured 48 kHz stereo clip at unity gain and zero pan.

Maximum 100,000-frame throughput and total native memory remain unmeasured.
No output received normal-speed watching or hearing during this review.
The complete musical pilot, creative gates, and 273-second final film remain incomplete.
