# Step 5: Generate & Download Remix from Suno.ai

## Objective

Navigate to Suno.ai using Chrome DevTools MCP, upload the extracted acapella, paste the Suno meta-tag lyrics and style, generate the remix (Suno creates 2 variations), then **download both audio files** to the workspace.

## Prerequisites

- `workspaces/<slug>/<slug>-acapella.mp3` exists (from Step 2)
- `workspaces/<slug>/<slug>-suno-lyrics.txt` exists (from Step 4)
- `workspaces/<slug>/<slug>-suno-style.txt` exists (from Step 4)
- `workspaces/<slug>/meta.json` exists with `genre`, `slug`
- Logged into Suno.ai (https://suno.com)

---

## Pre-Upload: Copyright Detection Pitch Shift

Suno.ai may detect that an uploaded acapella matches an existing copyrighted work and block or flag the generation. If this happens, pitch-shift the acapella down by **2 semitones** before re-uploading.

**When to apply:** If Suno rejects the upload or returns an error indicating the audio matches an existing work.

**Command:**

```bash
SLUG="<slug>"
ffmpeg -i "workspaces/$SLUG/${SLUG}-acapella.mp3" \
  -af "rubberband=pitch=0.8909" \
  -codec:a libmp3lame -b:a 192k \
  "workspaces/$SLUG/${SLUG}-acapella-pitched.mp3" -y
```

**Options explained:**
- `rubberband=pitch=0.8909` — shifts pitch down exactly 2 semitones (`2^(-2/12) ≈ 0.8909`) while preserving the original tempo
- `-codec:a libmp3lame -b:a 192k` — re-encodes to MP3 at 192kbps

**Then upload** `workspaces/<slug>/<slug>-acapella-pitched.mp3` instead of the original acapella in step 5.4.

---

## Instructions

### 5.1 — Create a New Suno Workspace

**This must be done BEFORE navigating to the create page or uploading anything.**

**Chrome DevTools MCP tool:** `navigate_page`

Navigate to the Suno workspaces page:

```
URL: https://suno.com/workspaces
```

**Chrome DevTools MCP tool:** `take_snapshot`

Look for a **"New Workspace"** or **"Create Workspace"** button. Click it:

```
Element: button labeled "New Workspace" or "Create Workspace"
```

**Chrome DevTools MCP tool:** `fill`

Enter the slug as the workspace name:

```
Element: text input for workspace name
Value: <slug> (e.g., "adi-enti-okkasari-dark-deep-house")
```

**Chrome DevTools MCP tool:** `click`

Click the confirm/create button:

```
Element: button labeled "Create" or "Save"
```

**Chrome DevTools MCP tool:** `take_snapshot`

Verify the new workspace appears in the list with the slug name before proceeding.

---

### 5.2 — Navigate to Suno Create Page

**Chrome DevTools MCP tool:** `navigate_page`

Navigate to the Suno creation page:

```
URL: https://suno.com/create
```

Take a snapshot to confirm the page loaded:
```
Tool: take_snapshot
```

Verify these elements are present on the page:
- "Simple" / "Advanced" mode toggle buttons
- "Add audio" button (for uploading acapella)
- Lyrics text area
- Styles text area
- "Create song" button

---

### 5.3 — Switch to Advanced Mode

**Chrome DevTools MCP tool:** `click`

Click the "Advanced" button to enable the full creation form with separate lyrics and style fields:

```
Element: button labeled "Advanced"
```

Take a snapshot to confirm Advanced mode is active with expanded fields:
```
Tool: take_snapshot
```

---

### 5.4 — Select the Workspace Created in Step 5.1

**Chrome DevTools MCP tool:** `click`

Click the workspace dropdown (labeled "Open workspace dropdown" or "Save to...") in the create form:

```
Element: button labeled "Open workspace dropdown"
```

Select the workspace you created in step 5.1 (named after the slug):

```
Element: list item matching "<slug>" (e.g., "adi-enti-okkasari-dark-deep-house")
```

**Chrome DevTools MCP tool:** `take_snapshot`

Verify the dropdown now shows the slug name as the selected workspace before continuing.

---

### 5.5 — Upload the Acapella Audio to the Workspace

**Chrome DevTools MCP tool:** `click`

Click the "Add audio" button to open the audio upload options:

```
Element: button labeled "Add audio - Remix, upload, or record audio"
```

A dropdown or dialog will appear with options: Remix, Upload, Record.

**Chrome DevTools MCP tool:** `click`

Click the "Sample" or "Upload" option (whichever allows local file upload):

```
Element: button labeled "Sample" or "Upload"
```

**Chrome DevTools MCP tool:** `upload_file`

When the file chooser dialog appears, upload the acapella:

```
Element: file input element that appears after clicking Upload
File path: workspaces/<slug>/<slug>-acapella.mp3
```

Take a snapshot after uploading to confirm the audio waveform or file name appears in the audio section:
```
Tool: take_snapshot
```

**If the uploaded acapella does NOT appear immediately in the audio section**, follow these steps to locate it:

**Chrome DevTools MCP tool:** `click`

Click the "Remix" button (usually near the top or in the creation interface):

```
Element: button labeled "Remix"
```

**Chrome DevTools MCP tool:** `click`

Click the "Library" tab to view your uploaded audio files:

```
Element: tab or button labeled "Library"
```

**Chrome DevTools MCP tool:** `wait_for` then `take_snapshot`

Wait for the library to load and look for the recently uploaded acapella file. The file should appear in the library list with the filename or a waveform preview:

```
Tool: wait_for
Text to watch for: ["<slug>-acapella" or waveform preview or "Library"]
Timeout: 30000 (30 seconds)
```

Once the file appears in the library, click on it to select it for remixing:

```
Tool: click
Element: library item containing "<slug>-acapella" or the uploaded acapella file
```

The selected acapella should now appear in the audio section of the creation interface.

**IMPORTANT:** Ensure the file was uploaded to the workspace you created in Step 5.1. The file should be associated with your slug-named workspace.

---

### 5.6 — Set the Audio Influence Mode

**Chrome DevTools MCP tool:** `click`

After uploading, Suno will show mode options for how the audio influences the generation. Select "Cover" mode to use the acapella as a vocal reference:

```
Element: button labeled "Cover" (or "Change condition type from Cover")
```

Optionally adjust the "Audio Influence" slider if visible. A value between 70–85% works well for preserving vocal character.

---

### 5.7 — Paste the Suno Meta-Tag Lyrics

**Chrome DevTools MCP tool:** `click` then `fill`

Read the content of `workspaces/<slug>/<slug>-suno-lyrics.txt` first.

Click on the lyrics text area to focus it:
```
Element: textbox with placeholder "Write some lyrics or a prompt — or leave blank for instrumental"
```

Clear any existing content, then fill with the full contents of `<slug>-suno-lyrics.txt`:

```
Tool: fill
Element: lyrics textbox
Value: <full contents of workspaces/<slug>/<slug>-suno-lyrics.txt>
```

Take a snapshot to confirm the lyrics are entered correctly:
```
Tool: take_snapshot
```

---

### 5.8 — Paste the Style Description

**Chrome DevTools MCP tool:** `click` then `fill`

Read the content of `workspaces/<slug>/<slug>-suno-style.txt`.

Click the Styles text area to focus it:
```
Element: textbox with placeholder text related to styles (multiline, near the style suggestions)
```

Clear any existing styles, then fill with the contents of `<slug>-suno-style.txt`:

```
Tool: fill
Element: styles textbox
Value: <full contents of workspaces/<slug>/<slug>-suno-style.txt>
```

**Important:** The style field has a 1000-character limit. Confirm the character counter below the field stays within limit. If it exceeds, trim the style block.

Take a snapshot to check:
```
Tool: take_snapshot
```

---

### 5.9 — Set the Song Title

**Chrome DevTools MCP tool:** `fill`

Fill in the Song Title field with the workspace slug for easy identification:

```
Element: textbox labeled "Song Title (Optional)"
Value: <slug> (e.g., "meesaala-pilla-lofi")
```

---

### 5.10 — Review Before Submitting

Take a final snapshot to review all fields before clicking Create:

```
Tool: take_snapshot
```

Confirm:
- Audio section shows the uploaded acapella file
- Lyrics text area contains the full Suno meta-tag formatted lyrics in Indic script
- Style field contains the genre/style block
- Song title is set to the workspace slug
- Character count on style is within 1000

---

### 5.11 — Submit the Creation

**Chrome DevTools MCP tool:** `click`

Click the "Create song" button:

```
Element: button labeled "Create song"
```

Take a snapshot immediately after clicking:
```
Tool: take_snapshot
```

---

### 5.12 — Wait for Song Generation

**Chrome DevTools MCP tool:** `wait_for`

Suno.ai will generate 2 song variations. Watch for the generated songs to appear:

```
Tool: wait_for
Text to watch for: ["Play", "Download", "Like", "Share", "Publish", slug title]
Timeout: 300000 (5 minutes)
```

---

### 5.13 — Get Song IDs from Generated Song Pages

Once generation is complete, Suno shows 2 song cards. Click each song title to open its detail page and capture the song ID from the URL.

**Chrome DevTools MCP tool:** `click`

Click the title of the first generated song to navigate to its detail page:

```
Element: song title or card for Variation 1
```

**Chrome DevTools MCP tool:** `evaluate_script`

Extract the song ID from the URL:

```javascript
() => window.location.href
```

The URL will be in the form `https://suno.com/song/<song-id>`. Extract the `<song-id>` portion (a UUID like `00084c0d-5978-4377-aebc-36a349cf0a7a`).

Repeat for Variation 2.

---

### 5.14 — Download Songs Directly from Suno CDN

The Suno CDN serves MP3 files at a predictable URL from the song ID. Download both variations with curl:

```bash
SLUG="<slug>"
SONG_ID_V1="<song-id-1>"
SONG_ID_V2="<song-id-2>"

curl -L "https://cdn1.suno.ai/${SONG_ID_V1}.mp3" \
  -o "workspaces/${SLUG}/${SLUG}-remix-v1.mp3"

curl -L "https://cdn1.suno.ai/${SONG_ID_V2}.mp3" \
  -o "workspaces/${SLUG}/${SLUG}-remix-v2.mp3"
```

**Verify both files downloaded correctly:**

```bash
ls -lh workspaces/<slug>/<slug>-remix-*.mp3
```

Expected: each file is 4–10MB for a typical 3–4 minute song.

---

### 5.15 — Verify Downloads

**Bash tool:**

```bash
ls -lh workspaces/<slug>/<slug>-remix-*.mp3
```

---

### 5.16 — Save Metadata

**Write tool** (filesystem):

Update `workspaces/<slug>/meta.json`:

```json
{
  "status": {
    "mp3_downloaded": true,
    "acapella_extracted": true,
    "lyrics_saved": true,
    "suno_lyrics_generated": true,
    "remix_uploaded": true,
    "remix_v1_downloaded": true,
    "remix_v2_downloaded": true,
    "suno_remix_url_v1": "https://suno.com/song/<song-id-1>",
    "suno_remix_url_v2": "https://suno.com/song/<song-id-2>",
    "suno_cdn_v1": "https://cdn1.suno.ai/<song-id-1>.mp3",
    "suno_cdn_v2": "https://cdn1.suno.ai/<song-id-2>.mp3"
  }
}
```

---

### 5.17 — Present Options to User

Print the results and ask user to select which version to use:

```
Remix generation complete! Two variations created:

📁 Files downloaded to workspace:
   workspaces/<slug>/<slug>-remix-v1.mp3
   workspaces/<slug>/<slug>-remix-v2.mp3

🔗 Suno song pages:
   Song 1: https://suno.com/song/<id-1>
   Song 2: https://suno.com/song/<id-2>

🎵 Listen to both files and tell me which version to use for the video:
   - Reply "v1" to use <slug>-remix-v1.mp3
   - Reply "v2" to use <slug>-remix-v2.mp3

Once you select, I'll proceed to Step 6: Extract Acapella & Align Lyrics.
```

---

## File Outputs

| File | Path |
|---|---|
| Remix Variation 1 | `workspaces/<slug>/<slug>-remix-v1.mp3` |
| Remix Variation 2 | `workspaces/<slug>/<slug>-remix-v2.mp3` |
| Updated metadata | `workspaces/<slug>/meta.json` |

---

## Next Step

After user selects v1 or v2, proceed to **Step 6: Extract Acapella & Align Lyrics**.
