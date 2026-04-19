# Step 1: Download MP3 from YouTube

## Objective

Download the YouTube video as an MP3 file directly into the workspace using yt-dlp.

## Prerequisites

- `WORKSPACE_DIR` exists (created in Step 0)
- `${WORKSPACE_DIR}/meta.json` exists with `youtube_url` and `slug`
- `uv`/`uvx` available for running yt-dlp

## Workspace Path Resolution

Before using any filesystem path in this step:

1. Read `.remix-workspace-root.json` from the repo root.
2. Resolve `WORKSPACE_ROOT` from its `workspaceRoot` field.
3. Resolve `WORKSPACE_DIR` as `<workspaceRoot>/<slug>/`.
4. Use absolute paths under `WORKSPACE_DIR` for filesystem commands.
5. Keep any stored `meta.json.files.*` values root-relative, for example `<slug>/design.json`.

---

## Instructions

### 1.1 — Download MP3 with yt-dlp

**Bash tool:**

Use `uvx yt-dlp` to download the audio from the YouTube URL and save it as MP3:

```bash
SLUG="<slug from meta.json>"
YOUTUBE_URL="<youtube_url from meta.json>"

uvx yt-dlp \
  -x \
  --audio-format mp3 \
  --audio-quality 0 \
  -o "${WORKSPACE_DIR}/${SLUG}-original.%(ext)s" \
  "$YOUTUBE_URL"
```

**Options explained:**
- `-x` or `--extract-audio`: Extract audio only (no video)
- `--audio-format mp3`: Convert to MP3 format
- `--audio-quality 0`: Best audio quality (0 = best, 9 = worst for VBR)
- `-o`: Output template for filename

---

### 1.2 — Verify Download

Verify the file was downloaded successfully:

```bash
ls -lh "${WORKSPACE_DIR}/${SLUG}-original.mp3"
```

Expected output: file exists with size > 1MB.

---

### 1.3 — Update meta.json Status

**Write tool:**

Update `${WORKSPACE_DIR}/meta.json` to mark this step complete:

Set `status.mp3_downloaded` to `true` in `meta.json`:

```json
"status": {
  "mp3_downloaded": true
}
```

> **Note:** Only update the fields shown above. Do not overwrite other status fields.

---

### 1.4 — Confirm File Ready

Print a summary before proceeding:

```
MP3 downloaded: <workspaceRoot>/<slug>/<slug>-original.mp3
File size: <size>

Proceeding to Step 2: Extract Acapella...
```

---

## File Outputs

| File | Path |
|---|---|
| Downloaded MP3 | `<workspaceRoot>/<slug>/<slug>-original.mp3` |
| Updated metadata | `<workspaceRoot>/<slug>/meta.json` |

---

## Error Handling

**See**: [Error Handling Patterns > YouTube Download Errors](references/error-handling-patterns.md#youtube-download-errors-step-1) for detailed fixes.

| Error | Solution |
|---|---|
| 403/401 Forbidden | Add `--cookies-from-browser chrome` or `--cookies-from-browser safari` |
| No audio formats available | Try without `-x`, then extract audio with ffmpeg |
| uvx not found | Install uv: `brew install uv` |
| File is 0 bytes | Check disk space and permissions |

---

## Reference

- [Workspace Conventions](references/workspace-conventions.md) — File naming conventions
- [Error Handling Patterns](references/error-handling-patterns.md) — Common errors
