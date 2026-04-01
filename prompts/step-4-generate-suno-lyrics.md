# Step 4: Generate Suno Meta-Tag Lyrics

## Objective

Convert the raw Indic language lyrics from `lyrics.txt` into Suno.ai's meta-tag format, structured according to the target genre and style from `meta.json`. Save the result to the workspace.

## Prerequisites

- `workspaces/<slug>/<slug>-lyrics.txt` exists with lyrics in native Indic script
- `workspaces/<slug>/meta.json` exists with `genre`, `language`, `tempo`, `song_length`
- No browser interaction required for this step — this is a pure text transformation

---

## Instructions

### 4.1 — Read Inputs

Read the following files:
- `workspaces/<slug>/<slug>-lyrics.txt` — raw original lyrics
- `workspaces/<slug>/meta.json` — genre, tempo, song_length, language

---

### 4.2 — Ask Clarifying Questions (if not already in meta.json)

Before generating, confirm or collect the following if missing:

| Question | Default if skipped |
|---|---|
| What genre/style remix? (e.g. Lo-Fi, EDM, Hip-Hop, Carnatic Fusion) | Already in meta.json |
| What tempo? (slow / medium / energetic) | medium |
| Full song or shortened version? | full |
| Vocal gender preference? (male / female / mixed) | match original |
| Any specific mood or vibe? (e.g. dark, romantic, melancholic, party) | match genre |
| Keep all verses or trim to key sections only? | keep all |

---

### 4.3 — Understand Suno Meta-Tag Format

**See**: [Suno Format Guide](references/suno-format-guide.md) for complete format reference.

**Quick overview:**
- **Style block** (top of file): `[genre, mood, language, vocal type, bpm, instruments]`
- **Section tags**: `[Intro]`, `[Verse 1]`, `[Chorus]`, `[Bridge]`, `[Outro]`, etc.
- **Production cues**: `(soft guitar intro)`, `(drums kick in)` — inline parentheses
- **Key rules**:
  - Style block first, under 1000 characters
  - Section tags on their own line
  - Indic script only — **never romanize**

---

### 4.4 — Map Original Lyrics to Song Structure

**See**: [Suno Format Guide > Indic-to-Suno Section Mapping](references/suno-format-guide.md#indic-to-suno-section-mapping)

| Indic Term | Suno Tag |
|------------|----------|
| పల్లవి (Pallavi) | `[Chorus]` |
| చరణం (Charanam) | `[Verse]` |
| అనుపల్లవి (Anupallavi) | `[Pre-Chorus]` or `[Bridge]` |
| ముక్తాయింపు (Muktayimpu) | `[Outro]` |

If lyrics lack section labels, use context and repetition to infer them.

---

### 4.5 — Build the Style Block

**See**: [Suno Format Guide > Style Block Templates by Genre](references/suno-format-guide.md#style-block-templates-by-genre)

**Template:**
```
[<genre>, <mood>, <language>, <vocal type>, <bpm>, <instruments>, <influences>]
```

Select a template matching the genre from the guide and customize:
- Replace `<language>` with actual language (Telugu/Hindi/Tamil)
- Match vocal type to original singer gender
- Adjust BPM based on tempo preference (slow: 70-85, medium: 90-110, energetic: 120-130)

---

### 4.6 — Generate the Full Suno Meta-Tag Lyrics

Assemble the complete formatted lyrics:

1. Start with the style block on line 1
2. Add `[Intro]` with production cue if applicable
3. Map each section to appropriate Suno tag using section mapping
4. Preserve all Indic script lyrics exactly as-is
5. Add optional inline production cues in parentheses
6. End with `[Outro]` or `[Final Chorus]`

**See**: [Suno Format Guide > Example Complete Format](references/suno-format-guide.md#example-complete-format) for a full example.

---

### 4.7 — Check Length Constraints

**See**: [Suno Format Guide > Length Constraints](references/suno-format-guide.md#length-constraints)

| Component | Limit |
|-----------|-------|
| Style block | 1000 characters (hard limit) |
| Lyrics | ~3000 characters (effective limit) |

If lyrics are too long for "shortened" version, trim to:
`Intro → Chorus → Verse 1 → Chorus → Bridge → Outro`

---

### 4.8 — Save to Workspace

**Write tool:**

Save the formatted Suno lyrics to:
```
File path: workspaces/<slug>/<slug>-suno-lyrics.txt
```

Also save the style block separately for easy copy-paste in Step 5:
```
File path: workspaces/<slug>/<slug>-suno-style.txt
```

---

### 4.9 — Update meta.json Status

Update `workspaces/<slug>/meta.json`:

```json
"status": {
  "mp3_downloaded": true,
  "acapella_extracted": true,
  "lyrics_saved": true,
  "suno_lyrics_generated": true,
  ...
}
```

---

### 4.10 — Confirm Ready

Print a summary:

```
Suno lyrics generated: workspaces/<slug>/<slug>-suno-lyrics.txt
Style block: workspaces/<slug>/<slug>-suno-style.txt
Total lyrics length: <char count> characters
Style block length: <char count>/1000 characters

Proceeding to Step 5: Upload to Suno.ai...
```

---

### 4.11 — Generate design.json for Video Pipeline

**Dynamically generate a design configuration** based on the Suno style block created in 4.5. The colors should match the mood/vibe described in the style.

**Read the style block** from the generated `suno-style.txt` and analyze descriptors like:
- Mood: dark, bright, warm, cold, dreamy, aggressive, melancholic, romantic
- Atmosphere: smoky, nocturnal, hazy, vibrant, energetic, chill
- Visual cues: reverb-drenched, lo-fi warmth, synthwave textures, OVO Sound aesthetic

**Color Palette Generation Rules:**

| Style Descriptor | Suggested Palette |
|---|---|
| "dark", "nocturnal", "smoky", "moody" | Deep navy, charcoal, dark purples (#0a0a0a, #1a1a2e, #4a1a6a) |
| "warm", "golden hour", "sunset" | Amber, rust, warm browns (#c9a961, #8b4513, #d4af37) |
| "bright", "vibrant", "energetic" | Coral, yellow, cyan (#ff6b6b, #feca57, #48dbfb) |
| "dreamy", "ethereal", "lo-fi" | Soft pastels, muted blues, lavender (#a8d8ea, #d4a5a5, #9b59b6) |
| "romantic", "melancholic" | Rose, dusty pink, soft grays (#e8b4b8, #d4a5a5, #6c5ce7) |
| "carnatic", "classical", "devotional" | Gold, saffron, deep maroon (#d4af37, #ff9933, #800020) |

**Motif Selection Rules:**
- EDM/House: "aurora" or "geometric-burst"
- Hip-Hop/Trap: "geometric-burst"
- Carnatic/Classical: "waveform-rings"
- Lo-Fi/Chill: "particles"
- Pop/Bollywood: "aurora"

**Font Selection Rules:**
- EDM: "Orbitron"
- Hip-Hop: "Exo 2"
- Lo-Fi: "Lora"
- Carnatic: "Cormorant Garamond"
- Pop: "Space Grotesk"

**Generate the design.json:**

```json
{
  "palette": {
    "backgroundType": "gradient",
    "backgroundStops": [
      { "color": "#<start-color>", "position": "0%" },
      { "color": "#<mid-color>", "position": "50%" },
      { "color": "#<end-color>", "position": "100%" }
    ],
    "backgroundAngle": <90-180>,
    "primaryColor": "#ffffff",
    "secondaryColor": "#b2bec3",
    "accentColor": "#<accent>",
    "highlightColor": "#<highlight>",
    "glowColor": "#<accent>40"
  },
  "typography": {
    "googleFont": "<font-name>",
    "mainLyricSize": <70-100>,
    "mainLyricWeight": <400|600|700|800>,
    "mainLyricItalic": <true|false>,
    "letterSpacing": "<0-0.04>em",
    "textEffect": "<glow|shadow|none>",
    "sectionBadgeStyle": "<pill|box>"
  },
  "layout": {
    "variant": "cover-art",
    "showSectionBadge": true,
    "showNextLyric": true,
    "showProgressBar": true,
    "visualizerPosition": "bottom"
  },
  "motif": {
    "primary": "<motif-name>",
    "secondary": "<noise-field|particles|waveform-rings|null>",
    "intensity": "<low|medium|high>"
  },
  "animation": {
    "personality": "<smooth|aggressive|dreamy|bouncy|sharp>",
    "lyricEntrance": "<fade|slide-up|scale-in>",
    "beatReactivity": <0.5-1.0>
  }
}
```

**Save to:**
```
File path: workspaces/<slug>/design.json
```

**Update meta.json files section:**
```json
"files": {
  ...,
  "design": "workspaces/<slug>/design.json"
}
```

---

## File Outputs

| File | Path |
|---|---|
| Suno meta-tag lyrics | `workspaces/<slug>/<slug>-suno-lyrics.txt` |
| Style block only | `workspaces/<slug>/<slug>-suno-style.txt` |
| Video design config | `workspaces/<slug>/design.json` |
| Updated metadata | `workspaces/<slug>/meta.json` |

---

## Error Handling

**See**: [Error Handling Patterns > Suno Generation Errors](references/error-handling-patterns.md#suno-generation-errors-steps-4-5)

| Error | Solution |
|---|---|
| Lyrics too long | Split into `suno-lyrics-part1.txt` / `part2.txt` for separate submissions |
| Style block over 1000 chars | Trim to: genre + mood + language + vocal type |
| Song structure unclear | Default: Intro → Chorus → Verse → Chorus → Bridge → Chorus → Outro |
| Missing sections | Add comment: `# [section missing from source]` |

---

## Reference

- [Suno Format Guide](references/suno-format-guide.md) — Complete format reference
- [Workspace Conventions](references/workspace-conventions.md) — File naming
- [Error Handling Patterns](references/error-handling-patterns.md) — Common errors

