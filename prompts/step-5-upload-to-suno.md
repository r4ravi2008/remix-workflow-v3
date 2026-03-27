# Step 5: Upload Acapella & Generate Remix on Suno.ai

## Objective

Navigate to Suno.ai using Chrome DevTools MCP, upload the extracted acapella, paste the Suno meta-tag lyrics and style, then submit to generate the remix. Save the resulting song URL back to the workspace.

## Prerequisites

- `workspaces/<slug>/<slug>-acapella.mp3` exists (from Step 2)
- `workspaces/<slug>/<slug>-suno-lyrics.txt` exists (from Step 4)
- `workspaces/<slug>/<slug>-suno-style.txt` exists (from Step 4)
- `workspaces/<slug>/meta.json` exists with `genre`, `slug`
- Logged into Suno.ai (https://suno.com)

---

## Instructions

### 5.1 — Navigate to Suno Create Page

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

### 5.2 — Switch to Advanced Mode

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

### 5.3 — Create or Select Suno Workspace

**Chrome DevTools MCP tool:** `click`

Before uploading, ensure you're working in the correct workspace. Look for a workspace selector (usually near the top-left or in the navigation bar). If no workspace is selected or you need to create a new one:

Click the workspace dropdown or "New Workspace" button:

```
Element: button labeled "New Workspace" or workspace dropdown
```

**If creating a new workspace:**

**Chrome DevTools MCP tool:** `fill` then `click`

Enter the slug name as the workspace name:

```
Element: text input for workspace name
Value: <slug> (e.g., "meesaala-pilla-lofi")
```

Click the "Create" or "Create Workspace" button to confirm.

**Chrome DevTools MCP tool:** `take_snapshot`

Verify the workspace name (slug) is displayed in the interface, indicating you're now working in the correct workspace.

---

### 5.4 — Upload the Acapella Audio to the Workspace

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

**IMPORTANT:** Ensure the file was uploaded to the workspace you created in Step 5.3. The file should be associated with your slug-named workspace.

---

### 5.5 — Set the Audio Influence Mode

**Chrome DevTools MCP tool:** `click`

After uploading, Suno will show mode options for how the audio influences the generation. Select "Cover" mode to use the acapella as a vocal reference:

```
Element: button labeled "Cover" (or "Change condition type from Cover")
```

Optionally adjust the "Audio Influence" slider if visible. A value between 70–85% works well for preserving vocal character.

---

### 5.6 — Paste the Suno Meta-Tag Lyrics

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

### 5.7 — Paste the Style Description

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

### 5.8 — Set the Song Title

**Chrome DevTools MCP tool:** `fill`

Fill in the Song Title field with the workspace slug for easy identification:

```
Element: textbox labeled "Song Title (Optional)"
Value: <slug> (e.g., "meesaala-pilla-lofi")
```

---

### 5.9 — Review Before Submitting

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

### 5.10 — Select the Workspace Before Submitting

**Chrome DevTools MCP tool:** `click` then `take_snapshot`

Before clicking "Create song", verify and select the correct workspace. Look for a workspace selector dropdown near the creation button or in the interface header:

```
Tool: click
Element: workspace dropdown or selector showing current workspace name
```

If a dropdown appears, select the workspace named after your slug:

```
Tool: click
Element: dropdown option containing "<slug>"
```

Take a snapshot to confirm the correct workspace is selected:
```
Tool: take_snapshot
```

**Verify:** The workspace selector should display your slug name (e.g., "meesaala-pilla-lofi"), ensuring the remix will be saved to the correct workspace.

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

Suno.ai will generate 2 song variations. Watch for the generated songs to appear in the right-hand panel:

```
Tool: wait_for
Text to watch for: ["Play", "Like", "Share", "Publish", slug title]
Timeout: 300000 (5 minutes)
```

Periodically take a snapshot to check generation progress:
```
Tool: take_snapshot
```

Generation states:
- Queued: Spinner visible, no audio yet
- Generating: Progress indicator on song cards
- Complete: Play button active on generated song cards

---

### 5.13 — Retrieve the Remix URLs

**Chrome DevTools MCP tool:** `take_snapshot`

Once generated, the song cards appear in the right panel. Each card has a link to the song's page.

Read the snapshot and find the song URLs. They follow the pattern:
```
https://suno.com/song/<song-id>
```

Click on the first generated song to open it:
```
Tool: click
Element: link with the song title (slug name)
```

Copy the URL from the browser. You can also use:
```
Tool: evaluate_script
Function: () => window.location.href
```

---

### 5.14 — Save Remix URLs to Workspace

**Write tool** (filesystem):

Update `workspaces/<slug>/meta.json` with the generated song URLs and mark the step complete:

```json
"status": {
  "mp3_downloaded": true,
  "acapella_extracted": true,
  "lyrics_saved": true,
  "suno_lyrics_generated": true,
  "remix_uploaded": true,
  "suno_remix_url": "https://suno.com/song/<song-id-1>",
  "suno_remix_url_2": "https://suno.com/song/<song-id-2>"
}
```

---

### 5.15 — Share Results with User

Print the final summary:

```
Remix generated successfully!

Song 1: https://suno.com/song/<id-1>
Song 2: https://suno.com/song/<id-2>

Workspace: workspaces/<slug>/
  original.mp3     — Downloaded YouTube audio
  <slug>-acapella.mp3     — Extracted vocals
  <slug>-lyrics.txt       — Original Indic lyrics
  <slug>-suno-lyrics.txt  — Suno meta-tag formatted lyrics
  <slug>-suno-style.txt   — Style block used
  meta.json        — Session metadata and status
```

---

## File Outputs

| File | Path / Value |
|---|---|
| Updated metadata with remix URLs | `workspaces/<slug>/meta.json` |
| Remix Song 1 | `https://suno.com/song/<id>` |
| Remix Song 2 | `https://suno.com/song/<id>` |

---

## Error Handling

- **Audio upload not accepted:** Confirm the `<slug>-acapella.mp3` file is a valid MP3. Try converting to WAV if MP3 fails.
- **Style field over 1000 characters:** Trim to core descriptors: `[<genre>, <mood>, <language>, <vocal type>]` and remove instrument/influence details.
- **Lyrics not rendering in Indic script in Suno:** This is a display issue only — Suno still processes Unicode correctly. Proceed.
- **Generation fails or times out:** Retry by clicking "Create song" again. Suno credits are deducted per generation attempt — confirm with user before retrying.
- **Songs generated but don't match the style:** Try adjusting the Audio Influence slider (lower = less influence from acapella, more from style prompt) and regenerate.
- **Login session expired:** Navigate to `https://suno.com` and log in before retrying from Step 5.1.

---

## Pipeline Complete

All steps are done. The workspace at `workspaces/<slug>/` contains all artifacts from this remix session. Share the Suno song links with the user.
