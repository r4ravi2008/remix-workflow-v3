# Implementation review A12

## Result

No P1 or P2 correctness or scope defect remains in the bounded streaming PCM unit.

The current implementation owns stereo PCM in chunks of at most 4,096 sample frames.
Each producer uses a channel with capacity two.
The writer and verifier preserve exact integer sample positions without buffering the complete selection in Rust.

The A03 producer exported and reopened the 12-second fixture successfully.
The independent observer checked all 288 frames and all 576,000 decoded stereo sample frames.

`README.md`, `docs/WORK.md`, discovery, and the behavior-unit document now state the implemented A03 boundary consistently.

This unit does not complete audio mixing, resampling, the general compositor, or the hybrid film.

## Review boundary

The reviewed implementation hashes are:

- `pcm.rs`: `5b9b99d77b1a2472d1eac885e48c9522ff02e8cbd558bc22ae699bdfa7eebb4d`.
- `movie.rs`: `7faad217a0b41cc4181ab79c9a865a39179864c4e2d1c24dc27fab8545fd7155`.
- `media.rs`: `673354f4062a387ec084dccef8186e7bd4f20358f16963bc9ef36628cd53dea8`.
- `exports.rs`: `ada31ede174c68c00adfe07be3aa966df0682ab76d35f1d9af180bf5bda766b1`.
- `model.rs`: `5a0a5f50f9163d5350f1ce0c3efea0670fb3969ee8b33246ad915f266af12d90`.
- CLI `main.rs`: `1cc76c8130ecc1a348f11447ce5054f01405fc99f88ef15dd533962dd343f175`.
- `Cargo.lock`: `e1499a56b2de8f306dd29bddd44a72a4d2d420e1b3591cff8ba777b5eb123448`.

The final producer A03 SHA-256 is `43be79d1f680030213682bc8c8c1fd73f0057c3a4328970c1e7a4430d6cda345`.
Its Mach-O UUID is `e66253337ff83d438321b85fa1c7e0a5`.

The independent observer SHA-256 is `42b5b162c31320b6e981958c88458ab1de7fff9e8faf825edb7cb0f2293b2b2f`.
The observer uses separate code and a separate executable, but it also uses AVFoundation.

I inspected saved evidence and reran read-only relationships from the raw WAV and decoded PCM.
I did not edit runtime files, operate the GPU, or operate DaVinci Resolve.

Cross-family model review was unavailable.

## Defects found and fixed during review

### Track loading could outlive bounded PCM drop

The first implementation waited up to 1,800 seconds for an asynchronous track callback.
Dropping a stream before that callback could block while joining its worker.

`with_track_cancellable` now polls its caller every 25 milliseconds.
Cancellation calls `AVAsset.cancelLoading` and marks the callback as retired.
The callback checks that state before starting the native operation.

Tests cover cancellation before callback start and dropping PCM before the first callback.

### Local stop could replace the export failure class

The first cancellation closure set the PCM stream’s local stop flag.
That could race the export lease and replace cancellation or fencing with `native_pcm_error`.

The PCM wait now uses its local stop only for consumer ownership.
The native track helper owns callback cancellation separately.
The shared `ExportControl` remains authoritative for cancellation, lease loss, and fencing.

### Some native waits lacked export ownership

Movie decode, encoded-track inspection, and output-video verification now use cancellable track waits.
Their loops also check the shared export control.

Cancellation remains cooperative between native calls.
The library cannot forcibly interrupt a native call already executing inside AVFoundation.

### Interrupted finalization recovery verified without its new epoch

Recovery formerly called the unowned artifact verifier.
A replacement worker could therefore continue recovery verification after losing its epoch.

Recovery now passes its `ExportControl` into `movie::verify_owned`.
Verification checks the control after native reopening and before storing its verification record.
`finish_export` still requires the same epoch, running state, and no cancellation request.

Completed replay and explicit verification do not claim an export epoch.
They may store a separate fresh verification document without changing the completed artifact receipt.

### The first long binary label was wrong

The frozen A02 binary is byte-identical to A01: `d70b254654af3969ce6f9335ea18506f3708ddda319a03c14393a18ea4c3484f`.
It still reports the 240-frame limit and correctly rejected the 288-frame attempt.

`build-a02-observation-correction.json` preserves the failed build cause and corrected observation.
The successful long export uses fresh intent `long-a02` and producer A03.

## PCM ownership and clocks

`Stream::open` creates one decoder worker and a `sync_channel(2)`.
Every delivered `PcmChunk` owns interleaved stereo `f32` values.
No chunk exceeds 4,096 sample frames.

The decoder requests 48 kHz, two-channel, 32-bit float, little-endian interleaved PCM.
It rejects unexpected layout and non-finite samples.

For every nonempty native buffer, the decoder requires:

`pts.value * 48000 == decoded_prefix * pts.timescale`

This check gives the source stream one exact integer sample clock.
The decoder copies only the intersection with the requested half-open selection.

`PcmChunk.first_sample` is relative to the selected output interval.
The writer requires it to equal the next timeline sample exactly.
The Core Media sample buffer uses that value as its PTS at timescale 48,000.

The receipt distinguishes range completion from reader EOF.
The selected source stream stops after its requested endpoint and reports `reader_reached_end=false`.
The reopened output reads through native completion and reports `reader_reached_end=true`.

The evidence also records the decoded prefix, delivered sample count, chunk count, and largest owned chunk.
Chunk partitioning may vary between native reads, so replay compares stable clocks, extents, and EOF state.
Fresh verification also requires each observed owned chunk to remain within 4,096 frames.

## Backpressure, cancellation, and writer behavior

The PCM producer uses nonblocking sends with repeated stop checks.
Closing the receiver releases a producer blocked by the full channel.
`Stream::drop` marks local stop, closes the receiver, and joins the Rust worker.

The picture path retains its separate capacity-two channel.
The writer polls video and audio readiness independently instead of enforcing strict alternation.

The writer rejects empty, oversized, discontinuous, or excess audio chunks.
It requires exactly the plan’s timeline sample count before finalization.

The export lease renews independently every ten seconds.
Cancellation, lost epoch, and lease failure retain distinct control states.
The database claim is checked again before promotion and final completion.

The tests exercise PCM backpressure drop, shared export interruption, callback cancellation, lease renewal, cancellation, and fencing.
The recovery path was code-inspected; this unit did not hard-kill the A03 long export.

## Incremental output verification

The verifier opens two independent PCM streams:

- The exact selected source interval.
- The complete reopened AAC output.

It compares samples incrementally at zero offset.
It accumulates per-channel dot product and energy in `f64`.

The verifier requires exactly the planned number of output samples.
It rejects extra source or output samples.
It also requires both channel correlations to remain at least 0.99.

The product separately records compressed track evidence.
For A03, AVAssetReader groups the AAC track into 21 compressed sample buffers.
The independent MP4 table contains 565 AAC packets.
Those counts describe different APIs and are not interchangeable.

## Receipt compatibility and replay

`NativeMeasurements.streaming_audio` is optional.
Serde defaults it to `None` and omits it when absent.

A review-only deserialize-and-reserialize probe preserved historical receipt
`8e0bc864df8f07f0ddf831000ac4601d49909d927030bbe67de03b13b6d0dd53` byte for byte.
Its SHA-256 therefore remains unchanged.

The same probe preserved the new short receipt
`83e07ecc313ba1669ce03b6fab41893ca25ca4474479221101da682353a8715f` byte for byte.

Old receipts can therefore replay under the current reader without acquiring a new receipt identity.
New receipts bind source and output stream extents and endpoint evidence.

Frozen A03 also reverified the historical 206-frame schema-2 hybrid artifact without re-encoding it.
The original receipt remains `44c0c27ad1a58f22746011673d8e4d4a211c5b5cdeffcb18172d6cc73fc73be2`.
The original output remains `e487e36c6927916428085f262d530d8abdafc8a8e6f3edc5bfdf80ecaa617e94`.

The fresh verification is `5640cf1611037b4ae6994abc2775cb0bda8bd1eb3f8d0eae5244964d67055349`.
It retains the historical receipt and adds current streaming observations only to the new verification document.
Those observations contain 412,000 samples, 101 source chunks, 101 output chunks, and output EOF.

## Actual short regression

Producer A01 exercised the new streaming path against the actual mixed PNG, movie, and canonical-audio project.
That binary predates the final cancellation and frame-bound repairs.

Its exact output is:

- Output SHA-256: `71d5ae19fa0817533a193d78aab47d1c4ec53205f679f3b9085c3304b1322108`.
- Output bytes: 1,312,034.
- Revision: `1bd422f2175ce5468fe4efc24593677897570c5c04cbe0767bbac5a3f6234572`.
- Plan: `18efdaaa55867111235b174c194d99315608d04ee599f166466e11cf06f833d7`.
- Receipt: `83e07ecc313ba1669ce03b6fab41893ca25ca4474479221101da682353a8715f`.
- Fresh verification: `fe9e63746c59341dd927963687c0a62b257b81fe6659da1c03dbd036d68c30ee`.

It contains 48 H.264 frames and 96,000 decoded stereo sample frames.
The selected source and output each use 24 owned chunks, with a 4,096-frame maximum.
The output reached EOF; the selected canonical source stopped at its requested endpoint.

Its channel correlations are `0.9999705560560641` and `0.9999708586933663`.
This is numerical evidence for the actual 24-bit canonical source prefix.
It is not a listening result.

## Final A03 long proof

The exact long output is:

- Project: `native-streaming-audio-fixture-a01`.
- Revision: `a4afc9237cdc477ddc0c62023b7e0ed185a9f39bd3f72fd3f6596964d1c82423`.
- Plan: `4e5a89b00e7b5fabaafb4bf1335c1a5c3538c593765b4f5e5c818ff6bcede219`.
- Output SHA-256: `1cd3f084d467ff693856d42f3b6594b0333c2009b63265f3e27dca501b9f9d13`.
- Output bytes: 435,328.
- Receipt: `8e8de8d99960a584ced8a3f67a5647acd1ce72fd68bc92ac1966c3df14c032ce`.
- Fresh verification: `19fb8b83ebe9d1ef1522319e69002e28191175816f17da70f2152f83730c1c5c`.

The timeline is 288 frames at 24 fps and 320 by 180 pixels.
It holds one static image for exactly 12 seconds.

The synthetic source WAV SHA-256 is `5da985961720761f773e0aae2e72ba056abe2f83b11ed5c7eecd653b3d7269ff`.
The plan selects `[8191, 584191)`, which contains 576,000 stereo sample frames.

The producer source stream reports 142 chunks and a decoded prefix of 589,824 frames.
Its exact delivered range is 576,000 frames, and it does not claim whole-source EOF.

The reopened output reports 141 chunks, exactly 576,000 frames, and reader EOF.
Both observed maximum owned chunks are 4,096 frames.

The independent report SHA-256 is `f93a8fa70f091b68ae9ff4e5fe416a53ecb03036642a9dcf2e7da84fd2058b36`.
Its comparison script SHA-256 is `d10dec960dfa7c6e9c70baa3633269a6917bcc7389974f51643132cee4f156e8`.

The saved independent checks establish:

- All 288 decoded video frames and exact `n/24` PTS.
- Video and audio reader completion at EOF.
- Every output frame compared with an independent Pillow source evaluation.
- Minimum RGB PSNR of `41.847044409234186` dB.
- Exactly 576,000 decoded stereo output frames.
- No extra decoded output samples.
- Zero-offset correlations of `0.9999962748277015` and `0.9999895066983935`.
- RMSE values of `0.0007659646753412136` and `0.0013648656474181643`.
- Independent MP4 video sample count of 288.
- Raw AAC duration of 578,560 ticks, including 2,560 padding ticks beyond presentation.

I independently recomputed the output hash, exact PTS sequence, PCM length, correlations, RMSE, and receipt stream extents.
Those recomputed values agree with the saved report.

## Tests and capability inventory

The current workspace passed all 54 tests:

- 40 editor unit tests.
- 1 frame-directory verification test.
- 10 project-invariant tests.
- 3 replay-and-cleanup tests.

`cargo fmt --all -- --check` passed.
`cargo clippy --locked --all-targets -- -D warnings` passed.

Frozen A03 discovery reports the 100,000-frame implementation bound.
It also reports 4,096-frame PCM chunks, capacity-two channels, and incremental AAC verification.

The 100,000-frame value is a structural input limit.
This review did not prove throughput at that limit.
The 1,800-second deadlines apply to individual native operations, not one total export wall clock.

The Rust-owned PCM chunks are bounded.
AVFoundation sample-buffer allocation and total process peak memory remain unmeasured.

## Truthful acceptance boundary

This review accepts the bounded streaming PCM behavior and its 12-second technical fixture.

It establishes exact source selection, sample clocks, owned chunk bounds, output EOF, incremental waveform comparison, immutable receipts, and the raised structural frame limit.

The actual canonical-audio regression belongs to A01.
The final cancellation, recovery, and 100,000-frame-bound code belongs to A03.
The final A03 duration proof uses a synthetic 16-bit WAV.

The unit still supports one measured 48 kHz stereo PCM clip with unity gain and zero pan.
It does not implement mixing, resampling, automation, multiple audio clips, or channel-layout conversion.

No maximum-bound throughput or native-framework peak-memory proof exists.
No normal-speed playback or listening occurred.
Watched, heard, and creative acceptance remain false.

The fixture is not the 273-second Panja film or the hardest complete musical and action pilot.
The general compositor, source representation model, text, masks, motion, color, tenant orchestration, complete film, and final human review remain incomplete.
