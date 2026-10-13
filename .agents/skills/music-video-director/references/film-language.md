# Film language for shot design

Use this as a decision vocabulary, not a checklist of effects. A shot combines several independent dimensions. A dolly is a movement, a close-up is a scale, and a reaction shot is a function. They can describe the same shot.

The academic vocabulary below follows Yale's film-analysis teaching materials. The music-video applications are our own working suggestions, not academic prescriptions. This is a practical cross-disciplinary index, not an exhaustive taxonomy of filmmaking.

## Camera vocabulary

| Dimension | Terms and distinctions |
|---|---|
| Scale | Extreme wide/long, wide/long, medium-long, medium, medium-close, close-up, extreme close-up/detail |
| Angle and level | Eye-level, high angle, low angle, overhead, ground-level, canted/Dutch; camera height and tilt are separate |
| Viewpoint | Objective observer, character POV, following shot, reframing |
| Movement | Static; pan/tilt rotate; dolly/tracking translate; crane changes elevation; handheld introduces bodily movement |
| Optics | Wide versus telephoto; shallow/deep focus; rack focus transfers attention; zoom changes focal length |
| Time | Real-time, slow motion, accelerated motion, stop-motion; long take describes duration, not scale |

A dolly changes camera position and spatial relationships; a zoom does not move the camera. Scale, focus, angle, motion, and duration work together rather than carrying fixed emotional meanings. See [Yale: Cinematography](https://filmanalysis.yale.edu/cinematography/).

Production planning can further specify lateral truck, push-in/pull-out, orbit/arc, pedestal, stabilized follow, aerial/drone, whip pan, roll, or dolly zoom. Specify the actual start/end framing and trajectory instead of stacking camera adjectives. Treat these as shot directions to test in generated output, not promises that a provider simulates a physical lens.

## Shot functions and coverage

Use an establishing view for orientation, a master for spatial context, two-shots for relationships, over-the-shoulder views and reverses for exchanges, inserts for consequential details, cutaways for context, and reaction shots for a character's response. These are production-planning labels. One frame can serve several functions.

For a story sequence, plan enough coverage to show cause and consequence. Example: a hand releases a ribbon, a wider shot establishes who released it, a second character notices, and an altered framing reveals that the ribbon never reaches them. Each shot contributes information; four unrelated ribbon images would not establish that action.

For abstraction, replace plot continuity with a legible rule: a light travels through successive spaces, a material changes state, or one composition gradually opens. Preserve the rule long enough for its change to matter.

## Editing vocabulary

Continuity techniques include the 180-degree axis, eyeline matches, shot/reverse-shot, and match-on-action. Graphic matches link shapes or colors. Crosscutting alternates lines of action; ellipsis omits time; jump cuts expose discontinuity. Dissolves overlap images; fades transition to or from a uniform field. A long take can carry internal movement without cuts. Rhythm comes from shot duration, movement, sound, and accents together. See [Yale: Editing](https://filmanalysis.yale.edu/editing/).

Our use in generated music videos:

| Choice | Candidate use | What to inspect |
|---|---|---|
| Straight cut | Clear change on a musical or emotional event | Does the new shot add information? |
| Graphic/action match | Source footage crossing into its stylized counterpart | Pose, screen direction, subject size, horizon |
| Dissolve | Memory, sustained harmony, gradual emotional change | Double faces, muddy contrast, sufficient handles |
| Occlusion/wipe | Pass behind fabric, architecture, shadow | Direction and edge continuity |
| Crop/split overlays | A deliberate burst of fragmented attention | Faces and lyric space; overuse |
| Speed ramp | A motivated change within an action | Cadence, optical-flow warping, cut handles |
| Discontinuous montage | Associative ideas or memory fragments | Is the association readable without exposition? |
| Held shot | Anticipation, observation, release | Is there meaningful internal change? |

Choose a transition vocabulary sized to the explicit brief. A restrained default must not override a request for ten or more recurring styles. Use [transitions-and-motion.md](transitions-and-motion.md) to configure and audit the palette. Surprise can come from composition or meaning rather than a new effect at every cut. Do not inherit Yemi's energetic crop effects for a mellow song just because its edit was successful.

## Mise-en-scene and performance

Setting, décor, costume, blocking, and lighting shape relationships within the frame. Key, fill, and back light describe different lighting roles; high-key and low-key approaches shape shadow and contrast. These decisions can support mood without camera movement. See [Yale: Mise-en-scene](https://filmanalysis.yale.edu/mise-en-scene/).

For generation, write a continuity card per scene: time of day, weather, costume, props, dominant light direction, character positions, and what changes. Pick a repeatable physical action. A subtle glance or a hand pause is often more controllable than a multi-person dance with complex contact. Reserve unambiguous negative space if lyrics will occupy the frame.

Production design, cinematography, performance, editing, typography, compositing, color, and sound should agree on the same emotional turn. For example, a new warm light, an opening composition, and a less constrained movement can make a chorus feel released without rapid cutting. This is a treatment option, not a fixed rule for choruses.

## Sound and image

Diegetic sound belongs to the represented story world; nondiegetic sound comes from outside it. A sound bridge connects scenes across an image change. Sound and image need not always coincide literally. See [Yale: Sound](https://filmanalysis.yale.edu/sound/).

In this workflow, the supplied song normally remains continuous and authoritative. Do not add generated dialogue, whooshes, or ambience by default. “Audio-reactive” can mean changing visual behavior without adding any sound. If sound design is requested, make its relationship to the song explicit and review the resulting mix.

## Storyboard card

For each shot record:

- Shot/scene ID and timeline range; musical anchor and story purpose.
- Source type, reference frame/clip with source timecode, and continuity card.
- Subject/action, shot scale, angle, viewpoint, camera path, focus, light, and palette.
- Start and end composition; incoming/outgoing transition and usable handles.
- Required usable duration, generation duration, retime intent, and fallback coverage.
- Lyric or title placement if enabled; exclusion areas for faces and important actions.
- Prompt, selected asset ID, and acceptance criteria.

Write a short AV storyboard with audio/meaning beside image/action. Storyboards may illustrate mood, performance, story, or combinations. See the practical [StudioBinder music-video storyboard guide](https://www.studiobinder.com/blog/how-to-make-a-music-video-storyboard/) for this planning format. Link every attractive shot to its role in the song before generating it.
