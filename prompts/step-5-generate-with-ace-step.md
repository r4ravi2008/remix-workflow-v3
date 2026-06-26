# Step 5: Generate Remix Locally with ACE-Step

## Objective

Generate two remix candidates locally with ACE-Step 1.5 instead of uploading the acapella to Suno.ai. Save the candidates using the same filenames expected by Step 5.5 and downstream steps.

## Prerequisites

- `${WORKSPACE_DIR}/${SLUG}-acapella-prepped.mp3` exists from Step 2.5.
- `${WORKSPACE_DIR}/${SLUG}-lyrics.txt` exists from Step 3.
- `${WORKSPACE_DIR}/${SLUG}-suno-style.txt` exists from Step 4.
- `${WORKSPACE_DIR}/meta.json` exists with `slug`, `genre`, `language`, `tempo`, and `song_length`.
- `tools/ace-step-generator` dependencies are installed with `uv sync`; ACE-Step 1.5 is a required dependency.
- `--ace-step-root` is optional and only needed to override the installed package with a local ACE-Step source checkout.

## Workspace Path Resolution

Before using any filesystem path in this step:

1. Read `.remix-workspace-root.json` from the repo root.
2. Resolve `WORKSPACE_ROOT` from its `workspaceRoot` field.
3. Resolve `WORKSPACE_DIR` as `<workspaceRoot>/<slug>/`.
4. Use absolute paths under `WORKSPACE_DIR` for filesystem commands.
5. Keep stored `meta.json.files.*` values root-relative, for example `<slug>/<slug>-remix-v1.mp3`.

## Instructions

### 5.1 - Verify Local ACE-Step Setup

Confirm the ACE-Step generator environment is installed:

```bash
cd tools/ace-step-generator && uv sync
```

If the user provides a source checkout override, verify it before passing `--ace-step-root`:

```bash
test -d "$ACE_STEP_ROOT" && test -f "$ACE_STEP_ROOT/pyproject.toml"
```

### 5.2 - Verify Workspace Inputs

Check that these files exist:

- `${WORKSPACE_DIR}/meta.json`
- `${WORKSPACE_DIR}/${SLUG}-lyrics.txt`
- `${WORKSPACE_DIR}/${SLUG}-suno-style.txt`
- `${WORKSPACE_DIR}/${SLUG}-acapella-prepped.mp3`

If the prepped acapella is missing but `${WORKSPACE_DIR}/${SLUG}-acapella.mp3` exists, stop and ask before passing `--allow-raw-acapella-fallback` because Step 2.5 should normally prepare the Step-5 input. If both acapella files are missing but `${WORKSPACE_DIR}/${SLUG}-original.mp3` exists, ask before using `--allow-original-fallback` because the full mix may preserve less vocal control than the acapella.

### 5.3 - Optional JSON Config

Use defaults unless the user asks for specific ACE-Step controls. Config precedence is:

1. workspace defaults from lyrics/style/meta files
2. JSON config from `--config`
3. CLI flags

Default lyrics handling is `clean-native`: strip blank lines and metadata header lines beginning with `#`, preserve native Indic script, and keep bracketed lyric content. Use `suno-stripped` only when the lyrics file contains Suno section tags such as `[Verse]` or `[Chorus]` that should be removed. Use `raw` only when exact file contents should be sent to ACE-Step.

Example config at `${WORKSPACE_DIR}/ace-step-config.json`:

```json
{
  "caption": "deep house, romantic nocturnal, Hindi, intimate male vocal, 122 bpm",
  "audio_cover_strength": 0.6,
  "bpm": 122,
  "duration": 183,
  "guidance_scale": 8.5,
  "omega_scale": 10.0,
  "lyrics_mode": "clean-native",
  "manual_seeds": [111, 222],
  "use_random_seed": false
}
```

Supported CLI overrides include `--caption`, `--lyrics-file`, `--lyrics-mode`, `--guidance-scale`, `--omega-scale`, `--seeds`, `--use-random-seed` / `--no-use-random-seed`, `--bpm`, and `--duration`.

Use `--allow-raw-acapella-fallback` only after the user explicitly approves using `${SLUG}-acapella.mp3` because `${SLUG}-acapella-prepped.mp3` is missing.

### 5.4 - Dry Run The ACE-Step Tool

Run a dry run first to validate inputs and write an inspection report:

```bash
uv run --no-sync python -m ace_step_generator.generate \
  --workspace-dir "${WORKSPACE_DIR}" \
  --slug "${SLUG}" \
  --task-type cover \
  --batch-size 2 \
  --output-format mp3 \
  --dry-run
```

Working directory:

```bash
tools/ace-step-generator
```

Add `--config "${WORKSPACE_DIR}/ace-step-config.json"` if using a config file. Add `--ace-step-root "${ACE_STEP_ROOT}"` only when intentionally overriding the installed ACE-Step package.

Verify `${WORKSPACE_DIR}/${SLUG}-ace-step-generation.json` exists, has `"dry_run": true`, and records the intended `effective_request`.

### 5.5 - Generate Two Local Candidates

Run ACE-Step generation:

```bash
uv run --no-sync python -m ace_step_generator.generate \
  --workspace-dir "${WORKSPACE_DIR}" \
  --slug "${SLUG}" \
  --task-type cover \
  --batch-size 2 \
  --output-format mp3
```

Add the same `--config` and CLI override flags used in the approved dry run.

Expected outputs:

- `${WORKSPACE_DIR}/${SLUG}-remix-v1.mp3`
- `${WORKSPACE_DIR}/${SLUG}-remix-v2.mp3`
- `${WORKSPACE_DIR}/${SLUG}-ace-step-generation.json`

### 5.6 - Recovery Paths

If ACE-Step runs out of memory with `--batch-size 2`, stop and ask the user before changing generation mode, model, device, or system resources. Do not treat `--batch-size 1` as a complete Step 5 output unless the tool later supports accumulating two normalized candidates, because downstream steps require both `${SLUG}-remix-v1.mp3` and `${SLUG}-remix-v2.mp3`.

If cover mode fails or quality is unusable, ask the user whether to try text-to-music mode:

```bash
uv run --no-sync python -m ace_step_generator.generate \
  --workspace-dir "${WORKSPACE_DIR}" \
  --slug "${SLUG}" \
  --task-type text2music \
  --batch-size 2 \
  --output-format mp3
```

### 5.7 - Update meta.json

Update `${WORKSPACE_DIR}/meta.json`:

```json
{
  "generation_backend": "ace-step",
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

Preserve all existing unrelated `meta.json` fields.

### 5.8 - Ask User To Select A Candidate

Print:

```text
ACE-Step remix candidates generated:
1. <workspaceRoot>/<slug>/<slug>-remix-v1.mp3
2. <workspaceRoot>/<slug>/<slug>-remix-v2.mp3

Generation report: <workspaceRoot>/<slug>/<slug>-ace-step-generation.json

Listen to both files and reply `v1` or `v2` for the video.
```

### 5.9 - Persist the Selected Remix

After the user replies with `v1` or `v2`, update `${WORKSPACE_DIR}/meta.json` before proceeding:

```json
{
  "status": {
    "selected_remix": "v1 or v2"
  }
}
```

If the response is anything else, stop and ask the user to choose `v1` or `v2` explicitly. After `meta.json.status.selected_remix` is set, proceed to Step 6.
