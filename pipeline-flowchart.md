# Indic Song Remixer - Complete Pipeline Flowchart

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   INDIC SONG REMIXER PIPELINE                                   │
│                              YouTube URL + Genre/Style → Final Video                           │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              STEP 0: PREPARE WORKSPACE                                           │
│                              ┌────────────────────────────────────────┐                         │
│                              │ 0.1 Collect User Inputs               │                         │
│                              │    • YouTube URL                        │                         │
│                              │    • Remix genre/style                  │                         │
│                              │    • Language (optional)                │                         │
│                              │    • Tempo preference (optional)        │                         │
│                              │    • Song length preference (optional)  │                         │
│                              └────────────────────────────────────────┘                         │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 0.2 Fetch Video Title          │                                  │
│                              │    • Navigate to YouTube URL   │                                  │
│                              │    • Extract <title> from page │                                  │
│                              │    • Strip " - YouTube" suffix │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 0.3 Generate Workspace Slug    │                                  │
│                              │    • First 4-6 words + genre    │                                  │
│                              │    • Lowercase, hyphens       │                                  │
│                              │    • Remove special chars       │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 0.4 Create Workspace Directory│                                  │
│                              │    • mkdir -p workspaces/<slug> │                                  │
│                              │    • Verify creation          │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 0.5 Write meta.json           │                                  │
│                              │    • All inputs + derived data│                                  │
│                              │    • Status tracking         │                                  │
│                              │    • Created timestamp        │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 0.6 Confirm Workspace Ready   │                                  │
│                              │    • Print summary to user    │                                  │
│                              │    • Show workspace path      │                                  │
│                              └───────────────────────────────┘                                  │
│                                                                                                 │
│                              📁 OUTPUT: workspaces/<slug>/                                       │
│                              📄 OUTPUT: workspaces/<slug>/meta.json                              │
└───────────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              STEP 1: DOWNLOAD MP3 FROM YOUTUBE                                   │
│                              ┌────────────────────────────────────────┐                         │
│                              │ 1.1 Download MP3 with yt-dlp          │                         │
│                              │    • uvx yt-dlp -x --audio-format mp3  │                         │
│                              │    • Best quality (0)                   │                         │
│                              │    • Save as <slug>-original.mp3        │                         │
│                              └───────────────┬────────────────────────┘                         │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 1.2 Verify Download           │                                  │
│                              │    • Check file exists        │                                  │
│                              │    • Size > 1MB               │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 1.3 Update meta.json Status   │                                  │
│                              │    • mp3_downloaded: true     │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 1.4 Confirm File Ready         │                                  │
│                              │    • Print file path + size   │                                  │
│                              └───────────────────────────────┘                                  │
│                                                                                                 │
│                              📁 OUTPUT: workspaces/<slug>/<slug>-original.mp3                    │
│                              📄 OUTPUT: workspaces/<slug>/meta.json (updated)                   │
└───────────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              STEP 2: EXTRACT ACAPELLA                                            │
│                              (Mel-Band RoFormer via UV Tool)                                     │
│                              ┌────────────────────────────────────────┐                         │
│                              │ 2.1 Verify Tool Setup                 │                         │
│                              │    • Check .venv/bin/python exists   │                         │
│                              │    • Check extract.py exists          │                         │
│                              │    • Contact user if setup needed     │                         │
│                              └───────────────┬────────────────────────┘                         │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 2.2 Run Extraction           │                                  │
│                              │    • Load model (~300MB)      │                                  │
│                              │    • Process audio (2-5 min) │                                  │
│                              │    • Extract vocals-only      │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 2.3 Handle Output Format      │                                  │
│                              │    • Convert WAV to MP3       │                                  │
│                              │    • ffmpeg -i *.wav acapella.mp3│                               │
│                              │    • Remove source WAV        │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 2.4 Verify Output             │                                  │
│                              │    • Check file type          │                                  │
│                              │    • File size: 4-8MB         │                                  │
│                              │    • MP3 format confirmed     │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 2.5 Update meta.json           │                                  │
│                              │    • acapella_extracted: true │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 2.6 Complete                  │                                  │
│                              │    • Print success summary    │                                  │
│                              │    • Show output path         │                                  │
│                              └───────────────────────────────┘                                  │
│                                                                                                 │
│                              📁 OUTPUT: workspaces/<slug>/acapella.mp3                          │
│                              📄 OUTPUT: workspaces/<slug>/meta.json (updated)                   │
└───────────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              STEP 3: FIND & SAVE INDIC LYRICS                                   │
│                              ┌────────────────────────────────────────┐                         │
│                              │ 3.1 Build the Search Query            │                         │
│                              │    • <song name> <language> lyrics    │                         │
│                              │    • Strip filler words               │                         │
│                              │    • Example: "Meesaala Pilla Telugu lyrics"                    │
│                              └───────────────┬────────────────────────┘                         │
│                                              │                                                  │
│                              ┌───────────────▼───────────────────────┐                          │
│                              │ 3.2 Try lyricstape.com First          │                          │
│                              │    • Preferred for Telugu songs       │                          │
│                              │    • Navigate to: /?s=<song>          │                          │
│                              │    • If found → Skip to 3.4           │                          │
│                              │    • If not found → Go to 3.3         │                          │
│                              └───────────────┬────────────────────────┘                          │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 3.3 Search Google (Fallback) │                                  │
│                              │    • site:lyricstape.com first│                                  │
│                              │    • Broaden if needed        │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 3.4 Identify Best Lyrics      │                                  │
│                              │    • Prefer native script     │                                  │
│                              │    • Avoid romanized text     │                                  │
│                              │    • Check: lyricstape.com, │                                  │
│                              │      lyricsted.com, lyricsmint.com                              │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 3.5 Navigate to Lyrics Page   │                                  │
│                              │    • Click best result        │                                  │
│                              │    • Verify page loads        │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 3.6 Verify Native Script      │                                  │
│                              │    • Check for Telugu script  │                                  │
│                              │    • NOT romanized            │                                  │
│                              │    • Go back if wrong         │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 3.7 Extract Lyrics Text       │                                  │
│                              │    • evaluate_script with     │                                  │
│                              │      common selectors         │                                  │
│                              │    • Get full lyrics text     │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 3.8 Save Lyrics to Workspace  │                                  │
│                              │    • Include header metadata  │                                  │
│                              │    • <slug>-lyrics.txt         │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 3.9 Update meta.json Status   │                                  │
│                              │    • lyrics_saved: true       │                                  │
│                              │    • lyrics_source_url added  │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 3.10 Confirm Lyrics Ready     │                                  │
│                              │    • Print file path + lines  │                                  │
│                              └───────────────────────────────┘                                  │
│                                                                                                 │
│                              📁 OUTPUT: workspaces/<slug>/<slug>-lyrics.txt                    │
│                              📄 OUTPUT: workspaces/<slug>/meta.json (updated)                   │
└───────────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              STEP 4: GENERATE SUNO META-TAG LYRICS                              │
│                              ┌────────────────────────────────────────┐                         │
│                              │ 4.1 Read Inputs                │                                  │
│                              │    • <slug>-lyrics.txt          │                                  │
│                              │    • meta.json (genre, tempo)  │                                  │
│                              └───────────────┬────────────────────────┘                         │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 4.2 Ask Clarifying Questions  │                                  │
│                              │    (if not in meta.json)      │                                  │
│                              │    • Genre/style confirmation │                                  │
│                              │    • Tempo preference         │                                  │
│                              │    • Full vs shortened        │                                  │
│                              │    • Vocal gender preference  │                                  │
│                              │    • Mood/vibe                │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 4.3 Understand Suno Format      │                                  │
│                              │    • Style block format       │                                  │
│                              │    • Section tags: [Verse],   │                                  │
│                              │      [Chorus], [Bridge]       │                                  │
│                              │    • Production cues ()       │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 4.4 Map Lyrics to Structure   │                                  │
│                              │    • Pallavi → [Chorus]       │                                  │
│                              │    • Charanam → [Verse]       │                                  │
│                              │    • Anupallavi → [Pre-Chorus]/[Bridge]                         │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 4.5 Build Style Block         │                                  │
│                              │    • [genre, mood, language, │                                  │
│                              │      vocal, bpm, instruments] │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 4.6 Generate Full Lyrics      │                                  │
│                              │    • Start with style block   │                                  │
│                              │    • Add [Intro] with cues    │                                  │
│                              │    • Map each section         │                                  │
│                              │    • Preserve Indic script    │                                  │
│                              │    • End with [Outro]         │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 4.7 Check Length Constraints    │                                  │
│                              │    • Style: max 1000 chars    │                                  │
│                              │    • Lyrics: ~3000 chars      │                                  │
│                              │    • Trim if needed           │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 4.8 Save to Workspace         │                                  │
│                              │    • <slug>-suno-lyrics.txt   │                                  │
│                              │    • <slug>-suno-style.txt    │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 4.9 Update meta.json Status     │                                  │
│                              │    • suno_lyrics_generated: true│                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 4.10 Confirm Ready             │                                  │
│                              │    • Print file paths + sizes │                                  │
│                              └───────────────────────────────┘                                  │
│                                                                                                 │
│                              📁 OUTPUT: workspaces/<slug>/<slug>-suno-lyrics.txt               │
│                              📁 OUTPUT: workspaces/<slug>/<slug>-suno-style.txt                │
│                              📄 OUTPUT: workspaces/<slug>/meta.json (updated)                   │
└───────────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              STEP 5: GENERATE & DOWNLOAD REMIX FROM SUNO.AI                      │
│                              ┌────────────────────────────────────────┐                         │
│                              │ 5.1 Navigate to Suno Create Page│                                  │
│                              │    • URL: https://suno.com/create│                                 │
│                              │    • Verify page elements       │                                  │
│                              └───────────────┬────────────────────────┘                         │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 5.2 Switch to Advanced Mode    │                                  │
│                              │    • Click "Advanced" button    │                                  │
│                              │    • Verify expanded fields   │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 5.3 Create/Select Workspace     │                                  │
│                              │    • Click workspace dropdown │                                  │
│                              │    • Create new with slug     │                                  │
│                              │    • Verify workspace name    │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 5.4 Upload Acapella Audio       │                                  │
│                              │    • Click "Add audio"        │                                  │
│                              │    • Select "Sample"/"Upload"  │                                  │
│                              │    • Upload <slug>-acapella.mp3│                                  │
│                              │    • Verify upload appears    │                                  │
│                              │    • If not in audio section: │                                  │
│                              │      • Click "Remix" → "Library"│                                  │
│                              │      • Select from library    │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 5.5 Set Audio Influence Mode  │                                  │
│                              │    • Select "Cover" mode      │                                  │
│                              │    • Adjust slider 70-85%     │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 5.6 Paste Suno Lyrics         │                                  │
│                              │    • Read suno-lyrics.txt     │                                  │
│                              │    • Click lyrics text area   │                                  │
│                              │    • Paste full contents      │                                  │
│                              │    • Verify entered           │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 5.7 Paste Style Description   │                                  │
│                              │    • Read suno-style.txt      │                                  │
│                              │    • Click styles text area   │                                  │
│                              │    • Paste contents           │                                  │
│                              │    • Verify < 1000 chars      │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 5.8 Set Song Title            │                                  │
│                              │    • Fill title field         │                                  │
│                              │    • Value: <slug>            │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 5.9 Review Before Submit      │                                  │
│                              │    • Snapshot all fields      │                                  │
│                              │    • Confirm acapella present │                                  │
│                              │    • Verify lyrics correct    │                                  │
│                              │    • Check style within limit │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 5.10 Select Workspace         │                                  │
│                              │    • Click workspace dropdown │                                  │
│                              │    • Select slug workspace  │                                  │
│                              │    • Verify selected          │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 5.11 Submit Creation          │                                  │
│                              │    • Click "Create song"      │                                  │
│                              │    • Take snapshot            │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 5.12 Wait for Generation      │                                  │
│                              │    • Watch for "Play"/"Download"│                                  │
│                              │    • Timeout: 5 minutes       │                                  │
│                              │    • 2 variations generated   │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 5.13 Download Both Songs      │                                  │
│                              │    • Download variation 1     │                                  │
│                              │    • Download variation 2     │                                  │
│                              │    • Wait for completion      │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 5.14 Locate & Rename Files    │                                  │
│                              │    • Find in ~/Downloads/     │                                  │
│                              │    • Rename to:               │                                  │
│                              │      <slug>-remix-v1.mp3       │                                  │
│                              │      <slug>-remix-v2.mp3       │                                  │
│                              │    • Move to workspace        │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 5.15 Verify Downloads         │                                  │
│                              │    • Get Suno URLs            │                                  │
│                              │    • Confirm files exist      │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 5.16 Save Metadata            │                                  │
│                              │    • remix_v1_downloaded: true│                                  │
│                              │    • remix_v2_downloaded: true│                                  │
│                              │    • suno_remix_url_v1/v2     │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 5.17 Present Options to User  │                                  │
│                              │    • Show both file paths     │                                  │
│                              │    • Show Suno URLs           │                                  │
│                              │    • Ask user: v1 or v2?      │                                  │
│                              └───────────────────────────────┘                                  │
│                                                                                                 │
│                              📁 OUTPUT: workspaces/<slug>/<slug>-remix-v1.mp3                  │
│                              📁 OUTPUT: workspaces/<slug>/<slug>-remix-v2.mp3                  │
│                              📄 OUTPUT: workspaces/<slug>/meta.json (updated)                   │
└───────────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                                    │
                              ┌─────────────────────┴─────────────────────┐
                              │                                           │
                              ▼                                           ▼
                    ┌───────────────┐                           ┌───────────────┐
                    │ User Selects  │                           │ User Selects  │
                    │     v1        │                           │     v2        │
                    └───────┬───────┘                           └───────┬───────┘
                            │                                           │
                            └───────────────────┬───────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              STEP 6: GENERATE VIDEO WITH REMOTION                               │
│                              ┌────────────────────────────────────────┐                         │
│                              │ 6.1 Read Workspace Files       │                                  │
│                              │    • meta.json                 │                                  │
│                              │    • Extract: title, genre,    │                                  │
│                              │      language, slug            │                                  │
│                              └───────────────┬────────────────────────┘                         │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 6.2 Extract Acapella from     │                                  │
│                              │     Remix Audio               │                                  │
│                              │    • Run extractor on v1.mp3    │                                  │
│                              │    • Convert WAV to MP3       │                                  │
│                              │    • Output: <slug>-remix-v1-acapella.mp3                        │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 6.3 Generate Lyrics           │                                  │
│                              │     Timestamps                │                                  │
│                              │    • Run CTC forced aligner   │                                  │
│                              │    • Input: remix-v1-acapella │                                  │
│                              │      + suno-lyrics.txt        │                                  │
│                              │    • Output: lyrics-timestamps.json                              │
│                              │    • Language code: tel/hin/tam│                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 6.4 Verify Alignment          │                                  │
│                              │    • Run terminal karaoke     │                                  │
│                              │    • Check: ±500ms first line │                                  │
│                              │      ±1s chorus lines         │                                  │
│                              │      <3s end drift            │                                  │
│                              │    • Fix if needed            │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 6.5 Scaffold Remotion Project │                                  │
│                              │    • Run init-video.js        │                                  │
│                              │    • Auto-detect duration     │                                  │
│                              │    • Inject metadata          │                                  │
│                              │    • Create video/ folder     │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 6.6 Copy Assets to Video      │                                  │
│                              │    • Copy remix-v1.mp3 → audio.mp3                               │
│                              │    • Copy lyrics-timestamps.json │                                  │
│                              │    • Copy suno-lyrics.txt       │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 6.7 Install & Render          │                                  │
│                              │    • npm install              │                                  │
│                              │    • npx remotion render      │                                  │
│                              │    • Time: 1-2 minutes        │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 6.8 Copy Output to Workspace   │                                  │
│                              │    • video/out/video.mp4      │                                  │
│                              │    → <slug>-video.mp4          │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 6.9 Update Metadata           │                                  │
│                              │    • video_generated: true    │                                  │
│                              │    • Record all outputs       │                                  │
│                              └───────────────┬───────────────┘                                  │
│                                              │                                                  │
│                              ┌───────────────▼───────────────┐                                  │
│                              │ 6.10 Present Final Results    │                                  │
│                              │    • Show all output files    │                                  │
│                              │    • Show duration + lyrics    │                                  │
│                              │    • Show theme               │                                  │
│                              └───────────────────────────────┘                                  │
│                                                                                                 │
│                              📁 OUTPUT: workspaces/<slug>/<slug>-video.mp4                     │
│                              📁 OUTPUT: workspaces/<slug>/video/ (Remotion project)             │
│                              📄 OUTPUT: workspaces/<slug>/meta.json (final)                     │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              ✅ PIPELINE COMPLETE                                                │
│                                                                                                 │
│                              Final Deliverables in workspaces/<slug>/:                          │
│                              • <slug>-video.mp4          → Final music video (1920×1080)       │
│                              • <slug>-remix-v1.mp3       → Selected remix audio                  │
│                              • <slug>-original.mp3       → Original YouTube audio               │
│                              • <slug>-acapella.mp3       → Extracted vocals (original)          │
│                              • <slug>-lyrics.txt         → Original lyrics (native script)       │
│                              • <slug>-suno-lyrics.txt    → Suno-formatted lyrics                │
│                              • <slug>-suno-style.txt     → Suno style block                      │
│                              • meta.json                 → Session metadata                      │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘


## Legend

```
┌───────┐  =  Step/Process box
│       │
└───┬───┘
    │      =  Flow direction
    ▼
───────   =  Decision/branch point
│ v1  │
└──┬──┘
   │
```

## File Dependencies by Step

```
Step 0:
  → Creates: workspaces/<slug>/
  → Creates: meta.json

Step 1:
  ← Requires: meta.json (youtube_url, slug)
  → Creates: <slug>-original.mp3
  → Updates: meta.json (mp3_downloaded: true)

Step 2:
  ← Requires: <slug>-original.mp3, meta.json
  → Creates: acapella.mp3
  → Updates: meta.json (acapella_extracted: true)

Step 3:
  ← Requires: meta.json (video_title, language)
  → Creates: <slug>-lyrics.txt
  → Updates: meta.json (lyrics_saved: true, lyrics_source_url)

Step 4:
  ← Requires: <slug>-lyrics.txt, meta.json (genre, tempo)
  → Creates: <slug>-suno-lyrics.txt
  → Creates: <slug>-suno-style.txt
  → Updates: meta.json (suno_lyrics_generated: true)

Step 5:
  ← Requires: acapella.mp3, <slug>-suno-lyrics.txt, <slug>-suno-style.txt
  → Creates: <slug>-remix-v1.mp3
  → Creates: <slug>-remix-v2.mp3
  → Updates: meta.json (remix_*_downloaded, suno_remix_url_*)
  → User selects: v1 or v2 for video

Step 6:
  ← Requires: <slug>-remix-v1.mp3 (user selected), <slug>-suno-lyrics.txt, meta.json
  → Creates: <slug>-remix-v1-acapella.mp3
  → Creates: lyrics-timestamps.json
  → Creates: video/ folder (Remotion project)
  → Creates: <slug>-video.mp4
  → Updates: meta.json (video_generated: true)
```

## Key Constraints Summary

1. **All browser interactions**: Chrome DevTools MCP only
2. **File storage**: All files in `workspaces/<slug>/` only
3. **Lyrics**: Native Indic script only (no romanization)
4. **Suno.ai**: Free-tier features only
5. **Sequential execution**: Each step depends on previous outputs
6. **Unique slugs**: Append genre suffix to avoid collisions

## Error Handling Summary

```
Step 0:
  • YouTube fails to load → Confirm URL, retry
  • Slug collision → Append timestamp
  • Optional inputs skipped → Use defaults

Step 1:
  • 403/401 error → Use browser cookies
  • No audio formats → Download video+embedded audio
  • uvx not found → Install uv
  • 0 bytes file → Check disk space

Step 2:
  • Module not found → Check PYTHONPATH
  • uv not found → Install uv
  • .venv missing → Run uv sync
  • Model download hangs → Wait up to 10 min
  • Output missing → Check step 2.3

Step 3:
  • No Indic lyrics → Try alternative queries
  • JS required → Use screenshot + transcribe
  • Partial lyrics → Note gaps in file
  • Multiple scripts → Keep Indic only

Step 4:
  • Lyrics too long → Split into parts
  • Style >1000 chars → Trim instruments
  • Structure unclear → Use default: I-C-V-C-B-C-O
  • Missing sections → Comment gaps

Step 5:
  • Page load fails → Check login
  • Upload fails → Retry or check file size
  • Generation timeout → Wait longer
  • Download fails → Check permissions

Step 6:
  • ModuleNotFoundError → Use direct path, not -m
  • WAV output → Convert with ffmpeg
  • Lyrics not syncing → Check timestamps file
  • No lyrics visible → Missing delayRender, re-scaffold
  • Telugu garbled → System font fallback
  • ffprobe missing → brew install ffmpeg
  • Alignment off → Check acapella quality
```
