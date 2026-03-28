# Step 7: Fetch & Enhance Cover Art

## Objective

Find the original song's cover art via Google Images, download it, and enhance it to
1080p using the SeedVR2 upscaler on fal.ai. The enhanced image is used as a background
asset in the Remotion video (Step 8).

## Key Requirements

- **Native script search**: Use the song title from `meta.json` (may be in Telugu/Hindi/Tamil)
- **Cover art quality**: Prefer official album/single artwork; avoid fan art or YouTube thumbnails
- **Upscale target**: 1080p via SeedVR2 (`fal-ai/seedvr/upscale/image`)
- **Output format**: JPEG saved to workspace

## Prerequisites

- `workspaces/<slug>/meta.json` exists with `songTitle`, `language`, `slug`

---

## Instructions

### 7.1 — Read Workspace Files

Read `meta.json` and extract: `songTitle`, `language`, `slug`.

---

### 7.2 — Search Google Images for Cover Art

Use Chrome DevTools MCP to navigate to Google Images and search for the cover art:

1. Navigate to `https://images.google.com`
2. Search query: `<songTitle> song cover art` (use the original language title)
   - Example: `మీసాల పిల్ల song cover art`
   - If no results, try the romanized title + `Telugu song cover art`
3. Look for official artwork — square or portrait format, typically from music streaming
   platforms (Spotify, Apple Music, Gaana, JioSaavn)
4. Avoid: YouTube thumbnails, fan-made posters, screenshots

---

### 7.3 — Download the Cover Art Image

Once you identify a suitable image:

1. Right-click or inspect to get the full-resolution image URL
2. Download it to the workspace:

```bash
curl -L "<image-url>" -o "workspaces/<slug>/<slug>-cover-art-raw.jpg"
```

3. Verify the file exists and is non-zero:

```bash
ls -lh "workspaces/<slug>/<slug>-cover-art-raw.jpg"
```

---

### 7.4 — Upload to fal.ai and Enhance with SeedVR2

Use the fal.ai MCP to upload the raw image and run SeedVR2 upscaling:

1. **Upload the image** to fal.ai CDN using the `upload_file` MCP tool:
   - Read the file and base64-encode it
   - Pass via `data` parameter with `file_name: "<slug>-cover-art-raw.jpg"`
   - Note the returned fal.ai CDN URL

2. **Run SeedVR2** using the `run_model` MCP tool:
   - Endpoint: `fal-ai/seedvr/upscale/image`
   - Parameters:
     ```json
     {
       "image_url": "<fal-cdn-url>",
       "upscale_mode": "target",
       "target_resolution": "1080p",
       "output_format": "jpg",
       "noise_scale": 0.1
     }
     ```

3. **Download the enhanced image** from the returned URL:

```bash
curl -L "<output-image-url>" -o "workspaces/<slug>/<slug>-cover-art.jpg"
```

4. Clean up the raw file:

```bash
rm "workspaces/<slug>/<slug>-cover-art-raw.jpg"
```

---

### 7.5 — Verify Output

```bash
ls -lh "workspaces/<slug>/<slug>-cover-art.jpg"
```

The enhanced file should be noticeably larger than the raw input (SeedVR2 upscales to 1080p).

---

### 7.6 — Update Metadata

Update `workspaces/<slug>/meta.json`:

```json
{
  "status": { "cover_art_fetched": true },
  "outputs": {
    "cover_art": "workspaces/<slug>/<slug>-cover-art.jpg"
  }
}
```

---

### 7.7 — Confirm Ready for Video

```
Cover art ready!

   <slug>-cover-art.jpg   — Enhanced to 1080p via SeedVR2

Proceeding to Step 8: Generate Video with Remotion.
```

---

## Fallback: No Cover Art Found

If no suitable cover art can be found on Google Images:

1. Try alternative searches:
   - `<songTitle> album art site:open.spotify.com`
   - `<songTitle> <artist> cover`
2. If still nothing suitable, skip this step and note it in meta.json:
   ```json
   { "status": { "cover_art_fetched": false }, "cover_art_skipped": true }
   ```
3. The Remotion video will render without a background image (falls back to the
   design.json color palette).

---

## Error Handling

| Problem | Fix |
|---|---|
| Google Images blocks bot | Use Chrome DevTools MCP (real browser) — screenshots if needed |
| Image URL requires auth | Find a different result; prefer CDN-hosted images |
| fal.ai upload fails | Ensure file is valid JPEG/PNG; check file size < 20MB |
| SeedVR2 returns error | Try `upscale_mode: "factor"` with `upscale_factor: 2` instead |
| curl download fails | Try `wget` or inspect redirect chain manually |
