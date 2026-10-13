# Direction and musical structure

## Translate prose into a brief

Write only decisions relevant to the requested stage. For each choice, record `user-fixed`, `inherited-and-verified`, or `agent-assumption` so a later correction can retire the old choice explicitly.

| Choice | Useful values or questions |
|---|---|
| Input and endpoint | Exact song version; storyboard, footage, edit, full song, or Short |
| Emotional thesis | One sentence about what the listener should feel and how that feeling changes |
| Meaning | Literal lyric meaning, mood-only interpretation, or deliberately independent story; confidence and source |
| Form | Narrative, performance, abstract, or a hybrid with named section roles |
| Footage policy | Original clips permitted? Reference frames only? Entirely new world? Visible-time mix, if specified |
| Identity | Source characters to preserve, invented characters, or no people |
| Look | Palette, materials, lighting, realism/stylization, period, setting, motifs, exclusions |
| Motion | Camera movement, subject movement, shot-length range, slow motion, stillness, accent density |
| Text | None, native lyrics, transliteration, translation; personality, narrative-state type/motion families, title references, placement and collaborative review choices |
| Output | Aspect ratio, duration or range, resolution/fps when known, standalone film or optional frame layout |
| Quality | Profile, criterion overrides, required evidence, component attempt limits; see [quality-gates.md](quality-gates.md) |
| Exploration | Restrained, balanced, or adventurous variation; locked choices; generation/time budget if supplied |

Example interpretation: “modern but keep the original yearning; soulful and expensive” might become patient approaches, incomplete encounters, softened highlights, one recurring object, and a widening final frame. These are a proposed treatment, not fixed meanings attached to a genre or culture. “Modern” does not automatically mean neon, glitches, fast cuts, or a visualizer.

When interpretation matters, record language identification and meaning sources separately, such as user-supplied translation, reliable subtitles, or a fluent reviewer. Label uncertain lines and avoid literal plot claims based on them. For abstract direction, record whether people/characters are allowed. If output settings are absent, inherit verified project settings; otherwise use provisional 1920x1080 for landscape or 1080x1920 for vertical, choosing fps from dominant footage or 24 fps for fully generated planning. State these assumptions rather than treating them as user requirements.

If asked to explore, present two or three meaningfully different treatments, each with an emotional arc, a sample shot, and a production tradeoff. Variation should change an actual storytelling choice. Do not require a treatment vote if the user asked for autonomous completion.

When lyrics are requested, sketch their personality here and reserve composition space during shot design. Resolve detailed typography and animation against stable moving footage in the later [lyric design pass](lyric-art-direction.md). When collaboration is requested, ask concise questions about still-open creative choices and show actual alternatives; a previously fixed writing system or theme does not need another question.

## Read the audio

Record source path/hash, duration, channel layout, sample rate, and exact trim if any. Use a lossless supplied master when it is the user's selected version. Compatibility MP3s remain labeled derivatives.

Create a section map with time ranges, audible evidence, lyric meaning if known, perceived energy, and intended visual response. Inspect changes in percussion, bass, harmonic texture, vocals, silence, and sustain. A “drop” tag in a prompt is not evidence that a drop occurs at that timestamp.

Estimate tempo/onsets and verify downbeats by listening at the beginning, middle, and end. Handle half/double-tempo ambiguity and tempo changes. Store measured beat times when a fixed BPM grid drifts. Differentiate percussion onsets, beats, bar starts, and phrase boundaries; do not call every onset a downbeat. Mark uncertain regions instead of fabricating precision.

Choose musical anchors deliberately. A cloth movement may peak on a swell while the shot spans several bars. A look can land on a vocal entrance. A hard cut can punctuate a selected accent. Let quieter sections breathe and reserve the most noticeable change for a meaningful musical turn.

Build the event map in layers: (1) structure and emotional turns, (2) vocal/lyric entrances, exits and meaningful syllables, (3) bass, harmony and texture changes, (4) selected percussion accents. Record each event's time, audible source, confidence, intended response and priority. Resolve collisions deliberately; a structural reveal can outrank a nearby kick. Map events to shot changes, subject/camera movement, light, graphics or transition peaks rather than cutting at every event. Perceived energy can rise while BPM stays constant. Listen through the whole song before freezing the edit map, then watch and hear the rendered result to judge whether the intended hierarchy survives.

## Short selection

Honor an explicit excerpt first. Otherwise listen to a few plausible candidates and record start/end, hook, phrase completeness, emotional arc, and visual potential. Prefer an opening that presents an image or unresolved action immediately, then develops it and pays it off. Loudness alone is not a hook score.

For a narrative Short, design a small self-contained change. For an abstract Short, establish a motif, transform it, then resolve or loop it. Do not imply a complete plot where only a mood fragment is supported. Preserve words, vowel endings, breaths, and musical resolution. Extend or shift boundaries before cutting inside a sung phrase.

Respect the user's duration. If unspecified, propose a musically complete excerpt and state its length; do not import a fixed 30-second, 60-second, or three-minute rule from an old project. Check current platform requirements only when platform delivery is requested. Reframe for vertical composition shot by shot. Rebase beat and lyric timestamps by the exact excerpt start. A seamless loop is optional; it must not truncate a vocal resolution.

For a requested multi-part Short, plan the parts together from the actual music and story. Place the first ending at a complete phrase or clean pre-drop/turn boundary that leaves an intentional question; make the next part's opening continue or resolve that promise. Preview both sides with sound. An arbitrary halfway split or chopped sung syllable does not create suspense. Record each part's canonical source in/out and local cue/beat map, then reframe each shot and adapt titles/lyrics independently. Create every requested part; a split timestamp alone is a plan, not a delivery.

## Bounded variation

Record the choices that must remain stable across a sequence: character references, costume, setting, palette, motif, emotional trajectory, and movement limits. Vary shot scale, viewpoint, spatial reveal, transitions, and motif development within those constraints. Save selected treatment and generation prompts; a random seed, where supported, does not guarantee identical output.

Example palettes of choices, offered as creative starting points:

- Yearning: distant space, a restrained approach, withheld reverse angle, then one revealing close view.
- Mellow release: lateral travel, suspended fabric, soft light changes, a long exhale across a phrase.
- Restless celebration: alternating distances, directional movement, short bursts of crop cuts, then a stable shot to reset attention.

Do not treat these associations as universal psychology. Lyric meaning, cultural context, and the user's explanation can override every example.
