# Acapella Extractor Usage

Guide for using the `acapella-extractor` tool for vocal isolation and lyrics alignment.

## Tool Location

```
tools/acapella-extractor/
├── README.md
├── src/acapella_extractor/
│   ├── extract.py          ← Main extraction script
│   └── ...
├── align_lyrics.py         ← CTC forced alignment
├── verify_lyrics.py        ← Alignment verification
└── .venv/                  ← UV-managed virtual environment
```

## Prerequisites

- Python virtual environment set up at `tools/acapella-extractor/.venv/`
- Model weights cached at `tools/acapella-extractor/models/` (~300MB, auto-downloaded)

### Verify Setup

```bash
ls -la tools/acapella-extractor/.venv/bin/python
ls -la tools/acapella-extractor/src/acapella_extractor/extract.py
```

If files don't exist, run:
```bash
cd tools/acapella-extractor && uv sync
```

## Extraction (Step 2)

Extract vocals from the original YouTube download.

### Command

```bash
PYTHONPATH=tools/acapella-extractor/src \
uv run --python tools/acapella-extractor/.venv/bin/python \
python -m acapella_extractor.extract \
"${WORKSPACE_DIR}/${SLUG}-original.mp3" \
-o "${WORKSPACE_DIR}"
```

### What Happens

1. Loads Mel-Band RoFormer model (SOTA for music source separation)
2. Processes audio using hardware acceleration (MPS on Apple Silicon, CUDA on NVIDIA, CPU fallback)
3. Extracts vocals-only track
4. Outputs WAV file

### Processing Time

- 2–5 minutes for a typical 3–4 minute song
- First run downloads ~300MB model weights (cached for future runs)

### Convert Output to MP3

The tool outputs WAV that needs conversion:

```bash
cd "${WORKSPACE_DIR}"
for f in *.wav; do
  if [ -f "$f" ]; then
    ffmpeg -i "$f" -codec:a libmp3lame -b:a 192k "${SLUG}-acapella.mp3"
    rm "$f"
    break
  fi
done
```

### Verify Output

```bash
file "${WORKSPACE_DIR}/${SLUG}-acapella.mp3"
ls -lh "${WORKSPACE_DIR}/${SLUG}-acapella.mp3"
```

Expected: `Audio file with ID3... MPEG ADTS, layer III, v1, 192 kbps, 44.1 kHz, Stereo`

## Extraction from Remix (Step 6)

Extract vocals from the Suno remix for CTC alignment.

### Command

```bash
PYTHONPATH=tools/acapella-extractor/src \
uv run --python tools/acapella-extractor/.venv/bin/python \
python -m acapella_extractor.extract \
"${WORKSPACE_DIR}/${SLUG}-remix-v1.mp3" \
-o "${WORKSPACE_DIR}"
```

### Convert and Rename

```bash
WAV=$(ls "${WORKSPACE_DIR}"/*remix-v1*vocals*.wav 2>/dev/null | head -1)
ffmpeg -i "$WAV" -codec:a libmp3lame -q:a 2 \
  "${WORKSPACE_DIR}/${SLUG}-remix-v1-acapella.mp3"
rm "$WAV"
```

## CTC Forced Alignment (Step 6)

Generate precise word- and line-level timestamps using wav2vec 2.0/MMS CTC model.

### Command

```bash
PYTHONPATH=tools/acapella-extractor/src \
uv run --python tools/acapella-extractor/.venv/bin/python \
tools/acapella-extractor/align_lyrics.py \
--audio "${WORKSPACE_DIR}/${SLUG}-remix-v1-acapella.mp3" \
--lyrics "${WORKSPACE_DIR}/${SLUG}-suno-lyrics.txt" \
--output "${WORKSPACE_DIR}/lyrics-timestamps.json" \
--language <iso-639-3-code>
```

### Language Codes

| Language | ISO 639-3 |
|----------|-----------|
| Telugu | `tel` |
| Hindi | `hin` |
| Tamil | `tam` |

### What Happens

1. Loads MMS wav2vec 2.0 CTC checkpoint
2. Runs CTC forced alignment at ~20ms word-level resolution
3. Groups words back into lyric lines
4. Outputs JSON with timestamps

### Alignment Output Format

```json
{
  "lines": [
    {
      "text": "మల్లె తీగరోయ్ మనసే లాగుతోందిరోయ్",
      "start_time": 12.34,
      "end_time": 16.78,
      "words": [
        {"word": "మల్లె", "start": 12.34, "end": 13.10},
        {"word": "తీగరోయ్", "start": 13.15, "end": 14.50},
        ...
      ]
    }
  ]
}
```

## Alignment Verification (Step 6)

Verify timing quality before proceeding to video generation.

### Command

```bash
PYTHONPATH=tools/acapella-extractor/src \
uv run --python tools/acapella-extractor/.venv/bin/python \
tools/acapella-extractor/verify_lyrics.py \
"${WORKSPACE_DIR}/lyrics-timestamps.json"
```

### Quality Checks

| Check | Tolerance | Action if Failed |
|-------|-----------|------------------|
| First vocal onset | ±500ms of actual | Check acapella quality |
| Chorus alignment | ±1s | Re-run alignment |
| Instrumental gaps | No lyrics during instruments | Check section labels |
| End drift | < 3s total | Verify full song extracted |

## Technical Details

### Model: Mel-Band RoFormer

- **Variant**: Kim FT Unified
- **Processing**: 256-segment with 0.25 overlap
- **Hardware**: Auto-detects MPS → CUDA → CPU
- **Input**: Any audio format (MP3, WAV, etc.)
- **Output**: Vocals-only track

### Model: MMS wav2vec 2.0

- **Purpose**: CTC forced alignment for Indic languages
- **Resolution**: ~20ms at word level
- **Languages**: Supports 1000+ languages including Telugu, Hindi, Tamil
- **Output**: Word and line timestamps in seconds

### Hardware Acceleration

| Platform | Detection | Performance |
|----------|-----------|-------------|
| Apple Silicon (M1/M2/M3) | MPS | ~2-3 min/song |
| NVIDIA GPU | CUDA | ~2-3 min/song |
| CPU | Fallback | ~5-8 min/song |

## Troubleshooting

### "No module named 'acapella_extractor'"

**Cause**: PYTHONPATH not set
**Fix**: Ensure `PYTHONPATH=tools/acapella-extractor/src` is in the command

### "No such file or directory: .venv/bin/python"

**Cause**: Virtual environment not set up
**Fix**: Run `cd tools/acapella-extractor && uv sync`

### Model download hangs

**Cause**: First-time download of ~300MB weights
**Fix**: Wait up to 10 minutes, ensure stable internet. Subsequent runs use cache.

### Poor vocal separation

**Cause**: Complex instrumentation or backing vocals
**Fix**: Results vary by song. Usually sufficient for CTC alignment even if not perfect.

### Alignment too far off

**Cause**: Wrong language code or poor acapella quality
**Fix**: 
1. Verify correct ISO 639-3 code
2. Check acapella extraction quality
3. Re-run extraction if audio is corrupted
4. Try `--language` code for a closer MMS checkpoint variant

### ffprobe not found

**Cause**: FFmpeg not installed
**Fix**: `brew install ffmpeg` (macOS) or install via package manager
