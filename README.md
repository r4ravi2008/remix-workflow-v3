# Indic Song Remixer

An AI-powered pipeline that automates the end-to-end process of remixing Telugu and other Indic language songs. Give it a YouTube link and a target genre — it produces a fully rendered music video with synced lyrics, audio-reactive visuals, and AI-generated cover art.

## How It Works

```
YouTube URL + Genre (user input)
        |
        v
[Step 0] Prepare Workspace         → meta.json + workspace folder
[Step 1] Download MP3               → yt-dlp extracts audio from YouTube
[Step 2] Extract Acapella           → Mel-Band RoFormer vocal isolation
[Step 3] Find Lyrics                → Browser automation finds native-script lyrics
[Step 4] Generate Suno Lyrics       → Converts to Suno meta-tag format + generates design.json
[Step 5] Upload to Suno             → Creates 2 remix variations on Suno.ai
[Step 5.5] User Selection           → User picks preferred version
[Step 6] Extract & Align Lyrics     → CTC forced alignment for word-level timestamps
[Step 7] Fetch Cover Art            → Stylized with fal.ai (anime aesthetic, 2048x2048)
[Step 8] Generate Video             → Remotion renders audio-reactive music video
[Step 9] Generate YouTube Metadata  → Title, description, tags for upload
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Orchestration** | Claude Code multi-step agent workflow |
| **Audio Separation** | Mel-Band RoFormer (ONNX, SOTA source separation) |
| **Lyrics Alignment** | CTC Forced Aligner (WAV2Vec2, MMS multilingual) |
| **Music Generation** | Suno.ai (via Chrome DevTools MCP automation) |
| **Image Stylization** | fal.ai Nano Banana Pro |
| **Video Rendering** | Remotion (React-based programmatic video) |
| **Audio Tools** | FFmpeg, yt-dlp, PyTorch, TorchAudio |
| **Browser Automation** | Chrome DevTools MCP |

## Project Structure

```
remix-gpt-coding-agent/
├── docs/                              # Architecture and design docs
│   ├── intent.md                      # Pipeline overview and project intent
│   ├── video-visual-system-plan.md    # Video design system documentation
│   └── lyrics-sync-proposal.md        # Lyrics synchronization approach
├── prompts/                           # Step-by-step execution guides
│   ├── step-0-prepare-workspace.md
│   ├── step-1-download-mp3.md
│   ├── step-2-extract-acapella.md
│   ├── step-3-find-lyrics.md
│   ├── step-4-generate-suno-lyrics.md
│   ├── step-5-upload-to-suno.md
│   ├── step-6-extract-acapella-and-align.md
│   ├── step-7-fetch-cover-art.md
│   ├── step-8-generate-video.md
│   └── step-9-generate-youtube-metadata.md
├── tools/
│   ├── acapella-extractor/            # Python: vocal extraction + lyrics alignment
│   │   ├── extract.py                 # Mel-Band RoFormer extraction
│   │   ├── align_lyrics.py            # CTC forced alignment
│   │   ├── verify_lyrics.py           # Alignment quality checks
│   │   └── pyproject.toml             # UV dependencies
│   └── video-generator/               # Remotion video template system
│       ├── init-video.js              # Scaffolds video project from template
│       └── template/                  # Remotion project template
│           └── src/
│               ├── Root.tsx           # Composition config
│               ├── MusicVideo.tsx     # Main audio-reactive component
│               ├── components/        # Visual motifs (6 types)
│               ├── layouts/           # Layout variants (5 types)
│               └── utils/             # Audio processing, design loader
├── .agents/skills/                    # Agent skill definitions
│   ├── suno-music-creator/            # Suno.ai music creation workflows
│   └── video-generation/              # AI video generation capabilities
└── workspaces/                        # Output directory (one folder per remix)
```

## Pipeline Details

### Step 0: Prepare Workspace

Step 0 resolves a machine-local workspace root from `.remix-workspace-root.json`, then creates `<workspaceRoot>/<slug>/` with a `meta.json` tracking all inputs and pipeline state.

### Step 1: Download MP3

Downloads audio from YouTube using `yt-dlp` at best quality.

### Step 2: Extract Acapella

Uses **Mel-Band RoFormer** (current SOTA for music source separation) to isolate vocals. Supports Apple Silicon MPS, CUDA, and CPU backends.

### Step 3: Find Lyrics

Searches for lyrics in native Indic script using browser automation (Chrome DevTools MCP). Lyrics are never romanized — Telugu stays as తెలుగు, Hindi as हिंदी, Tamil as தமிழ்.

### Step 4: Generate Suno Lyrics + Design

Converts raw lyrics to Suno's meta-tag format with section tags (`[Verse]`, `[Chorus]`, `[Bridge]`, etc.). Also generates a `design.json` with visual configuration based on the song's genre and mood — colors, fonts, motifs, and animation personality.

### Step 5: Upload to Suno

Automates Suno.ai through Chrome DevTools MCP: uploads acapella, pastes formatted lyrics and style block, triggers generation, and downloads 2 remix variations. User picks the best one.

### Step 6: Extract & Align Lyrics

Extracts vocals from the chosen remix, then runs **CTC forced alignment** to produce word-level and line-level timestamps (`lyrics-timestamps.json`). Verifies alignment quality: first line within ±500ms, end drift under 3 seconds.

### Step 7: Fetch Cover Art

Finds the song's cover art via browser search, then stylizes it through fal.ai's Nano Banana Pro model at 2048x2048 resolution.

### Step 8: Generate Video

Scaffolds a Remotion project from the template, injects all assets (audio, timestamps, cover art, design config), and renders a 1920x1080 music video at 30fps with:

- **Audio-reactive visuals** driven by real frequency analysis (24 bands, attack/release smoothing)
- **Synced lyrics** with line-level timing and section badges
- **6 visual motifs**: particles, geometric-burst, aurora, waveform-rings, noise-field, frequency-bars
- **5 layout variants**: center-stage, full-bleed, minimal, sidebar, stacked
- **5 animation personalities**: smooth, bouncy, sharp, dreamy, aggressive

### Step 9: Generate YouTube Metadata

Produces a `youtube-metadata.json` with title, description, and tags ready for upload.

## Workspace Output

Each remix session produces a complete workspace:

```
<workspaceRoot>/<slug>/
├── meta.json                    # Session metadata and pipeline status
├── <slug>-original.mp3          # Downloaded from YouTube
├── <slug>-acapella.mp3          # Extracted vocals
├── <slug>-lyrics.txt            # Raw Indic lyrics
├── <slug>-suno-lyrics.txt       # Suno-formatted lyrics
├── <slug>-suno-style.txt        # Style block for Suno
├── design.json                  # AI-generated visual design config
├── <slug>-remix-v1.mp3          # Suno remix variation 1
├── <slug>-remix-v2.mp3          # Suno remix variation 2
├── <slug>-remix-v1-acapella.mp3 # Vocals from remix (for alignment)
├── lyrics-timestamps.json       # CTC-aligned word/line timestamps
├── <slug>-cover-art.jpg         # Stylized album art
├── <slug>-video.mp4             # Final rendered music video
├── youtube-metadata.json        # YouTube upload metadata
└── video/                       # Remotion project files
```

## Prerequisites

- **Python 3.12+** with [UV](https://github.com/astral-sh/uv) package manager
- **Node.js 18+** (for Remotion video rendering)
- **FFmpeg** (audio encoding and conversion)
- **yt-dlp** (YouTube audio download, installed via `uvx`)
- **Google Chrome** (for Chrome DevTools MCP browser automation)
- **Claude Code** (orchestrates the entire pipeline)

## Getting Started

1. Clone the repository
2. Configure the repo-local workspace root:
   ```bash
   cp .remix-workspace-root.example.json .remix-workspace-root.json
   ```
3. Install Python dependencies for the acapella extractor:
   ```bash
   cd tools/acapella-extractor && uv sync
   ```
4. Start a Claude Code session and provide:
   - A YouTube URL of the song to remix
   - A target genre/style (e.g., "Lo-Fi", "EDM", "Hip-Hop", "Carnatic Fusion")
5. The agent walks through each step sequentially, with a user checkpoint at Step 5.5 to select the preferred remix variation

## Supported Languages

Lyrics are preserved in their native script throughout the entire pipeline:

- **Telugu** (తెలుగు)
- **Hindi** (हिंदी)
- **Tamil** (தமிழ்)

Additional Indic languages are supported — the CTC aligner uses the MMS multilingual model. Indic scripts automatically fall back to Noto Sans for video rendering.

## Key Design Decisions

- **Native script only**: Lyrics are never transliterated or romanized
- **CTC alignment**: Timestamps come from forced alignment, not heuristics
- **Per-song design**: Every remix gets unique colors, fonts, and motifs based on its Suno style descriptors
- **Audio-reactive only**: All visuals react to real frequency data from the audio
- **Workspace isolation**: All files for a remix stay together in the configured external workspace root under `<workspaceRoot>/<slug>/`
- **Sequential pipeline**: Each step depends on outputs from earlier steps

## License

MIT
