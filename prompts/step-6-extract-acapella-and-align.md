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

**See also**: [Acapella Extractor Usage](references/acapella-extractor-usage.md) — Detailed tool documentation.

---

## Instructions

### 6.1 — Read Workspace Files

Read `meta.json` and extract: `video_title`, `genre`, `language`, `slug`.

---

### 6.2 — Extract Acapella from Remix Audio

**See**: [Acapella Extractor Usage > Extraction from Remix](references/acapella-extractor-usage.md#extraction-from-remix-step-6)

Run the acapella extractor on the remix (not the original) to get clean vocals for alignment. All commands run from the **project root**:

```bash
cd /Users/aira/projects/remix-gpt-coding-agent.flow-improvements && \
PYTHONPATH=tools/acapella-extractor/src \
uv run --python tools/acapella-extractor/.venv/bin/python \
python -m acapella_extractor.extract \
workspaces/<slug>/<slug>-remix-v1.mp3 \
-o workspaces/<slug>/
```

The extractor outputs WAV — convert to MP3:

```bash
WAV=$(ls workspaces/<slug>/*remix-v1*vocals*.wav 2>/dev/null | head -1)
ffmpeg -i "$WAV" -codec:a libmp3lame -q:a 2 \
  "workspaces/<slug>/<slug>-remix-v1-acapella.mp3"
rm "$WAV"
```

Output: `workspaces/<slug>/<slug>-remix-v1-acapella.mp3`

---

### 6.3 — Generate Lyrics Timestamps

**See**: [Acapella Extractor Usage > CTC Forced Alignment](references/acapella-extractor-usage.md#ctc-forced-alignment-step-6)

Run the CTC forced aligner against the acapella. All commands run from the **project root**:

```bash
cd /Users/aira/projects/remix-gpt-coding-agent.flow-improvements && \
PYTHONPATH=tools/acapella-extractor/src \
uv run --python tools/acapella-extractor/.venv/bin/python \
tools/acapella-extractor/align_lyrics.py \
--audio workspaces/<slug>/<slug>-remix-v1-acapella.mp3 \
--lyrics workspaces/<slug>/<slug>-suno-lyrics.txt \
--output workspaces/<slug>/lyrics-timestamps.json \
--language <iso-639-3-code>
```

**Language codes**: `tel` (Telugu), `hin` (Hindi), `tam` (Tamil)

The script strips section headers, aligns at ~20ms word-level resolution, and groups back into lines.

---

### 6.4 — Verify Alignment

**See**: [Acapella Extractor Usage > Alignment Verification](references/acapella-extractor-usage.md#alignment-verification-step-6)

Print a terminal karaoke preview:

```bash
cd /Users/aira/projects/remix-gpt-coding-agent.flow-improvements && \
PYTHONPATH=tools/acapella-extractor/src \
uv run --python tools/acapella-extractor/.venv/bin/python \
tools/acapella-extractor/verify_lyrics.py \
workspaces/<slug>/lyrics-timestamps.json
```

**Quality checks**:
- First vocal within ±500ms of actual onset
- Chorus lines within ±1s
- No lines during instrumental sections
- Total end drift < 3s

**Do not proceed to Step 7 until these pass.**

---

### 6.5 — Update Metadata

Update `workspaces/<slug>/meta.json` to record the alignment outputs:

```json
{
  "status": { "acapella_aligned": true },
  "files": {
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

**See**: [Error Handling Patterns > Alignment Errors](references/error-handling-patterns.md#alignment-errors-step-6) and [Acapella Extractor Usage > Troubleshooting](references/acapella-extractor-usage.md#troubleshooting)

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: acapella_extractor` | Ensure `PYTHONPATH` and full venv path are set |
| Acapella output is WAV | Use glob pattern `*remix-v1*vocals*.wav` to find and convert |
| Alignment too far off | Check acapella quality; verify language code |
| ffprobe not found | `brew install ffmpeg` |

---

## Reference

- [Acapella Extractor Usage](references/acapella-extractor-usage.md) — Full tool documentation
- [Workspace Conventions](references/workspace-conventions.md) — File naming
- [Error Handling Patterns](references/error-handling-patterns.md) — Common errors
