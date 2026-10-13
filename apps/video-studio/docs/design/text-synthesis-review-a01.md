# Native text synthesis review A01

## Disposition

The synthesis is **green for authoring the isolated native feasibility probe**.

Both P2 findings from `text-judgment-a01.md` are closed at the design level. I found no new P1 or P2 design contradiction.

This disposition authorizes probe authoring within the existing goal. It does not report a passing native probe. It does not authorize product integration based on prose alone. Native output, runtime compatibility, playback, hearing, creative acceptance, and film text remain unverified.

The reviewed synthesis is `text-synthesis-a01.md`, SHA-256 `d497f472b0d5162e61fab482e2f720a89192645b88b1430b1b61577f0330c323`.

The bound input exists at `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/synthetic-text-cases-a02.json`. I rehashed it as `a461e07c803793baa688b18452287ca73f3ba0e6d0f8c172458a0158e4ab513d`, 14,706 bytes.

All available reviewers use the same model family. This review is artifact-separated, not cross-family or blind-model review.

## P2 closure

### Closed: final-response cache retirement

The synthesis replaces the impossible “worker observes consumption” statement with an executable ownership sequence:

1. The worker owns one cache `Arc`.
2. The response owns a second `Arc` to the same admitted raster.
3. The worker drops its cache `Arc` before sending the final response.
4. The response retains the raster through compositor validation and blending.
5. The compositor drops the response before requesting the track's next frame.

The final `Arc` owns the single permit. No raster copy or acknowledgement channel is required.

The contract also covers disconnected sends, cancellation, worker drop, and test-observer retention. This closes the first judgment finding.

### Closed: simultaneous retained-payload accounting

The synthesis now separates every material application-owned category:

- one shared immutable Plan8 text payload;
- a separately admitted canonical JSON buffer;
- temporally active premultiplied text rasters;
- Rust font bytes and copied `CFData`;
- bounded table-copy and table-record scratch;
- fresh execution-side strings, UTF-16, runs, glyphs, positions, advances, and indices;
- the padded native alpha mask;
- existing movie, PNG, canvas, response, and writer payloads.

It forbids worker-deep-cloned plans and a second whole canonical alpha mask. It also requires fresh execution evidence to remain charged while retained plan evidence exists.

The fixed 128 MiB typed-text reservation is explicitly provisional. The synthesis requires a checked component derivation before product reliance. That remaining derivation is stated honestly and blocks product integration, but it does not block a bounded standalone probe.

This closes the second judgment finding for the architecture and probe-authoring phase.

## Contract consistency

The corrected synthesis retains the selected whole shape:

- exact untimed font resources share the blob CAS without using `SourceRange`;
- text appends to existing ordered picture tracks;
- the caller supplies a fixed integer box and local baseline;
- execution shapes and rasterizes once per active source;
- subsequent frames borrow the one cached admitted raster;
- Plan8 alone admits text;
- Plan2 through Plan7 retain their historical selector and validation behavior;
- Receipt2 through Receipt4 and output profiles remain unchanged;
- one validator dispatches prepare replay, render, verification, and recovery;
- historical verification does not reshape text on a newer host.

The closed raster policy is specific enough to implement a falsifiable probe. It declares stride, baseline transformation, matrices, row reversal, antialiasing, smoothing, subpixel positioning, subpixel quantization, and alpha arithmetic.

The synthesis correctly labels the row rule as a hypothesis. The isolated probe must establish it with asymmetric coordinates before product code relies on it.

The 512-pixel maximum matches the bound A02 source expectations. Aggregate string, font, run, glyph, curve, table, and observation limits are now explicit.

The A02 negative cases also have a truthful boundary. `ABC 123`, emoji, and U+0378 must reject through actual fallback or glyph-zero evidence. Nominal cmap inspection cannot satisfy that result.

## Exact remaining conditions

### Before the first native probe execution

Probe authoring may begin now. Freeze these facts before executing the probe:

1. Bind the exact A02 input path, byte count, SHA-256, font manifest, font hashes, pinned source commit, and license.
2. Pin the exact Rust dependencies, feature sets, SDK target, source hash, executable identity, host architecture, and framework versions.
3. Predeclare every accepted, rejected, and observation-only case. Do not reinterpret a result after execution.
4. Specify guarded-buffer width, height, stride, baseline translation, inner extraction, and native-to-editor row formulas numerically.
5. Specify the output schema for complete line and run ranges, full matrices, status bits, run fonts, glyphs, positions, advances, indices, coverage hash, count, bounds, and failures.
6. Bound every probe-owned font, table, string, UTF-16, run, glyph, alpha-mask, and output allocation before its allocation.
7. Preserve all failed and partial outputs. Do not overwrite earlier helpers or observations.

The Rust probe must not link to the editor crate. The Swift observer must not import the Rust text implementation.

### Before product integration

All of these conditions remain mandatory:

1. The Rust and Swift native probes must agree on the selected byte-owned font construction and evidence contract.
2. Actual runs must expose only the bound face, accepted size, identity matrices, empty variations, LTR status, known status bits, and nonzero glyph IDs.
3. Telugu and Devanagari fixtures must cover the complete exact UTF-16 ranges without scalar-to-glyph assumptions.
4. The asymmetric coordinate control must establish baseline placement, y-up native drawing, row reversal, stride handling, and guarded extraction.
5. Repeated calls must establish the selected alpha-mask stability on the bound host and architecture.
6. Every native raster switch must be applied and observed through decisive positive and negative controls.
7. Any coordinate, fallback, matrix, range, switch, or alpha discrepancy must stop integration and reopen the design.
8. Derive the checked 128 MiB retained Plan8 component bound from the actual Rust representations and allocation lifetimes.
9. Derive the maximum temporary charge with retained plan evidence, fresh execution evidence, font copies, table scratch, stride mask, and persistent raster simultaneously live.
10. Prove the combined temporal sweep stays within 512 MiB alongside current media, canvas, response, and writer reservations.
11. Freeze and recheck the real Plan7, Snapshot1, and Receipt2 through Receipt4 byte identities before adding Plan8 dispatch.

### Before bounded native text acceptance

Product integration alone is insufficient. Acceptance still requires the declared Plan8 tamper controls, independent pure arithmetic vectors, ordinary `NativeColorMasterV2` export, exact pre-writer frames, decoded frame and ROI checks, source and audio clocks, active cancellation, fencing, recovery, and legacy readbacks.

These checks can establish only the bounded technical text unit. They cannot establish normal-speed watching, hearing, creative approval, lyrics, or completion of the full film.

## Verdict

The corrected synthesis closes both design P2 findings enough to author the isolated native probe now. No design P1 or P2 remains open in this review.

The next truthful state is **probe source and policy authored, native feasibility pending**. Product implementation must wait for a passing probe and the checked retained-payload derivation.
