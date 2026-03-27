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

Suno.ai uses bracket-style metatags to structure lyrics. These guide the AI on song structure and production style.

**Style block (placed at the very top of lyrics):**
```
[genre, mood, language, vocal type, bpm, key, instruments, influences]
```

**Section tags:**
```
[Intro]
[Verse 1]
[Pre-Chorus]
[Chorus]
[Verse 2]
[Bridge]
[Outro]
[Instrumental Break]
[Hook]
[Refrain]
[Build]
[Drop]
[Adlib]
[Spoken]
```

**Production direction tags (optional, inline):**
```
(soft guitar intro)
(drums kick in)
(tempo drops)
(crowd chant)
(whispered)
```

**Key rules:**
- Place the style descriptor block in square brackets at the very top
- Section tags go on their own line before the lyrics of that section
- Indic script lyrics go directly under section tags — **never romanize or translate**
- Suno reads metatags as production instructions, not as lyrics to sing
- Keep the style block under 1000 characters total

---

### 4.4 — Map Original Lyrics to Song Structure

Analyze the raw lyrics from `lyrics.txt` and identify natural song sections:

- **Pallavi** (పల్లవి) → maps to `[Chorus]`
- **Charanam** (చరణం) → maps to `[Verse]`
- **Anupallavi** (అనుపల్లవి) → maps to `[Pre-Chorus]` or `[Bridge]`
- **Muktayimpu** (ముక్తాయింపు) → maps to `[Outro]`
- Repeated hook lines → `[Hook]` or `[Refrain]`
- Opening instrumental cues → `[Intro]`

If the source lyrics don't have section labels, use context and repetition to infer them.

---

### 4.5 — Build the Style Block

Construct the style block based on `meta.json` values:

**Template:**
```
[<genre>, <mood>, <language>, <vocal type>, <bpm if known>, <key if known>, <instruments>, <artist influences>]
```

**Examples by genre:**

Lo-Fi:
```
[lo-fi hip hop, nostalgic, Telugu, soft male vocal, 75 bpm, lo-fi guitar, vinyl crackle, dusty samples, J Dilla vibe]
```

EDM / Deep House:
```
[deep house, dark sexy, Telugu, breathy male vocal, 122 bpm, key E minor, serum synths, 4-on-floor kick, ZHU, After Hours vibe]
```

Carnatic Fusion:
```
[carnatic fusion, devotional-modern, Telugu, classical male vocal, mridangam, veena, subtle synth pads, AR Rahman vibe]
```

Hip-Hop:
```
[Telugu hip hop, confident, Telugu, trap male vocal, 95 bpm, 808 bass, hi-hats, boom bap drums]
```

---

### 4.6 — Generate the Full Suno Meta-Tag Lyrics

Assemble the complete formatted lyrics:

1. Start with the style block on line 1
2. Add `[Intro]` with any production cue if applicable
3. Map each section of the original lyrics to the appropriate Suno tag
4. Preserve all Indic script lyrics exactly as-is
5. Add optional inline production cues in parentheses where helpful
6. End with `[Outro]` or `[Final Chorus]`

**Example output structure:**
```
[lo-fi hip hop, nostalgic, Telugu, soft male vocal, 75 bpm, lo-fi guitar, vinyl crackle]

[Intro]
(soft guitar loop + vinyl crackle fade in)

[Chorus]
మల్లె తీగరోయ్ మనసే లాగుతోందిరోయ్
పిట్ట నడుమురోయ్ పిల్లా చంపుతోందిరోయ్
హే నవ్వమాకురోయ్ కలలే రువ్వమాకురోయ్
నరము నరములో వేడి పెంచామాకురోయ్

[Verse 1]
అల్లుకోకూరోయ్ అలలా గిళ్లిపోకూరోయ్
అగ్గిపుల్లవై నాలో భగ్గుమనకూరోయ్

[Bridge]
(tempo drops, soft piano)
అంతో ఇంతో నే ట్రై చేస్తా
ఏంతో ఇంతో రూటుకు తెస్తా

[Final Chorus]
మల్లె తీగరోయ్ మనసే లాగుతోందిరోయ్
పిట్ట నడుమురోయ్ పిల్లా చంపుతోందిరోయ్

[Outro]
(guitar loop fades out with vinyl crackle)
```

---

### 4.7 — Check Length Constraints

Suno.ai has a **1000-character limit on the Style field** and processes roughly **3000 characters of lyrics** effectively.

- Count the total character length of the style block
- If lyrics are very long and `song_length` is `"shortened"`, trim to: Intro + Chorus + Verse 1 + Chorus + Bridge + Outro
- If `song_length` is `"full"`, keep all sections

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

## File Outputs

| File | Path |
|---|---|
| Suno meta-tag lyrics | `workspaces/<slug>/<slug>-suno-lyrics.txt` |
| Style block only | `workspaces/<slug>/<slug>-suno-style.txt` |
| Updated metadata | `workspaces/<slug>/meta.json` |

---

## Error Handling

- **Lyrics too long:** If lyrics exceed Suno's effective processing length, split into two parts and generate two separate `suno-lyrics-part1.txt` / `suno-lyrics-part2.txt` files for separate Suno submissions.
- **Style block over 1000 chars:** Trim instrument and influence details, keep genre + mood + language + vocal type as minimum.
- **Song structure unclear:** Default to: Intro → Chorus → Verse → Chorus → Bridge → Chorus → Outro.
- **Missing lyrics sections:** Note gaps with a comment `# [section missing from source]` in the output file.

