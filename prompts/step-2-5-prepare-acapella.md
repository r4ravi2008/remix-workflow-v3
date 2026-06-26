# Step 2.5: Prepare Acapella BPM/Pitch

## Objective

Analyze the original full mix for BPM and key metadata, then render a Step-5-ready acapella file with deterministic tempo/pitch settings. Preserve the raw extracted acapella from Step 2.

Default behavior:
- Detect BPM/key from `${WORKSPACE_DIR}/${SLUG}-original.mp3`.
- Use detected BPM as the target BPM when no explicit target is provided.
- Preserve pitch by default with `--pitch-semitones 0`.
- Always create `${SLUG}-acapella-prepped.mp3` so Step 5 has a stable input.

## Prerequisites

- `${WORKSPACE_DIR}/meta.json` exists.
- `${WORKSPACE_DIR}/${SLUG}-original.mp3` exists from Step 1.
- `${WORKSPACE_DIR}/${SLUG}-acapella.mp3` exists from Step 2.
- Tool location: `tools/acapella-extractor/`.

## Workspace Path Resolution

Before using any filesystem path in this step:

1. Read `.remix-workspace-root.json` from the repo root.
2. Resolve `WORKSPACE_ROOT` from its `workspaceRoot` field.
3. Resolve `WORKSPACE_DIR` as `<workspaceRoot>/<slug>/`.
4. Use absolute paths under `WORKSPACE_DIR` for filesystem commands.
5. Keep stored `meta.json.files.*` values root-relative, for example `<slug>/<slug>-acapella-prepped.mp3`.

## Instructions

### 2.5.1 - Verify Tool Setup

```bash
ls -la tools/acapella-extractor/.venv/bin/python
ls -la tools/acapella-extractor/src/acapella_extractor/prepare.py
ffmpeg -hide_banner -filters | rg 'rubberband'
```

If the Python environment is missing, run:

```bash
cd tools/acapella-extractor && uv sync
```

If FFmpeg lacks `rubberband`, install an FFmpeg build with rubberband support before continuing.

### 2.5.2 - Run Default Preparation

Use this command unless the user explicitly requested a target BPM or pitch shift:

```bash
PYTHONPATH=tools/acapella-extractor/src \
uv run --python tools/acapella-extractor/.venv/bin/python \
python -m acapella_extractor.prepare \
  --workspace-dir "${WORKSPACE_DIR}" \
  --slug "${SLUG}"
```

This detects the original song BPM and uses it as the target BPM, preserving pitch.

### 2.5.3 - Optional Explicit Target BPM Or Pitch

Only add these flags when the user explicitly requests them:

```bash
--target-bpm 92
--pitch-semitones -2
```

The tool applies:

```text
tempo_ratio = target_bpm / detected_bpm
pitch_ratio = 2 ** (pitch_semitones / 12)
```

Rendering uses FFmpeg `rubberband` with formant preservation and high pitch quality.

### 2.5.4 - Verify Outputs

Expected files:

```bash
ls -lh "${WORKSPACE_DIR}/${SLUG}-acapella-prepped.mp3"
cat "${WORKSPACE_DIR}/${SLUG}-acapella-prep.json"
```

The report must include:
- detected BPM
- target BPM
- tempo ratio
- detected key and key candidates
- pitch semitones
- pitch ratio
- input/output paths
- FFmpeg command summary

### 2.5.5 - Metadata

The tool updates `${WORKSPACE_DIR}/meta.json`:

```json
{
  "files": {
    "acapella_prepped": "<slug>/<slug>-acapella-prepped.mp3",
    "acapella_prep_report": "<slug>/<slug>-acapella-prep.json"
  },
  "status": {
    "acapella_prepped": true
  },
  "audio_analysis": {
    "detected_bpm": 89.1,
    "target_bpm": 89.1,
    "detected_key": "D minor",
    "pitch_semitones": 0
  }
}
```

Preserve all unrelated metadata fields.

## File Outputs

| File | Path | Description |
|---|---|---|
| Prepped acapella | `<workspaceRoot>/<slug>/<slug>-acapella-prepped.mp3` | Step-5-ready vocal reference |
| Prep report | `<workspaceRoot>/<slug>/<slug>-acapella-prep.json` | BPM/key/pitch analysis and render metadata |
| Metadata | `<workspaceRoot>/<slug>/meta.json` | Updated files/status/audio analysis |

## Error Handling

| Error | Solution |
|---|---|
| Missing original MP3 | Re-run Step 1 |
| Missing raw acapella | Re-run Step 2 |
| BPM detection fails | Verify the original MP3 is readable and not silent |
| `rubberband` filter missing | Install an FFmpeg build with rubberband support |
| FFmpeg render fails | Inspect `<slug>-acapella-prep.json` if written, then retry after fixing the input/filter issue |

## Next Step

Proceed to Step 3: Find Lyrics. Step 5 must use `${SLUG}-acapella-prepped.mp3` by default.
