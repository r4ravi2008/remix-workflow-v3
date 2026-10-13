# Cloudflare editor progress

This document describes the Cloudflare editor. The standalone Rust editor is a separate application.

Updated: 2026-10-03. Owner: Release Kit Studio.

The editor is a separate Cloudflare Worker service. Cloudflare Containers run
native encoding behind it. Tailscale is a GPU provider transport. This replaces
the proposed Tailscale Linux Resolve finisher.

## Architecture phases

- [x] Ground: traced source, production, and output contracts. Researched Resolve and Cloudflare.
- [x] Sketch: compared immutable D1 revisions against a per-project event-log actor.
- [x] Agree: selected D1 authority with a release-scoped render DO. Adopted judge corrections.
- [x] Implemented the initial service, CLI, project model, renderer, and independent verification.
- [x] Scrap audit: fixed startup/cancellation races. The audit added no second project authority.

## Design comparison

- [x] Frame: separate editor, tenant ownership, six-output contract, honest evidence.
- [x] Fan out: two isolated designs with rationale.
- [x] Cross-judge: independent scores A 23/25, B 22/25.
- [x] Pick: immutable revisions with a durable render ledger.
- [x] Graft: edit batches, unsupported-feature errors and artifact-bound reviews.
- [x] Verify initial implementation: tests, native renders and local Workerd integration.

See [architecture](ARCHITECTURE.md) for rationale and rejected alternatives.

## Product milestones

| ID | Milestone | State | Evidence / next action |
|---|---|---|---|
| E01 | Resolve map and scoped replacement specification | Complete | [Specification](SPEC.md), [plan](IMPLEMENTATION.md) |
| E02 | Separate Worker, tenant-scoped revisions and render jobs | Implemented. Locally verified | [Worker receipt](worker-runtime-receipt.json), [shared capacity receipt](capacity-runtime-receipt.json). Cloud deployment pending |
| E03 | Tool catalog, feature ledger and agent CLI | Implemented. Locally verified | `agent/editor-cli.test.ts`, `editor/feature-ledger.json`, Worker receipt |
| E04 | Conform, edits, typography, framing, color and masked effects | Initial subset verified | [Six-format receipt](render-canary-receipt.json). Layers, keyframes, tracking and richer color remain |
| E05 | Cloudflare deployment and kit packaging | Packaging locally verified. Cloud billing pending | [Archive receipt](archive-runtime-receipt.json), [deployment receipt](deployment-receipt.json). Workers Paid and R2 activation required |
| E06 | Independent QC, provenance and review records | Measurements and review previews locally verified. Perceptual review pending | [Frame diagnostics](frame-diagnostics-runtime-receipt.json), [manifest export](frame-diagnostics-archive-runtime-receipt.json), [preview receipt](review-preview-runtime-receipt.json), [Studio session checks](review-preview-session-runtime-receipt.json), [full-length ending](review-preview-long-runtime-receipt.json). Semantic seam and complete motion/sound review remain |
| E07 | Hosted frontend and outer production-plan integration | Implemented. Local production canaries verified | [Measured-project receipt](production-runtime-receipt.json), [generated-media receipt](generated-production-runtime-receipt.json). Schemas v2/v3, exact lease, six-output R2 promotion and private downloads. Cloud pending |
| E08 | Pal Pal film, three promos, thumbnail and artwork | Pending direction and review | No completed Pal Pal kit |

## Verified now

These records describe local checks and observed results.

- Typecheck, lint, 129 app tests across 27 files, 49 Python checks, three real Bun HTTP checks, and frontend build passed. Preview tests cover strict frame bounds, source binding, private ranges, corrupt downloads, JPEG color conversion and independent moving-frame correspondence. The Bun checks preserve explicit deadlines and lease cancellation. Frame diagnostics cover complete coverage, terminal freezes, declared holds/fades, planned joins and bounded findings. Archive checks preserve findings and reject altered review suggestions. Earlier checks cover decoded duration, immutable bytes, interrupted inspection, tenant rotation, exact grants, production leases and ZIP64 packaging.
- The Linux amd64 container rendered four H.264/AAC videos and two JPEGs at the six required canvases. The outputs contain shaped Telugu text and a masked response effect.
- Complete decode, hashes, exact frame counts and canonical two-channel source correlation passed. Corruption, silent replacement and wrong canvas were rejected.
- Eleven engine HTTP checks passed. The checks covered cold verification without another render, checksum rejection, intent replay, and cancellation.
- Eighteen local Workerd checks passed. The checks covered service binding, CLI upload/download, D1 revisions, auth/origin controls, and tenant isolation. They also covered render/replay, R2 output and receipt readback, cold verification, review fences, cancellation, and token revocation.
- Seven more local Workerd/D1/R2 checks passed against the saved source hashes. Two tenants rendered through one shared capacity slot. A third queued job cancelled. Cancellation did not stop the active tenant. Cold verification returned explicit backoff, and the real agent waited before verification of the same stored bytes.

  Both outputs passed hashes and complete downloaded decodes. Physical samples showed one native Container at peak and zero afterward. Diagnostic credentials were revoked. [Capacity receipt](capacity-runtime-receipt.json).
- The production adapter completed a six-output synthetic kit through the Studio/Editor service binding. The outer ledger reached review. Final full/range downloads, hashes and complete downloaded decodes passed without another render. The diagnostic device was revoked and the session logged out. The saved receipt distinguishes resumed stored-kit verification.
- The schema-v3 recipe adapter also completed six synthetic outputs through local Workerd. Fifteen checks passed. The checks covered measurement of collected footage before immutable commit, independent native verification, complete downloaded decode, and exact byte ranges. This test submitted no GPU inference. Its diagnostic credentials were revoked.
- The separate Worker packaged the six current native canary outputs, project checkpoint, and manifest. The archive is a 2,476,212-byte ZIP64 file. Python independently verified eight entries. All six archived media files decoded completely. Studio and Editor HTTP downloads matched.

  The actual Foldkit browser download matched the CLI archive. Desktop and 390-pixel layouts were inspected. The run submitted no render or GPU inference. Both Pal Pal holds stayed unchanged.

  [Archive receipt](archive-runtime-receipt.json).
- The Mac launchd service was restarted while idle. Both Pal Pal holds now contain direction-v2 packets that name Cloudflare as the finisher. The browser-created job remains on attempt 1. No hold was resumed.
- Five offline audio-perception tests passed. A source-bound eight-second Pal Pal excerpt reached the pinned local Qwen2-Audio model. The model received 800 attended feature frames and 200 audio tokens. Peak allocation was 6.57 GB on the RTX 4070 Ti. Earlier descriptions from an ignored processor argument were invalidated. [Receipt](../audio-perception-canary-receipt.json). Full-song and audiovisual review remain separate.
- The complete-song model qualification stopped after one observed window. Window process isolation fixed retained GPU memory. The next response failed the observation contract and claimed a 3:20 transition in a 28-second excerpt. [Qualification](../audio-perception-qualification.json). This model is not qualified for automatic musical direction. No full-song listen or bulk approval is claimed.
- Later speech/silence calibration passed. A full-precision audio encoder fit the GPU. The current questionnaire processed all 239.68 seconds in ten windows. An independent execution-host decode audit verified coverage and rejected six numeric observations. [Complete coverage](../audio-perception-complete-coverage.json). Musical interpretation remains unverified.
- Real speech and an eight-second Pal Pal audio observation completed through the current Effect GPU abstraction. Terminal replays reused identical bytes without inference. The Pal Pal observer's two responses disagree about background music. Semantic qualification remains false.

  [Transport receipt](../gpu-observation-transport-receipt.json). Optional held-job observation preparation is implemented and tested. It remains disabled.
- Chronological lyric proposals preserve 29 lines and 184 exact native words. Recognition supplies 123 provisional word hints. Missing words retain null timings. Whisper forced alignment preserved the selected words but attached pre-roll to the first token. The new crop-edge guard prevents qualification of that result. [Lyric evidence](../lyric-evidence-qualification.json).
- Five explicitly selected CPU CTC operations completed through the same reserved transport. Wrong text and silence failed qualification. The known full-line control also retained uncertain words. No complete-line qualification is claimed.

  CTC token emissions remain distinct from verified word onsets. An independent source-bound audit found disagreements across recognition, Whisper and CTC. It preserved all raw times and rejected automatic timing qualification.
- One more CPU CTC operation tested the current Pal Pal vocal candidate. Eight decoded source windows showed zero measured shift relative to the master. The exact first-line alignment completed, but five words remained uncertain. Terminal replay reused the same receipt without inference.

  Historical cue boundaries differ by at most 0.06 seconds for this line. Their source lineage remains unverified. No lyric timing acceptance was recorded. [Vocal qualification](../pal-vocal-alignment-qualification.json).
- The vocal MP3 exposed a duration mismatch before model load. FFprobe on the workstation reported 239.725714 container seconds. Complete PCM decode measured 239.68 seconds. Browser selection, analysis, observer preflight and native verification now use decoded duration.

  The actual browser-exported brief preserved the original MP3 hash and measured 239.68 seconds. The original MP3 completed a new CPU alignment operation and identical terminal replay. Five words remain uncertain. The earlier failed operation and its inference fence remain preserved.

  [Duration receipt](../audio-duration-runtime-receipt.json).
- Nine full-length local Workerd/D1/R2 checks passed for the saved previous engine hash. A 239.68-second synthetic source produced a 5,753-frame film, three 720-frame portrait promos and two stills. Six cold stored-byte checks, complete downloaded decodes and eight archive-entry checks passed. Render and storage handoff took 1,371.502 seconds locally.

  Peak native Container count was one. Final count was zero. This establishes local synthetic performance. Cloud performance and real Pal Pal production remain unverified.

  [Full-length receipt](long-kit-runtime-receipt.json).
- The previous duration implementation passed a six-output MP3 regression through the actual local Container runtime. Its 48-frame film covered the complete two-second decoded source. Stored-byte verification, downloaded decodes and archive verification passed. The original compressed bytes and hash remained authoritative. [Compressed-source receipt](compressed-kit-runtime-receipt.json).
- The previous diagnostic engine passed eleven local Workerd/D1/R2 checks with a two-second MP3 source and six outputs. Every encoded frame was reduced to a 32-by-18 RGB-derived grayscale measurement. The verifier detected all 48 black frames and an undeclared freeze. An explicit image hold remained expected, and the planned join received a measured delta.

  Six cold checks reproduced the findings from stored bytes. Downloads decoded completely. The eight-entry archive passed independent verification. Peak native Container count was one.

  Final count was zero. Diagnostic credentials were revoked. Both Pal Pal holds stayed unchanged. [Diagnostic receipt](frame-diagnostics-runtime-receipt.json).
- Six more checks verified diagnostic export through the real agent archive CLI. The manifest preserved all six source-bound diagnostic records, thresholds, measured ranges and review suggestions. The blank/frozen warnings and expected image hold survived download. No new render or GPU operation ran. The diagnostic token was revoked. [Manifest export receipt](frame-diagnostics-archive-runtime-receipt.json).
- The previous preview engine passed eleven checks through the real agent CLI and local Cloudflare Container. A 36-frame source range produced a 960-by-540 review video and four 1920-by-1080 JPEG samples. The samples included both sides of a planned join. Independent source seeks measured mean RGB errors below 0.89 on the 0–255 scale.

  Stereo audio correlation, complete downloaded decodes, hashes, private ranges, tenant isolation and request bounds passed. A still preview produced two images without audio. Cached replay returned identical bytes without native compute. Peak native Container count was one.

  Final count was zero. Original kit bytes and both Pal Pal holds stayed unchanged. Diagnostic credentials were revoked. [Preview receipt](review-preview-runtime-receipt.json).
- Five Studio session checks verified cached preview creation and private full, ranged and HEAD downloads through the service binding. Foreign-origin mutations, missing sessions and another tenant's session were rejected. Sessions were logged out and the diagnostic token was revoked. The run submitted no native render or GPU inference.

  This verifies local HTTP session behavior. Browser playback and public-cloud deployment remain separate. [Session receipt](review-preview-session-runtime-receipt.json).
- The first full-length ending request exposed Bun's separate five-minute socket idle timeout. Native generation remained live after the caller timed out. The stored derivative was recovered and verified without duplicate native work. The client now disables that idle timer.

  The client retains explicit deadlines and lease cancellation. Native sample extraction extracts all requested JPEGs in one source decode. Full-source verification remains intact. [Failure record](review-preview-long-timeout-receipt.json), [stored recovery](review-preview-long-recovery-runtime-receipt.json), [Bun checks](request-client-runtime-receipt.json).
- The fixed engine passed eight fresh checks against the current 140 MB, 5,753-frame synthetic film. Its ten-second ending preview completed in 348.642 seconds through the real Bun CLI. All five downloaded derivatives passed hashes and complete decode. Four full-resolution samples matched independent source seeks. The last encoded frame was among them. Mean RGB errors were below 0.87.

  Both audio channels correlated above 0.9999 over the shorter 9.971667-second source tail. Cached replay took 0.107 seconds without native compute. Peak native count was one. Final count was zero.

  Original six-output receipts and both Pal Pal holds stayed unchanged. No new film render or GPU operation ran. [Full-length ending receipt](review-preview-long-runtime-receipt.json).
- Two ending JPEGs received visual inspection, with encoded frame 5,752 among them. Both showed intact diagnostic patterns and source counters. This remains separate from complete motion review, listening and creative acceptance. [Frame inspection](review-preview-long-frame-inspection.json).
- The owned launchd service loaded the observation backends and Editor client. Its current PID, source hashes and assigned holds are recorded in the [service readback](../editor-service-runtime-receipt.json). No Pal Pal hold was resumed.
- The pinned Qwen2.5-Omni-7B weights downloaded and passed full hash checks. The fixed backend is integrated into the Effect GPU transport and agent CLI. Its execution-host processor verified Pal Pal's exact eight-second PCM range, 800 attended frames and 200 audio tokens. Silence, known speech and two Pal Pal controls are prepared.

  Inference remains deferred while another music job owns the GPU. Model fit and semantic qualification remain unverified. [Omni receipt](../omni-observation-qualification.json).
- The source-bound Whisper pass preserved 23 raw segments and 176 words. Timing qualification rejected a word outside its segment. Exact Telugu lyrics remain unchanged. No timing repair was invented. [Speech qualification](../speech-evidence-qualification.json).
- Run-owned canary outputs are preserved under ignored `.local/`. Source-bound receipts are saved beside this file. The render runtime terminates after verified storage handoff and after independent verification.

## Deployment boundary

Alchemy declares `release-kit-editor-preview`, private D1/R2 bindings and one
`standard-3` container with zero warm instances. Container internet access is
disabled. The approved D1/R2/Containers OAuth expansion is saved for the
`release-kit-studio` Alchemy profile in the verified Dabbitech account.

The approved deployment attempt stopped during the plan phase: R2 is not activated,
and Containers require Workers Paid. Both checkout screens are ready. Approval for the new subscriptions, displayed terms, and usage budget remains unreviewed.
No cloud editor deployment or cloud render is claimed.

## Honest limits

`editor/feature-ledger.json` tracks implementation, verification, evidence and
remaining work per F01–F12. `bun run editor -- progress` and `/v1/progress` expose
it. The shared capacity gate and render tenant rotation are locally verified
in this Editor deployment. Cold verification uses the shared slot through bounded retry. Cold verification has no durable fairness queue.

Public-cloud enforcement, tenant quotas,
billing, public-cloud performance, crash/deadline behavior and creative quality
remain unverified. Unknown outcomes retain a render fence. Explicit cancellation can close the owned runtime without promotion of incomplete work.

Technical checks, frame inspection, complete motion review, listening and
creative acceptance remain distinct. The synthetic canary does not complete E08.

Frame diagnostics preserve every frame's timing but reduce spatial detail. Frame diagnostics identify candidates for review. Frame diagnostics cannot certify legibility, identity, sharpness, or seam quality. Findings retain thresholds and measured values.
Arrays contain at most 256 findings per type. Complete counts remain available.

Review previews bind the exact source hash and an end-exclusive frame range.
Video previews contain at most 240 frames and eight full-resolution JPEG samples.
Version 2 explicitly converts video color matrices for JPEG export. It uses a
different cache identity from the earlier, color-shifted diagnostic preview.

Preview generation does not record frame inspection, complete motion review,
listening or creative acceptance. The local amd64 Container runtime supplied the full-length ending performance measurements. Public-cloud performance remains unverified.
