# Project Intent: Indic Song Remixer

## Overview

This project automates the end-to-end process of remixing Telugu and other Indic language songs using AI tools. The user provides a YouTube video link and a target genre or style, and the system produces a remixed song on Suno.ai — all orchestrated through Chrome DevTools MCP.

## Target Use Case

Remixing Telugu and other Indic language songs into new styles or genres while preserving the original lyrics in their native script (Telugu, Hindi, Tamil, etc.).

---

## Pipeline Overview

```
YouTube URL + Genre/Style (user input)
        |
        v
[Step 0] Prepare Workspace
        |
        v
[Step 1] Download MP3  →  saved to workspace/
        |
        v
[Step 2] Extract Acapella (Mel-Band RoFormer via UV)  →  saved to workspace/
        |
        v
[Step 3] Find & Download Indic Lyrics  →  saved to workspace/lyrics.txt
        |
        v
[Step 4] Generate Suno Meta-Tag Lyrics  →  saved to workspace/suno-lyrics.txt
        |
        v
[Step 5] Upload & Generate Remix on Suno.ai
```

---

## Detailed Steps

### Step 0: Prepare Workspace

Before any processing begins, create a dedicated workspace folder for this remix session. All files produced during the pipeline are saved here.

**Workspace location:** `workspaces/<slug>/`

**Slug format:** Derived from the YouTube video title — lowercase, spaces replaced with hyphens, special characters removed.
Example: `meesaala-pilla-lofi-remix`

**Workspace structure created at this step:**
```
workspaces/
  <slug>/
    <slug>-meta.json          # Stores session metadata (URL, title, genre, language, timestamps)
    <slug>-original.mp3       # Downloaded from YouTube (Step 1)
    <slug>-acapella.mp3       # Extracted vocals (Step 2)
    <slug>-lyrics.txt         # Raw Indic lyrics (Step 3)
    <slug>-suno-lyrics.txt    # Suno meta-tag formatted lyrics (Step 4)
```

**Actions:**
1. Collect user inputs:
   - YouTube video URL
   - Desired remix genre or style (e.g., "Lo-Fi", "Hip-Hop", "Carnatic Fusion")
   - Language of the song (Telugu, Hindi, Tamil, etc.) — infer from video if obvious
   - Tempo preference (optional): Slow, Medium, Energetic
   - Song length preference (optional): Full song or shortened
2. Derive the slug from the video title (fetch title from YouTube page or URL metadata)
3. Create the workspace directory: `workspaces/<slug>/`
4. Write `meta.json` with all collected inputs and the workspace path

**Example `meta.json`:**
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=F-KfKbCDBIk",
  "video_title": "Meesaala Pilla Full Lyrical | Chiranjeevi | Nayanthara | Bheems Music",
  "slug": "meesaala-pilla-lofi-remix",
  "genre": "Lo-Fi",
  "language": "Telugu",
  "tempo": "slow",
  "song_length": "full",
  "workspace": "workspaces/meesaala-pilla-lofi-remix/",
  "created_at": "<timestamp>"
}
```

---

### Step 1: Download MP3

- Navigate to https://v1.mp3now.com/ using Chrome DevTools MCP
- Paste the YouTube URL into the converter input field
- Click "Convert" and wait for processing to complete
- Click "Download" to save the MP3 file
- Move / rename the downloaded file to `workspaces/<slug>/<slug>-original.mp3`

---

### Step 2: Extract Acapella via Mel-Band RoFormer (UV Tool)

- Run the acapella-extractor UV tool with Mel-Band RoFormer model
- Process `workspaces/<slug>/original.mp3` locally
- Extract vocals-only track using SOTA source separation
- Save as `workspaces/<slug>/acapella.mp3`
- Save it as `workspaces/<slug>/<slug>-acapella.mp3`

---

### Step 3: Find & Save Indic Language Lyrics

- Use the video title from `meta.json` to perform a Google search for lyrics
- Target lyric websites that provide Indic language scripts (not transliteration):
  - Preferred sources: lyricsted.com, lyricsmint.com, or similar Indic lyric sites
- Copy the full lyrics in the native Indic script
- Save to `workspaces/<slug>/<slug>-lyrics.txt`

---

### Step 4: Generate Suno Meta-Tag Lyrics

- Read `workspaces/<slug>/lyrics.txt`
- Convert the lyrics into Suno.ai's metatag format using the genre/style from `meta.json`
- Structure includes metatags such as:
  - `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]`, etc.
  - Style-specific or mood tags as applicable
- Preserve Indic script exactly — do not transliterate or translate
- Ask clarifying questions if needed before generating (tempo, length, mood)
- Save the result to `workspaces/<slug>/<slug>-suno-lyrics.txt`

---

### Step 5: Upload and Generate Remix on Suno.ai

- Navigate to https://suno.com using Chrome DevTools MCP
- Click the "Create" button to open the music creation interface
- Upload `workspaces/<slug>/<slug>-acapella.mp3`
- Paste the contents of `workspaces/<slug>/<slug>-suno-lyrics.txt` into the lyrics field
- Fill in the Style field with the genre/style from `meta.json`
- Submit and wait for Suno.ai to generate the remix
- Retrieve and share the resulting remix link with the user
- Optionally save the Suno remix URL back to `meta.json`

---

## Key Constraints

- All browser interactions must use Chrome DevTools MCP
- All files for a remix must be stored inside `workspaces/<slug>/` — nothing outside it
- Lyrics must remain in native Indic script (Telugu, Hindi, Tamil, etc.) — no romanization
- Only free-tier features of Suno.ai should be used unless otherwise specified
- Each step is sequential; later steps depend on outputs from earlier ones
- The workspace slug must be unique per remix session — append genre suffix to avoid collisions

---

## User Inputs Required

| Input | When Collected | Example |
|---|---|---|
| YouTube video URL | Step 0 | `https://www.youtube.com/watch?v=xyz` |
| Remix genre / style | Step 0 | "Lo-Fi Hip-Hop", "EDM", "Carnatic Fusion" |
| Language | Step 0 (infer if obvious) | Telugu, Hindi, Tamil |
| Tempo preference | Step 0 (optional) | Slow, Medium, Energetic |
| Song length preference | Step 0 (optional) | Full song, shortened |

---

## Prompts Folder

Step-by-step execution prompts for each stage are maintained in `/prompts/`:

- `step-0-prepare-workspace.md` — Collect inputs, create workspace folder, write meta.json
- `step-1-download-mp3.md` — Download MP3 from YouTube via MP3Now, save to workspace
- `step-2-extract-acapella.md` — Extract acapella using Mel-Band RoFormer (UV tool), save to workspace
- `step-3-find-lyrics.md` — Find and save Indic language lyrics to workspace
- `step-4-generate-suno-lyrics.md` — Convert lyrics to Suno meta-tag format, save to workspace
- `step-5-upload-to-suno.md` — Upload acapella and generate remix on Suno.ai
