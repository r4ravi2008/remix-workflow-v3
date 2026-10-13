# Picture motion design judgment A01

Status: design judgment only. No runtime, project state, media, GPU, or Resolve state changed.

## Decision

Use Candidate A's independent typed property curves as the whole-shape base.
Graft Candidate B's final-hold semantics, permissive constant programs, mixed-plan invariant, and stronger native proof fixture.

Candidate A better supports a general editor.
A caller can change opacity without restating geometry, or change one axis without rebuilding an entire pose.
The compiler still resolves every property into a complete immutable execution program.

Candidate A read Candidate B before drafting.
The candidates therefore do not provide blind independent convergence.
No cross-family reviewer was available.
This judgment is a source-grounded synthesis, not a blind or cross-family result.

## Required authoring contract

Keep Candidate A's optional `VideoClip.motion: Option<PictureMotion>` and five typed curves.
Do not store complete poses as the primary authoring shape.

The implementation must enforce these rules:

1. `PictureMotion` contains at least one property curve.
2. Each present curve contains at least one key and no more than the existing frame bound.
3. The first key is local frame zero.
4. Key frames are strictly increasing and less than clip length `L`.
5. Every nonfinal key has `to_next`; the final key omits it.
6. The final key holds through local frame `L - 1`.
7. One key holds for the complete clip.
8. A one-frame clip accepts one key at frame zero.
9. Constant curves and programs with no visible delta are valid.
10. A nonempty declared motion selects plan schema 5, even when its normalized curves are constant.

These rules reject Candidate A's required last key at `L - 1` and its two-key minimum.
They also reject Candidate A's requirement for visible animation.
Those restrictions remove valid editor states without strengthening execution.

A missing property inherits the authored static `PicturePlacement`.
An absent placement first normalizes to full-canvas geometry and opacity one.
Compilation resolves all five properties, so execution never applies partial defaults.

`Step` returns the left value on `[left.frame, right.frame)`.
The right key is exact at `right.frame`.
`Linear` uses one signed `i128` rational computation and one nearest-ties-away-from-zero rounding step.
Every stored key endpoint must evaluate exactly.
Widths and heights remain positive and bounded.
Signed `x` and `y` retain their current off-canvas meaning.

Author opacity can retain the existing finite `Opacity` value in `[0,1]`.
Compilation quantizes every opacity key once as `round(value * 65536)`.
Execution interpolates only Q16 integers.

`OpacityQ16` must serialize as one JSON integer in `0..=65536`.
Its deserializer must enforce that range directly.
`#[serde(transparent)]` alone does not enforce the range.
Use `try_from = "u32"`, or an equivalent custom deserializer.
A stored value such as `32768` must never pass through the decimal authoring constructor.

## Why complete poses are rejected

Candidate B's complete poses make unrelated edits affect movement curves.
This coupling is material because geometry uses integer rounding.

For example, `x: 0@0 -> 2@3` evaluates as `[0, 1, 1, 2]`.
Adding an opacity-only pose at frame 1 requires copying `x = 1` into that pose.
The second segment then evaluates as `[1, 2, 2]`, changing frame 2 from `1` to `2`.

Complete poses also repeat rectangles for ordinary fades.
That repetition increases authoring dependencies as more picture properties arrive.
Candidate A's compiler removes B's stated partial-default risk by normalizing all five planned curves.

Do not add `PoseProgram::fade_from_static` to the core aggregate.
CLI or Effect adapters may provide authoring helpers outside the stored domain model.

## Immutable plan and compatibility

Snapshot schema remains 1.
The optional `motion` field must default to absent and omit itself when absent.
Existing snapshot bytes must remain exact.

Plan schema 5 stores `PlannedPictureMotion` with complete typed curves.
It may use `Constant` and `Keyed` variants.
It must not expand curves into a per-frame pose table.

A schema-5 animated `VideoUse` has `motion: Some` and `placement: None`.
A static `VideoUse` in the same plan has normalized `placement: Some` and `motion: None`.
The validator must reject both-present and both-absent cases for schema 5.
Schemas 2 and 3 retain neither field; schema 4 retains placement only.

`ExportPlan.timeline` remains the authoring record.
`VideoUse.motion` is the normalized execution form, consistent with existing normalized uses.
It is not a second source or frame trace.

`plan::validate_picture_mapping` must recompile motion from the snapshot and compare exact planned curves.
It must retain the existing one-to-one ordered clip mapping.
It must also retain range, ordinal, cadence, source-PTS, framing, and lineage checks.

Motion must never change `presentation_ordinals`.
Movie source PTS authority remains `source_closure[asset].descriptor.samples[ordinal].pts`.
PNG sources remain held ordinal zero without a movie PTS.
Output video PTS remains the writer's `n / frame_rate` clock.
Audio keeps its independent 48 kHz sample clock and exact selected interval.

Plans 2, 3, and 4 must preserve exact bytes and execution paths.
Artifact receipt schema remains 2.
Its existing `plan_id` binds the schema-5 program.
Do not add per-frame motion evidence to the receipt or `PictureExecutionEvidence`.
Extend only the private plan allowlists and validators through schema 5.

Every current `schema == 4` layered-path gate needs an explicit `4 | 5` equivalent.
This includes pixel preflight, profile validation, decoder selection, and composed-channel capacity in `movie.rs`.
It also includes plan reconstruction and replay allowlists in `plan.rs`, `project.rs`, and `exports.rs`.
Schema 5 must never fall through to the single-track cuts decoder.

## Interface and ownership

Keep the existing aggregate boundary:

- `Project::commit`
- `Project::prepare_export`
- `Project::export`
- `Project::cancel_export`
- `Project::verify_export`

Candidate B's repaired example now uses complete 64-character hashes and the current method signatures.
Its sequential `export` then `cancel_export` call does not exercise active cancellation.
The cancellation proof must request cancellation while an export owns its epoch.

Add a private `motion.rs` for validation, normalization, Q16 conversion, rounding, and evaluation.
Keep resolved placement private and ephemeral.
Do not expose an executor, reader, worker, compositor, callback, or writer to callers.

`layers.rs` should evaluate the plan after each frame request.
Each response may carry its owned raster and resolved scalar placement.
`check_decision` must recompute that placement before blending.
This comparison catches a correct source frame paired with the wrong motion frame.

Retain A13's worker and callback ownership.
No native object or borrowed native buffer may cross a product channel.
AVFoundation reader, output, sample, and pixel-buffer use stays inside the native completion operation.
Only copied Rust pixels and scalar observations cross channels.

Reject Candidate B's private codec-registry addition in this unit.
Motion does not change the already measured source representation or codec capability boundary.

## Coverage and admission

Preflight must evaluate visible source content at every active output frame.
Coverage uses the fitted source-content rectangle intersected with destination and canvas.
Contain bars are absent raster regions, so lower layers remain visible.
Zero-Q16 opacity, fully offscreen placement, and empty source-content intersection contribute no coverage.

Retain the current global conservative maximum PNG temporary allowance for this first unit.
This is simpler and safer than making admission depend on a narrower start-frame timing proof.

Candidate A's start-frame PNG charge is not a confirmed scheduling defect.
The current executor receives the frame request before selecting or decoding a new clip.
It drops the last PNG cache before the final response.
Movie source pixels and their permit drop before response send.

The compositor consumes every raster before sending the composed canvas.
It cannot request the next frame until that output send completes.
Capacity-one request and response channels prevent a worker from retaining a second-frame raster.
The existing three-canvas allowance covers composed-frame backpressure.

Any later narrower PNG estimate must preserve these barriers and test them explicitly.
The per-frame peak must include all active PNG caches, movie source copies, response rasters, and three canvases.
Add the serialized PNG temporary maximum to that peak.
Runtime permits must reserve the same payload classes.

This accounting remains a logical application-owned estimate.
It does not prove allocator, framework, encoder, or total process peak memory.

## Required implementation and proof sequence

The following requirements block acceptance of the motion unit:

1. Implement the pure curve model and evaluator before changing native workers.
2. Share golden vectors with an independent implementation before native rendering.
3. Cover positive and negative half ties, Q16 endpoints, steps, final holds, constant programs, and one-frame clips.
4. Include the complete-pose rounding counterexample above as a regression vector.
5. Add malformed schema-5 tests for placement exclusivity, curve ordering, Q16 range, ordinals, source PTS, and normalized-plan mismatch.
6. Prove preflight admission against live reservations across gaps, clip boundaries, response backpressure, and composed-frame backpressure.
7. Preserve exact legacy snapshot, plan 2/3/4, receipt-2, and historical 206-frame artifact hashes.
8. Force cancellation during preflight, PNG decode wait, movie reads, raster work, channel waits, and writer readiness.

The actual native fixture must use two simultaneous movie readers plus an opaque PNG.
It must exercise movement, resizing, fading, signed placement, sparse coverage, contain bars, and overlapping layers.
Use at least 48 output frames.

The product proof must bind every source asset and measurement.
It must check every selected ordinal and source PTS against `source_closure`.
It must check every output PTS, reader EOF, track order, and resolved placement.

Pure pre-encode BGRA must match the independent evaluator exactly.
Separate code must compare every decoded output frame and relevant overlap region.
Declare the lossy threshold before rendering; Candidate A's 34 dB minimum is acceptable.

The first audio proof must use the synthetic offset interval and verify exact PCM length, PTS continuity, EOF, and zero-lag comparison.
A separate regression must use the canonical 24-bit stereo 48 kHz master and exact selected interval.
Neither proof changes source selection, gain, pan, or the master binding.

No new codec experiment is required before implementation.
Acceptance still requires the native fixture, independent pixel reference, legacy readback, and cancellation evidence.
These checks establish bounded technical behavior only.
They do not establish playback, hearing, creative quality, maximum throughput, total native memory, or the full film.

## Rejected choices

- Reject Candidate B's complete-pose storage because it couples unrelated property edits.
- Reject Candidate A's two-key, final-at-`L - 1`, and visible-change requirements.
- Reject a dense per-frame pose table because it duplicates execution state and inflates plans.
- Reject floating-point runtime interpolation because it weakens reproducibility.
- Reject a new receipt schema or persisted per-frame trace because `plan_id` already binds motion.
- Reject native-object channel handoff, a public executor, and caller-coordinated temporal stages.
- Reject codec-registry work, audio envelopes, masks, rotation, alpha inputs, and color changes from this bounded unit.

Candidate A with these grafts has the strongest whole shape.
It preserves a deep aggregate, exact clocks, legacy identities, and the current native ownership model.
