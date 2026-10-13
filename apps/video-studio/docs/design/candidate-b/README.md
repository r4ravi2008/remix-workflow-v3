# Candidate B: immutable evaluation plan

This candidate makes a validated, immutable `EvaluationPlan` the only input to native evaluation.
An immutable `ProjectRevision` stores the source facts and editing intent.
The plan compiler reads one revision, resolves every reference, validates every interval, and emits a content-addressed execution program.
The renderer never reads a mutable project or asks a caller to coordinate decode, composition, mix, and encode stages.

The assigned shape is the evaluation-plan shape. It is structurally different from a design centered on a long-lived project aggregate.

## Usage (caller's view)

The Rust library is the primary interface. The direct CLI is a thin process adapter over the same interface.
Callers provide typed domain requests. They do not provide framework objects, JSON envelopes, provider credentials, or renderer stage callbacks.

### General Rust caller

```rust
use video_studio::{
    CompileError, EditRequest, EvaluationOutcome, EvaluationRequest, ExportProfile,
    RenderScope, Studio, StudioConfig,
};

let studio = Studio::open("/work/panja-editor", StudioConfig::default())?;

// The result is an immutable revision. A later edit always creates another revision.
let revision = studio.edit(EditRequest::new(project_id)
    .bind_asset(source_movie_manifest)
    .bind_asset(canonical_audio_manifest)
    .set_timeline(sequence))?;

// Compilation validates hashes, bounds, tracks, source retiming, graph structure,
// native capability, and the required acceptance prerequisites.
let prepared = studio.compile(EvaluationRequest {
    revision: revision.id(),
    scope: RenderScope::Pilot { proof_case: proof_case },
    output: ExportProfile::NativeMovie(native_movie_profile),
})?;

// The plan is safe to inspect or persist. It contains all source hashes and
// the exact video/audio evaluation graph that the renderer will consume.
println!("plan={} requirements={:?}", prepared.plan_id(), prepared.requirements());

let result = studio.execute(prepared.plan_id())?;
match result {
    EvaluationOutcome::Rendered { artifact, .. }
    | EvaluationOutcome::Replayed { artifact, .. } => {
        assert_eq!(artifact.plan, prepared.plan_id());
    }
    other => return Err(unexpected_outcome(other)),
}
```

`compile` and `execute` are the only two explicit calls needed when a caller wants to inspect a plan before rendering.
They are public checkpoints, not internal decode or render stages.
The convenience call `studio.evaluate(request)` compiles and executes the same plan atomically from the caller's point of view.

### Full Panja evaluation

```rust
let full = match studio.compile(EvaluationRequest {
    revision: panja_revision,
    scope: RenderScope::FullFilm {
        pilot_gate: pilot_gate_certificate,
        required_review_policy: current_music_policy,
    },
    output: ExportProfile::NativeMovie(panja_movie_profile),
}) {
    Ok(plan) => plan,
    Err(CompileError::GatePending { missing }) => {
        report_pending(missing);
        return Ok(());
    }
    Err(error) => return Err(error.into()),
};

let result = studio.execute(full.plan_id())?;
match result {
    EvaluationOutcome::Rendered { artifact, checkpoint } => {
        deliver_to_application(artifact, checkpoint)?;
    }
    EvaluationOutcome::GatePending { missing } => report_pending(missing),
    EvaluationOutcome::Unsupported { capability, detail } => report_unsupported(capability, detail),
    EvaluationOutcome::Failed { error } => report_failure(error),
}
```

The full plan cannot be compiled without a version-bound pilot certificate.
The certificate must cover the exact revision, the exact pilot plan, the exact pilot artifact, and the watched/heard proof required by the policy.
Measurements can establish technical facts. They cannot construct the certificate.

### Direct agent CLI

The CLI owns stdin framing, schema negotiation, process deadlines, stdout/stderr, and exit codes.
The library owns all media and editing semantics.

```sh
video-studio discover
video-studio edit --request panja-bind.json
video-studio compile --request panja-pilot.json --write-plan .state/plans/pilot.json
video-studio evaluate --plan .state/plans/pilot.json
video-studio inspect --artifact <artifact-id>
```

`compile` emits a plan identity and a structured error for an unsupported codec or missing gate.
`evaluate` accepts only a stored immutable plan identity or an exact plan file whose hash matches the stored plan.
There is no `--ffmpeg`, subprocess renderer, or provider fallback flag.

### Separate tenant and GPU application caller

Effect application code remains outside the native crate. It owns tenant authorization, job records, provider adapters, and review workflows.

```rust
let intent = app.generation_intent(panja_revision, shot_id)?;
let attempt = app.submit_local_herdr(intent)?;

// An unknown response is reconciled before a new attempt can be created.
let accepted = app.reconcile_and_accept(attempt.id())?;
let next_revision = studio.edit(EditRequest::new(panja_revision)
    .register_accepted_asset(accepted.manifest()))?;
```

The native library receives a verified `AssetManifest` and its lineage.
It never submits a Herdr or provider request and never treats a provider completion badge as creative acceptance.

The source catalog must also distinguish the downloaded representation from a playable native representation.
The current source audit contains AV1 and VP9 MP4 references at 24 fps, while the preserved R23 export is H.264.
Candidate B does not assume that AVAssetReader can decode every downloaded YouTube codec.
`CapabilityInventory` probes each actual asset and profile.
An unsupported AV1 or VP9 source returns `unsupported_decode` before plan compilation; it is not silently replaced with R23 or a guessed proxy.
If an explicitly authorized native conversion creates a supported representation, that file gets a new hash and a `NativeSourceRepresentation` lineage edge to the original bytes.

## Problem

The editor must be a general Rust media library and direct agent CLI, while the Panja film requires a source-bound hybrid of real footage, source-derived anime, generated motion, masks, color, motion, original-script text, and mixed audio.
The native path cannot use FFmpeg, libav, subprocess rendering, or a copied predecessor runtime.
The source and audio records currently disagree, the historical film lacks the current creative-proof gate, and all review claims must remain tied to an exact revision and artifact.
The shape must therefore make stale source data, fractional timing, unverified perception, uncertain GPU submissions, and unsupported native codecs explicit before execution.

## Shape

### The load-bearing data structures

`ProjectRevision` is an immutable, content-addressed document. It contains editing facts, source manifests, track order, graph nodes, audio binding, and review prerequisites.
It is never mutated in place.

`EvaluationPlan` is a second immutable document compiled from one `ProjectRevision` plus one `EvaluationRequest`.
It contains a closed normalized graph, integer frame/sample coverage, exact asset hashes, native capability requirements, and output policy.
The renderer receives a plan and a content store only.

The plan is not a cache of a project. It is the validated execution contract.
If project data changes, the revision hash changes, the plan hash changes, and an old artifact remains bound to the old plan.

The full typed sketch is in [typed-sketch.rs](typed-sketch.rs).

### Project data to plan data

The compiler performs the following domain work inside one library call:

1. Load the requested immutable revision by `RevisionId`.
2. Verify each asset's exact byte hash, size, media kind, and measured stream descriptor.
3. Resolve one canonical audio asset and its exact sample interval.
4. Validate half-open frame and sample spans against source and output bounds.
5. Validate track order, overlap rules, composition graph acyclicity, masks, curves, text runs, and audio mix routing.
6. Validate source retiming maps and accepted usable ranges.
7. Validate the required native backend capabilities without selecting a hidden fallback.
8. Validate pilot or full-film review prerequisites against exact revision, plan, and artifact identities.
9. Freeze a normalized video graph, audio graph, coverage ledger, lineage set, and output request into `EvaluationPlan`.

The plan compiler reports every failure as a typed diagnostic.
It does not silently choose the other audio file, clamp an out-of-bounds range, round a frame boundary through floating-point seconds, or substitute a renderer.

### Evaluation graph

The normalized plan has separate typed video and audio graphs.
The graph nodes are arranged by the knowledge they own, not by a public sequence of decode/transform/save methods.

Video nodes include source reads, retiming, geometry, motion curves, color transforms, masks, layer composition, original-script typography, and output conversion.
Audio nodes include source reads, sample retiming, gain/pan, channel routing, mixing, and output conversion.
Each output frame or sample block is derived from integer coverage spans and graph nodes.

The plan stores spans and deterministic node parameters instead of requiring the caller to build per-frame commands.
The evaluator derives a frame program from the plan for a requested output frame and resolves source bytes only by the hashes embedded in the plan.

The `EffectSpec` values in the sketch are native operation descriptions, such as a color or mask operation.
They are not the Effect runtime, a provider adapter, or a tenant service.
The application-level Effect adapter remains outside this crate and can only add a verified asset or typed revision operation.

### Time and source invariants

All edit boundaries use integer positions.
`FrameRate` is a reduced positive rational.
`FrameSpan` and `SampleSpan` are half-open intervals with positive lengths.
Media timestamps at the native boundary use rational ticks and are converted through checked arithmetic.

Source retiming is a piecewise rational map with an explicit selection policy for non-integer source positions.
It cannot produce a source frame outside its declared `SourceFrameRange`.
Audio retiming uses a separate sample map and an explicit resampling policy.
Video frames and audio samples never share a floating-point time key.

The plan stores the source interval for every `VideoSourceUse` and `AudioSourceUse`.
An accepted generated range is a typed proof that a particular asset and interval passed the required review.
The compiler rejects a clip that asks for more usable range than its proof covers.

### Lineage and immutable assets

An asset manifest names exact bytes and a complete derivation record.
The derivation record distinguishes imported source, extracted source frame, source-derived transformation, generated original, accepted usable range, and supersession.
Generated originals remain immutable even after a downstream edit rejects part of their usable range.
An accepted range refers to the original asset, its exact frame/sample span, and the review evidence that accepted that span.

The native library does not infer lineage from filenames.
Paths are locators for local storage only; the content hash and derivation record are the identity.

### Review truthfulness

Review records carry the exact revision, plan, artifact hash, interval, evidence class, disposition, verifier identity, and capture metadata.
The evidence classes remain distinct:

- `Measured` records dimensions, timestamps, hashes, and sample counts.
- `FrameInspected` records selected decoded frames.
- `Watched` records normal-speed motion review.
- `Heard` records audio review with the selected audio binding.
- `UserApproved` records the requested approval boundary.

`Watched` and `Heard` are not derived from `Measured` or `FrameInspected`.
Pending or failed perceptual evidence cannot be promoted by a new measurement.
Only the review service can issue a `GateCertificate`; the transport layer accepts a certificate identifier and the store verifies its exact bindings.

The native artifact receipt therefore reports technical completion separately from playback, listening, and creative acceptance.
An output file, a decode check, or a plan hash never claims that a person watched or heard the film.

### Local-GPU recovery boundary

The native plan can require a generated asset, but it does not own provider execution.
The separate application adapter persists a generation intent and exact input snapshot before submission.
Each attempt has a new `AttemptId` and an idempotency key for its logical submission.
An absent or timed-out response creates `SubmittedUnknown`, not `Failed`.
The adapter reconciles the provider by intent and idempotency key before it can retry.
Downloaded originals are hash-verified before registration into the native asset catalog.

An accepted generated asset cannot enter a revision until its manifest contains the source anchor hashes, workflow/model identity, attempt receipt, transfer hash, and accepted usable range.
The native compiler rejects an asset whose provider outcome is uncertain, whose transfer is unverified, or whose acceptance evidence binds a different plan.

### Native movie and audio path

The macOS backend is a Rust-owned adapter. It exposes domain `VideoFrame`, `AudioBlock`, and `EncodedPacket` types to the evaluator.
No `AVAsset`, `CMSampleBuffer`, `CVPixelBuffer`, or Objective-C object crosses into the domain modules.

The adapter uses the following native path:

| Domain need | macOS framework boundary | Candidate B use |
| --- | --- | --- |
| Inspect assets and tracks | AVFoundation `AVAsset`, `AVAssetTrack` | Probe container, stream descriptors, duration, dimensions, and track identity. |
| Decode source video | AVFoundation `AVAssetReader` with `AVAssetReaderTrackOutput` | Request decoded pixel buffers in presentation order and map PTS to rational timestamps. |
| Decode source audio | AVFoundation reader or AudioToolbox PCM conversion | Produce fixed-format PCM blocks with integer sample positions. |
| Compose frames | Rust compositor over owned pixel buffers | Apply graph nodes, masks, motion, color, and text before output. |
| Encode video | AVAssetWriter pixel-buffer input backed by VideoToolbox, or direct `VTCompressionSession` | Probe H.264/HEVC/ProRes support and encode only a declared profile. |
| Encode and mux audio | AVAssetWriter audio input plus AudioToolbox/AVAudioConverter | Mix/resample PCM, append native sample buffers, and mux with video. |
| Reopen output | AVFoundation `AVAssetReader` | Independently measure frame/sample counts, timestamps, dimensions, and hashes. |

Apple documents that an `AVAssetReaderTrackOutput` with output settings decodes samples and returns them in presentation order, while a `nil` output setting returns stored samples in decode order.
That distinction is part of the adapter contract.
Apple documents `CMSampleBuffer` timing and sample metadata, `VTDecompressionSession`/`VTCompressionSession` session workflows, and Audio Converter Services for PCM and compressed conversion.

This path is feasible on the current host: `xcrun --sdk macosx --show-sdk-path` resolves the Command Line Tools macOS SDK, and the SDK contains AVFoundation, VideoToolbox, CoreMedia, CoreVideo, and AudioToolbox frameworks and headers.
Rust bindings are available through the `objc2-av-foundation` and `objc2-video-toolbox` crates, or through a small isolated C/Objective-C FFI layer if a required binding is missing.
The first experiment must compile and run this adapter on the current host before a timeline feature is considered implemented.

The observed build host is macOS 26.0.1 on arm64 with Darwin 25.0 and the Command Line Tools SDK.
That observation proves framework and header availability only.
It does not prove that the host decodes AV1 or VP9, accepts every H.264/HEVC profile, or supports every writer combination.

Codec support is an observed capability, not a framework promise for every file.
The registry records source decode support separately for AV1, VP9, H.264, HEVC, ProRes, and each measured container/profile.
The first experiment must probe the actual Panja source references and the preserved H.264 R23 reference independently.
Passing the H.264 case does not promote AV1 or VP9 support.

The framework adapter never invokes a process.
The Cargo dependency and link audit must fail if a new build links FFmpeg, libav, or an unapproved codec library.

### Native capabilities and general editor coverage

`CapabilityInventory` is produced by the native binary from its compiled backend registry and acceptance receipts.
It reports `Planned`, `Implemented`, `Verified`, or `Unsupported` per capability.
The plan compiler only treats a capability as executable when the current native build reports it.

The inventory remains general: media ingest, cut/edit, layered composition, masks, motion, color, Fairlight-style audio, typography, export, collaboration records, AI asset references, and extension boundaries can each have independent capability entries.
The Panja profile is a demanding acceptance case, not the definition of the editor's data model.

### Crash recovery and artifact identity

`execute(plan_id)` creates a durable pending render record keyed by the plan hash and an intent identity.
The evaluator writes a temporary output, flushes it, atomically promotes it, reopens it through the native reader, and only then stores a completed receipt.
On restart, the same plan and intent reconcile any pending or promoted bytes.
An artifact from a different plan, renderer build, backend build, or source hash cannot be adopted.
An incomplete output is never presented as a successful artifact.

The receipt binds project revision, plan, intent, renderer build, native framework backend build, output hash, dimensions, frame rate, frame count, audio sample rate, channel count, sample count, and measured durations.
The editable checkpoint binds the same revision and plan, with all asset manifests and graph parameters needed to reopen the edit.

## Public signatures

The following signatures are the small public surface. The complete type-level sketch is in `typed-sketch.rs`.

```rust
pub struct Studio { /* private storage, compiler, evaluator, and backend */ }

impl Studio {
    pub fn open(root: impl AsRef<std::path::Path>, config: StudioConfig)
        -> Result<Self, OpenError>;

    pub fn edit(&self, request: EditRequest)
        -> Result<ProjectRevision, EditError>;

    pub fn compile(&self, request: EvaluationRequest)
        -> Result<PreparedEvaluation, CompileError>;

    pub fn evaluate(&self, request: EvaluationRequest)
        -> Result<EvaluationOutcome, EvaluationError>;

    pub fn execute(&self, plan: PlanId)
        -> Result<EvaluationOutcome, EvaluationError>;

    pub fn inspect(&self, query: InspectionQuery)
        -> Result<InspectionResult, InspectionError>;

    pub fn capabilities(&self)
        -> Result<CapabilityInventory, CapabilityError>;
}
```

These methods hide storage transactions, graph validation, source reads, compositor scheduling, encoder backpressure, atomic artifact promotion, and receipt reconciliation.
They expose only domain decisions the caller must make: which revision, which output profile, which scope, and which review certificate.

The following traits are internal seams. They are not transport types and are not exported from the application adapter.

```rust
pub(crate) trait NativeMediaBackend {
    fn probe(&self, asset: &AssetManifest) -> Result<MediaProbe, MediaError>;
    fn decode_video(&self, use_: &VideoSourceUse) -> Result<VideoFrames, MediaError>;
    fn decode_audio(&self, use_: &AudioSourceUse) -> Result<AudioSamples, MediaError>;
    fn encode_movie(
        &self,
        plan: &EvaluationPlan,
        frames: FrameStream,
        audio: AudioStream,
        profile: &NativeMovieProfile,
        sink: &mut ArtifactSink,
    ) -> Result<BackendReceipt, MediaError>;
}

pub(crate) trait RevisionStore {
    fn load_revision(&self, id: RevisionId) -> Result<ProjectRevision, StoreError>;
    fn save_revision(&self, revision: &ProjectRevision) -> Result<(), StoreError>;
    fn save_plan(&self, plan: &EvaluationPlan) -> Result<(), StoreError>;
    fn load_plan(&self, id: PlanId) -> Result<EvaluationPlan, StoreError>;
    fn reconcile_render(&self, intent: RenderIntent) -> Result<RenderState, StoreError>;
}
```

## Module map

The module boundaries follow ownership of decisions. They do not mirror the temporal order of a render.

| Module | Owns | Does not own |
| --- | --- | --- |
| `domain::identity` | Hashes, IDs, canonical serialization, build identity | File paths or transport request IDs |
| `domain::time` | Rational rates, frame/sample spans, source maps, checked conversion | Native `CMTime` objects |
| `domain::media` | Asset manifests, stream descriptors, source ranges, lineage, accepted usable ranges | Provider calls or filename inference |
| `domain::project` | Immutable revisions, edit intents, track order, sequence data, audio binding | Render scheduling or framework objects |
| `domain::graph` | Typed video/audio nodes, masks, color, motion, text, mix routing | Storage transactions or UI commands |
| `domain::plan` | Revision-to-plan compilation, validation, capabilities, coverage, plan identity | Decode, encode, or application review UI |
| `domain::review` | Evidence classes, version bindings, gate certificates, promotion rules | Claims that a technical receipt means watched/heard |
| `engine::evaluate` | Plan interpreter, frame/sample program derivation, deterministic scheduling | Project mutation or provider orchestration |
| `engine::artifact` | Pending records, staging, flush/promotion, receipts, checkpoint identity | Creative acceptance or public publication |
| `platform::macos_media` | AVFoundation/CoreMedia/VideoToolbox/AudioToolbox FFI and owned buffer conversion | Domain graph policy and tenant state |
| `storage::local` | Content-addressed revisions, plans, receipts, recovery transactions | Native codec decisions |
| `cli` | Process lifetime, framing, schemas, deadlines, discovery, exit codes | Editing semantics and render fallbacks |
| `application::effect_adapter` | Tenant authorization, asset/job/review records, Effect adapters, Herdr recovery | Native media processing |

The native library has no dependency on `application::effect_adapter`.
The adapter can embed the library or invoke the CLI, but it cannot maintain a second timeline reducer or a second artifact identity scheme.

## First executable experiment

Build `native-media-smoke` before implementing the general timeline.
It must run against a real movie source and a declared audio fixture from the Panja workspace.

The experiment should:

1. Read the source movie with the macOS reader adapter.
2. Probe every video and audio track, including actual codec, dimensions, nominal rate, sample rate, channel layout, and duration.
3. Decode one exact source frame interval and one exact audio sample interval.
4. Write an identity source-bound movie through the native writer with the requested video and audio profile.
5. Reopen the output with the native reader.
6. Compare frame count, rational timestamps, dimensions, pixel samples, audio sample count, sample rate, channels, and selected sample hashes.
7. Record a structured `Verified`, `Unsupported`, or `Inconclusive` result.

The experiment must inspect the process tree and Cargo link/dependency graph.
Any subprocess renderer or FFmpeg/libav link is a failure.
An unsupported source or output profile is a structured capability error.
The experiment must not switch to a different backend to make the case pass.

Independent acceptance expects the verifier to reopen the saved output and perform its own measurements.
A successful API call, a file that exists, a queue state, or a source inventory cannot satisfy this experiment.

## Panja full-film acceptance path

Candidate B treats the Panja film as a sequence of exact, reviewable plans.

1. Bind the selected song, source movie catalog, and canonical audio hash in a new revision. The 261.56-second metadata WAV and the 273-second reprise WAV remain separate until an explicit source choice is made.
2. Import the original footage and every generated original with exact hashes. Attach source frame ranges, anchor hashes, generation attempt IDs, transformations, and accepted usable ranges.
3. Create a pilot revision containing the hardest original-to-anime-to-original handoff, the canonical audio, the requested grade, and the required character/action risk.
4. Compile the pilot into an immutable plan. Reject missing lineage, unresolved audio, unsupported codecs, uncovered output frames, and missing creative-proof prerequisites.
5. Execute the pilot through the native movie/audio path. Reopen and measure the result independently.
6. Record frame inspection, normal-speed watch, listening, and any user approval as separate evidence on the exact pilot plan and artifact.
7. Issue a pilot gate certificate only when the required current policy evidence exists. A measurement receipt cannot issue it.
8. Build the full chronological revision with opening, development, awakening/change, consequence, and ending. Match source-frame endpoints across real and drawn worlds. Keep every source interval and generated usable interval in the plan lineage.
9. Compile the full plan with the pilot certificate. Execute it with the selected native output profile and editable checkpoint.
10. Run component, event/join, full playback, listening, and two full-film correction passes. Each new correction creates a new revision and plan. Each predecessor review remains available but cannot promote the new artifact.

Resolve evidence remains separate from native output evidence.
A Resolve-generated reference film cannot establish native renderer capability.

## Synthesis decision

Pending the parent arena's cross-candidate comparison.
This candidate recommends the immutable evaluation-plan shape because it gives the renderer one complete, hashable contract and makes stale project reads impossible during evaluation.

## Tradeoffs accepted

- We accept a compilation step and a larger immutable plan record in exchange for deterministic execution and simple crash recovery.
- We accept a macOS-first media backend in exchange for a real native movie/audio path without FFmpeg or libav.
- We accept explicit capability failures in exchange for never hiding an unsupported codec behind a fallback renderer.
- We accept separate technical and perceptual evidence in exchange for truthful playback, listening, and approval claims.
- We accept that a changed source, review record, or renderer build invalidates a plan in exchange for source-bound artifacts.
- We accept that the first compositor may use owned CPU pixel buffers before a Metal path is verified in exchange for preserving one domain graph.
- We accept that provider and tenant orchestration stays outside the native library in exchange for clean recovery and authorization boundaries.

## Alternatives considered

### Persistent project aggregate

A persistent aggregate makes edits natural, but a renderer must repeatedly read aggregate state or expose a snapshot protocol.
That leaks revision loading, stage ordering, and recovery decisions to callers.
Candidate B hides those decisions behind one compiler and gives the evaluator an immutable input.

### AVMutableComposition as the rendering model

AVFoundation composition objects can represent basic track assembly, but they would expose framework timing, layer-instruction, and export policy to the native domain.
They do not provide the required domain contract for source lineage, accepted usable ranges, generated provenance, masks, review gates, or arbitrary graph nodes.
Candidate B uses AVFoundation for media I/O and native output, while Rust owns the composition graph.

### A streaming render pipeline with mutable callbacks

A callback pipeline can reduce intermediate storage, but it makes retry and exact artifact adoption depend on callback history.
It also encourages callers to coordinate decode, transform, mix, and encode lifetimes.
Candidate B derives a deterministic frame/sample program from a plan and persists pending render identity before consuming media.

## Open questions and risks

- Does the Panja source movie decode through AVAssetReader on the current host with the exact frame timestamps and color metadata required by the acceptance case?
- Which current Panja references are AV1 or VP9 MP4 files, and does this host's native decoder support each one at the required pixel format and frame timing?
- If a downloaded source is unsupported, will the product stop with `unsupported_decode`, or will an explicitly authorized native source representation be prepared and linked by lineage before editing?
- Which native output profile is actually available for the selected source and target dimensions: QuickTime/H.264/AAC, QuickTime/HEVC/AAC, ProRes/PCM, or another measured profile?
- Should the first release require a macOS deployment target matching the current SDK, or should the adapter weak-link newer VideoToolbox symbols and report runtime availability?
- Can the chosen Rust Objective-C binding safely contain AVFoundation callbacks and CoreFoundation ownership without `Send` or lifetime escapes?
- Which CoreText/font inventory is required for the Panja original-script typography, and how will missing fonts become a typed capability error?
- What independent playback and listening harness will issue `Watched` and `Heard` evidence for the exact artifact?
- Which tenant application stores and signs gate certificates, and how will the native store verify their producer identity without importing tenant logic?
- What resource ceiling is safe for a full 273-second plan and its decoded frame windows on the local workstation?
- Which Metal or CPU compositor acceptance corpus will prove masks, color transforms, and motion curves before either backend is marked `Verified`?

## Next implementation step

Implement the macOS `native-media-smoke` against this plan boundary, then make its independent reopen verifier the first capability receipt.

## Reference grounding

- [Apple: Media reading and writing](https://developer.apple.com/documentation/avfoundation/media-reading-and-writing)
- [Apple: AVAssetReader](https://developer.apple.com/documentation/avfoundation/avassetreader)
- [Apple: CMTimeRange](https://developer.apple.com/documentation/coremedia/cmtimerange)
- [Apple: CMSampleBuffer](https://developer.apple.com/documentation/coremedia/cmsamplebuffer)
- [Apple: VTDecompressionSession](https://developer.apple.com/documentation/videotoolbox/vtdecompressionsession-api-collection)
- [Apple: VTCompressionSession](https://developer.apple.com/documentation/videotoolbox/vtcompressionsession-api-collection)
- [Apple: Audio Converter Services](https://developer.apple.com/documentation/audiotoolbox/audio-converter-services)
- [`objc2-av-foundation` Rust bindings](https://docs.rs/objc2-av-foundation/latest/objc2_av_foundation/)
- [`objc2-video-toolbox` Rust bindings](https://docs.rs/objc2-video-toolbox/latest/objc2_video_toolbox/)
