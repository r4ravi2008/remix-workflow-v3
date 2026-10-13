# Implementation review A04

## Result

No P1 defect remains in the bounded three-cut native behavior unit.

Producer A07 correctly renders adjacent cuts from one picture track. It preserves the immutable source map and canonical audio interval.

The exact A03 output passes native reopening and an independent 24-check rerun. Cancellation and epoch fencing also protect promotion under real fault probes.

This result supports the next bounded editor unit. It does not establish a general compositor or the completed hybrid film.

Two P2 defects remain. Hard process death leaks the abandoned epoch's staged movie. Discovery still describes the renderer as single-clip.

The product verifier also lacks semantic cut-map measurements. Independent verification supplies that evidence for A03 only.

## Review boundary

The reviewed producer is `video-studio-producer-a07`.

Its SHA-256 is `bd56fa07cdd27d31447ed3a398c35a755bb637c96ca02aa1dd27a18ec4449214`.

The current `target/debug/video-studio` has the same SHA-256.

The reviewed product artifact has these bindings:

- Project: `panja-scratch`.
- Revision: `90b2770b84fd6c8acec758816158f40351d604b6031e5ff1844223a09b54c41a`.
- Plan: `8af87bb38295d818f3114fb7d28a4ac53f408b416be04fb8609e067d81f5cd64`.
- Output: `979dd4fcc064387ce619efa8e6122851b7e22514a299e6fe45b517875f21ccf5`.
- Output bytes: `2,105,258`.
- Artifact receipt: `9004955188b8d76d02eda2aa1c715df811b71feae722d1ca5657aab946a0487d`.
- Initial verification: `c6312e97be31820f53dcbc3524f349f47cf935e6cc698b4a27a75091a6214b68`.

All destructive probes used copied stores under `/tmp`. They did not change source files or the original project state.

## Plan and source-map ownership

The schema-2 plan owns three `VideoUse` records on track `picture`.

Their timeline intervals are `[0,16)`, `[16,32)`, and `[32,48)`.

Their source presentation ordinals are `[0,16)`, `[48,64)`, and `[96,112)`.

The plan stores all 48 ordinals explicitly. It also stores each allowed source interval.

Each interval has decode evidence measured before plan persistence. Each record reports 16 decoded samples and verified PTS.

The source closure contains the exact AV1 movie and the exact canonical WAV. No external path substitutes for either asset hash.

`decode_timeline` opens a native reader for each clip. It checks each decoded PTS against the immutable source index.

The decoder copies each BGRA image into an owned Rust byte vector. Only owned bytes cross the bounded channel.

`Pixels::into_native` allocates and fills a new native pixel buffer on the writer thread. Native reader objects remain inside their callback.

The bounded channel holds two evaluated frames. This keeps decoded-frame memory bounded for the current dimensions.

The writer advances video and audio whenever each input is ready. It no longer requires strict alternating readiness.

The saved A05 sample confirms the old deadlock. Its decoder was blocked on a full channel while the writer waited inside `ready`.

The independent stream pump removes that circular wait. Both A02 and A03 complete with the same declared cut map.

## Exact A03 technical evidence

I reran the independent verifier against A03 and producer A07. The rerun generated frames only in a temporary directory.

All 24 checks passed. The checks include receipt bytes, producer identity, native codecs, sample tables, source-map coverage, and immutable receipt identity.

All 48 decoded output PTS values equal `n/24`. Every output frame matches its declared source ordinal.

The minimum every-frame PSNR is `43.8891106242491` dB. It occurs at timeline frame 32, source ordinal 96.

The raw compressed H.264 interval is `50/600` through `1250/600`. Its span is exactly two seconds.

The decoded presentation clock still starts at zero. Compressed H.264 reordering does not replace decoded PTS authority.

The output decodes to exactly 96,000 stereo PCM frames at 48 kHz.

The raw AAC interval contains 98,304 ticks. Native reopening trims 2,304 encoder-padding frames.

Waveform lag is zero on both channels. Correlations are `0.9999705561508012` and `0.999970858626734`.

The receipt's AAC `sample_buffers: 1` remains callback aggregation. It is not an AAC packet count.

No normal-speed watch or listen occurred. Watched, heard, and creative acceptance remain false.

## Source-time and audio authority

The movie asset is AV1 hash `a2247e96ab4335eb6b365ef52b6203e53377c6cf317ebb2e156789e6bd470b7f`.

Its index contains 2,277 presentation samples. The selected ranges use measured PTS at the actual 12,288-tick source clock.

The selected ranges have both plan-time decode proof and render-time PTS checks. A03 also has an independent decoded-frame map.

This resolves source timing for the exact three ranges. It does not prove arbitrary retiming, orientation, aperture, or color handling.

The canonical audio asset is hash `cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8`.

It is 24-bit interleaved PCM stereo at 48 kHz. Its measured extent is 13,104,000 frames, or 273 seconds.

The plan consumes source samples `[0,96000)`. The timeline consumes the same exact interval.

The older 16-bit, 261.56-second metadata WAV is not an authority in this plan.

Channel labels remain an explicit stereo interpretation. The source descriptor still reports `measured_channel_labels: null`.

Correlation proves channel-preserving waveform alignment. It does not prove the semantic left/right labels or listening acceptance.

## Cancellation, fencing, and recovery probes

The saved `export-native-cuts-v1` attempt was cancelled after the A05 stall.

Its job and attempt rows are `cancelled`. Its caller received `export_cancelled`, and its owned cut stage is absent.

I repeated late cancellation with producer A07 in a copied store. The producer was paused after claiming epoch 1.

Cancellation then set `cancel_requested`. The resumed producer returned `export_cancelled`.

The copied job and attempt became `cancelled`. No stage for that intent remained.

I also forced an expired epoch-1 owner while that producer was paused. A second A07 process claimed epoch 2.

Epoch 2 completed and promoted its exact output. The resumed epoch-1 process returned `worker_fenced`.

The epoch-1 attempt became `fenced`. The epoch-2 attempt remained `completed`, and neither owned stage remained.

These results confirm the late-cancellation fix. They also confirm that an old worker cannot overwrite a newer completed epoch.

I then killed an A07 producer after it wrote 1,346 staged bytes. Epoch 2 recovered and completed the same intent.

The killed attempt became `abandoned`. The recovered attempt became `completed`.

The epoch-1 staged file still existed after recovery. This is the first P2 finding below.

## Actionable findings

### P2: takeover does not reclaim an abandoned epoch's stage

The current error path removes its own stage after handled cancellation, fencing, or failure.

`SIGKILL` cannot run that path. A later epoch renders and promotes safely, but it leaves the older stage behind.

The original store already contains two historical staged movies from `export-native-roundtrip-v5` and `v6`.

Repeated interruption can consume full-render disk space. Future tenant sharing would also require tenant-scoped cleanup ownership.

After a new epoch claims the job, reclaim lower-epoch stages for that exact project and intent.

Cleanup must never glob unrelated projects or active epochs. Record cleanup failure separately from render correctness.

### P2: discovery understates the implemented cut scope

Producer A07 still reports `one movie clip` for `native_movie_export`.

The implementation accepts one picture track with adjacent, complete source-bound clips. A03 proves three clips.

Update discovery to name that exact scope. Keep one PCM clip, exact dimensions, unity gain, zero pan, and 240-frame limits.

The scope should also retain the planned status for layers, transforms, masks, color, motion, and text.

### P2: product verification does not measure the semantic cut map

`movie::verify` checks codecs, clocks, frame count, dimensions, decoded audio extent, and audio correlation.

It does not compare output pixels with `VideoUse.presentation_ordinals`.

The external verifier proves A03's complete cut map. The product's `ArtifactVerification` does not retain that measurement.

A valid H.264/AAC file with the wrong source frames could pass `project.verify-export` alone.

For the cut profile, persist independent source-map evidence against the exact plan and output hash.

For later effects, use operation-aware review evidence. Do not treat source-pixel PSNR as a universal compositor test.

## General-editor boundary

The accepted unit is one picture track with adjacent cuts and complete coverage.

It also requires one complete 48 kHz stereo PCM clip with identity gain and pan.

The runtime still lacks layered composition, transitions, masks, motion, color, text, scaling, and aperture transforms.

It also lacks exact-file human review, tenant application orchestration, and full-film policy evaluation.

Source orientation and color metadata remain unverified. These limits matter before mixing broader footage.

The Panja hybrid film is not produced or accepted. A03 is a two-second technical artifact.

## Validation

`cargo test --workspace --locked` passed 17 tests.

`cargo clippy --workspace --all-targets --locked -- -D warnings` passed.

`cargo fmt --all -- --check` passed.

The concurrent first-open migration test passed 20 additional fresh-store runs.

The independent A03 rerun passed all 24 technical checks against producer A07.

No source file, original database, original receipt, or original artifact was changed during this review.

Cross-family model review was unavailable. This document does not claim one.
