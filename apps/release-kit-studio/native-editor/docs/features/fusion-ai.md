# Fusion and AI feature contracts

These twelve families describe proposed behavior. No runtime feature in these contracts is complete. FUSION families are planned P3 capabilities, with camera solving and full 3D workflows deferred to P7. AI families are planned P7 capabilities.

Only CORE-01 through CORE-08 have current Rust implementations. No family has a trusted verified state. P0 renders one solid-color track to PNG with no overlap. P0 does not render movies, audio, text, or layered compositions.

Rust owns these native operations. Separate Effect and UI applications can submit commands in a future implementation. No Effect credentials are necessary for local use. Model choice, inference runtime, hardware, and codec SDK support are experiments.

Unsupported operations fail explicitly. There is no FFmpeg, libav, Resolve execution, or hidden renderer fallback. Blackmagic capability references do not establish identical algorithms or output. These contracts extend the [layer model](../LAYERS.md), [native specification](../SPEC.md), and [implementation sequence](../IMPLEMENTATION.md).

## FUSION-01. Typed node graphs and caching

### What it does

A node graph connects small image operations through declared input and output types. A cache reuses an unchanged operation's result during repeated previews.

### Scenario

A creator previews a 24 fps chorus across frames 960 through 1199. The graph combines a harbor background, performer mask, and Telugu lyric layer. The agent changes only the lyric opacity. Background decoding and the unchanged mask can reuse cached results. The requested frame still reflects the new opacity and exact revision.

### Inputs and result

Planned `graph.put` accepts a project revision, stable intent, graph identity, typed nodes, connections, and source bindings. Rust owns the immutable graph revision and evaluation dependencies. Port types, operator versions, and resource limits must have a Rust schema before implementation.

### Behavior rules

- Validate the whole graph before you commit a revision. Cycles, missing nodes, and incompatible ports leave no new revision.
- Evaluate at integer frame positions with the project's rational rate and declared source mapping.
- Cache identity includes node content, upstream inputs, frame position, source hashes, graph binding, and renderer build.
- Changed dependencies invalidate dependent results. Unrelated results stay reusable only when their complete bindings match.
- The first version supports a bounded operator set. Unknown operators fail before the renderer starts without fallback.

### Implementation pieces

- FUSION-01.1. Define typed graph ports, stable identities, and atomic graph validation.
- FUSION-01.2. Evaluate an acyclic graph in dependency order at an exact frame.
- FUSION-01.3. Store cache entries with complete content and build bindings.
- FUSION-01.4. Add bounded eviction and inspectable cache decisions without a change to output semantics.

### Verification

FUSION-01-A compares cold and cached renders through an independent native PNG decoder. Pixels and source bindings must match. A lyric change must invalidate its dependent merge.

FUSION-01-B submits a cycle and a mismatched port. Project readback must show the previous revision and no accepted graph mutation.

### Status and dependencies

Planned P3, owned by Rust `fusion`. Ledger prerequisites are CORE-01 and CORE-02. Measured native ingest support is also necessary for movie sources. No graph evaluator or cache currently exists.

## FUSION-02. Merge masks and blend modes

### What it does

A merge combines foreground and background images. A mask supplies pixel coverage, while a blend mode defines how covered colors combine.

### Scenario

Frames 480 through 719 contain a singer over a replacement harbor. V1 contains the harbor. V2 contains the masked singer. V3 contains transparent lyrics. The agent reduces harbor glow and keeps the singer's hair edge and lyric opacity unchanged. An inactive lyric clip reveals lower tracks rather than black pixels.

### Inputs and result

Planned `graph.compose` takes ordered inputs, mask references, opacity, blend mode, coordinate mapping, and working color policy. Rust owns the composite graph and revision-bound frame artifact. The supported blend list and numeric tolerances are open schema and corpus decisions.

### Behavior rules

- Normal source-over reuses the fixed P2 linear-RGB compositor and premultiplied alpha. Premultiplied colors already include alpha. New blend operators must have their own declared contracts.
- Effective coverage combines source alpha, clip opacity, and mask coverage. Clip inactivity stays separate from zero opacity.
- Masks declare inversion, feather width, coordinates, and time binding. Missing masks fail instead of conversion to full coverage.
- Track order sets the stack order between clips. Node order governs merges inside a clip.
- Rational-rate frame boundaries and immutable revisions stay authoritative. Unsupported blend modes fail without approximation or fallback.

### Implementation pieces

- FUSION-02.1. Implement declared normal source-over and alpha conversion boundaries.
- FUSION-02.2. Sample geometric or imported masks in explicit coordinates.
- FUSION-02.3. Add inversion, feathering, and timed opacity with bounded parameters.
- FUSION-02.4. Add independently specified blend operators after reference-image checks.

### Verification

FUSION-02-A decodes a small reference composite independently. Every color channel and alpha value must match expected opaque, transparent, and partial-coverage pixels.

FUSION-02-B requests an absent mask or unsupported blend. Readback must show no new revision or output. Interval-boundary frames must reveal the correct lower track.

### Status and dependencies

Planned P3, owned by Rust `fusion`. Ledger prerequisites are CORE-01, CORE-02, and FUSION-01. Multi-track use must have EDIT-01. Current P0 pixels do not prove alpha composition.

## FUSION-03. Native-script titles and typography

### What it does

The planned text renderer gives Telugu, Hindi, and Tamil text correct glyph placement. A glyph is the visible shape from a font.

### Scenario

A Telugu chorus displays "నిన్నే తలచాను" on V3 from frame 960 for 96 frames at 24 fps. The agent replaces the line. The performer and adjacent captions stay unchanged. The renderer joins the script correctly and keeps the line inside its declared portrait-safe bounds.

### Inputs and result

Planned `text.render` takes exact Unicode text, font artifacts, style, layout bounds, and frame visibility. Rust owns the text-layer definition, shaped layout, and rendered artifact. Font selection, fallback order, line-breaking rules, and overflow policy must have explicit schema decisions.

### Behavior rules

- Keep native script and supplied text. Do not romanize, translate, or silently rewrite text.
- Shaping maps text to glyphs before layout. Combining marks and joined forms stay part of their text clusters.
- Record font hashes and any fallback font. Missing glyphs produce a declared failure or explicit diagnostic, never silent substitution.
- Text visibility uses integer intervals at the rational project rate. Animation affects the text layer only when explicitly requested.
- Initial work supports bounded two-dimensional layout. Complex layout must have corpus checks before support. Revisions stay immutable and unsupported paths have no fallback.

### Implementation pieces

- FUSION-03.1. Bind Unicode content, fonts, and explicit layout policy to a text layer.
- FUSION-03.2. Shape and rasterize native-script clusters with measured glyph bounds.
- FUSION-03.3. Implement line breaks, fallback diagnostics, and overflow policy.
- FUSION-03.4. Expose layout measurements for caption placement and later animation.

### Verification

FUSION-03-A compares Telugu, Hindi "तुम साथ हो", and Tamil "நீ அருகில்" against reviewed glyph references. An independent image decoder confirms bounds and transparent backgrounds. Native readers examine script correctness separately.

FUSION-03-B removes a required font or narrows the bounds below the declared overflow limit. The operation must report the exact layout problem without a change to the accepted revision.

### Status and dependencies

Planned P3, owned by Rust `fusion`. Ledger prerequisites are CORE-01, CORE-02, and FUSION-01. Timed captions also must have timeline support. No current text shaping or font corpus is verified.

## FUSION-04. Motion curves and expressions

### What it does

Motion curves change a parameter over time between specified values. Bounded expressions calculate parameters through a small permitted language.

### Scenario

An interview lower third fades in across frames 120 through 131, holds, then exits across frames 360 through 371. The agent animates the graphic's position and opacity. The interview image and audio stay unchanged. A sample of frame 132 shows the completed entrance. It does not show an intermediate result that changes with execution timing.

### Inputs and result

Planned `graph.animate` takes node and parameter targets, frame-indexed keys, interpolation policy, and optional expressions. Rust owns the animation binding in an immutable revision. The permitted expression grammar, numeric bounds, and behavior outside the keyed interval must have schemas.

### Behavior rules

- Initial curves support declared constant and linear interpolation. Later easing operators must have separate reference cases.
- Evaluate time from integer positions and rational frame rate. Preview order cannot change a parameter result.
- Expressions use bounded evaluation cost and declared inputs. They cannot execute arbitrary code, read files, access a network, or mutate state.
- Reject undefined references, non-finite values, and expression cycles before you commit.
- Keep generic keyframe edit operations in EDIT-08. This family applies curves to graph parameters. Unsupported interpolation fails without fallback.

### Implementation pieces

- FUSION-04.1. Bind typed animatable parameters to frame-indexed curves.
- FUSION-04.2. Implement deterministic interpolation and endpoint policy.
- FUSION-04.3. Parse and evaluate a bounded expression language.
- FUSION-04.4. Examine sampled values and enforce numeric and evaluation limits.

### Verification

FUSION-04-A reads parameter values at the first, midpoint, last, and adjacent frames. Independently decoded frames must match the declared fade and position values.

FUSION-04-B submits an expression cycle and an excessive evaluation request. Both must fail atomically. Restart and reversed preview order must not alter accepted samples.

### Status and dependencies

Planned P3, owned by Rust `fusion`. Ledger prerequisites are CORE-01, CORE-02, FUSION-01, and EDIT-08. No motion evaluator or expression runtime currently exists.

## FUSION-05. Keying and rotoscoping

### What it does

Keying extracts coverage from selected image colors. Rotoscoping defines coverage with drawn shapes that can change across frames.

### Scenario

A singer performs against green cloth during frames 240 through 479. The agent creates a key, then corrects a sleeve edge with a drawn mask. The mask places the singer over V1's harbor. The agent previews hair and hand edges before the agent accepts the extraction for the chorus.

### Inputs and result

Planned `mask.extract` takes hashed source frames, extraction method, color parameters or shape keys, coordinate space, and frame range. Rust owns a revision-bound mask artifact. Initial key thresholds, shape interpolation, edge treatment, and confidence reports must have a declared schema.

### Behavior rules

- Start with explicit color selection and manually keyed shapes. AI-02 owns AI segmentation. Keying does not imply segmentation support.
- Store coverage separately from foreground colors. Despill, which removes background color contamination, must have its own explicit operator settings.
- Keep integer source and timeline mapping at rational rates. Mask edits create new revisions without replacement of the original sources.
- Temporal interpolation cannot silently bridge a shot cut or unsupported range. Invalid shapes and unavailable decode support fail before output.
- Do annotated experiments on hair, transparency, motion blur, and green clothing. The contract does not claim proprietary keyer equivalence or a hidden fallback.

### Implementation pieces

- FUSION-05.1. Define source-bound mask artifacts and extraction settings.
- FUSION-05.2. Implement bounded color-key coverage on decoded native frames.
- FUSION-05.3. Rasterize manually keyed shapes and explicit temporal interpolation.
- FUSION-05.4. Add separately measured edge treatment and despill operators.

### Verification

FUSION-05-A compares coverage against labeled opaque, transparent, and edge pixels. Independently decoded masks and adjacent-frame differences establish measured accuracy and stability.

FUSION-05-B uses green clothing and a shot cut. The test must expose wrong coverage and prevent silent interpolation across the cut. Visual review still decides whether the creator accepts the extraction.

### Status and dependencies

Planned P3, owned by Rust `fusion`. Ledger prerequisites are CORE-01 and CORE-02. Movie extraction must have MEDIA-01 and native decoder evidence. Mask application must have FUSION-02. Nothing is runtime verified.

## FUSION-06. Point planar and camera tracking

### What it does

Point tracking calculates the position of an image location. Planar tracking calculates the position of a flat region. Camera tracking estimates camera motion through a scene.

### Scenario

A documentary shot pans past a shop sign for 120 frames. The agent tracks the sign's corners. The agent attaches a replacement graphic. When a pedestrian obscures the sign for 12 frames, the track reports the gap. The graphic cannot jump onto the pedestrian through an unreported guess.

### Inputs and result

Planned `track.solve` takes source hashes, frame range, selected points or region, tracking mode, and camera assumptions when applicable. Rust owns the trajectory artifact and diagnostic measurements. Units, coordinate conventions, failure thresholds, and camera calibration fields are open schema decisions.

### Behavior rules

- Start with bounded two-dimensional point and planar tracks with explicit seeds or regions. Camera solving is a P7 experiment.
- Bind trajectories to exact source frames. Timeline placement uses declared integer mapping at the rational project rate.
- Report missing observations and confidence. Interpolation across a gap must use an explicit policy.
- Measure reprojection error, the distance between observed positions and positions predicted by a solution. Reject insufficient evidence under declared thresholds.
- Tracking creates no mask or edit by itself. Application of a solution creates an immutable revision. Unsupported solvers or decoder formats fail without fallback.

### Implementation pieces

- FUSION-06.1. Define source-bound observations, trajectories, and diagnostic units.
- FUSION-06.2. Implement bounded point tracking with explicit gap results.
- FUSION-06.3. Implement bounded planar tracking against annotated corner trajectories.
- FUSION-06.4. Evaluate calibrated camera solving and degeneracy detection separately.

### Verification

FUSION-06-A compares a synthetic translated sign against known point positions. Readback must keep frame identities. Measured pixel error must meet the corpus threshold.

FUSION-06-B uses an occluded region and a scene without sufficient distinct features. The solver must report gaps or reject the solve. A successful attachment artifact must not substitute for a failed solution.

### Status and dependencies

Planned P3, owned by Rust `fusion`. CORE-01 and CORE-02 are ledger prerequisites. P3 covers bounded point and planar tracking. Camera solving and advanced integration must have P7 experiments. Native frame ingest is also necessary. No solver is available.

## FUSION-07. 3D scenes lights and particles

### What it does

A 3D scene places objects, lights, and a camera in a shared coordinate system. Particles supply repeated objects in motion with declared initial conditions.

### Scenario

A music-video harbor background shows distant dust during frames 720 through 959. The agent renders the dust behind the singer and V3 lyrics. Near particles pass behind a foreground pier because depth determines visibility. A fixed particle seed makes repeated previews follow the same trajectories.

### Inputs and result

Planned `scene.render` takes scene objects, camera, lights, materials, frame range, and seeded particle settings. Rust owns the scene definition, evaluated frame artifacts, and source bindings. Coordinate handedness, distance units, material support, and render precision must have an explicit schema.

### Behavior rules

- The first P3 slice uses bounded geometry, a declared camera, minimal lighting, and seeded particles. Full scene workflows must have P7 acceptance.
- Evaluate particle age from integer frames and rational rate. Frame render order cannot change particle trajectories.
- Depth visibility is distinct from alpha composition. FUSION-02 owns integration with performer and text layers.
- Scene changes create immutable revisions. Receipts bind seeds, parameters, source artifacts, and renderer build.
- Set limits for objects, particles, and memory before execution. Unsupported render paths fail without fallback. GPU support must have actual device and recovery evidence.

### Implementation pieces

- FUSION-07.1. Define scene coordinates, bounded objects, cameras, and transforms.
- FUSION-07.2. Render minimal geometry with measured depth occlusion.
- FUSION-07.3. Implement a declared lighting model and transparent output policy.
- FUSION-07.4. Evaluate seeded particle trajectories independently of preview order.

### Verification

FUSION-07-A renders a known camera and two objects that overlap. Independent image and depth readback must show the expected projection and occlusion.

FUSION-07-B repeats a seeded sequence in forward and reversed frame order. Trajectories must match. An excessive particle count must fail before allocation or revision mutation.

### Status and dependencies

Planned P3, owned by Rust `fusion`, with CORE-01 and CORE-02 as prerequisites. Simple 3D and seeded particles form the bounded slice. Full 3D workflows and advanced integration must have P7 experiments. Composition must have FUSION-02. No scene renderer or GPU claim is verified.

## FUSION-08. Music-reactive environment layers

### What it does

Audio measurements change selected background parameters over time. Protection masks keep performers, lyrics, and titles outside the affected region.

### Scenario

During a 96-frame chorus passage, bass energy changes harbor-light intensity on V1. V2 holds the singer and V3 holds "నిన్నే తలచాను". The agent binds only harbor glow and water displacement to the exact song's measurements. Comparison frames show water in motion. Performer identity and lyric geometry stay fixed.

### Inputs and result

Planned `reactive.bind` takes the canonical audio hash, measured envelope artifact, environment parameter targets, protection masks, bounds, and smoothing. Rust owns the binding in an immutable revision. An envelope is a time series of audio measurements. Sample-to-frame mapping and allowed target classes must have schemas.

### Behavior rules

- AUDIO-08 owns audio measurements. This family consumes those source-bound values. It does not analyze an unrelated song.
- Map sample positions to integer timeline frames through declared rational timing. Retiming must have an explicit mapping.
- Make sure that protection coverage includes people, lyrics, and titles. Missing or stale coverage blocks the binding.
- Bound displacement, intensity, and rate of change. Protection applies to the operator's full affected region, which includes blur or glow spread.
- Initial work supports a small declared environment-parameter set. Unsupported targets fail without fallback. Temporal quality must also have motion review.

### Implementation pieces

- FUSION-08.1. Validate envelope, audio, frame mapping, and protection-mask bindings.
- FUSION-08.2. Evaluate bounded parameter response and explicit smoothing.
- FUSION-08.3. Apply protection to complete effect regions before composition.
- FUSION-08.4. Produce comparison samples and diagnostics for response limits.

### Verification

FUSION-08-A uses known impulses and protection masks. Independent frames must show expected background changes and unchanged protected pixels. Readback confirms the audio hash and exact frame mapping.

FUSION-08-B substitutes an envelope from another song or omits protection. The operation must fail without output or revision mutation. Two short motion reviews stay separate from numerical checks and creative acceptance.

### Status and dependencies

Planned P3, owned by Rust `fusion`. Ledger prerequisites are CORE-01, CORE-02, FUSION-02, and AUDIO-08. Performer masks can use FUSION-05 or later AI-02. No reactive runtime currently exists.

## AI-01. Transcription and text-driven editing

### What it does

Transcription proposes native-script words with source timestamps. Text-driven editing converts selected transcript intervals into proposed timeline edits for explicit acceptance.

### Scenario

A Telugu interview includes a pause between two answers. The agent proposes a transcript and marks the pause's sample interval. The creator corrects one word before the agent proposes a cut. Acceptance of the cut removes only the approved interval. The original audio, transcript proposal, and edit decision stay inspectable.

### Inputs and result

Planned `speech.align` takes hashed audio, language, optional exact text, model artifacts, and alignment policy. Rust `operators` owns the timestamped proposal artifact and provenance. Transcript corrections and timeline mutations are separate revisioned results. Model license, token timing, confidence, and acceptance thresholds stay open.

### Behavior rules

- Keep Telugu, Hindi, and Tamil scripts. Never substitute romanized text as an accepted native-script result.
- Store word positions in source samples. Frame conversion declares rounding and rational timing.
- Record model hash, runtime version, parameters, source hash, and nondeterminism. A model change must have new drift evaluation.
- No inferred word or cut becomes accepted silently. Text selection uses EDIT operations for an atomic immutable timeline revision.
- Missing model artifacts, unsupported language, decoder, or inference SDK fail before execution. No provider, hardware, quality, or fallback path is promised.

### Implementation pieces

- AI-01.1. Define source-bound transcript, alignment, and provenance artifacts.
- AI-01.2. Evaluate one licensed native inference path on a labeled speech corpus.
- AI-01.3. Keep corrected words and uncertainties through alignment.
- AI-01.4. Translate accepted text intervals into explicit timeline edit proposals.

### Verification

AI-01-A measures word errors and timestamp errors against independently labeled native-script audio. Artifact readback must keep language, source hash, and model identity.

AI-01-B uses speech from simultaneous speakers, an unsupported language, and a changed model. Uncertainty or failure must stay visible. Model drift must block promotion until thresholds pass. Listening and native-reader acceptance stay separate.

### Status and dependencies

Planned P7, owned by Rust `operators`. Ledger prerequisites are CORE-01 and CORE-02. Actual use also must have a native audio decoder, AUDIO-02 timing, and EDIT-01 for cuts. No inference path is selected or verified.

## AI-02. Segmentation object recognition and masks

### What it does

Segmentation proposes which pixels belong to a selected subject. Recognition proposes object labels, with uncertainty retained rather than treated as fact.

### Scenario

A singer crosses a dim harbor during frames 480 through 719. The agent proposes a performer mask for background reactivity. At frame 603, the model misses a raised hand. The preview exposes the missing coverage, and the creator corrects it before FUSION-08 uses the mask. Lyrics stay a separate protected layer.

### Inputs and result

Planned `vision.segment` takes hashed source frames, selected subject or prompt, frame range, model artifacts, and inference settings. Rust owns a mask proposal sequence, confidence diagnostics, and provenance. Object identity, label vocabulary, correction storage, and threshold policy must have schemas.

### Behavior rules

- Bind each mask to exact source frames and dimensions. Rational-rate timeline mapping stays explicit.
- Separate recognition labels from mask coverage. A high-confidence label cannot prove accurate edges.
- Record model hash, runtime, parameters, and source hashes. Reevaluate labeled scenes when a model or inference path changes.
- Get explicit acceptance before a proposal protects a performer. Corrections create immutable artifacts without replacement of the initial proposal.
- Shot cuts, occlusion, unsupported decode formats, or unavailable inference SDKs produce declared gaps or errors. No hidden fallback or guaranteed quality applies.

### Implementation pieces

- AI-02.1. Define frame-bound masks, labels, uncertainty, and provenance.
- AI-02.2. Evaluate one licensed segmentation model on a labeled scene corpus.
- AI-02.3. Keep subject selection and measure temporal coverage changes.
- AI-02.4. Store reviewed corrections and accepted mask versions for composition.

### Verification

AI-02-A measures overlap with labeled performer masks and boundary error across frames. An independent mask decoder confirms dimensions, frame count, and source binding.

AI-02-B uses hand occlusion and a shot cut. Missing coverage must stay inspectable and unaccepted. A substituted model must have a new drift assessment. Motion review examines flicker separately from measured coverage.

### Status and dependencies

Planned P7, owned by Rust `operators`. Ledger prerequisites are CORE-01 and CORE-02. Movie use must have native ingest. Application of accepted coverage must have FUSION-02. No segmentation or object-recognition implementation is available.

## AI-03. Smart reframe upscale and motion synthesis

### What it does

A reframe proposes a crop that keeps selected subjects. An upscale proposes more output pixels. Motion synthesis proposes more or changed frames.

### Scenario

A creator makes a 20-second portrait promo from a landscape chorus. The agent proposes a crop that tracks the singer's motion. The crop keeps her raised hand inside its bounds. A separate upscale proposal supplies the requested dimensions. Lyrics render afterward in FUSION-03. Before the creator accepts either proposal, the creator compares original and transformed motion.

### Inputs and result

Planned `vision.transform` takes source hashes, operation mode, source interval, target geometry, protected regions, and model provenance. Rust owns new proposed media artifacts and mappings. Crop constraints, temporal synthesis policy, model licenses, and inference SDK support must have separate contracts.

### Behavior rules

- Treat reframe, upscale, and synthesis as distinct modes. Each mode has its own support status and acceptance thresholds.
- Keep source media. Accepted substitutions create immutable revisions with explicit source-to-output frame mapping at rational rates.
- Record model hash, runtime, parameters, seed where applicable, and measured output hashes. A model change must have drift acceptance.
- Reframe must report retention failures. An upscale does not prove restored detail. Synthesis must not invent accepted performer identity or rewrite baked-in text silently.
- Unsupported native codecs, inference paths, or resource requests fail without fallback. No provider, hardware availability, resolution quality, or motion quality is guaranteed.

### Implementation pieces

- AI-03.1. Define separate transform modes, provenance, and exact frame mappings.
- AI-03.2. Propose constrained crops with subject-retention diagnostics.
- AI-03.3. Evaluate licensed upscale inference against native-resolution references.
- AI-03.4. Evaluate motion synthesis with identity, seam, and text-preservation checks.

### Verification

AI-03-A independently decodes a transformed sequence. Dimensions, frame count, timing, source bindings, and labeled subject retention must meet declared thresholds.

AI-03-B does tests of late-frame face changes, occluded hands, baked-in lyrics, and a shot boundary. Detected distortion blocks acceptance. Model substitution must have a new corpus run. Complete motion review stays separate from technical success.

### Status and dependencies

Planned P7, owned by Rust `operators`. Ledger prerequisites are CORE-01 and CORE-02. Real use must have native ingest and export support. Composition and text reconstruction must have FUSION-02 and FUSION-03. No transform model is selected.

## AI-04. Automatic color and scene search

### What it does

Scene search proposes source intervals that match a description or reference. Automatic color matching proposes adjustments relative to a declared reference image.

### Scenario

A documentary editor asks for evening harbor shots to accompany a Telugu interview. The agent returns ranked intervals from the project's hashed footage. The creator selects one interval and requests a color proposal that matches an accepted sunset still. The agent keeps the selected shot and exposes the proposed grade for comparison.

### Inputs and result

Planned `vision.search` takes a bound media collection, query or reference, operation mode, and model artifacts. Rust owns ranked interval results or a color-adjustment proposal with provenance. Search scores, index format, color parameter representation, and acceptance thresholds stay open schema choices.

### Behavior rules

- Search results identify exact sources and integer intervals at declared rational rates. A result does not insert footage into a timeline.
- Color proposals use declared color-space metadata and COLOR operations. Missing metadata blocks a color match. Do not assume a color space.
- Record source, reference, model, index, runtime, and parameter identities. Changed collections or models must have new drift checks.
- Keep original media and accepted grades. Application of a proposal creates an immutable revision after explicit selection.
- Report uncertain or empty results. Unsupported native decode, model artifacts, or SDKs fail without fallback. No semantic accuracy or proprietary matching equivalence is promised.

### Implementation pieces

- AI-04.1. Define source-bound search indexes, interval results, and provenance.
- AI-04.2. Evaluate one licensed retrieval path against labeled scene queries.
- AI-04.3. Define managed color-reference proposals and inspectable parameters.
- AI-04.4. Evaluate retrieval and color drift before you accept changed models or indexes.

### Verification

AI-04-A measures retrieved intervals against labeled harbor scenes. Independent source readback confirms interval boundaries. Color reference cases measure declared patch differences separately from creative grade approval.

AI-04-B uses an absent scene, stale index, and reference without color metadata. Results must stay empty, rejected, or explicitly uncertain. The operation must not insert a source or change a grade automatically.

### Status and dependencies

Planned P7, owned by Rust `operators`. Ledger prerequisites are CORE-01 and CORE-02. Real retrieval must have MEDIA-01. Managed matching must have COLOR-01 and the selected grading operator. No search index, inference provider, or model is verified.
