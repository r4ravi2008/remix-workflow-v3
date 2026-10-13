# Composition, focus, typography, and join review

Read for an edit, revision, or complete render. A technically intact clip can still be unusable in its intended shot. Review source, timeline and final export at their actual viewing sizes. A review candidate may carry unavailable listening or continuous playback as pending; a defect plainly visible in still frames remains a defect to repair.

## Approve the picture before using the shot

For every planned shot, name the focal person, object, or architecture and its intended scale. Define protected content: faces, the top of a head, important gestures, garment/prop action, horizon, and an architectural crown or roofline when it conveys the place. Identify deliberate partial views explicitly. A close-up may crop a shoulder; a head or key structure accidentally severed by the active-picture edge fails.

Inspect the selected source at the actual in/out range before editing or generating dependent material. At minimum inspect first, middle, last and the moment the subject reaches each relevant edge. View at full resolution for detail and at delivery size for composition. Track the subject in motion; a good midpoint cannot rescue an entrance that cuts off the head. Confirm the subject is recognizable and visually dominant when the shot's story purpose requires it. Check focus on the intended subject, not merely overall sharpness of the background. Generated blur, face drift and out-of-focus lead action require rejection or a better range; upscaling or sharpening cannot restore missing detail or a cropped head.

If the source contains the defect, choose a better trim, alternate accepted footage, or redesign the shot. If the edit introduced it, adjust crop, pan, matte or transition carrier, then rerender. Recheck visual continuity and available handles. Do not spend on regeneration without the project's current authorization and cost gate. A shot-specific intentional silhouette, extreme close-up or headless action needs a named narrative/musical purpose and should be balanced against surrounding coverage.

## Design text as part of the frame

Separate speech captions, headlines, source labels, illustrative disclosures, story graphics and music lyrics. Check each role against its actual text and content authority. For factual content, inspect values, dates, attribution and uncertainty as well as fit. Source/disclosure labels must stay readable long enough to establish the role of the accompanying image. Use native Telugu shaping and actual rendered glyphs for Telugu work. The expressive lyric rules below apply only to that music brief; restrained news captions need clear speech synchronization and information hierarchy.

### Music lyrics, when enabled

Legibility is necessary but does not establish good typography. When placement is unresolved, pilot at least two layouts on representative close, wide, bright, dark and moving shots: an allowed negative-space placement within the picture, a restrained edge treatment, or a justified title/card approach. Choose the one that serves the film's look and reading rhythm. When the user has chosen matte/bottom placement, evaluate readable scale, hierarchy and motion within that layout rather than reopening it. Preserve the latest selected weight, style and writing system; see [lyric-art-direction.md](../../music-video-director/references/lyric-art-direction.md).

Judge every cue's entrance, midpoint and exit in the rendered film at desktop and phone viewing sizes. Check actual font glyphs, line breaks, contrast, scale, location, motion, subject clearance and visual integration. Keep title/location cards and lyrics distinct. A geometry-safe cue can still be too small, too low, or disconnected from the action. If a position changes shot by shot, maintain a coherent typographic grammar and avoid distracting jumps. Use the actual rendered cue; a transparent PNG or Resolve setting alone cannot prove the composite.

Use the selected [lyric design](../../music-video-director/references/lyric-art-direction.md) as the comparison, including theme/layout ID, scene emotion and intended entrance/hold/exit. Use each cue's existing `visual_integration`, `legibility`, `subject_clearance` and `timing` observations to record the realized design, fully readable interval, graphic-tail clearance and musical landing; review complete handoffs between lyric families. A generic bottom line or color swap does not pass visual integration when the brief requested physical ink motion or scene-specific typography. Do not impose those effects on a deliberately restrained design.

## Make every join intentional

Build a join inventory from the actual Resolve timeline: every adjacent shot pair, relevant phrase/idea/action boundary, intended visual link, source handles, effect or deliberate cut, and rendered behavior. An API failure or missing transition effect is an unresolved design change. Test another supported Resolve/Fusion route on a duplicate and compare the result in exported frames. An all-cuts solution is valid only when the cuts themselves fulfill the requested visual language and are reviewed as such. Do not call a list of “action, eyeline, light and time cuts” proof without per-join evidence.

For each join, inspect the outgoing clean frame, all transition frames if any, incoming clean frame and the next second. Watch with the intended soundtrack/narration at normal speed when supported. Check focal visibility, size, motion direction, color/light relation, mask edges, carried source time, landing and variety across neighboring joins. A mix of effects needs deliberate recurrence and rests; a string of default dissolves or identical wipes is not polish. If playback cannot be perceived, record the visual inspection and leave cadence pending; do not assert that the transition feels right.

## Audit the exact exported timeline

Export or read back the actual edited Resolve shot and overlay ranges, reconcile them with the plan, and render a versioned file. Use [finish_review.py](../scripts/finish_review.py) to create a review matrix tied to the plan and render hashes:

```sh
python3 <skill-dir>/scripts/finish_review.py --plan <video-dir>/actual-timeline.json --render <video-dir>/render-vN.mp4 --review <video-dir>/finish-review-vN.json init
python3 <skill-dir>/scripts/finish_review.py --plan <video-dir>/actual-timeline.json --render <video-dir>/render-vN.mp4 --review <video-dir>/finish-review-vN.json check
```

The plan uses `frames`, ordered `shots` with stable occurrence IDs and half-open `recordStart`/`recordEnd`, plus optional `lyric_events` and general `text_events`, each with `id`, `start`, `end`; general text also has a `role` such as `captions`, `headline`, `source`, `label` or `story_graphic`. Explicitly role-tagged text `overlays` are also supported. Include every actual rendered text occurrence, including nested captions and disclosures. The legacy untyped `L01` lyric convention remains supported. If a source repeats, give each timeline occurrence its own ID. The helper derives every join and requires a check for each shot, lyric/general text cue and join. Fill `inspected_frames` with real exported frame numbers (opening/middle/closing are the minimum); record concrete observations for composition, critical content, focus, motion, text meaning/design/timing and join execution. A failed observation stays failed until a new render is reviewed. Method changes require a reviewed reason. The helper checks record completeness and render binding; it cannot see pictures or prove the observations truthful.

Run the project quality gate with the current template coverage check too. A project policy copied before a skill revision may omit the new gates; the checker rejects that drift while preserving custom thresholds. If no quality manifest or finish matrix exists, report the exact review gap and keep creative readiness pending. Do all available frame-level repairs before handing off a review candidate. A candidate with unavoidable playback limitations may be delivered only under the user's review mode, with known defects and pending methods stated plainly.
