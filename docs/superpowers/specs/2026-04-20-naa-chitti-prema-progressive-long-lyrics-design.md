# Naa Chitti Prema Progressive Long Lyrics Design

## Goal

Add a new Suno lyric artifact for the `naa-chitti-prema-deep-house` workspace that is specifically shaped for a longer progressive-house arrangement.

The new artifact must:
- preserve the original hook lines as anchor moments
- introduce newly written Telugu sections for long-form flow
- use Suno-compatible meta-tags and concise production cues
- map cleanly to 16-bar progressive-house sections
- leave the existing `full` and `short` lyric artifacts unchanged

## Workspace Scope

Target workspace:
- `/mnt/c/Users/r4rav/iCloudDrive/ai-music/workspaces/naa-chitti-prema-deep-house/`

New file to add:
- `naa-chitti-prema-deep-house-suno-lyrics-progressive-long.txt`

Metadata update:
- add `files.suno_lyrics_progressive_long` to `meta.json`

## Creative Direction

The new lyric file should aim for a melodic, romantic, late-night progressive-house feel rather than a compact radio-style arrangement.

Guiding principles:
- keep `కాదన్నా ప్రేమే...` and `నా చిట్టి ప్రేమా...` as the emotional anchors
- write new Telugu verses, pre-chorus, build, and bridge lines around those anchors
- favor shorter, loop-friendly phrasing over dense literary lines
- preserve a devotional-romantic emotional tone close to the source song
- give Suno clear structure and energy changes without overloading the prompt with instructions

## Structure

The new artifact will use a long-form 16-bar-oriented structure:

1. `[Intro]` - 16 bars
2. `[Verse 1]` - 16 bars
3. `[Pre-Chorus]` - 16 bars
4. `[Chorus]` - 16 bars
5. `[Verse 2]` - 16 bars
6. `[Build]` - 16 bars
7. `[Drop]` - 16 bars
8. `[Bridge]` - 16 bars
9. `[Final Chorus]` - 16 bars
10. `[Outro]` - 16 bars

Implementation intent for each section:
- `[Intro]`: mostly production cues and sparse lyrical setup
- `[Verse 1]`: new Telugu lines that establish longing and closeness
- `[Pre-Chorus]`: rising, repetitive phrasing that creates lift
- `[Chorus]`: preserve the original hook lines intact
- `[Verse 2]`: new Telugu lines that deepen emotional commitment
- `[Build]`: repetition, open vowels, and lift cues suitable for progressive-house escalation
- `[Drop]`: hook-led section, explicitly reusing the original chorus lines again
- `[Bridge]`: emotional release centered on `నా చిట్టి ప్రేమా...`
- `[Final Chorus]`: strongest reprise of the original hook material
- `[Outro]`: deconstruction and fade cues with minimal text

## Suno Meta-Tag Design

The file should follow the existing repository Suno conventions:
- style block on line 1
- section tags on their own lines
- optional energy, mood, and vocal-style control tags where useful
- production cues in parentheses only when they add clear value

Recommended style direction:
- `deep house`
- `progressive romantic nocturnal`
- `Telugu`
- `soft male vocal`
- around `116 bpm`
- `key E minor`
- `warm sub bass`, `four-on-the-floor kick`, `analog synth pads`, `airy plucks`
- a negative constraint such as `no harsh distortion`

Recommended control tags to use sparingly:
- `[Energy: Low]`
- `[Energy: Rising]`
- `[Energy: Medium→High]`
- `[Mood: Romantic]`
- `[Vocal Style: Soft]`

## Lyric Writing Rules

Rules for the new lyrical content:
- Telugu script only
- preserve original hook lines exactly in `[Chorus]`, `[Drop]`, and `[Final Chorus]`
- write new Telugu lines for the non-hook sections
- keep lines short enough for Suno phrasing and melodic repetition
- avoid excessive internal complexity or crowded syllable counts
- prefer phrases that can sustain long progressive-house loops and emotional repetition

The verses and bridge should feel newly tailored for the genre rather than copied from the original song body.

## File and Metadata Changes

Add the new lyric artifact:
- `naa-chitti-prema-deep-house-suno-lyrics-progressive-long.txt`

Update `meta.json` to include:

```json
{
  "files": {
    "suno_lyrics_progressive_long": "naa-chitti-prema-deep-house/naa-chitti-prema-deep-house-suno-lyrics-progressive-long.txt"
  }
}
```

Do not remove or overwrite:
- `suno_lyrics`
- `suno_lyrics_shortened`
- `suno_style`

## Validation

After implementation, verify:
- the new file exists in the workspace
- `meta.json` points to it correctly
- the style block remains under 1000 characters
- the full lyric artifact remains within a practical Suno length range, targeting roughly 1800-2800 characters
- original hook lines are preserved exactly in the intended sections
- existing lyric artifacts remain unchanged

## Non-Goals

This design does not include:
- changing the existing `full` or `short` lyric files
- uploading to Suno
- generating remix audio
- modifying design assets or video configuration

## User Constraint

Do not create a git commit for this work unless the user explicitly asks for one.
