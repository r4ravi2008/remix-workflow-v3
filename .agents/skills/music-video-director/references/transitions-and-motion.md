# Configurable transitions and motion graphics

Copy [effects-config.json](../assets/effects-config.json) into the workspace's `music-video/` directory. Resolve the user's wording into the config before changing the edit. The template is a starting point, not a mandatory look. Preserve canonical audio and existing accepted edits in versioned timelines.

## Independent controls

- **Scene transitions:** enabled palette, distinct-style minimum, uses per style, section density, durations in beats, placement and recurrence. A request for at least10 recurring styles means at least10 visually different implemented families, each recurring across the requested duration. Do not satisfy the count with twelve names for one dissolve or left/right variants of one wipe.
- **Temporal accents:** reverse/forward order, beat-relative leg duration, eligible shots, event cap and return to forward playback. Reverse picture only; keep the canonical soundtrack continuous.
- **Motion graphics:** spectrum, edge pulse, rings, particles or other selected motifs; owner, palette, opacity, density, rest intervals, placement and face/lyric exclusions. They are distinct from both camera movement and transitions. Disable unrelated motifs.
- **Lyrics:** native, transliterated, or translated display is explicit. Keep original-script canonical text intact. English-letter transcription in a Udi-like brief means transliteration when the reference confirms it; do not replace it with invented English poetry.

## Resolve ordinary language

“Ten styles repeated throughout, boomerang cuts on beats” overrides the restrained default: set a minimum10-style palette, minimum2 uses each, distribute it across the song and shortened exports, and add bounded time-map events on suitable shots. “Like Yemi” supplies evidence to inspect, not permission to inherit its crop or palette. A full-frame lock prohibits permanent crop/zoom; transient transition masks may reveal the complete source frame but must not silently reframe it.

A candidate 12-style Resolve palette is Cross Dissolve, Additive Dissolve, Non-Additive Dissolve, Blur Dissolve, Dip To Color Dissolve, Edge Wipe, Center Wipe, Push, Slide, Clock Wipe, Barn Door and Diamond Iris. These names were verified in one Resolve21.1 session; probe the live build and read the actual created type before relying on them. Do not use face-morphing interpolation as an interchangeable dissolve.

## Build an event plan

Bind the plan to canonical audio hash, frame rate, beat-map version and source/timeline revision. Store each event's ID, musical anchor, exact frame range, style, parameters, adjacent source IDs, handles, owner, intended effect and fallback. Separately store boomerang time maps and motion-graphic events. Validate that frame markers and source-time events are ordered; reject impossible or unintended non-monotonic sequences before applying them. Use deterministic selection; balance recurrence while varying duration, musical role and rests. An explicit minimum is a delivery requirement, not a suggestion.

Anchor impact or turnaround to a measured beat; document whether that beat is the start, midpoint or end. Do not present estimated downbeats as measured. Preserve phrases and give quieter sections room. Reject repeating zoom jerks as a substitute for varied editing.

Choose duration by rendered readability. Urvashi needed both a repair of masks hanging unfinished for several seconds and a later repair of identical 6–8-frame wipes that read as glitches. “Snappier” does not mean make every effect shorter; distinguish anticipation, reveal, musical landing and clean-image dwell. Pilot visibly different families at the actual tempo, then tune duration and rests. Preserve approved color accents while varying the underlying motion, source moment and composition. Count rendered visual differences, not parameter names.

Do not silently replace a requested transition design with generic hard cuts because a Resolve API call failed. Try a supported native or Fusion route on a duplicate timeline; verify render pixels. A cut can be an intentional transition when its outgoing/incoming action, eyeline, shape or light connection and musical landing are actually designed and reviewed. Record the intended and rendered method for **every** join, including plain cuts, and note any deviation. A global sentence such as “purposeful action cuts” cannot establish that 35 individual joins work. Use the [finish matrix](composition-and-finish.md) to catch omissions and compare neighboring joins for pacing and variety.

For composited transitions, record each source's native dimensions, pixel aspect, active picture/matte, crop/flip/resize order, retime and source frame at entry/exit. Bring both inputs to the intended canvas exactly once. Use a carrier with verified dimensions and duration; a small carrier can shrink a full-frame source into an inset even when the nodes use apparently correct scale values. Match the last composite frame to the next underlying shot in size, position and source time. Include retimed and mixed-resolution sources in the pilot.

Apply the reveal to the entire intended picture, including any outer strips; otherwise incoming footage may leak above/below a central mask. Keep accent strokes on their intended mask without exposing other layers. Review every occurrence at entrance, midpoint, landing and the first clean frame, and inspect every frame of any suspect join. Refresh stale Resolve/Fusion output only after confirming that the saved graph and full render disagree. See [revision-and-self-review.md](revision-and-self-review.md).

## Implement and prove temporal effects

Never invent `Speed`/`RetimeSpeed` properties. Query current tools. A supported Fusion TimeStretcher can map source frames forward, then reverse, then forward without deriving a new source file. Probe SourceTime and actual MediaOut connections. Example for a source-frame leg L: `t` before L, `2L-t` between L and2L, then `t-2L`; this is a continuous forward/reverse/forward excursion, not a reversed soundtrack. Convert beat duration into source frames and account for trim, clip fps, timeline fps and Fusion time origin. Keep every requested source frame within available handles.

Render a short diagnostic before bulk use. Compare corresponding pre/post-turnaround frames and inspect normal-speed playback. A decreasing SourceTime expression alone does not prove the output is reversed. Restoring forward motion must not jump, freeze unexpectedly or break a meaningful action. Intentional stutters must be configured and visible in the plan.

At ordinary scene changes, do not reveal the incoming motion during an outgoing Fusion composition and then restart that same clip at the cut. Either keep its source time continuous through the transition or use a true handled transition between separate clean frames. Inspect outgoing clean frame, transition span, incoming clean frame, and the next second of motion together.

## Lyrics and motion graphics

### Environment-only music response

When the brief restricts reactive shaders/effects to background environments, record the eligible surfaces and response strength by musical section. Use subtle light, reflection, haze, texture or architectural response that supports the selected palette and emotion. Derive the response from the canonical music and use quieter holds/rests so intensity follows the song's structure.

Isolate the environment with verified masks, depth/segmentation or tracked mattes; protect characters and consequential props, then composite lyrics and titles independently. A full-frame pulse, grade or overlay also changes people and fails this scope. Inspect moving hair, hands, silhouettes and prop edges at entrances, peaks and exits, especially across real-to-anime transformations. Compare effect-on/off renders at matching times for face color, detail, motion and text stability. Repair bleed, halos, flicker or mask lag before full rollout. Technical mask presence alone does not prove isolation in the final pixels.

Use [lyric-art-direction.md](lyric-art-direction.md) for the scene-dependent typography and motion system. Lyric ink trails, falling entrances and light strokes belong to their cues, with a stable readable hold and bounded effect tails; they are separate from scene-transition counts and general background motion graphics. Keep a phrase continuous through a real-to-stylized transformation using its recorded narrative-state handoff.

Use the selected song/vocal stem and a separate display/transliteration file for forced alignment. Check repeated choruses and outro independently. Forced alignment can stretch a final word through silence; bound repairs by audible/waveform evidence and preserve uncertain cues as pending. Do not distribute word timing by character count and call it verified karaoke.

Keep one text owner and one audio owner across Resolve and Remotion. Fit no more than the configured number of lyric lines using actual rendered font metrics. Keep overlay motion deterministic and away from faces and captions. A canonical-audio-only packaging correction may stream-copy the finished video; record packet identity and repeat audio sync verification. It must not become an FFmpeg replacement montage for a requested Resolve edit.

## Review and delivery

Read back actual transition types/counts/ranges and source coverage. Audit distinct style count and minimum recurrence against each requested export, not only the full timeline. Render head/mid/tail evidence for each style occurrence plus forward/reverse turnaround evidence. Check blank frames, unavailable handles, clipped faces, flashing intensity, edge artifacts, lyric overlap, and focal sharpness. Keep sampled-frame checks separate from full playback with sound.

Record config, event manifest, actual render receipts, hashes and quality evidence. Unsupported effects remain unresolved until substituted with a genuinely distinct verified style or the brief changes. Do not mark a palette complete from planned names alone. Apply the existing component quality gates to these exact revisions.

## Aggressive back-and-forth requests

A request such as `1-2-2-1-1-2-3-4` describes a shot-selection pattern, not merely a repeated dissolve or a gentle time reversal. Configure shot slots, direction per slot, beat subdivision, burst length, recurrence, and phrase rests independently. Repeat the same source window forward and backward for a visible movement reversal; alternate distinct shots for spatial back-and-forth. Keep short burst interiors as hard cuts when transitions would obscure the rhythm. Count and inspect the actual rendered cuts.

Preserve visible singing: match original performance footage to the words actually heard in the canonical remix, keep those clips forward, and review mouth movement against sound. Align source and remix vocal timings separately; identical lyrics do not guarantee identical delivery. Source-word retiming can support a candidate, but never proves lip sync without playback. If the source performance cannot be matched, use verified non-singing coverage for that interval. Do not apply reverse, shuffle, freeze, or arbitrary speed bursts to a singing face.

An explicit source-crop or zoom request overrides an earlier full-frame preference only within the requested scope. Record per-source framing rules and inspect every affected shot at head, middle, and tail. A corner-logo exclusion crop must keep the logo outside the entire animated viewport, not just one sampled frame, and must preserve the intended focal subject. Generated shots retain their separate framing policy.

When Resolve Fusion retimes interact badly with transition handles, render reusable full-length motion sources in Resolve, import them, and rebuild the edit with verified handles. Audit clip start/end readback after appending or retiming: frame-rate rounding can create one-frame gaps. Probe actual joins before a full render.

For source-character storyboards, extract a documented face/profile/body reference set from the original song before generating. Store source time, file hash, character label, and role. Original frames control identity and body proportions; generated images control style only. Do not use background performers as the lead reference. Bind the reference manifest to each relevant shot card.
