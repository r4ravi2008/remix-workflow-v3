# Transparent PNG proof requirements A01

Status: predeclared requirements. No alpha output is accepted.
The implementation contract is alpha-synthesis-a01.md, SHA b86adde3537a2fcf285a97ba35ed52a374db69859052ae40b36864f5ce3d8db8.

## Ordinary producer and separate observation

Freeze a fresh ordinary CLI only after runtime tests, strict legacy hashes, fmt, Clippy and release build pass.
Bind every Rust source, Cargo manifest, Cargo.lock, relevant test fixture, design contract and check log.
The production binary identity and native loaded-image identity must match its measured plan/receipt evidence.
Use a new isolated alpha-unit state. Preserve the main film head and existing mastering states.

The private test observer records borrowed pre-handoff canvas hashes against independent expectations.
Disclose its separate instrumented executable. Do not use test-only observation as ordinary-production output proof.
The media observer has independently authored code and a separately bound executable. Disclose shared AVFoundation.

## Native baseline

Use 72 timeline frames at 24 fps and a 320x180 opaque canvas.
Use a freshly inspected preserved H.264 lower source and freshly measured static PNG assets.
Source grounding must prove that the chosen first 72 movie ordinals match that output cadence.
It must distinguish selected-range completion from source EOF.

The asymmetric 64x48 RGBA PNG includes opaque, partial and zero-alpha regions.
Zero-alpha pixels carry vivid hidden RGB. An inner transparent rectangle enables the crop-hole control.
The fully transparent PNG remains an active source on its own track above the lower movie.
The timeline uses at most four tracks, with frames before, during and after the sparse overlay.
Include two overlapping alpha layers, signed placement, contain fit, crop, motion, opacity and an inverted mask.

The canonical WAV binding remains 13,104,000 stereo48k source frames.
The baseline consumes exactly [0,144000), with unity gain and zero pan.
Distinguish declared L/R interpretation from measured channel labels.

Before export, freeze the concrete authored timeline, PNG bytes/facts, source captures, reference frame hashes and ROI manifest.
Use exclusive file creation. Retain each failed execution and report under its own version or run directory.
Do not change thresholds or remove difficult regions after observing results.

## Acceptance checks

| Dimension | Required evidence |
| --- | --- |
| Straight source truth | Compressed PNG hash/bytes, dimensions, exact straight RGBA hash and independently recomputed alpha hash/extrema/counts |
| Execution policy | Plan7, exact policy, unique sorted per-asset alpha identity, normalized placement/motion/mask, ordinal-zero PNG lineage |
| Exact arithmetic | Independent vector bytes and pre-handoff BGRA hashes; hidden RGB, partial alpha, bilinear ties, opaque equality, crop/contain/clipping/order/weight cases |
| Native picture | Every decoded output frame, full-frame and all required nonempty ROI PSNR >=34 dB for NativeColorMasterV1 |
| Empty regions | Zero area explicitly observed; no fabricated metric or pass assigned |
| Opaque output | Every decoded pixel alpha=255, independently observed |
| Video clocks | Exactly 72 frames, epoch0, PTS n/24, exact dimensions and full output video EOF |
| Source clocks | Every selected movie ordinal/PTS remains checked even when covered; PNG ordinal0 has no PTS |
| Audio | Exactly 144000 stereo PCM24 frames, zero output offset, every code exact, EOF and bounded chunks |
| Format | QuickTime, ap4h and lpcm, measured PCM24LE stereo48k format |
| Binding | Exact source closure, raw revision/plan/receipt CAS hashes, producer identity, output path/hash/bytes, completed job/attempt and epoch |
| Replay | Same immutable artifact receipt and output; fresh verification semantics permit varying bounded chunk partition only |
| Coverage failure | Fully transparent sole input rejects preflight; nonzero source cropped to a transparent hole fails before uncovered frame append and cannot publish a completed receipt |
| Cancellation | Public cancel against a running alpha owner, exporter exit, terminal actor/state readback, no completed artifact receipt, and owned-stage cleanup |
| Logical admission | Source/raster/canvas permits, checked eight-byte raster charge before allocation, four workers/capacity-one channels, actual logical high-water within admitted bound |
| Historical data | All eleven legacy document hashes, Receipt3/store4 readback, old artifacts unchanged and main film head unchanged |

H.264/AAC is a separate technical clock and opaque-output smoke path.
It does not pass the NativeColorMasterV1 pixel gate by association.
Preserved H.264 ROI failures remain unchanged.

## Negative controls

Require a bound passing baseline before applying controls.
Each control must name its intended false check and retain both the mutation and observed result.
Do not count an unrelated missing-file or binding error as a successful pixel or clock control.

Pixel sensitivity controls include straight-RGB filtering, ignored alpha, reversed layer order, black contain bars and asymmetric weight scaling.
Capture mutations must recompute incidental capture hashes so a specific pixel or opacity check detects the error.
Label these observer-sensitivity controls. They do not demonstrate a production renderer bug.

Actual product rejection controls include changed PNG bytes, forged measured alpha facts, omitted/wrong policy, wrong alpha identity and noncanonical schema.
Keep modified source/state copies isolated. Preserve the canonical sources and historical states.

Clock/audio controls include changed PTS, changed epoch, false EOF, truncated frame count, one PCM24 code change and selected-source offset.
Recompute incidental capture hashes when needed to reach the intended semantic check.

Binding controls include wrong producer, plan, receipt, output hash/bytes and completed-epoch relationship.
Missing zero-alpha Source observation must fail its lineage check rather than pass as a structural gap.

## Limits

These checks qualify one bounded transparent-PNG composition unit.
They do not qualify managed color, APNG, sixteen-bit PNG, movie alpha, transparent export or maximum throughput.
They do not measure whole-process/native peak memory or power-loss durability.
They do not establish normal-speed watching, hearing, creative approval, the complete editor or the full Panja film.
