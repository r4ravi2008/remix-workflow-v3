# Step 1: Download MP3 from YouTube

## Objective

Download the YouTube video as an MP3 file directly into the workspace using yt-dlp.

## Prerequisites

- `workspaces/<slug>/` directory exists (created in Step 0)
- `workspaces/<slug>/meta.json` exists with `youtube_url` and `slug`
- `uv`/`uvx` available for running yt-dlp

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
  -o "workspaces/$SLUG/${SLUG}-original.%(ext)s" \
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
ls -lh "workspaces/$SLUG/${SLUG}-original.mp3"
```

Expected output: file exists with size > 1MB.

---

### 1.3 — Update meta.json Status

**Write tool:**

Update `workspaces/<slug>/meta.json` to mark this step complete:

```json
"status": {
  "mp3_downloaded": true,
  "acapella_extracted": false,
  "lyrics_saved": false,
  "suno_lyrics_generated": false,
  "remix_uploaded": false,
  "suno_remix_url": null
}
```

---

### 1.4 — Confirm File Ready

Print a summary before proceeding:

```
MP3 downloaded: workspaces/<slug>/<slug>-original.mp3
File size: <size>

Proceeding to Step 2: Extract Acapella...
```

---

## File Outputs

| File | Path |
|---|---|
| Downloaded MP3 | `workspaces/<slug>/<slug>-original.mp3` |
| Updated metadata | `workspaces/<slug>/meta.json` |

---

## Error Handling

- **Download fails with 403/401:** The video may be age-restricted or require authentication. Try adding `--cookies-from-browser chrome` or `--cookies-from-browser safari` to use browser cookies.
- **No audio formats available:** Some videos don't have separate audio streams. Try removing `-x` to download the video with audio embedded.
- **uvx not found:** Install uv first: `brew install uv`
- **Conversion fails:** Ensure the YouTube URL is valid and publicly accessible. Try visiting the URL directly in a browser.
- **File is 0 bytes:** Check disk space and permissions on the workspaces directory.
