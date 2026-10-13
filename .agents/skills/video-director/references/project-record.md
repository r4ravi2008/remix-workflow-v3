# Persistent video project record

Use existing workspace structures where they already serve these purposes. Avoid parallel sources of truth. In a remix workspace, keep `meta.json` authoritative for the chosen audio and pointers/status; put detailed creative work in a `music-video/` directory. Preserve unrelated metadata. Preserve existing `music-video/` paths when resuming a music project. For a new standalone news/story project use `video/project.json` as the index and `meta.json` for workspace identity and pointers/status. A news project needs no song ID, song file or remix-pipeline status.

Record category and format independently (for example `news-byte` and `short`), language, audience, endpoint, resolved workspace, source/content authority, approval mode and intended editor/project/timeline. Create records only for the requested stages. `<video-dir>` means the existing `music-video/` directory or the standalone `video/` directory.

For news/story narration, use `sources.json`, `claims.json`, `script-te.md`, canonical narration and `speech-map.json`, with source/claim → script → voice take → captions/graphics → placements → export dependencies. Keep event/publication/update/access/as-of dates and qualifiers in the source ledger; bind speech cues to the exact narration hash, source-second ranges, spoken text and claim IDs. See [news-bytes.md](news-bytes.md). Do not create song/lyric records for spoken news. For music, the song-specific records below remain unchanged.

Bind each enabled audio role (song, narration, source sound, effects, optional bed) to its version/hash/trim and single owner. Text roles are separate: lyrics, speech captions, headlines, source/disclosure labels, story graphics and titles. A script-only stage has no imaginary audio master.

| Additional record | Minimum useful contents |
|---|---|
| `captions.json` or SRT for spoken video | Native-script text, narration/script revision, actual speech ranges, deliberate transcript/display differences, rendered cue checks |
| `text_events` in `actual-timeline.json` | Every actual text occurrence, stable ID, explicit role, zero-based half-open `start`/`end` frames, including nested captions and disclosures |

Create the applicable shared/category records:

| Record | Minimum useful contents |
|---|---|
| `quality-policy.json` | Category template path, profile, criterion overrides, hard gates, retry limits |
| `quality-manifest.json` | Component versions, artifact hashes, dependencies, evidence, acceptance reviews |
| `brief.md` | Endpoint, fixed/inherited/assumed choices, story/idea/emotional progression, exclusions, current treatment |
| `audio-map.json`, for music | Audio path/hash, duration, source trim, tempo confidence, beat/section events in source seconds |
| `storyboard.md` | Sequence with content/audio, visual and text columns; shot cards; continuity and references |
| `lyric-design.md` or one section of the existing design record, when lyrics are requested | User decisions/open questions, verified title/font references, narrative-state type/motion families, cue/layout bindings, readable holds, rendered pilots and chosen treatment; see [lyric-art-direction.md](../../music-video-director/references/lyric-art-direction.md) |
| `anchor-library-policy.json` | Exact frame, active-picture, matte, naming, and duplicate-audit contract |
| `anchor-catalog.json` | Chronological current/superseded anchors, generated originals, normalized/model derivatives, hashes, transforms, and reviews |
| `anchor-audit.json` | Technical canvas/name/hash/duplicate report; visual checks remain separate |
| `assets.json` | Stable asset IDs, type, source/prompt/job lineage, local path, duration, usable ranges, review status |
| `edit.json` | Timeline settings/start, shot placements, source in/out, speed, transitions, enabled audio/text ownership and source/claim references |
| `actual-timeline.json` and `finish-review-vN.json` for a finished edit | Editor readback of shot and enabled text/lyric ranges and exact-render per-shot/cue/join decisions, with plan/render hashes; see [composition-and-finish.md](composition-and-finish.md) |
| `review.md` | Exact export, checks/ranges, measured/watched/heard evidence, failures, pending items |
| Correction ledger in the existing review record | User request, exact affected range, observed cause, preserved choices, repair, rendered recheck, equivalent occurrences, and open/verified/superseded status |
| Footage run record when GPU generation is needed | Current input snapshot, allowed backend/model/GPU, budget/deadlines, immutable attempt IDs, receipts, downloaded originals, accepted ranges and shutdown readback |
| Upscale evidence in existing asset/edit/review records, when used | Native source/hash and time map, processing host/engine/version/settings, output dimensions/hash, equal-size comparison, per-shot apply/bypass decision, and affected-placement/export review; see [upscaling-and-restoration.md](../../music-video-director/references/upscaling-and-restoration.md) |

Keep one binding block in the existing index: source URLs/content/script revisions, song ID when applicable, each enabled canonical audio path/hash/duration/trim, resolved workspace, selected source catalog/revision, intended Resolve project/timeline, and latest delivery pointer/hash. Compare it with the latest request and live project before mutation. An unrelated open timeline, a familiar folder name or a newer file does not override that binding. Resolve discrepancies from source evidence; ask only when the intended source remains ambiguous. A standalone supplied MP3 needs no invented Suno ID.

For a new film or substantial redesign, also keep the current production stage, its unresolved prerequisites, and the creative-proof path/hash with linked requirement/review evidence in that index. Advance from proof to coverage only after the [production-workflow.md](production-workflow.md) conditions pass. A pending checker report remains part of the current state rather than becoming an attachment ignored by the next stage.

For corrections, retain the predecessor/candidate IDs, actual input lineage, comparison range, and reason to keep or revert the candidate. Record approval scope separately: a script, anchor, motion take, bounded edit, full-video review or publication state. A later rejection reopens the affected scope and its dependents; it leaves other accepted decisions intact.

Acceptance is controlled by [quality-gates.md](quality-gates.md), including components imported from prior work. Check that a project's copied policy still covers the skill's current template before trusting its migration note; keep the manifest and checker result with the handoff. Use explicit statuses such as `planned`, `generated-unreviewed`, `accepted`, `rejected`, `rendered-unreviewed`, and `reviewed`. A file's existence must not promote its status automatically. Separate the requested endpoint from whole-film completion: an accepted storyboard can complete a storyboard-only task.

Example music edit entry, with illustrative values rather than a preset; narration projects bind their voice take and speech map instead of a song/beat map:

```json
{
  "schemaVersion": 1,
  "audio": {
    "path": "../song.wav",
    "sha256": "record-actual-hash",
    "sourceStartSeconds": 42.0,
    "sourceEndSeconds": 72.0
  },
  "timeline": {
    "fpsNumerator": 24,
    "fpsDenominator": 1,
    "startFrame": 86400,
    "durationFrames": 720,
    "width": 1080,
    "height": 1920
  },
  "shots": [{
    "id": "shot-01",
    "assetId": "motion-07",
    "origin": "generated-from-stylized-source",
    "timelineInFrame": 0,
    "timelineOutFrame": 144,
    "sourceInSeconds": 0.5,
    "sourceOutSeconds": 6.5,
    "speed": 1.0,
    "anchor": "opening vocal phrase",
    "status": "planned"
  }],
  "audioOwner": "resolve",
  "lyricOwner": "none"
}
```

All timeline ranges are zero-based half-open offsets, independent of timeline start. Audio/speech-map events remain in original source seconds; subtract `sourceStartSeconds` before conversion. Keep actual render frame count and duration together, since audio length may not land exactly on a frame boundary. Any tiny end pad must be deliberate and must not cut audible content.

Asset lineage should identify the original source frame and timestamp, generated still original, normalized and provider-input derivatives, prompt/revision, generation job, downloaded clip, accepted range, and final shot placements. Classify `generated`, `extracted_from_video`, `derived`, and `superseded` explicitly. Record original-visible interval unions for a footage cap; report stylized derivatives and generated material separately. Do not add overlapping clip durations to claim unique coverage.

Keep a chronological browsing view for current production anchors and original generated videos, backed by the catalog. Stable `S##-I##` and `S##-V##` names plus zero-padded timeline tokens make sequence review possible without making filenames the source of truth. Preserve compatibility paths for live Resolve media; use links or byte-identical review copies instead of reorganizing sources underneath an active edit.

## Resume or revise

Read the latest request and record first, then verify referenced inputs. Reconcile final-file pointers against render manifests, actual media, and the latest accepted decision. Neither a stale metadata pointer nor the newest filename alone establishes the correct version. Retire superseded decisions explicitly. Reuse accepted assets and existing live jobs. Update downstream records only when their dependencies changed:

- New source facts/qualifiers invalidate affected script, narration, captions/graphics and exports. Recheck unchanged wording against new evidence without gratuitous regeneration. Changed words require a new script revision and consumer checks.
- New narration version or trim invalidates affected speech cues, caption timing, placements and exports.
- New music audio version or trim invalidates the affected beat map, lyric timing, placements, and exports.
- New style or identity direction invalidates affected stills/motion and grades, not the selected audio.
- A replaced, removed, re-timed, or re-matted anchor invalidates its model inputs, dependent motion, placements, contact sheets, and renders. Update every consumer and re-run coverage before promotion.
- A rejected shot invalidates its placements and renders, not unrelated accepted footage.
- Aspect-ratio changes require composition/text review and a new export; they do not automatically require every shot to be regenerated.
- A lyric font, motion, placement or narrative-state change invalidates dependent lyric comps, clearance checks, handoffs and exports; preserve accepted picture and audio. Changed cue/audio timing also invalidates animation landings and readable holds.
- A wrapper color change affects the wrapper export, not the accepted Resolve film.

A failed generation should retain its ID, prompt, and rejection reason so resuming does not pay for the same failure again.

Changes to source framing, flips, retimes, nesting or text ownership also invalidate any transition/overlay that copied those settings or sources. Update the live Resolve consumers and render the affected placement. Keep a candidate animatic, a different full-motion branch, and the selected delivery distinct by project/timeline IDs and source hashes. Never promote one merely because another was blocked. See [revision-and-self-review.md](revision-and-self-review.md).

Do not clean provenance, generated originals, accepted anchors, job ledgers, or review evidence merely because a final render exists. First classify files as current source, derived/reproducible, superseded, or unrelated; confirm no active timeline or requested future high-quality regeneration depends on them. Space cleanup is a separate scoped operation with a manifest of what was removed and what remains recoverable.

## Music examples, when this category is selected

- “Here is an MP3. Make a complete 16:9 video: lonely first, hopeful at the end, no lyrics.” Analyze and direct from audio; generate a coherent world and finish in Resolve.
- “Give me three storyboards for this song. Do not generate anything yet.” Deliver treatments and shot plans only.
- “Make a 45-second vertical story from the most moving complete phrase. Use these two characters.” Choose a justified excerpt and maintain identity through a compact arc.
- “Use these clips and beat-sync the edit, no new generations.” Inventory and edit existing material; surface genuine coverage limits.
- “Use only stylized versions of the original frames, none of the original video.” Preserve source lineage while keeping untouched original footage out of the render.
- “Continue this Resolve project. Replace the repetitive middle, preserve the opening and audio.” Inspect and checkpoint the project, revise the specified region, and verify the resulting full export.
- “Keep the song's wistfulness, surprise me visually, and use at most 25% original footage.” Lock emotion and the cap, explore within them, then measure visible original time.
