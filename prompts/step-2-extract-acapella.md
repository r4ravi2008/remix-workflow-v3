# Step 2: Extract Acapella using Mel-Band RoFormer (UV Tool)

## Objective

Extract a clean vocals-only acapella track from the downloaded MP3 using the open-source Mel-Band RoFormer model (SOTA for music source separation) via the UV-based acapella-extractor tool.

## Prerequisites

- `workspaces/<slug>/original.mp3` exists (produced by Step 1)
- `workspaces/<slug>/meta.json` exists with the slug
- Tool location: `tools/acapella-extractor/`

---

## Quick Reference

**Command to execute:**
```bash
cd /Users/aira/projects/remix-gpt-coding-agent && \
PYTHONPATH=tools/acapella-extractor/src \
uv run --python tools/acapella-extractor/.venv/bin/python \
python -m acapella_extractor.extract \
workspaces/<slug>/original.mp3 \
-o workspaces/<slug>/
```

**Processing time:** 2-5 minutes  
**Output:** `workspaces/<slug>/acapella.mp3`

---

## Instructions

### 2.1 — Verify Tool Setup

**Bash tool:** Run this command to verify the tool is ready:

```bash
ls -la tools/acapella-extractor/.venv/bin/python && \
ls -la tools/acapella-extractor/src/acapella_extractor/extract.py
```

**Expected output:** Both files should exist (no "No such file or directory" errors).

**If files don't exist:** The tool needs to be set up first. Contact the user or check the tool README at `tools/acapella-extractor/README.md`.

---

### 2.2 — Run Extraction

**Bash tool:** Execute the extraction (replace `<slug>` with actual slug from meta.json):

```bash
cd /Users/aira/projects/remix-gpt-coding-agent && \
PYTHONPATH=tools/acapella-extractor/src \
uv run --python tools/acapella-extractor/.venv/bin/python \
python -m acapella_extractor.extract \
workspaces/<slug>/original.mp3 \
-o workspaces/<slug>/
```

**What happens:**
1. Loads Mel-Band RoFormer model (downloads once to `tools/acapella-extractor/models/`, ~300MB, cached for all future runs)
2. Processes audio using hardware acceleration (Apple Silicon MPS/CoreML preferred)
3. Extracts vocals-only track
4. Saves output (may be WAV initially)

**Monitor for this output:**
```
🎵 Acapella Extractor
   Model: Mel-Band RoFormer (SOTA)
   Input: workspaces/<slug>/original.mp3
   Output: workspaces/<slug>/

Loading Mel-Band RoFormer model...
Separating vocals... (this may take a few minutes)
✓ Acapella extracted successfully!
```

---

### 2.3 — Handle Output Format

The tool outputs WAV format that needs conversion to MP3.

**Bash tool:** Run this to convert and clean up:

```bash
cd workspaces/<slug>

# Find the vocals WAV file and convert to MP3
for f in *.wav; do
  if [ -f "$f" ]; then
    ffmpeg -i "$f" -codec:a libmp3lame -b:a 192k acapella.mp3
    rm "$f"
    echo "✓ Converted $f to acapella.mp3"
    break
  fi
done

# Check if acapella.mp3 exists
if [ -f "acapella.mp3" ]; then
  echo "✓ Acapella ready: $(ls -lh acapella.mp3)"
else
  echo "❌ Error: acapella.mp3 not found"
  exit 1
fi
```

---

### 2.4 — Verify Output

**Bash tool:** Confirm the file is valid:

```bash
file workspaces/<slug>/acapella.mp3
ls -lh workspaces/<slug>/acapella.mp3
```

**Expected results:**
- File size: 4-8MB (varies by song length)
- Type: `Audio file with ID3... MPEG ADTS, layer III, v1, 192 kbps, 44.1 kHz, Stereo`

**If verification fails:** Check step 2.3 completed successfully.

---

### 2.5 — Update meta.json

**Read tool:** Read current meta.json

**Edit tool:** Update status fields:

```json
{
  "status": {
    "mp3_downloaded": true,
    "acapella_extracted": true
  }
}
```

---

### 2.6 — Complete

**Print summary:**

```
✅ Step 2 Complete: Acapella Extracted

📁 Output: workspaces/<slug>/acapella.mp3
📊 Size: <actual file size>
🎵 Format: MP3, 192kbps, 44.1kHz
🤖 Model: Mel-Band RoFormer (SOTA)

Proceeding to Step 3: Find Lyrics...
```

---

## Troubleshooting

### Error: "No module named 'acapella_extractor'"
**Solution:** Ensure `PYTHONPATH=tools/acapella-extractor/src` is set in the command.

### Error: "uv: command not found"
**Solution:** UV should be available in the environment. Try using the full path or install UV.

### Error: "No such file or directory: .venv/bin/python"
**Solution:** The virtual environment doesn't exist. Run `cd tools/acapella-extractor && uv sync` first.

### Error: Model download hangs
**Solution:** First run downloads ~300MB to `tools/acapella-extractor/models/`. Ensure stable internet. Wait up to 10 minutes. Subsequent runs use the cached model.

### Output file is missing
**Solution:** Check if WAV file was created. Run step 2.3 conversion manually.

### Poor vocal separation
**Solution:** Mel-Band RoFormer is SOTA but results vary. The acapella is usually good enough for CTC forced alignment in Step 6.

---

## File Outputs

| File | Path | Description |
|---|---|---|
| Acapella | `workspaces/<slug>/acapella.mp3` | Clean vocals-only track |
| Metadata | `workspaces/<slug>/meta.json` | Updated status |

---

## Technical Details

**Model:** Mel-Band RoFormer Kim FT Unified  
**Processing:** 256-segment with 0.25 overlap  
**Hardware:** Auto-detects MPS (Apple Silicon) → CUDA → CPU  
**Input:** MP3/WAV (any format)  
**Output:** MP3, 192kbps, 44.1kHz, Stereo
