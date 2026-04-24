# Phase One Hybrid Stem Extraction Design

## Summary

Expand phase one Step 2 from a vocals-only extraction step into a hybrid extraction step that
produces both:

- a canonical high-quality acapella for the existing remix pipeline
- a full six-stem arrangement pack for archival, analysis, and future mixing workflows

The recommended implementation keeps the current RoFormer vocal extraction path for
`<slug>-acapella.mp3` and adds a second `htdemucs_6s` separation pass that writes named stems into
`stems/`.

## Goals

- Preserve the current best-quality acapella asset for Step 5 and other vocal-first workflows.
- Make full stem extraction the default behavior for every phase-one run.
- Produce a predictable, named six-stem pack for archive and future production use.
- Keep downstream phase-one and phase-two contracts stable.
- Record the exact model outputs in `meta.json`.

## Non-Goals

- Do not replace the canonical acapella with the Demucs vocal stem.
- Do not redesign Step 5 or Step 6 to consume the full stem pack.
- Do not introduce best-effort fallbacks to smaller stem sets for the default path.
- Do not attempt DAW session export, stem mastering, or additional remixing features in this
  change.

## Current State

The repository already uses `audio-separator` through `tools/acapella-extractor/`.

Current behavior:

- `tools/acapella-extractor/src/acapella_extractor/extract.py` hardcodes
  `output_single_stem="vocals"`
- the default model is `mel_band_roformer_kim_ft_unwa.ckpt`
- Step 2 documents a single output: `<slug>-acapella.mp3`

This means the current limitation is not the underlying package. The limitation is the repo's
wrapper and prompt contract.

## Chosen Approach

Use a hybrid two-pass extraction model in Step 2.

### Pass 1: Canonical Acapella

- Model: `mel_band_roformer_kim_ft_unwa.ckpt`
- Purpose: highest-quality vocals-only extraction for the existing pipeline
- Required output: `<workspace>/<slug>/<slug>-acapella.mp3`

### Pass 2: Production Stem Pack

- Model: `htdemucs_6s.yaml`
- Purpose: named instrument separation for archive, analysis, and future mixing workflows
- Required outputs:
  - `<workspace>/<slug>/stems/<slug>-vocals.mp3`
  - `<workspace>/<slug>/stems/<slug>-drums.mp3`
  - `<workspace>/<slug>/stems/<slug>-bass.mp3`
  - `<workspace>/<slug>/stems/<slug>-guitar.mp3`
  - `<workspace>/<slug>/stems/<slug>-piano.mp3`
  - `<workspace>/<slug>/stems/<slug>-other.mp3`

### Why This Approach

- It keeps the strongest current vocal model in place.
- It uses a multi-stem model already supported by the existing `audio-separator` dependency.
- It avoids weakening Step 5 by forcing Suno uploads to depend on a lower-trust multi-stem vocal.
- It adds immediate value for stem archive and later production workflows without broad pipeline
  churn.

## Output Contract

Step 2 should write these files by default:

```text
<workspace>/<slug>/<slug>-acapella.mp3
<workspace>/<slug>/<slug>-instrumental.mp3
<workspace>/<slug>/stems/<slug>-vocals.mp3
<workspace>/<slug>/stems/<slug>-drums.mp3
<workspace>/<slug>/stems/<slug>-bass.mp3
<workspace>/<slug>/stems/<slug>-guitar.mp3
<workspace>/<slug>/stems/<slug>-piano.mp3
<workspace>/<slug>/stems/<slug>-other.mp3
```

Rules:

- `<slug>-acapella.mp3` is the official vocal source for the pipeline and comes from the RoFormer
  pass.
- `stems/` contains the named Demucs 6-stem outputs.
- `<slug>-instrumental.mp3` is a convenience artifact outside the stem directory for workflows that
  want a single backing track, derived from the Demucs non-vocal stems.
- Step 5 continues to consume `<slug>-acapella.mp3` unchanged.

## Metadata Contract

`meta.json` should record both status flags and the full stem manifest.

Example shape:

```json
{
  "status": {
    "mp3_downloaded": true,
    "acapella_extracted": true,
    "stems_extracted": true
  },
  "files": {
    "acapella": "<slug>/<slug>-acapella.mp3",
    "instrumental": "<slug>/<slug>-instrumental.mp3",
    "stems": {
      "vocals": "<slug>/stems/<slug>-vocals.mp3",
      "drums": "<slug>/stems/<slug>-drums.mp3",
      "bass": "<slug>/stems/<slug>-bass.mp3",
      "guitar": "<slug>/stems/<slug>-guitar.mp3",
      "piano": "<slug>/stems/<slug>-piano.mp3",
      "other": "<slug>/stems/<slug>-other.mp3"
    }
  },
  "stem_metadata": {
    "acapella_model": "mel_band_roformer_kim_ft_unwa.ckpt",
    "stem_model": "htdemucs_6s.yaml",
    "profile": "hybrid-production-pack"
  }
}
```

## Execution Flow

Step 2 should execute in this order:

1. Verify prerequisites:
   - original MP3 exists
   - `meta.json` exists
   - tool environment is available
2. Run the RoFormer extraction pass and produce `<slug>-acapella.mp3`.
3. Run the `htdemucs_6s` separation pass and produce all six stem files in `stems/`.
4. Derive `<slug>-instrumental.mp3` by combining the Demucs non-vocal stems.
5. Verify that every expected file exists and is readable.
6. Update `meta.json` with status and manifest information.

## Tooling Changes

### Extractor API

`tools/acapella-extractor/src/acapella_extractor/extract.py` should no longer be a vocals-only
wrapper. It should become a small extraction entrypoint that supports named profiles.

Recommended profiles:

- `acapella` for the existing RoFormer vocal pass
- `hybrid-production-pack` for the default Step 2 workflow

This change should stay minimal. The tool does not need a generic abstraction for every possible
future model. It only needs enough structure to support the approved hybrid path cleanly.

### Naming Normalization

The wrapper should normalize model-native output names into the repository naming convention.

That includes:

- writing the RoFormer output to `<slug>-acapella.mp3`
- writing Demucs outputs into `stems/` with lowercase canonical names
- ensuring `piano` stays named `piano` even if future UI text refers to `keys`

## Failure Handling

This workflow should fail fast. Partial success is not success for the default path.

Hard failures:

- missing canonical acapella output
- missing any of the six required Demucs stems
- unreadable or zero-byte audio files
- model setup or download failure

Behavior:

- stop immediately
- do not mark Step 2 complete
- print which output was missing or invalid

## Prompt and Documentation Changes

Update these documents to reflect the new Step 2 contract:

- `prompts/step-2-extract-acapella.md`
- `prompts/references/acapella-extractor-usage.md`
- `tools/acapella-extractor/README.md`
- any prompt index or summary text that still describes Step 2 as vocals-only

The step title can remain unchanged if minimizing prompt churn is preferred, but the body must make
the hybrid behavior explicit.

## Testing Strategy

- Unit tests for output renaming and stem manifest generation.
- Unit tests for profile dispatch between RoFormer and Demucs runs.
- Integration-style tests for the expected Step 2 file map using mocked separator outputs.
- Doc-level verification that Step 5 still references the canonical acapella path.

## Validation Targets

- Step 2 always produces `<slug>-acapella.mp3`.
- Step 2 always produces all six `htdemucs_6s` stem files.
- `meta.json` records both the convenience artifacts and the full stem pack.
- Downstream phase-one steps remain compatible without consuming the new stems.
- The implementation remains within the current `audio-separator` toolchain.

## Implementation Notes

- `htdemucs_6s` is the chosen default because it is the cleanest path to named multi-stem output in
  the current stack.
- The Demucs `vocals` stem is useful for the stem pack but should not silently replace the RoFormer
  acapella.
- If runtime later proves too expensive, the next simplification would be changing the stem pass to
  `htdemucs_ft`, not removing the separate RoFormer acapella pass.
