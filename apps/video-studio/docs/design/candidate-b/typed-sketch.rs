//! Candidate B type and signature sketch.
//!
//! This file is architecture material, not runtime code. Bodies intentionally
//! remain `not implemented!()` so the data flow and ownership stay reviewable.

// ---------- identity and exact time ----------

pub struct Sha256([u8; 32]);
pub struct ProjectId(String);
pub struct RevisionId {
    pub project: ProjectId,
    pub ordinal: u64,
    pub content: Sha256,
}
pub struct PlanId(Sha256);
pub struct AssetId(Sha256);
pub struct AttemptId(String);
pub struct ReviewId(Sha256);
pub struct GateCertificateId(Sha256);
pub struct ArtifactId(Sha256);
pub struct RendererBuild(Sha256);
pub struct BackendBuild(Sha256);

pub struct Rational {
    numerator: std::num::NonZeroU64,
    denominator: std::num::NonZeroU64,
}

impl Rational {
    pub fn new(numerator: u64, denominator: u64) -> Result<Self, TimeError> {
        not_implemented!()
    }
}

pub struct FrameRate(Rational);
pub struct SampleRate(std::num::NonZeroU32);
pub struct FrameIndex(pub u64);
pub struct SampleIndex(pub u64);

/// Half-open interval `[start, start + length)`.
pub struct FrameSpan {
    start: FrameIndex,
    length: std::num::NonZeroU64,
}

impl FrameSpan {
    pub fn new(start: FrameIndex, length: std::num::NonZeroU64) -> Result<Self, TimeError> {
        not_implemented!()
    }
}

/// Half-open interval `[start, start + length)`.
pub struct SampleSpan {
    start: SampleIndex,
    length: std::num::NonZeroU64,
}

impl SampleSpan {
    pub fn new(start: SampleIndex, length: std::num::NonZeroU64) -> Result<Self, TimeError> {
        not_implemented!()
    }
}

pub struct MediaTimestamp {
    pub ticks: i64,
    pub timescale: std::num::NonZeroU32,
}

pub struct TimelineClock {
    pub video_rate: FrameRate,
    pub audio_rate: SampleRate,
}

pub enum SourceFrameSelection {
    ExactFrame,
    NearestFrame,
    BlendAdjacentFrames,
}

pub struct FrameMapSegment {
    pub destination: FrameSpan,
    pub source: FrameSpan,
    pub speed: Rational,
    pub selection: SourceFrameSelection,
}

pub struct SampleMapSegment {
    pub destination: SampleSpan,
    pub source: SampleSpan,
    pub speed: Rational,
}

pub struct FrameTimeMap {
    pub segments: Vec<FrameMapSegment>,
}
pub struct SampleTimeMap {
    pub segments: Vec<SampleMapSegment>,
}

// ---------- media identity and lineage ----------

pub enum MediaKind {
    Movie,
    Still,
    Audio,
    Font,
    Other,
}

pub enum RepresentationKind {
    Original,
    NativeSourceRepresentation,
    Derived,
    GeneratedOriginal,
}

pub struct SourceLocator {
    /// A locator is not identity. The bytes and hash below are identity.
    pub path: String,
}

pub struct VideoDescriptor {
    pub codec: String,
    pub container: String,
    pub width: u32,
    pub height: u32,
    pub nominal_rate: FrameRate,
    pub duration: FrameSpan,
    pub pixel_format: String,
    pub color_metadata: ColorMetadata,
}

pub struct AudioDescriptor {
    pub codec: String,
    pub container: String,
    pub sample_rate: SampleRate,
    pub channels: u16,
    pub sample_format: String,
    pub duration: SampleSpan,
}

pub struct ColorMetadata {
    pub primaries: String,
    pub transfer: String,
    pub matrix: String,
    pub range: String,
}

pub enum Lineage {
    Imported {
        source_bytes: Sha256,
        locator: SourceLocator,
    },
    NativeSourceRepresentation {
        parent: AssetId,
        source_bytes: Sha256,
        conversion_recipe: Sha256,
    },
    Extracted {
        parent: AssetId,
        source_range: FrameSpan,
        extraction_recipe: Sha256,
    },
    Transformed {
        parent: AssetId,
        source_range: Option<FrameSpan>,
        recipe: Sha256,
    },
    Generated {
        attempt: AttemptId,
        input_assets: Vec<AssetId>,
        workflow: Sha256,
        model: Sha256,
        output_bytes: Sha256,
    },
}

pub struct AssetManifest {
    id: AssetId,
    bytes: u64,
    sha256: Sha256,
    media_kind: MediaKind,
    representation: RepresentationKind,
    lineage: Lineage,
    video: Option<VideoDescriptor>,
    audio: Option<AudioDescriptor>,
}

pub enum EvidenceClass {
    Measured,
    FrameInspected,
    Watched,
    Heard,
    UserApproved,
}

pub enum EvidenceDisposition {
    Pending,
    Passed,
    Failed,
}

pub struct ReviewRecord {
    id: ReviewId,
    revision: RevisionId,
    plan: Option<PlanId>,
    artifact: Option<ArtifactId>,
    asset: Option<AssetId>,
    interval: Option<FrameSpan>,
    audio_interval: Option<SampleSpan>,
    class: EvidenceClass,
    disposition: EvidenceDisposition,
    verifier: String,
    evidence_bytes: Sha256,
}

pub struct AcceptedUsableRange {
    pub asset: AssetId,
    pub range: FrameSpan,
    pub review: ReviewId,
}

pub struct AssetUse {
    pub asset: AssetId,
    pub source_range: FrameSpan,
    pub accepted_range: Option<AcceptedUsableRange>,
    pub map: FrameTimeMap,
}

// ---------- project data ----------

pub enum TrackKind {
    Video,
    Audio,
}
pub struct TrackId(String);
pub struct ClipId(String);
pub struct NodeId(String);

pub struct Track {
    pub id: TrackId,
    pub kind: TrackKind,
    pub order: u32,
    pub clips: Vec<Clip>,
}

pub struct Clip {
    pub id: ClipId,
    pub destination: FrameSpan,
    pub source: ClipSource,
    pub effects: Vec<EffectSpec>,
}

pub enum ClipSource {
    Video(AssetUse),
    Audio {
        asset: AssetId,
        source_range: SampleSpan,
        map: SampleTimeMap,
    },
    GeneratedStill(AssetId),
}

pub struct Sequence {
    pub clock: TimelineClock,
    pub duration: FrameSpan,
    pub video_tracks: Vec<Track>,
    pub audio_tracks: Vec<AudioTrack>,
    pub root: VideoNodeId,
    pub audio_root: AudioNodeId,
}

pub struct AudioTrack {
    pub id: TrackId,
    pub order: u32,
    pub clips: Vec<AudioClip>,
}

pub struct AudioClip {
    pub id: ClipId,
    pub destination: SampleSpan,
    pub source: AudioUse,
    pub effects: Vec<AudioEffect>,
}

pub struct AudioUse {
    pub asset: AssetId,
    pub source_range: SampleSpan,
    pub map: SampleTimeMap,
}

pub struct ProjectRevision {
    id: RevisionId,
    parent: Option<RevisionId>,
    assets: AssetCatalog,
    sequence: Sequence,
    audio_binding: AudioBinding,
    direction: DirectionRecord,
    review_prerequisites: ReviewPrerequisites,
}

impl ProjectRevision {
    pub fn id(&self) -> RevisionId {
        not_implemented!()
    }
}

pub struct AudioBinding {
    pub asset: AssetId,
    pub exact_range: SampleSpan,
    pub sha256: Sha256,
}

pub struct DirectionRecord {
    pub story_states: Vec<StoryState>,
    pub musical_events: Vec<MusicalEvent>,
    pub requirements: Vec<RequirementEvidence>,
}

pub struct StoryState {
    pub name: String,
    pub interval: FrameSpan,
}
pub struct MusicalEvent {
    pub name: String,
    pub interval: SampleSpan,
}
pub struct RequirementEvidence {
    pub requirement: String,
    pub evidence_ids: Vec<ReviewId>,
}

pub struct ReviewPrerequisites {
    pub full_film_policy: Sha256,
    pub pilot_gate: Option<GateCertificateId>,
}

pub struct AssetCatalog {
    by_id: std::collections::BTreeMap<AssetId, AssetManifest>,
}

pub struct EditRequest {
    pub project: ProjectId,
    pub expected_revision: Option<RevisionId>,
    pub intent: String,
    pub operations: Vec<EditOperation>,
}

impl EditRequest {
    pub fn new(project: ProjectId) -> Self {
        not_implemented!()
    }
    pub fn bind_asset(self, asset: AssetManifest) -> Self {
        not_implemented!()
    }
    pub fn register_accepted_asset(self, asset: AssetManifest) -> Self {
        not_implemented!()
    }
    pub fn set_timeline(self, sequence: Sequence) -> Self {
        not_implemented!()
    }
}

pub enum EditOperation {
    BindAsset(AssetManifest),
    BindAudio(AudioBinding),
    PutSequence(Sequence),
    PutReviewPrerequisites(ReviewPrerequisites),
}

// ---------- typed graph ----------

pub struct VideoNodeId(String);
pub struct AudioNodeId(String);

pub enum VideoNode {
    Source {
        use_: AssetUse,
    },
    Retimed {
        input: VideoNodeId,
        map: FrameTimeMap,
    },
    Transform {
        input: VideoNodeId,
        geometry: Geometry,
        motion: MotionCurve,
    },
    Color {
        input: VideoNodeId,
        transform: ColorTransform,
    },
    Mask {
        input: VideoNodeId,
        mask: Mask,
    },
    Composite {
        layers: Vec<Layer>,
    },
    Text {
        input: Option<VideoNodeId>,
        text: ScriptText,
        style: TextStyle,
    },
    Still {
        asset: AssetId,
    },
}

pub struct VideoGraph {
    pub nodes: std::collections::BTreeMap<VideoNodeId, VideoNode>,
    pub topological_order: Vec<VideoNodeId>,
    pub root: VideoNodeId,
}

pub enum AudioNode {
    Source(AudioUse),
    Retimed {
        input: AudioNodeId,
        map: SampleTimeMap,
    },
    Gain {
        input: AudioNodeId,
        curve: ScalarCurve,
    },
    Pan {
        input: AudioNodeId,
        curve: ScalarCurve,
    },
    Mix {
        inputs: Vec<AudioNodeId>,
    },
    Silence {
        range: SampleSpan,
    },
}

pub struct AudioGraph {
    pub nodes: std::collections::BTreeMap<AudioNodeId, AudioNode>,
    pub topological_order: Vec<AudioNodeId>,
    pub root: AudioNodeId,
}

pub struct Layer {
    pub input: VideoNodeId,
    pub z: u32,
    pub opacity: ScalarCurve,
    pub mask: Option<Mask>,
}

pub struct Geometry {
    pub scale: ScalarCurve,
    pub position_x: ScalarCurve,
    pub position_y: ScalarCurve,
    pub rotation: ScalarCurve,
}

pub struct MotionCurve {
    pub channels: Vec<(String, ScalarCurve)>,
}

pub struct ScalarCurve {
    pub keys: Vec<(FrameIndex, Rational)>,
}

pub struct Mask {
    pub shape: MaskShape,
    pub feather: Rational,
    pub invert: bool,
    pub motion: Option<MotionCurve>,
}

pub enum MaskShape {
    Rectangle,
    Ellipse,
    Path(Vec<(Rational, Rational)>),
    AlphaFromAsset(AssetId),
}

pub struct ColorTransform {
    pub operations: Vec<ColorOperation>,
}
pub enum ColorOperation {
    Matrix([[Rational; 4]; 4]),
    Exposure(Rational),
    Lut(Sha256),
    ToneMap(String),
}

pub struct ScriptText {
    pub unicode: String,
    pub language: String,
    pub script: String,
    pub direction: TextDirection,
}

pub enum TextDirection {
    Ltr,
    Rtl,
    Ttb,
}
pub struct TextStyle {
    pub font_family: String,
    pub size: Rational,
    pub color: [u16; 4],
}

pub struct EffectSpec {
    pub name: String,
    pub parameters: Vec<(String, String)>,
}
pub struct AudioEffect {
    pub name: String,
    pub parameters: Vec<(String, String)>,
}

// ---------- plan and gates ----------

pub enum RenderScope {
    Pilot {
        proof_case: ProofCase,
    },
    FullFilm {
        pilot_gate: GateCertificateId,
        required_review_policy: Sha256,
    },
    Interval {
        range: FrameSpan,
    },
}

pub struct ProofCase {
    pub name: String,
    pub required_source_worlds: Vec<String>,
    pub required_audio: SampleSpan,
}

pub struct EvaluationRequest {
    pub revision: RevisionId,
    pub scope: RenderScope,
    pub output: ExportProfile,
}

pub enum ExportProfile {
    NativeMovie(NativeMovieProfile),
    FrameSequence,
    AudioOnly,
}

pub struct NativeMovieProfile {
    pub container: String,
    pub video_codec: String,
    pub audio_codec: String,
    pub width: u32,
    pub height: u32,
    pub frame_rate: FrameRate,
    pub audio_rate: SampleRate,
    pub channels: u16,
}

pub struct EvaluationPlan {
    id: PlanId,
    revision: RevisionId,
    renderer: RendererBuild,
    backend: BackendBuild,
    clock: TimelineClock,
    output: ExportProfile,
    video: VideoGraph,
    audio: AudioGraph,
    video_coverage: Vec<FrameSpan>,
    audio_coverage: Vec<SampleSpan>,
    assets: AssetCatalog,
    source_uses: Vec<AssetUse>,
    required_capabilities: Vec<CapabilityId>,
    gate_certificate: Option<GateCertificateId>,
}

pub struct PreparedEvaluation {
    pub plan: EvaluationPlan,
    pub diagnostics: Vec<PlanDiagnostic>,
}

impl PreparedEvaluation {
    pub fn plan_id(&self) -> PlanId {
        not_implemented!()
    }
    pub fn requirements(&self) -> &[CapabilityId] {
        not_implemented!()
    }
}

pub struct PlanDiagnostic {
    pub code: String,
    pub detail: String,
}
pub struct CapabilityId(String);

pub enum EvaluationOutcome {
    Rendered {
        artifact: RenderArtifact,
        checkpoint: EditableCheckpoint,
    },
    Replayed {
        artifact: RenderArtifact,
        checkpoint: EditableCheckpoint,
    },
    GatePending {
        missing: Vec<ReviewId>,
    },
    Unsupported {
        capability: CapabilityId,
        detail: String,
    },
    Failed {
        error: EvaluationError,
    },
}

pub struct RenderArtifact {
    pub id: ArtifactId,
    pub plan: PlanId,
    pub output_sha256: Sha256,
    pub frame_count: u64,
    pub sample_count: u64,
    pub measured_width: u32,
    pub measured_height: u32,
    pub measured_rate: FrameRate,
}

pub struct EditableCheckpoint {
    pub revision: RevisionId,
    pub plan: PlanId,
    pub manifest_sha256: Sha256,
}

// ---------- native backend boundary ----------

pub struct MediaProbe {
    pub video: Vec<VideoDescriptor>,
    pub audio: Vec<AudioDescriptor>,
    pub native_decode: bool,
    pub native_encode: Vec<NativeMovieProfile>,
}

pub struct VideoFrame {
    pub frame: FrameIndex,
    pub timestamp: MediaTimestamp,
    pub width: u32,
    pub height: u32,
    pub pixels: OwnedPixelBuffer,
}

pub struct AudioBlock {
    pub samples: SampleSpan,
    pub sample_rate: SampleRate,
    pub channels: u16,
    pub pcm: Vec<f32>,
}

pub struct OwnedPixelBuffer {
    pub bytes: Vec<u8>,
    pub format: String,
}
pub struct VideoFrames;
pub struct AudioSamples;
pub struct FrameStream;
pub struct AudioStream;
pub struct ArtifactSink;
pub struct BackendReceipt;

pub(crate) trait NativeMediaBackend {
    fn probe(&self, asset: &AssetManifest) -> Result<MediaProbe, MediaError>;
    fn decode_video(&self, use_: &AssetUse) -> Result<VideoFrames, MediaError>;
    fn decode_audio(&self, use_: &AudioUse) -> Result<AudioSamples, MediaError>;
    fn encode_movie(
        &self,
        plan: &EvaluationPlan,
        frames: FrameStream,
        audio: AudioStream,
        profile: &NativeMovieProfile,
        sink: &mut ArtifactSink,
    ) -> Result<BackendReceipt, MediaError>;
}

pub struct MacosNativeMedia;
// `MacosNativeMedia` contains the only unsafe AVFoundation, CoreMedia,
// VideoToolbox, CoreVideo, AudioToolbox, and CoreText boundary.

// ---------- review and recovery ----------

pub struct GateCertificate {
    id: GateCertificateId,
    exact_review_ids: Vec<ReviewId>,
}

pub(crate) trait ReviewStore {
    fn read(&self, id: ReviewId) -> Result<ReviewRecord, ReviewError>;
    fn verify_gate(
        &self,
        id: GateCertificateId,
        plan: &EvaluationPlan,
    ) -> Result<GateCertificate, ReviewError>;
}

pub enum ProviderJobState {
    IntentPersisted,
    SubmittedUnknown,
    Accepted,
    Running,
    Failed,
    Downloaded,
    TransferVerified,
    Rejected,
}

pub struct GenerationIntent {
    pub id: String,
    pub revision: RevisionId,
    pub shot: String,
    pub input_snapshot: Sha256,
    pub workflow: Sha256,
    pub model: Sha256,
}

pub struct GenerationAttempt {
    pub id: AttemptId,
    pub intent: GenerationIntent,
    pub provider_key: String,
    pub idempotency_key: String,
    pub state: ProviderJobState,
}

pub(crate) trait TenantEffectAdapter {
    fn persist_intent(
        &self,
        intent: GenerationIntent,
    ) -> Result<GenerationAttempt, ApplicationError>;
    fn reconcile(&self, attempt: AttemptId) -> Result<GenerationAttempt, ApplicationError>;
    fn register_verified_asset(
        &self,
        attempt: AttemptId,
    ) -> Result<AssetManifest, ApplicationError>;
}

// ---------- storage, public facade, and CLI boundary ----------

pub(crate) trait RevisionStore {
    fn load_revision(&self, id: RevisionId) -> Result<ProjectRevision, StoreError>;
    fn save_revision(&self, revision: &ProjectRevision) -> Result<(), StoreError>;
    fn save_plan(&self, plan: &EvaluationPlan) -> Result<(), StoreError>;
    fn load_plan(&self, id: PlanId) -> Result<EvaluationPlan, StoreError>;
    fn reconcile_render(&self, plan: PlanId, intent: String) -> Result<RenderState, StoreError>;
}

pub struct StudioConfig {
    pub renderer: RendererBuild,
    pub resource_limits: ResourceLimits,
}

impl Default for StudioConfig {
    fn default() -> Self {
        not_implemented!()
    }
}

pub struct ResourceLimits {
    pub max_pixels: u64,
    pub max_frames: u64,
    pub max_samples: u64,
}

pub struct Studio;

impl Studio {
    pub fn open(
        root: impl AsRef<std::path::Path>,
        config: StudioConfig,
    ) -> Result<Self, OpenError> {
        not_implemented!()
    }
    pub fn edit(&self, request: EditRequest) -> Result<ProjectRevision, EditError> {
        not_implemented!()
    }
    pub fn compile(&self, request: EvaluationRequest) -> Result<PreparedEvaluation, CompileError> {
        not_implemented!()
    }
    pub fn evaluate(
        &self,
        request: EvaluationRequest,
    ) -> Result<EvaluationOutcome, EvaluationError> {
        not_implemented!()
    }
    pub fn execute(&self, plan: PlanId) -> Result<EvaluationOutcome, EvaluationError> {
        not_implemented!()
    }
    pub fn inspect(&self, query: InspectionQuery) -> Result<InspectionResult, InspectionError> {
        not_implemented!()
    }
    pub fn capabilities(&self) -> Result<CapabilityInventory, CapabilityError> {
        not_implemented!()
    }
}

pub struct InspectionQuery {
    pub artifact: Option<ArtifactId>,
    pub plan: Option<PlanId>,
}
pub struct InspectionResult;
pub struct CapabilityInventory;

pub enum RenderState {
    Pending,
    PromotedUnreceipted,
    Completed(RenderArtifact),
    Rejected,
}
pub struct OpenError;
pub struct EditError;
pub enum CompileError {
    GatePending {
        missing: Vec<ReviewId>,
    },
    Unsupported {
        capability: CapabilityId,
        detail: String,
    },
    Invalid {
        diagnostics: Vec<PlanDiagnostic>,
    },
}
pub struct EvaluationError;
pub struct InspectionError;
pub struct CapabilityError;
pub struct MediaError;
pub struct ReviewError;
pub struct StoreError;
pub struct ApplicationError;
pub struct TimeError;
