# Native movie and audio feasibility

The proposed first path is macOS AVFoundation through Rust-owned Objective-C bindings.
It reads real movie samples, renders full frames, mixes PCM, and writes one interleaved movie.

This path uses no FFmpeg executable, libav library, subprocess renderer, or old runtime.

The checks below establish API and fixture feasibility.
They do not establish an implemented Rust renderer or creative acceptance.

## Grounded host observations

These observations were made on 2026-10-05 in America/Los_Angeles.

| Item | Observed state | Meaning |
| --- | --- | --- |
| Host | macOS 26.0.1, Apple Silicon | The intended native frameworks are present. |
| SDK | Command Line Tools macOS SDK 26.1 | AVFoundation, Core Media, Core Video, Core Image, Core Text, and Metal headers are available. |
| Rust | `rustc 1.94.0`, target `aarch64-apple-darwin` | Rust can build and link native macOS crates on this host. |
| Rust bindings | `objc2-av-foundation`, `objc2-core-media`, `objc2-core-video`, `objc2-core-image`, `objc2-core-text`, and `objc2-metal` 0.3.2 are published | The required classes and C APIs have current Rust binding surfaces. |
| Offline Metal compiler | `xcrun -f metal` and `xcrun -f metallib` fail | The installed Command Line Tools cannot build offline Metal shader libraries. |
| Native frameworks | All six framework bundles exist under `/System/Library/Frameworks` | Runtime linkage is available. |

The installed AVFoundation headers expose `AVAssetReader`, `AVAssetReaderTrackOutput`, `AVAssetWriter`, `AVAssetWriterInput`, and `AVAssetWriterInputPixelBufferAdaptor`.
The installed Core Media headers expose exact `CMTime` and sample-buffer timestamps.

The published [`objc2-av-foundation` bindings](https://docs.rs/objc2-av-foundation/0.3.2) expose those reader and writer methods.
The published [`objc2-core-media` bindings](https://docs.rs/objc2-core-media/0.3.2) expose `CMTime` and `CMSampleBuffer` features.

Apple documents AVAssetReader and AVAssetWriter as its sample-level media reading and writing APIs.
AVAssetWriter supports interleaved tracks and MPEG-4 output.
See [Media reading and writing](https://developer.apple.com/documentation/avfoundation/media-reading-and-writing) and [AVAssetWriter](https://developer.apple.com/documentation/avfoundation/avassetwriter).

## Actual Panja media probes

Native AVFoundation probes loaded the current files and inspected their real format descriptions.
The probes then requested the first BGRA pixel buffer through `AVAssetReaderTrackOutput`.

| Asset | SHA-256 | Native format | Native decode result |
| --- | --- | --- | --- |
| `references/ePOglweqy7o.mp4` | `a2247e96ab4335eb6b365ef52b6203e53377c6cf317ebb2e156789e6bd470b7f` | AV1, 1920×1080; nominal rate reports 12 fps | First 1920×1080 BGRA samples decoded. Their PTS values advance by `512/12288`, exactly 1/24 second. |
| `references/AVf7upKp7TM.mp4` | `b2845509598401915f274cd4c962872280c031156346dadfd02e347a76af5e3d` | VP9, 1920×1080, about 24 fps | Reader failed with `AVFoundationErrorDomain -11833 Cannot Decode`, underlying `-12906`. |
| `R6-REAL-06-edit.mov` | Existing edit proxy | ProRes 4444, 1920×1080, 24 fps | First sample decoded. |
| `LW02-OUT-motion-r5-a01-aspect-r5b-edit.mov` | Existing transformation proxy | ProRes 4444, 1920×1080, 24 fps | First sample decoded. |
| Preserved R23 film | `1aa59625f61a496e199f3f21fa72867548d185bd3aab5504a299b635e2341301` | H.264, 2560×1440, 24 fps | First sample decoded. |
| Preserved reprise master | `cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8` | 24-bit, 48 kHz stereo linear PCM, 13,104,000 samples | Asset duration is exactly 273 seconds. |

The AV1 file also proves that nominal rate and container duration can disagree with sample timing.
AVFoundation reports a 189.75-second asset duration and 12 fps nominal rate.
Decoded PTS advances at 24 samples per second.
The fragmented MP4 `mdhd` duration is 94.875 seconds.

Sample timestamps are timing authority.
Nominal rate and asset duration remain measured descriptors and mismatch warnings.

The VP9 failure is a design constraint.
A filename extension cannot establish decode support.

The project model therefore separates preserved source authority from the selected native representation.
An unsupported original remains in lineage.
A decodable representation needs its own hash, sample map, and verification receipt.

The editor must fail `unsupported_codec` when no verified representation exists.
It must not invoke a fallback process or silently use an unrelated proxy.

## Concrete native path

### 1. Import and probe

The aggregate opens the caller file once.
It hashes and copies the same byte stream into content-addressed storage.

The macOS adapter creates an `AVURLAsset` for the owned blob.
It loads tracks and format descriptions.
It records:

- Container and codec identifiers.
- Display and coded dimensions.
- Clean aperture and preferred transform.
- Color primaries, transfer function, and YCbCr matrix.
- Native time base, presentation timestamps, decode timestamps, and sample durations.
- Audio sample rate, channel layout, and sample count.

The adapter builds a presentation-order sample index.
Timeline edits use sample ordinals and integer native ticks.

Nominal frame rate is descriptive metadata.
It never defines exact source boundaries.

### 2. Decode source video and audio

For video, `AVAssetReaderTrackOutput` requests an uncompressed pixel format.
The first unit uses BGRA to reduce adapter complexity.

For audio, `AVAssetReaderTrackOutput` requests linear PCM.
The Rust mixer receives sample blocks with exact presentation times.

Apple documents AVAssetReader as a reader for file-based media and track outputs.
See [AVAssetReader](https://developer.apple.com/documentation/avfoundation/avassetreader).

The decoder seeks before the selected source sample when keyframe preroll is required.
It discards decoded samples until the selected presentation ordinal.
The receipt records the requested and consumed sample range.

### 3. Evaluate and composite video

The Rust core evaluates one output frame at an integer frame index.
It maps that frame through the clip's exact retime knots.

The first correct compositor can use CPU BGRA surfaces.
This keeps semantics under Rust ownership and avoids an unavailable offline Metal compiler.

Core Image can provide a later native acceleration adapter.
Apple documents rendering a `CIImage` into a `CVPixelBuffer` or Metal texture.
See [CIContext](https://developer.apple.com/documentation/coreimage/cicontext).

Core Text shapes exact Unicode into glyph runs.
Core Graphics rasterizes those runs into the composition surface.
Apple defines a Core Text run as glyphs with shared attributes and direction.
See [CTRun](https://developer.apple.com/documentation/coretext/ctrun).

The project binds every font file by content hash.
The text adapter disables implicit font fallback.
Missing glyph coverage is a validation error.

### 4. Mix audio

The Rust core mixes decoded PCM at the project sample rate.
Clip starts, ends, gains, pans, and fades use integer sample positions.

Frame and sample clocks meet through checked rational conversion.
At 24 fps and 48 kHz, each frame spans exactly 2,000 audio samples.

The first unit supports identity rate and explicit resampling.
Time stretch and pitch preservation remain separate capabilities.

### 5. Encode and mux

The macOS adapter creates one `AVAssetWriter` for MP4.
It adds one compressed video input and one compressed audio input.

The video input requests H.264.
An `AVAssetWriterInputPixelBufferAdaptor` receives composed pixel buffers.
The presentation time for output frame `n` is exact `CMTime(n * denominator, numerator)`.

Apple documents the pixel-buffer append time as relative to the writer session start.
See [append pixel buffer](https://developer.apple.com/documentation/avfoundation/avassetwriterinputpixelbufferadaptor/append%28_%3Awithpresentationtime%3A%29).

The audio input requests AAC.
Rust supplies linear PCM sample buffers at exact sample presentation times.

The coordinator respects `readyForMoreMediaData` for both inputs.
It marks each input finished before it finalizes the writer.

The classic Objective-C pixel-buffer adaptor remains available in SDK 26.1.
Its Swift projection is deprecated in favor of the new receiver API.
The Rust binding currently exposes the Objective-C adaptor.
The framework adapter hides this choice from the core.

### 6. Reopen and verify

The aggregate does not promote the output after `finishWriting` alone.

It reopens the staged movie and checks:

- Container, video codec, and audio codec.
- Video frame count and every presentation timestamp.
- Dimensions, orientation, clean aperture, and color tags.
- Audio start, sample rate, channel layout, decoded coverage, and encoder trim.
- Expected timeline end and A/V alignment.
- Output byte count and SHA-256.

H.264 and AAC are lossy.
The verifier must not require decoded pixels or PCM to equal source bytes.

Video uses declared decoded-image tolerances and sentinel-frame fingerprints.
Audio uses alignment, correlation, loudness, and error tolerances after declared AAC trim.

The receipt preserves both timeline sample count and encoded sample count.
AAC encoder priming cannot disappear behind a rounded duration.

## First executable experiment

Name the first experiment `MAC-NATIVE-MOVIE-AUDIO-ROUNDTRIP-01`.

### Inputs

- Original AV1 movie `ePOglweqy7o.mp4` with the measured SHA-256 above.
- Video presentation samples `[0, 48)` from its immutable sample index.
- Reprise WAV with the measured SHA-256 above.
- Audio samples `[0, 96_000)` at 48 kHz.
- A 1920×1080 Rec.709 timeline at 24/1 fps.
- Explicit one-to-one mapping from decoded 1/24-second PTS values to 24 output frames per second.
- H.264 video and AAC stereo audio in MP4.

The result must have exactly 48 video frames and 96,000 timeline audio samples.
The output duration is exactly two timeline seconds before codec padding.

### Required observations

1. The runtime capability probe accepts AV1 decode, H.264 encode, AAC encode, and MP4 mux for this host.
2. The decoder returns the declared 48 source samples with exact sample ordinals and native timestamps.
3. The renderer produces 48 output frames with timestamps `n/24` for `n` from 0 through 47.
4. The writer receives audio blocks beginning at sample zero and covering 96,000 timeline samples.
5. The staged MP4 reopens through a separate reader path.
6. The reopened movie reports 48 video samples at exact expected timestamps.
7. The reopened audio aligns to sample zero after declared encoder trim.
8. Decoded video and audio meet predeclared lossy-codec tolerances.
9. The receipt binds both input hashes, both exact ranges, the immutable revision, backend identity, and output hash.
10. Static dependency and source audits find no FFmpeg, libav, or renderer subprocess path.
11. A request using the VP9 original fails before rendering with `unsupported_codec`.
12. The same failed request does not select the ProRes proxy automatically.

Any missing observation makes the experiment incomplete.
A playable file alone is insufficient.

## Independent acceptance expectations

The acceptance verifier owns fixture expectations before it invokes the CLI.
It does not trust the editor's reported frame count or pass flag.

The verifier:

- Hashes source files independently.
- Parses the saved artifact receipt independently.
- Reopens the movie through a separate reader instance.
- Enumerates output sample timestamps and decoded media.
- Compares observations with the fixture manifest.
- Hashes its own source and records the native binary hash.
- Saves stdout, stderr, exit code, observations, and final case outcome.

The first experiment proves only its codec and timeline profile.
It does not prove masks, text, layered composition, arbitrary retiming, or Panja creative quality.

Each later feature needs its own behavior case.

## Full Panja hybrid acceptance

Panja is the first full-film acceptance case.
It is not the first codec experiment.

The native acceptance project must bind one canonical audio master before editing.
The preserved state currently names two candidates:

- A 261.56-second master with SHA-256 `8cd42eb7af959f8fbc172d906470abda7952bd6b041ceda45670e565e6840923`.
- A 273-second reprise master with SHA-256 `cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8`.

The current work record treats the 273-second timeline master as the reproduction candidate.
The acceptance project must record the final source decision.

If the 273-second master is selected, the exact 24 fps timeline is 6,552 frames.
Its exact 48 kHz audio extent is 13,104,000 samples.

The full acceptance must demonstrate:

- Consecutive real footage with original asset hashes and exact source sample ranges.
- Source-derived anime anchors that cite their exact movie samples.
- Immutable local-GPU generated originals with attempt and workflow receipts.
- Separate cleanup, normalization, and upscale derivatives with transformation lineage.
- Accepted usable ranges tied to asset hashes and review records.
- Motivated real-to-anime and anime-to-real handoffs in the rendered film.
- Opening, development, change, consequence, and ending in chronological order.
- Multiple native video and audio tracks where the film requires them.
- Native composition, masks, motion curves, color transforms, and source retiming.
- Original-script text through a separate exact-text acceptance fixture if Panja does not exercise it.
- A native H.264/AAC or other declared native output with a source-closure receipt.
- A restorable native project revision as the editable checkpoint.

Technical proof and creative proof stay separate.

The native output must pass decode, timestamp, duration, sync, lineage, and tamper checks.
The exact output must then receive:

- Pilot review for the hardest hybrid handoff.
- Component review for every consumed source and generated range.
- Event review for shots, joins, story graphics, and text.
- Full normal-speed playback with sound.
- Full listening evidence.
- Two complete correction passes with regression checks.
- Current-policy `creative_proof_reviewed` and `creative_intent_realized` evidence.

A pending, failed, or inconclusive review cannot promote acceptance.
Measurements and frame sheets cannot satisfy watched or heard gates.

A Resolve render can remain a comparison reference.
It cannot establish the Rust renderer's capability.

## Material feasibility risks

### Codec coverage is source-specific

The current host decodes Panja's AV1 source and rejects its VP9 source.
Native support can also change across macOS versions and hardware.

Mitigation: probe exact files during import and bind a verified representation.
Record OS, framework, codec, and backend identities in receipts.

### Historical frame labels may not be native sample ordinals

The preserved plan names integer source frames from earlier proxy workflows.
One original reports 12 fps despite 1/24-second sample PTS.
Another reports a noninteger nominal rate.

Mitigation: rebuild native sample indexes and reconcile each historical label to exact PTS and presentation ordinal.
Do not copy historical frame integers into the new project without a mapping receipt.

### Rust bindings cross unsafe Objective-C boundaries

The `objc2` bindings expose the required surfaces.
Ownership, autorelease pools, callback lifetimes, dictionaries, and framework exceptions remain implementation risks.

Mitigation: contain all unsafe calls in `video-studio-macos`.
Add negative tests for writer errors, callback cancellation, and object lifetime.

### MP4 writing is not yet behaviorally proven

Headers and bindings establish an available path.
They do not prove this exact H.264/AAC configuration, backpressure loop, or finish behavior.

Mitigation: build `MAC-NATIVE-MOVIE-AUDIO-ROUNDTRIP-01` before timeline expansion.

### AAC priming can hide sync defects

AAC encoders insert delay and may pad the final packet.
A rounded container duration cannot establish sample alignment.

Mitigation: retain trim metadata, decoded alignment tests, and exact timeline sample counts.

### Color and geometry can drift silently

Clean aperture, preferred transform, pixel aspect, color primaries, transfer function, and range can change appearance.

Mitigation: store all measured descriptors.
Require explicit conversion into the timeline working color space and output tags.

### Original-script typography can vary by font and OS

Implicit system fallback can change glyphs or layout after an OS update.

Mitigation: bind font bytes by hash, use an explicit fallback list, and reject missing glyphs.
Acceptance compares shaped glyph runs, bounds, and rendered frames for Telugu and another complex script.

### The host lacks offline Metal tools

The Metal framework exists, but `metal` and `metallib` are absent.

Mitigation: use the CPU or built-in Core Image path first.
Treat custom Metal acceleration as unavailable until its toolchain and output are verified.

### Full-film performance is unknown

A correct CPU compositor may be too slow for a 6,552-frame 2K film.

Mitigation: measure the first real passage before committing to the full render.
Acceleration must preserve the same semantic and acceptance contract.

### Local-GPU submission recovery belongs outside the editor

The native editor cannot infer whether an absent provider response means no job exists.

Mitigation: the Effect/Herdr adapter persists intent before submission.
It reconciles queue and history before any retry.
The native editor imports only a verified transferred original and completed attempt receipt.

### Creative review remains unavailable to the renderer

The renderer can measure bytes and timing.
It cannot infer that a film was watched, heard, or creatively accepted.

Mitigation: store those observations as distinct external evidence tied to the exact output.
