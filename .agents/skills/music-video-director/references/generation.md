# From sources to usable footage

Apply [quality-gates.md](quality-gates.md) at source selection, still, and motion boundaries. Before expanding a new film or substantial redesign, complete the [creative proof](production-workflow.md#prove-one-edited-passage-before-expanding). When a storyboard or anchor sequence is involved, read [storyboard-and-anchors.md](storyboard-and-anchors.md) first. Only accepted inputs enter the next production stage. Existing assets require evidence too.

## Inventory and coverage

Read the project's existing inventory before generating. Record source URLs or local paths, selected frames with source timestamps, identity references, existing stylization prompts, and which frames already have accepted motion clips. A new render of the same seed frame is not necessarily new coverage.

If source footage is supplied, watch the relevant sequence around each candidate frame. Understand action, relationships, and direction before extracting a pretty still. Select complementary scales, reactions, details, settings, and actions. Record whether the source is permitted in the final edit or is reference-only. Preserve original files; write extractions and derivatives separately. A reference URL is not evidence that a downloaded file is valid or that publication rights are settled.

Compute coverage from accepted usable in/out ranges after trimming failures and providing transition handles. Track reused ranges separately from unique footage. Sum timeline coverage with overlaps accounted for. Do not assume that ten six-second jobs yield sixty usable seconds. Plan extra coverage only where the current edit has a real gap or repetition problem.

## ChatGPT images

Use the installed `imagegen` skill and its supported image-generation tool. Inspect supplied references before editing. For source-derived shots, attach the selected source frame and identity references, preserving facial structure, costume, blocking, and distinctive objects unless the brief changes them. For a new story, establish a character/location reference sheet before generating disconnected angles. Generate each production anchor as a separate full-size asset; do not promote a cropped storyboard-sheet cell or contact-sheet thumbnail as a raw anchor.

A useful prompt specifies subject and action, composition, intended style, lighting/palette, continuity requirements, and aspect ratio. Preserve the already approved workspace style where applicable. Distinguish source-character likeness from a generic “cinematic person.” Avoid unwanted captions, logos, baked borders, and UI text. Generate typography in the editor unless the brief needs it inside the image.

Inspect each still for likeness, anatomy, focal sharpness, continuity, framing, canvas/matte consistency, chronological meaning, and whether it supports the planned movement. Normalize a derivative to the recorded production canvas without stretching while preserving the immutable generated original. Record accepted/rejected status and reason before spending motion generation on it. Review the still both individually and beside its chronological neighbors.

## Lock character and performance

Use this contract for character-led generation and identity corrections. Store it in the existing brief/reference manifest and shot cards rather than creating a second catalog.

| Contract | Bind and compare |
|---|---|
| Identity | User-selected appearance/era; clear face, profile and body references with source time/hash; observed facial width, jaw, nose, eyes, hair and facial hair. Label identity references separately from style and pose references. |
| Proportions and pose | Natural adult anatomy, relative height/build, shoulder/torso/limb relationships, stance and silhouette. Review a full-body view as well as a portrait. |
| Cast roles | Distinguishable leads and supporting characters through faces, silhouettes, wardrobe and blocking. Check a group frame for accidental clones. |
| Performance | Scene emotion and its progression, permitted expression/mouth movement, action and resulting state. Restrained remorse can use breath, sweat, gaze and posture; a cheerful smile or speaking mouth changes that performance. |
| Continuity | Stable appearance, costume, consequential props and each world's selected palette. Intentional world differences remain distinct while the character stays recognizable. |

Choose references that match the current requested appearance; a mix of incompatible ages, builds or facial-hair states can undermine the contract. Attach the accepted full-size identity/style anchors to each relevant job, and verify the actual submitted input bytes. An actor's name in prose or an old approval does not prove that the current model received the right reference.

For repeated face/proportion drift, compare the source references, accepted anchor, normalized/provider derivative, generated take and rendered placement in that order. Locate where the mismatch first appears. Repair an incorrect anchor or derivative before generating more dependent motion; if the anchor is correct, inspect conditioning, prompt conflicts and model behavior. Request anchor selection only when the user has set that gate. Under autonomous review, apply the same contract and preserve alternatives.

Test a close-up, full-body/action shot and any required real-to-stylized handoff before expanding a character-led batch. Compare at useful full resolution and in motion; a good portrait cannot certify later body proportions or facial stability. Preserve a previously better take when a retry regresses, following [revision-and-self-review.md](revision-and-self-review.md).

## Choose and verify the motion provider

For RunPod or a local network GPU controlled through Herdr, use [gpu-footage-generation](../../gpu-footage-generation/SKILL.md). It provides source snapshots, setup/transfer pilots, measured cost controls and resumable job receipts. Read the user's latest generation restriction first; possession of an older RunPod plan does not authorize new GPU work during an existing-footage-only edit.

Honor an explicit provider or model choice. Otherwise choose from the providers that are live in the current environment based on the shot's reference needs, identity-continuity risk, duration, aspect ratio, cost, and the user's existing account or project library. Record the provider and exact model per job; do not describe an aggregator as though it were the underlying model.

Use Executor's `openart` integration for OpenArt or a MiniMax model offered through OpenArt, following [openart.md](openart.md). Use Grok through its supported browser flow. Do not silently fall back between providers after an unavailable model, exhausted credits, or a failed job: preserve the attempt and obtain direction unless the brief already authorizes provider flexibility.

## Generate motion

Discover current tools or use supported browser control. Use the user's chosen existing browser/tab when specified. Inspect the current account or workspace, credit state, generation options, duration, aspect ratio, and available reference modes; provider capabilities can change. Do not assume start/end-frame conditioning exists just because an earlier task requested it.

Bind each job to accepted anchor IDs, revisions, hashes, and provider-input derivatives. All inputs in one chained sequence must share the same dimensions and active-picture geometry. If the provider should receive a barless active picture, derive it consistently from the accepted 1080p anchor library and reapply the project matte once in Resolve.

Two useful intents:

- In-frame motion: animate an accepted frame with a simple subject action and a coherent camera path. Preserve composition/identity throughout.
- Frame-to-frame bridge: connect deliberate start and end compositions if the current provider supports both references. If unsupported, generate compatible shots separately and bridge them in Resolve; label this as an editorial solution rather than a conditioned generation.

Prompt card example:

> Use the attached accepted frame as the visual reference. Keep this character's facial proportions, hair, clothing, and the scene's soft amber/indigo palette. Begin in a medium view beside the window; drift laterally as the fabric moves once in the breeze. End with the reflection occupying the right third. Quiet, unhurried movement; stable face and hands; no speaking or singing, added text, scene jump, or extra person. Leave the left lower area clear for optional lyrics.

Adapt that card to the song. A negative prompt cannot guarantee identity or motion quality. Before a batch, prove the pilot's intended face, body or building and its critical edges stay visible and focused through the usable interval. A sharp background with a soft lead or a head clipped by the generated camera fails the shot even when the file decodes. Watch the entire generated clip, including its ending. Inspect face drift, hands, unintended speech, morphing, flicker, and camera discontinuities. Download the actual video and probe it. A completion badge, remote URL, or cached thumbnail is insufficient evidence of a usable local asset. Retry authenticated download if needed; never accept an HTML/XML error saved with an `.mp4` extension.

Keep editor notes outside the model prompt. Phrases about future messages, subtitles or editing software can cause generated lettering even when the intent is to leave the area empty. Describe the visible blocking and negative space instead. For quick editorial cuts, plan complementary actions/angles with clean usable moments and handles; do not generate the same slow portrait repeatedly and expect transitions to create coverage. Review the fixed musical shot boundaries in an animatic before expensive infill when those boundaries will become conditioning constraints.

Use modest batches tied to coverage needs. Reuse completed job IDs after interruptions rather than resubmitting blindly. Within user limits, simplify failed actions or regenerate rejected shots. Use the project quality policy's attempt limit. When it is reached, change the shot design or report the specific limitation; do not run an unbounded loop or exceed a supplied budget. A successful provider response is still `generated-unreviewed` until the local media is downloaded, technically verified, watched, and accepted under the project quality policy.

## Realistic-to-stylized continuity

Keep native motion originals available for the optional [upscaling finish](upscaling-and-restoration.md). A normalized delivery-size plate is a derivative, not evidence of native detail. Accept identity and motion before enhancement; do not try to repair a failed performance through sharper pixels.

Pair a source frame with its stylized version using pose, scale, eyeline, light direction, and motion. Transition at a useful occlusion, gesture, or graphic match. Inspect both sides in motion. Avoid a dissolve between mismatched faces or an unmotivated change of identity.

For a reference-only brief, original clips never enter the final timeline. For a hybrid brief, measure original footage by timeline visibility. Track stylized derivatives separately so “mostly generated” cannot disguise extensive untouched source reuse. Resolve dissolves conservatively: count any interval where original footage is visible toward an original-footage cap, and report this method. Multiple original layers in one interval count once.

Slow motion must serve the action. Inspect source cadence and any interpolation before accepting the retime. Do not stretch a short clip through a whole verse to meet coverage. Generate an additional action, angle, or setting that advances the motif instead.

For quick action, specify readable action beats with setup, contact/consequence and reaction, plus complementary angles and clean edit handles. Judge the physical performance separately from shot length: cutting a slow portrait faster does not create fast action. Keep hands, weapons and contact with fabric/objects physically coherent through the usable range. Replace broken contact or frozen action with better coverage; reserve retiming for motion that survives the intended speed. Intentional returning nightmares or motifs must change the action, framing or emotional consequence rather than replaying the same range without development.
