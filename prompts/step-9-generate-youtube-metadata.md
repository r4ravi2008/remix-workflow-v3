# Step 9: Generate YouTube Metadata

## Objective

Create optimized YouTube metadata (title, description, tags, thumbnail text) for the remix video to maximize discoverability and engagement. The metadata should highlight the remix genre while respecting the original song's cultural roots.

## Key Requirements

- **SEO-optimized title**: Include original song name, remix genre, and key descriptors — no references to Suno, AI, or any generation tools
- **Compelling description**: Hook viewers in first 2 lines, include credits, links, and timestamps — no references to Suno, AI, or any generation tools
- **Strategic tags**: Mix of broad (genre) and specific (song/artist) keywords — no AI/tool tags
- **Thumbnail text**: Short, bold text that reads well at small sizes — no AI/tool references
- **Language tags**: Include both English and native language (Telugu/Hindi/Tamil) keywords
- **STRICT RULE**: Never mention Suno, AI, "AI-generated", "AI-powered", or any music generation tool anywhere in the title, description, tags, hashtags, or thumbnail text

## Prerequisites

- `${WORKSPACE_DIR}/meta.json` exists with `video_title`, `genre`, `language`, `youtube_url`
- `${WORKSPACE_DIR}/${SLUG}-suno-style.txt` exists (for style descriptors)
- `${WORKSPACE_DIR}/${SLUG}-video.mp4` exists (video is ready to upload)

## Workspace Path Resolution

Before using any filesystem path in this step:

1. Read `.remix-workspace-root.json` from the repo root.
2. Resolve `WORKSPACE_ROOT` from its `workspaceRoot` field.
3. Resolve `WORKSPACE_DIR` as `<workspaceRoot>/<slug>/`.
4. Use absolute paths under `WORKSPACE_DIR` for filesystem commands.
5. Keep any stored `meta.json.files.*` values root-relative, for example `<slug>/design.json`.

---

## Instructions

### 9.1 — Read Inputs

Read the following files:
- `${WORKSPACE_DIR}/meta.json` — original song info, genre, language
- `${WORKSPACE_DIR}/${SLUG}-suno-style.txt` — style descriptors for keywords

Extract:
- Original song title and movie/album
- Original artists (singers, composers, lyricists)
- Remix genre and BPM
- Language (Telugu/Hindi/Tamil)

---

### 9.2 — Generate YouTube Title

**Format:**
```
<Original Song Name> (Remix) — <Genre> | <Language> | <Movie>
```

**Rules:**
- Keep under 100 characters (optimal: 60-80)
- Put the most important keywords first
- Include "Remix" to signal it's a transformation
- Never mention Suno, AI, or any generation tool
- If original movie is known, include it at the end

**Examples:**
```
Chitapata Chinukulu (Dark Deep House Remix) — Telugu | Mallanna
Bella Bella (Lo-Fi Remix) — Telugu | Bhartha Mahasayulaku Wignyapthi
Neeve Neeve (EDM Remix) — Telugu | Naa Peru Surya
```

---

### 9.3 — Generate YouTube Description

**Structure:**
```
🎵 <Hook line describing the vibe>

A fan-made remix of "<Original Song>" reimagined as <Genre>.

🎧 ORIGINAL SONG:
• Title: <Original Title>
• Movie/Album: <Movie>
• Singer(s): <Singers>
• Composer: <Composer>
• Lyricist: <Lyricist>

🎛️ REMIX DETAILS:
• Genre: <Genre>
• BPM: <BPM>
• Key: <Key>
• Style: <Short style description from suno-style.txt>

🔗 LINKS:
• Original Song: <youtube_url from meta.json>

📱 FOLLOW FOR MORE:
Subscribe for more remixes of classic Indian songs!

#<GenreTag> #<Language>Remix #IndianMusic

---

⚠️ DISCLAIMER: This is a fan-made remix created for educational and entertainment purposes. All rights to the original song belong to the respective copyright holders. No copyright infringement intended.
```

**Rules:**
- First 2 lines are crucial (shown in search results)
- Use emojis sparingly for visual breaks
- Include all original credits to respect artists
- Add timestamps if video has distinct sections
- Never mention Suno, AI, or any generation tool anywhere
- Include disclaimer for copyright safety

---

### 9.4 — Generate Tags

**Categories:**

1. **Genre Tags** (broad discovery):
   - `<Genre>` (e.g., "deep house", "lo-fi hip hop", "edm")
   - `<Genre> remix`
   - `<Genre> mix`
   - `electronic music`
   - `remix`

2. **Language + Region Tags**:
   - `<Language> songs` (e.g., "telugu songs")
   - `<Language> remix`
   - `<Language> music`
   - `south indian music`
   - `indian remix`

3. **Original Song Tags** (specific discovery):
   - `<Original Song Name>`
   - `<Movie Name>`
   - `<Singer Name>`
   - `<Composer Name>`
   - `<Original Song Name> remix`

4. **Mood/Vibe Tags** (from suno-style.txt):
   - `chill music`
   - `late night vibes`
   - `introspective`
   - `smoky beats`

**Rules:**
- Generate 15-20 tags total
- Mix broad and specific keywords
- Include variations (singular/plural, spaces/hyphens)
- YouTube allows 500 characters total for tags

---

### 9.5 — Generate Thumbnail Text

**Primary Text** (large, center):
```
<Short Song Name>
<Genre>
```

**Examples:**
```
Chitapata
Deep House
```

**Secondary Text** (smaller, bottom):
```
Fan Remix
```

**Rules:**
- Maximum 2-3 words per line
- Must be readable at 1280×720 scaled to 160×90 (mobile)
- Use high contrast colors from design.json palette
- Consider Telugu/Hindi text if original script is recognizable

---

### 9.6 — Generate Hashtags for Shorts/Reels

If creating Shorts versions:
```
#<Language>Remix #<Genre> #IndianMusic #Remix #<SongShortName>
```

---

### 9.7 — Save Metadata to Workspace

**Write files:**

```json
File path: ${WORKSPACE_DIR}/youtube-metadata.json
```

```json
{
  "title": "<generated title>",
  "description": "<generated description>",
  "tags": ["tag1", "tag2", ...],
  "thumbnail": {
    "primaryText": "<line 1>",
    "secondaryText": "<line 2>",
    "suggestedColors": {
      "background": "<from design.json>",
      "text": "<from design.json>",
      "accent": "<from design.json>"
    }
  },
  "hashtags": ["#tag1", "#tag2", ...],
  "category": "Music",
  "privacy": "public",
  "madeForKids": false
}
```

Also generate a markdown artifact for easy copy-paste:
```
File path: ${WORKSPACE_DIR}/youtube-metadata-artifact.md
```

The markdown artifact format should be:

```markdown
# YouTube Upload Metadata — <Song Name>

## 📹 TITLE (Copy & Paste)
```
<generated title>
```

## 📝 DESCRIPTION (Copy & Paste)
```
<generated description>
```

## 🏷️ TAGS (Copy & Paste)
```
tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8, tag9, tag10, tag11, tag12, tag13, tag14, tag15, tag16, tag17, tag18, tag19, tag20
```

## 🎨 THUMBNAIL TEXT

**Primary (Large):**
```
<primary text>
```

**Secondary (Small):**
```
<secondary text>
```

**Color Scheme:**
- Background: `<color>`
- Text: `<color>`
- Accent: `<color>`

## 📱 SHORTS HASHTAGS
```
#Tag1 #Tag2 #Tag3 #Tag4 #Tag5
```

---

**Generated:** <timestamp>
**Song:** <original song name>
**Genre:** <genre>
```

---

### 9.8 — Update meta.json

Update `${WORKSPACE_DIR}/meta.json`:

```json
"status": {
  ...,
  "youtube_metadata_generated": true
},
"files": {
  ...,
  "youtube_metadata": "<slug>/youtube-metadata.json"
}
```

---

### 9.9 — Present Metadata Summary

```
YouTube Metadata Generated for: <slug>

TITLE (<char count> chars):
<generated title>

DESCRIPTION (<char count> chars):
<first 2 lines>
...

TAGS (<count> tags, <char count> chars total):
<tag1>, <tag2>, <tag3>, ...

THUMBNAIL TEXT:
  Primary: <text>
  Secondary: <text>
  Suggested Colors: <colors from design.json>

Files saved:
  • youtube-metadata.json
  • youtube-metadata-artifact.md
```

---

## SEO Best Practices

| Element | Best Practice |
|---------|---------------|
| Title | Keywords first, brand last, keep under 100 chars |
| Description | Hook in first 2 lines, 150-200 words total |
| Tags | Mix broad (high volume) + specific (low competition) |
| Thumbnail | Contrasting colors, max 3 words, readable at small size |
| Hashtags | 3-5 per Short, relevant to content |

## File Outputs

| File | Path |
|---|---|
| Full metadata JSON | `<workspaceRoot>/<slug>/youtube-metadata.json` |
| **Markdown artifact (copy-paste)** | `<workspaceRoot>/<slug>/youtube-metadata-artifact.md` |
| Updated metadata | `<workspaceRoot>/<slug>/meta.json` |

## Error Handling

**See**: [Error Handling Patterns](references/error-handling-patterns.md) for detailed fixes.

| Error | Solution |
|---|---|
| Title too long | Trim secondary descriptors, keep "Song (Remix) — Genre \| Language" |
| Missing original credits | Use placeholder: "[Original artist info unavailable — please verify]" |
| Description over 5000 chars | Truncate tags section or remove timestamps |
| No design.json | Use neutral colors (#1a1a2e, #ffffff) for thumbnail suggestions |

---

## Reference

- [Workspace Conventions](references/workspace-conventions.md) — File naming
- [Error Handling Patterns](references/error-handling-patterns.md) — Common errors
