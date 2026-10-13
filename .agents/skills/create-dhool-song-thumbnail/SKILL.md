---
name: create-dhool-song-thumbnail
description: Create paired Dhool YouTube thumbnails and Instagram Reel covers with ChatGPT image generation using source-video frames to preserve recognizable lead-character identities, then apply the deterministic Dhool title system and optionally publish the YouTube image with exact live verification. Use for branded song covers, incorrect or generic faces, source-authentic actor or performer artwork, and platform-cover refreshes in this remix repository.
---

# Create Dhool Song Covers

Build the artwork from canonical song frames, then add branding with the repository renderer. Produce a matched landscape and portrait pair. Treat recognizable character identity and platform-specific composition as hard acceptance gates.

## Workflow

1. Read `.remix-workspace-root.json`, then the song workspace `meta.json` before acting.
2. Read the workspace cover/stylization prompt and `design.json` when present. Use them for mood and palette, not as authority to turn recognizable people into generic anime characters.
3. Establish source authority in this order:
   - local `source-frames/` extracted from the canonical original or visual-source video;
   - the canonical original video itself;
   - an official song page or credited release page;
   - publicity imagery only when no authentic video frame is usable.
4. Verify the lead identities and select references:
   - one clear close-up per lead;
   - one shared scene when the relationship or composition matters;
   - avoid blurred, occluded, tiny, back-facing, or heavily color-obscured faces.
5. Load every selected local reference with `view_image`. Label each reference role in the prompt.
6. Generate two artwork-only backgrounds with the built-in `image_gen` tool: one 16:9 composition for YouTube and one independently composed 9:16 version for Instagram. Use `identity-preserve` or `style-transfer` semantics and request cinematic semi-realism unless the user explicitly wants illustration. Do not stretch or blindly center-crop the landscape artwork.
7. Require:
   - recognizable facial geometry, age, hairstyle, skin tone, and screen persona for every lead;
   - YouTube: characters grouped on the right or center-right, with clean negative space on the left for the Dhool title lockup;
   - Instagram: characters and title space inside the center-safe region, with nonessential atmosphere allowed near the top and bottom Reel UI zones;
   - the workspace palette and emotional theme;
   - no text, logos, watermark, extra people, face fusion, or generic anime substitution.
8. Inspect both backgrounds at full resolution. Reject either if a viewer familiar with the song could not identify the leads without the title.
9. Preserve prior backgrounds under `backgrounds/archive/`, install the approved artwork at the renderer's expected paths, and apply the deterministic Dhool labels.
10. Save the final pair as `<slug>-youtube-thumbnail.jpg` at 1280x720 and `<slug>-instagram-reel-cover.jpg` at 1080x1920. Store both paths in `meta.json` and set their generated status fields only after review.
11. Inspect the full images and previews at 320x180 and 180x320. Keep title spelling, movie/source credit, genre badge, accent bar, and footer deterministic; do not ask image generation to render these labels. For Instagram, also simulate top and bottom UI occlusion and verify that faces and essential text remain intact.

Read [references/dhool-brand.md](references/dhool-brand.md) before composing the final prompt or overlay.

## Live YouTube replacement

Only publish when the user requests replacement. Change the thumbnail field only.

1. Record the selected live thumbnail URL before upload.
2. Upload through `Options` -> `Change` or `Upload file`.
3. Confirm the local data-image preview is visible and selected; wait at least five seconds before Save.
4. Save, wait at least five seconds, reopen the details page, and require the selected live thumbnail URL to differ from the recorded URL.
5. Run `scripts/verify-thumbnail-match.sh <local-final.jpg> <live-thumbnail-url>`. Accept a normalized RMSE at or below `0.06`; this allows YouTube recompression while rejecting unrelated artwork.
6. Do not change title, description, visibility, monetization, audience, playlist, end screen, or synthetic-media disclosure unless separately authorized.

## Prompt skeleton

```text
Use case: identity-preserve
Asset type: 16:9 YouTube thumbnail background for Dhool
Primary request: Reimagine the canonical song leads in the Dhool cinematic neon style while keeping them immediately recognizable.
Input images: Image 1: male lead face reference; Image 2: female lead face reference; Image 3: shared-scene composition reference.
Scene/backdrop: A source-appropriate cinematic environment with restrained neon atmosphere.
Subject: The verified lead characters; preserve facial geometry, age, hair, skin tone, clothing cues, and relationship.
Style/medium: Polished cinematic semi-realistic poster art, not anime or cartoon.
Composition/framing: Landscape 16:9; leads on the right half; uncluttered dark negative space on the left.
Lighting/mood: Match the workspace design palette and the song's emotional theme.
Text: none.
Constraints: Identity fidelity is more important than stylization; no face fusion; no invented cast.
Avoid: generic anime faces, beauty-filter homogenization, extra people, logos, watermark, captions, title text.
```

Generate a second prompt from the same verified references by changing only the platform composition requirements:

```text
Asset type: 9:16 Instagram Reel cover background for Dhool
Composition/framing: Portrait 9:16; keep recognizable faces and clean title space in the center-safe region; reserve the outer top and bottom for nonessential atmosphere that may sit behind Reel UI.
Constraints: Recompose from the references. Do not stretch or center-crop the YouTube artwork.
```
