# Lyrics Synchronization: Research & Proposal

## Problem Statement

We need millisecond-precision synchronization of Indic-language (Telugu) lyrics to the
Suno-generated remix audio for display as a karaoke-style overlay in a Remotion music video.

### Why all previous attempts failed

| Approach | Root cause of failure |
|---|---|
| **Mechanical distribution** | No audio analysis at all. Divides total duration equally across lines. Ignores actual vocal onsets entirely. |
| **Aeneas** | Synthesizes text via espeak TTS, then correlates the TTS waveform to audio using DTW. Designed for audiobooks (clean speech). Completely misled by instruments, beat, reverb. |
| **Whisper / WhisperX** | Transcription model — decodes what it hears. Poor on singing voices, polyphonic music, and non-Latin scripts like Telugu under music. |

**Core insight:** This is not a generic forced-alignment problem. It is **music-specific lyrics
alignment** — matching a known transcript to vocal onsets in a mixed audio signal. The correct
approach requires isolating the vocal track first, then aligning against clean vocals only.

---

## Correct Pipeline

```
workspaces/<slug>/<slug>-remix-v1.mp3   ← Suno-generated remix (full mix)
        │
        ▼
  tools/acapella-extractor/             ← Mel-Band RoFormer SOTA vocal isolation
        │
        ▼
  workspaces/<slug>/remix-v1-acapella.mp3   ← Clean vocals from remix
        │
        ▼
  tools/lyrics-aligner/align.py         ← ctc-forced-aligner (MMS/Wav2Vec2, Telugu)
   + workspaces/<slug>/suno-lyrics.txt  ← Known transcript (section-tagged lyrics)
        │
        ▼
  workspaces/<slug>/lyrics-timestamps.json   ← Word+line level timestamps (ms precision)
        │
        ▼
  workspaces/<slug>/video/public/            ← Copied into Remotion project
        │
        ▼
  bella-bella-lofi-video.mp4                 ← Final rendered video
```

**Key distinction from Step 2:** Step 2 extracts acapella from the *original YouTube download*
for upload to Suno. This new step extracts acapella from the *Suno remix output* specifically
for alignment — different audio, same tool.

---

## Why Acapella Extraction First

Feeding a full mix (vocals + instruments + beat + bass) into any alignment tool produces poor
results because:
- Beat transients are louder than vocal onsets
- Reverb blurs phoneme boundaries
- Instruments produce spectral content in the same frequency range as voice

The Zalo AI Challenge 2022 winners (lyrics alignment task) confirmed this: their winning
pipeline was **Demucs vocal separation → Wav2Vec2 CTC alignment**. We use the same principle
with our Mel-Band RoFormer (higher quality than Demucs).

---

## Recommended Alignment Tool: `ctc-forced-aligner`

**Repository:** https://github.com/MahmoudAshraf97/ctc-forced-aligner  
**Stars:** 468 · **Last update:** Feb 2026 · **License:** BSD

### How it works

Uses Meta's **MMS (Massively Multilingual Speech)** Wav2Vec2 model with CTC (Connectionist
Temporal Classification) forced alignment. Given:
- An audio file (our acapella)
- A known text transcript (our lyrics)

It runs the audio through the neural network to get frame-level CTC emissions (~20ms frames),
then uses dynamic programming to find the optimal monotonic alignment path — no transcription,
no guessing, guaranteed to match the input text.

### Why it fits our use case

| Requirement | ctc-forced-aligner |
|---|---|
| Telugu support | ✅ via `tel` ISO 639-3 code, MMS model covers 1130+ languages |
| Precision | ✅ ~20ms frame resolution (50 frames/sec) |
| Known transcript input | ✅ Forced alignment — uses our lyrics, not guessing |
| Polyphonic music | ✅ With acapella extraction first |
| pip installable | ✅ `pip install ctc-forced-aligner` |
| Output format | ✅ JSON with word-level `start`/`end` timestamps |
| Active maintenance | ✅ Feb 2026 |

### Output format

```json
{
  "text": "బార్సిలోనా బేబీ మార్స్ నుండి మే బీ ...",
  "segments": [
    { "start": 18.020, "end": 18.800, "text": "బార్సిలోనా" },
    { "start": 18.820, "end": 19.100, "text": "బేబీ" },
    { "start": 19.400, "end": 20.100, "text": "మార్స్" }
  ]
}
```

---

## Implementation Plan

### Step 1: Extract acapella from remix

Use the existing `tools/acapella-extractor/` — same tool, different input file.

```bash
cd tools/acapella-extractor
uv run python -m acapella_extractor.extract \
  ../../workspaces/<slug>/<slug>-remix-v1.mp3 \
  --output-dir ../../workspaces/<slug>/
# Renames output to: workspaces/<slug>/remix-v1-acapella.mp3
```

The `extract.py` currently always outputs `acapella.mp3`. We need a small change to support
a custom output filename — or just rename after the fact:

```bash
mv workspaces/<slug>/acapella.mp3 workspaces/<slug>/remix-v1-acapella.mp3
```

### Step 2: Install `ctc-forced-aligner` alongside acapella-extractor

Add to `tools/acapella-extractor/pyproject.toml`:

```toml
dependencies = [
    "audio-separator>=0.44.1",
    "demucs>=4.0.1",
    "onnxruntime>=1.24.4",
    "torch>=2.11.0",
    "torchaudio>=2.11.0",
    "ctc-forced-aligner>=0.2",   # ← add this
]
```

Both tools share torch/torchaudio — single venv, no duplication.

### Step 3: Write `tools/acapella-extractor/align_lyrics.py`

New script — clean, purpose-built:

**Inputs:**
- `--audio` — path to remix acapella (`remix-v1-acapella.mp3`)
- `--lyrics` — path to `suno-lyrics.txt` (section-tagged)
- `--output` — path for `lyrics-timestamps.json`
- `--language` — ISO 639-3 code (default: `tel` for Telugu)

**Processing:**
1. Parse `suno-lyrics.txt` — strip `[Section]` markers, build line list + section map
2. Write plain text file of just the lyric lines (ctc-forced-aligner input format)
3. Run ctc-forced-aligner at word level → get word timestamps
4. Group word timestamps back into lines (by matching words to original line text)
5. Reconstruct section boundaries from line groups
6. Write `lyrics-timestamps.json`

**Output schema** (backward compatible, adds `words` array per line):

```json
{
  "audio_duration": 223.16,
  "sections": [
    {
      "name": "Verse 1",
      "start_time": 18.020,
      "end_time": 57.800,
      "lines": ["బార్సిలోనా బేబీ", "మార్స్ నుండి మే బీ"]
    }
  ],
  "lyrics": [
    {
      "text": "బార్సిలోనా బేబీ",
      "start_time": 18.020,
      "end_time": 20.900,
      "section": "Verse 1",
      "words": [
        { "text": "బార్సిలోనా", "start_time": 18.020, "end_time": 18.800 },
        { "text": "బేబీ",       "start_time": 18.820, "end_time": 19.100 }
      ]
    }
  ]
}
```

### Step 4: Write `tools/acapella-extractor/verify_lyrics.py`

**Purpose:** Print a terminal karaoke preview before committing to a full Remotion render.
This breaks the painful cycle of: align → 2-min render → wrong → repeat.

```
$ uv run python verify_lyrics.py ../../workspaces/bella-bella-lofi/lyrics-timestamps.json

[00:00.000]  (instrumental intro)
[00:18.020]  బార్సిలోనా బేబీ
[00:20.900]  మార్స్ నుండి మే బీ
[00:23.400]  పుట్టుకొచ్చిందో
...
```

Play the audio alongside — if lines appear when they're sung, alignment is correct.

### Step 5: Update `prompts/step-6-generate-video.md`

Replace sections 6.3–6.4 with:

```
6.3 — Extract acapella from remix audio (acapella-extractor)
6.4 — Verify acapella quality (optional listen)
6.5 — Generate lyrics timestamps (align_lyrics.py)
6.6 — Verify alignment (verify_lyrics.py) ← NEW QA GATE
6.7 — Scaffold Remotion project
...
```

---

## File Changes Summary

### New files to create

```
tools/acapella-extractor/
├── align_lyrics.py       ← ctc-forced-aligner wrapper + JSON output
└── verify_lyrics.py      ← terminal karaoke QA preview
```

### Modified files

```
tools/acapella-extractor/pyproject.toml   ← add ctc-forced-aligner dependency
prompts/step-6-generate-video.md          ← update steps 6.3–6.6
docs/intent.md                            ← note remix acapella step
```

### No new tool directories needed

Everything lives in `tools/acapella-extractor/` — both extraction and alignment share
the same Python venv (torch/torchaudio already there).

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| MMS model struggles with Telugu *singing* (trained on speech) | Medium | Test on acapella; if alignment drifts, try `--romanize` flag off; fall back to AutoLyrixAlign |
| Python version mismatch (ctc-forced-aligner requires 3.9–3.13, extractor uses 3.12) | None | Already on 3.12 per `.python-version` |
| Model download size (~300MB for MMS) | Low | One-time, cached by HuggingFace in `~/.cache/huggingface/` |
| Remix acapella extraction takes several minutes | Expected | Same as Step 2; no mitigation needed |
| `--romanize` needed for non-Latin scripts may reduce precision | Medium | Test both; Telugu has its own MMS checkpoint `mms-300m-1130-forced-aligner` |

---

## Validation Criteria

Alignment is considered correct when:

1. `verify_lyrics.py` output shows first vocal line within ±500ms of its actual onset
2. Chorus lines align within ±1s of their actual position
3. No lines appear during instrumental sections
4. Total drift at end of song is < 3s

Once these pass visually, proceed to Remotion render.

---

## Decision

**Approved approach:**
1. `tools/acapella-extractor/` extracts vocals from `<slug>-remix-v1.mp3`
2. `ctc-forced-aligner` (added to same venv) aligns extracted vocals to known lyrics
3. Verification before rendering eliminates wasted render cycles

Awaiting approval to implement `align_lyrics.py` and `verify_lyrics.py`.
