# Step 7: Fetch & Stylize Cover Art

## Objective

Find the original song's cover art from JioSaavn (preferred) or Google Images, then
stylize it into Japanese anime style using the Nano Banana Pro model on fal.ai. The
stylized image is used as the background asset in the Remotion video (Step 8).

## Key Requirements

- **Source**: JioSaavn CDN (preferred) or Google Images — official album/single artwork only
- **Stylization**: Japanese anime style via `fal-ai/nano-banana-pro/edit` at 2K resolution
- **Text on image**: Song title only — no watermarks, logos, artist names, or other text
- **Output format**: JPEG saved as `workspaces/<slug>/<slug>-cover-art.jpg`

## Prerequisites

- `workspaces/<slug>/meta.json` exists with `video_title`, `language`, `slug`

**See also**: [Chrome DevTools Patterns](references/chrome-devtools-patterns.md) — Browser automation reference.

---

## Instructions

### 7.1 — Read Workspace Files

Read `meta.json` and extract: `video_title`, `language`, `slug`.

---

### 7.2 — Get Cover Art from JioSaavn (Preferred)

**See**: [Chrome DevTools Patterns](references/chrome-devtools-patterns.md)

JioSaavn CDN hosts high-quality cover art for Indian film songs.

**Steps:**
1. Navigate to `https://www.jiosaavn.com`
2. Search for: `<song name> <movie name>`
3. Open the song page
4. Extract the OG image URL:

```javascript
() => document.querySelector('meta[property="og:image"]')?.content
```

This returns the direct CDN URL. Use it as the source image.

**If JioSaavn doesn't have the song**, fall back to Google Images (step 7.3).

---

### 7.3 — Fallback: Find Cover Art via Google Images

**See**: [Chrome DevTools Patterns](references/chrome-devtools-patterns.md)

If JioSaavn doesn't have the song:

1. Navigate to `https://images.google.com`
2. Search: `<movie name> <song name> album cover site:saavn.com OR site:gaana.com`
3. Look for official artwork from streaming platforms
4. Avoid: YouTube thumbnails, fan edits, screenshots

Right-click the best result to get the full-resolution image URL.

---

### 7.4 — Upload Cover Art to fal.ai CDN

Use the fal.ai MCP `upload_file` tool to upload the image by URL:

```
Tool: upload_file
url: <jiosaavn-or-image-url>
```

Note the returned fal.ai CDN URL — this is `<fal-cdn-url>`.

---

### 7.5 — Stylize with Nano Banana Pro

Use the fal.ai MCP `run_model` tool to stylize the cover art:

```
Tool: run_model
endpoint_id: fal-ai/nano-banana-pro/edit
input:
  image_urls: ["<fal-cdn-url>"]
  resolution: "2K"
  aspect_ratio: "1:1"
  prompt: "Japanese anime style illustration, vibrant colors, cinematic lighting, include only the text '<songTitle>' in stylized anime lettering, no other text, no watermarks, no logos"
```

The model returns a 2048×2048 stylized image URL.

---

### 7.6 — Download the Stylized Image

```bash
curl -L "<output-image-url>" -o "workspaces/<slug>/<slug>-cover-art.jpg"
```

Verify:

```bash
ls -lh "workspaces/<slug>/<slug>-cover-art.jpg"
```

Expected: 500KB–2MB, 2048×2048px.

---

### 7.7 — Update Metadata

Update `workspaces/<slug>/meta.json`:

```json
{
  "status": { "cover_art_fetched": true },
  "files": {
    "cover_art": "workspaces/<slug>/<slug>-cover-art.jpg"
  }
}
```

---

### 7.8 — Confirm Ready for Video

```
Cover art ready!

   <slug>-cover-art.jpg   — Anime-stylized via Nano Banana Pro (2048×2048)

Proceeding to Step 8: Generate Video with Remotion.
```

---

## Fallback: No Cover Art Found

If no suitable source image can be found:

1. Try alternative searches: `<songTitle> <artist> cover site:open.spotify.com`
2. If still nothing, skip this step and note it in meta.json:
   ```json
   { "status": { "cover_art_fetched": false }, "cover_art_skipped": true }
   ```
3. The Remotion video falls back to the `design.json` color palette with no image panel.

---

## Error Handling

**See**: [Error Handling Patterns](references/error-handling-patterns.md)

| Problem | Fix |
|---|---|
| JioSaavn search returns no result | Fall back to Google Images (step 7.3) |
| fal.ai upload_file rejects URL | Download image locally with curl, then base64-encode |
| Nano Banana Pro returns unwanted text | Add `"no text, no captions"` to prompt |
| Output image has wrong aspect ratio | Pass `aspect_ratio: "1:1"` explicitly |
| curl download fails | Try `wget -O` as alternative |

---

## Reference

- [Chrome DevTools Patterns](references/chrome-devtools-patterns.md) — Browser automation
- [Workspace Conventions](references/workspace-conventions.md) — File naming
- [Error Handling Patterns](references/error-handling-patterns.md) — Common errors
