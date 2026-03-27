# Step 0: Prepare Workspace

## Objective

Collect all user inputs for the remix session, create a dedicated workspace folder, and write a `meta.json` file that all subsequent steps will reference.

## Prerequisites

- Access to the local filesystem (Bash tool)
- The `workspaces/` directory exists at the project root, or will be created now

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

Ask all questions upfront in a single prompt to the user before proceeding.

---

### 0.2 — Fetch the Video Title

Navigate to the YouTube URL using Chrome DevTools MCP and extract the video title from the page.

```
Tool: navigate_page
URL: <youtube_url>
```

Once the page loads, take a snapshot and read the page title (the `<title>` element or the heading). Strip the " - YouTube" suffix if present.

**Example:**
- Raw page title: `Meesaala Pilla Full Lyrical | Chiranjeevi | Nayanthara | Bheems Music - YouTube`
- Cleaned title: `Meesaala Pilla Full Lyrical | Chiranjeevi | Nayanthara | Bheems Music`

---

### 0.3 — Generate Workspace Slug

Derive a short, filesystem-safe slug from the video title and genre:

**Rules:**
1. Take the first 4–6 meaningful words of the video title (skip filler words like "Full", "Lyrical", "Video", "Official")
2. Append the genre/style as a suffix
3. Lowercase everything
4. Replace spaces and special characters with hyphens
5. Remove any characters that are not alphanumeric or hyphens

**Examples:**
- Title: `Meesaala Pilla Full Lyrical | Chiranjeevi | Nayanthara` + Genre: `Lo-Fi`
  → Slug: `meesaala-pilla-lofi`
- Title: `Oo Antava Oo Oo Antava | Pushpa Songs` + Genre: `Hip-Hop`
  → Slug: `oo-antava-hip-hop`

---

### 0.4 — Create Workspace Directory

Create the workspace folder at:
```
workspaces/<slug>/
```

**Bash command:**
```bash
mkdir -p workspaces/<slug>
```

Verify the directory was created successfully.

---

### 0.5 — Write meta.json

Write a `meta.json` file inside the workspace with all collected and derived information.

**File path:** `workspaces/<slug>/meta.json`

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
  "workspace": "workspaces/<slug>/",
  "files": {
    "original_mp3": "workspaces/<slug>/<slug>-original.mp3",
    "acapella": "workspaces/<slug>/<slug>-acapella.mp3",
    "lyrics": "workspaces/<slug>/<slug>-lyrics.txt",
    "suno_lyrics": "workspaces/<slug>/<slug>-suno-lyrics.txt"
  },
  "status": {
    "mp3_downloaded": false,
    "acapella_extracted": false,
    "lyrics_saved": false,
    "suno_lyrics_generated": false,
    "remix_uploaded": false,
    "suno_remix_url": null
  },
  "created_at": "<ISO timestamp>"
}
```

---

### 0.6 — Confirm Workspace Ready

Print a summary to the user before proceeding:

```
Workspace ready: workspaces/<slug>/
  Video   : <video_title>
  Genre   : <genre>
  Language: <language>
  Tempo   : <tempo>
  Length  : <song_length>

Proceeding to Step 1: Download MP3...
```

---

## File Outputs

| File | Path |
|---|---|
| Workspace folder | `workspaces/<slug>/` |
| Session metadata | `workspaces/<slug>/meta.json` |

---

## Error Handling

- **YouTube page fails to load:** Ask the user to confirm the URL is valid and publicly accessible. Do not proceed until the title is confirmed.
- **Slug collision (folder already exists):** Append a short timestamp suffix to the slug (e.g., `meesaala-pilla-lofi-20260327`) to ensure uniqueness.
- **User skips optional inputs:** Use defaults silently and note them in `meta.json`.

