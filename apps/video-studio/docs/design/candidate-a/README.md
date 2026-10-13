# Candidate A: persistent project aggregate

This candidate makes one persistent `Project` aggregate the authority for editing state.
Every edit creates an immutable revision.
The aggregate also owns intent replay, asset lineage, render jobs, artifacts, and review evidence.

The Rust library is independently usable.
The direct CLI adapts JSON and process lifetime to the same library.
Effect application adapters remain outside the native editor.

## Usage first

### Create and edit a real movie project

The caller submits one atomic change set.
The aggregate hashes and probes imports before it commits the revision.
Stored revisions contain asset identities, never caller file paths.

```rust,no_run
use video_studio::{
    AssetImport, AssetOriginDeclaration, AudioClip, AudioSampleInterval, Canvas,
    ChangeSet, CommitProject, CreateProject, ExpectedFile, FrameCount, FrameInterval,
    FrameRate, ImportKey, IntentId, MovieSourceDraft, ProjectId, ProjectSettings,
    SampleCount, SampleIndex, SampleRate, SourceBindingKey, Studio, StudioConfig,
    Timeline, TimelineId, VideoClip, VideoSampleInterval,
};

let studio = Studio::open("./state", StudioConfig::macos_native())?;
let project = studio.create_project(CreateProject {
    project_id: ProjectId::parse("panja-native-proof")?,
    intent_id: IntentId::parse("create-panja-v1")?,
    name: "Panja native proof".into(),
    settings: ProjectSettings {
        canvas: Canvas::new(1920, 1080)?,
        frame_rate: FrameRate::new(24, 1)?,
        audio_rate: SampleRate::new(48_000)?,
        working_color: "rec709-scene-linear".parse()?,
    },
})?;

let movie = ImportKey::parse("real-movie")?;
let song = ImportKey::parse("song-master")?;
let movie_source = SourceBindingKey::parse("real-movie-source")?;

let timeline = Timeline::builder(TimelineId::parse("main")?)
    .video_track("picture", 0)
    .place(VideoClip::movie(
        "real-range",
        FrameInterval::new(0, FrameCount::new(48)?)?,
        movie_source.clone(),
        VideoSampleInterval::new(0, 48)?,
    )
    .use_source_presentation_timestamps()?)?
    .audio_track("song", 0)
    .place(AudioClip::media(
        "song-range",
        AudioSampleInterval::new(SampleIndex(0), SampleCount::new(96_000)?)?,
        song.clone(),
        AudioSampleInterval::new(SampleIndex(0), SampleCount::new(96_000)?)?,
    ))?
    .finish()?;

let committed = project.commit(CommitProject {
    base_revision: project.head("main")?.revision,
    branch: "main".parse()?,
    intent_id: IntentId::parse("bind-real-source-v1")?,
    changes: ChangeSet::builder()
        .import(
            movie.clone(),
            AssetImport::local_file(
                "/path/to/ePOglweqy7o.mp4",
                ExpectedFile::sha256(
                    "a2247e96ab4335eb6b365ef52b6203e53377c6cf317ebb2e156789e6bd470b7f",
                    11_620_016,
                )?,
                AssetOriginDeclaration::source_original("panja-reference-ePOglweqy7o")?,
            ),
        )
        .import(
            song.clone(),
            AssetImport::local_file(
                "/path/to/panda-r12-master-with-melodic-reprise-a02.wav",
                ExpectedFile::sha256(
                    "cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8",
                    78_624_044,
                )?,
                AssetOriginDeclaration::source_original("canonical-song-candidate")?,
            ),
        )
        .bind_source(movie_source, MovieSourceDraft::native(movie))
        .put_timeline(timeline)
        .finish()?,
})?;

println!("revision: {}", committed.revision);
# Ok::<(), Box<dyn std::error::Error>>(())
```

`ImportKey` and `SourceBindingKey` exist only inside one change set.
The commit result returns their resolved content identities.
The aggregate stores the source movie's sample index and measured stream properties.

The example follows decoded presentation timestamps at 1/24 second intervals.
The source's reported nominal rate is 12 fps and is not timing authority.
No floating-point seconds identify the edit.

### Bind a generated original without losing its source ancestry

The Herdr or provider adapter reconciles its job before this call.
The native editor receives an immutable generated original and its completed attempt receipt.

```rust,no_run
let anime_original = ImportKey::parse("anime-original-w03")?;

let committed = project.commit(CommitProject {
    base_revision: project.head("main")?.revision,
    branch: "main".parse()?,
    intent_id: IntentId::parse("import-w03-generated-original-v1")?,
    changes: ChangeSet::builder()
        .import(
            anime_original,
            AssetImport::local_file(
                "/verified-transfer/W03-original.mp4",
                ExpectedFile::sha256("<measured-sha256>", 42_000_000)?,
                AssetOriginDeclaration::generated_original(
                    "herdr-attempt-0187",
                    "<workflow-sha256>".parse()?,
                    ["source-anchor-first", "source-anchor-last"],
                    "<provider-receipt-sha256>".parse()?,
                )?,
            ),
        )
        .finish()?,
})?;
```

The generated original stays immutable.
Trims, cleanup, aspect normalization, and upscales become separate derived assets.
Each derived asset cites exact input ranges and a transformation receipt.

### Export one source-bound movie

The caller requests an outcome, not internal decode or render stages.
The aggregate binds the job to an immutable revision before it starts work.

```rust,no_run
let outcome = project.export(ExportRequest {
    intent_id: IntentId::parse("panja-native-main-mp4-v1")?,
    revision: committed.revision,
    timeline: TimelineId::parse("main")?,
    range: ExportRange::whole_timeline(),
    profile: MovieProfile::h264_aac_mp4(
        Canvas::new(1920, 1080)?,
        FrameRate::new(24, 1)?,
        SampleRate::new(48_000)?,
    ),
    required_policy: None,
})?;

let receipt = outcome.completed()?;
project.verify_artifact(&receipt.artifact_id)?;
```

The same export intent is safe after interruption.
The aggregate inspects the persisted job and output before it resumes or recomputes.
It never selects another codec or renderer as a fallback.

### Record timed review evidence

Technical verification and perceptual review use different evidence variants.
Neither can be converted into the other.

```rust,no_run
let review = project.record_review(ReviewSubmission::full_playback(
    IntentId::parse("review-panja-playback-v1")?,
    receipt.binding(),
    ReviewActor::agent("video-director", "<reviewer-build-sha256>")?,
    PlaybackObservation::watched_normal_speed(
        FrameInterval::new(0, receipt.video.frame_count)?,
        ObservationOutcome::Pass,
    ),
))?;

let listening = project.record_review(ReviewSubmission::full_listening(
    IntentId::parse("review-panja-listening-v1")?,
    receipt.binding(),
    ReviewActor::agent("video-director", "<reviewer-build-sha256>")?,
    ListeningObservation::heard(
        AudioSampleInterval::new(SampleIndex(0), receipt.audio.timeline_samples)?,
        ObservationOutcome::Pass,
    ),
))?;

let status = project.evaluate_policy(receipt.binding(), "music-export-v1".parse()?)?;
assert!(status.is_pending_until_every_required_gate_passes());
```

A failed or incomplete observation remains evidence of failure or missing coverage.
It cannot satisfy a gate.
Evidence for an older revision or another output hash also cannot satisfy the gate.

## Direct agent CLI

The CLI owns JSON framing, schema negotiation, signals, deadlines, and exit codes.
The library owns all project and media semantics.

```sh
video-studio capabilities --json
video-studio call project.create --state ./state --request create.json
video-studio call project.commit --state ./state --request bind-and-edit.json
video-studio call project.export --state ./state --request export.json
video-studio call artifact.verify --state ./state --request verify.json
video-studio call review.record --state ./state --request watched.json
```

If export is interrupted, run the same `project.export` request again.
Keep its project, intent, revision, profile, and request bytes unchanged.

The CLI never launches a renderer subprocess.
It calls the Rust library in process.

## Application boundary

An Effect adapter may authenticate tenants and execute the CLI on a native worker.
The adapter owns Herdr job submission, provider reconciliation, and process supervision.

```ts
const completed = yield* GpuJobs.reconcileBeforeRetry(generationIntent);
const original = yield* GpuJobs.verifyTransferredOriginal(completed);

yield* NativeVideoStudio.commitGeneratedOriginal({
  tenantProject,
  expectedRevision,
  intentId: "import-w03-generated-original-v1",
  original,
  attemptReceipt: completed.receipt,
});
```

`reconcileBeforeRetry` must inspect the existing queue, history, and saved submission intent.
An absent HTTP response does not authorize another GPU submission.

The adapter does not query the native editor's SQLite database.
It uses the versioned CLI contract and verifies the returned native receipt.

## Design package

- [`types.rs`](types.rs) sketches the public types and load-bearing internal records.
- [`modules.md`](modules.md) assigns ownership and dependency direction.
- [`native-media-feasibility.md`](native-media-feasibility.md) grounds the macOS movie and audio path.
- [`rationale.md`](rationale.md) applies the architect rationale template.
- [`red-flag-screen.md`](red-flag-screen.md) screens the candidate against the required design red flags.
