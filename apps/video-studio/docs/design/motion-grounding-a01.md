# Native picture motion grounding A01

Status: source grounding only. The A13/A08 static layer unit is the current base.
This note does not choose a motion API and does not change runtime or native state.

## Overview

The public caller still submits one `CommitProject` and one `ExportRequest`.
`Project::commit`, `prepare_export`, `export`, `cancel_export`, and `verify_export` remain the aggregate boundary.
Motion must become immutable plan data before native execution. The writer must still receive one flattened BGRA canvas per frame.

The current static path is:

```text
CLI JSON
 -> Project::commit
 -> schema-1 Snapshot and CAS blobs
 -> Project::prepare_export
 -> plan::compile -> immutable ExportPlan
 -> movie::verify_inputs -> decode evidence
 -> movie::write -> layers::decode -> EvaluatedFrame
 -> encode_frames -> staged movie -> receipt -> fresh reopen
```

`crates/cli/src/main.rs:9-108` deserializes typed requests and serializes typed results inside an outer `schema:1` envelope.
`crates/editor/src/project.rs:393-509` validates and hashes the snapshot before appending the revision.
`project.rs:241-277` compiles, probes, hashes, source-checks, and persists the export plan.

## Current public data and static normalization

`model.rs:364-376` defines `VideoClip` with `timeline_frames`, `asset`, `source_samples`, `cadence`, optional `framing`, and optional static `placement`.
`VideoTrack.clips` order is stored in `Timeline.video_tracks`; the compositor treats nonempty track order as bottom-to-top.
`Snapshot::validate` at `model.rs:433-640` checks schema 1, IDs, timeline bounds, same-track overlap, source ranges, framing, and placement.
`PicturePlacement` at `composition.rs:70-86` contains a signed `PixelRect` and finite `Opacity` in `[0,1]`.

`plan::compile` at `plan.rs:94-365` decides layered mode when multiple nonempty picture tracks or any explicit placement exist.
Layered mode normalizes absent placement to the full canvas at opacity one.
`VideoUse` at `plan.rs:28-41` then stores `clip`, `track`, `timeline_frames`, `asset`, `allowed_source_samples`, `presentation_ordinals`, `framing`, and optional normalized `placement`.
No current `VideoClip`, `VideoUse`, or `ExportPlan` field represents a curve or a per-frame pose.

`plan::validate_picture_mapping` at `plan.rs:376-565` reconstructs a schema-1 snapshot, checks one-to-one plan mapping, and validates every ordinal.
For movies, it checks `source_closure[asset].descriptor.samples[ordinal].pts` against the cadence-derived source clock.
The source execution check is in `layers::check_decision` at `layers.rs:344-388`; it reads that same `source_closure` sample table.
There is no `plan.timeline.samples` field. Source PTS validation must continue to use `source_closure[asset].descriptor.samples`.

## Static mapping and frame execution

`Mapping::new` at `composition.rs:117-204` computes crop, fit scale, signed destination origin, half-pixel bounds, and source clamps once from one `PicturePlacement`.
`Mapping::rasterize` at `composition.rs:206-253` reuses that mapping for every frame of the use and returns an owned opaque `Raster`.
Its bounds are empty when the static destination has no canvas intersection or its quantized opacity is zero.
`Opacity::weight` at `composition.rs:41-56` rounds to `[0,65536]`; `blend` at `composition.rs:329-364` uses fixed-point nearest rounding and keeps output alpha 255.

`layers::run_track` at `layers.rs:169-342` constructs one `Mapping` per `VideoUse`.
Movie readers walk `VideoUse.presentation_ordinals` in order, compare each observed PTS with `source_closure` samples, copy BGRA into Rust-owned `Pixels`, rasterize, and send a `Decision`.
PNG holds keep one owned image while the clip runs. The movie native objects stay in `media::with_track_cancellable`'s completion callback.

`layers::decode` at `layers.rs:390-528` creates up to four track workers and one ordered compositor.
`check_decision` validates frame, clip, asset, ordinal, and PTS, but `LayerFrame` has no placement or opacity observation.
The compositor therefore reads static `use_.placement.opacity` at `layers.rs:493-503` and sends an owned `EvaluatedFrame`.
`movie::write` at `movie.rs:152-202` uses the schema-4 layer path; `encode_frames` remains unaware of layer count.

For motion, source selection and `presentation_ordinals` must remain independent from pose evaluation.
The missing boundary is a deterministic per-frame resolved placement/opacity value between `VideoUse` validation and `Mapping::new`/`blend`.
The plan must bind every timeline frame, while the channel must carry only owned pixels and scalar observations.

## Clocks, preparation, and output

`plan::compile` selects movie samples by stored `SampleTiming.pts` for `Cadence::SourcePresentationTime`, or repeats an explicit held ordinal.
`layers.rs:280-312` checks native reader PTS against the measured source ordinal before copying pixels.
This source clock is separate from the output clock and must not change when motion changes.

`encode_frames` at `movie.rs:537-581` assigns output PTS as `video_frame * denominator / numerator`.
It writes PCM with independent sample PTS and ends the movie at `timeline_sample_frames / 48000`.
Curve evaluation must never retime source ordinals, audio, or writer timestamps.

`Project::prepare_export` records decode evidence before storing `plan_id = ContentHash::document(plan)`.
`project.rs:279-320` replays an exact stored plan and accepts current plan schemas 2 through 4 after hash validation.
`Project::verify_export` at `exports.rs:549-600` reconstructs the request from the stored plan and reopens the receipt-bound movie.

## Metadata, responses, and compatibility

The relevant request, plan, evidence, and receipt structs use `serde(deny_unknown_fields)`.
The CLI envelope remains schema 1, but `main.rs:72-85` delegates request validation to `ExportRequest` and `CommitProject`.
Motion response validation must bind normalized curve semantics, plan hash, renderer identity, and any per-frame evidence before persistence.
It must reject omitted, extra, non-finite, out-of-domain, or ambiguously ordered motion data.

Static snapshot schema 1 and plan schemas 2, 3, and 4 must retain their current bytes and meaning.
Absent optional fields may preserve old snapshot bytes, but old readers reject newly present fields through `deny_unknown_fields`.
Animation therefore needs an explicit execution-version gate in the plan; the exact schema number and field shape remain undecided.
`exports.rs:671-710` currently accepts only `StoredArtifact` around immutable receipt schema 2, and `receipt.plan_id` binds the complete serialized plan.
A receipt schema change is needed only if motion evidence must live outside the plan; that choice is not made here.
`ExportResult.picture_execution` at `exports.rs:372-381` is optional producer evidence and currently carries no pose or opacity trace.
Any chosen plan field changes `ContentHash::document` and must update replay and verification allowlists in `project.rs:302-307` and `exports.rs:561-570`.

## Ownership, cancellation, and memory

`media::with_track_cancellable` at `media.rs:65-180` captures only `Send` Rust values in its callback block.
`AVAsset`, `AVAssetReader`, `CMSampleBuffer`, and `CVPixelBuffer` stay in callback scope; `Pixels::copy` at `pixels.rs:51-83` copies tight BGRA bytes before channel send.
`ReaderGuard` cancels unfinished readers, and the writer guard cancels unfinished native output.

`layers::send` and `receive` use bounded channels with `Signal::check`; `Workers::Drop` closes ports, marks the local stop flag, and joins every Rust worker.
`ExportControl` at `exports.rs:385-416` preserves cancellation, lease loss, interruption, and fencing causes.
Motion evaluation must check control at frame boundaries and before bounded sends; it must not retain native objects or borrowed pixel locks across a channel.

`pixels::extent` limits each owned BGRA source or canvas to 128 MiB.
`composition::preflight` at `composition.rs:373-491` currently calls `validate_picture_mapping`, builds one static mapping per use, interval-sweeps source plus raster charges, adds PNG temporary allowance, and enforces a 512 MiB logical admission policy.
Motion invalidates the single static raster charge: visible bounds and raster bytes can change every frame.
Preflight must account for the actual bounded per-frame or segmented schedule before opening readers.
The policy excludes allocator capacity, PNG internals, Core Video, AVFoundation, encoder buffers, and total process memory.

## Minimal proof seams

1. Preserve byte-identical legacy snapshots, plans, receipts, and replay behavior.
2. Prove constant evaluated motion matches static placement and produces identical pure BGRA bytes; declared animation still requires its execution-version gate.
3. Prove every active output frame has one resolved pose, one quantized opacity, and one source ordinal.
4. Check source ordinal and PTS through `source_closure`, then check output PTS through the writer clock.
5. Test signed offscreen movement, resizing, zero/mid/full opacity, contain bars, zero-coverage intervals, and cross-track handoffs.
6. Prove preflight coverage from per-frame visible content and prove reservations stay below admitted logical payload.
7. Force reader, worker, compositor, writer, cancellation, lease-loss, and channel-close failures; require cause preservation and joins.
8. Decode the complete output with separate code and compare every frame, source mapping, output PTS, EOF, and unchanged PCM.

## Unresolved invariants

- Keyframe domain: clip-local frame, absolute timeline frame, or rational media time.
- Endpoint rule: whether `Span` end is exclusive and how keyframes at both clip endpoints behave.
- Interpolation: linear versus step, extrapolation, and invalid ordering or duplicate-key handling.
- Rounding order: interpolate then quantize opacity, or quantize key values first; geometry rounding and half-pixel bounds.
- Coverage: whether zero quantized opacity, offscreen poses, and contain bars contribute at each frame.
- Non-integer frame-rate behavior: motion frame index must not alter rational source or writer clocks.
- Deterministic float serialization and overflow checks for signed rectangle interpolation.

The current capability inventory keeps motion planned until these invariants and a real-media bounded proof are complete.

## Source pointers

- `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/model.rs`
- `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/plan.rs`
- `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/composition.rs`
- `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/layers.rs`
- `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/movie.rs`
- `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/project.rs`
- `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/exports.rs`
- `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/cli/src/main.rs`
