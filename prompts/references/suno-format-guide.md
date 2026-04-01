# Suno Format Guide

Reference for Suno.ai meta-tag format used in Steps 4 and 5.

## Meta-Tag Format Overview

Suno.ai uses bracket-style metatags to structure lyrics and guide production. These are instructions, not lyrics to be sung.

### Style Block (Required)

Place at the very top of the lyrics file:

```
[<genre>, <mood>, <language>, <vocal type>, <bpm>, <key>, <instruments>, <influences>]
```

**Character limit**: 1000 characters for the entire style block.

### Section Tags

Use these tags on their own line to mark song sections:

| Tag | Purpose |
|-----|---------|
| `[Intro]` | Opening instrumental or vocal section |
| `[Verse 1]`, `[Verse 2]` | Main narrative sections |
| `[Pre-Chorus]` | Build-up before chorus |
| `[Chorus]` | Main hook/refrain |
| `[Bridge]` | Contrasting middle section |
| `[Outro]` | Closing section |
| `[Instrumental Break]` | Music-only section |
| `[Hook]` | Catchy repeated phrase |
| `[Refrain]` | Recurring lines |
| `[Build]` | Increasing intensity |
| `[Drop]` | EDM-style bass drop |
| `[Adlib]` | Improvised vocalizations |
| `[Spoken]` | Spoken word section |

### Production Direction Tags (Optional)

Use parentheses for inline production cues:

```
(soft guitar intro)
(drums kick in)
(tempo drops)
(crowd chant)
(whispered)
(echo effect)
```

## Indic-to-Suno Section Mapping

Map traditional Indic song structure to Suno sections:

| Indic Term | Suno Tag | Notes |
|------------|----------|-------|
| **పల్లవి (Pallavi)** | `[Chorus]` | Main recurring theme |
| **చరణం (Charanam)** | `[Verse]` | Narrative sections |
| **అనుపల్లవి (Anupallavi)** | `[Pre-Chorus]` or `[Bridge]` | Transitional section |
| **ముక్తాయింపు (Muktayimpu)** | `[Outro]` | Closing flourish |
| **స్వరం (Swaram)** | `[Instrumental Break]` | Musical interlude |
| **స్థాయి (Sthayi)** | `[Build]` or `[Verse 2]` | Higher octave section |

## Style Block Templates by Genre

### Lo-Fi

```
[lo-fi hip hop, nostalgic, <language>, soft <gender> vocal, 75 bpm, lo-fi guitar, vinyl crackle, dusty samples, J Dilla vibe, chill beats]
```

### Deep House / EDM

```
[deep house, dark sexy, <language>, breathy <gender> vocal, 122 bpm, key E minor, serum synths, 4-on-floor kick, sub bass, ZHU, After Hours aesthetic]
```

### Carnatic Fusion

```
[carnatic fusion, devotional-modern, <language>, classical <gender> vocal, 85 bpm, mridangam, veena, tabla, subtle synth pads, tanpura drone, AR Rahman inspired]
```

### Hip-Hop / Trap

```
[<language> hip hop, confident, <language>, trap <gender> vocal, 95 bpm, 808 bass, hi-hats, boom bap drums, vocal chops, modern trap]
```

### Synthwave / Retro

```
[synthwave, retro-futuristic, <language>, smooth <gender> vocal, 110 bpm, analog synths, arpeggios, neon aesthetic, 80s inspired]
```

## Language Codes

Use full language names in the style block:

| Language | Use This |
|----------|----------|
| Telugu | `Telugu` |
| Hindi | `Hindi` |
| Tamil | `Tamil` |
| Kannada | `Kannada` |
| Malayalam | `Malayalam` |

## Vocal Type Options

| Option | Use When |
|--------|----------|
| `male vocal` | Original singer is male |
| `female vocal` | Original singer is female |
| `mixed vocals` | Both male and female |
| `soft male vocal` | Gentle, mellow delivery |
| `breathy female vocal` | Intimate, whispery style |
| `classical male vocal` | Traditional/Carnatic style |
| `trap male vocal` | Modern hip-hop style |

## Example Complete Format

```
[lo-fi hip hop, nostalgic rainy night vibe, Telugu, soft male vocal, 75 bpm, lo-fi electric guitar, vinyl crackle, dusty samples, distant thunder, J Dilla beat aesthetic, chill study beats]

[Intro]
(soft guitar loop with vinyl crackle fade in)
(rain ambience)

[Chorus]
మల్లె తీగరోయ్ మనసే లాగుతోందిరోయ్
పిట్ట నడుమురోయ్ పిల్లా చంపుతోందిరోయ్
హే నవ్వమాకురోయ్ కలలే రువ్వమాకురోయ్
నరము నరములో వేడి పెంచామాకురోయ్

[Verse 1]
అల్లుకోకూరోయ్ అలలా గిళ్లిపోకూరోయ్
అగ్గిపుల్లవై నాలో భగ్గుమనకూరోయ్

[Bridge]
(tempo drops, soft piano enters)
అంతో ఇంతో నే ట్రై చేస్తా
ఏంతో ఇంతో రూటుకు తెస్తా

[Final Chorus]
మల్లె తీగరోయ్ మనసే లాగుతోందిరోయ్
పిట్ట నడుమురోయ్ పిల్లా చంపుతోందిరోయ్

[Outro]
(guitar loop fades out)
(vinyl crackle continues)
(thunder rumbles)
```

## Key Rules

1. **Style block first**: Must be line 1, in square brackets
2. **Section tags on their own line**: Each `[Tag]` gets its own line before lyrics
3. **Indic script only**: Never romanize lyrics — Suno can handle Telugu/Hindi/Tamil
4. **Production cues in parentheses**: Optional inline directions
5. **Keep style under 1000 chars**: Trim instruments/influences if needed
6. **Meta-tags are NOT sung**: Suno treats them as production instructions

## Length Constraints

| Component | Limit | Notes |
|-----------|-------|-------|
| Style block | 1000 characters | Hard limit |
| Lyrics | ~3000 characters | Effective processing limit |
| Total song | 4 minutes | Suno generation limit |

If lyrics exceed limits for a "shortened" version, trim to:
```
Intro → Chorus → Verse 1 → Chorus → Bridge → Outro
```
