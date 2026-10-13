# Architecture judgment

## Decision

Use Candidate A as the base.

Candidate A has the stronger invariant owner, native timing model, artifact binding, and interrupted-export recovery model.
Candidate B contributes several useful records, but its typed sketch does not support its strongest prose claims.

Candidate A is not ready for implementation unchanged.
The required grafts and corrections below are part of this recommendation.

This judgment reviewed every file in both candidate directories, `WORK.md`, `design/task.md`, and the current native media receipts.
Cross-family model review was unavailable and is not claimed.

## Scorecard

Scores use a five-point scale.
A score of five means the design is specific, internally consistent, and supported by current evidence.

| Criterion | Candidate A | Candidate B | Judgment |
| --- | ---: | ---: | --- |
| 1. Native movie/audio feasibility and source timestamp authority | 4.0 | 2.0 | A uses presentation-sample ordinals and native ticks. B still models source selection mainly as frame spans. |
| 2. Immutable asset, revision, time-map, and lineage invariants | 4.0 | 3.0 | A has the stronger aggregate and representation map. B has richer origin variants and a canonical audio binding. |
| 3. Interface depth and few caller coordination steps | 4.5 | 3.5 | A completes commit and export as whole operations. B exposes an optional plan well, but its gates add caller coordination. |
| 4. Truthful version-bound review and exact-file acceptance | 4.5 | 3.0 | A binds evidence to revision, project hash, artifact hash, and renderer. B's types omit several bindings promised by its prose. |
| 5. Interrupted job, retry, recovery, and tenant separation | 4.0 | 2.5 | A specifies stable intents, fenced leases, and promotion checks. Neither candidate types tenant ownership strongly enough. |
| 6. General editor extensibility without a PNG-only foundation | 4.5 | 2.5 | A has a coherent typed movie, audio, timeline, text, color, and mask model. B's stored graph is incomplete and partly string-typed. |
| **Total** | **25.5 / 30** | **16.5 / 30** | **Choose A, then graft the listed parts from B.** |

## 1. Native movie and audio feasibility

### Current measured evidence

- AVFoundation decoded 24 BGRA samples from the real AV1 source.
- Those samples have PTS increments of `512/12288`, or exactly `1/24` second.
- The AV1 track reports a nominal rate of 12 fps.
- AVFoundation reports 189.75 seconds for that asset.
- The current box parser reports 94.875 seconds and no ordinary sample table.
- The current evidence therefore does not establish the complete source sample count.
- The VP9 source fails with `AVFoundationErrorDomain -11833 Cannot Decode`.
- The H.264 source decoded through the same Rust-owned native path.
- Native writing appended 24 H.264 frames and 48,000 source PCM frames.
- The saved MP4 contains 24 video samples at `25/600` ticks each.
- The saved MP4 contains 49 AAC packets at 1,024 ticks each.
- Its audio track therefore contains 50,176 encoded ticks for 48,000 submitted PCM frames.
- Independent native reopening, decoding, A/V alignment, and trim verification remain pending.
- The output remains `encoded-unreviewed`, with `watched=false` and `heard=false`.

These receipts prove a promising native path.
They do not yet prove the proposed round trip or a source-bound editor export.

### Why Candidate A wins

Candidate A makes presentation-sample ordinals and native media ticks the source authority.
It treats nominal frame rate and asset duration as descriptors and mismatch warnings.
It also separates an unsupported authority asset from a verified native representation.

Candidate A models timeline samples, encoded samples, and encoder trim separately.
That distinction is required by the observed 48,000-to-50,176 AAC expansion.

Candidate B defines `VideoDescriptor.duration` as `FrameSpan`.
Its `FrameMapSegment.source` is also a `FrameSpan`.
Those types can accidentally turn nominal-rate frame numbers into source authority.
`MediaTimestamp` exists only on decoded output frames and does not identify stored source selections.

Candidate B's capability prose is careful.
Its type system does not carry the source PTS index needed by the real AV1 discrepancy.

### Blocking timing corrections

Candidate A must not equate 48 source samples with 48 output frames by count alone.
The compiler must prove the selected source PTS coverage and explicit cadence map.

The source index must record presentation ordinal, PTS, DTS, duration, and sync status.
The index must enumerate the complete native reader result before full-film use.

Historical `source_frames` cannot enter a new revision directly.
Each historical label needs a receipt mapping it to an authority sample, PTS, or known proxy frame.

The VP9 authority must fail until a verified representation exists.
Any representation needs its own hash, codec receipt, and exact authority-to-representation sample map.

## 2. Immutable assets, revisions, time maps, and lineage

Candidate A has the better invariant owner.
Its revision snapshot, content-addressed assets, source bindings, and optimistic commits form one atomic boundary.
Its authority-versus-representation split is especially important for VP9.

Candidate A still has a material typed-model gap.
`AssetImport.origin` does not have a complete stored counterpart in `MediaAsset`.
`LineageGraph::Derivation` also loses generated attempt, model, and provider receipt fields.
The prose promises more lineage than the stored types preserve.

Candidate B's `Lineage` variants preserve imported, extracted, transformed, generated, and native-representation roles.
Its generated variant retains attempt, workflow, model, inputs, and output bytes.
Those fields should be grafted into A's stored asset record.

Candidate B's representation lineage lacks A's exact sample mapping.
The final design needs both structures.

Each stored asset must preserve:

- Exact byte hash and byte count.
- Measured stream descriptors and probe receipt.
- Declared role without inventing source originality.
- Exact parent assets and source ranges.
- Transformation, workflow, model, attempt, and provider receipts when applicable.
- Accepted usable ranges through exact review evidence.
- An explicit supersession relation that never mutates the superseded bytes.

## 3. Interface depth

Candidate A exposes whole project operations.
`commit` hides staging, hashing, probing, alias resolution, validation, and revision creation.
`export` hides compilation, decode, composition, mixing, encoding, recovery, verification, and promotion.

That is the deepest public interface of the two candidates.
The Effect adapter also remains a policy boundary instead of becoming another editor.

Candidate B's `evaluate(request)` is a useful convenience.
Its public `compile` and `execute` split is valuable for inspection and reproducibility.
That split should remain optional for callers.

The final A-based interface should add an inspectable immutable plan without requiring stage coordination:

```text
Project::prepare_export(request) -> PreparedExportPlan
Project::execute_plan(plan_id, intent_id) -> ExportOutcome
Project::export(request) -> compile, persist, execute, and reconcile in one call
```

The plan must be content-addressed and revision-bound.
It must include the normalized graphs, source closure, cadence maps, audio binding, profile, backend requirements, and policy inputs.

## 4. Truthful review and exact-file acceptance

Candidate A has the stronger review binding.
It binds revision, project hash, artifact ID, artifact hash, and renderer build.
It also keeps measurement, frame inspection, playback, listening, and creative judgment as separate variants.

Candidate B states the same policy in prose.
Its `ReviewRecord` only stores optional artifact and plan identifiers.
It does not type the artifact hash, renderer build, policy version, playback speed, continuity, or capture metadata.

Candidate B also creates a pilot-gate contradiction.
Its prose requires the pilot certificate to cover the exact revision.
Its acceptance flow then creates a different full-film revision.
The certificate cannot bind both revisions without an explicit compatibility rule.

Reject any rule that lets pilot evidence accept the final artifact.
Pilot evidence may authorize production work under a versioned policy.
The final artifact still needs its own exact-file playback, listening, and creative review.

Candidate A's optional export policy must remain technical or pre-production only.
Creative acceptance cannot exist before the exported bytes exist.

## 5. Recovery, retries, and tenant separation

Candidate A defines stable intent replay, request hashing, fenced leases, staging ownership, and final promotion checks.
A stale worker cannot promote after another worker takes ownership.
An interrupted first version may safely recompute from frame zero.

Candidate B names useful recovery states, including `PromotedUnreceipted`.
That state should be grafted into A's export journal.
It covers a crash after atomic promotion but before receipt persistence.

Candidate B's `execute(plan_id)` does not accept a stable intent.
Its store later reconciles by plan and intent.
That public and internal contract is inconsistent.

Both candidates keep tenant orchestration outside the native editor.
That boundary is correct.
Neither typed sketch proves tenant separation for application records.

The Effect adapter must key every project mapping, job, attempt, review, budget, delivery, and worker claim by `TenantId`.
The native project ID cannot authorize access.
Worker paths and CLI requests must come from an authorized tenant-to-native-project mapping.

Provider retries need a durable logical intent and distinct attempt IDs.
`submission_uncertain` must reconcile queue, history, and provider identity before a new attempt exists.

## 6. General editor extensibility

Candidate A provides the better general editor foundation.
It models real movies, audio, stills, nested timelines, tracks, masks, motion, color, text, and native movie export.
It does not make PNG frames the execution authority.

Candidate B's normalized evaluation graph is a useful execution representation.
Its stored project representation is incomplete.
`Sequence` contains graph root IDs but no stored graph node maps.
The compiler therefore lacks a typed source for those roots.

Candidate B also exposes `EffectSpec` and `AudioEffect` as string names with string parameters.
That moves semantic validation into runtime conventions.
It recreates the weak capability boundary that the fresh design must remove.

Candidate B's `TextStyle` uses a font-family string.
It cannot guarantee the exact font bytes or stable original-script shaping.
Candidate A's content-addressed font chain is the correct base.

## Required grafts from Candidate B

1. Add a content-addressed `EvaluationPlan` inside Candidate A's export path.
2. Keep plan inspection optional through `prepare_export` and `execute_plan`.
3. Add a typed canonical `AudioBinding` to every revision.
4. Add source sample format, bit depth, packing, endianness, and channel-label state.
5. Persist Candidate B's richer lineage variants inside A's asset catalog.
6. Keep A's exact representation sample map with every native representation edge.
7. Add `AcceptedUsableRange` as review-bound evidence over immutable assets.
8. Add `PromotedUnreceipted` to A's recovery state machine.
9. Report `Planned`, `Implemented`, `Verified`, and `Unsupported` capability states.
10. Bind each verified capability to the binary, backend, OS, fixture, and verifier receipts.

## Required audio decision

The two WAV files are distinct assets.
They are not two metadata descriptions of one byte identity.

The metadata master has these measured properties:

- SHA-256 `8cd42eb7af959f8fbc172d906470abda7952bd6b041ceda45670e565e6840923`.
- 12,554,880 sample frames at 48 kHz.
- 261.56 seconds.
- Interleaved stereo signed 16-bit PCM.

The current timeline master has these measured properties:

- SHA-256 `cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8`.
- 13,104,000 sample frames at 48 kHz.
- 273 seconds.
- Interleaved stereo signed 24-bit little-endian PCM.

The current acceptance authority identifies the 273-second reprise as the canonical timeline master.
The revision must bind that exact hash and full sample interval.
The 261.56-second file remains separate song identity evidence.

The 273-second file must not be declared a source original without provenance evidence.
Use an imported timeline-master role until its derivation is established.

Both WAV probes report no channel layout.
The editor must record an explicit stereo channel-order decision instead of inventing measured labels.

Sample intervals also need a clock domain.
A source interval and a timeline interval can both start at sample zero while using different rates or transforms.
One unqualified `AudioSampleInterval` type does not prevent that mix-up.

## Concrete rejected choices

- Reject Candidate B as the base architecture.
- Reject nominal frame rate or frame count as source timestamp authority.
- Reject direct reuse of historical `source_frames` without a mapping receipt.
- Reject automatic proxy selection for the unsupported VP9 asset.
- Reject a representation edge without an exact authority sample map.
- Reject B's dangling graph roots and string-parameter effect system.
- Reject font-family strings as typography identity.
- Reject mandatory caller coordination of compile, execute, verify, and promote stages.
- Reject `execute(plan_id)` without a stable intent, request hash, and fenced claim.
- Reject a pilot certificate that claims acceptance for a later full-film revision.
- Reject pre-export creative acceptance gates.
- Reject A's current loss of imported and generated origin data after commit.
- Reject A's `source_original` label for the reprise until provenance establishes that claim.
- Reject any claim that the current MP4 is independently reopened or A/V verified.
- Reject any native capability promotion from a header check, successful API call, or playable file alone.

## First implementation gate

Build the A-based aggregate with the grafted immutable plan and canonical audio binding.
Then finish one bounded native round trip before timeline expansion.

The gate must use an exact real source range and the 24-bit reprise WAV.
It must independently reopen and decode the saved movie.
It must enumerate output video PTS and decoded audio coverage.
It must explain the 48,000 submitted samples versus 50,176 AAC ticks.
It must verify trim, alignment, dimensions, hashes, and backend identity.
It must also preserve the VP9 failure as an explicit unsupported result.

Until those checks pass, native H.264/AAC output remains encoded but unverified.
