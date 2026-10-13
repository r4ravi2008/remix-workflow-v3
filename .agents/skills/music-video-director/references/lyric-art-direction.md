# Lyric art direction and performance

Use when lyrics are requested, especially when the user wants personality, kinetic typography, transliterated lyrics or distinct narrative worlds. Design from the song, story, current shot and established titles. Text should feel authored for this film; a permanent bottom coordinate is not the default. A restrained subtitle treatment remains valid when chosen deliberately.

## Place the pass in the workflow

During the brief/storyboard, establish writing system, mood, references and likely lyric-safe areas. Keep temporary timing captions clearly provisional. Once scene order, vocal timing, principal transitions and grade are stable enough, develop and compare lyric treatments over actual moving footage. Do this before the full lyric rollout and final export; do not wait until the film is flattened. Fine-tune after any picture/upscale change that affects contrast, geometry or placement. Typography remains independently editable in Resolve/Fusion, with one lyric owner.

This is a creative design conversation when requested, not a new unconditional approval gate. Reuse decisions already supplied. Ask one to three concise, concrete questions only about unresolved choices, with a recommendation and short options when useful. Continue independent timing/clearance work while optional preferences are pending. If the user explicitly wants to select a pilot, obtain that selection before full rollout; otherwise use the existing autonomous review mode and record assumptions. Do not replace a requested collaboration with a finished generic preset.

Useful questions, selected for the actual uncertainty:

- **Personality and intensity:** restrained cinematic, expressive motion on key phrases, or frequent kinetic emphasis? Show what changes in the picture.
- **Typography and reference:** inherit the verified title-card lettering, adapt a supplied reference, or compare two readable families? Show the same real lyric in context.
- **Placement and rhythm:** stable positions within each scene, occasional hero words in negative space, or a specific user layout? Confirm line-level versus word-level emphasis only if unsettled.

Do not re-ask a fixed language, palette or effect. A reference such as “Tim Miller vibe” is a creative cue to translate into visible qualities and preview, not a complete font or animation specification. Inspect supplied visual references and actual title comps before claiming to match them.

## Record a small lyric design

Use `music-video/lyric-design.md` or a clearly named section of the existing design record, with one authoritative copy. Link existing text/cue files instead of duplicating the lyrics. Record:

| Decision | What the next pass needs |
|---|---|
| Bindings | Canonical audio and display-text versions/hashes, cue revision, timeline/fps, frame coordinate convention, and inspected title/reference versions |
| User choices | Fixed decisions, open questions, assumptions, review mode and selected pilot; a proposed look is not user approval |
| Shared type system | Exact available font family/style and verified fallback, size/line limits, tracking, case, stroke/shadow, safe margins and readable contrast |
| Narrative states | Stable theme IDs and scene/cue mappings, emotional role, palette/material, allowed positions, animation intensity and recurring motifs |
| Motion grammar | Entrance, readable hold and exit; musical landing, easing, restrained fallback, accent density/rests, and behavior across theme changes |
| Cue exceptions | Existing cue ID, shot/state, layout/position, emphasis, readable interval, animation range, effect extent and exception reason |
| Evidence | Actual rendered pilot paths/hashes, alternatives considered, chosen treatment and per-cue/full-export review |

Store exact cue timings and placement overrides in the existing cue/edit manifest. Keep vocal timing separate from decorative animation timing. Add theme/layout IDs there so an implementation cannot silently reduce the design to one global font and bottom offset. Screen position can stay stable within a scene while material or motion changes meaningfully.

## Build a coherent family, then compose each cue

Choose a small number of treatments from the narrative states, rather than a different font every shot. Scene emotion and lyric meaning guide the state; “real footage” versus “anime” is not itself an emotion. Let framing, subject movement and lyric length determine placement within that family. Use clear negative space, align with useful visual axes and protect eyes, hands, weapons and story props. Track text into the world only when that perspective is desired and the track can be verified. Avoid random position jumps that make the viewer hunt for each line.

Connect the lyric and title designs through shared proportions, edge treatment, palette or motif. A display font that works for a two-word title may need a more readable companion weight/family for long lines. Verify installed glyphs and rendered font output, including Romanized vowel combinations, punctuation and any requested diacritics. Preserve syllables and word order; do not turn transliteration into translation or guessed English. Keep native canonical text separately, follow the user's explicit display choice, and do not ask them to reauthorize an already requested transliteration.

The latest user-selected treatment controls this pass. When the user chooses thin italic lettering or lyrics in the top/bottom mattes, record that choice and apply its actual weight/style/placement. Evaluate hierarchy, contrast, readable holds and fit there while preserving approved picture/audio. The `visual_integration` criterion and `lyrics_integrated_in_picture` gate mean integration with the selected composition, including deliberately chosen matte placement. They do not require moving text back over the story or restoring superseded kinetic effects.

Outline or shadow must work against the moving background, including bright flashes and red-on-red scenes. Judge stroke thickness after final scaling: it must separate the letters without filling their counters. Spaced modern lettering still needs readable word grouping. Decorative texture should leave the letterforms intact.

Design **entrance → readable hold → exit** as one performance. A falling line should settle into a stable reading position; a blood/ink trail should support its arrival rather than cover the words. Land selected impacts on verified vocal or musical accents, using a short lead-in where appropriate. Maintain enough fully readable time while the phrase is heard. Reserve large impacts for meaningful words/phrases and allow quiet cues. Do not make every word bounce, slide or flash on every kick. Word-level animation requires verified word timing; use phrase-level motion when only line timing is reliable.

For a line spanning a picture or narrative-world transition, choose a deliberate handoff: retain the readable line while its material/palette changes, or split at a verified phrase boundary. Preserve text position and meaning through the handoff unless a composed move is justified. Do not restart the same sung words, create duplicate layers or carry an outgoing ink/blood effect into an unrelated intimate scene. Effect tails need their own bounds, not just the lyric clip's nominal cue range.

## Example: ELA ELA × OG2 user direction

This table preserves the film's initial exploratory brief. On 2026-09-30 the user subsequently selected thin italic lettering and then top/bottom black-bar placement while keeping the film intact. That later scoped choice supersedes the earlier placement/intensity wherever it conflicts. Read the current correction ledger before reusing this example; neither stage is a universal preset or evidence of a verified implementation. Inspect the actual title card before deriving any complementary family.

| Narrative state | Typography and material | Motion and composition |
|---|---|---|
| Nightmare / former violent life | Readable Roman transliteration with Japanese-inspired brush/cut letterforms, crimson emphasis and a contrast-tested outline or keyline. Keep letter identity clear; Japanese influence does not require replacing Latin words with decorative Japanese glyphs. | Graphic blood/ink trails accompany a short downward arrival and controlled impact, then settle for reading; use brush/slash accents and restrained textured exits. Translate the user's Tim Miller reference into bold title-sequence rhythm and physical ink motion, with a rendered pilot. |
| Love / present life | Cool blue or cyan accents, modern spacious lettering with a subtle futuristic quality, related to the Panjaa-inspired ELA ELA side of the title. Use a readable weight and measured tracking. | Gentle lateral/opacity reveals, controlled spacing changes or a fine light trail, then a calm hold. Preserve remorse and restraint until the story earns relief. |
| Passage between worlds | Shared scale, alignment and recognizable words bind the two families. | Let an ink trail thin into a blue light stroke, or change outline/material while the line remains readable. Preview the complete real-to-anime transition with the lyric, not two disconnected style stills. |

Crimson here is a lyric accent; it does not authorize recoloring the first nightmare's blue Japanese environment. The title reference guides the family, while long lyric lines need their own legibility test. A possible progression is stronger ink impacts early and lighter traces as healing develops; treat that as a proposal unless the user selects it.

## Render pilots, apply and review

Render short samples over the actual graded footage and canonical audio: each distinct narrative state, a state transition, a long line and the hardest moving/bright/busy background present. Compare meaningful alternatives on the same lyric and shot so the user can judge personality, placement and intensity. Static style frames help choose type; the motion brief needs motion previews. In collaborative mode, discuss the concrete previews instead of asking for an abstract font decision.

Build the selected design with supported Resolve/Fusion text, masks, paths and compositing controls. Keep readable text editable; do not generate the lyric lettering inside video footage. Reusable comps can parameterize text, family, colors, outline, position, entrance/hold/exit and accent strength, with per-cue overrides. A color-only subtitle preset does not implement a falling-ink entrance. If an effect cannot be realized, record that unmet choice and test a supported equivalent under the existing review mode rather than silently reverting to bottom captions.

Apply the accepted design across the full cue list. In [composition-and-finish.md](composition-and-finish.md), record for every cue its theme/layout, full readable interval, protected-subject clearance, and actual entrance/exit behavior; inspect all theme handoffs and effect tails. Use the existing lyric criteria for visual integration, motion quality, placement, legibility and timing. Evaluate personality as well as correctness: the words must belong to this scene, remain readable through motion, and preserve the story's emotional register.

Render and check the complete requested film in Resolve using [typography-and-story-graphics.md](typography-and-story-graphics.md) and [resolve-and-review.md](resolve-and-review.md). Confirm one lyric owner, unchanged song/timing, all cues covered and the correct ending. Report actual frame, watch and listening coverage separately. Finish with the full updated film when requested, not only the typography pilot.
