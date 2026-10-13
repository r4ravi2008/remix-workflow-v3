# Storyboards and production anchors

Use this reference before motion generation when a task creates, replaces, or inherits a storyboard. The goal is a complete chronological set of production stills that can safely drive video generation and survive later revisions.

## Keep the artifacts distinct

- A **scene** is a story or visual state with a purpose and timeline range.
- A **storyboard panel** communicates the planned scene. It may be part of a multi-panel sheet.
- A **production anchor** is one full-size still intended to condition motion or define an edit boundary.
- A **model input** is a provider-specific derivative of an accepted production anchor.
- A **motion plate** is generated footage for one planned interval.
- A **contact sheet** is a review index. It is never the authoritative source for an individual anchor.

Do not call cropped cells from a storyboard sheet “raw anchors.” Cropping a sheet often leaves too few pixels for sharp 1080p production. Generate every current production anchor as its own image with the installed `imagegen` skill, or explicitly classify it as a lower-resolution derived placeholder that cannot pass the final image gate.

## Lock authority before timing the storyboard

Bind the storyboard to the canonical audio path, hash, duration, selected trim, and listening evidence. Confirm the latest user direction, permitted source use, character identities, style references, aspect ratio, lyric/text policy, and approval mode. If the user corrects the song or mix, retire the old timing rather than adapting it by filename or duration alone.

Choose one of these approval modes and record it in the brief:

- `user-gated`: stop after the requested storyboard, anchor library, pilot, or range and provide reviewable files.
- `autonomous`: perform the same gates with recorded inspection evidence and continue when they pass.

An end-to-end request permits ordinary preparation; it does not permit using failed or unreviewed anchors.

## Design a complete chronological sequence

Create the audio/meaning map first, then define scenes and the changes between them. Each scene needs a narrative or motif purpose, timeline range, initial state, action/change, resulting state, and musical anchor. Show consequential action visually rather than explaining it with invented commentary text. Distinguish lyrics, translation, transliteration, titles, and story commentary; never add the last category merely because the user said “captions.”

Audit causal coverage, not just scene count. For a message being sent, for example, the sequence may need intent, tap/action, result, and the other character's consequence. Verify interface semantics as well as appearance. Check that time-of-day, wardrobe, props, geography, screen direction, and relationship state advance coherently.

Plan anchors from the intended motion method:

- A contiguous chain of `N` first-to-last-frame plates needs `N + 1` accepted anchors, because adjacent plates share endpoints.
- A single-anchor image-to-video shot needs one accepted anchor plus a defined end composition and edit fallback.
- A cut between independent shots does not require a fabricated intermediate anchor.

The formula is conditional on the live provider supporting the reference mode. Verify start/end-frame conditioning before committing to a chain. Map every requested timeline interval to its source and intended output; do not leave a long gap hidden behind scene numbering.

## Generate full-size anchors with ImageGen

Establish character/location/style reference packs before disconnected shots. For source characters, use documented face, profile, and body frames from the correct source; generated artwork controls style, not identity. For every anchor, supply the relevant previous/current/next sequence context and label each reference image's role.

Apply the [character and performance contract](generation.md#lock-character-and-performance) before expanding the library: validate likeness, full-body proportions and pose, distinguish supporting characters, and tie expressions to the emotional arc. A user-approved face does not approve a new body, costume, world or action. For recurring worlds, keep an explicit palette and story-state map; a unified grade need not erase intentionally different nightmare and present-life environments.

Generate one asset per anchor. Prompt for the exact story state, composition, action, wardrobe, setting, lighting, identity, and exclusions. Avoid baked captions, logos, UI, and borders unless the storyboard explicitly needs them. When regenerating only for clarity or resolution, attach the current image and request that single change while locking composition, identity, wardrobe, objects, palette, and story state; re-describing the scene can introduce unnecessary drift.

Keep the original ImageGen output byte-for-byte. A generated output may not arrive at the requested delivery dimensions even when the prompt says “1080p”; inspect it and create a recorded derivative rather than claiming the request guaranteed the pixels.

## Enforce one canvas and matte contract

Before the first anchor, copy [anchor-library-policy.json](../assets/anchor-library-policy.json) into the project and resolve its values. For a 1080p landscape project, the frame is exactly `1920x1080`, square pixels, with one consistent active-picture rectangle. If the film is letterboxed, record the exact top/bottom (and any side) matte thickness and color. If it is full-frame, record zero matte. “All images are 1080p” is insufficient when their active pictures or black bars differ.

Normalize each accepted original non-destructively:

1. Detect and remove any baked matte from the source artwork.
2. Center-crop or art-direct the active image to the project active-picture ratio; never stretch people or architecture.
3. Scale the active image to the exact active-picture dimensions.
4. Add the project matte once, producing the exact frame dimensions and pixel aspect ratio.
5. Record original and derivative hashes, crop rectangle, scale, matte, and output path.

If a motion provider requires a different input size, derive every input in that chain from the same accepted active picture. Do not mix canvas geometries inside a chain. Prefer barless active-picture model inputs when a model would animate or corrupt black mattes, then apply the canonical matte once in Resolve; the review/production anchor library still retains the exact 1080p canvas requested by the project.

Run the supplied technical audit before review:

```sh
uv run --with pillow python <skill-dir>/scripts/anchor_audit.py \
  --contract music-video/anchor-library-policy.json \
  --directory music-video/source-of-truth/01-anchor-images \
  --output music-video/anchor-audit.json
```

The audit checks names, dimensions, matte geometry/color, hashes, and possible visual duplicates. It does not judge identity, sharpness, story meaning, or whether a near-duplicate is a legitimate action progression.

## Accept the library as images and as a sequence

Inspect every anchor individually at full size, including 100% detail crops for focal subjects. Reject softness, face/anatomy drift, wrong wardrobe or objects, unintended text, incorrect UI, mismatched framing, or unusable motion composition. Upscaling cannot restore missing detail; regenerate a soft source when it remains visibly poor at delivery size.

Then inspect the chronological contact sheet and compare each changed anchor with at least the nearby sequence needed to understand it—five prior anchors is a useful default for suspected repetition, not a universal fixed count. Reject:

- exact or semantic duplicates that add no new state;
- backward time or repeated action after its consequence;
- unexplained character, setting, costume, or light changes;
- missing approach/reaction/result states;
- inconsistent active-picture geometry or matte thickness;
- large timeline gaps with no declared visual source.

Record `planned`, `generated-unreviewed`, `accepted`, `rejected`, or `superseded` per exact revision. A contact sheet helps sequence review but does not replace full-size inspection. Under `user-gated` mode, provide both the sheet and accessible individual files and stop at the stated boundary.

## Replace without breaking lineage

Never delete or overwrite an anchor in isolation. Create the replacement, compare it in sequence, mark the predecessor superseded, and update every storyboard card, manifest, prompt/job record, model-input derivative, timeline placement, and source-of-truth pointer that consumed it. Re-run coverage and dependency audits. Preserve immutable originals and generation manifests until the dependent film is approved.

Use provenance categories consistently: `generated`, `extracted_from_video`, `derived`, and `superseded`. A timeline-extracted frame is not a generated anchor, even when it is sharp and hash-verified.

## Keep a browsable source of truth

Maintain one chronological production view rather than making people hunt through generation runs. A useful layout has current anchors and original generated videos as the two primary browsing folders, backed by a catalog rather than destructive moves. Use stable sortable names such as:

```text
S03-I02__T013667__office-access-midpoint__openai-imagegen.png
S03-V01__T012760-T017760__first-approach__local-minimax-h3__accepted.mp4
```

The catalog records stable ID, scene/order, exact timeline time/range, current/superseded state, provider/model/job, original and derivative paths/hashes, canvas transform, dependencies, and review evidence. Existing Resolve source paths may remain as compatibility storage while the clean view uses links or byte-identical copies.

If cloud-backed files cannot be opened reliably, create a verified local review mirror with byte counts/hashes. Do not equate a synced placeholder, preview thumbnail, or contact sheet with accessible full-size evidence.

## Motion handoff

Submit only accepted anchors. The handoff names the exact start/end IDs and hashes, model-input paths and dimensions, provider/model/reference mode, intended duration/fps, motion and camera action, protected invariants, handles, fallback, and approval boundary. A technically completed video remains `generated-unreviewed` until downloaded, decoded, watched through at normal speed, and accepted against those anchors.
