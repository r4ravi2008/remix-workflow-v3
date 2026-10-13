# Color and photo feature contracts

All 13 families in this document are planned P4 behavior contracts. No color or photo tool in these contracts is implemented. The current Rust renderer produces raw solid-color PNG frames. It does not decode photographs, manage color, track masks, or communicate with cameras.

Rust owns these proposed local features. These features need no Effect credentials, UI framework, external service, current GPU, or Resolve session. A software development kit, or SDK, supplies a vendor's programming interface. Native SDK, device, RAW camera-data format, and model support stay unproven until named experiments pass. Public Blackmagic capability references establish family scope only. They do not establish proprietary algorithm parity or bitwise identical output.

Each proposed mutation uses an expected immutable revision and a stable intent. Frame selection uses integer positions at the project's rational frame rate. Alpha means pixel transparency. For example, a transparent lyric layer shows the scene underneath.

Unsupported operations fail explicitly without FFmpeg, libav, or a hidden renderer fallback. Acceptance must bind source hashes, parameters, color declarations, and implementation identity. Numeric color evidence, frame inspection, playback, and appearance approval stay separate states. See the [native specification](../SPEC.md) and [phase guide](../IMPLEMENTATION.md).

## COLOR-01. Color management and transforms

### What it does

Color management declares what pixel values represent before image operations or display. A color transform converts values between declared spaces so mixed camera sources share a consistent interpretation.

### Scenario

A documentary combines a camera's flat recording with a finished interview image. The agent declares each input space and one working space. For frames 240 through 479 at 24 fps, both clips use the same declared output transform. The comparison preview lets the creator assess the interview without an accidental second transform.

### Inputs and result

Planned command `color.configure` accepts project revision, source bindings, input declarations, working space, and output policy. Rust stores a versioned color configuration and returns its revision and hash. Color primaries define red, green, and blue references. A transfer function maps stored numbers to light. The working space is the shared calculation space. Supported identifiers, precision, white-point adaptation, and configuration scope do not yet have schemas.

### Behavior rules

- Start with one documented transform path and reference patches, instead of automatic camera detection.
- Correct missing input declarations or declarations that disagree before the renderer starts.
- Apply each declared transform once. Keep source bytes and timeline positions.
- Declare the alpha policy and out-of-range behavior. Do not silently clamp during intermediate calculations.

### Implementation pieces

- `COLOR-01.1` Define validated input, working, and output declarations.
- `COLOR-01.2` Implement one reference-tested conversion path.
- `COLOR-01.3` Bind configuration revisions to frame evaluation and receipts.
- `COLOR-01.4` Evaluate more camera profiles as separate experiments.

### Verification

`COLOR-01-A` converts independently generated patches.

1. Compare decoded output values with independent equations under a published numeric tolerance.

`COLOR-01-B` supplies an unknown input space.

1. Read back the result.
2. Make sure that the rejection is explicit.
3. Make sure that the project hash is unchanged.
4. Make sure that no output artifact exists.

Patch values that agree do not approve the film's appearance.

### Status and dependencies

Planned P4, Rust `color`. Ledger prerequisites are CORE-01 and CORE-02. Real image evaluation also must have native media support. No managed transform is available in P0.

## COLOR-02. Primary wheels curves and grading

### What it does

A primary grade changes the whole image's brightness, color balance, and contrast. A curve maps an input channel value to an output value.

### Scenario

A music video's night scene is too dark after its input transform. The agent raises the scene's darker values and reduces its blue cast on V1. The change covers frames 720 through 959 at 24 fps. Performer and Telugu lyric layers retain their separate grades. The creator sees two previews of the same source frame.

### Inputs and result

Planned command `color.grade` accepts a clip or node target, immutable revision, named operator parameters, and optional frame interval. Rust stores an ordered grade version. Wheel controls represent channel adjustments over declared tonal ranges. Their formulas, parameter units, curve interpolation, and supported ranges do not yet have definitions. Schemas cannot expose the controls before these definitions exist.

### Behavior rules

- Start with explicit exposure and channel operations. Advanced wheels must have independent reference cases.
- Run primary operations in the declared working space and recorded order.
- Reject nonfinite parameters and invalid curve points before you commit a revision.
- Keep unclipped intermediate values where supported. Record any deliberate output clipping policy.
- Clip-local grades must not change other layers or integer edit boundaries.

### Implementation pieces

- `COLOR-02.1` Define grade operators, units, and valid parameter domains.
- `COLOR-02.2` Implement exposure and channel transforms with patch references.
- `COLOR-02.3` Add bounded curve interpolation and ordered evaluation.
- `COLOR-02.4` Bind grade versions to clips and comparison frames.

### Verification

`COLOR-02-A` applies a known exposure adjustment to a linear ramp.

1. Independently decode the image.
2. Compare each channel against reference arithmetic.

`COLOR-02-B` submits an invalid curve.

1. Examine the result.
2. Make sure that the rejection is atomic.
3. Make sure that the grade revision is unchanged.

Numeric agreement does not establish favorable skin tones or approved contrast.

### Status and dependencies

Planned P4, Rust `color`. The prerequisites are CORE-01, CORE-02, and COLOR-01. Primary wheels and curves are unavailable in the current renderer.

## COLOR-03. Secondary qualifiers and windows

### What it does

A secondary grade changes a selected image region. A qualifier selects pixels by color properties, while a window selects a geometric area.

### Scenario

The creator wants a brighter red shoe in a storefront commercial. The model's face must not change. At frame 360, the agent selects the shoe's red pixels inside a drawn window. The preview displays the selection as a grayscale mask. White means full adjustment and black means none. The grade then affects that selection on the shoe clip.

### Inputs and result

Planned command `color.qualify` accepts source and grade references, color thresholds, window geometry, feather width, and combination policy. Feathering softens the selection edge. Rust owns a versioned mask definition and its source binding. Threshold units, coordinate space, alpha policy, and mask combination operators do not yet have schemas.

### Behavior rules

- Start with one static geometric window and a documented color threshold operator.
- Evaluate color thresholds in a named color space. A changed space invalidates cached masks.
- Define intersection, union, inversion, and feathering explicitly before you expose those operators.
- Reject invalid geometry or thresholds atomically. Keep unselected pixels under the declared grade policy.
- Tracking belongs to COLOR-07. A static window cannot imply motion tracking.

### Implementation pieces

- `COLOR-03.1` Define source-bound qualifier and window types.
- `COLOR-03.2` Produce bounded static masks with an explicit coordinate system.
- `COLOR-03.3` Evaluate the selected grade with defined edge coverage.
- `COLOR-03.4` Add independently tested combination and feather operators.

### Verification

`COLOR-03-A` uses an annotated shoe image.

1. Compare decoded mask coverage and protected pixels against an independent reference image.

`COLOR-03-B` submits an inverted threshold range.

1. Make sure that the operation rejects the range.
2. Make sure that no new mask or grade revision exists.

Mask accuracy and numeric pixel preservation stay distinct from the creator's judgment of the shoe's appearance.

### Status and dependencies

Planned P4, Rust `color`. The prerequisites are CORE-01, CORE-02, and COLOR-01. Mask application also must have the planned P3 composition contract. No qualifier is currently callable.

## COLOR-04. LUTs and node ordering

### What it does

A lookup table, or LUT, maps input colors to recorded output colors. Ordered nodes let a creator place that mapping before or after other grade operations.

### Scenario

A music-video creator supplies a sunset LUT for V1's harbor scene. The agent creates an exposure node before the LUT for frames 0 through 119 at 24 fps. When the agent moves exposure after the LUT, the change creates a separate comparison revision. The creator can inspect how that order changes bright sky detail.

### Inputs and result

Planned command `color.lut` accepts a hashed LUT asset, declared input and output domains, interpolation method, and ordered node references. Interpolation calculates colors between recorded samples. Rust stores the parsed LUT identity and grade order. Initial file formats, table sizes, interpolation choice, and limits stay open.

### Behavior rules

- Start with one bounded LUT format and one declared interpolation method.
- Reject malformed tables, missing samples, and incompatible domains before the renderer starts.
- Record trilinear or tetrahedral interpolation by name. Do not switch methods implicitly.
- Keep node order in immutable revisions. Reject graph cycles and absent node references.
- Report the out-of-domain policy explicitly. A LUT does not identify a camera's input space automatically.

### Implementation pieces

- `COLOR-04.1` Parse and validate one bounded LUT format.
- `COLOR-04.2` Implement interpolation with independent sample references.
- `COLOR-04.3` Store ordered grade nodes and reject invalid dependencies.
- `COLOR-04.4` Bind LUT hashes and order to output receipts and caches.

### Verification

`COLOR-04-A` samples a synthetic LUT at corners and interior points.

1. Compare decoded values with a separate interpolation calculation.
2. Make sure that the order change alters expected pixels.

`COLOR-04-B` supplies a truncated LUT or cyclic order.

1. Read back the result.
2. Make sure that no revision or artifact exists.

Correct table evaluation does not approve the LUT's look.

### Status and dependencies

Planned P4, Rust `color`. The prerequisites are CORE-01, CORE-02, and COLOR-01. Graph evaluation depends on planned composition support. No LUT engine is implemented.

## COLOR-05. Scopes and clipping diagnostics

### What it does

Scopes measure the image's brightness and color distribution. Clipping diagnostics identify values outside a declared range. These values include highlights that the declared output transform discards.

### Scenario

An interview has a bright window behind the speaker. At frame 480, the agent measures the graded image before and after the output transform. A waveform shows brightness by horizontal position. A histogram counts values in bins. The report identifies clipped window pixels so the creator can compare a revised grade.

### Inputs and result

Planned command `color.measure` accepts an immutable frame binding, evaluation stage, declared range, channel selection, and scope configuration. Rust returns a source-bound measurement artifact without a change to the grade. A vectorscope plots color components around a neutral center. Bin counts, axis units, subsampling policy, and report schema do not yet have definitions.

### Behavior rules

- Start with a full-frame histogram and exact out-of-range counts.
- Record the measured color space, transform stage, frame index, and alpha treatment.
- Define waveform accumulation and vectorscope equations before you add those reports.
- Reject unsupported scope settings. Do not return a display approximation without measurement evidence.
- Never change pixels to produce a measurement or treat a legal range as an aesthetic requirement.

### Implementation pieces

- `COLOR-05.1` Define measurement stages, units, and bin boundaries.
- `COLOR-05.2` Implement histogram and clipping counts without image mutation.
- `COLOR-05.3` Add waveform and vectorscope reference calculations.
- `COLOR-05.4` Save source-bound diagnostic artifacts with implementation identity.

### Verification

`COLOR-05-A` measures an image that contains known patches.

1. Independently calculate every bin and clipped-pixel count.
2. Compare these calculations with the stored report.

`COLOR-05-B` places values exactly on range boundaries.

1. Make sure that the result obeys the documented inclusive boundary behavior.
2. Make sure that the decoded pixels are unchanged.

Scope calculations that pass do not approve exposure or conditions during visual review.

### Status and dependencies

Planned P4, Rust `color`. The prerequisites are CORE-01, CORE-02, and COLOR-01. Current PNG byte verification supplies no scopes or clipping analysis.

## COLOR-06. HDR grading and tone mapping

### What it does

High dynamic range, or HDR, represents a wider brightness range than a conventional output. Tone mapping compresses that range for a declared display target.

### Scenario

A documentary sunset includes a bright sun and a dim foreground. The agent creates separate HDR and conventional-output grade versions of the same frame. The conventional version compresses highlights toward its declared target brightness. The creator reviews both on suitable displays before the creator approves delivery. A preview on an unverified display establishes no HDR appearance proof.

### Inputs and result

Planned command `color.hdr` accepts source color declarations, target brightness, tone-mapping operator, grade reference, and output metadata policy. Brightness uses declared units such as nits, which are candelas per square meter. Rust stores the HDR configuration and output bindings. Supported transfer functions, operators, display targets, and metadata formats stay unresolved.

### Behavior rules

- Start with one documented reference transform and brightness target.
- Record peak and reference brightness. Reject contradictory or missing declarations.
- Keep source values before tone mapping. Do not silently classify conventional footage as HDR.
- Output metadata must describe the actual encoded output. Movie encoding support must have separate native proof.
- Advanced HDR operators and hardware display paths must have individual experiments, not generic HDR support claims.

### Implementation pieces

- `COLOR-06.1` Define luminance units and validated HDR configurations.
- `COLOR-06.2` Implement one reference tone-mapping operator.
- `COLOR-06.3` Bind output metadata to measured artifacts.
- `COLOR-06.4` Evaluate more transfer functions and display paths.

### Verification

`COLOR-06-A` maps a measured luminance ramp.

1. Compare decoded output luminance and stored metadata against independent reference calculations.

`COLOR-06-B` requests unsupported HDR encoding.

1. Make sure that the request fails before work enters the schedule.
2. Make sure that no artifact has false HDR tags.

Numeric luminance agreement does not prove appearance on a display or creator approval.

### Status and dependencies

Planned P4, Rust `color`. Ledger prerequisites are CORE-01 and CORE-02. Usable HDR evaluation also must have COLOR-01 and supported media paths. P0 has no HDR processing.

## COLOR-07. Tracking grading masks

### What it does

Mask tracking calculates the position of a selected region across source frames. The path keeps a local grade attached to the object during motion.

### Scenario

In an interview, the speaker leans across frames 120 through 239 at 24 fps. The agent starts with a face window at frame 120 and requests a tracked path. When the speaker passes behind a microphone, the path marks an uncertain span. The agent leaves that span for explicit correction. The agent does not move the grade onto the microphone.

### Inputs and result

Planned command `color.track` accepts exact source hash, initial mask, source-frame interval, tracking method, and stop criteria. Rust returns versioned positions, confidence information, and gaps. Confidence describes an algorithm's uncertainty, not creative quality. Coordinate transforms, confidence scale, supported methods, and cache rules do not yet have schemas.

### Behavior rules

- Start with a bounded position tracker tested on annotated motion.
- Bind paths to source identity, dimensions, frame indices, and implementation version.
- Cuts, occlusion, or loss of confidence create explicit gaps or failure states.
- Timeline retiming uses an explicit source-frame mapping. A changed source cannot reuse an old path silently.
- Named model and runtime experiments are necessary for AI trackers. No model support or current GPU use is established.

### Implementation pieces

- `COLOR-07.1` Define tracked paths, gaps, and source bindings.
- `COLOR-07.2` Implement one bounded tracker with loss detection.
- `COLOR-07.3` Map source paths to rational timeline positions.
- `COLOR-07.4` Add correction revisions and independently evaluated advanced methods.

### Verification

`COLOR-07-A` tracks an annotated target in motion.

1. Measure per-frame position error against independent coordinates.
2. Examine decoded mask frames.

`COLOR-07-B` substitutes a different source or introduces occlusion.

1. Read back the path.
2. Make sure that the result shows cache rejection or an explicit gap.

Low tracking error does not approve the grade's appearance.

### Status and dependencies

Planned P4, Rust `color`. Ledger prerequisites are CORE-01 and CORE-02. Practical use must have COLOR-03, native frame access, and timeline mapping. Tracking is unavailable.

## COLOR-08. Noise reduction restoration and grain

### What it does

Restoration reduces declared image defects and keeps useful detail. Grain adds a controlled texture that can repeat under a recorded random seed.

### Scenario

A documentary's dim street shot contains visible noise. The agent produces a conservative spatial-filter comparison for frames 960 through 1079 at 24 fps. A separate grain version uses a saved seed. The creator examines faces and signs for lost detail. The creator then watches the range for flicker before the creator selects a version.

### Inputs and result

Planned command `color.restore` accepts a source-bound range, operator, strength, temporal neighborhood when applicable, and grain seed. A spatial filter uses adjacent pixels. A temporal filter uses adjacent frames. Rust stores parameters and creates version-bound comparison artifacts. Operator formulas, edge policy, precision, and supported models stay open.

### Behavior rules

- Start with one documented spatial filter and seeded grain generator.
- Bound memory and neighborhood size before execution. Keep source bytes and edit timing.
- A temporal operator cannot sample across a cut without a declared policy.
- Record seed, frame mapping, and implementation identity for grain reproduction.
- Advanced restoration and AI models must have defect corpora and temporal experiments. Do not infer recovered detail or proprietary equivalence.

### Implementation pieces

- `COLOR-08.1` Define filter neighborhoods, strengths, and resource bounds.
- `COLOR-08.2` Implement reference-tested spatial filtering and seeded grain.
- `COLOR-08.3` Produce comparison artifacts with unchanged source bindings.
- `COLOR-08.4` Evaluate temporal and model-based operators separately.

### Verification

`COLOR-08-A` uses clean images with independently added noise. Repeated seed and build must reproduce decoded grain samples.

1. Measure noise change and detail error.

`COLOR-08-B` places a cut inside a temporal range.

1. Make sure that the result obeys the declared boundary rule.
2. Examine independent late-frame differences for contamination.

Measurements stay separate from playback and acceptance of texture, faces, or restoration artifacts.

### Status and dependencies

Planned P4, Rust `color`. Ledger prerequisites are CORE-01 and CORE-02. Real restoration must have native image access and COLOR-01. No restoration operator is implemented.

## COLOR-09. Stills galleries and grade matching

### What it does

A gallery keeps reference frames and their grade versions. Grade matching proposes adjustments toward a selected reference. The destination source stays unchanged.

### Scenario

A music-video creator approves the harbor's blue-hour frame at frame 72. The agent saves that still with its source and grade references. For a later street shot at frame 840, the agent proposes a separate match version. Both previews retain their original scenes so the creator can compare color continuity.

### Inputs and result

Planned command `color.match` accepts a reference still, destination source and frame, grade versions, and explicit matching method. Rust owns immutable gallery entries and proposed grade results. A reference still binds decoded pixels, color configuration, source hash, and frame index. Decisions about gallery operations, matching metrics, and result schemas are open.

### Behavior rules

- Start with capture and recall of source-bound stills and exact grade versions.
- Reference deletion must not silently substitute another still or destroy historical bindings.
- A grade match creates a proposal revision. The proposal cannot overwrite an accepted grade implicitly.
- Reject incompatible color declarations or missing source references before a grade match.
- Automatic matching must have an independent corpus. Similar numeric distributions do not establish that lighting, identity, or artistic intent agree.

### Implementation pieces

- `COLOR-09.1` Store immutable still, frame, and grade references.
- `COLOR-09.2` Recall comparison frames from exact historical bindings.
- `COLOR-09.3` Implement one explicit grade proposal method.
- `COLOR-09.4` Evaluate match metrics across varied scene content.

### Verification

`COLOR-09-A` saves and recalls a reference across restart.

1. Compare frame hash, decoded pixels, source identity, and grade version independently.

`COLOR-09-B` attempts a grade match with a missing reference or changed source.

1. Make sure that the failure is explicit.
2. Make sure that the destination grade is unchanged.

A valid proposal and numeric match score do not establish creator approval.

### Status and dependencies

Planned P4, Rust `color`. Ledger prerequisites are CORE-01 and CORE-02. Matching also must have COLOR-01 and COLOR-02. Gallery recall and matching are unavailable.

## PHOTO-01. Still development and RAW processing

### What it does

Still development creates a viewable image from source data and recorded adjustments. RAW processing interprets camera sensor data. It does not treat the samples as completed color pixels.

### Scenario

A creator supplies a camera RAW portrait for square song artwork. The agent checks the source hash. The agent checks the actual format support. For a supported file, the agent creates a development version with declared white balance and exposure. The portrait stays uncropped so a later artwork crop can reuse full source resolution.

### Inputs and result

Planned command `photo.develop` accepts source identity, development parameters, color declarations, and output format. Rust owns the developed image and source-bound receipt. White balance compensates for the recorded light's color. Demosaicing reconstructs color pixels from sensor samples. SDK choice, supported cameras, demosaicing methods, metadata policy, and parameter schemas stay unselected.

### Behavior rules

- Start with one supported decoded still path. Do separate format-specific experiments for RAW.
- Keep original source bytes and record every development version.
- Reject unknown camera data or absent required metadata without a JPEG-preview substitution.
- Declare white balance, exposure units, orientation, precision, and color output.
- Native SDK and camera-model support must have real files and independently measured results. The contract does not claim blanket RAW or Blackmagic-identical processing.

### Implementation pieces

- `PHOTO-01.1` Define development versions and source identity checks.
- `PHOTO-01.2` Develop one supported still format with declared color output.
- `PHOTO-01.3` Evaluate a native RAW decoder on named camera corpora.
- `PHOTO-01.4` Add validated RAW controls and metadata receipts.

### Verification

`PHOTO-01-A` develops a documented reference image.

1. Independently decode dimensions, orientation, pixels, and output color metadata.
2. Compare these values against the declared processing reference.

`PHOTO-01-B` supplies an unsupported RAW sample.

1. Make sure that the rejection is explicit.
2. Make sure that no substituted preview artifact exists.

Numeric reference agreement does not approve portrait appearance or fine detail.

### Status and dependencies

Planned P4, Rust `photo`. Ledger prerequisites are CORE-01 and CORE-02. Development also must have native ingest and COLOR-01. The current renderer produces solid PNG frames. This output is not photo development.

## PHOTO-02. Crop reframe and image export

### What it does

A crop selects a source-image rectangle. A reframe positions that selection inside an output size. The relationship to the original pixels stays documented.

### Scenario

A creator wants square artwork and a wide thumbnail from a 4000 by 6000 portrait. The agent selects two crop rectangles at source resolution. The square crop keeps the singer's face clear of the intended title area. The dimensions and color metadata of the exports are declared. The original portrait stays unchanged.

### Inputs and result

Planned command `photo.export` accepts immutable image and grade references, crop coordinates, orientation, output dimensions, resampling method, and format. Resampling calculates output pixels when dimensions change. Rust owns exported bytes and the receipt. Crop coordinate conventions, rounding, supported encoders, and maximum dimensions do not yet have schemas and resource measurements.

### Behavior rules

- Start with an integer source-pixel crop and a proven native export format.
- Apply orientation under a declared coordinate policy before you evaluate the crop.
- Reject empty or out-of-bounds crops unless an explicit padding operator is supported.
- Record dimension changes and color transforms. Do not silently upscale or use an unsupported encoder.
- Keep source identity and grade version. Image export is separate from movie delivery and timeline retiming.

### Implementation pieces

- `PHOTO-02.1` Define crop coordinates, orientation, and dimension validation.
- `PHOTO-02.2` Produce source-resolution crops with independent pixel references.
- `PHOTO-02.3` Add one bounded resampler and native format encoder.
- `PHOTO-02.4` Save export receipts and do a check of the actual stored bytes.

### Verification

`PHOTO-02-A` crops a numbered pixel grid.

1. Independently decode dimensions.
2. Compare corner and interior pixels against the requested rectangle.

`PHOTO-02-B` requests an out-of-bounds crop or unsupported format.

1. Make sure that no completed artifact exists.
2. Make sure that the source hash is unchanged.

Correct dimensions and pixels do not establish creator-approved framing or title placement.

### Status and dependencies

Planned P4, Rust `photo`. The prerequisites are CORE-01, CORE-02, COLOR-01, and MEDIA-01. Native still codecs must have their own proof. No source-image crop exists in P0.

## PHOTO-03. Albums and grade versions

### What it does

Albums organize image references. They do not copy or replace their sources. Grade versions keep different treatments of the same image for later comparison or export.

### Scenario

A commercial shoot produces twelve shoe photographs. The agent creates a campaign album and adds each exact image reference. For the selected hero photo, the agent saves neutral and warm grade versions. When the agent opens the project again, Rust restores the same order and version references. The creator can resume the comparison without guesses about filenames.

### Inputs and result

Planned command `photo.album` accepts an album operation, image identities, ordered membership, grade references, expected revision, and intent. Rust owns immutable album revisions and version references in local storage. An album entry names a source, not whichever file currently occupies a path. Operation variants, labels, membership limits, and grade selection semantics do not yet have definitions.

### Behavior rules

- Start with ordered membership and explicit references to saved grade versions.
- Replay an identical intent without duplicate entries or a second album revision.
- Missing image or grade references fail the entire mutation atomically.
- Removal of album membership does not delete source bytes or historical album revisions.
- Photo albums organize sources. COLOR-09 galleries bind specific graded frame references. Neither includes a hosted share operation or simultaneous collaboration.

### Implementation pieces

- `PHOTO-03.1` Define album membership and grade-reference types.
- `PHOTO-03.2` Commit ordered album revisions with stable-intent replay.
- `PHOTO-03.3` Restore exact membership and versions across restart.
- `PHOTO-03.4` Validate removal and historical-reference retention.

### Verification

`PHOTO-03-A` creates an album, restarts, and replays its intent.

1. Independently examine order, image hashes, grade references, and unchanged revision count.

`PHOTO-03-B` adds a nonexistent grade in a multi-entry mutation.

1. Read back the project.
2. Make sure that no partial membership exists.

Durable organization does not approve any selected image or grade.

### Status and dependencies

Planned P4, Rust `photo`. Ledger prerequisites are CORE-01 and CORE-02. Display and grading must have PHOTO-01 and color processing. The current revisions do not implement album semantics.

## PHOTO-04. Tethered capture

### What it does

Tethered capture receives photographs from an identified connected camera. Each completed capture becomes a source-bound local asset with an explicit acquisition state.

### Scenario

A product photographer connects a camera for a shoe shoot. The agent identifies the supported device before the agent requests one photograph. During transfer, the cable disconnects. The capture stays incomplete until reconciliation proves the exact received file. A connection to another camera cannot complete the first camera's capture request.

### Inputs and result

Planned command `photo.capture` accepts device identity, supported operation, capture intent, destination project, and bounded timeout. Rust owns device interaction, acquisition state, hash calculation of received bytes, and asset registration. Capture states distinguish requested, acknowledged, transfer in progress, completed, failed, and uncertain outcomes. SDK selection, permissions, camera models, remote shutter controls, and recovery schemas stay unknown.

### Behavior rules

- Start with one named device and proven transfer mode. Device discovery does not prove remote shutter support.
- Register a source only after complete-byte verification and format validation.
- Disconnects keep the original intent and explicit uncertainty. Do not trigger a second shutter automatically.
- Reconciliation must distinguish one received image from duplicate or incomplete transfers.
- Unsupported devices fail explicitly. No browser, Resolve, current GPU, or undocumented SDK fallback supplies capture support.

### Implementation pieces

- `PHOTO-04.1` Evaluate one native camera SDK and exact device identity.
- `PHOTO-04.2` Define acquisition states and bounded capture operations.
- `PHOTO-04.3` Register verified transfers as immutable image assets.
- `PHOTO-04.4` Reconcile disconnects and uncertain capture outcomes.

### Verification

`PHOTO-04-A` captures on a named physical camera.

1. Save actual device readback, transfer bytes, file hash, and independently decoded image properties.

`PHOTO-04-B` disconnects during transfer and substitutes another device.

1. Read back the device.
2. Read back the project.
3. Make sure that no completed asset exists.
4. Make sure that no automatic duplicate shutter occurs.

A device simulator cannot prove hardware support. Successful capture does not approve exposure or composition.

### Status and dependencies

Planned P4, Rust `photo`. Ledger prerequisites are CORE-01 and CORE-02. Registration must have MEDIA-01 and a supported still decoder. No camera experiment or callable capture tool exists.
