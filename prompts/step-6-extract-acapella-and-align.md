# Step 6: Extract Acapella & Align Lyrics

## Objective

Extract clean vocals from the Suno remix audio and use CTC forced alignment to generate
precise word- and line-level timestamps. These timestamps are the input to the video
generation step.

## Key Requirements

- **Remix acapella only**: Extract from the Suno remix, not the original YouTube download
- **CTC forced alignment**: Timestamps must come from forced alignment, not guessing
- **Verification gate**: Do not proceed to Step 7 (cover art) until alignment passes quality checks
- **Indic script support**: Use the correct ISO 639-3 language code for alignment

## Prerequisites

- `workspaces/<slug>/<slug>-remix-v1.mp3` exists (user-selected version from Step 5)
- `workspaces/<slug>/<slug>-suno-lyrics.txt` exists
- `workspaces/<slug>/meta.json` exists with `genre`, `slug`, `language`

---

## Instructions

### 6.1 — Read Workspace Files

Read `meta.json` and extract: `songTitle`, `genre`, `language`, `slug`.

---

### 6.2 — Extract Acapella from Remix Audio

Run the acapella extractor on the remix (not the original) to get clean vocals for alignment. All commands run from the **project root**:

```bash
uv run --python tools/acapella-extractor/.venv/bin/python \
  tools/acapella-extractor/src/acapella_extractor/extract.py \
  workspaces/<slug>/<slug>-remix-v1.mp3 \
  --output-dir workspaces/<slug>/
```

The extractor writes a WAV file to `workspaces/<slug>/`. Convert it to MP3 and name it with the slug prefix:

```bash
WAV=$(ls workspaces/<slug>/*remix-v1*vocals*.wav 2>/dev/null | head -1)
ffmpeg -i "$WAV" -codec:a libmp3lame -q:a 2 \
  "workspaces/<slug>/<slug>-remix-v1-acapella.mp3"
rm "$WAV"
```

Output: `workspaces/<slug>/<slug>-remix-v1-acapella.mp3`

This acapella is extracted from the remix (not the original YouTube download) and is used exclusively for CTC lyrics alignment.

---

### 6.3 — Generate Lyrics Timestamps

Run the CTC forced aligner against the acapella. All commands run from the **project root**:

```bash
uv run --python tools/acapella-extractor/.venv/bin/python \
  tools/acapella-extractor/align_lyrics.py \
  --audio workspaces/<slug>/<slug>-remix-v1-acapella.mp3 \
  --lyrics workspaces/<slug>/<slug>-suno-lyrics.txt \
  --output workspaces/<slug>/lyrics-timestamps.json \
  --language <iso-639-3-code>
```

Use `tel` for Telugu, `hin` for Hindi, `tam` for Tamil. The script strips section headers and
stage directions automatically, aligns at word level (~20ms resolution), and groups results
back into lyric lines.

---

### 6.4 — Verify Alignment

Print a terminal karaoke preview and confirm timing is correct before proceeding. Run from the **project root**:

```bash
uv run --python tools/acapella-extractor/.venv/bin/python \
  tools/acapella-extractor/verify_lyrics.py \
  workspaces/<slug>/lyrics-timestamps.json
```

Check:
- First vocal line appears within ±500ms of its actual onset
- Chorus lines align within ±1s
- No lines appear during instrumental sections
- Total drift at end < 3s

Do not proceed to Step 7 (cover art) until these pass. If alignment is off, check acapella
quality and re-run `align_lyrics.py`.

---

### 6.5 — Update Metadata

Update `workspaces/<slug>/meta.json` to record the alignment outputs:

```json
{
  "status": { "acapella_aligned": true },
  "outputs": {
    "remix_acapella": "workspaces/<slug>/<slug>-remix-v1-acapella.mp3",
    "lyrics_timestamps": "workspaces/<slug>/lyrics-timestamps.json"
  }
}
```

---

### 6.6 — Confirm Ready for Video

```
Acapella extraction and lyrics alignment complete!

Outputs in workspaces/<slug>/:
   <slug>-remix-v1-acapella.mp3   — Vocals extracted from remix (alignment source)
   lyrics-timestamps.json          — Word+line timestamps (CTC aligned)

Alignment verified: <n> lines synced  |  End drift: <Xs>

Ready to proceed to Step 7: Fetch & Enhance Cover Art.
```

---

## Error Handling

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: acapella_extractor` | Run from project root using the full venv path as shown in step 6.2 |
| Acapella output is WAV | Use the glob pattern `*remix-v1*vocals*.wav` to find the output and convert with ffmpeg as shown in step 6.2 |
| Alignment too far off | Check acapella quality; try `--language` code for a closer MMS checkpoint |
| ffprobe not found | `brew install ffmpeg` |
