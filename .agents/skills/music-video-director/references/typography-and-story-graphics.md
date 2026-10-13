# Lyrics, messages, titles, and tracked text

Read before a typography or story-message pass. Use the approved visual reference and latest user wording, then validate the actual export. Font choice and text placement are part of the composition.

For lyrics, first use [lyric-art-direction.md](lyric-art-direction.md) to resolve personality, narrative states, type families, placement and motion through a small design conversation and rendered pilots. Run this after picture timing is stable enough to compose against, before full rollout/final export. Temporary alignment captions do not establish the finished design.

## Separate text roles

Keep lyrics, story dialogue/messages, location/intro titles, and end credits in separate records and editable tracks/comps. Each needs canonical content, owner, intended range and style. “Captions” in a lyric request does not authorize invented narration. Keep native-script canonical lyrics; create a separately labeled transliteration only when requested. Nonlexical vocalizations can guide cuts without becoming visible lyrics; apply the user's ad-lib policy explicitly.

Message graphics need a conversation ledger: sender, recipient, relationship label, exact wording, order, incoming/outgoing direction, delivery/reply times, emotional consequence, and scene ownership. Use approved names and natural register; do not invent additional exchanges or robotic exposition to explain a story problem. Drafting fictional dialogue is an editorial action, not permission to message a real person.

Generate clean phone imagery with natural blocking: a person reading a phone held toward them, not presenting a screen to the viewer just to make text visible. Compose the UI in Resolve. Keep future edit instructions, software names and typography terms out of footage-generation prompts; models can turn those words into visible lettering.

## Make a representative typography pilot

Before applying a style everywhere, render the longest lyric, a close-up, a red/busy background, each lyric narrative state and a handoff between states, a multi-message exchange, and intro/outro typography. Choose only the representative risks present in the film. Compare with the selected lyric design and approved visual references at delivery size and mobile size. Verify the font Resolve actually rendered and the text canvas dimensions; a font name or Text+ setting alone does not prove the intended glyphs appeared. A requested motion treatment requires an animated preview over actual footage and audio, not only a still font board.

Measure rendered text bounds, line wrapping, padding and safe areas. Card height must follow its content. Check italic overhangs and animation overshoot, not only centered static text. Inspect whether the chosen placement supports the picture's hierarchy at desktop and phone size: a small caption in a persistent lower matte can pass legibility checks yet look detached and unpolished. Compare an in-picture negative-space option and any user-authorized matte/card option before locking a global placement. If the user rejected a black backing card, improve position, contrast or a permitted subtle edge treatment without restoring that card. Use distinct shapes, rhythm and typography for messages versus lyrics so viewers can tell what was sung and what was sent.

Allocate reading time after the full text arrives and before the exit begins. Preview the whole exchange at normal speed while reading it; if it cannot be understood, simplify wording with authorization or lengthen/restructure the scene within the audio/shot contract. Do not squeeze a story exchange into a short musical accent solely because it fits the timeline numerically.

## Check clearance throughout the shot

Treat faces, hands performing a story action, key props, lyric regions and message panels as protected regions. Inspect entrance, midpoint, exit and the subject's closest approach to text. Split or relocate a cue when a moving subject crosses its initial negative space. Recheck overlapping text tracks together; independently readable layers can become unreadable when combined.

Include ink trails, particles, strokes, shadows and animation overshoot in clearance checks. Inspect the full readable hold and the first clean frame after each effect ends. A lyric may deliberately span a scene transformation; keep its words continuous and use the designed style handoff rather than restarting the cue or leaking an outgoing scene's graphic motif.

Mirroring a shot can create space when allowed, but review screen direction, eyeline, handed props, signage and story continuity before using it. Mirror only the intended picture; preserve readable text. Update transitions or copies of that source using the same framing. Overlays tied to a scene must reach zero opacity before the next unrelated scene's first frame; account for animation tails and inclusive/exclusive frame conversion.

## Track only a suitable surface

For text meant to belong to a wall, glass or laptop, select a stable planar surface, track it with the supported Resolve/Fusion tracker, solve perspective/occlusion, and render a pilot before spreading the technique. Do not call arbitrary keyframes or independent per-frame corner guesses a verified planar track.

Review every frame of the pilot for sliding, scale pumping, corner-order flips, warp, flicker, occlusion errors and disappearing text, then watch at normal speed. Use a simpler transform only when the shot supports it. If the surface cannot hold a convincing track, preserve a screen-positioned candidate and report the limitation or follow an authorized fallback. When the user rejects tracking, remove its transforms and retain the approved color/font and unrelated fixes.

## Ending and vertical variants

If a moving ending is required, use the associated accepted motion through the title reveal and fade; do not hold its still anchor because it is easier. Distinguish song title from artist credit, and inspect the whole audio decay and final frame.

When moving lyrics outside a nested film, verify that the inner lyric track is actually absent in the export. Disable/rebuild nested text as needed; never cover old lyrics with new ones. Recalculate text canvas, font sizes and cue times for the new aspect ratio and authorized retime. Follow the shot-specific framing rules in [resolve-and-review.md](resolve-and-review.md).
