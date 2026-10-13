# Automated director implementation

This document records director work with the separate Cloudflare editor. It does not report completion of the standalone Rust editor.

The artist uploads one song and receives a six-output Release Kit. Cinematic
direction, exact native lyrics and environment reactivity must work together.
The separate Cloudflare editor Worker owns edit operations and native cloud rendering.
The GPU abstraction connects to the workstation through Tailscale and Herdr.

## Current progress

| ID | Capability | Current evidence | Next acceptance condition |
|---|---|---|---|
| D01 | Frozen song and artist inputs | Live Pal Pal upload, exact SHA-256, 239.68 seconds, Telugu lyrics, direction-v2 packets | Reverify the same binding before each production attempt |
| D02 | Actual audio perception | Known speech/silence calibration passed. Complete 239.68-second input coverage passed verification. The audit rejected six numeric claims | Reliable musical interpretation. Automatic-direction qualification still fails |
| D03 | Native lyric timing | Source-bound Whisper pass preserved 176 raw words. Invalid word range rejected | Align exact supplied words against the frozen master. Inspect phrasing |
| D04 | Chronological story and coverage | Artist brief preserves the existing characters and neon-city identity | Full coverage, stable identity, distinct portrait plans and hardest-passage pilot |
| D05 | GPU footage and observation operations | Existing footage transport. Real speech observation and replay verified. Optional held-job preparation tested | Reviewed shot graphs and new originals. Qualify perception before automation starts |
| D06 | Editor integration and output QC | Measured-project and generated-media canaries each produced six outputs locally | Public-cloud readback and a complete source-bound Pal Pal kit |
| D07 | Automatic pilot and film review | Review evidence remains separate from technical checks | Actual motion/audio ranges, artifact hashes, protected masks and final review |

## Implementation sequence

1. Before you connect perception to held jobs, qualify perception against known fixtures.

   A processed excerpt cannot certify its interpretation or approve bulk generation.

2. Preserve failed observations and uncertainty.

3. Expose qualified perception through an Effect service and the same reserved workstation transport.

4. Bind requests and results to the complete frozen brief.

5. After a lost response, reconcile the saved evidence.

6. Preserve unknown outcomes.

7. Add source-bound lyric timing with exact native words.

   Historical timestamps remain draft inputs until verification against the current master is complete.

8. Generate a typed storyboard and six-output recipe from the frozen brief, reliable observations, and measured song curves.

9. Reject coverage gaps before GPU inference.

10. Calculate generated hashes only after you collect actual originals.

11. Produce the hardest complete pilot passage.

12. Review that passage.

13. Bind image, motion, sound, masks, and caption findings to exact bytes and ranges.

14. Resume the assigned hold only after reviewed coverage exists.

15. Preserve the outer job lease throughout generation, editor rendering, and R2 promotion.

16. Verify all six stored outputs and their private downloads.

Complete motion, listening, and creative acceptance remain explicit evidence states.

## Current model boundary

Qwen2-Audio-7B-Instruct runs locally with NF4 text decoding and full-precision
audio encoding. The pinned revision is
`0a095220c30b7b31434169c3086508ef3ea5bf0a`. The runner validates actual audio
features, attended frames and audio tokens. Each window runs in a separate
process and reserves the shared GPU lease.

Known speech and silence calibration passed. All ten Pal Pal windows reached the
model and covered the song tail. A separate execution-host audit verified exact
decoded checksums and coverage. It rejected six unmeasured numeric observations.

These results do not qualify musical interpretation or establish a full-song
listen. Earlier failed attempts remain preserved. See
[complete coverage](audio-perception-complete-coverage.json) and the historical
[qualification](audio-perception-qualification.json).

The Effect GPU service now exposes fixed source-bound observation operations. The real speech operation completed through Tailscale/Herdr. A repeat reused the identical receipt without inference. Pal Pal's audio transport request
deferred when shared GPU work appeared.

See
[transport receipt](gpu-observation-transport-receipt.json).

Optional held-job observation preparation is implemented and tested. The installed
service configuration leaves it disabled. Complete observation coverage cannot
resume a production hold or approve bulk generation.

Whisper processed the complete source into raw recognition evidence. Timing
validation rejected one word that exceeded its segment boundary. The canonical
Telugu lyrics remain unchanged. See
[speech qualification](speech-evidence-qualification.json).

Cloudflare Workers Paid/R2 activation and a usage budget remain pending. Local
canaries do not complete hosted production or the Pal Pal Release Kit.
