# Native picture masks unit A01

Status: design only. A09 preserves the completed motion unit before this work.

## Purpose

Support source-bound masked picture composition and reveals in the general native editor.
The Panja film needs motivated transitions between real footage and its generated counterpart.
A mask unit cannot establish an accepted musical passage, story, playback or listening.

## Fixed boundaries

- Preserve immutable snapshots, stable intents, source lineage, exact clocks and receipt identities.
- Preserve the current deep `Project` aggregate and direct CLI.
- Do not expose readers, native objects, workers, compositors or ordered stages to callers.
- Retain in-process AVFoundation output and cooperative export ownership.
- Retain one measured stereo 48 kHz PCM clip, unity gain and zero pan.
- Keep tenant, provider and UI adapters separate from the Rust runtime.
- Preserve actual historical Snapshot 1, Plan 2/3/4/5 and Receipt 2 documents byte for byte.
- Keep schemas 2/3/4/5 on their existing paths when no mask is authored.
- Keep the four-track limit, capacity-one picture channels and explicit logical payload admission.
- Do not change source ordinals, source PTS, output PTS or the canonical master binding.
- Retain all movie, generated-source, old observer and predecessor artifacts.
- Do not mutate GPU, Resolve, film project or provider state during design.

Actual motion-era documents now reside in `tests/fixtures/legacy/plan-schema5.json`
and `snapshot-schema1-motion.json`. Their immutable database bytes and expected hashes
are recorded in `masks-legacy-fixtures-a01.json`. Focused roundtrip tests remain pending.

## Questions each complete candidate must resolve

1. Define the mask authoring shape, stored execution shape and scalar observation boundary.
2. Choose source or destination coordinates and explain crop, fit, placement and motion interactions.
3. Define the first useful mask family and its deferred extensions.
4. Specify coverage, inversion, opacity combination, sampling and edge behavior exactly.
5. Explain contain bars, signed clipping, sparse tracks and fully masked frames.
6. Choose internal alpha precision and blending order without changing opaque input semantics silently.
7. Account for owned mask, source, raster, cache, response and canvas payloads.
8. Keep cancellation, shutdown and native callback ownership verifiable.
9. Define schema selection, normalization and central tamper checks.
10. Provide examples through the existing public `Project` operations.
11. Define independent pure-pixel and actual native tests before implementation.

## Required proof structure

Build on the completed motion unit's source and receipt checks.
Use expected file hashes anchored before the run, rather than comparing a file hash with itself.
Require each source closure entry, measurement producer, selected ordinal and source PTS explicitly.
Bind the immutable receipt document and complete fresh product reverify result.
Require explicit observed clock fields; do not supply a missing epoch as zero.
Compare each fresh audio capture to the actual selected WAV interval under the declared policy.
Decoded AAC floating-point bytes can vary between reads; retain and report observed variation.
Retain unsuccessful attempts and identify any lost bytes as unverifiable.
Use deliberate corrupt-record controls against the independent validation helpers.
Keep the musical and creative acceptance gates separate from bounded native technical proof.

## Candidate independence

Candidate A and Candidate B may read current code, A14 and this task.
Neither candidate may read the sibling candidate until both drafts are delivered.
The judge reads both complete designs after delivery.
No cross-family reviewer is available through the current agent tools.
