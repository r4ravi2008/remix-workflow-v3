# Workflow evidence and its limits

Recorded 2026-09-17 from the two Codex task histories and local workspace artifacts. These examples explain choices and failure modes. They are not current provider state or mandatory presets. Resolve workspaces through the repository's `.remix-workspace-root.json`; paths below are relative to that root.

## Yemi Cheyamanduve

Task: `Create DaVinci beat-synced video`, UUID `01a09888-85c9-78b3-aa36-aa0d3f9d5469`.
Workspace: `yemi-cheyamanduve-deep-house-somber/`.

The user progressively requested source-derived stylization, Grok motion, original-character likeness, more coverage, energetic crop transitions, varied swing rather than repeated zoom jerks, and lyric placement away from faces. Original footage was eventually excluded from the film. Later corrections removed public-facing production labels and repaired lyric drift after about 3:40. These instructions belong to that song and its revisions.

Useful evidence:

- `yemi-cheyamanduve-deep-house-somber-davinci-edit-plan.json`: section map, beat analysis, scene/cut candidates, event plan.
- `bridge-plan.json`: anchor-to-anchor transition concepts using reflections, cloth, and related motifs.
- `build-resolve-refined-v4.py`: historical Resolve/Fusion assembly and crop/lyric treatment. Inspect APIs before reuse.
- `lyric-placement-audit.json`: 46 V4 cue midpoint frames and 19 placement corrections.
- `davinci-previews/v5-tail-lyric-sync/v5-tail-lyric-contact-sheet.jpg`: targeted late-song correction evidence.
- `phase-two-public-showcase-v5-lyric-sync-render-manifest.json`: corrected Resolve video embedded in Remotion, with the video muted and the canonical repaired WAV supplying sound.
- `yemi-cheyamanduve-deep-house-somber-phase-two-public-showcase-v5-lyric-sync.mp4`: later public-layout export found during this investigation.

The beat analysis and public BPM descriptions disagree. Re-measure the selected audio instead of borrowing a style-prompt BPM. Also, the workspace's older `files.final_video` pointer did not identify the latest public V5 export. Reconcile filenames, manifest lineage, actual file contents, and the user's latest selection before acting. Newest filename alone is not authority.

Later vertical-recut tasks (`01a0ae68-2173-7872-bbfd-01abb35c7a27` and `01a0afd0-aa7b-7e32-887b-4c3319e7fe7a`) showed that a technically valid portrait crop could still miss faces and focal actions. The user required shot-specific selection/repositioning, mobile lyric placement, scene contact sheets, and a Remotion frame in which the film occupied roughly 80% of the composition. Treat focal framing, focal sharpness, and wrapper prominence as separate checks.

## Udi Udi

Task: `Locate udi udi workspace`, UUID `01a0a3e4-71df-7562-9783-485f9d69c445`.
Workspace: `udi-udi-deep-house/`.

The user requested a mellow, soulful, ethereal film with smooth minimal transitions, then rejected an edit that leaned too heavily on untouched original footage. The correction called for roughly 20–30% original material and enough generated stylized footage for the full song. This is the origin of that mix range; do not silently impose it on later songs.

Useful evidence:

- `video-production.json`: records rejection of the original-heavy treatment.
- `video-production-v3.json`, `channel-vibe-audit-v3.md`, and `davinci-assets-v3/visual-edit-manifest-v3.json`: the Liminal Indigo Pavilion treatment, indigo/plum/oxblood/silver palette, fabric/water/reflection motifs, and coverage.
- Manifest counts: 144.4-second song, 33 segments, 30.395 seconds of original source, about 21.05%. These are historical manifest measurements, not a fresh opacity-aware visibility audit.
- `build-resolve-udi-liminal-v3.py`: historical assembly implementation.
- `renders/udi-udi-deep-house-liminal-indigo-resolve-master-v3-fixed.mov`: Resolve mezzanine.
- `renders/udi-udi-deep-house-remotion-showcase-v5.mp4` and `render-receipt-v5.json`: later Remotion delivery and receipt.
- `.analysis/udi-remotion-v5/contact-sheet.png`: visual sampling evidence.

Four/eight-bar holds and restrained accents were choices for this treatment. Environment shots, partial profiles, silhouettes, fabric, and hands reduced dependence on unstable generated singing faces. They are useful alternatives when likeness fails, but must not silently replace a requested character performance.

## Shared lessons

Both workflows distinguish still anchors, generated motion, Resolve assembly, and optional Remotion presentation. Existing prompts can supply continuity, but a new MP3-only project must be able to establish its own look. Repeated seed images produced repetitive coverage; new angles/actions were necessary. Generated lips and facial drift required rejection, not just more transitions.

Contact sheets, decode checks, hashes, render receipts, and sampled timeline review exist in these workspaces. They support technical completion and targeted visual corrections. This investigation did not independently watch and listen to both full final exports, so it does not certify whole-film creative acceptance.

The shared-record sweep used repository git/history/docs and local workspace manifests/scripts. Unrelated tickets, team chat, runtime observability, and analytics were outside these two personal media workflows. Provider pages and the live Resolve project were not mutated or audited for this skill-writing task.

## Yekantanga

Task: `Create Yekantanga Unna storyboard`, UUID `01a0ad96-78dd-7f21-9a90-9a0c1f4c8ba4`.
Workspace: `yekantanga-deep-house/`.

The visible storyboard needed prompts directly under each anchor, followed by end-to-end generation and Resolve assembly rather than a detached prompt list. Provider limits interrupted Grok generation; the resumable ledger and incomplete Resolve checkpoint were therefore part of the deliverable state. Later requests added full-frame preservation, Resolve upscaling, provider mixing across the whole film rather than clustering one provider by section, aggressive shot-selection patterns, source-performance lip sync, source-character references, and stylization of original footage.

Useful corrections:

- A generated-job count is not usable coverage. Record accepted trimmed duration, handles, repeated ranges, and gaps.
- Preserve provider job IDs and quota failures; resume missing slots rather than regenerating completed work.
- Mixing provider styles is an editorial design problem. Distribute and grade them deliberately instead of letting chronology expose the provider switch.
- Original performance footage with visible singing must be selected against the remix vocal phrase and kept forward. A matching lyric title does not prove lip sync.
- “Captions” later meant lyrics, not invented scene narration. Text semantics and ownership must be explicit before typography work.

## Urvashi storyboard, anchors, and motion repair

Primary task UUIDs: `01a0b383-59ac-71a3-8f07-27e78816d7b6` (direction and illustrated storyboard), `01a0b653-8ccb-7712-95ef-715a329f2b0d` (forensic range corrections), `01a0b840-676a-7c90-81f1-1041f30984ae` (anchor-chain infill and later correction), `01a0bb51-03be-7d12-be6b-f029e647ceb0` (generated-anchor source of truth), and `01a0c157-469b-7340-8044-523ea1841391` (full-size local review and replacements).
Workspace: `urvashi/`.

The first timed work was invalidated when the user corrected the selected song. Later, multi-panel storyboard crops were too soft for production; multiple images also had mismatched active-picture geometry and black bars. Full-size review found blurry anchors, repeated story states, a calendar-like phone interface where a messaging action was intended, and duplicate/regressive invitation, bridge, cab, and ending frames. Replacements had to update every consumer rather than merely change a file in one folder.

The durable current evidence is under `music-video/source-of-truth-v1/`: 47 current anchors are normalized to exact 1920x1080 frames with a shared 1920x790 active picture and 145-pixel top/bottom matte. `catalog.json` preserves generated originals, transformations, hashes, provider lineage, and current/superseded state. This is an Urvashi contract, not a universal matte preset. The chronological naming scheme uses scene, within-scene item, and zero-padded timeline milliseconds.

The opening demonstrated the anchor arithmetic: four contiguous two-second first/last-frame plates required five anchors, so three missing intermediate stills were generated before H3 motion. All provider inputs in that chain used one 1088x448 active-picture canvas. The 8-second Resolve review preserved later material and canonical audio, used handled joins, and found no technical black frames or incomplete masks; human creative approval remained a separate gate.

Resolve review then exposed different failures from asset generation:

- Slow/incomplete masks, arbitrary black overlays, and fades were not corrected by deleting all transitions; the intended geometric language needed shorter handled implementations.
- Incoming footage was sometimes shown during an outgoing Fusion transition and restarted at the cut, making time appear to run backward. Source-time event order and transition preloads need explicit auditing.
- Contact sheets revealed macro order, but normal-speed playback was still required for motion direction, pacing, sharpness, and sound.
- A kick grid alone did not express the song. Structural, vocal/lyric, harmonic, bass/texture, and selected rhythmic cues needed a hierarchical event map.
- The full technical delivery could be probe/decode/hash/black/freeze verified while still remaining pending for watched-and-heard creative approval.
- A later full-film review found a dark translucent overlay plus teal/red guide-like shapes after 2:32 and requested a project-specific no-static policy. Black-frame scans alone were insufficient for the overlay, while freeze detection still required visual classification of intentional versus broken holds.
- The request for “generated anchors” meant ImageGen originals, not frames extracted from generated videos. Generated stills, video-extracted frames, provider motion, and normalized derivatives needed separate provenance categories before any cleanup.

These facts justify the reusable order: canonical audio -> story/coverage -> separate full-size production anchors -> canvas and chronological sequence acceptance -> bounded motion canary -> Resolve assembly -> range diagnostics -> full playback and delivery. They do not make Urvashi's story, palette, matte size, provider, or transition vocabulary defaults for other songs.

## Urvashi GPU generation and finishing corrections, reviewed 2026-09-27

The follow-up audit read the correction chain across 17 relevant tasks and 32 local rollout files, including resumed sessions, with targeted runtime and render records. Key later tasks were `01a0c2ed-a2ed-75a2-87c3-6ec62fc9482d` (RunPod/H3 and integrated replacement), `01a0df67-6a4f-7642-af45-4c31e8523506` (V6 finishing), and `01a0e156-8db3-7732-8c80-c69071644665` (private upload and ongoing vertical adaptation). This was a history/skill audit, not a fresh audiovisual certification of those films.

Corrections that changed the reusable process:

- The remote WSL catalog was stale despite a familiar path. Verify the selected snapshot on the execution host and bind the graph to those exact images. Preserve alternate illustrated/hyperreal branches independently.
- Paid setup encountered incompatible Pod images, slow network storage/transfers, changing allocation prices and a failed save-node schema. Prove the full sampling-to-download route with a bounded pilot, save job receipts, recover completed sampling when possible, and verify compute shutdown separately from process exit. Use [gpu-footage-generation](../../gpu-footage-generation/SKILL.md).
- New footage sometimes contained unwanted lettering or speaking mouths, or barely moved. Keep future graphics instructions outside visual prompts, reject unsupported performance, and judge usable movement at normal speed. Plan complementary angles and actions for fast cuts before buying a larger batch.
- A replacement existed on disk without being the source in Resolve. Completion requires updating all consumers, reading back the target timeline and checking the changed render.
- Later passes omitted already requested messages/intro/outro, restored unwanted features, or attempted fresh generation despite an existing-footage restriction. Keep a correction ledger and preserve accepted decisions through scoped changes.
- Message cards overflowed, looked too similar to lyrics, crowded faces and crossed scene boundaries. The user repeatedly requested self-checks of actual rendered fonts, full conversation flow and every affected panel. See [typography-and-story-graphics.md](typography-and-story-graphics.md).
- Screen-space text was replaced with unstable apparent surface tracking, then reverted. A tracking pilot must survive every frame plus playback before propagation. Revert only that feature and keep later approved fixes.
- Transition carriers used the wrong geometry, left partial inset rectangles or lower-layer strips, and sometimes produced stale full renders after a correct diagnostic. Check source canvas, every composite layer, source clocks and diagnostic/full-export pixel agreement. A six-to-eight-frame geometric move looked like a glitch in this later treatment; shortening is not a universal repair.
- Mirroring picture to clear lyrics changes phone/text/eyeline semantics and transition framing. Recheck those dependencies. An invitation needed to disappear completely before the following scene, with the actual alpha exit checked at consecutive frames.
- Vertical delivery exposed nested old lyrics, incorrect cue durations after an authorized song speed change, small picture prominence and a global crop that failed different shot types. Rebuild timing from the authorized transform, identify each text owner/canvas, and choose framing shot by shot.

The historical `music-video/enhancement-v6-prism/finish-v17/STATUS.md` recorded 4,482 decoded frames, unchanged audio versus V16, and 84 inspected samples, but explicitly **no normal-speed watch or hearing**, with creative approval pending for V17. A private upload or a previous version's scoped approval does not fill those evidence gaps. The reusable review and revision procedure is [revision-and-self-review.md](revision-and-self-review.md).

## Hello Ammayi full revision: composition and finish, reviewed 2026-09-27

The task `01a0e33e-b2b5-7e11-8585-32b86add238d` used this skill for a 227.625-second Hyderabad-to-beach Resolve revision. Its v4 edit plan has 36 shots and 39 lyric overlays. The type manifest fixed 43-pixel Gill Sans at canvas `y=966`, centered in the lower matte. Rendered cue samples were legible, yet the lyrics appeared small and visually detached at the bottom. Several samples showed heads or important picture content near an active-picture edge; the project's own final review called out tight headroom as a known point. Source clips without a recorded reframe can themselves contain that composition problem.

The v4 Resolve script duplicated the v1 timeline, set three reframes, checked shot/cue counts and recorded `TRANSITIONS: Deliberate cuts; native dissolve API unavailable`. The edit plan likewise says the native dissolve API did not apply. Count, timing and decode checks established a complete candidate file, but did not show the requested transition design was realized. The final review marked 108 shot samples and 39 lyric samples inspected while `WATCHED`, `HEARD`, lip-sync and creative approval remained false. The user then reported weak transitions, low lyrics, cropped heads/structures and unfocused leads.

The revision-local `quality-policy.json` also lacked several current template gates and all `timed_review` rules, despite a migration note saying those fields had been merged; no `quality-manifest.json` was present in that revision folder. This is a process failure as well as an aesthetic failure. The skill now uses [composition-and-finish.md](composition-and-finish.md), a per-shot/cue/join matrix bound to the render, and a template-coverage check for copied policies. A user-authorized review candidate can retain genuinely unavailable playback as pending, but visible frame defects and unrealized effects must be repaired or reported as known failures.

## Weekly correction audit, 2026-09-26 through 2026-10-02

The audit uses only local Codex chats: 28 rollout files including archived/resumed sessions and 174 human messages across 16 prior chats. Automated wakeups, injected skills and the audit's own messages were excluded from recurrence counts. This was a skill/history audit, not a fresh viewing or approval of the films.

| Evidence | Reusable decision and maintained procedure |
|---|---|
| `panja x og2`, 2026-09-28 and 09-30: repeated wrong likeness/body proportions, then the explicit request to recheck the anchor | Trace references → anchor → actual model input → motion → edit before another retry. Separate face, body/pose, supporting-cast distinction and performance in [generation.md](generation.md#lock-character-and-performance). |
| `panja x og2`, 09-28 through 09-30: repeated speaking/smiling, beard/style/grade drift, disconnected transformations and a changed ending | Preserve the current character/performance and world-state contract. Diagnose causality as well as continuity; keep deliberate world palettes distinct. |
| `Create Urvashi V5 beat-synced video`, 09-26: overflow, face obstruction, repeated rectangles, tracking flicker, identical glitch-like transitions and partial reversion | Inspect every equivalent template occurrence and the exact full export. Revert only the rejected feature; preserve later approved fixes in [revision-and-self-review.md](revision-and-self-review.md). |
| `panja x og2`, 09-30: expressive lyrics were followed by thin italic and then black-bar placement requests | Latest scoped decisions supersede old examples. Matte lyrics remain a valid selected composition in [lyric-art-direction.md](lyric-art-direction.md). |
| Urvashi 09-26 and Panda 10-02: review every 10–20 seconds, refine again; Panda explicitly requested at least two loops | Use timestamped defect and regression loops for substantial full-film polish. Tie observations to exports and retain separate watched/heard states. |
| `panja x og2`, 09-28: “Just giving the first 20 seconds won't help”; 09-30: retry once or use the better previous footage | Deliver integrated full-film context for a full-film revision and keep a recoverable predecessor. |
| Local model chats 09-27, Urvashi assembly 09-26, upscale comparison 09-30 and billing correction 09-29 | Honor the selected provider and no-generation scope, discover Herdr instead of stopping, preserve resource ownership, compare moving outputs, and use the existing GPU closeout procedure. |
| Urvashi mobile review 09-26 and the local review handoff reported missing 09-30 | Verify a usable exact-version handoff with direct media/bundle fallback in [resolve-and-review.md](resolve-and-review.md). |

Two additional explicit Panda requirements informed conditional branches: environment-only music response (10-02) and a two-part Short ending at an intentional musical turn (10-02). They are project requests rather than evidence of repeated agent failures. See [transitions-and-motion.md](transitions-and-motion.md#environment-only-music-response) and [direction.md](direction.md).

Panda's Pawan Kalyan likeness, beard, blue first nightmare, crimson second nightmare, thin italic matte lyrics and ending choreography remain film-specific choices. Hello Ammayi's selected friends and Urvashi's red trapezoid/message treatment likewise remain scoped examples. The skill preserves a new project's own brief instead of imposing these looks.

## Cyberpunk India film: production proof, reviewed 2026-10-02

Local Codex chat `Create cyberpunk India music video`, UUID `01a0ff3f-8968-7922-a88b-74ed982185f8`, used this skill for original Ram/Ileana footage woven with surreal cyberpunk nightlife, using Grok and the local GPU. The user's later location correction selected Amaravati, Vijayawada and Vizag. Three character-motion diagnostics failed; the agent switched to original performances plus separate environment footage and expanded into a 221.625-second film.

The exact R03 export was hash-verified and 20 frames inspected across all three city chapters. Samples showed neon night environments intercut with daytime desert/aircraft-yard performances. All generated storyboard shots used the same generic purpose; six local inputs were extracted from the six Grok clips. The saved quality report had `targets_pass=false`; listening, musical/emotional fit and full-speed review were pending. Refinement records mainly repaired source framing, a dark join and a flash. This audit did not watch or hear the full film and cannot establish an unheard pacing/mastering judgment.

The missing step was an edited creative proof before expanding the replacement treatment. Cutaways can fulfill a hybrid brief, but alternating clip categories does not prove that these particular worlds connect. [production-workflow.md](production-workflow.md) now defines ordered stages, requirement-to-observation mapping and the diagnostic/production boundary; the policy includes creative-proof and realized-intent gates. See the [local process audit](../../../../docs/research/cyberpunk-director-process-audit-2026-10-02.md) for exact file evidence and validation. The film-specific identities, locations, palette and footage ratio remain examples rather than defaults.
