# Mastering implementation review A01

## Result

Accept the current native mastering implementation as a code-only unit.
No identified P1 or P2 defect remains after the reviewed repairs.

The implementation follows the selected private-format design.
It does not add a persisted recipe, Plan 7, public codec settings, or an H.264 fallback.

This review does not accept the complete mastering behavior unit.
The fixed 72-frame, 683-ROI-per-variant independent output proof remains pending.
The producer is not frozen yet.

No cross-family reviewer was available.

## Findings

P1: none.

P2: none after three repairs.

### Finalization now observes cancellation and fencing

The original implementation waited once for 30 seconds after `finishWriting`.
That wait did not observe cancellation, lease loss, or epoch loss.

`NativeWriterSession::finish` now receives the owned `ExportControl`.
It checks ownership before ending the session, every 25 milliseconds while waiting, and after the callback.

An error drops the export-thread-owned writer session.
Its guard cancels any writer that did not complete.
The stage guard then removes only its owned payload and owner document.

This closes the code path that could report a finalization timeout after the worker had already lost ownership.
The pending native proof must still exercise active cancellation and stale fencing with the fresh mastering producer.

### Receipt 3 now requires complete streaming evidence

The initial validator accepted a Receipt 3 with `streaming_audio` absent.
Legacy comparison intentionally ignores fresh streaming fields when an old Receipt 2 omitted them.
That compatibility rule made the missing Receipt 3 field material.

The mastering contract now requires both source and output stream evidence.
It validates positive bounded chunks, exact sample counts, and half-open sample intervals.

The output stream must start at zero, reach reader EOF, and decode its full declared count.
The receipt must also report a complete video decode and nonempty numeric encoded-track clocks.

The source stream preserves its selected source interval.
It is not relabeled as the zero-based output clock.

Negative tests reject a missing streaming field, false output EOF, oversized chunks, and incomplete profile evidence.
Receipt 2 retains the earlier optional-field behavior.

### The public profile now rejects ignored format overrides

Serde accepted extra keys beside the original unit variant despite the enum's unknown-field annotation.
That allowed callers to submit ignored codec or container parameters.

`MovieProfile` now uses a strict private wire enum for deserialization.
The empty mastering wire variant rejects every extra field.

The public Rust variant remains `NativeColorMasterV1`.
Its canonical JSON remains `{"kind":"native_color_master_v1"}`.
Historical H.264 JSON remains byte-identical.

## Format and plan authority

`NativeFormatContract::for_profile` is the sole profile-to-format mapping.
The contract owns container type, video codec, audio settings, MIME hint, stage name, artifact suffix, receipt schema, and validation.

The mastering mapping is fixed to QuickTime, `ap4h`, and stereo 48 kHz packed PCM24LE.
H.264/AAC retains MPEG-4, `.mp4`, and Receipt 2.

The writer implementation lives behind the private contract.
No other public type exposes codec strings, PCM flags, extensions, or native dictionaries.

Picture plan schemas remain 2 through 6.
The output profile stays an independent request and plan field.
The tests route the master through both image Plan 3 and layered Plan 4 without changing either schema.

The legacy fixture test preserves 11 exact documents.
It covers Snapshot 1 variants, Plans 2 through 6, both actual mask plans, and the historical Receipt 2.

Mastering fields on `NativeMeasurements` use absent-default and omit-when-absent serialization.
The H.264 contract rejects mastering container, PCM layout, or PCM comparison evidence.
The mastering contract rejects Receipt 2, `.mp4`, wrong codecs, or incomplete Receipt 3 evidence.

## PCM24 and clock correctness

The pure quantizer implements the selected finite-input rule.
It clamps to `[-1,1]`, scales by 8,388,608, rounds ties to even, and clamps to signed 24-bit range.

The sample-buffer path packs three little-endian bytes per channel in left-right order.
Its ASBD declares signed packed interleaved PCM, 24 bits, six bytes per stereo frame, and 48 kHz.

The unit vectors cover positive and negative half ties, both saturation endpoints, byte order, channel order, nonfinite rejection, and sample PTS.

Fresh output verification inspects every encoded sample description.
It requires stable `lpcm` layout and exact flags, bit depth, packet size, frame size, and channel layout.

The reopened output is decoded incrementally.
Each output chunk begins at its cumulative zero-based sample offset.
The output must reach EOF with the planned sample count.

For mastering, every reopened sample must equal the exact source-derived PCM24 code.
The decoded float must also equal that code divided by 8,388,608.
Receipt 3 records a zero maximum code delta.

Source selection remains separate from output timing.
The source evidence retains the selected interval and decoded prefix.
The writer assigns output audio PTS as `i/48000` and video PTS as `n/frame_rate`.

Encoded video and audio tracks retain their raw sample clocks.
Decoded video independently requires epoch-zero `n/frame_rate` PTS and EOF.
Compressed audio buffer count is never treated as a PCM sample-frame count.

## Native ownership and failure paths

The combined writer starts before the PCM stream and picture worker.
The same writer must accept and add video and audio inputs before source work begins.

One export thread retains the writer, both inputs, and the pixel adaptor.
The completion block captures only a unit sender, so no native object crosses its channel.

Source AVFoundation assets, tracks, readers, samples, and pixel buffers remain inside callback-owned operations.
Rust pixels, bounded PCM chunks, evidence, and structured errors cross product channels.

Objective-C exceptions during writing become `native_exception` failures.
Track callbacks catch exceptions before returning a Rust result.

Writer failure interrupts the shared control before joining the picture worker.
Dropping a PCM consumer closes its receiver, stops backpressure, and joins its worker.
The picture pipeline closes bounded ports and joins every Rust worker.

No failed, cancelled, or fenced path publishes a receipt or promotes a stage.

## Stage, promotion, and recovery

The contract supplies a typed `movie.mov` or `movie.mp4` payload name.
`ExportStage` does not infer format from a schema or caller extension.

The stage directory key binds project, intent, and epoch.
Creation remains exclusive and writes an owner document before rendering.

Cleanup removes only the expected regular payload and matching owner document.
Unknown files, wrong payload names, links, unreadable owners, and ownership mismatches remain retained.

Reconciliation hashes and validates the stored plan before deriving the payload type.
A `.mov` stage cannot be reclaimed under an H.264 plan or beside an unexpected `.mp4` file.

Promotion derives the content-addressed `.mov` path from the same contract.
Cancellation and epoch checks run before promotion under the existing transaction fence.

Finalizing recovery accepts only a receipt-bound promoted artifact after complete product verification.
A missing promoted artifact causes a fresh owned render under the new epoch.
The implementation does not adopt retained stage bytes.

## Validation

I independently ran these checks against the reviewed source:

- `cargo fmt --all -- --check`: passed.
- `cargo test --workspace`: 94 tests passed.
- `cargo clippy --workspace --all-targets -- -D warnings`: passed.

The suite performs real combined ProRes 4444 and PCM24 writes through Plan 3 and Plan 4.
The Plan 4 test reopens, verifies, and replays the Receipt 3 artifact.
It observes `ap4h`, `lpcm`, PCM flags 12, 48,000 sample frames, and zero code delta.

Those temporary tests use one-second 16-bit PCM fixtures.
They do not replace the pending 24-bit canonical source or fixed mask-output proof.

The saved 94-test log SHA-256 is `996a6998b6c72866cd6b5a90ca39b1a0c3b82c357de567255add80437ae71faa`.
The saved Clippy log SHA-256 is `dc49115c903c3462b668cd213d9315563546758bdde234cce52c995e45a4ef97`.

The frozen A15 review remains unchanged at SHA-256 `9e973d4e86791dbb73819dc4216c4dc1b34e803535b3f63b4576045582193038`.

## Reviewed source identity

| File | SHA-256 |
| --- | --- |
| `native_format.rs` | `e5e6a7e5a5fdc4e05784a676c390700a2c74cbfec22121a516a257b61b4292c7` |
| `movie.rs` | `05eb47cd416f8486c55698c0513e9b3a479545d0d8d1a2408651f145631b9012` |
| `media.rs` | `490fe7871d4521fbd586810bd0ae13d84ca4288bb8c610035b9cb4ea72c91b4d` |
| `pcm.rs` | `7ff87caa9a49b3b5b78a6aacfa10e798069ccf9e7f4216a60464c2c7b20dc76a` |
| `plan.rs` | `fb1e1857e38f04505e765c7545529221165cfede6c05d679ad4dedb635509fd0` |
| `exports.rs` | `50dd6ae14e071129018dc17590ecbaf1cea7d7a58a91e04843395f7d6ad2776c` |
| `export_stage.rs` | `5e713fe78b20d766dd9be59653849346440e41508da241043f1f2374ad52b5ad` |
| CLI inventory | `be300a0f202a070ba3f0679d05ee1f39af10cc4ae773a32db707f54d5f616702` |

## Remaining acceptance gates

Freeze a fresh producer only after binding this reviewed source and capability inventory.
Then run both unchanged 72-frame Plan 6 variants through the master profile.

Complete acceptance still requires these saved results:

1. Verify all 72 decoded frames and all 683 fixed nonempty ROIs per variant at the unchanged 34 dB policy.
2. Verify 144,000 exact PCM24 frames for synthetic `[8191,152191)` and canonical `[0,144000)` selections.
3. Bind complete source closure, plans, receipts, producer, observer, output hashes, output clocks, and both EOF observations.
4. Exercise product verification, completed replay, active cancellation, stale-epoch fencing, and interrupted recovery.
5. Reopen historical schemas 2 through 6 without changing their exact receipt or output identities.
6. Run independent negative controls for profile overrides, brands, codecs, PCM layout, clocks, EOF, tampering, cancellation, and promotion.

The pending proof must preserve the failed H.264 outputs and the 24 Mbps probe as failures.
It must not weaken the fixed ROI policy or alter the frozen references.

This review does not establish watched playback, heard audio, creative quality, managed color, Resolve suitability, full-film acceptance, maximum throughput, or native peak memory.
