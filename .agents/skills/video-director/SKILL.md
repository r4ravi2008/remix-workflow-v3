---
name: video-director
description: Direct, produce, revise, and finish videos and Shorts from a story, news item, script, audio, footage, or an existing edit. Use for Telugu news bytes, narrative videos, explainers, and music videos; select the relevant category. Do not use for audio-only composition or upload-only tasks.
---

# Video director

Turn the user's material into a video with a clear purpose, coherent sequence, deliberate sound and readable graphics. Accept any entry stage and deliver the requested endpoint: research, script, storyboard, pilot, finished video, or revision. A planning request authorizes planning; a video request includes ordinary asset preparation. Publication is a separate task.

## Select category and format independently

Read one category before applying its production rules. `short` is a delivery format, not a genre; a music video, news byte or explainer can each have a vertical short and a longer version.

| Category | Read | Content and timing authority |
|---|---|---|
| Music video | [music-video-director](../music-video-director/SKILL.md) | Selected song, verified meaning, section/phrase map; music-specific lyrics and performance rules |
| News byte or factual story, initially Telugu | [news-bytes.md](references/news-bytes.md) | Verified source/claim ledger → native-language script → reviewed narration and speech map |
| Other narrative, explainer or visual story | Shared stages below | User brief, supplied script/footage, narration or deliberate silent sequence; verify factual claims when present |

The music skill is a specialization of this workflow and remains a supported entrypoint. Load the shared workflow once, then apply its music-specific direction and references. Do not send a non-music project through Suno, vocal isolation, beat mapping or lyric alignment. Add future categories as focused references; keep common production and review here.

Record `category`, `format`, language, intended audience, requested endpoint and any fixed choices. Preserve supplied format/duration/voice/style. For a Telugu news byte with no other brief, use an engaging factual voiceover, native Telugu captions, a 45–60-second target and a 1080×1920 vertical canvas. These are adjustable starting choices, not platform limits. Do not create a news episode until the user supplies its item/story.

## Run only the needed stages

Read [production-workflow.md](references/production-workflow.md) for a complete video or substantial redesign and [project-record.md](references/project-record.md) before resuming or mutating a project. Preserve sequential prerequisites when participating in the numbered remix pipeline; standalone news/story work uses the stages here.

| Stage | Work and completion criterion |
|---|---|
| 1. Bind scope and inputs | Read existing metadata and actual sources. Bind workspace, current brief/content/script versions, audio when present, assets and intended editor project/timeline. Check actual viewing/listening and required provider capability. Resolve mismatched inputs before mutation. |
| 2. Establish content and direction | Apply category rules. For factual work verify claims before scripting; for music listen to the song. Define the opening promise, development, turn/payoff and ending, with material requirements mapped to visible/audible checks. |
| 3. Script and plan | Produce the category's content map and chronological shot/graphic plan for the complete requested range. Bind script → narration → speech cues where applicable. Specify the job, source, duration, framing and text for every interval; count missing coverage. |
| 4. Prove the treatment | Test the shortest passage containing the hardest visual/audio/text requirement with its setup and landing. Render in the chosen editor, watch and hear it, and compare against the brief and category checks before expensive coverage. Reuse a verified treatment when its relevant dependencies are unchanged. Script/storyboard-only tasks end before production. |
| 5. Produce coverage | Acquire or generate only the planned missing assets within the selected provider/budget. Preserve provenance, immutable originals and reviewed usable ranges. Inspect every component in its intended context before accepted downstream use. |
| 6. Assemble and finish | Use [resolve-and-review.md](references/resolve-and-review.md). Cut to the category's timing authority: musical phrases, spoken ideas or action. Finish framing, joins, grade, sound and role-specific text; make each vertical composition work through motion. |
| 7. Review and deliver | Review the exact export against the complete brief and category requirements. Repair defects and regressions, run the applicable quality and event checkers, then deliver the requested export and editable checkpoint with honest evidence states. |

For a scoped correction, start with [revision-and-self-review.md](references/revision-and-self-review.md). Reuse accepted stages, preserve unaffected choices and rerun only changed dependencies and their boundaries. Follow the user's approval mode; autonomous review does not create a new approval stop. Ask only for genuinely blocking missing inputs or an explicit collaborative decision.

## Shared production and acceptance

- Use one source of truth. In this repository resolve `.remix-workspace-root.json` and read the selected `meta.json`; preserve existing music project paths. New standalone projects use `<workspace>/<slug>/video/`. No song ID, song file or remix status is required for a news story.
- Read [quality-gates.md](references/quality-gates.md) before accepting components. Select the category template and record its path with the project policy. Imported and generated components need version-bound evidence, accepted dependencies and a passing policy decision. The checker audits records; it cannot see, hear or establish factual truth.
- Plan each shot's contribution to the viewer's understanding or experience. Keep scene, storyboard panel, production anchor, provider input and motion plate distinct. A contact sheet is a review surface. Use the existing [anchor/generation mechanics](../music-video-director/references/storyboard-and-anchors.md) only when those assets are needed; music-specific requirements apply only to music.
- Keep variation within the selected identity, palette and camera/graphic grammar. Count usable screen time, including handles. Repeated loops or provider variants cannot conceal missing story coverage.
- Keep factual evidence, archival/context footage, illustration and reconstruction visibly distinguishable when their presentation could mislead. Category rules control verification and disclosure. Generated pictures cannot establish that a real event occurred.
- Separate lyrics, speech captions, headlines, source labels, story graphics and titles. Canonical Telugu words remain in Telugu script. Check rendered glyphs, meaning, dwell, fit, contrast and subject clearance; do not treat narration captions as lyrics. See [composition-and-finish.md](references/composition-and-finish.md).
- Bind each audio role: canonical song, narration, source sound, effects and optional music bed. Record one owner per role, review the mix, and keep speech clear. A changed script or voice take invalidates dependent cues, timing and exports. Do not alter selected music audio to fit pictures without authorization.
- Use the requested provider and live supported tools. For generated motion read the relevant [generation guidance](../music-video-director/references/generation.md) and [gpu-footage-generation](../gpu-footage-generation/SKILL.md) when needed; apply only relevant character/anchor controls. Use the discovered imagegen skill for image generation. Verify current model/reference capabilities at execution time.
- Resolve is the default editor. Preserve an existing or user-selected Remotion/other supported workflow and read its docs before use. Python/FFmpeg may analyze, extract references and verify exports; do not replace a requested Resolve edit with a montage. Reserve shared Resolve/GPU resources before heavy work and honor live ownership.

## Finish the requested endpoint

Persist artifact hashes, provenance, current/superseded versions, dependencies, source/editor readback and review coverage. Report `MEASURED`, `FRAME-INSPECTED`, `WATCHED`, `HEARD` and user approval separately. A decode, contact sheet, successful API call or rendered job cannot prove the experience. Known defects fail; unavailable perception remains pending under the [diagnostic/production boundary](references/production-workflow.md#when-perception-or-a-required-technique-is-unavailable).

A full replacement includes updated consumers, the correct editor timeline, an integrated export and rendered checks. Review a complete claimed deliverable in motion with sound, including every shot, text cue, join and ending. Deliver actual accessible files and an editable checkpoint; verify any review page and provide a durable file/bundle. Upload, saved draft and public release remain separate provider states requiring their own authorization and readback.
