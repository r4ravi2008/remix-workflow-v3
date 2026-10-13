# Implementation review A06

## Result

No P1 defect remains in the reviewed bounded geometry unit.

Producer A11 renders the exact 24-frame fixture with contain, cover, stretch, and a partial normalized crop.

The fresh A02 artifact passes product reopening and all 24 independent checks. Its minimum every-frame PSNR is `42.90374374930746` dB.

A02 supersedes A01 for geometry acceptance. A01 remains preserved as the historical pre-fix artifact and proof record.

Two P2 gaps remain. Product verification does not retain semantic geometry measurements, and the declared per-frame memory limit is not an aggregate resource bound.

This result accepts one bounded coded-raster unit. It does not establish a general compositor or the completed hybrid film.

## Review boundary

The exact accepted producer is `video-studio-producer-a11`.

Its SHA-256 is `a001c39347152aff2ba4384f90b45941182729a68b9e370d65bfe5661fd9ea71`.

The final reviewed development binary is `97f6b644546f7bb29c1d384162529c3400c5adf5d90b8cd4d1b3a965b34c4c2e`.

The later binary adds validation, preflight coverage, and narrower capability wording. Its pixel evaluator is the evaluator archived in A11.

The accepted A02 artifact has these bindings:

- Project: `panja-framing-proof`.
- Revision: `4ea1255a8d0214b6051ec9beefbb87c5d714d7675da3fb794de01a7cf0a2884f`.
- Plan: `fecd6676c8c08d858fd546cd7ff9c20c2a1a0ae02de6344662ceb3c9519506f2`.
- Output: `3cf39c54b2edcbdc40ac6d9531e4c560746207d14a8437d43f7630aaab8b6622`.
- Output bytes: `900,894`.
- Artifact receipt: `cf87d57edef9a174f9d22e84653ea422f7768be069770ca4871054b1477c749d`.
- Initial verification: `20d4ecbbac919cb31dcf5d7671cc95113c85923e7e35c1865511add4878004dd`.
- Fixture SHA-256: `fb33322b20a9237c0bac1fcbe31286a57feb021866ff2e0fd6a8e745edd219cb`.
- Independent report SHA-256: `3d53d6c4abcd75087672ddf335c37a12c8c213978ac7d7c3e045cf96c87a5c8d`.

All behavioral probes used relocated copies under `/tmp`. No probe changed an original database, source, receipt, artifact, or project head.

## Defects found and fixed during review

### Floating-point crop bounds

The first implementation accepted `x = 1.0` with `width = 5e-324`.

That crop could produce non-finite scaling and an invalid evaluated frame. It also violated the declared inside-source invariant.

The first fix used `width > 1.0 - x`. A complementary probe then exposed the reverse rounding case.

The intermediate binary accepted `x = 5e-324` with `width = 1.0`. The copied project committed revision `26f4605dd63523e278b434558e12104ca8d0550a3cb2b4c58acf573e0e93c4b3`.

Final validation checks both subtraction directions for each axis. It also requires each crop dimension to retain at least one coded source pixel.

Fresh copied-store probes reject both boundary cases as `invalid_framing`. The copied head remains revision `4ea1255a...`, sequence 2.

### Crop-edge sampling

The A10 bilinear evaluator could sample outside a partial crop.

For the A01 horizontal crop, the first mapped coordinate was approximately `479.734`. Source pixel 479 was outside the requested `[480,1440)` interval.

The A11 evaluator clamps both interpolation taps to included pixel centers. The fixture crop now samples only columns 480 through 1439.

The regression test places markers outside a crop. It confirms no marker enters contain, cover, or stretch output.

The A01 natural-image PSNR check did not detect this edge leak. Its threshold tolerated the small difference.

### Pixel extent preflight

Project settings permit dimensions through 8192 by 8192. One tight BGRA frame at that size requires 256 MiB.

The pixel evaluator already rejected owned frames above 128 MiB. Earlier planning could therefore succeed before a late render failure.

`Project::prepare_export` now preflights the canvas and every source frame before selected-range decode or plan persistence.

The replay path and concurrent transaction replay path apply the same check. Native profile validation repeats the check before writing.

The discovery inventory now reports the 128 MiB per-owned-frame limit.

## Immutable model and plan ownership

`VideoClip.framing` and `VideoUse.framing` are optional fields. Missing fields deserialize as `None` and remain omitted when serialized.

This preserves historical revision and plan identities. A final-build copied-store probe replayed historical plan `8af87bb38295d818f3114fb7d28a4ac53f408b416be04fb8609e067d81f5cd64` unchanged.

That plan still binds revision `90b2770b84fd6c8acec758816158f40351d604b6031e5ff1844223a09b54c41a`. Its three video uses correctly contain no framing field.

The A02 revision is sequence 2 with parent `6c9738cf82bac0f339ce5c0f50740643d2f2c36bd23b458d6c18295dc78f67a5`.

Its timeline owns these exact mappings:

| Timeline frames | Source ordinals | Geometry |
| --- | --- | --- |
| `[0,8)` | `[0,8)` | Full-source contain |
| `[8,16)` | `[48,56)` | Full-source cover |
| `[16,24)` | `[96,104)` | Stretch after crop `x=0.25`, `width=0.5` |

The schema-2 plan stores all 24 presentation ordinals. It also stores each allowed source interval and each framing value.

Each range has pre-save decode evidence. Every record reports eight decoded samples, verified PTS, and producer A11.

The source closure contains the exact AV1 movie and canonical PCM master. The plan hash therefore owns geometry, source selection, and transitive media identity.

## Source-clock and bounds authority

The movie asset is `a2247e96ab4335eb6b365ef52b6203e53377c6cf317ebb2e156789e6bd470b7f`.

Its immutable index contains 2,277 presentation samples at the actual 12,288-tick source clock.

The selected samples advance by `512/12288`, which equals `1/24` second. Nominal container-rate labels do not replace these timestamps.

Plan compilation maps each local output frame from the selected range's measured first PTS. It requires an exact indexed PTS for every output frame.

Rendering reopens each clip and checks every decoded PTS against that asset index. It also checks decoded source dimensions before framing.

Snapshot validation bounds source spans by the immutable sample count. It validates crop extent against the stored 1920 by 1080 source dimensions.

This evidence resolves timing and bounds for the three selected ranges. It does not establish arbitrary retiming or full-source decode.

## Canonical audio authority

The canonical master is `cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8`.

It is 24-bit interleaved PCM stereo at 48 kHz. Its measured extent is 13,104,000 frames, or 273 seconds.

A02 consumes exact source samples `[0,48000)`. The output timeline owns the same 48,000-sample interval.

The older 16-bit, 261.56-second metadata WAV has no authority in this revision or plan.

The stored left/right labels remain an explicit interpretation. The imported descriptor reports no measured channel labels.

Waveform correlation proves channel-preserving alignment for this interval. It does not prove semantic channel labels or listening acceptance.

## Exact A02 technical evidence

`independent-framing-verify-a02/report.json` passes all 24 recorded checks.

The report compares every output frame with a separately evaluated Pillow `ImageOps` reference.

The minimum PSNR values are:

- Contain: `48.981376302700696` dB.
- Cover: `42.90374374930746` dB.
- Stretch with partial crop: `44.03007319257455` dB.

The output decodes to 24 frames at 2048 by 1536. Every decoded output PTS equals `n/24`.

The raw compressed H.264 interval is `50/600` through `650/600`. Its span is exactly one second.

The output decodes to 48,000 stereo PCM frames. The raw AAC interval contains 50,176 ticks, with 2,176 ticks trimmed during native decode.

Waveform lag is zero on both channels. Correlations are `0.9999769192056728` and `0.9999686975209157`.

The external report binds the source hashes, output hash, A11 producer hash, fixture hash, verifier script hash, and helper binary hash.

Its `noLibavLink` check directly covers the native helper. A separate `otool -L` inspection found no libav or FFmpeg dependency in A11.

## P2: product verification does not retain geometry semantics

`movie::verify` reopens the exact artifact and checks codecs, clocks, counts, dimensions, and audio correlation.

It does not compare output pixels with `VideoUse.framing` or `presentation_ordinals`.

The external A02 report supplies complete frame comparisons for this fixture. Manual review confirmed its ranges and framing equal the immutable plan.

The script does not load that plan itself. The report also remains outside the immutable receipt content-addressed store.

A wrong but structurally valid picture could therefore pass `project.verify-export` without the external report.

Store operation-aware geometry evidence against the exact plan, output, source hashes, and verifier identity.

For later effects, define evidence per operation. Source-pixel PSNR cannot validate color work, titles, masks, transitions, or generative footage.

## P2: per-frame bounds do not bound aggregate resources

The 128 MiB check bounds each tight source or canvas BGRA vector. It does not cap total process memory.

The channel holds two evaluated frames. One writer-pending frame and one blocked sender can coexist with those frames.

At the A02 canvas, four tight output vectors total 48 MiB before native source and writer buffers.

At the declared per-frame maximum, those four vectors alone can total 512 MiB. Native buffers can increase the peak further.

Framing also uses scalar bilinear loops. Each clip opens a new reader and decodes from ordinal zero to its selected range.

A02 proves 24 frames at 2048 by 1536. It records neither peak RSS nor authoritative render elapsed time.

The 240-frame and 128 MiB limits are therefore accepted input bounds, not a proven throughput or total-memory envelope.

Add an aggregate render budget and record peak memory and elapsed time at supported limits. Reuse or seek readers before scaling to long timelines.

## General-editor and proof boundary

The final discovery output now says geometry uses coded BGRA source dimensions.

It also says orientation, clean aperture, sample aspect ratio, and color metadata remain unverified.

The A02 source is a 1920 by 1080 BT.709 AV1 asset. A review-only probe found no display side-data record.

That observation is not native product-bound metadata evidence. The editor must later index these properties or reject nonidentity values.

The Pillow transform is independent from the Rust transform. Both source and output frames still use the same AVFoundation helper decoder.

The 35 dB threshold proves strong lossy similarity. It is not exact pixel equality or a color-management proof.

The exact helper and script hashes are recorded and still match current files. They are not archived in the immutable product receipt store.

A relocated copied store cannot replay the exact receipt because schema 2 binds the absolute artifact path.

The copied-store probe returned `job_tampered` at that location check. Request hashes, plan identity, receipt identity, and output bytes remained unchanged.

I did not run current-build verification against the original store because this review was read-only.

The unit still lacks layers, position, rotation, keyframed motion, transitions, masks, titles, color operations, and general audio mixing.

No normal-speed watch or listen occurred. Watched, heard, and creative acceptance remain false.

The full hybrid film remains unproduced and unaccepted.

## Validation

`cargo fmt --all -- --check` passed.

`cargo test --locked --workspace` passed all 27 tests.

`cargo clippy --locked --workspace --all-targets -- -D warnings` passed.

The final invalid-crop probes used binary `66c799bdac49100592ef72938cda187528b6fb210310b51fe5aab722ca651872`.

The final build differs only in the later capability qualifier. The reviewed current binary is `97f6b644546f7bb29c1d384162529c3400c5adf5d90b8cd4d1b3a965b34c4c2e`.

No GPU or Resolve operation ran during this review.

Cross-family model review was unavailable. This document does not claim one.
