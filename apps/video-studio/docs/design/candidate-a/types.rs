//! Architecture sketch only.
//! This file is not runtime code and is not part of a Cargo target.

use std::num::{NonZeroU32, NonZeroU64};
use std::path::PathBuf;

// ---------- Public aggregate surface ----------

pub struct Studio {
    // Owns the project registry, content-addressed blob store, and selected native backend.
    _private: (),
}

impl Studio {
    /// Opens local state and measures the selected native backend.
    /// This does not read CLI arguments or start a process.
    pub fn open(root: impl Into<PathBuf>, config: StudioConfig) -> Result<Self, StudioError> {
        not_implemented()
    }

    /// Reports compiled and runtime-probed capabilities separately.
    pub fn capabilities(&self) -> Result<CapabilityReport, StudioError> {
        not_implemented()
    }

    /// Creates revision zero with stable-intent replay.
    pub fn create_project(&self, create: CreateProject) -> Result<Project, StudioError> {
        not_implemented()
    }

    /// Opens one persistent aggregate without exposing its storage schema.
    pub fn project(&self, id: ProjectId) -> Result<Project, StudioError> {
        not_implemented()
    }
}

pub struct Project {
    // A cheap handle. Each call opens a bounded aggregate transaction.
    _private: (),
}

impl Project {
    pub fn head(&self, branch: &str) -> Result<ProjectHead, ProjectError> {
        not_implemented()
    }

    pub fn inspect(&self, at: RevisionSelector) -> Result<ProjectSnapshot, ProjectError> {
        not_implemented()
    }

    /// Stages imports, validates the complete candidate snapshot, and appends one revision.
    pub fn commit(&self, command: CommitProject) -> Result<CommitReceipt, ProjectError> {
        not_implemented()
    }

    /// Hides probe, decode, evaluation, mix, encode, mux, and artifact promotion.
    /// Replaying the same intent reconciles the persisted job before work restarts.
    pub fn export(&self, request: ExportRequest) -> Result<ExportOutcome, ProjectError> {
        not_implemented()
    }

    /// Remeasures bytes from the aggregate-owned artifact path.
    pub fn verify_artifact(&self, id: &ArtifactId) -> Result<ArtifactVerification, ProjectError> {
        not_implemented()
    }

    /// Adds immutable evidence. It never changes the bound edit revision.
    pub fn record_review(&self, review: ReviewSubmission) -> Result<ReviewRecord, ProjectError> {
        not_implemented()
    }

    /// Derives gate state from matching evidence. No mutable accepted flag exists.
    pub fn evaluate_policy(
        &self,
        target: ReviewBinding,
        policy: ReviewPolicyId,
    ) -> Result<PolicyEvaluation, ProjectError> {
        not_implemented()
    }
}

// ---------- Identity, clocks, and exact intervals ----------

pub struct ProjectId(pub String);
pub struct BranchId(pub String);
pub struct IntentId(pub String);
pub struct RevisionId(pub Sha256);
pub struct ArtifactId(pub String);
pub struct AssetId(pub Sha256);
pub struct SourceBindingId(pub String);
pub struct TimelineId(pub String);
pub struct TrackId(pub String);
pub struct ItemId(pub String);
pub struct StreamId(pub u32);
pub struct MediaIndexId(pub Sha256);
pub struct ReviewRecordId(pub Sha256);
pub struct ReviewPolicyId(pub String);
pub struct ExportJobId(pub String);
pub struct ExternalAttemptId(pub String);

pub struct Sha256(pub [u8; 32]);

impl ProjectId {
    pub fn parse(value: &str) -> Result<Self, ProjectError> {
        not_implemented()
    }
}

impl IntentId {
    pub fn parse(value: &str) -> Result<Self, ProjectError> {
        not_implemented()
    }
}

impl ImportKey {
    pub fn parse(value: &str) -> Result<Self, ProjectError> {
        not_implemented()
    }
}

impl SourceBindingKey {
    pub fn parse(value: &str) -> Result<Self, ProjectError> {
        not_implemented()
    }
}

impl TimelineId {
    pub fn parse(value: &str) -> Result<Self, ProjectError> {
        not_implemented()
    }
}

pub struct FrameIndex(pub u64);
pub struct FrameBoundary(pub u64);
pub struct FrameCount(pub NonZeroU64);
pub struct SampleIndex(pub u64);
pub struct SampleCount(pub NonZeroU64);
pub struct VideoSampleOrdinal(pub u64);
pub struct VideoSampleCount(pub NonZeroU64);
pub struct MediaTick(pub i64);

/// Always reduced. Numerator and denominator are both positive.
pub struct FrameRate {
    pub numerator: NonZeroU32,
    pub denominator: NonZeroU32,
}

pub struct SampleRate(pub NonZeroU32);

/// Half-open `[start, start + duration)`.
pub struct FrameInterval {
    pub start: FrameIndex,
    pub duration: FrameCount,
}

/// Half-open `[start, start + duration)` in one declared sample rate.
pub struct AudioSampleInterval {
    pub start: SampleIndex,
    pub duration: SampleCount,
}

/// Presentation-order sample ordinals from the asset's immutable sample index.
pub struct VideoSampleInterval {
    pub start: VideoSampleOrdinal,
    pub duration: VideoSampleCount,
}

/// Exact native media clock. Conversion never calls `CMTimeGetSeconds`.
pub struct MediaTimeBase(pub NonZeroU32);

impl FrameRate {
    pub fn new(numerator: u32, denominator: u32) -> Result<Self, ProjectError> {
        not_implemented()
    }
}

impl SampleRate {
    pub fn new(value: u32) -> Result<Self, ProjectError> {
        not_implemented()
    }
}

impl FrameCount {
    pub fn new(value: u64) -> Result<Self, ProjectError> {
        not_implemented()
    }
}

impl SampleCount {
    pub fn new(value: u64) -> Result<Self, ProjectError> {
        not_implemented()
    }
}

impl FrameInterval {
    pub fn new(start: u64, duration: FrameCount) -> Result<Self, ProjectError> {
        not_implemented()
    }
}

impl AudioSampleInterval {
    pub fn new(start: SampleIndex, duration: SampleCount) -> Result<Self, ProjectError> {
        not_implemented()
    }
}

impl VideoSampleInterval {
    pub fn new(start: u64, duration: u64) -> Result<Self, ProjectError> {
        not_implemented()
    }
}

pub struct SampleTiming {
    pub presentation_ordinal: VideoSampleOrdinal,
    pub pts: MediaTick,
    pub dts: Option<MediaTick>,
    pub duration: NonZeroU64,
    pub sync_sample: bool,
}

pub enum ClockRounding {
    Floor,
    Ceil,
    NearestTiesToEven,
}

// ---------- Project revisions ----------

pub struct StudioConfig {
    pub backend: NativeBackend,
    pub limits: ResourceLimits,
}

impl StudioConfig {
    pub fn macos_native() -> Self {
        not_implemented()
    }
}

pub enum NativeBackend {
    MacOsNative,
}

pub struct CreateProject {
    pub project_id: ProjectId,
    pub intent_id: IntentId,
    pub name: String,
    pub settings: ProjectSettings,
}

pub struct ProjectSettings {
    pub canvas: Canvas,
    pub frame_rate: FrameRate,
    pub audio_rate: SampleRate,
    pub working_color: ColorSpace,
}

pub struct Canvas {
    pub width: NonZeroU32,
    pub height: NonZeroU32,
    pub pixel_aspect: RationalU32,
}

impl Canvas {
    pub fn new(width: u32, height: u32) -> Result<Self, ProjectError> {
        not_implemented()
    }
}

pub struct ProjectHead {
    pub branch: BranchId,
    pub revision: RevisionId,
    pub sequence: u64,
}

pub enum RevisionSelector {
    Head(BranchId),
    Exact(RevisionId),
}

/// This immutable document is the semantic source of truth for one revision.
pub struct ProjectSnapshot {
    pub project_id: ProjectId,
    pub revision: RevisionId,
    pub parents: Vec<RevisionId>,
    pub settings: ProjectSettings,
    pub assets: AssetCatalog,
    pub source_bindings: Vec<SourceBinding>,
    pub timelines: Vec<Timeline>,
    pub markers: Vec<ProjectMarker>,
}

pub struct CommitProject {
    pub base_revision: RevisionId,
    pub branch: BranchId,
    pub intent_id: IntentId,
    pub changes: ChangeSet,
}

pub struct ChangeSet {
    /// Import keys can be referenced by later edits in this same change set.
    pub imports: Vec<(ImportKey, AssetImport)>,
    pub edits: Vec<ProjectEdit>,
}

pub struct ChangeSetBuilder {
    _private: (),
}

impl ChangeSet {
    pub fn builder() -> ChangeSetBuilder {
        not_implemented()
    }
}

impl ChangeSetBuilder {
    pub fn import(self, key: ImportKey, import: AssetImport) -> Self {
        not_implemented()
    }

    pub fn bind_source(self, key: SourceBindingKey, source: MovieSourceDraft) -> Self {
        not_implemented()
    }

    pub fn put_timeline(self, timeline: TimelineDraft) -> Self {
        not_implemented()
    }

    pub fn finish(self) -> Result<ChangeSet, ProjectError> {
        not_implemented()
    }
}

pub struct ImportKey(pub String);
pub struct SourceBindingKey(pub String);

pub enum ProjectEdit {
    PutSourceBinding(SourceBindingDraft),
    RemoveSourceBinding(SourceBindingId),
    PutTimeline(TimelineDraft),
    RemoveTimeline(TimelineId),
    PutMarker(ProjectMarker),
    RemoveMarker(String),
}

pub struct CommitReceipt {
    pub project_id: ProjectId,
    pub branch: BranchId,
    pub revision: RevisionId,
    pub parent: RevisionId,
    pub resolved_imports: Vec<(ImportKey, AssetId)>,
    pub resolved_sources: Vec<(SourceBindingKey, SourceBindingId)>,
    pub replayed: bool,
}

// ---------- Assets, representations, and lineage ----------

pub struct ExpectedFile {
    pub sha256: Sha256,
    pub bytes: u64,
}

impl ExpectedFile {
    pub fn sha256(hex: &str, bytes: u64) -> Result<Self, ProjectError> {
        not_implemented()
    }
}

pub struct AssetImport {
    /// A boundary-only locator. The stored asset is addressed by measured content.
    pub locator: LocalAssetLocator,
    pub expected: ExpectedFile,
    pub declared_media_type: Option<String>,
    pub origin: AssetOriginDeclaration,
}

impl AssetImport {
    pub fn local_file(
        path: impl Into<PathBuf>,
        expected: ExpectedFile,
        origin: AssetOriginDeclaration,
    ) -> Self {
        not_implemented()
    }
}

pub enum LocalAssetLocator {
    File(PathBuf),
}

pub enum AssetOriginDeclaration {
    SourceOriginal {
        external_source_id: String,
    },
    GeneratedOriginal {
        attempt_id: ExternalAttemptId,
        workflow_sha256: Sha256,
        input_lineage: Vec<AssetRangeDraft>,
        provider_receipt_sha256: Sha256,
    },
    Derived {
        operation: TransformationRecipe,
        inputs: Vec<AssetRangeDraft>,
        receipt_sha256: Sha256,
    },
    FontOriginal {
        license_record_sha256: Option<Sha256>,
    },
}

impl AssetOriginDeclaration {
    pub fn source_original(external_source_id: &str) -> Result<Self, ProjectError> {
        not_implemented()
    }

    pub fn generated_original(
        attempt_id: &str,
        workflow_sha256: Sha256,
        input_lineage: impl IntoIterator<Item = &'static str>,
        provider_receipt_sha256: Sha256,
    ) -> Result<Self, ProjectError> {
        not_implemented()
    }
}

pub struct AssetCatalog {
    pub assets: Vec<MediaAsset>,
    pub lineage: LineageGraph,
}

pub struct MediaAsset {
    pub id: AssetId,
    pub byte_count: u64,
    pub media_type: String,
    pub streams: Vec<MediaStream>,
    pub probe: NativeProbeReceipt,
}

pub enum MediaStream {
    Video(VideoStream),
    Audio(AudioStream),
    Image(ImageStream),
    Font(FontStream),
}

pub struct VideoStream {
    pub id: StreamId,
    pub codec: CodecId,
    pub coded_size: Canvas,
    pub clean_aperture: RectI32,
    pub orientation: Orientation,
    pub color: ColorDescription,
    pub time_base: MediaTimeBase,
    pub sample_index: MediaIndexId,
    pub sample_count: VideoSampleCount,
}

pub struct AudioStream {
    pub id: StreamId,
    pub codec: CodecId,
    pub sample_rate: SampleRate,
    pub channels: ChannelLayout,
    pub sample_count: SampleCount,
}

pub struct ImageStream;
pub struct FontStream;

pub struct SourceBinding {
    pub id: SourceBindingId,
    /// The original bytes that establish source authority.
    pub authority: AssetId,
    /// The exact bytes selected for native decode.
    pub representation: AssetId,
    pub mapping: RepresentationMapping,
}

pub struct SourceBindingDraft {
    pub key: SourceBindingKey,
    pub authority: AssetRefDraft,
    pub representation: AssetRefDraft,
    pub mapping: RepresentationMappingDraft,
}

pub struct MovieSourceDraft {
    pub authority: AssetRefDraft,
    pub representation: AssetRefDraft,
    pub mapping: RepresentationMappingDraft,
}

impl MovieSourceDraft {
    pub fn native(asset: ImportKey) -> Self {
        not_implemented()
    }

    pub fn verified_representation(
        authority: AssetRefDraft,
        representation: AssetRefDraft,
        mapping: Vec<SampleRangeMap>,
        verification_receipt_sha256: Sha256,
    ) -> Self {
        not_implemented()
    }
}

pub enum AssetRefDraft {
    Stored(AssetId),
    Imported(ImportKey),
}

pub enum RepresentationMapping {
    Identity,
    VerifiedSampleMap {
        ranges: Vec<SampleRangeMap>,
        verification: ReviewRecordId,
    },
}

pub enum RepresentationMappingDraft {
    Identity,
    VerifiedSampleMap {
        ranges: Vec<SampleRangeMap>,
        verification_receipt_sha256: Sha256,
    },
}

pub struct SampleRangeMap {
    pub authority: VideoSampleInterval,
    pub representation: VideoSampleInterval,
}

pub struct LineageGraph {
    /// Acyclic edges from immutable inputs to immutable outputs.
    pub derivations: Vec<Derivation>,
}

pub struct Derivation {
    pub output: AssetId,
    pub operation: TransformationRecipe,
    pub inputs: Vec<AssetRange>,
    pub receipt_sha256: Sha256,
}

pub struct AssetRange {
    pub asset: AssetId,
    pub stream: StreamId,
    pub range: MediaRange,
}

pub struct AssetRangeDraft {
    pub asset: AssetRefDraft,
    pub stream: StreamId,
    pub range: MediaRange,
}

pub enum MediaRange {
    Video(VideoSampleInterval),
    Audio(AudioSampleInterval),
    WholeAsset,
}

pub enum TransformationRecipe {
    SourceFrameStyleTransfer {
        model_or_service: String,
        prompt_sha256: Sha256,
    },
    TwoAnchorVideoGeneration {
        workflow_sha256: Sha256,
    },
    Inpaint {
        mask_asset: AssetId,
    },
    AspectNormalize {
        aperture: RectI32,
        target: Canvas,
    },
    Upscale {
        method: String,
        scale: RationalU32,
    },
    Custom {
        kind: String,
        parameters_sha256: Sha256,
    },
}

// ---------- Timeline, source timing, and composition ----------

pub struct Timeline {
    pub id: TimelineId,
    pub extent: TimelineExtent,
    /// Bottom to top. Track order is semantic and hash-significant.
    pub video_tracks: Vec<VideoTrack>,
    pub audio_tracks: Vec<AudioTrack>,
    pub marker_tracks: Vec<MarkerTrack>,
}

/// Draft-only timeline. It may contain change-set import and source aliases.
/// Commit resolution converts it into the stored `Timeline` above.
pub struct TimelineDraft {
    _private: (),
}

pub struct TimelineBuilder {
    _private: (),
}

pub struct VideoClip {
    _private: (),
}

pub struct AudioClip {
    _private: (),
}

impl Timeline {
    pub fn builder(id: TimelineId) -> TimelineBuilder {
        not_implemented()
    }
}

impl TimelineBuilder {
    pub fn video_track(self, id: &str, z_index: i32) -> Self {
        not_implemented()
    }

    pub fn audio_track(self, id: &str, mix_order: i32) -> Self {
        not_implemented()
    }

    pub fn place<T>(self, item: T) -> Result<Self, ProjectError> {
        not_implemented()
    }

    pub fn finish(self) -> Result<TimelineDraft, ProjectError> {
        not_implemented()
    }
}

impl VideoClip {
    pub fn movie(
        id: &str,
        interval: FrameInterval,
        source: SourceBindingKey,
        source_samples: VideoSampleInterval,
    ) -> Self {
        not_implemented()
    }

    pub fn use_source_presentation_timestamps(self) -> Result<Self, ProjectError> {
        not_implemented()
    }
}

impl AudioClip {
    pub fn media(
        id: &str,
        timeline_range: AudioSampleInterval,
        source: ImportKey,
        source_range: AudioSampleInterval,
    ) -> Self {
        not_implemented()
    }
}

pub struct TimelineExtent {
    pub video: FrameInterval,
    pub audio: AudioSampleInterval,
    pub end_alignment: ClockRounding,
}

pub struct VideoTrack {
    pub id: TrackId,
    pub z_index: i32,
    pub enabled: bool,
    /// Items on one track cannot overlap. Layering uses separate tracks.
    pub items: Vec<VisualItem>,
}

pub struct AudioTrack {
    pub id: TrackId,
    pub mix_order: i32,
    pub enabled: bool,
    pub items: Vec<AudioItem>,
    pub gain: Animated<Decibels>,
    pub pan: Animated<UnitScalar>,
}

pub struct MarkerTrack {
    pub id: TrackId,
    pub namespace: String,
    pub markers: Vec<TimelineMarker>,
}

pub struct VisualItem {
    pub id: ItemId,
    pub interval: FrameInterval,
    pub content: VisualContent,
    pub transform: Animated<Transform2D>,
    pub opacity: Animated<UnitScalar>,
    pub blend: BlendMode,
    pub masks: MaskStack,
    pub color: ColorPipeline,
}

pub enum VisualContent {
    Movie(VideoMediaUse),
    Still(ImageUse),
    Text(TextLayer),
    Solid(ColorValue),
    NestedTimeline(TimelineId),
}

pub struct VideoMediaUse {
    pub source: SourceBindingId,
    pub stream: StreamId,
    pub allowed_source: VideoSampleInterval,
    pub retime: RetimeMap,
    pub sampling: VideoSampling,
}

pub struct RetimeMap {
    /// Knots map integer output frame boundaries to integer source ticks.
    /// Linear interpolation between knots uses checked rational arithmetic.
    pub source_time_base: MediaTimeBase,
    pub knots: Vec<RetimeKnot>,
}

pub struct RetimeKnot {
    pub at: FrameBoundary,
    pub source_tick: MediaTick,
}

pub enum VideoSampling {
    HoldPrevious,
    Nearest,
    LinearBlend,
    OpticalFlow { implementation: CapabilityId },
}

pub struct AudioItem {
    pub id: ItemId,
    pub timeline_range: AudioSampleInterval,
    pub source: AssetId,
    pub stream: StreamId,
    pub source_range: AudioSampleInterval,
    pub retime: AudioRetime,
    pub gain: Animated<Decibels>,
    pub pan: Animated<UnitScalar>,
}

pub enum AudioRetime {
    Identity,
    Resample {
        ratio: RationalI64,
    },
    TimeStretch {
        ratio: RationalI64,
        algorithm: CapabilityId,
    },
}

pub struct ImageUse {
    pub asset: AssetId,
}

pub struct MaskStack {
    pub masks: Vec<Mask>,
}

pub struct Mask {
    pub operation: MaskOperation,
    pub inverted: bool,
    pub path: Animated<VectorPath>,
    pub feather_pixels: Animated<FiniteF32>,
    pub opacity: Animated<UnitScalar>,
}

pub enum MaskOperation {
    Add,
    Subtract,
    Intersect,
}

pub struct VectorPath {
    pub closed: bool,
    pub points: Vec<BezierPoint>,
}

pub struct BezierPoint {
    pub position: Point2,
    pub in_handle: Point2,
    pub out_handle: Point2,
}

pub struct ColorPipeline {
    pub input: ColorSpace,
    pub nodes: Vec<ColorNode>,
    pub output: ColorSpace,
}

pub enum ColorNode {
    Matrix3x3([FiniteF32; 9]),
    LiftGammaGain { lift: Vec3, gamma: Vec3, gain: Vec3 },
    Exposure(FiniteF32),
    Saturation(FiniteF32),
    Curves(CurveSet),
    Lut3d { asset: AssetId },
}

pub struct TextLayer {
    /// Exact UTF-8 is preserved. No normalization or transliteration is implicit.
    pub text: String,
    pub text_sha256: Sha256,
    pub language: Option<String>,
    pub script: Option<String>,
    pub direction: TextDirection,
    /// Every font is a content-addressed project asset. Missing glyphs are errors.
    pub fonts: Vec<AssetId>,
    pub spans: Vec<TextSpan>,
    pub layout: TextLayout,
    pub fill: Animated<ColorValue>,
}

pub enum TextDirection {
    Auto,
    LeftToRight,
    RightToLeft,
}

pub struct TextSpan;
pub struct TextLayout;

pub struct Animated<T> {
    pub default: T,
    pub keys: Vec<Keyframe<T>>,
}

pub struct Keyframe<T> {
    pub at: FrameIndex,
    pub value: T,
    pub interpolation: Interpolation,
}

pub enum Interpolation {
    Hold,
    Linear,
    CubicBezier {
        out_tangent: Point2,
        in_tangent: Point2,
    },
}

// ---------- Export and artifact truth ----------

pub struct ExportRequest {
    pub intent_id: IntentId,
    pub revision: RevisionId,
    pub timeline: TimelineId,
    pub range: ExportRange,
    pub profile: MovieProfile,
    /// Optional technical gate. Creative acceptance remains post-export evidence.
    pub required_policy: Option<ReviewPolicyId>,
}

pub enum ExportRange {
    WholeTimeline,
    Frames(FrameInterval),
}

impl ExportRange {
    pub fn whole_timeline() -> Self {
        Self::WholeTimeline
    }
}

pub struct MovieProfile {
    pub container: MovieContainer,
    pub canvas: Canvas,
    pub frame_rate: FrameRate,
    pub video: VideoEncoding,
    pub audio_rate: SampleRate,
    pub audio: AudioEncoding,
    pub color: ColorDescription,
}

impl MovieProfile {
    pub fn h264_aac_mp4(canvas: Canvas, frame_rate: FrameRate, audio_rate: SampleRate) -> Self {
        not_implemented()
    }
}

pub enum MovieContainer {
    Mp4,
    QuickTime,
}

pub enum VideoEncoding {
    H264 { profile: String, bitrate: u64 },
    ProRes { flavor: String },
}

pub enum AudioEncoding {
    Aac {
        bitrate: u64,
        channels: ChannelLayout,
    },
    LinearPcm {
        bits_per_sample: u8,
        channels: ChannelLayout,
    },
}

pub enum ExportOutcome {
    Completed(ArtifactReceipt),
    Paused {
        job: ExportJobId,
        reason: PauseReason,
    },
    Failed {
        job: ExportJobId,
        error: ExportFailure,
    },
}

impl ExportOutcome {
    pub fn completed(self) -> Result<ArtifactReceipt, ProjectError> {
        not_implemented()
    }
}

pub struct ArtifactReceipt {
    pub artifact_id: ArtifactId,
    pub project_id: ProjectId,
    pub revision: RevisionId,
    pub project_sha256: Sha256,
    pub timeline: TimelineId,
    pub intent_id: IntentId,
    pub request_sha256: Sha256,
    pub source_closure_manifest_sha256: Sha256,
    pub renderer: NativeBuildIdentity,
    pub output_sha256: Sha256,
    pub output_bytes: u64,
    pub video: MeasuredVideo,
    pub audio: MeasuredAudio,
}

impl ArtifactReceipt {
    pub fn binding(&self) -> ReviewBinding {
        not_implemented()
    }
}

pub struct MeasuredVideo {
    pub frame_count: FrameCount,
    pub frame_rate: FrameRate,
    pub dimensions: Canvas,
    pub codec: CodecId,
    pub color: ColorDescription,
}

pub struct MeasuredAudio {
    pub timeline_samples: SampleCount,
    pub encoded_samples: SampleCount,
    pub encoder_trim_start: SampleCountOrZero,
    pub encoder_trim_end: SampleCountOrZero,
    pub sample_rate: SampleRate,
    pub channels: ChannelLayout,
    pub codec: CodecId,
}

pub struct ArtifactVerification {
    pub receipt: ArtifactReceipt,
    pub outcome: VerificationOutcome,
    pub measured_at_utc: String,
}

// ---------- Review evidence ----------

pub struct ReviewBinding {
    pub project_id: ProjectId,
    pub revision: RevisionId,
    pub project_sha256: Sha256,
    pub artifact_id: ArtifactId,
    pub artifact_sha256: Sha256,
    pub renderer_build_sha256: Sha256,
}

pub struct ReviewSubmission {
    pub intent_id: IntentId,
    pub target: ReviewBinding,
    pub actor: ReviewActor,
    pub policy_version: Option<ReviewPolicyId>,
    pub evidence: ReviewEvidence,
}

impl ReviewSubmission {
    pub fn full_playback(
        intent_id: IntentId,
        target: ReviewBinding,
        actor: ReviewActor,
        observation: PlaybackObservation,
    ) -> Self {
        not_implemented()
    }

    pub fn full_listening(
        intent_id: IntentId,
        target: ReviewBinding,
        actor: ReviewActor,
        observation: ListeningObservation,
    ) -> Self {
        not_implemented()
    }
}

pub enum ReviewEvidence {
    Measurement(MeasurementObservation),
    FrameInspection(FrameInspectionObservation),
    Playback(PlaybackObservation),
    Listening(ListeningObservation),
    Creative(CreativeObservation),
}

pub struct MeasurementObservation {
    pub checks: Vec<TechnicalCheck>,
    pub outcome: ObservationOutcome,
}

pub struct FrameInspectionObservation {
    pub frames: Vec<FrameIndex>,
    pub outcome: ObservationOutcome,
}

pub struct PlaybackObservation {
    pub coverage: Vec<FrameInterval>,
    pub speed: PlaybackSpeed,
    pub continuous: bool,
    pub outcome: ObservationOutcome,
}

impl PlaybackObservation {
    pub fn watched_normal_speed(coverage: FrameInterval, outcome: ObservationOutcome) -> Self {
        not_implemented()
    }
}

pub struct ListeningObservation {
    pub coverage: Vec<AudioSampleInterval>,
    pub monitoring: MonitoringPath,
    pub outcome: ObservationOutcome,
}

impl ListeningObservation {
    pub fn heard(coverage: AudioSampleInterval, outcome: ObservationOutcome) -> Self {
        not_implemented()
    }
}

pub struct CreativeObservation {
    pub scope: CreativeScope,
    pub criteria: Vec<CriterionResult>,
    pub outcome: ObservationOutcome,
}

pub enum ObservationOutcome {
    Pass,
    Fail { defects: Vec<TimedDefect> },
    Inconclusive { reason: String },
}

pub struct ReviewRecord {
    pub id: ReviewRecordId,
    pub submission: ReviewSubmission,
    pub recorded_at_utc: String,
}

pub struct PolicyEvaluation {
    pub target: ReviewBinding,
    pub policy: ReviewPolicyId,
    pub gates: Vec<GateEvaluation>,
    pub state: GateState,
}

impl PolicyEvaluation {
    pub fn is_pending_until_every_required_gate_passes(&self) -> bool {
        not_implemented()
    }
}

pub enum GateState {
    Satisfied,
    Pending,
    Failed,
}

pub struct GateEvaluation {
    pub gate: String,
    pub state: GateState,
    pub matching_evidence: Vec<ReviewRecordId>,
    pub missing_or_failed_reason: Option<String>,
}

// ---------- Internal aggregate and recovery shape ----------

pub(crate) struct ProjectAggregate {
    pub id: ProjectId,
    pub revisions: RevisionStore,
    pub heads: BranchHeads,
    pub intents: IntentStore,
    pub assets: ContentAddressedStore,
    pub jobs: ExportJobStore,
    pub artifacts: ArtifactStore,
    pub reviews: ReviewStore,
}

impl ProjectAggregate {
    /// Stages bytes first. One database transaction then checks replay, compares the
    /// branch head, validates the candidate snapshot, appends the revision, and records
    /// the intent result. Orphaned content-addressed blobs are safe to collect later.
    pub(crate) fn apply_commit(
        &mut self,
        command: CommitProject,
        platform: &dyn MediaPlatform,
    ) -> Result<CommitReceipt, ProjectError> {
        not_implemented()
    }

    /// Claims a fenced job in a short transaction, releases the database lock, renders,
    /// verifies staged bytes, then promotes them only if the fencing epoch still matches.
    pub(crate) fn execute_export(
        &mut self,
        request: ExportRequest,
        platform: &dyn MediaPlatform,
        cancellation: &dyn Cancellation,
    ) -> Result<ExportOutcome, ProjectError> {
        not_implemented()
    }
}

pub(crate) struct ExportJobRecord {
    pub id: ExportJobId,
    pub intent_id: IntentId,
    pub request_sha256: Sha256,
    pub revision: RevisionId,
    pub project_sha256: Sha256,
    pub renderer: NativeBuildIdentity,
    pub state: ExportJobState,
}

pub(crate) enum ExportJobState {
    Prepared,
    Running {
        lease: FencedLease,
    },
    Finalizing {
        lease: FencedLease,
        staged_sha256: Sha256,
    },
    Completed {
        receipt: ArtifactReceipt,
    },
    Failed {
        failure: ExportFailure,
    },
    Cancelled,
}

pub(crate) struct FencedLease {
    pub owner: String,
    pub epoch: u64,
    pub expires_at_utc: String,
}

/// This interface is private to the native implementation.
/// AVFoundation and Core Media types never cross it.
pub(crate) trait MediaPlatform {
    fn capabilities(&self) -> Result<NativeCapabilitySet, MediaError>;
    fn probe(&self, bytes: &OwnedBlob) -> Result<NativeProbeReceipt, MediaError>;
    fn decode_video(&self, request: DecodeVideoRequest) -> Result<VideoFrameStream, MediaError>;
    fn decode_audio(&self, request: DecodeAudioRequest) -> Result<AudioBlockStream, MediaError>;
    fn write_movie(&self, request: WriteMovieRequest) -> Result<StagedMovie, MediaError>;
    fn reopen_movie(&self, movie: &StagedMovie) -> Result<MeasuredMovie, MediaError>;
}

pub(crate) trait Cancellation {
    fn is_cancelled(&self) -> bool;
}

// ---------- Capability and external-job boundaries ----------

pub struct CapabilityReport {
    pub engine: NativeBuildIdentity,
    pub compiled: Vec<Capability>,
    pub runtime: Vec<RuntimeCapability>,
    pub unavailable: Vec<UnavailableCapability>,
}

pub struct NativeBuildIdentity {
    pub binary_sha256: Sha256,
    pub crate_lock_sha256: Sha256,
    pub target: String,
    pub os_build: String,
    pub framework_versions: Vec<String>,
}

pub struct CapabilityId(pub String);
pub struct Capability;
pub struct RuntimeCapability;
pub struct UnavailableCapability;

/// This belongs in the separate Effect/Herdr adapter store.
/// The native project aggregate sees only a completed receipt and verified bytes.
pub enum ExternalGpuAttemptState {
    Prepared { source_snapshot_sha256: Sha256 },
    SubmissionUncertain { request_sha256: Sha256 },
    Bound { provider_job_id: String },
    Collecting { provider_job_id: String },
    TransferVerified { output_sha256: Sha256, bytes: u64 },
    Failed { reason: String, retry_allowed: bool },
    Closed,
}

// ---------- Abbreviated supporting values ----------

pub struct RationalU32(pub NonZeroU32, pub NonZeroU32);
pub struct RationalI64(pub i64, pub NonZeroU64);
pub struct FiniteF32(pub f32);
pub struct UnitScalar(pub FiniteF32);
pub struct Decibels(pub FiniteF32);
pub struct SampleCountOrZero(pub u64);
pub struct Point2(pub FiniteF32, pub FiniteF32);
pub struct Vec3(pub FiniteF32, pub FiniteF32, pub FiniteF32);
pub struct Transform2D;
pub struct CurveSet;
pub struct ColorValue;
pub struct ColorSpace;
pub struct ColorDescription;
pub struct ChannelLayout;
pub struct CodecId(pub String);
pub struct RectI32;
pub struct Orientation;
pub struct BlendMode;
pub struct TimelineMarker;
pub struct ProjectMarker;
pub struct NativeProbeReceipt;
pub struct ResourceLimits;
pub struct PauseReason;
pub struct ExportFailure;
pub struct ReviewActor;
impl ReviewActor {
    pub fn agent(name: &str, build_sha256: &str) -> Result<Self, ProjectError> {
        not_implemented()
    }
}
pub struct PlaybackSpeed;
pub struct MonitoringPath;
pub struct CreativeScope;
pub struct CriterionResult;
pub struct TechnicalCheck;
pub struct TimedDefect;
pub struct VerificationOutcome;
pub struct RevisionStore;
pub struct BranchHeads;
pub struct IntentStore;
pub struct ContentAddressedStore;
pub struct ExportJobStore;
pub struct ArtifactStore;
pub struct ReviewStore;
pub struct NativeCapabilitySet;
pub struct OwnedBlob;
pub struct DecodeVideoRequest;
pub struct DecodeAudioRequest;
pub struct WriteMovieRequest;
pub struct VideoFrameStream;
pub struct AudioBlockStream;
pub struct StagedMovie;
pub struct MeasuredMovie;
pub struct StudioError;
pub struct ProjectError;
pub struct MediaError;

fn not_implemented<T>() -> T {
    unimplemented!("architecture sketch")
}
