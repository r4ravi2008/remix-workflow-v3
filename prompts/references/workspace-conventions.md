# Workspace Conventions

Shared conventions for workspace structure, file naming, and metadata management.

## Slug Format

The workspace slug identifies each remix uniquely and determines the folder name.

### Rules

1. Take the first 4–6 meaningful words of the video title
2. Skip filler words: "Full", "Lyrical", "Video", "Official", "HD", "Song"
3. Append the genre/style as a suffix
4. Lowercase everything
5. Replace spaces and special characters with hyphens
6. Remove characters that are not alphanumeric or hyphens

### Examples

| Video Title | Genre | Slug |
|-------------|-------|------|
| `Meesaala Pilla Full Lyrical \| Chiranjeevi \| Nayanthara` | Lo-Fi | `meesaala-pilla-lofi` |
| `Oo Antava Oo Oo Antava \| Pushpa Songs` | Hip-Hop | `oo-antava-hip-hop` |
| `Chitapata Chinukulu Video Song \| Mallanna` | Deep House | `chitapata-chinukulu-deep-house` |

### Collision Handling

If a workspace folder already exists, append a timestamp suffix:
```
meesaala-pilla-lofi-20260327
```

## Workspace Root Configuration

Each cloned repo uses a local, untracked config file at the repo root:

```json
{
  "workspaceRoot": "/absolute/path/to/your/remix-workspaces"
}
```

- The file name is `.remix-workspace-root.json`.
- Copy it from `.remix-workspace-root.example.json` after cloning.
- `workspaceRoot` is the parent directory that contains all slug folders.
- If the file is missing, malformed, or points to a missing directory, stop and fix local setup before running any pipeline step.

## Directory Structure

```text
<workspaceRoot>/
└── <slug>/
    ├── meta.json
    ├── <slug>-original.mp3
    ├── <slug>-acapella.mp3
    ├── <slug>-lyrics.txt
    ├── <slug>-suno-lyrics.txt
    ├── <slug>-suno-style.txt
    ├── <slug>-remix-v1.mp3
    ├── <slug>-remix-v2.mp3
    ├── <slug>-remix-v1-acapella.mp3
    ├── lyrics-timestamps.json
    ├── <slug>-cover-art.jpg
    ├── <slug>-video.mp4
    ├── design.json
    ├── youtube-metadata.json
    ├── youtube-metadata-artifact.md
    ├── shorts-segments.json
    └── <slug>-short.mp4
```

## meta.json Schema

```json
{
  "youtube_url": "https://www.youtube.com/watch?v=...",
  "video_title": "Cleaned Video Title",
  "slug": "song-name-genre",
  "genre": "Lo-Fi",
  "language": "Telugu",
  "tempo": "medium",
  "song_length": "full",
  "shorts_clip_mode": "auto",
  "shorts_duration": 30,
  "workspace": "song-name-genre/",
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
    "youtube_metadata_generated": false,
    "shorts_clip_selected": false,
    "short_video_generated": false,
    "suno_remix_url_v1": null,
    "suno_remix_url_v2": null,
    "suno_cdn_v1": null,
    "suno_cdn_v2": null,
    "selected_remix": null,
    "lyrics_source_url": null,
    "cover_art_skipped": false
  },
  "created_at": "2026-03-27T12:00:00Z"
}
```

## File Naming Convention

All files in a workspace follow this pattern:
```
<slug>-<purpose>.<ext>
```

- `<slug>`: The workspace slug (lowercase, hyphenated)
- `<purpose>`: Brief descriptor of the file's role
- `<ext>`: Appropriate extension for the file type

### Purpose Suffixes

| Suffix | Meaning |
|--------|---------|
| `original` | Original audio from YouTube |
| `acapella` | Extracted vocals (from original) |
| `lyrics` | Raw lyrics in native script |
| `suno-lyrics` | Lyrics in Suno meta-tag format |
| `suno-style` | Style block for Suno.ai |
| `remix-v1` | First Suno variation |
| `remix-v2` | Second Suno variation |
| `remix-v1-acapella` | Vocals extracted from remix v1 |
| `cover-art` | AI-stylized cover image |
| `video` | Final rendered music video |
| `short` | Rendered vertical short video |

## Native Script Rule

**All lyrics must be in native Indic script. Never romanize or transliterate.**

### Supported Languages

| Language | Script | Example |
|----------|--------|---------|
| Telugu | Telugu | `మల్లె తీగరోయ్` |
| Hindi | Devanagari | `मल्ले तीगरोय` |
| Tamil | Tamil | `மல்லே தீகரோய்` |

### Anti-Pattern

❌ Romanized: `malle theegaroy`
✅ Native: `మల్లె తీగరోయ్`

This applies to:
- Saved lyrics files
- Suno meta-tag lyrics
- Video subtitle text
- Any display text in the pipeline
