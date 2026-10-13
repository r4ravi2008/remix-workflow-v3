# Implementation review A17

## Result

Accept the bounded AlphaV2 technical behavior unit.
No identified P1 or P2 defect remains after the A04 closure repair.

This acceptance covers Plan 7 alpha composition through `NativeColorMasterV2` and Receipt 4.
It covers the fixed 72-frame, 320-by-180 diagnostic and its exact three-second PCM24 interval.

The A04 closure predates this review.
Its `nativeOutputAccepted: false` value correctly records the earlier pending state.
This review supplies the bounded technical disposition without rewriting that evidence.

This was an independent same-model-family review.
No cross-family reviewer was available.
The separate native observer still shares AVFoundation with the product.

## Findings

P1: none.

P2: none after the A04 closure repair.

### Closure repairs

A01 omitted direct bindings for the capture tree, movies, receipt CAS files, and verification CAS files.
A02 added recursive configuration and capture-manifest bindings.
A03 added exact capture-tree equality and required 72 named PNG frames per variant.
A04 added the canonical WAV pathname, size, and current full-file hash.

A04 also requires both variants to use that exact WAV and hash.
It binds A01 through A03 as preserved preliminary closures.
Those earlier files remain historical evidence and are not relabeled as final closures.

The final closure files are:

| File | SHA-256 |
| --- | --- |
| `close_alpha_unit_a04.py` | `6f362a65b99e9e84ed583ea4b3b2483a2e65ff363178b97d8b00ac236dbcc2db` |
| `closure-inputs-a04.json` | `0dfb145a38a8c6391ebb123678f642ce5531b3ef149f1be410f4bbcb9e78d01a` |
| `closure-report-a04.json` | `d0a05120fa5519a367f99ec3a199814023c362bb020e60f955a6e218c246b47a` |

## Independent rehash

I independently rehashed all 594 distinct file bindings.
Every path, byte count, and SHA-256 matched the A04 input inventory.

The rehash covered these current inputs:

- 30 Rust source files.
- 18 compatibility fixtures.
- `Cargo.lock`.
- The frozen production executable.
- The canonical 24-bit WAV.
- The separate native observer executable.
- Both ordinary outputs and all receipt and verification CAS files.
- All 162 capture files, including 144 decoded PNG frames.
- All fixed reference files and earlier retained closure evidence.
- All ten legacy receipts and their exact output files.

The frozen producer SHA-256 is `ff89563d736a985380c09ff64b7bccac67c7751545aa8a28425b2b2630bba57a`.
The canonical WAV SHA-256 is `cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8`.

The build records 139 passing tests, formatting, Clippy, and release gates.
This reviewer rehashed those records and their bound sources.
This reviewer did not rerun the build or test suite.

The closure reports 1,829 passing assertion executions.
Some build and policy bindings check the same path twice.
The report contains 1,470 distinct check identifiers and 594 unique file paths.

## Native picture and color evidence

The master output is a 7,347,788-byte MOV.
Its SHA-256 is `1b4e4829bf6002156029057dd58e55b717ffec8099a63f4b1f5033835a74ad76`.

The master plan ID is `a771942c48dc0e9b1832bb81bccb56fe21e074fe58546f9c49a3bc95a1ec91a2`.
Its Receipt 4 ID is `ba96d0b9d262bd424b4785324c38d3609ed3d5a563fe784382e3a988a6cfd259`.

The media verifier passes all 548 checks.
It verifies all 72 decoded frames, their zero-epoch PTS, and reader EOF.
The minimum full-frame PSNR is 49.942224 dB.

The verifier checks 752 declared ROIs.
It records 516 nonempty ROIs and 236 empty ROIs.
Every nonempty ROI passes the unchanged 34 dB floor.
The minimum finite nonempty ROI PSNR is 48.253317 dB.

Receipt 4 contains the exact Rec.709 tuple for encoded samples and decoded buffers.
Each field is `ITU_R_709_2`.
The independent MOV inspection finds one AP4H entry and one `nclc` 1/1/1 atom.

The AP4H parser also requires the measured four-zero sample-entry suffix.
That suffix rule applies only to this measured AVFoundation profile.
It is not a general QuickTime parsing claim.

The H.264 compatibility output remains a Receipt 2 artifact.
Its SHA-256 is `81555cf13a70833931c01e55cf9f3d8923a5dd776ecdb71b234f6986474d9ab1`.
It does not acquire Receipt 4 color evidence.

## Audio and clock evidence

The master contains exactly 144,000 packed PCM24 stereo frames at 48 kHz.
The selected source interval is `[0,144000)`.
The decoded PCM24 codes match the canonical WAV exactly.

The master source and output streaming evidence binds counts, intervals, chunk bounds, clocks, and EOF.
The H.264 smoke output retains its AAC correlation and padding-clock evidence.

Fresh H.264 reads may report different enclosing source read-ahead endpoints.
Each raw endpoint remains in the report.
Each endpoint must stay within `[selectedEnd,13104000]` before comparison normalization.

The 4,096-frame maximum describes the Rust-owned PCM chunk.
It does not claim a native `CMSampleBuffer` memory bound.

## Negative controls and graph authority

The A06 media controls pass 47 of 47 checks.
The protected evidence inventory remains unchanged.

A06 fixes the three ineffective A05 mutations without changing the 47-control manifest:

- Frame 41 pixel `(131,118)` now targets the declared 128-sample crop-hole ROI.
- The frame 41 80-by-80 mutation now fails full-frame and ROI checks.
- The H.264 codec control changes `avc1` to `ap4h` and fails the codec check.

The A05 44-of-47 report remains preserved as a superseded failed control run.
It is not counted as a passing result.

The independent graph verifier passes 137,539 checks.
Its 16 graph sensitivity controls also pass.
They bind Plan 7, source lineage, alpha facts, Receipt 4, renderer identity, CAS roots, and prior state.

The six public product rejection controls pass.
They reject changed PNG bytes, forged alpha facts, missing or wrong policy, wrong source lineage, and noncanonical schema.

## Coverage, cancellation, and compatibility

The three public coverage and cancellation controls pass.
The A02 unframed request and A03 missing-crop request remain preserved as control-authoring failures.
A04 changes only the isolated requests to supply complete explicit framing.

The sole transparent layer fails preparation before an export job exists.
The cropped transparent hole fails with no completed receipt.

The cancellation control observes 442,404 stage bytes under the live owner and epoch.
Public cancellation returns `export_cancelled` after 9.918611 seconds.
The job and attempt end as cancelled with no receipt.
The owned stage is absent before reconciliation.

Frame-zero rejection before writer handoff remains a reviewed code-order inference.
The control has no direct handoff timing hook.

Ten legacy readbacks preserve their exact Receipt 2 or Receipt 3 identities and outputs.
Legacy records remain without Receipt 4 color evidence.
The current 13 project heads match the saved prior-state snapshot.

## Scope limits

This review accepts only the bounded Alpha Plan 7, Rec.709 V2, and Receipt 4 behavior unit.
It does not accept the whole editor or the 273-second film.

The decoded-output comparisons do not expose every raw compositor buffer.
The evidence does not establish source color management, ICC behavior, gamma conversion, HDR, or managed display output.

The evidence does not establish maximum throughput, native process peak memory, or every cancellation timing point.
The observer is separate code but uses the same AVFoundation implementation.

No normal-speed playback was watched.
No audio was heard.
No creative or full-film acceptance is implied.

No native export, media decode, rebuild, GPU operation, Resolve operation, or production-state mutation was performed for this review.
