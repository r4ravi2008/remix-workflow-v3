# Error Handling Patterns

Common errors across the Indic Song Remixer pipeline and their fixes.

## File System Errors

### Permission Denied

**Symptom**: `Permission denied: <workspaceRoot>/<slug>/`

**Fixes**:
1. Check that `.remix-workspace-root.json` exists and points to a valid directory.
2. Check write permissions on the configured root: `ls -ld "<workspaceRoot>"`
3. Create the resolved workspace directory explicitly: `mkdir -p "<workspaceRoot>/<slug>"`

### Disk Space

**Symptom**: `No space left on device` or 0-byte files

**Fixes**:
1. Check available space: `df -h`
2. Clean old workspaces: `rm -rf workspaces/old-slug/`
3. Each workspace uses ~500MB (MP3s, video, images)

### File Not Found

**Symptom**: `File not found: <filename>`

**Fixes**:
1. Verify file was created in previous step
2. Check meta.json status fields
3. Re-run previous step if status is false
4. Check for typos in filename (use slug from meta.json)

## YouTube Download Errors (Step 1)

### 403/401 Forbidden

**Symptom**: `HTTP Error 403: Forbidden`

**Causes**: Age-restricted video or requires authentication

**Fixes**:
```bash
# Try with browser cookies
uvx yt-dlp --cookies-from-browser chrome -x --audio-format mp3 ...

# Or Safari
uvx yt-dlp --cookies-from-browser safari -x --audio-format mp3 ...
```

### No Audio Formats Available

**Symptom**: `ERROR: No audio formats available`

**Fixes**:
1. Try without `-x` flag to get video with audio
2. Convert after download: `ffmpeg -i video.mp4 -vn -acodec libmp3lame audio.mp3`

### URL Invalid

**Symptom**: `ERROR: Unable to extract video data`

**Fixes**:
1. Verify URL is publicly accessible
2. Check URL format: `https://www.youtube.com/watch?v=VIDEO_ID`
3. Try opening URL in browser

## Acapella Extraction Errors (Steps 2, 6)

### Module Not Found

**Symptom**: `ModuleNotFoundError: No module named 'acapella_extractor'`

**Fix**: Ensure PYTHONPATH is set correctly:
```bash
PYTHONPATH=tools/acapella-extractor/src uv run --python ...
```

### Virtual Environment Missing

**Symptom**: `No such file or directory: .venv/bin/python`

**Fix**: Set up the environment:
```bash
cd tools/acapella-extractor && uv sync
```

### Model Download Hangs

**Symptom**: Stuck at "Loading Mel-Band RoFormer model..."

**Fixes**:
1. Wait up to 10 minutes (first-time ~300MB download)
2. Check internet connection
3. Subsequent runs use cached model

### Poor Vocal Separation

**Symptom**: Acapella still has backing music or sounds distorted

**Context**: This is normal for some songs with dense instrumentation

**Fixes**:
1. Results vary — usually sufficient for CTC alignment
2. For critical use, try alternative source separation tools

## Browser Automation Errors (Steps 3, 5, 7)

### Page Won't Load

**Symptom**: Snapshot shows blank or error page

**Fixes**:
1. Try reloading: Navigate to same URL again
2. Check network connection
3. Verify URL is valid
4. Some sites block automation — try alternative sources

### Element Not Found

**Symptom**: Can't find button/link in snapshot

**Fixes**:
1. Take fresh snapshot — page may have loaded async content
2. Check exact text (case-sensitive)
3. Try alternative selectors (aria-label vs visible text)
4. Wait for content: `wait_for` with longer timeout

### JavaScript Execution Failed

**Symptom**: `evaluate_script` returns null or errors

**Fixes**:
1. Check script syntax
2. Verify page fully loaded
3. Check browser console for CSP errors
4. Try simpler selectors

### Suno Upload Issues

**Symptom**: Acapella not appearing in Suno library

**Fixes**:
1. Ensure workspace was created first (Step 5.1)
2. Check file uploaded: Look for filename in audio section
3. Try "Remix" → "Library" to find uploaded file
4. If copyright detected, pitch-shift the acapella (see Step 5)

## Lyrics Errors (Step 3)

### No Indic Script Found

**Symptom**: All search results show romanized lyrics

**Fixes**:
1. Try alternative queries:
   - `<song name> <language> పాట సాహిత్యం` (Telugu for "song lyrics")
   - `<song name> lyrics <movie name>`
2. Try multiple sources: lyricstape.com, lyricsted.com, lyricsmint.com
3. Search YouTube comments for lyrics

### Lyrics Page Won't Load

**Symptom**: Site requires heavy JavaScript, won't render

**Fixes**:
1. Take screenshot to visually read lyrics
2. Try alternative lyrics sites
3. Manually transcribe if needed

### Partial Lyrics

**Symptom**: Only first verse or chorus found

**Fix**: Note missing sections in file header:
```
# [Verse 2 missing from source]
```

## Suno Generation Errors (Steps 4, 5)

### Style Block Too Long

**Symptom**: Suno rejects style with "too long" error

**Fix**: Trim to essentials:
```
[<genre>, <mood>, <language>, <vocal type>, <bpm>]
```

### Lyrics Too Long

**Symptom**: Suno processes only part of lyrics

**Fix**: For shortened versions, trim to:
`Intro → Chorus → Verse 1 → Chorus → Bridge → Outro`

### Copyright Detection (Step 5)

**Symptom**: Suno rejects upload as "copyrighted work"

**Fix**: Pitch-shift the acapella:
```bash
ffmpeg -i input.mp3 -af "rubberband=pitch=0.8909" -codec:a libmp3lame -b:a 192k output.mp3
```
This shifts down 2 semitones while preserving tempo.

## Alignment Errors (Step 6)

### Alignment Off by Seconds

**Symptom**: Lyrics don't sync with audio

**Fixes**:
1. Check correct language code (tel/hin/tam)
2. Verify acapella quality — re-extract if distorted
3. Check for wrong song lyrics in file
4. Try `--language` variant codes

### CTC Model Not Found

**Symptom**: `model not found for language <code>`

**Fix**: Use correct ISO 639-3 codes:
- Telugu: `tel`
- Hindi: `hin`
- Tamil: `tam`

### ffprobe Not Found

**Symptom**: `ffprobe not found` during alignment

**Fix**: Install FFmpeg:
```bash
brew install ffmpeg  # macOS
sudo apt-get install ffmpeg  # Ubuntu/Debian
```

## Video Generation Errors (Step 8)

### Remotion Not Installed

**Symptom**: `remotion: command not found`

**Fix**: Install in video-generator directory:
```bash
cd tools/video-generator/template && npm install
```

### Design.json Missing

**Symptom**: `Error: design.json not found`

**Fix**: Verify Step 4 completed — it generates design.json from Suno style

### Cover Art Missing

**Symptom**: Video generation fails without cover art

**Fix**: Verify Step 7 completed and file exists:
```bash
ls "<workspaceRoot>/<slug>/<slug>-cover-art.jpg"
```

### Out of Memory

**Symptom**: Render crashes with memory error

**Fixes**:
1. Reduce resolution: Edit `remotion.config.js`
2. Close other applications
3. Render shorter preview first to test

## General Recovery

### Start Over

If multiple steps have errors:
```bash
# Remove workspace and restart
rm -rf "<workspaceRoot>/<slug>/"
# Re-run from Step 0
```

### Check meta.json

Always read the workspace status first:
```bash
jq .status "<workspaceRoot>/<slug>/meta.json"
```

### Resume from Failed Step

Most steps can be re-run safely:
1. Read meta.json to see last successful step
2. Re-run the failed step
3. Update meta.json manually if needed
