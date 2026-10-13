# Editing feature contracts

All twelve families below describe proposed P2 behavior. The editor does not implement these tools. The current P0 Rust model has one solid-color track without overlap and native PNG output. P0 has no movie, audio, text, or layer composition. Current Core checks do not verify these families.

Rust owns the timeline and its local commands. Effect and optional UI applications remain outside the editor. Native commands need no external-service credentials. FFmpeg, libav, hidden renderers, Resolve execution, and current GPU use remain excluded.

The scenarios and named verification cases specify required future results. These cases do not establish completed production or creative reviews. [Timeline layers and composition](../LAYERS.md) supplies the shared layer contract.

## EDIT-01. Track and timeline composition

### What it does

A creator combines timed visual layers and independent audio tracks in one timeline. A layer is a visual track whose pixels appear above lower tracks.

### Scenario

A music video has an environment on V1 for frames `[0, 240)` at 24 fps. The notation includes frame 0 and excludes frame 240. A performer appears on V2 during `[48, 192)`. Telugu lyrics occupy V3 during `[96, 144)`. The agent binds each source hash and source offset. The agent then sets this track order.

Frame 47 shows the environment. Frame 48 adds the performer. Frame 96 adds the lyrics. Frame 144 removes the lyrics. Frame 192 reveals the environment again.

An opaque performer pixel covers the environment. A transparent performer pixel reveals the environment. A later extraction mask restricts the performer layer to the person. The song on A1 continues when the agent hides V2.

An unretimed clip starts at frame 48 with source offset 120. Timeline frame 50 selects source frame 122. This example uses equal source and timeline rates. Different rates require an explicit sampling rule.

### Inputs and result

Planned `timeline.put` accepts a project, expected revision, intent, canvas, rational frame rate, ordered track IDs, and timed clips. Each clip binds its source, source interval, transform, and opacity. Rust stores one immutable revision with the final track order. Track-enable fields, empty-composition background policy, and mixed-rate sampling need final Rust schemas.

### Behavior rules

- Higher active video tracks composite over lower tracks. Database row order never selects the foreground.
- Each clip uses a positive half-open interval. Rust validates source bounds and exact rational time mapping before commit.
- The P2 compositor uses finite normalized RGBA32F in linear RGB with sRGB primaries and premultiplied alpha. Reference inputs declare that space. Unsupported transforms fail. Opacity multiplies source alpha and mask coverage.
- An inactive or disabled visual track contributes no pixels. The editor does not mute an audio track when a visual track is hidden.
- Within-track overlap requires an explicit transition or overlap policy. Unsupported masks, blend modes, or operators fail without a fallback.

### Implementation pieces

- EDIT-01.1. Versioned multi-track snapshot and migration preserve historical hashes and completed intents.
- EDIT-01.2. Clip activation and source mapping return exact active-source positions for a requested frame.
- EDIT-01.3. Ordered normal compositor implements declared alpha and background policies.
- EDIT-01.4. Independent audio routing and visual visibility preserve song continuity.
- EDIT-01.5. Later graph and mask integration identifies each operator's capability and bounds.

### Verification

- EDIT-01-A.

  1. Decode independently rendered boundary frames 47, 48, 95, 96, 143, 144, 191, and 192.
  2. Compare every fixture pixel with its expected stack.
  3. Reorder two opaque tracks.
  4. Assert changed foreground pixels with unchanged source bindings and intervals.

- EDIT-01-B.

  1. Submit undeclared within-track overlap or an unsupported mask.
  2. Assert rejection and an unchanged revision hash.
  3. Hide V2.
  4. Independently compare A1 PCM samples with the visible-track render.

  All audio samples must remain unchanged.

### Status and dependencies

Planned P2, owned by the native Rust `timeline` module. Ledger prerequisites are CORE-01, CORE-02, and MEDIA-01. Actual sound needs AUDIO-01. Masks and graphs need FUSION-01 and FUSION-02 in P3. Current P0 proves neither normal alpha composition nor multi-track playback. See [specification](../SPEC.md) and [phase sequence](../IMPLEMENTATION.md).

## EDIT-02. Insert overwrite replace append

### What it does

A creator places a shot without manual changes to adjacent intervals. Each operation declares whether current material moves, disappears, or keeps its position.

### Scenario

An interview has shot A at `[0, 96)` and shot B at `[96, 192)`, both at 24 fps. The agent inserts a 24-frame reaction at frame 96. B moves to `[120, 216)`.

An overwrite at `[96, 120)` instead preserves the end at 192. The remaining portion of B begins at 120 with its source offset advanced by 24. A replace operation exchanges A's source. The operation preserves `[0, 96)`. An append operation places a new shot at the declared timeline end. Each example starts from the same revision.

### Inputs and result

Planned `timeline.edit` accepts the operation, target tracks, exact placement, source hash and offset, expected revision, and intent. Rust returns a new immutable snapshot plus affected clip IDs and intervals. Replace uses a source start that the agent explicitly selects. Append's treatment of empty space at the end needs a final schema policy.

### Behavior rules

- Insert shifts only the declared ripple scope. This scope contains the tracks selected to move with the insertion.
- Overwrite splits affected clips and preserves their remaining source mapping. It does not shorten the timeline implicitly.
- Replace preserves target duration and rejects a source that cannot supply that duration under the selected mapping.
- Append uses the declared timeline end until the contract specifies another end policy. Linked audio changes require explicit scope.
- All operations validate together. Locked tracks or insufficient source bounds reject the transaction without partial edits.

### Implementation pieces

- EDIT-02.1. Typed operation variants prevent ambiguous placement and duration requests.
- EDIT-02.2. Insert and overwrite reducers produce exact split intervals and source offsets.
- EDIT-02.3. Replace and append preserve their declared duration and end policies.
- EDIT-02.4. Scope validation produces a readable affected-clip result before atomic commit.

### Verification

- EDIT-02-A.

  1. Read each output snapshot independently.
  2. Assert B starts at 120 after insert and retains its original end after overwrite.
  3. Decode numbered-source frames to prove the remaining overwrite portion begins at B's source offset plus 24.

- EDIT-02-B.

  1. Replace a 96-frame target with a 48-frame source and no retime instruction.
  2. Assert rejection and unchanged history.
  3. Repeat a valid intent.
  4. Assert that the original revision returns.

### Status and dependencies

Planned P2 in native Rust. Ledger prerequisites are CORE-01, CORE-02, and EDIT-01. Real source inspection also needs MEDIA-01. The current `project.commit` solid-clip mutation does not provide these operations. Command schemas and acceptance fixtures remain proposed.

## EDIT-03. Ripple roll slip slide trimming

### What it does

A trim changes a shot's boundaries or selected source portion. The operation determines which neighbors move and whether the overall sequence length changes.

### Scenario

A documentary has A at `[0, 96)`, B at `[96, 192)`, and C at `[192, 288)`. The agent makes four alternative edits.

A ripple trim shortens A by 24 frames. The ripple trim moves B and C 24 frames earlier. A roll moves the A/B cut to 120. A extends, and B shortens with its source offset advanced by 24. C stays fixed.

A slip advances B's source offset by 12. B's timeline interval stays unchanged. A slide moves B to `[108, 204)`. B's duration and source portion stay unchanged. A extends to 108, and C begins at 204 with its source offset advanced by 12.

Source handles are unused source frames available beyond a clip's current selection.

### Inputs and result

Planned `timeline.trim` accepts the operation, clip or cut IDs, signed frame delta, link scope, expected revision, and intent. Rust returns exact changed intervals and source offsets in a new immutable revision. Behavior across gaps and locked neighbors needs explicit schema variants.

### Behavior rules

- Ripple changes sequence duration only in the declared scope. Unselected tracks never move silently.
- Roll preserves combined duration of adjacent clips. Rust validates both source-handle requirements before commit.
- Slip preserves timeline start and duration. Slide preserves the middle clip's source selection and duration.
- Zero-duration clips, source overrun, and collisions outside the chosen scope reject the whole edit.
- Initial operators use constant-rate sources. Trims across speed curves need EDIT-09 mapping rules and separate fixtures.

### Implementation pieces

- EDIT-03.1. Cut and neighbor resolution identifies exact affected intervals.
- EDIT-03.2. Ripple and roll operators validate source handles and sequence length.
- EDIT-03.3. Slip and slide operators preserve their distinct source and timeline invariants.
- EDIT-03.4. Linked-track and gap policies reject unspecified propagation.

### Verification

- EDIT-03-A.

  1. Compare all four snapshots with manually calculated intervals.
  2. Independently decode numbered-source boundary frames to distinguish a slipped source from a moved clip.

- EDIT-03-B.

  1. Roll 24 frames into a source with only 12 available handle frames.
  2. Assert failure and unchanged snapshot hash.
  3. Repeat with a locked affected track.
  4. Require the same atomic behavior.

### Status and dependencies

Planned P2, owned by Rust. Ledger prerequisites are CORE-01, CORE-02, and EDIT-01. MEDIA-01 supplies measured source bounds. AUDIO-01 is required for actual linked audio outcomes. Current solid-clip commands provide no trim operators.

## EDIT-04. Split edits and linking

### What it does

Linked clips share explicitly selected timing edits. Their audio and video boundaries remain independent. A split edit lets sound change before or after the picture cut.

### Scenario

An interview switches picture at frame 240, but the next speaker's audio starts at frame 216. This is a J-cut, where incoming sound precedes the incoming picture. The agent links the incoming audio and video through their measured source relationship.

The agent moves that linked group 48 frames later. The picture cut becomes 288, and the incoming audio start becomes 264. The 24-frame lead remains. An L-cut is the reverse arrangement, where outgoing sound continues after the picture changes. The link preserves unequal start times.

### Inputs and result

Planned `timeline.link` accepts stable clip IDs, link-group identity, source-sync relation, operation scope, expected revision, and intent. Rust stores group membership and separate frame and sample intervals. A split edit also needs a typed boundary operation. The ledger command name does not yet define that complete request schema.

### Behavior rules

- A link preserves each member's current boundary and offset. The link does not imply synchronized source recordings.
- Video uses integer frames. Audio uses integer samples with exact rational conversion and a declared rounding policy.
- A group move preserves relative timing. An independent trim requires explicit unlink or member-only scope.
- Visual opacity and visibility do not propagate through a timing link to audio gain or mute.
- Missing members, incompatible source-sync references, or locked affected tracks reject the complete transaction.

### Implementation pieces

- EDIT-04.1. Link-group model stores independent intervals and measured sync references.
- EDIT-04.2. Boundary edits implement J-cuts and L-cuts without forced alignment.
- EDIT-04.3. Group move and unlink operations preserve declared relative timing.
- EDIT-04.4. Frame-to-sample conversion and lock checks reject ambiguous edits.

### Verification

- EDIT-04-A.

  1. At 24 fps and 48 kHz, read the moved picture boundary at frame 288 and audio start at sample 528000.
  2. Decode a test sound impulse to confirm the 24-frame lead.

- EDIT-04-B.

  1. Attempt a group move when one member is locked.
  2. Assert no member moves and no revision commits.
  3. Hide the video member.
  4. Independently compare unchanged audio samples.

### Status and dependencies

Planned P2 in Rust. Ledger prerequisites are CORE-01, CORE-02, EDIT-01, and AUDIO-01. Source synchronization can use MEDIA-05. P0 has no audio intervals, link groups, or split-edit behavior. Listening remains a separate review after sample measurements.

## EDIT-05. Nested and compound timelines

### What it does

A nested timeline appears as one timed clip in a parent timeline. A compound timeline groups several tracks so a creator can move the group together.

### Scenario

A chorus contains environment, performer, and lyrics in child frames `[0, 96)` at 24 fps. The agent places child frames `[24, 72)` into parent frames `[240, 288)`.

Parent frame 240 displays child frame 24. Parent frame 287 displays child frame 71. Parent frame 288 displays no child pixels.

Child track order remains intact inside the nested result. The parent's higher logo track composites above that result. A child edit creates a new child revision. The parent keeps its original child revision until the agent explicitly updates the reference.

### Inputs and result

Planned `timeline.nest` accepts the child timeline ID, immutable revision, child source interval, parent interval, and rate mapping. The command also accepts expected parent revision and intent. Rust stores the nested reference and dependency bindings. Compound creation from selected clips also needs an explicit coordinate conversion and returned child identity. Its schema remains open.

### Behavior rules

- Nested references bind a revision, never an implicit latest child. Render receipts include transitive source bindings.
- Initial nesting at the same rate maps offsets exactly. Mixed-rate nesting requires an explicit sampling policy before support.
- Parent transforms apply to the completed child image. Child audio routes separately under declared parent mixing rules.
- Direct and indirect recursion fail before commit. Dependency depth and frame-evaluation limits require measured bounds.
- Flattening expands child clips into parent coordinates. For supported operators, flattening must preserve output and source mapping.

### Implementation pieces

- EDIT-05.1. Immutable nested references and dependency-cycle validation prevent recursive timelines.
- EDIT-05.2. Parent-to-child time mapping preserves half-open boundaries.
- EDIT-05.3. Compound creation remaps selected tracks and keeps their stack order.
- EDIT-05.4. Render dependency bindings and flatten comparisons prove equivalent output.

### Verification

- EDIT-05-A.

  1. Independently compare every pixel and PCM sample of a nested fixture with its manually flattened equivalent.
  2. Assert parent frames 240 and 287 use child frames 24 and 71.

- EDIT-05-B.

  1. Create a child that references its ancestor.
  2. Assert rejection and unchanged content in both timelines.
  3. Update a child separately.
  4. Assert that the pinned parent output hash remains unchanged.

### Status and dependencies

Planned P2 in native Rust. Ledger prerequisites are CORE-01, CORE-02, and EDIT-01. Actual audio needs AUDIO-01. Child masks and graphs require their P3 owners. P0's single snapshot contains no nested references or compound operation.

## EDIT-06. Transitions and fades

### What it does

A transition combines two shots over a declared interval. A fade changes a clip's contribution to the composition. The clip remains in the timeline.

### Scenario

A commercial changes from a room to a product close-up during frames `[96, 121)`. The agent chooses a linear dissolve with 25 evaluated frames. The incoming weight is 0 at 96, 0.5 at 108, and 1 at 120.

Opaque black and white reference images use a declared linear working space. For these images, frame 108 has linear channel value 0.5. The declared color transform can cause output encoding to produce a different stored channel value. A fade to zero on only the upper product layer reveals the room beneath that layer. This fade does not necessarily fade the entire composition to black.

### Inputs and result

Planned `timeline.transition` accepts clip IDs, interval, operator, endpoint convention, source handles, expected revision, and intent. Rust stores an explicit transition relation or opacity curve in a new revision. Alignment at a cut, default duration, and one-frame endpoint behavior need finalized schemas.

### Behavior rules

- Initial support covers linear dissolve and clip-opacity fade. Each transition owns its within-track overlap explicitly.
- Rust validates required source handles before commit. The editor never invents frames or repeats an endpoint without a declared rule.
- Initial weights use the fixed P2 linear-RGB and premultiplied-alpha policy. Configurable color transforms and HDR working ranges require P4 support.
- A visual dissolve does not add an audio crossfade. Sound gain curves belong to AUDIO-01.
- Wipes and motion-based transitions require separate operators and reference corpora. Unsupported operators fail before render.

### Implementation pieces

- EDIT-06.1. Transition relation validates interval, clip pairs, and source handles.
- EDIT-06.2. Linear weights and endpoint sampling produce deterministic dissolve values.
- EDIT-06.3. Opacity fades reveal lower layers under normal composition.
- EDIT-06.4. Later transition registry declares supported operator parameters and limits.

### Verification

- EDIT-06-A.

  1. Independently decode frames 96, 108, and 120.
  2. Compare channels with analytically calculated values under the declared encoding.
  3. Confirm a transparent endpoint reveals the expected lower image.

- EDIT-06-B.

  1. Request a 25-frame dissolve with insufficient outgoing handles.
  2. Assert rejection and unchanged history.
  3. Assert audio samples remain identical when the command requests only visual transition changes.

### Status and dependencies

Planned P2, owned by Rust. Ledger prerequisites are CORE-01, CORE-02, and EDIT-01. The P3 phase guide defines broader transition rendering. FUSION-02 supplies later advanced composition operators. P0 has no transition evaluation or color-managed blending.

## EDIT-07. Transforms cropping and stabilization

### What it does

Transforms place, resize, and rotate a shot. A crop removes specified source edges. Stabilization estimates unwanted camera movement and applies a compensating transform.

### Scenario

A creator prepares a portrait excerpt from a landscape performer shot. The agent places the performer's measured face point at canvas position `(540, 600)` on a 1080-by-1920 canvas. The agent declares scale and crop edges so the head remains inside the frame.

A later stabilization pass processes a handheld background shot. A test chart moves 8 pixels right only because of camera translation. In this case, the compensating transform moves the chart 8 pixels left. A performer's walk does not automatically indicate camera shake. The analysis needs a declared region and evidence before acceptance of the correction.

### Inputs and result

Planned `timeline.transform` accepts clip identity, translation, scale, rotation, anchor, crop edges, resampling policy, expected revision, and intent. Rust stores parameters and, for stabilization, a source-bound analysis result and correction curve. Coordinate order, border fill, and supported stabilization models need final schemas and experiments.

### Behavior rules

- Initial geometry declares pixel coordinates, anchor, operation order, and sampling. No automatic reframing changes the target.
- Cropped or uncovered pixels use an explicit alpha or fill policy. Source files remain unchanged.
- Geometry operates in clip activation and source mapping. Animation belongs to EDIT-08.
- Stabilization analysis binds the source hash, interval, region, model, and measured correction limits.
- Unsupported motion models fail explicitly. Stabilization cannot promise removal of rolling shutter, blur, or moving-subject distortion without experiments.

### Implementation pieces

- EDIT-07.1. Coordinate and crop types define reproducible geometric evaluation.
- EDIT-07.2. Bounded resampling and border policies handle uncovered pixels.
- EDIT-07.3. Initial translation-analysis experiment measures camera-motion estimates.
- EDIT-07.4. Stabilization curves and crop-budget checks separate analysis from application.

### Verification

- EDIT-07-A.

  1. Transform a grid with known landmarks.
  2. Independently decode output.
  3. Assert landmark coordinates, crop boundaries, and alpha.
  4. Measure reduced translation on the synthetic stabilization chart.

- EDIT-07-B.

  1. Request a correction that exceeds the declared crop budget or uses an unsupported motion model.
  2. Assert explicit failure without revision mutation.
  3. Evaluate a moving-subject corpus separately for false camera-motion estimates.

### Status and dependencies

Planned P2 in native Rust. Ledger prerequisites are CORE-01, CORE-02, and EDIT-01. MEDIA-01 supplies real source measurements. Stabilization requires an experimental corpus before implementation claims. Current P0 has no crop, transform, or stabilization support.

## EDIT-08. Keyframes and interpolation

### What it does

A keyframe specifies a parameter value at an exact time. Interpolation defines the values between keyframes, such as a steady movement or a held value.

### Scenario

A music-video environment graphic moves horizontally while the performer and lyrics stay fixed. The agent sets the graphic's x position to 100 at clip-local frame 0 and 340 at frame 24.

Linear interpolation places the graphic at x 220 on frame 12. Hold interpolation keeps x 100 through frame 23 and changes to 340 at frame 24. A clip move preserves its local motion. A separate opacity curve affects only that graphic layer, not linked sound or the performer's pixels.

### Inputs and result

Planned `timeline.animate` accepts a clip and parameter target, time-coordinate choice, ordered keyframes, interpolation type, expected revision, and intent. Rust stores a typed curve in an immutable revision. Curve control points, extrapolation, and source-time versus timeline-time attachment need explicit schemas.

### Behavior rules

- Initial support uses clip-local integer frames with hold and linear interpolation. Values before and after the keys hold the endpoint.
- Duplicate key times fail until the contract explicitly specifies a replacement operation. Parameters require declared units and valid bounds.
- Curves change only their named target. Track order, source selection, and linked audio stay unchanged.
- Curved interpolation declares control points and overshoot policy. Unsupported expression evaluation has no fallback.
- Trim and retime operations must preserve or explicitly remap the curve's chosen time coordinates.

### Implementation pieces

- EDIT-08.1. Typed parameter targets and curve coordinates prevent unit and timing ambiguity.
- EDIT-08.2. Hold and linear evaluators return deterministic frame samples.
- EDIT-08.3. Edit remapping preserves declared curve attachment through moves and trims.
- EDIT-08.4. Later curve operator specifies control points, limits, and independent references.

### Verification

- EDIT-08-A.

  1. Read parameter samples at frames 0, 12, 23, and 24.
  2. Independently decode a marked graphic.
  3. Compare its pixel position.
  4. Move the clip.
  5. Require identical clip-local samples.

- EDIT-08-B.

  1. Submit duplicate times or opacity outside its allowed range.
  2. Assert atomic rejection.

  Without a declared curve policy, Rust must reject retiming.
  Rust must not silently switch time coordinates.

### Status and dependencies

Planned P2, owned by Rust. Ledger prerequisites are CORE-01, CORE-02, and EDIT-01. EDIT-07 supplies geometric targets. Advanced motion expressions belong to FUSION-04 in P3. P0 has no parameter curves or animated opacity.

## EDIT-09. Retiming and optical flow

### What it does

Retiming changes how timeline time selects source time. Optical flow estimates pixel movement between source frames to synthesize intermediate images.

### Scenario

A creator slows a 24 fps dance shot to half speed. The agent selects source frames `[0, 24)` and declares 48 output frames with nearest-frame sampling.

Output frame 0 uses source frame 0. Output frame 1 also uses source frame 0. Output frame 47 uses source frame 23. The duration becomes two seconds.

A later optical-flow operator can synthesize positions between frames as an alternative to frame duplication. A hand that crosses a face creates occlusion, where one object hides another. That situation requires an explicit quality experiment, not a promise of smooth footage.

### Inputs and result

Planned `timeline.retime` accepts source and output intervals, exact rate or time map, interpolation operator, audio policy, expected revision, and intent. Rust stores the mapping and operator identity. Variable-speed knot schemas, reverse behavior, and audio stretch modes remain unresolved.

### Behavior rules

- Initial constant positive rates use rational mapping and a declared nearest-frame rounding convention.
- Duration and downstream edit scope are explicit. A speed change never stretches linked audio silently.
- Frame duplication and interpolation are separate operators with different evidence requirements.
- Unsupported optical flow fails before render. It cannot silently substitute nearest-frame duplication.
- Freeze, reverse, variable-speed ramps, and audio time stretch need separate bounded behavior in this family and their respective audio operator.

### Implementation pieces

- EDIT-09.1. Constant-rate source mapper and exact output-duration validation support usable retiming.
- EDIT-09.2. Frame-selection operator records duplicate and omitted source frames.
- EDIT-09.3. Variable mapping and curve-attachment rules define later ramps and reverse playback.
- EDIT-09.4. Optical-flow experiment measures known motion and occlusion against reference images.

### Verification

- EDIT-09-A.

  1. Independently decode numbered source frames after half-speed output.
  2. Assert sequence `0, 0, 1, 1` and final source frame 23.
  3. Measure exactly 48 output frames and unchanged separately bound song samples.

- EDIT-09-B.

  1. Request unimplemented optical flow or a map beyond source bounds.
  2. Assert structured rejection and no artifact.

  Later flow tests compare occluded-region errors against a declared reference corpus and threshold.

### Status and dependencies

Planned P2 in native Rust. Ledger prerequisites are CORE-01, CORE-02, and EDIT-01. MEDIA-01 supplies decoding and source bounds. Audio time stretch requires audio research. P0 has no source frame mapping or optical-flow implementation. Playback review remains separate from mapping proof.

## EDIT-10. Subtitles and closed captions

### What it does

Subtitles store timed readable text. Closed captions can also describe sound and speaker identity for viewers who cannot hear the program.

### Scenario

A Telugu interview contains the spoken phrase `ఇది మా ఊరు`. The agent places that exact text at frames `[48, 96)` in a 24 fps timeline. A separate cue `సంగీతం` identifies a music passage.

A timed-text export retains both native-script strings and their exact two-second and four-second boundaries. A later burned-in preview shapes Telugu glyphs. The preview displays the first cue at frame 48 and removes the cue at frame 96. Burned-in text becomes image pixels. A selectable caption track remains separate text in a supported output container.

### Inputs and result

Planned `caption.put` accepts cue IDs, native Unicode text, language, exact intervals, speaker or sound metadata, expected revision, and intent. Rust stores a versioned caption collection. Import formats, export timebase conversion, overlap policy, style fields, and container support require finalized schemas.

### Behavior rules

- Preserve text without transliteration or implicit Unicode normalization. Native script remains authoritative.
- Cue duration is positive. Cues that overlap need an explicit presentation policy. Accidental list order cannot determine presentation.
- Initial storage and round-trip behavior do not claim glyph shaping, burned-in output, or closed-caption container encoding.
- File-format conversion declares rounding at rational rates and reports unrepresentable boundaries.
- A cue edit preserves all other cue text and times. Speech audio stays unchanged when a visual cue is hidden.

### Implementation pieces

- EDIT-10.1. Cue model preserves Unicode, language, metadata, and exact intervals.
- EDIT-10.2. Initial timed-text import and export declare supported formats and rounding.
- EDIT-10.3. Later native-script rendering integrates shaped glyphs and declared caption placement.
- EDIT-10.4. Container-caption experiments measure format and accessibility limitations.

### Verification

- EDIT-10-A.

  1. Independently parse an exported caption fixture.
  2. Compare Unicode scalar sequences and intervals.
  3. Later decode preview frames 47, 48, 95, and 96 to prove exact visible boundaries and shaped reference glyphs.

- EDIT-10-B.

  1. Submit a zero-duration cue or an unsupported presentation of cues that overlap.
  2. Assert rejection and unchanged revision.

  A target format unable to preserve a boundary must report that limit before export.

### Status and dependencies

Planned P2, owned by native Rust. Ledger prerequisites are CORE-01 and CORE-02. Burned-in visuals also need EDIT-01 and FUSION-03 in P3. Container exports need DELIVER-01. P0 preserves general Unicode in names but provides no caption storage or Indic shaping proof.

## EDIT-11. Undo redo and versions

### What it does

A creator restores earlier project content. The history between revisions remains unchanged. Undo and redo identify explicit previous and subsequent edit results.

### Scenario

Revision 7 has the approved chorus timing. Revision 8 trims the chorus, and revision 9 reorders two visual tracks. The creator asks the agent to restore revision 7.

The agent restores against expected revision 9. Rust creates revision 10 with revision 7's edit content. Revisions 8 and 9 remain inspectable. The old rendered artifact still binds revision 7. A new render binds revision 10 even when the restored pixels match. A replay of the restore intent returns revision 10 again.

### Inputs and result

Planned `project.restore` accepts the target revision, current expected revision, intent, and restoration scope. Rust returns a new immutable revision plus restoration provenance. Undo-stack ownership, branch names, redo after other edits, and content-hash treatment need final schema decisions.

### Behavior rules

- Restore copies edit content into a new revision. It never renumbers, mutates, or deletes historical revisions.
- Historical asset hashes remain pinned. Restore does not substitute a newer source or repair missing media silently.
- If another agent changes the current revision, the expected-revision check rejects the stale undo request.
- Identical intent replay returns the original restore result, even after later edits.
- Initial restore targets one known revision. Branch navigation and collaborative undo require separately specified behavior before support.

### Implementation pieces

- EDIT-11.1. Restore transaction copies supported snapshot content and records provenance.
- EDIT-11.2. Readback distinguishes restored content identity from new revision identity.
- EDIT-11.3. Undo and redo navigation declare their scope and intervening-edit policy.
- EDIT-11.4. Source-availability checks report missing historical inputs and preserve their bindings.

### Verification

- EDIT-11-A.

  1. Compare revision 10's edit fields with revision 7.
  2. Read revisions 8 and 9 unchanged.
  3. Independently compare restored fixture pixels.
  4. Require the new receipt to name revision 10.

- EDIT-11-B.

  1. Restore with a stale expected revision or nonexistent target.
  2. Assert rejection and preserved history.
  3. Replay a completed restore after another edit.
  4. Require the original revision and result.

### Status and dependencies

Planned P2 in Rust. Ledger prerequisites are CORE-01 and CORE-02. Current Core stores immutable revisions but does not implement `project.restore`, undo, or redo. Promotion requires restore-specific cases, not general history-readback tests.

## EDIT-12. Markers flags and timeline metadata

### What it does

Markers attach notes to an exact timeline position or interval. Flags attach labels to identified clips or assets so a creator can find review tasks.

### Scenario

A director marks the chorus start at frame 960. The director adds a 48-frame note that requests a background-reactivity review. The note targets the environment clip, not the performer or Telugu lyrics. The agent adds a yellow flag to that clip and records a source reference.

A timeline-anchored marker remains at frame 960 when the clip moves. A clip-anchored marker moves with the clip through its stored local offset. The attachment must be explicit. Markers appear in inspection results or a future UI. They do not add pixels to the exported film unless a separate burn-in operation requests it.

### Inputs and result

Planned `timeline.mark` accepts marker or flag IDs, anchor type, position or interval, text, color, target references, expected revision, and intent. Rust stores metadata in the immutable project snapshot. Color representation, custom-field limits, and behavior when a referenced clip is removed need final schemas.

### Behavior rules

- Timeline and clip-local anchors are distinct types. Source-time markers require an explicit later mapping rule.
- Rust validates positive intervals and valid references before commit. Metadata text preserves native Unicode.
- Flags never authorize content changes or establish human approval. Review status remains an explicit separate record.
- Marker edits leave clip timing, source bindings, sound, and pixels unchanged.
- Initial behavior supports bounded local metadata. External comments, notifications, and shared review belong to separate collaboration capabilities.

### Implementation pieces

- EDIT-12.1. Marker and flag types encode anchor, duration, color, and bounded text.
- EDIT-12.2. Move and removal rules preserve or reject references explicitly.
- EDIT-12.3. Metadata inspection and round-trip export preserve stable identities.
- EDIT-12.4. Render exclusion checks keep metadata separate from burn-in output.

### Verification

- EDIT-12-A.

  1. Round-trip names, Telugu notes, colors, frame positions, and references through restart.
  2. Move a clip.
  3. Assert that only its clip-anchored marker moves.
  4. Independently compare output pixels and PCM samples before and after metadata changes.

- EDIT-12-B.

  1. Submit a marker outside the timeline or a nonexistent target reference.
  2. Assert atomic rejection.

  Removal of a referenced clip must obey the declared removal policy.
  Rust must not silently change the note target.

### Status and dependencies

Planned P2, owned by native Rust. Ledger prerequisites are CORE-01 and CORE-02. Clip anchors also depend on EDIT-01's stable identities. P0 has no marker or flag commands. This local metadata contract needs no external service or Effect credentials.
