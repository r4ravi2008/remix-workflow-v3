# Step 0: Prepare Workspace

## Objective

Collect all user inputs for the remix session, create a dedicated workspace folder, and write a `meta.json` file that all subsequent steps will reference.

## Prerequisites

- Access to the local filesystem (Bash tool)
- `.remix-workspace-root.json` exists at the repo root and contains a valid `workspaceRoot`
- The configured `workspaceRoot` directory already exists and is writable

**See also**: [Workspace Conventions](references/workspace-conventions.md) for slug format, meta.json schema, and file naming rules.

---

## Instructions

### 0.1 — Collect User Inputs

Ask the user for the following. If any optional inputs are not provided, use the defaults.

| Input | Required | Default | Example |
|---|---|---|---|
| YouTube video URL | Yes | — | `https://www.youtube.com/watch?v=F-KfKbCDBIk` |
| Remix genre / style | Yes | — | `Lo-Fi`, `EDM`, `Carnatic Fusion`, `Hip-Hop` |
| Language of the song | No | Infer from video title | `Telugu`, `Hindi`, `Tamil` |
| Tempo preference | No | `medium` | `slow`, `medium`, `energetic` |
| Song length preference | No | `full` | `full`, `shortened` |
| Short clip selection | No | `auto` | `auto` (best segment), `manual` (present choices) |
| Short clip duration (seconds) | No | `30` | `15`, `30`, `60` |

Ask all questions upfront in a single prompt to the user before proceeding.

---

### 0.2 — Fetch the Video Title

Use `uvx yt-dlp` to extract the video title from the YouTube URL without downloading:

```bash
uvx yt-dlp --get-title "<youtube_url>"
```

Strip any trailing suffixes like `| Official Video`, `| Full Lyrical`, `| Audio`, etc. if present, keeping the core song/artist title.

**Example:**
- Raw title: `Meesaala Pilla Full Lyrical | Chiranjeevi | Nayanthara | Bheems Music`
- Cleaned title: `Meesaala Pilla`

---

### 0.3 — Generate Workspace Slug

Derive a short, filesystem-safe slug from the video title and genre.

**See**: [Workspace Conventions > Slug Format](references/workspace-conventions.md#slug-format) for detailed rules and examples.

**Quick reference**:
- Take 4–6 meaningful words from title
- Skip filler words ("Full", "Lyrical", "Official")
- Append genre as suffix
- Lowercase, hyphenate, remove special chars

---

### 0.4 — Resolve Workspace Root And Create Workspace Directory

Read `.remix-workspace-root.json` from the repo root and extract `workspaceRoot`.

- If the file is missing: stop and tell the user to copy `.remix-workspace-root.example.json` to `.remix-workspace-root.json`.
- If the JSON is invalid: stop and tell the user to fix the file.
- If the configured root does not exist: stop and tell the user to create that directory first.

Resolve the workspace directory as:

```text
<workspaceRoot>/<slug>/
```

Create that directory and verify it exists.

---

### 0.5 — Write meta.json

Write a `meta.json` file inside the workspace with all collected and derived information.

**See**: [Workspace Conventions > meta.json Schema](references/workspace-conventions.md#metajson-schema) for full schema reference.

**File path:** `<workspaceRoot>/<slug>/meta.json`

**Template:**
```json
{
  "youtube_url": "<youtube_url>",
  "video_title": "<cleaned video title>",
  "slug": "<slug>",
  "genre": "<genre>",
  "language": "<language>",
  "tempo": "<tempo>",
  "song_length": "<song_length>",
  "shorts_clip_mode": "<auto or manual>",
  "shorts_duration": "<duration>",
  "workspace": "<slug>/",
  "files": {
    "original_mp3": "<slug>/<slug>-original.mp3",
    "acapella": "<slug>/<slug>-acapella.mp3",
    "lyrics": "<slug>/<slug>-lyrics.txt",
    "suno_lyrics": "<slug>/<slug>-suno-lyrics.txt",
    "suno_style": "<slug>/<slug>-suno-style.txt",
    "design": "<slug>/design.json",
    "remix_acapella": null,
    "lyrics_timestamps": null,
    "cover_art": null,
    "final_video": null,
    "shorts_segments": null,
    "short_video": null
  },
  "status": {
    "mp3_downloaded": false,
    "acapella_extracted": false,
    "lyrics_saved": false,
    "suno_lyrics_generated": false,
    "remix_uploaded": false,
    "remix_v1_downloaded": false,
    "remix_v2_downloaded": false,
    "acapella_aligned": false,
    "cover_art_fetched": false,
    "video_generated": false,
    "shorts_clip_selected": false,
    "short_video_generated": false,
    "youtube_metadata_generated": false,
    "suno_remix_url_v1": null,
    "suno_remix_url_v2": null,
    "suno_cdn_v1": null,
    "suno_cdn_v2": null,
    "selected_remix": null,
    "lyrics_source_url": null,
    "cover_art_skipped": false
  },
  "created_at": "<ISO timestamp>"
}
```

---

### 0.6 — Confirm Workspace Ready

Print a summary to the user before proceeding:

```
Workspace ready: <workspaceRoot>/<slug>/
  Video        : <video_title>
  Genre        : <genre>
  Language     : <language>
  Tempo        : <tempo>
  Length       : <song_length>
  Shorts Mode  : <shorts_clip_mode>
  Shorts Dur   : <shorts_duration>s

Proceeding to Step 1: Download MP3...
```

---

## File Outputs

| File | Path |
|---|---|
| Workspace folder | `<workspaceRoot>/<slug>/` |
| Session metadata | `<workspaceRoot>/<slug>/meta.json` |

---

## Error Handling

**See**: [Error Handling Patterns](references/error-handling-patterns.md) for detailed fixes.

| Error | Solution |
|---|---|
| YouTube page fails to load | Ask user to confirm URL is valid and publicly accessible |
| Slug collision (folder exists) | Append timestamp suffix: `slug-20260327` |
| User skips optional inputs | Use defaults silently, note in meta.json |
| Permission denied on configured workspace root | Ensure `workspaceRoot` exists and is writable |

---

## Reference

- [Workspace Conventions](references/workspace-conventions.md) — Slug format, meta.json schema, file naming
- [Error Handling Patterns](references/error-handling-patterns.md) — Common errors and recovery
