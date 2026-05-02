# Fal Frame Stylizer Design

## Goal

Create a reusable slug-based fal.ai frame stylization script for Step 7 visual sequences. The script will take a workspace slug and a prompt file, edit selected source frames through fal.ai Nano Banana Pro, and write consistently named outputs into `stylized-frames/` for manifest generation.

## Recommended Approach

Add `tools/visual-sequence/stylize-fal.ts` as a TypeScript CLI using `effect@beta` / Effect v4. Keep it separate from `visual-sequence.js` so extraction and manifest logic stay stable while the external API workflow can evolve independently.

## CLI

```bash
node tools/visual-sequence/stylize-fal.ts <slug> \
  --prompt-file=<path> \
  [--limit=N] \
  [--frame=frame-001] \
  [--concurrency=N] \
  [--overwrite] \
  [--dry-run]
```

Defaults:
- `--concurrency=2` to avoid expensive request spikes.
- Skip existing outputs unless `--overwrite` is set.
- Process every selected frame unless `--limit` or `--frame` is provided.

## Inputs

- `FAL_API_KEY` from the environment.
- `<slug>/selected-visual-frames.json` for frame order and `source_image_path` values.
- Prompt text from `--prompt-file`. For this remix, the prompt is stored in `frame-stylization-prompt-template.txt`.
- Source frames under `<workspace>/<slug>/source-frames/`.

## Outputs

- Stylized frame images saved as `stylized-frames/<slug>-frame-001.jpg` and so on.
- A concise run summary showing processed, skipped, and failed frames.
- `meta.json.status.visual_frames_stylized=true` only after at least one stylized image exists and all requested frames for the run succeeded.

## Effect v4 Usage

Use `effect@beta` for:
- Typed config loading and validation.
- Explicit failure channels for missing env vars, missing files, invalid prompt files, upload failures, and download failures.
- Retry policy with bounded retries for transient fal.ai/network failures.
- Controlled concurrency for batch processing.

Avoid unstable modules unless required by the fal.ai SDK integration.

## fal.ai Integration

Use Nano Banana Pro edit model: `fal-ai/nano-banana-pro/edit`.

Each frame request sends:
- One source image.
- The shared prompt.
- 16:9 output preference if supported by the model API.
- JPEG output when supported; otherwise save the returned image extension and rely on existing manifest support for `.jpg`, `.jpeg`, `.png`, and `.webp`.

## Error Handling

- Missing `FAL_API_KEY`: fail before reading or uploading images.
- Missing selected frames: fail with command to run extraction first.
- Missing prompt file: fail with the expected file path.
- Existing output: skip unless `--overwrite` is present.
- Partial batch failure: keep successful outputs, print failures, and exit non-zero.

## Testing

Add tests for:
- Argument parsing.
- Frame filtering from `--limit` and `--frame`.
- Skip/overwrite behavior.
- Missing env and missing file errors.
- Mocked fal client response writing to `stylized-frames/` without calling fal.ai.

## Current Remix Usage

For the current workspace:

```bash
node tools/visual-sequence/stylize-fal.ts manike-mage-hithe-manake-love-a-ayithe-deep-house \
  --prompt-file=workspaces/manike-mage-hithe-manake-love-a-ayithe-deep-house/frame-stylization-prompt-template.txt \
  --limit=1
```

After approving the test frame, run the same command without `--limit=1`, then generate the manifest:

```bash
node tools/visual-sequence/visual-sequence.js manifest manike-mage-hithe-manake-love-a-ayithe-deep-house
```
