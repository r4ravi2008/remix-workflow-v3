# Layered picture judgment A01

## Decision

Use Candidate A as the whole-shape base.

Candidate A preserves the `Project` aggregate, immutable plan, fenced export job, and one-call export interface. Its bounded track workers and single ordered compositor fit the proven native ownership model.

Graft these Candidate B ideas into that shape:

- Compute peak active sessions and owned pixels with an interval sweep.
- Treat sparse coverage as the union of visible, canvas-intersecting content.
- Keep rectangle construction, intersection, opacity, and allocation arithmetic checked and typed.
- Keep one-frame backpressure and an explicit admission-policy report.

Do not graft Candidate B's parallel evaluation plan, public execution limits, or native queue handoff. Those choices duplicate existing authority and add an unproved native-lifetime boundary.

## Public interface and compatibility

The public interface must retain the current signatures:

```rust
Project::commit(CommitProject) -> Result<RevisionReceipt>
Project::prepare_export(ExportRequest) -> Result<PreparedExport>
Project::export(ExportRequest) -> Result<ExportResult>
Project::cancel_export(EntityId) -> Result<ExportCancellation>
Project::verify_export(EntityId) -> Result<ExportResult>
```

Candidate A's signature sketch has three incorrect result types. Candidate B invents `execute_plan` and `ExportResult::plan_id()`. Neither exists or should be added.

Candidate B's caller JSON is also invalid. `CommitProject` has `intent`, `base_revision`, `imports`, `canonical_audio`, and `timelines`. It has no top-level `schema`, `project`, singular `timeline`, direct `audio`, or `opaque_background`. `ContentHash` requires exactly 64 lowercase hexadecimal characters. A `sha256:` prefix and abbreviated hashes are rejected.

Add `VideoClip.placement: Option<PicturePlacement>` last, with `default` and `skip_serializing_if`. Keep snapshot schema 1 for this bounded addition. An absent field has the old stored meaning, and old snapshot bytes remain unchanged. Old binaries already reject an unknown `placement` field. Plan schema 4 provides the required execution-version gate.

Snapshot schema 2 would add migration and downgrade rules without a stronger safety property. A later incompatible snapshot invariant can justify that version change.

Layered mode starts when a timeline has multiple nonempty picture tracks or any explicit placement. In layered mode, an absent placement means the full output canvas at opacity 1. Mixed explicit and absent placement is valid. The compiler must normalize every schema 4 `VideoUse` to a concrete rectangle and opacity.

This default avoids forcing callers to rewrite every base clip when adding one overlay. It also keeps the aggregate interface deep. Test that previously unexportable multi-track schema 1 revisions compile only into schema 4 plans under the new renderer.

Keep plan schemas 2 and 3 byte-identical. Keep artifact receipt schema 2 unchanged. The existing receipt `plan_id` already binds the exact schema 4 plan. Extend every plan replay and verification allowlist to schema 4 only with the layered validator present.

Do not persist a second layer trace. `ExportPlan.video` already binds clip, track, span, asset, source ordinals, framing, and order. `source_closure` supplies the measured PTS for each ordinal. Schema 4 only needs normalized placement and opacity added to each `VideoUse`.

## Composition contract

The track vector defines bottom-to-top order. Same-track overlap remains invalid. Cross-track overlap is valid.

Use opaque source pixels only. Selected movie frames must have alpha 255. PNG import keeps its existing opaque-alpha requirement.

Represent each layer as an opaque `LayerRaster`. Its bounds cover only the fitted source-content rectangle intersected with the destination and canvas. A `contain` bar produces no raster pixels, so lower layers remain visible. This contract needs no alpha-bearing input or premultiplication rule.

Sample relative to the complete destination rectangle before canvas clipping. Signed offscreen placement must not rescale the image. Blend covered BGRA channels bottom to top with one specified fixed-point rounding rule. Output alpha remains 255.

Start each output frame with opaque black. Sparse overlay gaps are valid when another visible layer contributes at that time. A zero-opacity layer does not contribute. An empty canvas intersection does not contribute. A destination that intersects only a `contain` bar also does not contribute.

Preflight must derive temporal coverage from the fitted content geometry, not only clip spans. The visible union must cover every output frame for this unit.

## Native ownership and shutdown

Use at most four nonempty track workers and one ordered compositor. Each worker advances sequential clips and holds at most one active reader or one decoded PNG hold.

Retain the current `media::with_track_cancellable` ownership shape. AVFoundation objects and the native operation remain inside the native completion callback scope. The waiting Rust worker does not necessarily own those objects on its thread.

Only owned Rust pixels and scalar observations may cross channels. No `Retained` native object, raw pointer, `CMSampleBuffer`, or `CVPixelBuffer` may cross a Rust channel.

Candidate B's serial-queue retained-track handoff is a blocking experiment, not a suitable base. It introduces unproved `Send`, thread-affinity, callback-generation, and close-order behavior.

Use capacity-one request and response channels. Make each wait and send cancellation-aware with short `try_send` or timeout loops plus `ExportControl::check`.

The current blocking sender is not a proven deadlock because the receiver drops before join. Parallel teardown still needs the stronger cancellation loop.

Define one shutdown order:

1. Preserve the owned epoch's cancellation, lease-loss, fence-loss, or writer-error classification.
2. Stop new requests and close the layer channels.
3. Cancel every active reader and writer through their guards.
4. Join all Rust workers and the compositor.
5. Run ownership-checked stage cleanup or retained-stage recovery.

Test worker failure, compositor failure, writer backpressure, delayed callbacks, requested cancellation, lease loss, fence loss, and same-intent recovery. A local stop signal must not replace the export job's authoritative terminal cause.

Concurrent independent `AVAssetReader` instances still require a bounded target-macOS experiment. A stalled framework call remains cooperatively cancellable through the existing deadline. Do not claim stronger interruption.

## Admission and module depth

Run admission before opening any source. Use checked arithmetic and Candidate B's interval sweep over the actual allocation schedule.

The estimate must include active copied sources, fitted layer rasters, held PNGs, queued responses, compositor canvas and scratch, output handoff, compressed PNG bytes, expanded PNG storage, and the configured decoder allowance. Count a cache beyond its clip interval if the executor actually retains it.

Runtime permits must enforce the application-owned BGRA cap. Record the estimate and permit high-water mark in bounded experiment evidence. Describe 512 MiB only as an admission policy. It is not total process or native memory.

State the exclusions: allocator capacity, PNG internals, Core Video, AVFoundation, and encoder allocations. Maximum-bound throughput and native peak memory are outside this unit.

Candidate A has the deeper interface because callers submit one commit and one export request. Readers, channels, permits, and composition remain private. Candidate B's `execute_plan`, `LayerCompileLimits`, and `NativeCapabilitySnapshot` expose temporal stages and executor policy.

Do not add `LayeredEvaluationPlan`, `LayeredPicturePlan`, `PictureUse`, `IdentityAudioPlan`, or a layered receipt object. They repeat `ExportPlan`, `VideoUse`, `AudioUse`, profile, and receipt facts. Private checked helper types are appropriate inside the existing plan and movie modules.

## Required proof before this unit closes

Pure pixel tests must prove bottom-to-top order, opacity 0/mid/full, and the exact rounding rule. They must cover signed clipping, a 50-pixel move without rescaling, transparent `contain` bars, and common destination windows. They must also reject non-opaque inputs, incomplete visible coverage, and false coverage from bars or zero opacity.

Golden serialization tests must preserve historical schema 1 snapshots, schema 2 movie plans, schema 3 image plans, and schema 2 receipts byte-for-byte. Replay the preserved historical plans and receipts.

The bounded native fixture should use two simultaneous H.264 movie readers, sparse PNG or anchor layers, signed 50-pixel placement, nontrivial opacity, and synthetic stereo audio. Follow it with a separate canonical 48 kHz stereo audio regression. H.264 is the proven movie path. AV1 needs complete indexing evidence. VP9 remains an explicit negative capability.

Run `project.export` and `project.verify-export`. The latter is fresh readback through the same product library, so it is not independent verification.

A separate-code observer must inspect the whole output. It must check every frame, exact output PTS, source ordinal and PTS selection, geometry, opacity, visible coverage, output EOF, and the complete audio interval. Bind the observer, source, plan, renderer, and output hashes.

Use exact bytes for the pure compositor stage. H.264 output is lossy, so native comparison needs declared full-frame and region PSNR thresholds. Do not convert those checks into playback, hearing, or creative acceptance.

The bounded unit can close on its technical proof. Maximum-bound throughput, the full hybrid film, normal-speed watching, listening, and creative approval remain separate work.

## Rejected choices

- Mandatory placement on every layered clip.
- Snapshot schema 2 for this optional placement addition.
- Reusing the legacy opaque-black `framing::apply` result as an overlay.
- Sending retained AVFoundation objects to per-clip serial queues.
- Public decode, blend, execute-plan, or writer coordination stages.
- A parallel layer plan or receipt trace that repeats plan-owned facts.
- Multiple writer picture inputs presented as composition.
- Alpha-bearing sources, masks, motion, color, text, audio mixing, or PNG output in this unit.
- Silent proxy or codec substitution under the original asset identity.
- Total-memory or maximum-throughput claims from the admission estimate.

This judgment is a static design and code-interface review. It does not add runtime proof or creative acceptance.
