# README Features, Tools, And Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the root `README.md` so users/operators can understand the full remix pipeline, available features, major tools, and generated outputs.

**Architecture:** Keep the root README as an operator-facing overview. Use `prompts/README.md`, `docs/intent.md`, `tools/acapella-extractor/README.md`, and `tools/video-generator/README.md` as source-of-truth references, but do not duplicate every implementation detail. The only planned file change is `README.md`.

**Tech Stack:** Markdown documentation, existing prompt docs, existing Python acapella extractor, Remotion video generator, Suno.ai, Chrome DevTools MCP, fal.ai, yt-dlp, FFmpeg.

---

## File Structure

- Modify: `README.md`
- Reference only: `prompts/README.md`
- Reference only: `docs/intent.md`
- Reference only: `tools/acapella-extractor/README.md`
- Reference only: `tools/video-generator/README.md`

---

### Task 1: Confirm README Pipeline Gaps

**Files:**
- Inspect: `README.md`
- Inspect: `prompts/README.md`
- Inspect: `docs/intent.md`

- [ ] **Step 1: Read the existing root README pipeline section**

Run:

```bash
grep -n "Step 10\|Step 11\|short" README.md
```

Expected before implementation: either no `Step 10` / `Step 11` matches, or only incomplete short-video mentions.

- [ ] **Step 2: Read the prompt pipeline index for current steps**

Run:

```bash
grep -n "Step 10\|Step 11\|Complete Steps" prompts/README.md
```

Expected: output includes `step-10-select-short-clip.md`, `step-11-generate-short-video.md`, and `Complete Steps 6-11`.

- [ ] **Step 3: Read intent docs for short-video behavior**

Run:

```bash
grep -n "Step 10\|Step 11\|shorts-segments\|short.mp4" docs/intent.md
```

Expected: output includes short clip selection, short video rendering, `shorts-segments.json`, and `<slug>-short.mp4`.

---

### Task 2: Update README Opening And Feature Summary

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace the opening description with complete operator-facing outputs**

Change the opening paragraph to communicate that the pipeline produces both full-length and short-form video outputs.

Use this text:

```markdown
An AI-powered pipeline that automates the end-to-end process of remixing Telugu and other Indic-language songs. Give it a YouTube link and a target genre; it produces Suno remix candidates, synced native-script lyrics, AI-stylized cover art, a full audio-reactive music video, YouTube upload metadata, and a vertical short-video cutdown.
```

- [ ] **Step 2: Add a `## Features` section after the opening paragraph**

Insert this section before `## How It Works`:

```markdown
## Features

- **End-to-end remix workflow**: Turns a YouTube URL and genre prompt into finished remix assets.
- **Native Indic-script lyrics**: Preserves Telugu, Hindi, Tamil, and other Indic scripts without romanization.
- **Suno remix generation**: Uses the original vocal stem and Suno-formatted lyrics to generate two remix candidates.
- **User-selected final remix**: Pauses once for the user to choose the preferred Suno variation.
- **Forced lyric alignment**: Produces line-level and word-level timing with CTC alignment for synced video lyrics.
- **AI cover art enhancement**: Finds source cover art and stylizes it for the video package.
- **Audio-reactive full video**: Renders a 1920x1080 Remotion music video with frequency-driven visual motifs.
- **Short-form cutdown**: Selects a high-energy segment and renders a 1080x1920 vertical short.
- **YouTube packaging**: Generates title, description, tags, and thumbnail text for upload workflows.
```

- [ ] **Step 3: Verify the new features section exists**

Run:

```bash
grep -n "## Features\|Short-form cutdown\|YouTube packaging" README.md
```

Expected: output includes all three searched phrases.

---

### Task 3: Update The Pipeline Flow To Steps 0-11

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace the `## How It Works` diagram block**

Replace the current diagram with this block:

```markdown
```
YouTube URL + Genre (user input)
        |
        v
[Step 0] Prepare Workspace         -> meta.json + workspace folder
[Step 1] Download MP3               -> yt-dlp extracts audio from YouTube
[Step 2] Extract Acapella           -> Mel-Band RoFormer vocal isolation
[Step 3] Find Lyrics                -> Browser automation finds native-script lyrics
[Step 4] Generate Suno Lyrics       -> Suno meta-tags + style block + design.json
[Step 5] Upload to Suno             -> Creates 2 remix variations on Suno.ai
[Step 5.5] User Selection           -> User picks preferred version
[Step 6] Extract & Align Lyrics     -> CTC forced alignment for synced lyrics
[Step 7] Fetch Cover Art            -> Browser search + AI stylization
[Step 8] Generate Full Video        -> Remotion renders 1920x1080 music video
[Step 9] Generate YouTube Metadata  -> Title, description, tags, thumbnail text
[Step 10] Select Short Clip         -> Scores lyrics/audio segments for a short
[Step 11] Generate Short Video      -> Remotion renders 1080x1920 vertical video
```
```

- [ ] **Step 2: Verify all pipeline steps are visible**

Run:

```bash
grep -n "\[Step 10\]\|\[Step 11\]\|Generate Full Video" README.md
```

Expected: output includes Step 10, Step 11, and `Generate Full Video`.

---

### Task 4: Add Operator-Facing Tooling Section

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Expand `## Tech Stack` with a practical `## Tools And Services` section**

Insert this section after the existing Tech Stack table:

```markdown
## Tools And Services

- **Workspace orchestration**: `meta.json` tracks every input, generated file, selected remix, and step status inside each remix workspace.
- **YouTube audio download**: `yt-dlp` downloads and converts the source audio to MP3.
- **Vocal isolation**: `tools/acapella-extractor` uses Mel-Band RoFormer for original and remix vocal stems.
- **Lyrics alignment**: The acapella extractor also provides CTC forced alignment and verification utilities.
- **Browser automation**: Chrome DevTools MCP handles lyrics search, Suno.ai interaction, and cover-art search.
- **Music generation**: Suno.ai creates two remix candidates from the vocal stem, Suno lyrics, and style prompt.
- **Image generation**: fal.ai stylizes cover art for the final video package.
- **Video rendering**: `tools/video-generator` scaffolds and renders Remotion projects for full and short videos.
- **Metadata generation**: Step 9 produces upload-ready YouTube metadata artifacts.
```

- [ ] **Step 2: Verify tool names are findable in the README**

Run:

```bash
grep -n "Tools And Services\|tools/acapella-extractor\|tools/video-generator\|Chrome DevTools MCP" README.md
```

Expected: output includes the section title and the listed tool names.

---

### Task 5: Update Project Structure For Steps 10-11 And Skills

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add Step 10 and Step 11 prompt files to the project tree**

In the `prompts/` section of the project structure code block, add:

```markdown
│   ├── step-10-select-short-clip.md
│   └── step-11-generate-short-video.md
```

Make sure `step-9-generate-youtube-metadata.md` uses `├──`, not `└──`, because more prompt files follow it.

- [ ] **Step 2: Add Remotion skill to the `.agents/skills/` section**

In the `.agents/skills/` portion of the project tree, include:

```markdown
│   ├── remotion-best-practices/          # Remotion video rendering guidance
```

Keep the existing Suno and video-generation skill entries.

- [ ] **Step 3: Verify the project tree lists short-video steps**

Run:

```bash
grep -n "step-10-select-short-clip\|step-11-generate-short-video\|remotion-best-practices" README.md
```

Expected: output includes all three paths.

---

### Task 6: Update Pipeline Details For Steps 8-11

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Rename Step 8 heading**

Change:

```markdown
### Step 8: Generate Video
```

To:

```markdown
### Step 8: Generate Full Video
```

- [ ] **Step 2: Expand Step 9 description**

Replace the Step 9 paragraph with:

```markdown
Produces `youtube-metadata.json` with title, description, tags, and thumbnail text ready for upload workflows. The step can also create a human-readable metadata artifact for review.
```

- [ ] **Step 3: Add Step 10 details after Step 9**

Insert:

```markdown
### Step 10: Select Short Clip

Analyzes aligned lyric sections and audio energy to identify the strongest short-form segment. Chorus sections are preferred, with additional scoring from loudness and section type. Saves the selected segment to `shorts-segments.json` and updates video configuration for vertical rendering.
```

- [ ] **Step 4: Add Step 11 details after Step 10**

Insert:

```markdown
### Step 11: Generate Short Video

Renders a 1080x1920 vertical short from the existing Remotion project using the selected clip window. The short keeps the same palette, motifs, cover art, and synced native-script lyrics as the full video while adapting the layout for mobile viewing.
```

- [ ] **Step 5: Verify Step 8-11 details are present**

Run:

```bash
grep -n "Step 8: Generate Full Video\|Step 10: Select Short Clip\|Step 11: Generate Short Video\|shorts-segments.json" README.md
```

Expected: output includes all four searched phrases.

---

### Task 7: Update Workspace Output Inventory

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add short-video outputs to the workspace tree**

In the `Workspace Output` code block, add these entries after `youtube-metadata.json`:

```markdown
├── youtube-metadata-artifact.md  # Optional human-readable metadata review artifact
├── shorts-segments.json          # Selected short clip segment and scoring
├── <slug>-short.mp4              # Final rendered vertical short video
```

Adjust tree markers so only the final `video/` line uses `└──`.

- [ ] **Step 2: Verify output inventory contains short artifacts**

Run:

```bash
grep -n "youtube-metadata-artifact.md\|shorts-segments.json\|<slug>-short.mp4" README.md
```

Expected: output includes all three artifact names.

---

### Task 8: Update Getting Started And Design Decisions

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update Getting Started final pipeline sentence**

Change the final Getting Started step to:

```markdown
6. The agent walks through each step sequentially, with a user checkpoint at Step 5.5 to select the preferred remix variation. After selection, the pipeline can complete the full video, YouTube metadata, short clip selection, and vertical short video autonomously.
```

- [ ] **Step 2: Add short-video design decision**

Add this bullet to `## Key Design Decisions`:

```markdown
- **Shorts reuse final assets**: Vertical shorts use the selected remix, aligned lyrics, cover art, and design palette from the full-video pipeline
```

- [ ] **Step 3: Verify operator-facing run guidance mentions shorts**

Run:

```bash
grep -n "vertical short video autonomously\|Shorts reuse final assets" README.md
```

Expected: output includes both phrases.

---

### Task 9: Final Documentation Verification

**Files:**
- Verify: `README.md`

- [ ] **Step 1: Check the README has no stale 0-9-only language**

Run:

```bash
grep -n "Steps 0-9\|Step 9.*final\|Complete Steps 6-9" README.md
```

Expected: no output.

- [ ] **Step 2: Check all current prompt steps are represented in README**

Run:

```bash
grep -n "Step 0\|Step 1\|Step 2\|Step 3\|Step 4\|Step 5\|Step 5.5\|Step 6\|Step 7\|Step 8\|Step 9\|Step 10\|Step 11" README.md
```

Expected: output includes every step from Step 0 through Step 11, including Step 5.5.

- [ ] **Step 3: Review the rendered markdown mentally for structure**

Open `README.md` and confirm:

- The first page explains what users get from the pipeline.
- `## Features` appears before implementation details.
- The full pipeline diagram includes Steps 10 and 11.
- Tooling details are concise and operator-facing.
- Deep implementation information remains linked or summarized, not duplicated excessively.

- [ ] **Step 4: Commit the README update**

Run:

```bash
git add README.md docs/superpowers/plans/2026-04-24-readme-features-tools-pipeline.md
git commit -m "docs: document remix pipeline features and tools"
```

Expected: commit succeeds. If hooks modify files, inspect the modifications and create a new commit only if the first commit failed; do not amend unless explicitly requested.

---

## Self-Review

- Spec coverage: The plan covers the approved README design: capability overview, features, full Steps 0-11 pipeline, tools/services, workspace outputs, getting started, and design decisions.
- Placeholder scan: No TBD/TODO/fill-in placeholders are present.
- Scope check: This is a single documentation update isolated to `README.md`, plus this implementation plan document.
- Type/name consistency: Step names and filenames match `prompts/README.md`; output names match `docs/intent.md` and existing README naming conventions.
