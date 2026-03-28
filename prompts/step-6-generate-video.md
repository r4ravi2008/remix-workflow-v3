# Step 6: Generate Video with Remotion

## Objective

Create a music video with full audio duration and karaoke-style synchronized lyrics using the
Remotion video template. The template handles all synced-lyrics rendering logic — this step
focuses on running the pipeline and wiring up the correct data.

## Key Requirements

- **Full audio duration**: Video must match the complete audio length (not hardcoded)
- **Lyrics synchronization**: Lyrics timed to audio via CTC forced alignment, not guessing
- **Section display**: Show current section (Verse, Chorus, etc.) prominently
- **Indic script support**: Telugu/Hindi/Tamil text renders correctly via system fonts

## Prerequisites

- Remix audio exists: `workspaces/<slug>/<slug>-remix-v1.mp3`
- `workspaces/<slug>/<slug>-suno-lyrics.txt` exists
- `workspaces/<slug>/meta.json` exists with `genre`, `slug`, `language`

---

## Instructions

### 6.1 — Read Workspace Files

Read `meta.json` and extract: `songTitle`, `genre`, `language`, `slug`.

---

### 6.2 — Extract Acapella from Remix Audio

Run the acapella extractor on the Suno remix (not the original) to get clean vocals for alignment:

```bash
cd tools/acapella-extractor
uv run python src/acapella_extractor/extract.py \
  ../../workspaces/<slug>/<slug>-remix-v1.mp3 \
  --output-dir ../../workspaces/<slug>/
```

The separator writes a WAV file. Convert it to MP3 and give it the slug-prefixed name:

```bash
ffmpeg -i "workspaces/<slug>/<slug>-remix-v1_(vocals)_mel_band_roformer_kim_ft_unwa.wav" \
  -codec:a libmp3lame -q:a 2 \
  "workspaces/<slug>/<slug>-remix-v1-acapella.mp3"
rm "workspaces/<slug>/<slug>-remix-v1_(vocals)_mel_band_roformer_kim_ft_unwa.wav"
```

Output: `workspaces/<slug>/<slug>-remix-v1-acapella.mp3`

**Note:** This is separate from the Step 2 acapella (extracted from the original YouTube
download). This one is from the Suno remix and is used only for lyrics alignment.

---

### 6.3 — Generate Lyrics Timestamps

Run the CTC forced aligner against the acapella:

```bash
cd tools/acapella-extractor
uv run python align_lyrics.py \
  --audio ../../workspaces/<slug>/<slug>-remix-v1-acapella.mp3 \
  --lyrics ../../workspaces/<slug>/<slug>-suno-lyrics.txt \
  --output ../../workspaces/<slug>/lyrics-timestamps.json \
  --language <iso-639-3-code>
```

Use `tel` for Telugu, `hin` for Hindi, `tam` for Tamil. The script strips section headers and
stage directions automatically, aligns at word level (~20ms resolution), and groups results
back into lyric lines.

---

### 6.4 — Verify Alignment

Print a terminal karaoke preview and confirm timing is correct before rendering:

```bash
cd tools/acapella-extractor
uv run python verify_lyrics.py ../../workspaces/<slug>/lyrics-timestamps.json
```

Check:
- First vocal line appears within ±500ms of its actual onset
- Chorus lines align within ±1s
- No lines appear during instrumental sections
- Total drift at end < 3s

Do not proceed to render until these pass. If alignment is off, check acapella quality and
re-run `align_lyrics.py`.

---

### 6.4.5 — Generate Visual Design Configuration

Generate a unique visual design for this song based on its metadata:

```bash
cd tools/video-generator
node generate-design.js <slug>
```

This creates `workspaces/<slug>/design.json` with:
- **Layout variant**: center-stage, full-bleed, minimal, sidebar, or stacked
- **Visual motif**: particles, geometric-burst, aurora, waveform-rings, or noise-field
- **Color palette**: Generated from genre and mood
- **Typography**: Font, sizing, and text effects
- **Animation personality**: smooth, bouncy, sharp, dreamy, or aggressive

The design is seeded from the song slug and duration, ensuring the same song always gets
the same visual identity.

---

### 6.5 — Scaffold Remotion Project

The `init-video.js` scaffolder copies the template, detects the audio duration from the remix
file via ffprobe, injects song title and genre into `Root.tsx`, and copies the design.json
automatically. No manual code editing needed.

```bash
cd tools/video-generator
node init-video.js <slug> --design=../../workspaces/<slug>/design.json
```

This creates `workspaces/<slug>/video/` with everything wired up, including the visual design
configuration.

---

### 6.6 — Copy Assets to Video Project

```bash
cp workspaces/<slug>/<slug>-remix-v1.mp3          workspaces/<slug>/video/public/audio.mp3
cp workspaces/<slug>/lyrics-timestamps.json        workspaces/<slug>/video/public/
cp workspaces/<slug>/design.json                   workspaces/<slug>/video/public/
cp workspaces/<slug>/<slug>-suno-lyrics.txt        workspaces/<slug>/video/public/suno-lyrics.txt
```

---

### 6.7 — Install Dependencies and Render

```bash
cd workspaces/<slug>/video
npm install
npx remotion render MusicVideo out/video.mp4
```

Rendering takes 1–2 minutes for a typical 3–4 minute song.

---

### 6.8 — Copy Output to Workspace

```bash
cp workspaces/<slug>/video/out/video.mp4 workspaces/<slug>/<slug>-video.mp4
```

---

### 6.9 — Update Metadata

Update `workspaces/<slug>/meta.json` to record the video output:

```json
{
  "status": { "video_generated": true },
  "outputs": {
    "final_video": "workspaces/<slug>/<slug>-video.mp4",
    "remix_acapella": "workspaces/<slug>/<slug>-remix-v1-acapella.mp3",
    "lyrics_timestamps": "workspaces/<slug>/lyrics-timestamps.json",
    "design_config": "workspaces/<slug>/design.json"
  }
}
```

---

### 6.10 — Present Final Results

```
Video generation complete!

Outputs in workspaces/<slug>/:
   <slug>-video.mp4                  — Final music video (1920×1080) with audio-reactive visuals
   <slug>-remix-v1.mp3               — Remix audio
   <slug>-remix-v1-acapella.mp3      — Vocals extracted from remix
   lyrics-timestamps.json            — Word+line timestamps (CTC aligned)
   design.json                       — LLM-generated visual design configuration
   video/                            — Remotion project

Duration: <duration>s  |  Lyrics: <n> lines synced  |  Layout: <layout>  |  Motif: <motif>
```

---

## How the Template Works

The video template in `tools/video-generator/template/` is self-contained:

- **`Root.tsx`** — sets composition duration (in frames) and passes song metadata as props.
  `init-video.js` fills in `AUDIO_DURATION`, `SONG_TITLE`, and `GENRE` automatically.

- **`MusicVideo.tsx`** — handles all synced-lyrics rendering with audio-reactive visuals:
  - Uses `useAudioData()` from `@remotion/media-utils` to get real frequency data
  - Loads `design.json` for layout, colors, fonts, and visual motifs
  - Renders one of 5 layout variants (center-stage, full-bleed, minimal, sidebar, stacked)
  - Displays audio-reactive visual motifs (particles, geometric-burst, aurora, waveform-rings, noise-field)
  - Uses Remotion's `delayRender` / `continueRender` for async data loading
  - Finds the active lyric line and section for the current timestamp

- **`design.json`** — LLM-generated design configuration with palette, typography, layout,
  animation personality, and visual motif selection. Generated by `generate-design.js`.

Do not edit the generated video project manually unless customizing visuals. Re-scaffold from
the template if the project gets into a broken state.

---

## Error Handling

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: acapella_extractor` | Use `src/acapella_extractor/extract.py` directly, not `-m` |
| Acapella output is WAV | Convert with ffmpeg as shown in step 6.2 |
| Lyrics not syncing | Check `lyrics-timestamps.json` is in `video/public/` |
| No lyrics visible in rendered video | Missing `delayRender` — re-scaffold from template |
| Telugu text garbled | Font issue — system-ui fallback handles it; no fix needed |
| ffprobe not found | `brew install ffmpeg` |
| Alignment too far off | Check acapella quality; try `--language` code for a closer MMS checkpoint |
