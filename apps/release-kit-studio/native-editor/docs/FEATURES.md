# Feature guide with scenarios

This guide gives creators and agents details for all 81 mapped capability families.
The eight CORE families have a bounded Rust implementation. The other 73 families remain planned.
Trusted acceptance-case receipts did not promote any feature to verified. Refer to [current measurements](PROGRESS.md).
This guide does not list every Resolve control or claim identical algorithms.

The product target is one-to-one coverage of DaVinci Resolve feature behaviors through the Rust editor and direct agent CLI.
The catalog spans general media projects across the Resolve feature areas.
Release Kit is one optional workflow that uses these features.
Its song inputs and fixed output profile do not restrict the editor's project or timeline model.
The 81-family catalog is an initial breakdown, not complete parity.
A versioned Resolve reference inventory and local coverage record remain required.

## Start with a task

Choose the situation nearest to your goal. Each link opens the applicable feature, scenario, implementation pieces, and checks.

| Task | Scenario | Features | Availability |
| --- | --- | --- | --- |
| Do a test of the local Rust editor | Create a test project. Add one solid clip. Render a PNG. Verify its stored bytes. | [CORE-01](features/core.md#core-01-capability-and-schema-discovery), [CORE-02](features/core.md#core-02-local-project-revisions), [CORE-04](features/core.md#core-04-typed-timeline-transaction), [CORE-05](features/core.md#core-05-native-frame-preview), [CORE-06](features/core.md#core-06-artifact-integrity) | Current bounded P0 |
| Build a scene with layers | Place an environment below a masked performer, with timed Telugu lyrics above both. | [EDIT-01](features/editing.md#edit-01-track-and-timeline-composition), [EDIT-08](features/editing.md#edit-08-keyframes-and-interpolation), [FUSION-02](features/fusion-ai.md#fusion-02-merge-masks-and-blend-modes), [FUSION-03](features/fusion-ai.md#fusion-03-native-script-titles-and-typography), [FUSION-05](features/fusion-ai.md#fusion-05-keying-and-rotoscoping) | Planned P2/P3 |
| Make the background react to music | Measure the canonical song. Drive background effects that preserve people and lyrics. | [AUDIO-08](features/audio.md#audio-08-music-envelopes-and-beat-analysis), [FUSION-08](features/fusion-ai.md#fusion-08-music-reactive-environment-layers) | Planned P2/P3 |
| Edit footage into a film | Import sources. Sync the sources. Assemble shots. Trim the shots. Add declared transitions. | [MEDIA-01](features/media-cut.md#media-01-media-ingest-and-metadata), [MEDIA-05](features/media-cut.md#media-05-audio-and-video-synchronization), [EDIT-02](features/editing.md#edit-02-insert-overwrite-replace-append), [EDIT-03](features/editing.md#edit-03-ripple-roll-slip-slide-trimming), [EDIT-06](features/editing.md#edit-06-transitions-and-fades) | Planned P1/P2 |
| Make a portrait chorus promo | Choose the exact source interval. Crop or reframe the picture. Preserve song timing. Export the promo. | [EDIT-07](features/editing.md#edit-07-transforms-cropping-and-stabilization), [AI-03](features/fusion-ai.md#ai-03-smart-reframe-upscale-and-motion-synthesis), [DELIVER-02](features/delivery-collaboration-extensions.md#deliver-02-movie-encoding-and-muxing), [DELIVER-07](features/delivery-collaboration-extensions.md#deliver-07-release-kit-profile-and-archive) | Planned native output. Advanced AI P7 |
| Finish the sound | Edit exact samples. Route tracks. Mix the audio. Measure the output separately from listening. | [AUDIO-01](features/audio.md#audio-01-sample-accurate-editing-and-mixing), [AUDIO-02](features/audio.md#audio-02-waveforms-meters-and-loudness), [AUDIO-03](features/audio.md#audio-03-eq-dynamics-and-effects), [AUDIO-04](features/audio.md#audio-04-buses-sends-automation-and-folders) | Planned P2 |
| Give the film a consistent look | Declare color transforms. Adjust grades. Compare scopes. Export matching stills. | [COLOR-01](features/color-photo.md#color-01-color-management-and-transforms), [COLOR-02](features/color-photo.md#color-02-primary-wheels-curves-and-grading), [COLOR-05](features/color-photo.md#color-05-scopes-and-clipping-diagnostics), [COLOR-09](features/color-photo.md#color-09-stills-galleries-and-grade-matching), [PHOTO-02](features/color-photo.md#photo-02-crop-reframe-and-image-export) | Planned P4 |
| Produce a complete release kit | Export the full-song film, three promos, a thumbnail, and square artwork from actual assets. | [DELIVER-05](features/delivery-collaboration-extensions.md#deliver-05-source-bound-technical-qc), [DELIVER-07](features/delivery-collaboration-extensions.md#deliver-07-release-kit-profile-and-archive) | Planned P5 |
| Host the multi-tenant product | Authenticate the creator. Authorize sources. Schedule a native host. Bind returned receipts. | [COLLAB-01](features/delivery-collaboration-extensions.md#collab-01-project-libraries-and-tenant-authorization), [COLLAB-03](features/delivery-collaboration-extensions.md#collab-03-clip-bin-and-timeline-ownership), [COLLAB-04](features/delivery-collaboration-extensions.md#collab-04-cloud-media-synchronization), [DELIVER-04](features/delivery-collaboration-extensions.md#deliver-04-render-queue-cancellation-and-recovery), [DELIVER-06](features/delivery-collaboration-extensions.md#deliver-06-presets-and-remote-rendering) | Planned P6 |
| Add an optional interface | Use the Rust commands from a desktop adapter or through a browser service. Choose the UI separately. | [EXT-04](features/delivery-collaboration-extensions.md#ext-04-optional-editor-and-review-ui) | Planned P6. Local and hosted dependencies differ |

## Read one feature

Each feature has seven sections.

1. Read What it does.
2. Read Scenario.
3. Before an implementation decision, read Behavior rules.

Inputs and result identifies the command boundary. Implementation pieces divides the work into bounded units.
Verification gives names to the success and failure cases. Status and dependencies identifies what must exist first.

The named future cases are specifications. Verification still needs real fixture corpora and executable checks.

## Document structure

Each feature document uses the same seven sections.
Creator scenarios come before implementation details.
Each implementation piece names its acceptance cases.
The [development workflow](WORKFLOW.md) records the procedure and evidence boundary.

## Common terms

| Term | Meaning |
| --- | --- |
| Track or visual layer | Ordered timeline content that can contribute pixels over lower tracks |
| Clip | One source bound to a timed interval on a track |
| Mask | Pixel coverage that controls which parts of a layer contribute |
| Source time | The position read from the original media |
| Timeline time | The position that the renderer evaluates in the edited sequence |
| Revision | One immutable project state after an accepted edit |
| Intent | The stable identity of one requested operation, retained across retries |
| Verification | Measured evidence from the actual implementation and artifact, separate from human review |

## Complete feature index

The phase identifies the first bounded implementation slice. Advanced pieces can target later phases.
Rust owns native editing. Effect belongs to separate application workflows. React, Tauri, and Foldkit remain UI candidates.

### Core

| Feature | Example use | Phase and owner |
| --- | --- | --- |
| [CORE-01](features/core.md#core-01-capability-and-schema-discovery) Capability and schema discovery | A creator requests a Telugu song promo. | P0, Rust |
| [CORE-02](features/core.md#core-02-local-project-revisions) Local project revisions | A creator requests a four-second background test. | P0, Rust |
| [CORE-03](features/core.md#core-03-stable-command-intents) Stable command intents | The agent adds a four-second background but loses the response. | P0, Rust |
| [CORE-04](features/core.md#core-04-typed-timeline-transaction) Typed timeline transaction | A creator does a test of two chorus backgrounds at 24 fps. | P0, Rust |
| [CORE-05](features/core.md#core-05-native-frame-preview) Native frame preview | The creator examines a background before the creator adds footage. | P0, Rust |
| [CORE-06](features/core.md#core-06-artifact-integrity) Artifact integrity | Another program changes one byte in yesterday's background PNG. | P0, Rust |
| [CORE-07](features/core.md#core-07-native-cli-process-lifecycle) Native CLI process lifecycle | An agent loses the process after submitting a background edit. | P0, Rust |
| [CORE-08](features/core.md#core-08-agent-workflow-checks) Agent workflow checks | A creator requests a full Pal Pal film. | P0, Rust |

### Media

| Feature | Example use | Phase and owner |
| --- | --- | --- |
| [MEDIA-01](features/media-cut.md#media-01-media-ingest-and-metadata) Media ingest and metadata | A creator supplies three performance takes and a separate song master for a 24 fps music video. | P1, Rust |
| [MEDIA-02](features/media-cut.md#media-02-bins-and-smart-metadata-search) Bins and smart metadata search | An interview project contains 40 takes tagged by speaker and camera. | P1, Rust |
| [MEDIA-03](features/media-cut.md#media-03-proxies-and-optimized-media) Proxies and optimized media | A music-video creator has a supported 4K performance take on external storage. | P1, Rust |
| [MEDIA-04](features/media-cut.md#media-04-relink-and-media-management) Relink and media management | A creator moves an interview recording to a local SSD. | P1, Rust |
| [MEDIA-05](features/media-cut.md#media-05-audio-and-video-synchronization) Audio and video synchronization | An interview camera records the clap 2 seconds after its start. | P1, Rust |
| [MEDIA-06](features/media-cut.md#media-06-checksum-clone-and-consolidation) Checksum clone and consolidation | A documentary editor needs an interview project on a travel SSD. | P1, Rust |
| [MEDIA-07](features/media-cut.md#media-07-camera-raw-decoding) Camera RAW decoding | A music-video creator supplies a camera RAW performance take with bright stage lights. | P1, Rust |
| [MEDIA-08](features/media-cut.md#media-08-image-sequence-and-alpha-ingest) Image sequence and alpha ingest | A creator supplies 48 numbered PNG frames for a two-second transparent graphic at 24 fps. | P1, Rust |

### Edit

| Feature | Example use | Phase and owner |
| --- | --- | --- |
| [EDIT-01](features/editing.md#edit-01-track-and-timeline-composition) Track and timeline composition | A music video has an environment on V1 for frames `[0, 240)` at 24 fps. | P2, Rust |
| [EDIT-02](features/editing.md#edit-02-insert-overwrite-replace-append) Insert overwrite replace append | An interview has shot A at `[0, 96)` and shot B at `[96, 192)`, both at 24 fps. | P2, Rust |
| [EDIT-03](features/editing.md#edit-03-ripple-roll-slip-slide-trimming) Ripple roll slip slide trimming | A documentary has A at `[0, 96)`, B at `[96, 192)`, and C at `[192, 288)`. | P2, Rust |
| [EDIT-04](features/editing.md#edit-04-split-edits-and-linking) Split edits and linking | An interview switches picture at frame 240, but the next speaker's audio starts at frame 216. | P2, Rust |
| [EDIT-05](features/editing.md#edit-05-nested-and-compound-timelines) Nested and compound timelines | A chorus contains environment, performer, and lyrics in child frames `[0, 96)` at 24 fps. | P2, Rust |
| [EDIT-06](features/editing.md#edit-06-transitions-and-fades) Transitions and fades | A commercial changes from a room to a product close-up during frames `[96, 121)`. | P2, Rust |
| [EDIT-07](features/editing.md#edit-07-transforms-cropping-and-stabilization) Transforms cropping and stabilization | A creator prepares a portrait excerpt from a landscape performer shot. | P2, Rust |
| [EDIT-08](features/editing.md#edit-08-keyframes-and-interpolation) Keyframes and interpolation | A music-video environment graphic moves horizontally while the performer and lyrics stay fixed. | P2, Rust |
| [EDIT-09](features/editing.md#edit-09-retiming-and-optical-flow) Retiming and optical flow | A creator slows a 24 fps dance shot to half speed. | P2, Rust |
| [EDIT-10](features/editing.md#edit-10-subtitles-and-closed-captions) Subtitles and closed captions | A Telugu interview contains the spoken phrase `ఇది మా ఊరు`. | P2, Rust |
| [EDIT-11](features/editing.md#edit-11-undo-redo-and-versions) Undo redo and versions | Revision 7 has the approved chorus timing. | P2, Rust |
| [EDIT-12](features/editing.md#edit-12-markers-flags-and-timeline-metadata) Markers flags and timeline metadata | A director adds a chorus-start marker at frame 960. The director adds a 48-frame note for a background-reactivity review. | P2, Rust |

### Cut

| Feature | Example use | Phase and owner |
| --- | --- | --- |
| [CUT-01](features/media-cut.md#cut-01-source-tape-and-rapid-assembly) Source tape and rapid assembly | An agent prepares an opening montage from three music-video takes at 24 fps. | P7, Rust |
| [CUT-02](features/media-cut.md#cut-02-sync-bins-and-multicamera-edits) Sync bins and multicamera edits | An interview has a wide camera, close camera, and separate recorder audio. | P7, Rust |
| [CUT-03](features/media-cut.md#cut-03-source-overwrite-and-smart-insert) Source overwrite and smart insert | A 24 fps interview timeline shows the wide camera between frames 240 and 480. | P7, Rust |
| [CUT-04](features/media-cut.md#cut-04-live-ingest-and-replay) Live ingest and replay | During a filmed music performance, a creator wants to review the preceding chorus while the camera records the next verse. | P7, Rust |

### Fusion

| Feature | Example use | Phase and owner |
| --- | --- | --- |
| [FUSION-01](features/fusion-ai.md#fusion-01-typed-node-graphs-and-caching) Typed node graphs and caching | A creator previews a 24 fps chorus spanning frames 960 through 1199. | P3, Rust |
| [FUSION-02](features/fusion-ai.md#fusion-02-merge-masks-and-blend-modes) Merge masks and blend modes | Frames 480 through 719 contain a singer over a replacement harbor. | P3, Rust |
| [FUSION-03](features/fusion-ai.md#fusion-03-native-script-titles-and-typography) Native-script titles and typography | A Telugu chorus displays "నిన్నే తలచాను" on V3 from frame 960 for 96 frames at 24 fps. | P3, Rust |
| [FUSION-04](features/fusion-ai.md#fusion-04-motion-curves-and-expressions) Motion curves and expressions | An interview lower third fades in across frames 120 through 131. It holds, then exits across frames 360 through 371. | P3, Rust |
| [FUSION-05](features/fusion-ai.md#fusion-05-keying-and-rotoscoping) Keying and rotoscoping | A singer performs against green cloth during frames 240 through 479. | P3, Rust |
| [FUSION-06](features/fusion-ai.md#fusion-06-point-planar-and-camera-tracking) Point planar and camera tracking | A documentary shot pans past a shop sign for 120 frames. | P3, Rust |
| [FUSION-07](features/fusion-ai.md#fusion-07-3d-scenes-lights-and-particles) 3D scenes lights and particles | A music-video harbor background shows distant dust during frames 720 through 959. | P3, Rust |
| [FUSION-08](features/fusion-ai.md#fusion-08-music-reactive-environment-layers) Music-reactive environment layers | During a 96-frame chorus passage, bass energy changes harbor-light intensity on V1. | P3, Rust |

### Color

| Feature | Example use | Phase and owner |
| --- | --- | --- |
| [COLOR-01](features/color-photo.md#color-01-color-management-and-transforms) Color management and transforms | A documentary combines a camera's flat recording with a finished interview image. | P4, Rust |
| [COLOR-02](features/color-photo.md#color-02-primary-wheels-curves-and-grading) Primary wheels curves and grading | A music video's night scene is too dark after its input transform. | P4, Rust |
| [COLOR-03](features/color-photo.md#color-03-secondary-qualifiers-and-windows) Secondary qualifiers and windows | A storefront commercial needs a red shoe brighter without a change to the model's face. | P4, Rust |
| [COLOR-04](features/color-photo.md#color-04-luts-and-node-ordering) LUTs and node ordering | A music-video creator supplies a sunset LUT for V1's harbor scene. | P4, Rust |
| [COLOR-05](features/color-photo.md#color-05-scopes-and-clipping-diagnostics) Scopes and clipping diagnostics | An interview has a bright window behind the speaker. | P4, Rust |
| [COLOR-06](features/color-photo.md#color-06-hdr-grading-and-tone-mapping) HDR grading and tone mapping | A documentary sunset includes a bright sun and a dim foreground. | P4, Rust |
| [COLOR-07](features/color-photo.md#color-07-tracking-grading-masks) Tracking grading masks | In an interview, the speaker leans across frames 120 through 239 at 24 fps. | P4, Rust |
| [COLOR-08](features/color-photo.md#color-08-noise-reduction-restoration-and-grain) Noise reduction restoration and grain | A documentary's dim street shot contains visible noise. | P4, Rust |
| [COLOR-09](features/color-photo.md#color-09-stills-galleries-and-grade-matching) Stills galleries and grade matching | A music-video creator approves the harbor's blue-hour frame at frame 72. | P4, Rust |

### Fairlight

| Feature | Example use | Phase and owner |
| --- | --- | --- |
| [AUDIO-01](features/audio.md#audio-01-sample-accurate-editing-and-mixing) Sample-accurate editing and mixing | An interview has a clap 1,000 samples after unwanted opening silence. | P2, Rust |
| [AUDIO-02](features/audio.md#audio-02-waveforms-meters-and-loudness) Waveforms meters and loudness | A Telugu voice-over sits over music in a 20-second commercial. | P2, Rust |
| [AUDIO-03](features/audio.md#audio-03-eq-dynamics-and-effects) EQ dynamics and effects | An interview microphone records low rumble. | P2, Rust |
| [AUDIO-04](features/audio.md#audio-04-buses-sends-automation-and-folders) Buses sends automation and folders | A documentary has two interview tracks and music. | P2, Rust |
| [AUDIO-05](features/audio.md#audio-05-adr-voice-recording-and-foley) ADR voice recording and Foley | A documentary sentence contains handling noise. | P2, Rust |
| [AUDIO-06](features/audio.md#audio-06-surround-and-immersive-audio) Surround and immersive audio | A screening uses six named channels. | P2, Rust |
| [AUDIO-07](features/audio.md#audio-07-audio-plugins-and-external-processing) Audio plugins and external processing | A producer selects a plugin to reduce harsh interview sibilants. | P2, Rust |
| [AUDIO-08](features/audio.md#audio-08-music-envelopes-and-beat-analysis) Music envelopes and beat analysis | For Pal Pal, the agent binds the complete original master. The agent analyzes a chorus interval. | P2, Rust |

### Photo

| Feature | Example use | Phase and owner |
| --- | --- | --- |
| [PHOTO-01](features/color-photo.md#photo-01-still-development-and-raw-processing) Still development and RAW processing | A creator supplies a camera RAW portrait for square song artwork. | P4, Rust |
| [PHOTO-02](features/color-photo.md#photo-02-crop-reframe-and-image-export) Crop reframe and image export | A creator needs square artwork and a wide thumbnail from a 4000 by 6000 portrait. | P4, Rust |
| [PHOTO-03](features/color-photo.md#photo-03-albums-and-grade-versions) Albums and grade versions | A commercial shoot produces twelve shoe photographs. | P4, Rust |
| [PHOTO-04](features/color-photo.md#photo-04-tethered-capture) Tethered capture | A product photographer connects a camera for a shoe shoot. | P4, Rust |

### Deliver

| Feature | Example use | Phase and owner |
| --- | --- | --- |
| [DELIVER-01](features/delivery-collaboration-extensions.md#deliver-01-native-codec-capability-registry) Native codec capability registry | A creator supplies a 24 fps concert recording and requests an H.264 film with AAC audio. | P1, Rust |
| [DELIVER-02](features/delivery-collaboration-extensions.md#deliver-02-movie-encoding-and-muxing) Movie encoding and muxing | An interview editor requests frames 240 through 719 at 24 fps. The request includes the matching stereo audio interval. | P1, Rust |
| [DELIVER-03](features/delivery-collaboration-extensions.md#deliver-03-image-sequences-and-still-export) Image sequences and still export | A commercial designer needs frames 96 through 119 for a one-second package reveal at 24 fps. | P1, Rust |
| [DELIVER-04](features/delivery-collaboration-extensions.md#deliver-04-render-queue-cancellation-and-recovery) Render queue cancellation and recovery | A music-video render stops after a native host loses power at frame 2100. | P6, Effect |
| [DELIVER-05](features/delivery-collaboration-extensions.md#deliver-05-source-bound-technical-qc) Source-bound technical QC | A documentary contains an intentional black opening for 48 frames at 24 fps. | P2, Rust |
| [DELIVER-06](features/delivery-collaboration-extensions.md#deliver-06-presets-and-remote-rendering) Presets and remote rendering | A creator selects a portrait promo preset for source frames 1440 through 1919 at 24 fps. | P6, Effect |
| [DELIVER-07](features/delivery-collaboration-extensions.md#deliver-07-release-kit-profile-and-archive) Release-kit profile and archive | A creator supplies a three-minute canonical song, Telugu lyrics, artist references, and three chosen chorus intervals. | P5, Rust |

### Collaboration

| Feature | Example use | Phase and owner |
| --- | --- | --- |
| [COLLAB-01](features/delivery-collaboration-extensions.md#collab-01-project-libraries-and-tenant-authorization) Project libraries and tenant authorization | Two labels use the hosted application for separate music catalogs. | P6, Effect |
| [COLLAB-02](features/delivery-collaboration-extensions.md#collab-02-optimistic-revisions-and-shared-editing) Optimistic revisions and shared editing | Two agents inspect revision 18. | P6, Rust |
| [COLLAB-03](features/delivery-collaboration-extensions.md#collab-03-clip-bin-and-timeline-ownership) Clip bin and timeline ownership | An assistant claims the interview bin while the assistant organizes camera clips. | P6, Effect |
| [COLLAB-04](features/delivery-collaboration-extensions.md#collab-04-cloud-media-synchronization) Cloud media synchronization | A documentary editor publishes a 2 GB camera recording for a remote test host. | P6, Effect |
| [COLLAB-05](features/delivery-collaboration-extensions.md#collab-05-review-annotations-and-notifications) Review annotations and notifications | A reviewer marks the Telugu lyric at frame 420 as too low on a portrait promo. | P6, Effect |

### AI and extensions

| Feature | Example use | Phase and owner |
| --- | --- | --- |
| [AI-01](features/fusion-ai.md#ai-01-transcription-and-text-driven-editing) Transcription and text-driven editing | A Telugu interview includes a pause between two answers. | P7, Rust |
| [AI-02](features/fusion-ai.md#ai-02-segmentation-object-recognition-and-masks) Segmentation object recognition and masks | A singer crosses a dim harbor during frames 480 through 719. | P7, Rust |
| [AI-03](features/fusion-ai.md#ai-03-smart-reframe-upscale-and-motion-synthesis) Smart reframe upscale and motion synthesis | A creator makes a 20-second portrait promo from a landscape chorus. | P7, Rust |
| [AI-04](features/fusion-ai.md#ai-04-automatic-color-and-scene-search) Automatic color and scene search | A documentary editor asks for evening harbor shots to accompany a Telugu interview. | P7, Rust |
| [EXT-01](features/delivery-collaboration-extensions.md#ext-01-ofx-and-effect-plugin-execution) OFX and effect plugin execution | A commercial editor applies an experimental texture plugin to the background clip at frames 300 through 359. | P7, Rust |
| [EXT-02](features/delivery-collaboration-extensions.md#ext-02-interchange-edl-aaf-xml-and-otio) Interchange EDL AAF XML and OTIO | A documentary editor receives a cut list for ten interview clips at 30000/1001 fps. | P7, Rust |
| [EXT-03](features/delivery-collaboration-extensions.md#ext-03-control-panels-and-capture-hardware) Control panels and capture hardware | An interview editor binds a jog wheel to frame stepping on a 24 fps timeline. | P7, Rust |
| [EXT-04](features/delivery-collaboration-extensions.md#ext-04-optional-editor-and-review-ui) Optional editor and review UI | A creator opens a portrait promo. The creator uses the keyboard to select the Telugu lyric layer at frame 480. | P6, UI |

## Check the documentation

Run the optional document checks from the native-editor directory. Only documentation checks use Node.

```sh
node docs/features/check.mjs
node docs/check-spec.mjs
```

Coverage checks do not run the editor, approve a film, or verify future capabilities.

The index is a versioned family map.
It does not replace a complete Resolve reference inventory.
Use [TASKS.md](TASKS.md) for the inventory and local coverage backlog.

[Rust CLI examples](CLI-EXAMPLES.md) give the current local test sequence.
[Layer composition contract](LAYERS.md) explains layer order, timed visibility, alpha, masks, and graph boundaries.
[Implementation sequence](IMPLEMENTATION.md) describes the staged program.
