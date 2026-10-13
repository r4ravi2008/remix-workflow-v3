# Resolve hybrid diagnostic A04 review

## Result

The A04 movie passes the reviewed technical and frame-inspection checks for this bounded diagnostic.

The exact export contains 206 frames at 24 fps, or 8.583333 seconds. It is not the 273-second film.

One historical control gap remains. The source scope, case bindings, coverage wording, and canonical-audio receipt are now accurate.

This diagnostic does not authorize full-film production. It also does not pass the hardest musical or action pilot.

## Actionable findings

### P1: the saved evidence omits the Resolve lease renewal

`resource-owner.json` sets `deadlineEpoch` to `1791281730.376798`.

`resource-closeout.json` records release at `1791282130.746612`, 400.37 seconds after that saved deadline.

No contemporaneous saved renewal record exists. The request and terminal files also have filesystem times after the saved deadline.

Those filesystem times illustrate the journal gap. They are not lease authority.

`resource-renewal-retrospective-a01.json` records a live renewal through `1791282325.98519`. That deadline covers the recorded release.

The new record correctly identifies tool-call history as its authority. It also states that no contemporaneous durable artifact was preserved.

Require a durable renewal journal before any further Resolve or GPU operation. The current packet cannot independently prove continuous ownership.

The closeout otherwise records a saved project, no active render, and a completed exact job. It explicitly leaves the scratch project open.

## Accepted receipt-scope repairs

### Source-range evidence now matches the diagnostic scope

The A04 timeline readback reports adjacent durations of 48, 124, and 34 frames.

The generated clip reports `sourceStartReadback: 0` and `sourceEndReadback: 123` for its 124-frame timeline span.

The `apiSourceEndCaveat` correctly states that this getter does not establish endpoint semantics by itself.

The six selected endpoint comparisons reproduce exactly with Pillow Lanczos references. All six exceed 34 dB PSNR; the minimum is 37.4266 dB.

Those comparisons support OG frames 1560 and 1607, anime frames 0 and 123, and Panja frames 1916 and 1949.

All 34 inspected return frames show a visually continuous embrace. The review identifies `1916..1950` as the requested half-open source span.

It also states that intermediate source-ordinal equivalence remains unverified. This is the correct boundary for the endpoint and frame-inspection diagnostic.

Full source-range pixel equality is unnecessary for this bounded diagnostic, and the receipt does not claim it.

Each case now binds source and output PNG byte hashes plus decoded RGBA hashes.

The original-source cases bind their receipt files and asset hashes. The generated cases bind native observations from the exact provider movie.

I rechecked every declared hash and relationship. All six cases match their saved evidence.

### Corrected during review: coverage wording now matches the saved evidence

`native-sequence.json` records 206 frames and ends with `AVAssetReaderStatus(2)`. Every PTS equals `n/24` seconds through frame 205.

The old observer hard-codes `fullDecode: false`. Therefore, that field cannot prove or disprove EOF for A04.

The revised frame review now cites completed reader status, the expected frame count, and the exact clock extent.

The original review said “all PNG hashes.” The observer records decoded RGBA hashes and timestamps, not PNG byte hashes.

I decoded all 206 saved PNG files. Their dimensions and RGBA hashes match every observer entry.

The revised sentence now says the saved PNGs were decoded and their RGBA hashes and timestamps were checked.

### Corrected during review: the canonical-audio binding is now self-contained

The canonical-only audio claim is supported across the saved records.

The timeline contains one audio clip with media ID `f62b0606-bcdd-4986-a373-e2d0ab8dcd9c`. Creation readback maps it to the canonical master.

The actual master hashes to `cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8`.

It is 24-bit interleaved PCM, stereo, 48 kHz, with 13,104,000 frames and a 273-second duration.

The output contains 413,632 decoded AAC frames. The first 412,000 match canonical samples `[0, 412000)` at zero lag.

Channel correlations are `0.9999359172` and `0.9999237667`. The remaining 1,632 frames are identified as AAC padding.

The revised verification input now records the canonical path, SHA-256, and source span `{start: 0, length: 412000}`.

This evidence is measured. It is not hearing evidence.

## Confirmed frame evidence

The movie, checkpoint, observer, and decoded PCM files match their recorded byte counts and SHA-256 values.

All 206 output frames exist at 2560 by 1440. Their indices and PTS values are contiguous.

No decoded frame is fully black. The picture top is 186–187; the measured bottom-exclusive row is 1254–1255.

The seven contact sheets cover frames 0–205 in order. Enlarged boundary frames show clean cuts at frames 48 and 172.

The illustrated head, feet, and one katana remain inside the picture window. The original close-shot faces remain readable.

The Panja return retains a large `GaneshVideos` logo. Visible mouth-shape changes require synchronized normal-speed review.

## Remaining acceptance gates

No qualified normal-speed watch occurred. No qualified hearing pass occurred.

The evidence does not establish pacing, musical fit, lip synchronization, motion quality, or creative acceptance.

The diagnostic does not prove the complete nightmare, awakening, relationship, and peace progression.

The full 273-second film, hardest complete musical passage, and hardest action passage remain incomplete.

No cross-family model reviewer was available.

This review used saved evidence only. It did not operate DaVinci Resolve or the GPU.
