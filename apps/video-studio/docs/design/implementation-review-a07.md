# Implementation review A07

## Result

No P1 defect remains in the reviewed 24-frame source-clock unit.

The importer now uses Core Media output PTS and output duration as presentation authority.
It retains differing encoded PTS and duration without guessing an offset.

The guarded refresh preserved the exact source bytes and origin.
It created a new revision while leaving the old revision hash-valid and replayable.

The fresh product export reopened successfully and passed all 24 independent checks.
This result is technical evidence for one selected H.264 range.

Three P2 model gaps remain.
Decode timestamps still occupy a mixed clock domain.
Source measurements lack their exact producer identity.
The refresh target does not bind a stream identity.

The general compositor and complete hybrid film remain incomplete.

## Review boundary

The reviewed source file is 65,616,935 bytes.
All three checked copies have SHA-256 `b78939035919803ad33cd60979be7f1fb28798d8a34404c2881371300ce167ca`.

The copies are the downloaded publisher representation, the iCloud-bound import, and the project CAS blob.

The old revision is `29ec243126ea83f087335a54bfdf20b4334f6c656fe8732036511406ddedc903`.
Its source-measurement hash is `78430ab6c45ed7687c06143a1942dbbb9ec1383b7c82e6da240e133f6bb652f9`.

The refreshed revision is `624021b2286728d87df3972867ff47fd5f6ccbd4761a0d728cc7266a810e7470`.
Its source-measurement hash is `b6f3b1f29ea1435f8848cc864f7540aa9a97d7469b9b78db1d300cbe8217f31d`.

The successful export binds these identities:

- Plan: `096e80927a41df60f555d9d1fef64ac9e746cbd6a2634d3079aa62dff0df066b`.
- Producer: `11dc6297eedbe02b540a27e65fc14561676874c0dc95321f2bc81b71c43e49bb`.
- Output: `af3e408f677bd2907114bedcd7bf41c5e8740246b3c953aa17d4de5d2ddae7ab`.
- Output bytes: `640,834`.
- Artifact receipt: `cc720dd174abbc59d86df952655f25fc09379a1d8f82171b0b92ddfca69669ee`.
- Initial verification: `74f1a33508a72165f5f633abd3dda76fd867fe41220a3c47ed6c1dffce5eeeb3`.
- Independent report: `31d1c2ca951ede7d8ca83f76b10f2b08555020ac69b9c6b79b55acd501a8947d`.

The independent clock comparison document has SHA-256 `896a564090544bdb1179bd8c0fc39c35434833b4942774ec86c0f8d327a1cef5`.
That diagnostic does not record its helper executable identity.

The current reviewed development binary is `8af8ce1ba5f4bd342eba8f9adb54f9e4936ad4e9b674c6fae766d4bdc29df28c`.
It differs from the producer because the CLI capability wording changed after production.

The media, model, and project source hashes remained stable during final verification.

## Source-clock authority

The pre-fix index stored the first nonempty H.264 sample at `512/12288`.
Its first decoded frame appears at zero.

That mismatch caused the preserved prepare failure:
`Selected-range decode PTS differs from immutable source index`.

The native clock diagnostic reads the same exact source bytes through two AVAssetReader outputs.
The compressed path reports raw PTS `512/12288` and output PTS `0/12288`.

Its first compressed buffer contains zero samples and zero output duration.
The importer correctly skips that buffer.

The first nonempty compressed buffer still reports raw PTS `512/12288` and output PTS `0/12288`.
The decoded path reports its first frame at `0/12288`.

The diagnostic covers eight buffers per path and then cancels both readers.
Its `fullDecode`, `watched`, `heard`, and `creativeAccepted` fields are false.

The refreshed product index contains 6,462 nonempty compressed samples.
Its output PTS values start at zero and increase by exactly 512 ticks.

Every stored sample retains an encoded PTS exactly 512 ticks later than its output PTS.
The importer completed the full compressed reader before saving this index.

The prepared plan independently decoded source ordinals 0 through 23.
Every decoded PTS matched the refreshed output-clock index.

These observations support `output_presentation_time_stamp()` and `output_duration()` as the presentation index.
No fixed offset is inferred or applied by product code.

## Guarded refresh and immutable replay

`AssetImport.previous_measurement` is part of the canonical commit request hash.
The refresh request names the exact old `StoredAsset` document hash.

The commit compares that hash before replacing the measurement.
It also compares the content hash, byte count, and complete `Origin` value.

The head is checked before probing and again inside the immediate transaction.
Concurrent refreshes from one base revision therefore cannot both advance the project.

The production refresh retained these immutable values:

- Source SHA-256 `b789390...167ca`.
- Byte count `65,616,935`.
- External source `youtube:AVf7upKp7TM`.
- Role `publisher-alternate-h264-representation`.

The old revision body still hashes to its stored revision identity.
It contains no `encoded_time` fields.

The new revision body also hashes to its stored revision identity.
It contains `encoded_time` for all 6,462 source samples.

An isolated copied-store probe reopened both revisions with the producer binary.
The pre-fix revision returned its original measurement hash.

The same copy replayed the old import intent to sequence 2.
It also replayed the guarded refresh intent to sequence 3.

This proves the optional fields preserve old revision and request hashes.

A second copied-store probe supplied an incorrect previous-measurement hash.
It returned `measurement_conflict`.

The corrected request reused the same intent and committed sequence 4.
Its immediate retry returned `replayed: true`.

The failed guard therefore did not advance the copied head or consume the intent.
No original database or source file changed during these probes.

The current binary also replayed the exact stored plan on the copied store.
It retained the original plan ID and 24-frame decode evidence.

The checked-in guard test separately covers changed origin, unchanged head, successful commit, and intent replay.

## Product export evidence

The output contains 24 decoded frames at 2560 by 1440.
The independent verifier confirms every output PTS and every declared source ordinal.

Every frame matches source ordinals 0 through 23.
The minimum every-frame PSNR is `45.211483074847145` dB.

The output contains 48,000 decoded stereo PCM frames.
Both channels have zero-sample best lag.

The measured channel correlations are `0.9999769192056728` and `0.9999686975209157`.
The encoded AAC interval contains 50,176 ticks before native trim.

The receipt records raw encoded output-video PTS from `50/600` through `650/600`.
Those encoder timestamps are separate from decoded `n/24` presentation timestamps.

The independent report binds the source video, canonical audio, output, artifact receipt, and producer binary.
It also confirms no libav link.

No normal-speed watch or listen occurred.
Human and creative acceptance remain false.

## P2: decode timestamp remains in the raw clock

`SampleTiming.pts` and `duration` now use Core Media output timing.
`SampleTiming.dts` still uses `decode_time_stamp()`.

Core Media also exposes `output_decode_time_stamp()`.
The implementation does not measure or preserve that value.

The Panjaa record therefore places output PTS beside raw DTS in one structure.
No current planner or renderer reads `dts`, so this does not invalidate A07.

Future decode scheduling or mux logic could incorrectly assume all top-level fields share one clock domain.

Required change:

- Store output DTS beside output PTS when it is numeric.
- Move raw DTS into `EncodedTiming`, beside raw PTS and duration.
- Otherwise remove DTS until a consumer and clock contract exist.

Add a native fixture where raw and output DTS differ before using DTS operationally.

## P2: source measurements omit exact producer identity

The immutable `StoredAsset.backend` value is a static string.
It names Rust, objc2 0.3.2, AVFoundation, and asynchronous track loading.

It does not bind the executable hash, Cargo lock hash, macOS build, or AVFoundation bundle version.
The output plan and artifact receipt bind those values, but the source revision does not.

The archived A07 producer and external review records identify this refresh in practice.
That evidence is outside the immutable source-measurement document.

A later platform measurement can change the descriptor under the same static backend label.
The guard proves which metadata was replaced, but not which exact measurer produced either version.

Required change:

- Add an exact probe identity to `StoredAsset` or a hashed `NativeProbeReceipt`.
- Bind executable, lock file, host OS, framework bundle, and probe schema.
- Keep the probe identity inside the source-measurement hash.

## P2: refresh does not bind stream identity

`AssetImport.media_kind` selects the probed track.
The refresh comparison does not compare that selection with the stored descriptor kind.

Snapshot validation protects assets already referenced as video or audio.
An unused multi-stream asset can still replace its movie descriptor with an audio descriptor.

The current asset model also stores only one descriptor for one file hash.
It cannot expose both selected streams from a normal movie container at the same revision.

Source inspection establishes the missing comparison.
This review did not create a new mixed H.264 and LPCM fixture.

Required change:

- Give every stored stream a stable selector and identity.
- Make the refresh guard target that exact stream measurement.
- Preserve all measured streams under one immutable file asset.

This is a general-editor limitation, not a failure of the separate H.264 and WAV A07 fixture.

## Capability and proof limits

The current discovery output accurately names output PTS and duration as the movie index authority.
It also states that differing encoded times remain stored.

Discovery distinguishes the complete compressed index from selected-range decode coverage.
It keeps composition, human review, and tenant orchestration in `Planned` state.

The exact producer used earlier, less-specific capability wording.
That wording did not claim decoded whole-source coverage.

The complete 6,462-sample compressed index is not a complete decoded-source proof.
Only source ordinals 0 through 23 received plan-bound decode evidence here.

The H.264 byte identity is authoritative for this bounded export.
No representation map proves equivalence to the unsupported VP9 bytes or another logical source authority.

Orientation, clean aperture, sample aspect ratio, color metadata, and sync flags remain unverified.
The independent verifier does not establish those properties.

The clock diagnostic lacks a bound helper executable hash.
Its bounded observation should remain supporting evidence, not a capability receipt.

The unit still lacks layers, masks, motion, color operations, text, general audio mixing, and the full Panja edit.

## Validation

`cargo fmt --all -- --check` passed.

`cargo test --locked --workspace` passed all 28 tests.

`cargo clippy --locked --workspace --all-targets -- -D warnings` passed.

All behavioral probes used `/tmp/video-studio-a07-compat`.
No GPU or Resolve operation ran.

Cross-family model review was unavailable.
This document does not claim one.
