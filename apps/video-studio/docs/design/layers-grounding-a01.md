# Picture layers grounding A01

Status: source-grounding only. This report follows the current direct CLI to native export path and identifies the narrow insertion point for picture layers. It does not change runtime code, stored artifacts, GPU state, or Resolve state.

## Overview

The current native movie path evaluates one complete BGRA canvas per timeline frame. It sends those owned pixels to one H.264 `AVAssetWriterInput`. The model can already contain more than one `VideoTrack`, but `movie::validate_profile` deliberately accepts one adjacent picture track. There is no layer order, alpha blend, mask, transform, or sparse-overlay meaning in the executable path.

Picture layers therefore belong between native source decode and `EvaluatedFrame`. The layer executor must decode the exact source ordinals selected by the immutable plan, condition each source into owned pixels, composite layers in a stored order, and send one flattened canvas frame to the existing writer. Adding another AVAssetWriter picture input would produce parallel tracks. It would not implement deterministic picture composition.

The current ownership chain is:

```text
CLI JSON
  -> Project::commit
  -> immutable Snapshot revision and CAS source blobs
  -> Project::prepare_export
  -> immutable ExportPlan plus preparation decode evidence
  -> movie::write
       -> decode_timeline (bounded picture channel)
       -> encode_frames (native AVAssetWriter)
  -> owned staging movie
  -> immutable ArtifactReceipt and content-addressed artifact
  -> movie::verify / ArtifactVerification reopening the movie
```

The plan remains the authority for source selection. The writer remains the authority for output timestamps. A future compositor must not re-probe, renumber, or substitute a source after planning.

## The current call trace

1. **The direct CLI selects one operation.** `crates/cli/src/main.rs:9-94` opens the store and dispatches `project.create`, `project.commit`, `project.prepare-export`, `project.export`, `project.verify-export`, cancellation, and source verification. `main` prints a JSON envelope at `main.rs:97-108`. The inventory at `main.rs:15` states that the native renderer has no subprocess renderer and currently supports H.264/AAC, adjacent movie clips, opaque PNG holds, one 48 kHz stereo PCM clip, and a 128 MiB owned BGRA frame bound.

2. **Commit creates the immutable snapshot.** `crates/editor/src/project.rs:393-510` hashes the request, reopens the requested base revision, stages every import, checks the expected origin/hash/byte count, applies canonical audio and timeline changes, calls `Snapshot::validate`, hashes the serialized snapshot, and appends the revision in one immediate SQLite transaction. `project.rs:159-238` stores each accepted source in `blobs/<sha256>` and keeps the measured descriptor and lineage beside the immutable bytes. A layer source must follow this same path. A path string alone is not a layer identity.

3. **Preparation resolves the timeline into an immutable plan.** `project.rs:241-277` calls `plan::compile`, validates owned pixel extents, calls `movie::verify_inputs`, records movie and image decode evidence, recomputes the plan hash, verifies the transitive source closure, and persists the plan. A replay at `project.rs:279-320` accepts only plan schema 2 or 3 and verifies the plan's document hash. A future layer plan must carry its order, coverage, source references, and blend inputs before this persistence point.

4. **The compiler binds timeline frames to exact source samples.** `crates/editor/src/plan.rs:28-83` defines `VideoUse` with the clip, track, timeline span, allowed source range, presentation ordinals, and framing. `plan.rs:92-341` selects a movie sample by stored presentation time, records `SampleTiming.ordinal`, and rejects a selection whose stored duration does not cover its output frame. Images use ordinal zero and a hold cadence. The compiler also checks complete picture coverage and exact canonical audio coverage.

5. **Preparation freshly decodes selected input prefixes.** `crates/editor/src/movie.rs:808-929` reopens each planned movie with an AVAssetReader configured for 32-bit BGRA, walks samples in source order through the selected end ordinal, checks each decoded PTS against the immutable `SampleTiming`, checks dimensions, and stores `SourceDecodeEvidence`. Images are fully decoded and hashed separately. This proves native input coverage for the prepared plan; it does not prove a full final movie watch or listening review.

6. **`movie::write` starts one bounded picture worker and one PCM worker.** `movie.rs:142-185` validates the profile, opens `pcm::Stream`, creates `mpsc::sync_channel(2)`, spawns `decode_timeline`, and invokes `encode_frames` inside an Objective-C exception boundary. The worker sends `EvaluatedFrame` values. The encoder receives them in timeline order. A future compositor should run inside `decode_timeline` or a bounded stage immediately before its `send`, so `encode_frames` keeps one stable input contract.

7. **`decode_timeline` decodes by the planned ordinal, not by a guessed frame number.** `movie.rs:192-328` sorts `VideoUse` by timeline start, opens one reader per movie use, and walks `copyNextSampleBuffer` until the exact requested source ordinal. It checks the observed PTS against `plan.source_closure[asset].descriptor.samples[ordinal].pts`, copies the native CVPixelBuffer into owned Rust `Pixels`, applies framing, and sends the frame. A layer implementation should perform the same check for every active layer, then composite the resulting source pixels into one canvas before sending one `EvaluatedFrame`.

8. **`encode_frames` owns the output writer and exact output clocks.** `movie.rs:432-621` creates an H.264 video input, an AAC audio input, and a BGRA pixel-buffer adaptor. It appends each received canvas with `CMTime::new(video_frame * frame_rate.denominator, frame_rate.numerator)`. It builds interleaved float stereo PCM sample buffers with one `1/48000` duration per sample and the first sample as the audio PTS. It ends the session at `timeline_sample_frames / 48000`, finishes writing, and requires `AVAssetWriterStatus::Completed`.

9. **The staged movie is promoted only after fresh native readback checks.** `crates/editor/src/exports.rs:754-942` claims a fenced export epoch, renews a lease, creates an owned stage, writes the movie, fsyncs it, re-verifies source closure, calls `movie::verify_owned`, hashes the stage, stores an immutable schema-2 artifact receipt, hard-links the movie into `artifacts/<sha256>.mp4`, and marks the export complete. It then calls `verify_artifact` again. `exports.rs:547-598` reconstructs the request and plan from the database for a later `project.verify-export` call. `exports.rs:627-709` stores receipt JSON by its document hash and rejects changed receipt bytes. `exports.rs:711-751` rehashes the movie and compares reopened technical measurements.

## Exact source ordinals and clocks

`media::inspect_track` in `crates/editor/src/media.rs:228-391` obtains the source sample list from `AVAssetReaderTrackOutput::copyNextSampleBuffer`. It sorts samples by output presentation time and assigns `ordinal = index`. The ordinal is an index in the measured native presentation-sample table. It is not a compressed packet number, a decode-order index, or a timeline frame number.

`plan::compile` maps each target timeline frame to a selected `SampleTiming.ordinal`. For `Cadence::SourcePresentationTime`, it starts from the first selected source PTS, advances in the requested output frame clock, and finds the stored sample with that exact PTS. For `Cadence::Hold`, it repeats the explicit ordinal. A future layer plan must retain, per layer use, at least:

```text
(immutable asset hash, clip id, source range, timeline span,
 exact presentation ordinal, measured source PTS, framing/composite inputs)
```

Do not renumber ordinals after filtering a layer. Do not replace an unsupported source with another representation under the same asset identity. An alternate H.264 representation must be imported as its own immutable asset and bound by an explicit source map.

At execution, `decode_timeline` reads samples sequentially until each planned ordinal and checks the actual reader PTS against the stored PTS. The flattened output frame has a separate timeline ordinal. The writer assigns that output PTS from the requested frame rate. Audio has its own sample clock and starts at sample zero.

## Where a compositor integrates

The current domain types are in `crates/editor/src/model.rs:364-429`:

- `VideoClip` owns a timeline span, asset, source range, cadence, and optional framing.
- `VideoTrack` owns an ordered clip list.
- `Timeline` owns video tracks, audio tracks, and the frame count.
- `Snapshot::validate` at `model.rs:431-647` checks per-track bounds and non-overlap.

`VideoTrack` order alone is not yet a composition order. `movie::validate_profile` at `movie.rs:73-139` requires one video source, all clips on `plan.video[0].track`, adjacent clips, and no layer overlap. It must be replaced by explicit bottom-to-top track/layer order and a compositing policy before sparse overlays are accepted.

The smallest integration preserves the existing decode and write boundaries:

1. `plan::compile` expands every active layer into immutable per-frame source selections. It records stable bottom-to-top order, destination geometry, opacity, blend mode, and any mask or transform inputs. It validates coverage and a decoder/pixel budget before execution.
2. A bounded compositor reads the selected source frames. Each movie source is decoded to BGRA and each static source is decoded to owned pixels. It checks each source PTS and source geometry before compositing.
3. The compositor writes one owned BGRA canvas for the timeline frame. It sends one `EvaluatedFrame` to the existing capacity-two channel. The writer remains unaware of layer count.
4. The existing writer, receipt, and reopen verifier prove only the flattened canvas. Layer-specific evidence must also retain the source ordinals, layer order, and blend parameters used to make each frame.

This preserves ownership: the plan owns selection, the decoder owns native readers, the compositor owns temporary Rust pixels, and the writer owns the output movie. It also prevents a second layer reader from bypassing the immutable plan.

## Why black contain bars cannot be sparse overlays

`crates/editor/src/framing.rs:69-153` allocates a full canvas, initializes every pixel to `[0, 0, 0, 255]`, and then writes the fitted source into it. The test at `framing.rs:174-197` explicitly expects opaque black contain bars. `Pixels` in `crates/editor/src/pixels.rs:13-127` is a four-byte BGRA buffer with no separate alpha policy, and the image validator currently rejects non-opaque alpha.

Therefore a contained frame is an opaque full-canvas image. If it is placed above a background layer, its black bars overwrite the background. Reusing that output as a sparse overlay would change the picture. Sparse overlays require an explicit alpha-capable pixel representation, a defined premultiplication rule, and a compositor blend operation. “Black” is a color value. It is not transparency.

## Ownership, lifetimes, and cancellation

The native boundaries have these ownership rules:

| Object or data | Current owner and lifetime | Layer implication |
| --- | --- | --- |
| CAS source | Read-only hard link under `blobs`; verified by hash and byte count | A layer keeps the immutable asset hash and never owns a mutable source path. |
| `AVAsset`, track, reader, output | `with_track_cancellable` runs the native operation in the media completion callback; the Rust worker waits for its send result and does not necessarily own the native objects on its own thread | Do not send Objective-C media objects through the Rust channel. Send owned pixels and scalar evidence. |
| `CMSampleBuffer` | Returned retained by `copyNextSampleBuffer` and released when its Rust wrapper drops | Copy the selected CVPixelBuffer before the sample buffer leaves the reader scope. |
| `CVPixelBuffer` | `Pixels::copy` locks read-only and copies row-by-row; `Pixels::into_native` creates a separate native BGRA buffer | A compositor can retain Rust `Pixels`; it must not hold a borrowed lock across channel operations. |
| `PixelLock` | RAII unlock with the same flags in `pixels.rs:33-49` | Every lock path, including errors and panics, must unlock. |
| writer pixel buffer | Apple says the writer retains the buffer after append | Do not mutate or reuse the native buffer after `appendPixelBuffer_withPresentationTime` returns. |
| reader/writer | `ReaderGuard` and `WriterGuard` at `movie.rs:48-61` cancel unfinished native operations on drop | A layer decoder must have the same guard behavior for every reader. |
| PCM worker | `pcm::Stream` owns a worker and capacity-two channel; `Drop` stops and joins it | Layer cancellation must not leave a decoder or compositor thread blocked. |
| export | `ExportControl` at `exports.rs:383-416` carries cancellation/fencing; `ExportLease` renews ownership | Check control between source samples, layers, frames, and writes. |
| stage | `ExportStage` records owner, epoch, and allowed files; cleanup is ownership-checked | A failed layer export must leave only reclaimable owned staging files. |

`media::with_track_cancellable` at `media.rs:73-203` keeps AVFoundation setup and callback objects in the native completion callback, where `operation(&track)` also runs. The Rust decoder worker waits for the callback to send its `Result`; the native objects and operation therefore live in the callback scope, not necessarily on that worker thread. The function catches Objective-C exceptions, checks the deadline/control, and calls `asset.cancelLoading` on cancellation. The layer path should use this existing cancellation shape rather than inventing a blocking native call.

`decode_timeline` uses blocking `send` on the capacity-two channel. When `encode_frames` returns, `movie::write` drops its receiver before joining the worker, so a blocked send is released during teardown; this is not a guaranteed current deadlock. A layer implementation should still make sends cancellation-aware, such as a short `try_send` loop with `ExportControl::check`, before parallel layer teardown needs prompt cancellation across several readers and compositor workers.

## Pixel memory bound and layer budget

`pixels::extent` at `crates/editor/src/pixels.rs:19-31` limits one owned frame to `128 * 1024 * 1024` bytes. `Pixels::copy` then owns a tight BGRA `Vec<u8>`; `framing::apply` can hold both source and canvas pixels while resampling. `movie::validate_pixel_extents` at `movie.rs:63-71` checks the canvas and each declared picture source against that bound.

This is a per-frame bound. It is not a process-wide or per-export aggregate bound. The current channel can retain two evaluated frames, the sender can hold another frame while blocked, static image holds can clone one full frame per timeline output, and Core Video/AVAssetWriter can hold native buffers. Multiple active layers multiply source and intermediate memory. A real layer plan needs an explicit peak owned-pixel estimate, a decoder count, and a compositor scratch limit. The executor should reject a plan before opening readers when the estimate exceeds those limits.

## Serialization compatibility

The model types use `serde(deny_unknown_fields)` throughout `crates/editor/src/model.rs`. The snapshot is schema 1. Plans are schema 2 for movie-only inputs and schema 3 when opaque images are present. `project.rs:301-307` and `exports.rs:559-568` accept only plan schemas 2 and 3. Artifact receipts are schema 2 and are checked by `exports.rs:681-707`.

An old plan must keep its exact JSON body, content hash, and one-track meaning. Adding a `layers` field to the current plan and silently interpreting multiple tracks would violate that boundary. The safe compatibility choices are:

- Keep old schema 1 snapshots and old plans readable with their current semantics.
- Introduce a new snapshot/plan schema for explicit layer order, alpha, and blend inputs. A layer plan should be rejected by old readers through the existing unsupported-schema path.
- Introduce a new receipt schema when the receipt records layer evidence. Keep the old schema-2 receipt immutable and verifiable.
- Use `#[serde(default)]` and `skip_serializing_if` only for genuinely optional additions whose absent value has exactly the old meaning. Because `ContentHash::document` hashes `serde_json::to_vec`, changing serialized fields changes identity even when Rust defaults appear equivalent.
- Preserve source representation maps explicitly. A native decoder failure for AV1 or VP9 cannot trigger an unrecorded H.264 substitution.

## Native API and dependency pointers

The installed SDK and generated objc2 bindings provide the required native primitives. These are pointers for the eventual implementation, not runtime changes in this report.

| Operation | Rust binding | SDK/header pointer |
| --- | --- | --- |
| Read the next sample | `AVAssetReaderOutput::copyNextSampleBuffer` in `objc2-av-foundation-0.3.2/src/generated/AVAssetReaderOutput.rs:58-72` | `AVAssetReaderOutput.h:81-100` |
| Request decoded BGRA | `AVAssetReaderTrackOutput::assetReaderTrackOutputWithTrack_outputSettings` in `.../AVAssetReaderOutput.rs:168-217` | `AVAssetReaderOutput.h:195-241` |
| Clip contiguous interleaved PCM | `CMSampleBuffer::copy_sample_buffer_for_range` in `objc2-core-media-0.3.2/src/generated/CMSampleBuffer.rs:928-997` | `CMSampleBuffer.h` sample-range copy declarations |
| Rebuild a PCM buffer | `CMBlockBuffer::create_with_memory_block` at `CMBlockBuffer.rs:213-245`, then `CMSampleBuffer::create_ready` at `CMSampleBuffer.rs:526-536` | `CMBlockBuffer.h:181-245`, `CMSampleBuffer.h:359-446` |
| Copy PCM bytes | `CMBlockBuffer::copy_data_bytes` at `CMBlockBuffer.rs:638-653` | `CMBlockBuffer.h` copy-data declaration |
| Append audio | `AVAssetWriterInput::appendSampleBuffer` at `AVAssetWriterInput.rs:300-337` | `AVAssetWriterInput.h:300-337` |
| Append BGRA | `AVAssetWriterInput::appendPixelBuffer_withPresentationTime` at `AVAssetWriterInput.rs:909-915` | `AVAssetWriterInput.h:612-634` |
| Finish native writing | `startSessionAtSourceTime`, `endSessionAtSourceTime`, `finishWritingWithCompletionHandler` in `AVAssetWriter.rs:334-425` | `AVAssetWriter.h:316-355,393-404` |
| Lock/copy pixels | `CVPixelBuffer` lock and base-address methods used by `pixels.rs` | `CVPixelBuffer.h:191-203,387-432` |

The current dependency features are intentionally narrow. `objc2` enables `exception`; `objc2-foundation` enables standard collection/string/URL/error/object types; `objc2-av-foundation` enables AVAsset, track, reader, writer, settings, blocks, Core Media, Core Video, Core Graphics, and Core Foundation; `objc2-core-media` enables block buffers, format descriptions, sample buffers, times, ranges, Objective-C, audio types, and video; `objc2-core-video` enables CVBase/CVBuffer/CVImageBuffer/CVPixelBuffer/CVReturn; `objc2-core-audio-types` enables CoreAudio base types. There is no FFmpeg, libav, or subprocess renderer dependency.

For exact PCM clipping, `copy_sample_buffer_for_range` is the smallest native copy when the input is contiguous interleaved PCM. Its generated binding documents that non-interleaved audio is unsupported. If the source buffer has extra frames or a non-interleaved layout, copy the selected bytes with `CMBlockBuffer::copy_data_bytes`, create a new block buffer, and call `CMSampleBuffer::create_ready` with exactly 48,000 samples, a `CMSampleTimingInfo` duration of `1/48000`, and a PTS equal to the selected first sample. `create_copy_with_new_timing` changes timing metadata; it does not clip the underlying audio data. Validate sample count and endpoint after the copy.

The relevant primary API references are [CMSampleBuffer](https://developer.apple.com/documentation/coremedia/cmsamplebuffer), [CMSampleTimingInfo](https://developer.apple.com/documentation/coremedia/cmsampletiminginfo), [AVAssetReaderTrackOutput](https://developer.apple.com/documentation/avfoundation/avassetreadertrackoutput), [AVAssetWriter](https://developer.apple.com/documentation/avfoundation/avassetwriter), and [AVAssetWriterInputPixelBufferAdaptor append](https://developer.apple.com/documentation/avfoundation/avassetwriterinputpixelbufferadaptor/append(_:withpresentationtime:)). The checked local headers are under `/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/System/Library/Frameworks/`.

## Reopen and PCM proof

The fresh product readback path is `project.verify-export` in `cli/src/main.rs:51-55`, then `Project::verify_export` in `exports.rs:547-598`. It reconstructs the stored plan, verifies source closure and the immutable receipt, reopens the output, and calls `verify_artifact`. This is fresh readback through the same product library, not an independent implementation. The separate frozen observer at `apps/video-studio/experiments/native-media` uses AVFoundation too, but it provides a distinct implementation for comparison. The movie verifier at `movie.rs:1013-1151` checks codec, frame count, BGRA output PTS/dimensions, and audio waveform comparison. `compare_audio_streams` at `movie.rs:931-1011` reopens source and output PCM, checks chunk continuity and exact sample count, and computes per-channel correlation.

For the canonical 48 kHz stereo WAV, `pcm::Stream` at `crates/editor/src/pcm.rs:71-192` owns a bounded worker and `pcm.rs:201-369` decodes interleaved float32 chunks with PTS continuity. The output-side reader uses the same linear PCM conversion. This is a complete waveform comparison path within the product library when the stream reaches terminal evidence and the comparison checks source endpoint, output endpoint, frame count, and correlation. Use the frozen observer for a separate implementation comparison. A nil reader output is only acceptable for this preserved WAV fixture after the descriptor proves it is linear PCM; it is not a general compressed-audio rule.

The smallest real-media executable experiment is a one-second export with the preserved canonical WAV and the explicit native H.264 representation:

1. Run the existing binary's `discover` operation and confirm `rendererSubprocess:false`, H.264/AAC support, the 128 MiB frame bound, and the explicit unsupported VP9 capability.
2. Commit one H.264 movie asset and the preserved 48 kHz stereo WAV into a fresh project revision. Keep the original AV1/VP9 bytes as separate immutable assets if they are part of lineage.
3. Prepare a 24-frame, 24 fps export. Require preparation evidence to name every selected movie ordinal and PTS.
4. Export through `project.export`, then run `project.verify-export` with the same intent. Require `avc1`, `aac `, 24 video frames, 48,000 output PCM frames, a completed artifact receipt, and fresh video/audio readback measurements. Use the frozen observer when an independent implementation comparison is required.
5. Run the same probe against AV1 and VP9 only to preserve the observed native capability result. Do not make an alternate H.264 asset look like the unsupported source.

This experiment exercises the real CLI, CAS, plan, native reader, BGRA path, writer, staging, receipt, reopen, and PCM comparison without FFmpeg or a renderer subprocess. It proves the existing flattened path. It does not prove alpha composition, sparse layer coverage, arbitrary rate handling, color metadata, playback, listening, or creative acceptance.

## Gotchas and proof boundary

- The source sample table and output sample table are different clock domains. Store both. Never compare a source ordinal with an output frame index without the plan mapping.
- `AVAssetReader` can return marker-only buffers with zero samples. The existing inspection rejects ambiguous movie buffers. A layer decoder must retain that check.
- The writer retains an appended pixel buffer. `Pixels::into_native` must finish its copy before append, and no code may mutate that buffer afterward.
- Objective-C exceptions are not Rust `Result` values. Keep the existing `objc2::exception::catch` boundary around native reader/writer operations.
- Cancellation must stop readers, unblock bounded workers, release native buffers, and join threads before stage cleanup. A cancellation request is not an independent proof of a clean writer finish.
- Native framework features and codecs remain runtime claims. AV1 first-sample success does not prove full decode. VP9 currently returns AVFoundation `-11833` for the bound source. H.264 alternate representation, AAC output, BGRA conversion, and every future alpha/blend path require a real-media run.
- Technical reopen evidence does not replace normal-speed visual review, listening, or creative acceptance.

## Where the implementation lives

- CLI boundary: `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/cli/src/main.rs`
- Revision, CAS, and plan persistence: `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/project.rs`
- Snapshot and timeline model: `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/model.rs`
- Plan compilation and source ordinals: `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/plan.rs`
- Native probing and cancellation: `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/media.rs`
- Pixel ownership and framing: `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/pixels.rs` and `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/framing.rs`
- Bounded native movie decode, write, reopen, and audio comparison: `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/movie.rs`
- PCM stream: `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/pcm.rs`
- Export claims, immutable receipts, leases, cancellation, and promotion: `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/exports.rs` and `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/export_stage.rs`
