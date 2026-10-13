---
name: music-video-director
description: Music-video specialization of video-director. Direct and finish a song-driven film or Short in DaVinci Resolve from audio, storyboards, footage or an existing edit, with musical timing, continuity and optional kinetic lyrics. Use video-director for news and non-music stories; do not use for audio-only composition or upload-only tasks.
---

# Music video director

Turn the particular song's emotion and musical progression into a coherent film. Accept any language and any entry stage: an MP3 alone, an existing remix workspace, source footage, selected frames, a storyboard, generated clips, or a Resolve edit. Deliver only the stages requested. A storyboard request does not authorize generation; a video request includes the ordinary asset preparation needed to make it.

## Apply the shared workflow, then music direction

Read [video-director](../video-director/SKILL.md) once for the shared ordered stages, input/editor binding, component acceptance, production proof, revisions and exact-file delivery. This skill supplies the music category; do not route back through category selection. Preserve numbered-pipeline prerequisites when participating in the remix pipeline. A supplied finished song needs no new audio generation. Existing `music-video/` workspaces, policies and checker commands remain supported.

| Shared stage | Music-specific work |
|---|---|
| Bind | Read the repository workspace config and selected metadata; bind song/source ID when present, canonical audio path/hash/duration/trim, selected source catalog and intended Resolve project/timeline. Reconcile disagreements before mutation. |
| Direct | Listen through the selected song and read [direction.md](references/direction.md). Build the heard section/event map, emotional or motif progression, character/source-world relationship and requirement-to-evidence brief. Unsupported lyric interpretation remains provisional. |
| Plan | Read [film-language.md](references/film-language.md) and [storyboard-and-anchors.md](references/storyboard-and-anchors.md). Plan complete chronological coverage, musical turns and risky handoffs; every shot develops action, relationship or motif. |
| Prove | Read the shared [production workflow](../video-director/references/production-workflow.md). Render the shortest complete musical passage proving the hardest creative requirement with the canonical song, grade, source/generated handoffs and risky performance/text treatment. Watch/hear it before batch coverage; obey the configured approval mode. |
| Produce | Read [generation.md](references/generation.md). Accept chronological anchors and whole usable motion ranges; failed required character/world tests return to design/proof. |
| Finish | Use shared [Resolve assembly/review](../video-director/references/resolve-and-review.md). Cut to phrases/bars/selected accents. If lyrics are requested, define their personality and run [lyric-art-direction.md](references/lyric-art-direction.md) against stable moving picture before rollout. |
| Deliver | Review the exact export in motion with its selected song and run shared correction/event review plus the music quality policy. Deliver the requested range/full film and editable checkpoint with separate measured/frame-inspected/watched/heard evidence. |

Read shared [quality-gates.md](../video-director/references/quality-gates.md) before accepting components, using this category's [quality-policy.json](assets/quality-policy.json). The compatibility [quality_gate.py](scripts/quality_gate.py) defaults to that music template. Imported and generated components must pass current version/policy evidence before accepted downstream use; budget exhaustion never lowers the bar. For corrections, read shared [revision-and-self-review.md](../video-director/references/revision-and-self-review.md), preserve unaffected choices and repeat only invalidated work.

## Choose the work needed

| Need | Read and produce |
|---|---|
| Understand emotion, explore directions, choose a Short | [direction.md](references/direction.md): brief and audio map |
| Configure transitions, boomerangs, beat accents, or motion graphics | [transitions-and-motion.md](references/transitions-and-motion.md): project effect policy, event plan, and rendered evidence |
| Design shots, scenes, story, or transitions | [film-language.md](references/film-language.md): storyboard and shot cards |
| Build or revise a storyboard and its still anchors | [storyboard-and-anchors.md](references/storyboard-and-anchors.md): complete chronological anchor library, normalized production canvases, and an approval boundary |
| Extract/stylize frames or generate video | [generation.md](references/generation.md): verified asset inventory |
| Generate on rented or local GPUs | [gpu-footage-generation](../gpu-footage-generation/SKILL.md): RunPod or Herdr execution, verified transfers, resumable jobs, and reviewed footage |
| Give lyrics a personality tied to the story and scene | [lyric-art-direction.md](references/lyric-art-direction.md): collaborative brief, theme/font/motion system, rendered pilots, and cue-level application |
| Implement lyrics, messages, titles, or tracked text | [typography-and-story-graphics.md](references/typography-and-story-graphics.md): separate text roles, fit, timing, and subject clearance |
| Assemble, retime, add lyrics, export, or revise | [resolve-and-review.md](references/resolve-and-review.md): Resolve timeline and review |
| Improve low-resolution footage or prepare an upscale finish | [upscaling-and-restoration.md](references/upscaling-and-restoration.md): source-level Super Scale comparison, selective application, and full-film verification |
| Prove shot framing, subject focus, lyric integration and transition quality | [composition-and-finish.md](references/composition-and-finish.md): source and render inspection, per-event review matrix |
| Correct rejected work or validate before presenting | [revision-and-self-review.md](references/revision-and-self-review.md): defect diagnosis, bounded repair, regression checks, and review coverage |
| Resume, hand off, or change one part | [project-record.md](references/project-record.md): minimal persistent state |
| Reuse a choice or diagnose a recurring correction from Yemi, Udi, Yekantanga, Urvashi, Hello Ammayi, or Panda | [workflow-evidence.md](references/workflow-evidence.md): scoped examples and recent correction patterns |

Read only the relevant references. Use the discovered `imagegen` skill for ChatGPT image work. For motion, use the provider the user selected; when that provider is OpenArt or MiniMax through OpenArt, read [openart.md](references/openart.md) and use the live `openart` integration exposed by Executor. For Grok, discover its current browser capabilities. Use installed `resolve-mcp`, `resolve-edit`, `resolve-fusion`, `resolve-media-analysis`, and `resolve-delivery` skills as needed. Live tool schemas and current documentation determine implementation; do not assume a historical model, duration, price, or reference mode still exists. If a dependency is unavailable, complete independent planning/preparation and report the specific blocked stage.

## Creative rules

- Build a visual argument for this song. State the emotional beginning, change, and ending, or the abstract motif's development. Avoid a random slideshow of attractive images.
- Keep `scene`, `storyboard panel`, `production anchor`, `model input`, and `motion plate` distinct. A multi-panel illustration or contact sheet is a review surface, not a set of production-ready motion anchors.
- Resolve effect choices into `music-video/effects-config.json` using [transitions-and-motion.md](references/transitions-and-motion.md). Respect an explicit minimum style count and recurrence requirement; verify distinct rendered styles, not just labels or directional variants. Configure motion graphics, boomerangs, and rhythmic shot patterns separately from scene transitions. Protect visible singing from reverse/shuffle edits; source-match it to the remix vocal and review lip sync.
- Treat beat sync as a hierarchy of phrases, bars, accents, movement, and occasional cuts. A repeating zoom jerk on every other beat is not an adequate interpretation.
- Keep variation inside the brief's identity, palette, emotional range, and camera grammar. Let the user lock any of these. Propose alternatives when requested; otherwise choose a coherent direction and record why.
- Count how much usable footage each section needs. Generate missing coverage instead of disguising a shortage with repetitive loops. Reuse can be intentional, especially returning motifs, but show how the return develops.
- Original footage, restylized source frames, generated animation, and stills are distinct categories. Measure the requested mix by visible screen time, not clip count. A historical 20–30% original-footage choice is not a universal default.
- Preserve recognizable characters when requested. Use the [character and performance contract](references/generation.md#lock-character-and-performance) for likeness, proportions, emotional state and supporting-cast distinction. When repeated takes share a defect, trace their accepted anchor and actual model input before another retry. Use original characters when no source identity is requested.
- Treat consequential props and interfaces as story facts. A message, calendar, badge, clock, or phone screen must communicate the intended action and chronological state; attractive but incorrect UI fails the shot.
- For environment-only music-reactive effects, use [the background treatment](references/transitions-and-motion.md#environment-only-music-response). Protect people, lyrics, titles and consequential props throughout movement; a global shader does not fulfill that scope.
- Give narrative scenes and abstract intercuts different jobs. An insert may add energy without moving the story into its location. Maintain the relationship's progression through distance, eyeline, approach, reaction, and consequence; attractive anchors that skip those steps fail continuity.
- Keep the selected song as the audio master. Do not regenerate vocals or retime the song to fit pictures unless asked. Avoid generated singing mouths unless their actual synchronization can be verified.
- Lyrics are optional. Keep canonical words in their original script. Translation and transliteration are separate choices; follow explicit user direction and repository constraints, and clarify only when those conflict materially. Never infer that every video needs English text.
- Requested lyric presentation should carry the film's personality through type, placement, material, motion and musical timing. Use a small coherent family of scene/story states, with readable dwell and deliberate transitions; changing text color alone does not fulfill a kinetic typography brief. Preserve a user-selected understated subtitle treatment when that is the intended design.

## Finish the requested stage

Persist enough state to resume without regenerating accepted assets. Keep immutable generated originals, normalized derivatives, provenance, current/superseded status, and updated downstream references. Report deliverable paths, what was rendered or generated, what was actually watched/heard, and any remaining limitation. Review final exports in motion with sound; contact sheets and metrics alone cannot prove pacing, identity stability, lyric sync, or emotional fit.

A replacement requested for an existing film is complete only after its consumers are updated, the correct Resolve timeline is read back, and the affected edit is rendered and checked. For a full-film revision, integrate a proven diagnostic into the complete review film so its pacing and neighbors are visible. Before presenting, run the per-event finish matrix, review protocol and quality checker on that exact revision. A generated asset, successful API call, or technical render alone does not complete an edit. Follow [the diagnostic/production boundary](references/production-workflow.md#when-perception-or-a-required-technique-is-unavailable): a review-candidate label does not authorize scaling an unproven treatment or bypass failed quality targets. Use the user's configured approval mode; do not create a new human approval stop where autonomous review is authorized.

Use Resolve to assemble and finish the film. Python/FFmpeg may analyze media, extract reference frames, or verify exports; do not substitute an FFmpeg montage for a requested Resolve edit. Remotion framing is optional and requires a request or existing brief. Upload/publication is a separate task and is never implied by finishing a render.
