# Implementation review A14

## Result

Accept the bounded native picture-motion unit.
I found no remaining P1 or P2 product defect.

This verdict supersedes the pending status in the original static review.
That review remains unchanged in `implementation-review-a14-static-a01.md`.
Its SHA-256 is `bfaff3777b5ecb3c981a86dd2eabc0de7df623c4f46585a25ecc6e1902e4b379`.

The accepted producer is `video-studio-producer-release-a01`.
Its SHA-256 is `d8ae6b396206a2dc684183dbebb20fb410f6ecd48a84f0e26882ec5ea4be16e3`.
`build-a01.json` has SHA-256 `054c25b639a27a0de5e6ce5f5f3f56c3b59943682b33b7fe547e1614628a00e2`.
All 25 current Rust source files still match that frozen manifest.

I independently ran formatting, all targets, and Clippy with warnings denied.
All 80 tests passed.

No cross-family reviewer was available.
Candidate A read Candidate B before drafting, so the design review was not blind.

## Findings

P1: none.

P2: none.

The retained proof history exposed three evidence defects.
Each defect was repaired without changing the product binary or rendered movies.

1. The first Python opacity reference rounded a value just below one-half incorrectly.
   `motion_reference_a02.py` uses exact rational nearest-away rounding.
   Product prepare probes confirm below, at, and above one-half produce Q16 values `0, 1, 1`.
2. Native verifier A01 did not fully bind sources, measurements, receipts, and clock records.
   Verifier A02 added those bindings and 21 deliberate tamper controls.
3. A02's PCM records omitted the native `CMTime` epoch field.
   Verifier A03 uses a frozen standalone observer that serializes the epoch explicitly.
   Eight later controls reject missing epochs, nonzero epochs, discontinuous PTS, and false EOF.

The A03 report still records the later controls as pending.
`negative-controls-report-a02.json` completes that later check without rewriting A03.
Its SHA-256 is `956180e83fe5b1ee0f865ecbd34dba9ca1c56823aee5d90dfaf1f07f26478d0f`.

## Model, plan, and source authority

The implementation follows the selected typed-property design.
X, Y, width, height, and opacity remain independent curves.
One-key, one-frame, constant, and visually unchanged programs are valid.
The final key holds through the clip's last frame.

Linear interpolation uses one signed `i128` rational calculation.
It rounds once to the nearest value, with half ties away from zero.
Opacity is quantized once to a checked Q16 integer in `0..=65536`.

Snapshot schema remains 1.
Plan schema 5 stores normalized curves without a dense frame table.
A declared motion selects schema 5 even when the program is constant.

An animated schema-5 use has motion and no placement.
A static schema-5 use has placement and no motion.
Older schemas retain their original field rules and bytes.

Central validation recompiles the snapshot before execution.
It compares ordered tracks, clips, curves, ranges, ordinals, cadence, source PTS, framing, and lineage.
Motion does not change presentation ordinals.

Movie source PTS comes from each measured source sample.
Held PNGs use ordinal zero without inventing a movie clock.
The writer owns output video PTS, while audio keeps its 48 kHz sample clock.

A02 rehashes every imported source and validates the complete closure keyset.
It checks asset hash, byte count, measurement schema, producer identity, and descriptor.
It also checks the held-frame input against the exact imported movie.

A02 does not reproduce Rust's plan serialization hash in Python.
The product prepare, receipt CAS, and product reverify own that exact `plan_id`.
A02 hashes the complete saved plan response and independently validates its semantics.

## Runtime ownership and admission

Four bounded track workers feed one compositor.
Capacity-one request, response, and output channels preserve the reviewed ownership schedule.

A worker receives a frame request before opening a clip or decoding a PNG.
The final held-PNG cache retires before its final response.
Movie source pixels and their permits retire before each response.

The compositor consumes every current raster before sending the canvas.
It requests the next frame only after that send succeeds.
The three-canvas charge therefore covers cross-frame backpressure.

Preflight includes active caches, source copies, dynamic rasters, three canvases, and a conservative PNG temporary allowance.
Runtime permits reserve the same application-owned payload classes.
PNG decoding remains serialized.

Each movie operation moves once into its native completion callback.
AVFoundation readers, outputs, samples, and pixel buffers remain callback-confined.
Only copied Rust pixels, rasters, and scalar observations cross product channels.

The successful fixtures admitted 171,294,800 bytes.
Their maximum logical reservation was 169,724,767 bytes across four active sources.
These values do not measure allocator, framework, encoder, or process peak memory.

## Native picture and clock evidence

Verifier A02 is `verify_native_a02.py` at SHA-256 `8c323c743aed8c185f5720afb64b433999e2db365a7c1897bddcb7bdbddcf41a`.
Its report SHA-256 is `40f650818cea1e7687a2cdd174fef02ede95add80bbb62fccda9ba72a868c562`.

The synthetic and canonical fixtures each contain 72 frames at 320 by 180.
Each fixture uses four tracks, two simultaneous movie readers, and two PNG sources.
The plans exercise movement, resizing, fading, signed placement, sparse coverage, contain bars, and overlaps.

A02 binds all five imported files for each revision.
It checks 124 saved generated-source PNGs and their measured source PTS.
It also checks the selected held-movie ordinal and both image descriptors.

Separate Python code resolves every planned pose and composites every expected frame.
All 72 decoded frames passed the predeclared 34 dB threshold for both outputs.
The minimum full-frame PSNR was `36.12058809956287` dB.
All 173 visible-placement regions and all 126 overlap regions passed per fixture.

Both output readers reached video EOF with exactly 72 frames.
Every output PTS contains epoch zero and equals `n/24`.
Source movie and held-frame observations also contain epoch zero.

The verifier binds the exact output movies, receipt documents, receipt CAS bytes, plans, revisions, and producer.
The independent decoder is a separate executable but still uses AVFoundation.

The synthetic receipt is `505847160c4b16355af75199cc3775a7064219359086f543a062929819c053d7`.
Its output SHA-256 is `097dd9a1a59c02a8967db82463e8b43fc6ffc42a5294c997a77280967b1174df`.

The canonical receipt is `69b692a1cd7940a5a93f8f4112efefaf70d85871044b5f0a432cd63bcb9b5b28`.
Its output SHA-256 is `c4a94f3981bcb6a222aebca2d214b3c1f18972251ddddbfe460dac98b17928c3`.

## Audio evidence and observed decode variability

Verifier A03 is `verify_native_a03.py` at SHA-256 `1b28e53a695b06d44efbd2a6d9c22d9918a4abe8b3080c0bf199a9e34bd17d36`.
Its report SHA-256 is `6225fbd6200d0249583203e51fa4489ce2361eaac84bebc756b93c7733b91179`.

The standalone epoch observer has SHA-256 `1885e2ba4df470d806b51fed8a8e5238464f71ff70641e28a6ea3eecd4318b20`.
Its manifest binds the copied source, lockfile, build command, and binary.

Each primary output decode reached audio EOF with 144,000 stereo PCM frames.
Each has 18 positive, fully saved chunks.
Every chunk records epoch zero and begins at its cumulative sample offset over 48,000.

The synthetic comparison uses the 16-bit interval `[8191, 152191)`.
Its channel cosine values are `0.9999910976162989` and `0.9999782032912754`.

The canonical comparison uses the exact 24-bit master prefix `[0, 144000)`.
Its channel cosine values are `0.9999409173230048` and `0.9999440132552069`.
The original full canonical binding remains `[0, 13104000)`.

The first canonical A01 request used an invalid offset and failed before rendering.
Canonical A02 retained the original master binding and selected its prefix.

AVFoundation did not produce bit-identical canonical f32 output on every decode.
A03 retains two synthetic captures and nine canonical diagnostics.
Eight canonical captures use the explicit-epoch observer; one preserves the old observer record.

The first fresh canonical capture differs from the prior PCM file at 35,290 byte positions.
All retained captures still exceed the predeclared `0.999` master-cosine threshold.
The lowest recorded channel cosine is `0.9999409173230045`.

One earlier synthetic alternate was overwritten before A03.
Only its PCM and report hashes remain, so A03 assigns it no quality metric.
This history prevents a claim of bit-stable AAC float decoding.

The MP4 table checks confirm H.264 video, AAC audio, the video timing span, and 2,432 raw AAC padding ticks.
The padding is separate from the 144,000 decoded presentation frames.

## Cancellation and recovery

The active public cancellation used the frozen producer while epoch 1 owned its stage.
The stage contained 47,285 bytes before `project.cancel-export`.

The export process returned `export_cancelled` after 9.935 seconds.
The job and attempt ended as cancelled, with no receipt.
The owned stage was absent afterward.

Reconciliation reported no reclaimed or retained stage.
That result does not prove reconciliation removed the directory.
It is consistent with owned RAII cleanup before reconciliation inspected the path.

The report does not identify the exact native instruction at cancellation.
It also does not establish maximum cancellation latency.

## Compatibility

The frozen producer reverified all three historical artifact families.

- Schema 2 kept receipt `44c0c27ad1a58f22746011673d8e4d4a211c5b5cdeffcb18172d6cc73fc73be2`.
  Its output remains `e487e36c6927916428085f262d530d8abdafc8a8e6f3edc5bfdf80ecaa617e94`.
- Schema 3 kept receipt `8e0bc864df8f07f0ddf831000ac4601d49909d927030bbe67de03b13b6d0dd53`.
  Its output remains `ab65129d7bf451b193c764443a1731d0ecdb502b6889e1730a74e5b9760625ac`.
- Schema 4 kept receipt `580fa7c5bb6d0ade286f82d57b9945ca9a1df76679913580b61969415da0f715`.
  Its output remains `25373581534d7422236cd4ca6255ad9b048436bb8d85957d1a259e3a5fe52c2d`.

I rehashed the complete historical receipt and output files.
Their full identities match the saved readback records.
The film head remained sequence 9 at revision `1bd422f2175ce5468fe4efc24593677897570c5c04cbe0767bbac5a3f6234572`.

ArtifactReceipt remains schema 2.
Fresh `PictureExecutionEvidence` remains producer-only and absent on replay.

## Acceptance boundary

This review accepts bounded native technical motion behavior only.
It does not accept normal-speed playback, hearing, creative quality, or the full film.

The proof does not establish maximum-bound throughput or total native memory.
The source observations cover the selected fixture samples, not every frame of each provider movie.

Masks, rotation, alpha-bearing inputs, text, managed color, and the full general compositor remain future work.
The editor must not advertise those features as implemented.
