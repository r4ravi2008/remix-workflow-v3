# Video Generator

Remotion-based video generation for music remixes with genre-specific visual themes.

## Structure

```
tools/video-generator/
├── README.md
├── init-video.js       # CLI to scaffold videos with themes
├── template/           # Base Remotion project template
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── index.tsx
│       ├── Root.tsx         # Composition config
│       └── MusicVideo.tsx   # Main video component with themes
└── shared-components/  # (wip) Reusable visual components
```

## Available Themes

| Theme | Best For | Colors | Style |
|-------|----------|--------|-------|
| `lofi` | Lo-Fi, Chillhop | Dark grays, soft blues | Smooth, nostalgic |
| `chill` | Tropical, Downtempo | Pastel greens, pinks | Gentle, relaxed |
| `edm` | Electronic, House | Black, electric cyan | Energetic, futuristic |
| `hiphop` | Hip-Hop, Rap | Dark grays, orange | Urban, bold |
| `carnatic` | Indian Classical | Golds, earth tones | Traditional, elegant |
| `pop` | Pop, Top 40 | Rainbow gradients | Bright, modern |
| `default` | Any | Navy, soft blue | Clean, versatile |

## Usage

### Quick Start (Manual)

```bash
# Create video project for a workspace
cd tools/video-generator
node init-video.js <workspace-slug> --theme=<theme>

# Example:
node init-video.js akasam-lofi-tropical-chill --theme=lofi
```

### Integrated Workflow (Step 6)

This is automatically called as part of the remix pipeline:

```bash
# After user selects v1 or v2 in Step 5.5
cd tools/video-generator
node init-video.js <slug> --theme=<auto-detected-from-genre>

# Then in the workspace video folder:
cd workspaces/<slug>/video
cp ../<slug>-remix-v1.mp3 public/audio.mp3  # Or v2
npm install
npm run build    # Renders video.mp4
mv out/video.mp4 ../<slug>-video.mp4
```

## Development

### Preview Video

```bash
cd workspaces/<slug>/video
npm run dev      # Opens Remotion Studio at http://localhost:3000
```

### Customize Theme

Edit `src/MusicVideo.tsx` in the scaffolded project:
- Change `background` gradient
- Adjust `primaryColor` (text) and `accentColor` (highlights)
- Modify animations based on `animationStyle`

### Add Lyrics Display

The lyrics file is copied to `public/lyrics.txt`. To display them:

```typescript
// In MusicVideo.tsx
import { useEffect, useState } from 'react';

const [lyrics, setLyrics] = useState('');

useEffect(() => {
  fetch(staticFile('lyrics.txt'))
    .then(r => r.text())
    .then(setLyrics);
}, []);
```

## Project Structure (After Scaffold)

```
workspaces/<slug>/video/
├── package.json
├── tsconfig.json
├── remotion.config.ts
├── src/
│   ├── index.tsx
│   ├── Root.tsx
│   └── MusicVideo.tsx
└── public/
    ├── audio.mp3        # Selected remix audio
    ├── lyrics.txt       # Original lyrics
    ├── suno-lyrics.txt  # Suno-formatted lyrics
    └── theme.json       # Theme configuration
```

## Rendering

```bash
npm run build MusicVideo out/video.mp4
```

Options:
- `--codec=h264` (default) or `--codec=h265` for smaller files
- `--quality=high` for better quality (slower)

## Future Enhancements

- [ ] AI-generated cover art based on genre
- [ ] Real audio-reactive visualizers
- [ ] Lyrics sync with audio timestamps
- [ ] Transition effects between sections
- [ ] Custom font loading per theme
