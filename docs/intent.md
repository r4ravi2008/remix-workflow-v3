# Project Intent: Indic Song Remixer

## Overview

This project automates the end-to-end process of remixing Telugu and other Indic language songs using AI tools. The user provides a YouTube video link and a target genre or style, and the system produces remix candidates through Suno.ai via Chrome DevTools MCP or local ACE-Step generation.

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
[Step 5] Generate Remix Candidates  →  Suno or local ACE-Step creates 2 variations
        |
        v
[Step 5.5] Select Remix Version  →  User chooses v1 or v2
        |
        v
[Step 6] Extract Acapella & Align Lyrics  →  lyrics-timestamps.json
        |
        v
[Step 7] Fetch & Enhance Cover Art  →  <slug>-cover-art.jpg (SeedVR2 1080p)
        |
        v
[Step 8] Generate Video with Remotion  →  Final music video
        |
        v
[Step 9] Generate YouTube Metadata
        |
        v
[Step 10] Select Short Clip  →  shorts-segments.json
        |
        v
[Step 11] Generate Short Video  →  <slug>-short.mp4 (1080x1920 vertical)
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
    <slug>-suno-style.txt    # Style block for Suno (Step 4)
    <slug>-remix-v1.mp3      # Remix variation 1 (Step 5)
    <slug>-remix-v2.mp3      # Remix variation 2 (Step 5)
    <slug>-remix-v1-acapella.mp3  # Vocals from remix, for alignment (Step 6)
    lyrics-timestamps.json    # CTC-aligned word/line timestamps (Step 6)
    <slug>-cover-art.jpg     # Enhanced cover art via SeedVR2 (Step 7)
    <slug>-video.mp4         # Final music video (Step 8)
    <slug>-short.mp4         # Rendered vertical short video (Step 11)
    shorts-segments.json     # Clip segment analysis (Step 10)
    video/                   # Remotion project files (Step 8)
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

- Use `uvx yt-dlp` to download audio directly from the YouTube URL
- Extract audio only (`-x`), convert to MP3 at best quality (`--audio-quality 0`)
- Save directly to `workspaces/<slug>/<slug>-original.mp3`

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

- Read `workspaces/<slug>/<slug>-lyrics.txt`
- Convert the lyrics into Suno.ai's metatag format using the genre/style from `meta.json`
- Structure includes metatags such as:
  - `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]`, etc.
  - Style-specific or mood tags as applicable
- Preserve Indic script exactly — do not transliterate or translate
- Ask clarifying questions if needed before generating (tempo, length, mood)
- Save the result to `workspaces/<slug>/<slug>-suno-lyrics.txt`

---

### Step 5: Generate Remix Candidates

- Use either Suno.ai through Chrome DevTools MCP or local ACE-Step generation
- For Suno, upload `workspaces/<slug>/<slug>-acapella.mp3`, paste `workspaces/<slug>/<slug>-suno-lyrics.txt`, fill the Style field, and generate 2 variations
- For ACE-Step, run the local generation tool against the same workspace inputs
- Save both variations as `<slug>-remix-v1.mp3` and `<slug>-remix-v2.mp3`
- Save backend metadata to `meta.json`

### Step 5.5: Select Remix Version

- User listens to both variations (v1 and v2)
- User selects which version to use for video generation
- Selection stored in `meta.json.status.selected_remix` for Step 6

### Step 6: Extract Acapella & Align Lyrics

- Extract vocals from the selected remix using the Mel-Band RoFormer acapella extractor
- Run CTC forced alignment against the formatted lyrics to produce word- and line-level timestamps
- Verify alignment quality via terminal karaoke preview (±500ms first line, <3s end drift)
- Save `lyrics-timestamps.json` and update `meta.json` with `acapella_aligned: true`

### Step 7: Fetch & Enhance Cover Art

- Search Google Images for the song's official cover art using Chrome DevTools MCP
- Download the best result to `<slug>-cover-art-raw.jpg`
- Upload to fal.ai and upscale to 1080p using SeedVR2 (`fal-ai/seedvr/upscale/image`)
- Save enhanced image as `<slug>-cover-art.jpg` and update `meta.json`

### Step 8: Generate Video with Remotion

- Generate visual design configuration (`design.json`) from song metadata
- Scaffold Remotion project using `tools/video-generator/init-video.js`
- Copy audio, lyrics timestamps, cover art, and design config into the video project
- Render final video to `<slug>-video.mp4`
- Update `meta.json` with video generation status

### Step 9: Generate YouTube Metadata

- Generate title, description, tags, and thumbnail text optimized for YouTube
- Save metadata to `youtube-metadata.json`
- Create human-readable `youtube-metadata-artifact.md` for review
- Update `meta.json` with generation status

### Step 10: Select Short Clip

- Analyze lyrics-timestamps.json sections (Chorus, Verse, Bridge) and FFmpeg EBU R128 loudness
- Score candidate segments: Chorus +10, Verse +5, Bridge +3, plus energy bonus 0-5
- Auto-select highest-scoring segment (default) or present candidates if user opted into manual mode
- Save analysis to `shorts-segments.json` and merge clip config into `video-config.json`

### Step 11: Generate Short Video

- Render 9:16 vertical video using existing Remotion project's `MusicVideoShort` composition
- Audio trimmed via Remotion's native `trimBefore`/`trimAfter`
- Lyrics filtered and rebased to clip window (timestamps start at 0)
- Uses `CoverArtVerticalLayout`: cover art top 60%, lyrics middle 30%, visualizer bottom 10%
- Same design.json palette, motifs, and audio-reactive effects as full video
- Save as `<slug>-short.mp4`

---

## Key Constraints

- All browser interactions must use Chrome DevTools MCP; local ACE-Step generation does not require browser automation
- All files for a remix must be stored inside `workspaces/<slug>/` — nothing outside it
- Lyrics must remain in native Indic script (Telugu, Hindi, Tamil, etc.) — no romanization
- Only free-tier features of Suno.ai should be used when using the Suno backend unless otherwise specified
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
- `step-1-download-mp3.md` — Download MP3 from YouTube via yt-dlp, save to workspace
- `step-2-extract-acapella.md` — Extract acapella using Mel-Band RoFormer (UV tool), save to workspace
- `step-3-find-lyrics.md` — Find and save Indic language lyrics to workspace
- `step-4-generate-suno-lyrics.md` — Convert lyrics to Suno meta-tag format, save to workspace
- `step-5-upload-to-suno.md` — Generate and download both remix variations from Suno.ai
- `step-5-generate-with-ace-step.md` — Generate both remix variations with local ACE-Step
- `step-6-extract-acapella-and-align.md` — Extract remix acapella and generate CTC-aligned lyrics timestamps
- `step-7-fetch-cover-art.md` — Fetch song cover art via Google Images and enhance to 1080p with SeedVR2
- `step-8-generate-video.md` — Scaffold Remotion project and render final music video
- `step-10-select-short-clip.md` — Analyze audio and lyrics to select best short clip segment
- `step-11-generate-short-video.md` — Render 9:16 vertical short video using Remotion
