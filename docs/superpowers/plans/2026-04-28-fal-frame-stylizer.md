# Fal Frame Stylizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable slug-based fal.ai Nano Banana Pro frame stylizer for visual sequence workspaces.

**Architecture:** Add a focused TypeScript CLI in `tools/visual-sequence/` that resolves a workspace slug, reads `selected-visual-frames.json`, loads a prompt file, uploads each selected source frame to fal.ai, saves generated outputs to `stylized-frames/`, and updates `meta.json`. Tests cover planning/filtering, skip behavior, and mocked client output without real network calls.

**Tech Stack:** Node.js, TypeScript, Effect v4 beta (`effect@beta`), fal.ai REST API via `fetch`, existing workspace-root helper, `node:test`.

---

## File Structure

- Create `tools/visual-sequence/stylize-fal.ts`: TypeScript CLI, pure helpers, fal.ai upload/run/download workflow, metadata update.
- Create `tools/visual-sequence/stylize-fal.test.js`: node:test tests that import compiled/runtime module behavior through exported helper functions.
- Modify `tools/visual-sequence/package.json`: local package metadata and scripts for the stylizer tool if missing.
- Modify `docs/superpowers/specs/2026-04-28-fal-frame-stylizer-design.md`: only if implementation discovers a minor command correction.

## Task 1: Add Project Package For Visual Sequence Tools

**Files:**
- Create: `tools/visual-sequence/package.json`

- [ ] **Step 1: Create package metadata**

```json
{
  "type": "commonjs",
  "private": true,
  "scripts": {
    "test": "node --test *.test.js",
    "stylize:fal": "tsx stylize-fal.ts"
  },
  "dependencies": {
    "effect": "beta",
    "tsx": "latest"
  }
}
```

- [ ] **Step 2: Install dependencies**

Run: `npm install --prefix tools/visual-sequence`

Expected: `tools/visual-sequence/package-lock.json` is created and dependencies install without errors.

## Task 2: Add Pure Planning Helpers And Tests

**Files:**
- Create: `tools/visual-sequence/stylize-fal.ts`
- Create: `tools/visual-sequence/stylize-fal.test.js`

- [ ] **Step 1: Write failing tests for args and frame planning**

Add tests that assert:
- `parseStylizeArgs(["slug", "--prompt-file=prompt.txt", "--limit=1"])` returns slug, prompt path, limit 1.
- `selectFramesForRun(frames, {limit: 1})` returns only the first frame.
- `selectFramesForRun(frames, {frame: "frame-002"})` returns only frame 002.
- `planOutputs` marks existing output as skipped unless overwrite is true.

- [ ] **Step 2: Run tests to verify failure**

Run: `npm test --prefix tools/visual-sequence -- stylize-fal.test.js`

Expected: FAIL because `stylize-fal.ts` does not exist or exports are missing.

- [ ] **Step 3: Implement pure helpers**

Implement exported functions:
- `parseStylizeArgs(argv)`
- `selectFramesForRun(frames, options)`
- `planOutputs({slug, workspaceDir, frames, overwrite})`
- `resolveOutputPath({workspaceDir, slug, frameId, extension})`

- [ ] **Step 4: Run tests to verify pass**

Run: `npm test --prefix tools/visual-sequence -- stylize-fal.test.js`

Expected: PASS for helper tests.

## Task 3: Add Fal Client Workflow With Mocked Tests

**Files:**
- Modify: `tools/visual-sequence/stylize-fal.ts`
- Modify: `tools/visual-sequence/stylize-fal.test.js`

- [ ] **Step 1: Write failing mocked client test**

Add a test for `stylizeFrameWithClient` using a fake client with:
- `uploadFile` returning `https://example.test/input.jpg`
- `editImage` returning `{ url: "https://example.test/output.jpg" }`
- `downloadFile` writing `fake-image` to output path

Assert output file exists and contains `fake-image`.

- [ ] **Step 2: Run test to verify failure**

Run: `npm test --prefix tools/visual-sequence -- stylize-fal.test.js`

Expected: FAIL because workflow helper is missing.

- [ ] **Step 3: Implement fal client interface and workflow helper**

Add:
- `createFalClient({apiKey, fetchImpl})`
- `stylizeFrameWithClient({client, prompt, sourcePath, outputPath})`

Use fal.ai REST API endpoints:
- Upload: `https://fal.run/storage/upload`
- Submit model: `https://fal.run/fal-ai/nano-banana-pro/edit`

Parse the first returned image URL from `images[0].url`, `image.url`, or `url`.

- [ ] **Step 4: Run test to verify pass**

Run: `npm test --prefix tools/visual-sequence -- stylize-fal.test.js`

Expected: PASS.

## Task 4: Add Effect-Based CLI Runtime

**Files:**
- Modify: `tools/visual-sequence/stylize-fal.ts`

- [ ] **Step 1: Implement CLI runtime**

Use Effect v4 beta imports from `effect` for:
- reading environment config (`FAL_API_KEY`)
- validating files and prompt text
- bounded retry for each frame
- concurrency-limited batch processing

CLI behavior:
- `--dry-run` prints selected frames and exits 0.
- Missing `FAL_API_KEY` exits non-zero before uploads.
- Existing outputs are skipped unless `--overwrite` is set.
- Any failed frame exits non-zero after printing failures.

- [ ] **Step 2: Run dry run on current workspace**

Run: `npm run --prefix tools/visual-sequence stylize:fal -- manike-mage-hithe-manake-love-a-ayithe-deep-house --prompt-file=/Users/aira/projects/remix-gpt-coding-agent/workspaces/manike-mage-hithe-manake-love-a-ayithe-deep-house/frame-stylization-prompt-template.txt --limit=1 --dry-run`

Expected: output lists `frame-001` and no API request is made.

## Task 5: Verify With One Real Frame

**Files:**
- Generated: `workspaces/manike-mage-hithe-manake-love-a-ayithe-deep-house/stylized-frames/<slug>-frame-001.*`

- [ ] **Step 1: Run one-frame fal stylization**

Run: `npm run --prefix tools/visual-sequence stylize:fal -- manike-mage-hithe-manake-love-a-ayithe-deep-house --prompt-file=/Users/aira/projects/remix-gpt-coding-agent/workspaces/manike-mage-hithe-manake-love-a-ayithe-deep-house/frame-stylization-prompt-template.txt --frame=frame-001 --overwrite`

Expected: one stylized image is written to `stylized-frames/`.

- [ ] **Step 2: Verify file exists**

Run: `ls -lh workspaces/manike-mage-hithe-manake-love-a-ayithe-deep-house/stylized-frames/manike-mage-hithe-manake-love-a-ayithe-deep-house-frame-001.*`

Expected: one non-empty image file.

## Task 6: Run Tests And Summarize

**Files:**
- Modified/created files from prior tasks.

- [ ] **Step 1: Run visual sequence tests**

Run: `npm test --prefix tools/visual-sequence`

Expected: all tests pass.

- [ ] **Step 2: Run existing visual-sequence JS tests if needed**

Run: `node --test tools/visual-sequence/visual-sequence.test.js`

Expected: existing tests pass.

- [ ] **Step 3: Summarize usage**

Report the command for processing all 40 frames and the command for generating `image-sequence.json` after the frames are ready.
