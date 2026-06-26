# Acapella Extractor

Extract clean acapella (vocals-only) tracks from audio files using **Mel-Band RoFormer** — the current SOTA (state-of-the-art) model for music source separation.

This tool is part of the [Indic Song Remixer](../../docs/intent.md) project, which automates the process of remixing Telugu and other Indic language songs using AI.

## Features

- 🎯 **SOTA Quality**: Uses Mel-Band RoFormer Kim FT Unified model (current #1 on music source separation benchmarks)
- 🚀 **Hardware Acceleration**: Automatic Apple Silicon MPS/CoreML, CUDA, and CPU fallback
- 🎵 **High Quality**: 256-segment processing with optimal overlap
- 💾 **Standardized Output**: Generates `acapella.mp3` ready for Suno.ai
- 🔧 **UV Integration**: Built with modern Python packaging (UV) for fast dependency resolution
- 🎤 **Telugu Optimized**: Tested and optimized for Telugu/Indic vocal extraction

## Installation

### Prerequisites

- Python 3.12+
- [UV](https://github.com/astral-sh/uv) package manager
- FFmpeg (for MP3 conversion)

### Setup

```bash
cd tools/acapella-extractor

# Install dependencies using UV
uv sync

# Or using pip (not recommended)
pip install -e .
```

The first run will automatically download the Mel-Band RoFormer model (~300MB).

## Usage

### Command Line

```bash
# From the project root
cd /path/to/project

# Basic usage
PYTHONPATH=tools/acapella-extractor/src \
  uv run --python tools/acapella-extractor/.venv/bin/python \
  python -m acapella_extractor.extract \
  input.mp3 -o ./output

# Using the CLI script (after installation)
acapella-extract input.mp3 --output-dir ./output --model mel_band_roformer_kim_ft_unwa.ckpt
```

### Prepare Acapella for Remix Generation

After extracting vocals, prepare the Step-5 upload/cover input by detecting BPM/key from the original full mix and rendering a deterministic prepped acapella:

```bash
PYTHONPATH=tools/acapella-extractor/src \
  uv run --python tools/acapella-extractor/.venv/bin/python \
  python -m acapella_extractor.prepare \
  --workspace-dir /path/to/workspace/slug \
  --slug slug
```

Optional controls:

```bash
--target-bpm 92
--pitch-semitones -2
```

Outputs:
- `<slug>-acapella-prepped.mp3`
- `<slug>-acapella-prep.json`

If no target BPM is supplied, the detected original BPM is used and pitch is preserved.

### Python API

```python
from acapella_extractor import extract_vocals

# Extract vocals
extract_vocals(
    input_path="song.mp3",
    output_dir="./output",
    model_name="mel_band_roformer_kim_ft_unwa.ckpt"
)

# Returns: Path to acapella.mp3
```

## Model Details

**Mel-Band RoFormer** (Kim FT Unified)
- **Architecture**: RoFormer with mel-frequency band processing
- **Training**: Fine-tuned on unified datasets (MDX, MUSDB18, DnR)
- **Performance**: Current SOTA on all major music separation benchmarks
- **Model File**: `mel_band_roformer_kim_ft_unwa.ckpt`
- **Output Format**: WAV (44.1kHz, stereo) → converted to MP3 (192kbps)

### Processing Parameters

- **Hop Length**: 1024
- **Segment Size**: 256  
- **Overlap**: 0.25
- **Batch Size**: 1

## Output

The tool produces:
- `acapella.mp3` - Clean vocals-only track (192kbps, 44.1kHz, Stereo)
- `<slug>-acapella-prepped.mp3` - Step-5-ready tempo/pitch-prepped vocal reference
- `<slug>-acapella-prep.json` - BPM/key/pitch preparation report
- Temporary model files cached in `.models/` directory

## Project Structure

```
tools/acapella-extractor/
├── src/acapella_extractor/
│   ├── __init__.py          # Package exports
│   └── extract.py           # Main extraction logic
├── .venv/                   # UV virtual environment
├── .models/                 # Cached model files (auto-created)
├── pyproject.toml           # UV project configuration
├── README.md               # This file
└── uv.lock                 # Dependency lock file
```

## Dependencies

- `audio-separator>=0.44.1` - Main separation library
- `torch>=2.11.0` - PyTorch backend
- `torchaudio>=2.11.0` - Audio processing
- `onnxruntime` - ONNX runtime for model inference

## Hardware Support

| Platform | Acceleration | Status |
|----------|---------------|---------|
| Apple Silicon (M1/M2/M3) | MPS/CoreML | ✅ Recommended |
| NVIDIA GPU | CUDA | ✅ Supported |
| CPU | - | ✅ Fallback (slower) |

## Integration with Indic Song Remixer

This tool is Step 2 in the remix pipeline:

```
Step 1: Download MP3 from YouTube
    ↓
Step 2: Extract Acapella (THIS TOOL) → acapella.mp3
    ↓
Step 2.5: Prepare Acapella BPM/Pitch → <slug>-acapella-prepped.mp3
    ↓
Step 3: Find Lyrics
    ↓
Step 4: Generate Suno Lyrics
    ↓
Step 5: Generate Remix on Suno.ai
```

See the [project documentation](../../docs/intent.md) for full pipeline details.

## Troubleshooting

### Model Download Fails
- Ensure stable internet connection
- First run downloads ~300MB model file
- Models are cached in `.models/` directory

### Out of Memory
- Close other applications
- Reduce batch size in model config (edit `extract.py`)
- For very long songs, consider splitting first

### Poor Separation Quality
- Mel-Band RoFormer is SOTA, but results vary by song
- Ensure input audio is high quality
- Check that vocals are clearly audible in original

### "Module not found" errors
- Ensure `PYTHONPATH` includes `tools/acapella-extractor/src`
- Or run from the project root directory

## License

MIT

## Credits

- **Mel-Band RoFormer**: Developed by the audio separation research community
- **audio-separator**: Python wrapper library
- **Indic Song Remixer**: Part of the broader AI music remixing project
