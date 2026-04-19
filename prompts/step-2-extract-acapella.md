# Step 2: Extract Acapella using Mel-Band RoFormer (UV Tool)

## Objective

Extract a clean vocals-only acapella track from the downloaded MP3 using the open-source Mel-Band RoFormer model (SOTA for music source separation) via the UV-based acapella-extractor tool.

## Prerequisites

- `${WORKSPACE_DIR}/${SLUG}-original.mp3` exists (produced by Step 1)
- `${WORKSPACE_DIR}/meta.json` exists with the slug
- Tool location: `tools/acapella-extractor/`

## Workspace Path Resolution

Before using any filesystem path in this step:

1. Read `.remix-workspace-root.json` from the repo root.
2. Resolve `WORKSPACE_ROOT` from its `workspaceRoot` field.
3. Resolve `WORKSPACE_DIR` as `<workspaceRoot>/<slug>/`.
4. Use absolute paths under `WORKSPACE_DIR` for filesystem commands.
5. Keep any stored `meta.json.files.*` values root-relative, for example `<slug>/design.json`.

**See also**: [Acapella Extractor Usage](references/acapella-extractor-usage.md) for detailed setup and commands.

---

## Quick Reference

**Command to execute:**
```bash
cd /Users/aira/projects/remix-gpt-coding-agent.flow-improvements && \
PYTHONPATH=tools/acapella-extractor/src \
uv run --python tools/acapella-extractor/.venv/bin/python \
python -m acapella_extractor.extract \
"${WORKSPACE_DIR}/${SLUG}-original.mp3" \
-o "${WORKSPACE_DIR}"
```

**Processing time:** 2-5 minutes  
**Output:** `${WORKSPACE_DIR}/${SLUG}-acapella.mp3`

---

## Instructions

### 2.1 — Verify Tool Setup

**See**: [Acapella Extractor Usage > Prerequisites](references/acapella-extractor-usage.md#prerequisites)

**Bash tool:**
```bash
ls -la tools/acapella-extractor/.venv/bin/python && \
ls -la tools/acapella-extractor/src/acapella_extractor/extract.py
```

**If files don't exist:** Run `cd tools/acapella-extractor && uv sync`

---

### 2.2 — Run Extraction

**See**: [Acapella Extractor Usage > Extraction](references/acapella-extractor-usage.md#extraction-step-2)

Execute the extraction command from Quick Reference above.

**Monitor for this output:**
```
🎵 Acapella Extractor
   Model: Mel-Band RoFormer (SOTA)
   Input: <workspaceRoot>/<slug>/<slug>-original.mp3
   Output: <workspaceRoot>/<slug>/

Loading Mel-Band RoFormer model...
Separating vocals... (this may take a few minutes)
✓ Acapella extracted successfully!
```

---

### 2.3 — Handle Output Format

The tool outputs WAV format that needs conversion to MP3.

**See**: [Acapella Extractor Usage > Convert Output to MP3](references/acapella-extractor-usage.md#convert-output-to-mp3)

**Bash tool:**
```bash
cd "${WORKSPACE_DIR}"
for f in *.wav; do
  if [ -f "$f" ]; then
    ffmpeg -i "$f" -codec:a libmp3lame -b:a 192k "${SLUG}-acapella.mp3"
    rm "$f"
    echo "✓ Converted $f to ${SLUG}-acapella.mp3"
    break
  fi
done
```

---

### 2.4 — Verify Output

**Bash tool:** Confirm the file is valid:

```bash
file "${WORKSPACE_DIR}/${SLUG}-acapella.mp3"
ls -lh "${WORKSPACE_DIR}/${SLUG}-acapella.mp3"
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

📁 Output: <workspaceRoot>/<slug>/<slug>-acapella.mp3
📊 Size: <actual file size>
🎵 Format: MP3, 192kbps, 44.1kHz
🤖 Model: Mel-Band RoFormer (SOTA)

Proceeding to Step 3: Find Lyrics...
```

---

## File Outputs

| File | Path | Description |
|---|---|---|
| Acapella | `<workspaceRoot>/<slug>/<slug>-acapella.mp3` | Clean vocals-only track |
| Metadata | `<workspaceRoot>/<slug>/meta.json` | Updated status |

---

## Error Handling

**See**: [Error Handling Patterns > Acapella Extraction Errors](references/error-handling-patterns.md#acapella-extraction-errors-steps-2-6) and [Acapella Extractor Usage > Troubleshooting](references/acapella-extractor-usage.md#troubleshooting)

| Error | Solution |
|---|---|
| "No module named 'acapella_extractor'" | Add `PYTHONPATH=tools/acapella-extractor/src` |
| "No such file or directory: .venv/bin/python" | Run `cd tools/acapella-extractor && uv sync` |
| Model download hangs | Wait up to 10 minutes (first-time download) |
| Output file missing | Check if WAV was created, run conversion manually |

---

## Reference

- [Acapella Extractor Usage](references/acapella-extractor-usage.md) — Full tool documentation
- [Workspace Conventions](references/workspace-conventions.md) — File naming
- [Error Handling Patterns](references/error-handling-patterns.md) — Common errors
