# Video studio

Fresh general Rust editor and direct agent CLI, independent of the preserved Release Kit Studio prototypes.
The library owns immutable projects, source imports, revision transactions, sample clocks, export plans and bounded native movie output.

Build with `cargo build --locked`. Run `target/debug/video-studio discover` for current operation and capability scope.
The library is in crates/editor. The CLI calls that library in process.
The native media path uses macOS AVFoundation through Rust, without FFmpeg, libav or renderer subprocesses.

The current export unit supports adjacent clips and up to four ordered movie/PNG picture tracks.
Clips can use signed destination rectangles and fixed-point opacity. Sparse overlay tracks can have gaps.
Optional independent x/y/width/height/opacity curves use integer local-frame keys, steps or linear interpolation, and final holds.
Contain bars preserve lower layers. The visible temporal union must cover every output frame.
It consumes one measured48kHz stereo PCM clip and exports up to100000frames within explicit1800-second native operation deadlines.
Audio uses4096-frame owned chunks, capacity-two channels and incremental output comparison.
The frame bound is an implementation limit. Maximum-bound throughput and native-framework peak memory remain unmeasured.
Different source and canvas dimensions require explicit contain, cover or stretch framing with a normalized source crop.
Coordinates use coded BGRA dimensions. Display orientation, aperture, sample aspect ratio and color metadata remain unverified.
PNG import validates the exact IEND boundary, checksums, dimensions and straight decoded RGBA pixels.
Image ranges contain one sample, `[0, 1)`, and require hold cadence at ordinal zero.
Plan7 composites non-opaque eight-bit PNG alpha into the opaque canvas with copied premultiplied UNORM16 rasters.
Animation and sixteen-bit PNGs are rejected. ICC, gamma and color conversion remain unimplemented.
The framing operation uses owned BGRA pixels and bilinear sampling. Crops retain at least one source pixel per dimension; sampling taps stay within the crop. Each owned BGRA source/canvas frame is limited to128MiB.
Each copied alpha raster is limited to128MiB. Runtime output verification scans every decoded alpha byte for255.
Layer admission and runtime reservations use a512MiB logical picture-payload policy. This is separate from measured process or native-framework memory.
Rotation, movie alpha, transparent output, managed color, text, audio mixing/resampling and tenant orchestration remain implementation work.
This bound describes the current implementation; the complete general editor remains the target.

The Panja acceptance project binds actual OG source bytes and the preserved 273-second reprise master.
A 48-frame, three-cut diagnostic passed 24 independent frame, container, receipt and audio checks.
The fresh crop-corrected 24-frame framing diagnostic passed 24 independent checks. The current suite passes 133 tests.
Export ownership has fenced epochs, renewable leases, cancellation and exclusive hashed staging directories.
Reconciliation reclaims owner-recorded stages from retired dead owners. Uncertain and historical ambiguous stages remain preserved.
Full playback, listening, the hybrid production proof and the final film remain unaccepted.

Read docs/WORK.md for the full definition of done.
Read docs/design/synthesis.md for the selected ownership model.
The predecessor source, full film and editable historical checkpoint are preserved under ../../artifacts/scratch-video-goal-20261005/preserved/.

Source measurement refresh requires `AssetImport.previous_measurement` from `project.inspect` or `asset.verify` asset_measurements.
The refreshed source must retain its immutable bytes and origin. Old revisions retain their old measurements.
Movie indexing uses Core Media output presentation timestamps and durations. Differing encoded timestamps remain stored.
The publisher H.264 Panjaa source passed a24-frame source-clock export and24 independent checks.
These tests do not establish whole-source playback or creative acceptance.

`asset.inspect-frame STATE PROJECT REQUEST.json NEW_DIRECTORY` extracts one indexed coded frame without editing the project.
The receipt binds its revision, source measurement, native decoder, clock, PNG and RGBA hashes.
Source identity and bytes are checked before and after decode. AVFoundation opens a separate pathname; changes between observations remain excluded from the proof.
The saver uses descriptor-relative exclusive writes. Failures preserve all partial files.

`asset.verify-frame-inspection STATE PROJECT REQUEST.json` rechecks a saved directory.
The request contains `directory` and its expected `receipt_id`.
The result distinguishes complete, partial, foreign, corrupt and unverifiable records. It never deletes files.
Complete verification checks PNG pixels, receipt/request relationships, the stored revision and current source bytes.
It does not freshly decode the source movie or attest the original producer.

The fresh 16-frame catalog passed exact equivalence and three independent frame comparisons.
All 16 records passed the native verifier. Final classification fixes passed independent review A10.
The separate local ComfyUI adapter produced two H3 motion diagnostics on the Herdr RTX4070Ti.
Frame inspection rejected A01 for clipped feet and sword tip. A02 fixes the clipping in all124 inspected frames.
Both GPU leases are released. The corrected motion remains a diagnostic candidate without playback or creative acceptance.
The direct Rust CLI exported a206-frame real-to-anime-to-real sequence. An independent decoder verified all output frames, timestamps and canonical audio.
Six source endpoints passed independent pixel comparisons. Native contain framing remains separate from Resolve's corrected picture window.
The final PNG-capable producer saved a48-frame source-still, anchor-hold and local-motion diagnostic.
Every frame passed an independent Pillow source comparison; the minimum PSNR was40.1012dB.
The image descriptors match exact decoded source RGBA hashes. The audio contains96000 sampleframes with similarity above0.99997 at zero offset.
This is a two-second technical diagnostic. It establishes no playback, hearing or creative acceptance.
Strict input-validation producer A03 remeasured the same actual PNGs and prepared a fresh plan.
Their decoded pixels match the A02 export inputs exactly. The saved movie remains bound to producer A02.

The streaming audio unit exported a12-second,320x180 synthetic fixture beyond the previous ten-second limit.
An independent observer checked all288 frames, MP4 sample clocks and576000 stereo sampleframes.
The source selection starts at sample8191. Zero-offset similarities exceed0.999989; every picture comparison exceeds41.847dB PSNR.
Output video and audio readers reached EOF. Raw AAC padding is distinguished from the trimmed presentation.
Cancellation is checked during track loading, backpressure, native stream loops and owned recovery verification.
Native framework calls remain cooperative between calls; the library cannot forcibly interrupt a stalled native call.
This fixture proves duration/chunk behavior. It does not prove full-film, playback, hearing or creative acceptance.

The layered unit uses at most four track workers, one compositor and capacity-one picture channels.
Native framework objects remain inside completion callbacks. Owned Rust pixels and scalar observations cross the worker boundary.
Cancellation closes ports, preserves the export cause and joins all Rust workers.
Schema4 plans normalize every placement. Historical snapshot1, plan2/3 and receipt2 fixtures retain exact serialized hashes.
Structural validation checks all timeline/source mappings before decoding, indexing or worker creation.
The72-frame layered fixture exported simultaneous movie readers, sparse PNGs, signed clipping and opacity.
The first independent picture reference used incorrect Pillow sampling coordinates. That failed report remains saved.
The corrected reference passes all72frames and placement/overlap regions, with minimum36.1206dB full-frame PSNR.
The updated producer exported fresh72-frame synthetic and48-frame canonical-audio fixtures.
The72-frame output passes independent exact-picture/clock/PCM equivalence.
The canonical48-frame fixture passes every picture comparison, source/output clock, container check and output EOF check.
Its96000stereo sampleframes match the24-bit master prefix with both zero-offset similarities above0.99997.
The proof binds every imported file, generated source ordinal, held real frame, plan, producer and observer.
Historical206-frame output readback preserves its original movie and receipt.
These are bounded technical fixtures. Full playback, hearing, story and final-film acceptance remain required.

Review A13 accepts this bounded technical unit with no remaining P1/P2 finding. Full-film and perceptual acceptance remain pending.

The motion implementation uses schema5 with normalized sparse property curves and Q16 opacity.
Workers resolve placement after each frame request. The compositor rechecks placement, source ordinal and source PTS before blending.
Independent curve vectors cover 54 frames. A Fraction reference matches every pre-encode BGRA byte across six frames.
Two 72-frame actual movie/PNG exports are saved. Separate-code native picture, audio, clock and EOF comparisons pass under the declared policy.
The canonical offset setup failure is retained. Its corrected export selects the original master prefix and preserves the full binding.
An actual public cancel request stopped a live native write epoch in 9.935 seconds, without a completed receipt or remaining owned stage.
A14 accepts the bounded technical motion unit with no remaining P1/P2 finding.
Both outputs exceed 36.1205 dB full-frame PSNR, 34.8455 dB per placement and 35.2478 dB per overlap.
Each output contains 144,000 stereo PCM frames. Fresh epoch records and zero-offset WAV comparisons pass.
Twenty-nine deliberate proof mutations are rejected. Repeated AAC reads can vary in their last floating-point bits.
All retained reads pass the original audio threshold; one lost earlier diagnostic is explicitly unverifiable.
This unit establishes no full-film, watching, hearing or creative acceptance.

Picture masks use Plan6, sparse Q16 progress and analytic horizontal or vertical reveal coverage with inversion.
The mask origin follows the unclipped fitted picture window. Final opacity-weighted coverage governs visible bounds.
A15 code-only review, twelve exact8x8 pure frames, hidden-source native execution and87 tests pass.
The actual72-frame mask movies, independent ROI/audio verification and active Plan6 cancellation remain pending.

The NativeColorMasterV1 masks and publication unit now has A16 bounded technical acceptance.
Two 72-frame ProRes4444/PCM24 QuickTime fixtures pass independent frame, region, exact audio, clock, EOF and receipt checks.
Every nonempty region passes the original 34 dB gate; the minimum is39.5867dB.
The full-frame minimum is46.0541dB. Both stereo selections contain144000 exactPCM24frames.
The original H.264 mask failures remain failed and preserved.
Publication completion requires exact final availability and an owned job-and-attempt commit.
Cancellation, fencing, recovery, legacy compatibility and corruption controls pass in the bounded proof.
Read docs/design/implementation-review-a16.md for the exact scope and artifact identities.
The frozen producer's discovery text predates independent qualification; its receipts and the A16 evidence retain their exact identities.
Transparent PNG composition is implemented with pure runtime checks. Its independent ordinary-CLI native proof remains pending.
The general editor and complete Panja film remain unfinished.
