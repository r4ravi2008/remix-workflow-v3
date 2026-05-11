# ACE-Step Local Generation Design

## Summary

Add ACE-Step 1.5 as a local music-generation backend for the remix pipeline. The existing Suno flow remains available, but users can choose a local path that generates remix candidates directly on their machine without uploading acapella audio to Suno.ai.

The first implementation should use a direct Python tool because it fits the user's preference and keeps generation as a normal pipeline step instead of introducing browser automation or a required localhost service.

## Current Pipeline Context

The current pipeline creates reusable assets before generation:

- Step 0 creates the workspace and `meta.json`.
- Step 1 downloads the original audio.
- Step 2 extracts `<slug>-acapella.mp3`.
- Step 3 saves native-script lyrics.
- Step 4 writes `<slug>-suno-lyrics.txt`, `<slug>-suno-style.txt`, and `design.json`.
- Step 5 uploads the acapella to Suno and downloads two variations.
- Step 5.5 asks the user to select one remix.
- Steps 6-11 consume the selected remix audio and do not depend on Suno-specific details.

ACE-Step should replace only Step 5 at first. Steps 0-4 and 5.5-11 should remain compatible.

## Goals

- Generate two remix candidates locally using ACE-Step.
- Avoid uploading source vocals or song material to Suno.ai.
- Preserve the existing workspace structure and downstream pipeline contracts.
- Keep Suno as a selectable backend for cases where local generation is not available or quality is not good enough.
- Make local generation reproducible enough to diagnose issues by saving model, prompt, seed, and task metadata.

## Non-Goals

- Do not remove or rewrite the Suno path.
- Do not build a custom UI for ACE-Step.
- Do not require ACE-Step's REST API server for the first path.
- Do not train ACE-Step LoRAs as part of this integration.
- Do not change lyric alignment, video generation, metadata, or shorts steps except where they read the selected remix file path.

## Backend Selection

Add a generation backend setting to workspace metadata:

```json
{
  "generation_backend": "ace-step"
}
```

Allowed values:

- `suno`: existing Step 5 browser-upload flow.
- `ace-step`: new direct local Python flow.

If the field is absent, the pipeline should default to `suno` to avoid changing existing workspaces.

## New Tool

Create `tools/ace-step-generator/` with a Python entrypoint that wraps ACE-Step's Python inference API.

Proposed command shape:

```bash
uv run python generate.py \
  --workspace-dir /absolute/path/to/workspace \
  --slug <slug> \
  --ace-step-root /absolute/path/to/ACE-Step-1.5 \
  --task-type cover \
  --batch-size 2 \
  --output-format mp3
```

The tool should read existing workspace files, initialize ACE-Step handlers, generate candidates, normalize output filenames, and update a generation report. It should not update `meta.json` directly unless the step prompt explicitly instructs it to, so metadata ownership stays with the pipeline step.

## Inputs

Required workspace inputs:

- `meta.json`
- `<slug>-lyrics.txt`
- `<slug>-suno-style.txt`
- `<slug>-acapella.mp3` or `<slug>-original.mp3`

Preferred source audio:

- Use `<slug>-acapella.mp3` first for vocal-guided remixing.
- Fall back to `<slug>-original.mp3` if acapella is unavailable and the user explicitly accepts using the full original track.

Prompt inputs:

- Use `<slug>-suno-style.txt` as the initial ACE-Step caption because it already encodes genre, mood, language, vocal type, BPM, and instrumentation.
- Use native-script lyrics from `<slug>-lyrics.txt` or a cleaned version of `<slug>-suno-lyrics.txt`.
- Strip production cues only if ACE-Step quality suffers; the first implementation can pass bracket section tags because ACE-Step supports structured lyrics.

Metadata inputs:

- Map `meta.json.language` to ACE-Step `vocal_language` where practical.
- Map `meta.json.tempo` to approximate BPM if Step 4 did not already encode a BPM.
- Use `meta.json.song_length` to decide duration: full songs should allow automatic duration unless the user provides an explicit target.

## Generation Mode

The first implementation should default to ACE-Step `task_type="cover"` because this project is remixing an existing song, not generating unrelated music from scratch.

Cover parameters:

- `src_audio`: source audio path, preferably the acapella.
- `caption`: target genre/style prompt from Step 4.
- `lyrics`: native-script lyrics.
- `audio_cover_strength`: default `0.7` for a balanced remix that preserves source character while allowing style change.
- `batch_size`: default `2` to preserve the current Step 5.5 selection flow.
- `audio_format`: `mp3` to match current downstream file expectations.

Fallback generation mode:

- Support `task_type="text2music"` as a manual fallback when cover mode fails or produces poor results.
- Text-to-music should use the same caption and lyrics, with `thinking=true` when the user's hardware supports the LM.

## Outputs

The ACE-Step step should write the same candidate files as the Suno step:

- `<slug>-remix-v1.mp3`
- `<slug>-remix-v2.mp3`

It should also write:

- `<slug>-ace-step-generation.json`

The generation report should include:

```json
{
  "backend": "ace-step",
  "task_type": "cover",
  "model": "acestep-v15-turbo",
  "lm_model": null,
  "source_audio": "<slug>/<slug>-acapella.mp3",
  "caption": "...",
  "lyrics_file": "<slug>/<slug>-lyrics.txt",
  "batch_size": 2,
  "audio_cover_strength": 0.7,
  "outputs": [
    "<slug>/<slug>-remix-v1.mp3",
    "<slug>/<slug>-remix-v2.mp3"
  ],
  "seeds": [],
  "created_at": "ISO-8601 timestamp"
}
```

## Meta.json Updates

For ACE-Step generation, Step 5 should set the same downstream-compatible status keys currently used for Suno candidates:

```json
{
  "files": {
    "remix_v1": "<slug>/<slug>-remix-v1.mp3",
    "remix_v2": "<slug>/<slug>-remix-v2.mp3",
    "ace_step_generation": "<slug>/<slug>-ace-step-generation.json"
  },
  "status": {
    "remix_uploaded": false,
    "remix_v1_downloaded": true,
    "remix_v2_downloaded": true,
    "ace_step_generated": true
  }
}
```

The `remix_v*_downloaded` names are not ideal for local generation, but keeping them avoids broad downstream changes. Add the more explicit `ace_step_generated` key for clarity.

## Prompt Step Changes

Add a new prompt file:

- `prompts/step-5-generate-with-ace-step.md`

This prompt should:

- Resolve the workspace root using existing conventions.
- Verify ACE-Step is installed or ask for `ACE_STEP_ROOT` / config path.
- Verify required files exist.
- Run `tools/ace-step-generator/generate.py`.
- Confirm the two candidate files exist and are playable audio files.
- Update `meta.json`.
- Continue to Step 5.5 with the same user selection wording.

Update the prompt index and README to describe Step 5 as backend-selectable rather than Suno-only.

## Error Handling

Expected failures and recovery:

- Missing ACE-Step checkout: stop with setup instructions and do not modify `meta.json` generation status.
- Missing Python dependencies: tell the user to run `cd tools/ace-step-generator && uv pip install -e "$ACE_STEP_ROOT"` so ACE-Step and its dependencies are installed in the generator tool environment.
- Out of memory: retry with lower duration, CPU offload, or turbo model; if resources are still insufficient, stop and ask whether to change resources or switch backends.
- Cover mode failure: offer fallback to `text2music` using the same caption and lyrics.
- One candidate generated instead of two: keep Step 5 incomplete, do not proceed to Step 5.5, and generate the missing candidate or ask whether to change resources or backend.
- Output file format mismatch: transcode to MP3 with FFmpeg before updating workspace status.

## Testing And Verification

Unit-level checks:

- Test prompt/lyrics loading from a mock workspace.
- Test output filename normalization from arbitrary ACE-Step output paths.
- Test generation report writing.
- Test `meta.json` update logic in the prompt instructions or helper script if implemented.

Integration checks:

- Run the tool in dry-run mode against a mock workspace to verify command construction and file validation.
- If ACE-Step is available locally and resources permit, run a short two-candidate real generation; otherwise rely on dry-run and unit tests rather than validating a one-candidate output.
- Verify Steps 6-11 still accept ACE-Step candidate files without Suno URLs.

## First-Slice Decisions

- Require `ACE_STEP_ROOT` as an environment variable or command-line argument for the first implementation. A repo-local config file can be added later if repeated usage makes that worthwhile.
- Use acapella as the default source for cover mode. Original audio is only a fallback when acapella is missing and the user approves the tradeoff.
- Keep advanced ACE-Step settings as tool defaults and command-line flags. Do not add them to `meta.json` until there is a concrete need to persist them per remix.

## Recommended First Slice

Implement the smallest end-to-end version:

- Add `tools/ace-step-generator/generate.py` with direct Python invocation and dry-run support.
- Add `prompts/step-5-generate-with-ace-step.md`.
- Update docs to describe backend selection.
- Generate two local MP3 candidates matching the current Suno output names.
- Leave Step 5.5 and downstream steps unchanged.
