# Native mastering Candidate A: one closed profile, one private format authority

Status: design only. No direct ProRes write or decoded fidelity result exists yet.

## Caller usage

The caller selects one closed profile. The caller does not choose a container, codec, bitrate, PCM layout, or filename extension.

```json
{
  "intent": "export-masks-synthetic-color-master-a01",
  "revision": "a7bc52df330b5a9d7e0ef8e8fe71b47963d308be393eeefa0e00d0cfbbfc24dd",
  "timeline": "picture-masks",
  "profile": {
    "kind": "native_color_master_v1"
  }
}
```

The same request document goes to `Project::prepare_export` and `Project::export`.

```rust
let request: ExportRequest = serde_json::from_slice(&request_bytes)?;

let prepared = project.prepare_export(request.clone())?;
assert_eq!(prepared.plan.schema, 6); // Masks still determine the plan schema.

let exported = project.export(request)?;
assert_eq!(exported.receipt.artifact.schema, 3);
assert_eq!(
    exported.receipt.artifact.output_path.extension().and_then(|v| v.to_str()),
    Some("mov"),
);
```

The result remains behind the existing verification operation.

```rust
let verified = project.verify_export(EntityId::parse(
    "export-masks-synthetic-color-master-a01",
)?)?;

assert!(verified.replayed);
assert_eq!(verified.verification.technical.video_track.codec, "ap4h");
assert_eq!(verified.verification.technical.audio_track.codec, "lpcm");
```

Cancellation and cleanup also keep their current public operations. A controller can cancel while another owner runs `export`.

```rust
let cancelled = project.cancel_export(EntityId::parse(
    "export-masks-synthetic-color-master-a01",
)?)?;
assert_eq!(cancelled.state, "cancellation_requested");

let cleanup = project.reconcile_export_staging()?;
```

The caller must use a new intent when changing from `h264_aac_mp4` to `native_color_master_v1`.

The request hash already makes a profile change conflict with an existing intent.

## Public contract

`native_color_master_v1` is permanently defined as one exact opaque mastering format:

- QuickTime movie container;
- Apple ProRes 4444 video;
- opaque 32BGRA writer input;
- 24-bit signed integer PCM;
- little-endian interleaved stereo at 48 kHz;
- `.mov` stage and artifact names;
- no caller bitrate or encoder controls.

The `v1` name makes this mapping immutable. A different mapping requires another profile variant.

The public Project surface does not change.

The implementation remains direct, in-process AVFoundation. It adds no renderer subprocess, FFmpeg, libav, or predecessor runtime.

```rust
impl Project {
    pub fn prepare_export(&self, request: ExportRequest) -> Result<PreparedExport> {
        unimplemented!("existing operation; compile and store the selected profile")
    }

    pub fn export(&self, request: ExportRequest) -> Result<ExportResult> {
        unimplemented!("existing operation; derive and execute the private format contract")
    }

    pub fn verify_export(&self, intent: EntityId) -> Result<ExportResult> {
        unimplemented!("existing operation; derive the same contract from the stored plan")
    }

    pub fn cancel_export(&self, intent: EntityId) -> Result<ExportCancellation> {
        unimplemented!("existing cancellation fence")
    }

    pub fn reconcile_export_staging(&self) -> Result<StagingReconciliation> {
        unimplemented!("existing cleanup operation; derive the stage payload name per plan")
    }
}
```

## Type sketch

### Caller-visible profile

```rust
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum MovieProfile {
    H264AacMp4 {
        video_bitrate: u32,
        audio_bitrate: u32,
    },
    NativeColorMasterV1,
}
```

The unit variant accepts exactly `{"kind":"native_color_master_v1"}`. Extra settings are rejected at deserialization.

### Receipt observations

Existing schema-2 receipts omit every new optional field. Their serialized bytes remain unchanged.

```rust
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NativeFormatEvidence {
    pub schema: u32,                         // 1
    pub container: ObservedContainer,        // actual file bytes
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum ObservedContainer {
    QuickTime {
        major_brand: String,
        compatible_brands: Vec<String>,
    },
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PcmEncodingEvidence {
    pub bits_per_channel: u32,
    pub signed_integer: bool,
    pub floating_point: bool,
    pub big_endian: bool,
    pub non_interleaved: bool,
    pub bytes_per_frame: u32,
    pub frames_per_packet: u32,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Pcm24ComparisonEvidence {
    pub compared_sample_frames: u64,
    pub maximum_code_delta: u32,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NativeTrackEvidence {
    // Existing fields remain in their current order.
    pub codec: String,
    pub sample_buffers: u64,
    pub raw_sample_pts_start: MediaTime,
    pub raw_sample_pts_end: MediaTime,
    pub audio_layout: Option<(u32, u32)>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub pcm_encoding: Option<PcmEncodingEvidence>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NativeMeasurements {
    // Existing fields remain in their current order.
    pub video_frames: u64,
    pub audio_sample_frames: u64,
    pub width: u32,
    pub height: u32,
    pub full_video_decode: bool,
    pub audio_correlation: [f64; 2],
    pub video_track: NativeTrackEvidence,
    pub audio_track: NativeTrackEvidence,
    pub streaming_audio: Option<StreamingAudioEvidence>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub format: Option<NativeFormatEvidence>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub pcm24_comparison: Option<Pcm24ComparisonEvidence>,
}
```

The implementation appends both fields after existing fields. Schema-2 H.264 measurements set them to `None`.

Schema-3 receipts require both appended fields and `audio_track.pcm_encoding`. Fresh verification compares all three exactly.

### Private format authority

Only `native_format.rs` constructs this type. Its fields never enter a caller request.

```rust
#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct NativeFormatContract {
    key: NativeFormatKey,
    container: ContainerPolicy,
    video: VideoPolicy,
    audio: AudioPolicy,
    naming: ArtifactNaming,
    receipt_schema: u32,
}

#[derive(Clone, Debug, PartialEq, Eq)]
enum NativeFormatKey {
    H264AacMp4V1,
    NativeColorMasterV1,
}

#[derive(Clone, Debug, PartialEq, Eq)]
enum ContainerPolicy {
    Mpeg4,
    QuickTime,
}

#[derive(Clone, Debug, PartialEq, Eq)]
enum VideoPolicy {
    H264 { average_bitrate: u32 },
    AppleProRes4444,
}

#[derive(Clone, Debug, PartialEq, Eq)]
enum AudioPolicy {
    Aac { bitrate: u32 },
    PcmS24LeInterleavedStereo48k,
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct ArtifactNaming {
    stage_leaf: &'static str,
    extension: &'static str,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct StagePayloadName(&'static str);

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum OutputAssetHint {
    Mpeg4,
    QuickTime,
}

impl NativeFormatContract {
    pub(crate) fn derive(profile: &MovieProfile) -> Result<Self> {
        unimplemented!("one exhaustive mapping from the public profile")
    }

    pub(crate) fn validate_plan(&self, plan: &ExportPlan) -> Result<()> {
        unimplemented!("profile-specific settings and fixed audio-layout checks")
    }

    pub(crate) fn receipt_schema(&self) -> u32 {
        unimplemented!("2 for H.264/AAC; 3 for NativeColorMasterV1")
    }

    pub(crate) fn stage_payload_name(&self) -> StagePayloadName {
        unimplemented!("movie.mp4 or movie.mov")
    }

    pub(crate) fn artifact_path(
        &self,
        studio_root: &Path,
        output_sha256: &ContentHash,
    ) -> PathBuf {
        unimplemented!("content-addressed filename with the contract extension")
    }

    pub(crate) fn start_writer(
        &self,
        output: &Path,
        settings: &Settings,
        control: &ExportControl,
    ) -> Result<NativeWriterSession> {
        unimplemented!("settings, combined input admission, start, and zero session")
    }

    pub(crate) fn inspect_container(
        &self,
        output: &Path,
        control: Option<&ExportControl>,
    ) -> Result<NativeFormatEvidence> {
        unimplemented!("bounded container parse with the contract's explicit media hint")
    }

    pub(crate) fn output_media_hint(&self) -> OutputAssetHint {
        unimplemented!("explicit MPEG-4 or QuickTime MIME ownership for reopened output")
    }

    pub(crate) fn validate_measurements(
        &self,
        path: &Path,
        measurements: &NativeMeasurements,
    ) -> Result<()> {
        unimplemented!("one profile-specific structural check")
    }

    pub(crate) fn validate_receipt(
        &self,
        root: &Path,
        receipt: &ArtifactReceipt,
    ) -> Result<()> {
        unimplemented!("schema, naming, and required technical evidence")
    }
}
```

The contract owns the only mapping from profile to container, settings, extension, receipt schema, and verifier expectations.

No other module matches directly on `MovieProfile`.

### Native writer session

`NativeWriterSession` stays on the export thread. No retained AVFoundation object crosses a Rust worker channel.

```rust
pub(crate) struct NativeWriterSession {
    // Retained AVAssetWriter, both inputs, adaptor, and cancellation guard.
    // These fields are private to native_format.rs.
}

impl NativeWriterSession {
    pub(crate) fn append_picture(
        &mut self,
        frame: Pixels,
        timeline_frame: u64,
        rate: &Rate,
        control: &ExportControl,
    ) -> Result<()> {
        unimplemented!("wait for readiness, convert to native BGRA, append exact PTS")
    }

    pub(crate) fn append_audio(
        &mut self,
        chunk: PcmChunk,
        control: &ExportControl,
    ) -> Result<()> {
        unimplemented!("append the existing float PCM sample buffer and exact source clock")
    }

    pub(crate) fn finish(
        self,
        timeline_sample_frames: u64,
        control: &ExportControl,
    ) -> Result<()> {
        unimplemented!("mark inputs finished, end at N/48000, finalize, and require Completed")
    }
}
```

The session hides Objective-C dictionaries and codec-specific append requirements from `movie.rs`.

## Exact native format

For `native_color_master_v1`, the private contract builds these settings:

```text
AVAssetWriter file type              AVFileTypeQuickTimeMovie
AVVideoCodecKey                      AVVideoCodecTypeAppleProRes4444 (ap4h)
AVVideoWidthKey                      plan.settings.width
AVVideoHeightKey                     plan.settings.height
AVVideoCompressionPropertiesKey      absent
source pixel format                  kCVPixelFormatType_32BGRA

AVFormatIDKey                        kAudioFormatLinearPCM (lpcm)
AVSampleRateKey                      48000
AVNumberOfChannelsKey                2
AVLinearPCMBitDepthKey               24
AVLinearPCMIsFloatKey                false
AVLinearPCMIsBigEndianKey            false
AVLinearPCMIsNonInterleaved           false
AVEncoderBitRateKey                  absent
```

The profile has no video or audio bitrate. ProRes must not receive the H.264 average-bitrate property.

PCM24 is selected because this is a mastering artifact. It avoids adding another lossy encode after the unity PCM source.

AAC remains the established delivery audio for `h264_aac_mp4`. It does not define the mastering profile.

The current format query proves `canApplyOutputSettings` and individual `canAddInput` for both mastering audio options.

Its manifest SHA-256 is `f9ee98981347fcf559957e2d9b2f2e954344f53cde74d2f11f3585057d6274cd`.

It does not prove this selected combined ProRes 4444 and PCM24 writer. The full write gate remains mandatory.

## Writer and availability sequence

`movie::write` derives the contract before starting PCM or picture workers.

1. Validate the plan and the fresh stage suffix through `NativeFormatContract`.
2. Create `AVAssetWriter` with the contract file type.
3. Build both settings dictionaries inside `native_format.rs`.
4. Require `canApplyOutputSettings` for video and audio.
5. Require `canAddInput(video)`, then add the video input.
6. Require `canAddInput(audio)` in the combined writer state, then add the audio input.
7. Create the 32BGRA adaptor and require the video input relationship.
8. Call `startWriting` and start the session at exact zero.
9. Start the existing PCM worker and bounded picture workers.
10. Pump all planned picture frames and PCM sample frames.
11. Finish at `timeline_sample_frames / 48000` and require writer status `Completed`.
12. Reopen the staged file and run all structural verification before hashing it.

Any failure through step 8 proves the format unavailable for that host and build.

Any append or finish failure proves the writer path incomplete. Neither failure permits a receipt or promotion.

`WriterGuard` cancels an incomplete writer. `ExportStage` removes only its known payload after worker joins.

The staged file can exist before worker startup. Its owned stage makes that reversible.

## Container, filename, and codec authority

The contract derives every name from one `ArtifactNaming` value.

| Profile | Stage payload | Final artifact |
| --- | --- | --- |
| `h264_aac_mp4` | `movie.mp4` | `artifacts/<sha256>.mp4` |
| `native_color_master_v1` | `movie.mov` | `artifacts/<sha256>.mov` |

`ExportStage` accepts a typed `StagePayloadName`. It does not choose an extension.

```rust
impl ExportStage {
    pub(crate) fn create(
        root: &Path,
        owner: StageOwner,
        payload: StagePayloadName,
    ) -> Result<Self> {
        unimplemented!("write owner.json and remember exactly one allowed payload")
    }

    pub(crate) fn reclaim(
        root: &Path,
        owner: &StageOwner,
        payload: StagePayloadName,
    ) -> Result<Reclamation> {
        unimplemented!("remove only owner.json and the derived payload leaf")
    }
}
```

Reconciliation joins each attempt to its stored plan. It verifies the plan hash before deriving the payload name.

If the plan is absent, corrupt, or unsupported, reconciliation retains the stage for inspection.

Mastering verification requires all these observations:

- the receipt path equals `artifacts/<output_sha256>.mov` under the exact studio root;
- the filename has exactly one `.mov` suffix;
- a bounded ISO-BMFF parser finds a valid `ftyp` box;
- the major or compatible brand contains QuickTime brand `qt  `;
- the video track FourCC is exactly `ap4h` for every encoded sample;
- the audio track FourCC is exactly `lpcm` for every encoded sample;
- the audio ASBD is signed, non-float, little-endian, interleaved 24-bit stereo at 48 kHz;
- the output reopens through an explicit QuickTime MIME hint;
- the full decoded video and PCM streams reach EOF.

The source-import classifier remains unchanged. Output verification does not use its generic `ftyp` to MP4 guess.

## Plan and receipt schemas

### Plan schemas remain picture schemas

Output format does not add a normalized timeline field. The existing profile field already binds the selection.

Therefore, profile choice does not increment the plan schema.

The A01 mask master remains plan schema 6. A simple-cut master would remain schema 2.

The new profile changes request and plan hashes because `profile` is already serialized into both documents.

Old readers reject the unknown enum variant. New readers preserve every old plan meaning.

### Mastering receipts use schema 3

H.264/AAC continues to emit receipt schema 2 with the current serialized shape.

`native_color_master_v1` emits receipt schema 3. Schema 3 requires container, PCM encoding, and PCM comparison evidence.

The following combinations are rejected centrally:

- receipt schema 2 with `native_color_master_v1`;
- receipt schema 3 with `h264_aac_mp4`;
- schema 2 with new optional mastering evidence;
- schema 3 without container, PCM encoding, or PCM comparison evidence;
- any receipt schema outside 2 or 3;
- any output path that differs from the contract-derived content path.

`ArtifactVerification` remains schema 1. It stores the fresh extended `NativeMeasurements` already bound by the receipt ID.

### Exact historical fixtures

Implementation starts by freezing the current actual schema-6 H.264 plan before changing `MovieProfile`.

The source is the exact `plans.body` value for project `native-picture-masks-synthetic-a01`.

It resides in `artifacts/scratch-video-goal-20261005/native-project-a01/state/studio.sqlite`.

It is 417,605 bytes. Its SHA-256 and `plan_id` are both:

`5f9556fa7085bcd668d45cbc0564ff905adaf9b7f3d2e23b7fbed21ea65c5b28`

The new fixture path is `crates/editor/tests/fixtures/legacy/plan-schema6.json`.

The fixture must use the stored plan body bytes. It must not use the CLI response's reordered JSON object.

`legacy_hashes.rs` then requires exact deserialize and reserialize identity for all these documents:

| Document | SHA-256 |
| --- | --- |
| snapshot schema 1 | `a4afc9237cdc477ddc0c62023b7e0ed185a9f39bd3f72fd3f6596964d1c82423` |
| placement snapshot schema 1 | `00d8a0eb3bbf0cd6290e68fffaa8c4d8b5a654446fb2220f5d084da17944e1ea` |
| motion snapshot schema 1 | `1947fcb6939dbec40f13ae23b87a156f5d6e1758fa18e058aaa1f810abc313d3` |
| plan schema 2 | `97fdd9f63d48ee3b600ee37a845c302e79815bd1870b20dae376f9c4a957e025` |
| plan schema 3 | `4e5a89b00e7b5fabaafb4bf1335c1a5c3538c593765b4f5e5c818ff6bcede219` |
| plan schema 4 | `5cf0320f82bfc19839c5a06ffec15449fcdb80b97be15e2b4fb4105517ef0687` |
| plan schema 5 | `8ca51e03d048971a86cb598990fabd2f93f839c98b1b6c5fda3eb7aa90c3ee06` |
| new actual plan schema 6 | `5f9556fa7085bcd668d45cbc0564ff905adaf9b7f3d2e23b7fbed21ea65c5b28` |
| receipt schema 2 | `44c0c27ad1a58f22746011673d8e4d4a211c5b5cdeffcb18172d6cc73fc73be2` |

All optional mastering fields must serialize absent for these legacy documents.

## Verification contract

The verifier separates format truth from timeline truth.

`NativeFormatContract::validate_receipt` owns these checks:

- receipt schema, required evidence, suffix, and content-addressed location.

`NativeFormatContract::validate_measurements` owns these checks:

- QuickTime brand evidence;
- `ap4h` video throughout the track;
- `lpcm` audio throughout the track;
- exact PCM24 ASBD semantics from `audio_track.pcm_encoding`;
- required container and PCM comparison measurements.

`movie::verify_inner` remains responsible for these checks:

- exact planned video sample count;
- exact decoded frame PTS at `n * denominator / numerator`;
- exact width and height;
- complete decode and EOF;
- audio PTS start at zero;
- audio PTS end at `timeline_sample_frames / 48000`;
- exact decoded PCM sample count and continuous chunk offsets;
- exact source selection and canonical binding;
- source and output stream EOF evidence.

For PCM24, the verifier quantizes each selected source float sample to signed 24-bit code space.

It compares that expected code with the reopened output code. `maximum_code_delta` must be at most one.

The current correlation remains recorded. The one-code bound is the mastering acceptance check.

The comparison is incremental. It retains the current 4,096-frame chunks and capacity-two PCM channels.

No full audio buffer is admitted.

## Fences and recovery

The profile does not change the existing concurrency limits.

- one export-thread `NativeWriterSession` owns all AVAssetWriter objects;
- one picture coordinator owns up to four track workers;
- each track uses capacity-one request and response channels;
- composed output uses a capacity-one channel;
- PCM uses capacity-two chunks of at most 4,096 frames;
- picture payload admission remains an estimate capped at 512 MiB;
- each owned BGRA frame remains capped at 128 MiB;
- native and process peak memory remain unclaimed.

All readiness waits, callback waits, and worker waits call `ExportControl::check` on their current cadence.

The asynchronous track callback captures Send-owned Rust values only. `AVAssetTrack` stays on its callback thread.

The callback's mutex-held `FnOnce` prevents duplicate track work. Cancellation also cancels pending asset loading.

The writer finalization callback sends only `()` to its waiter. It does not send a retained framework object.

The export lease still renews every 10 seconds and extends ownership by 240 seconds.

Cancellation closes channels before joining workers. The writer guard then cancels unfinished native writing.

The export checks cancellation and epoch before storing `finalizing`. It checks both again before hard-link promotion.

Receipt schema 3 is stored before `.mov` promotion, following the current recovery order.

Finalizing recovery derives the contract from the immutable plan.

If `<sha256>.mov` exists, recovery verifies bytes, container, codecs, clocks, PCM24 evidence, and receipt measurements.

If the artifact is absent, recovery creates a fresh owned stage and rerenders under the new epoch.

An expired worker cannot promote because its epoch no longer matches.

## Required native proof

The saved settings query is dependency evidence only. Acceptance requires an actual Project export and independent decoded comparison.

### Pure contract proof

Focused tests first prove the exact profile JSON and its one exhaustive private mapping.

They cover both stage names, both final extensions, both receipt schemas, and rejection of every mismatched pairing.

A bounded container-parser vector set covers QuickTime brands, MP4 brands, malformed box sizes, truncation, and reordered compatible brands.

PCM vectors cover signed 24-bit endpoints, zero, one-code differences, clipping boundaries, stereo ordering, and chunk boundaries.

These tests also run the exact legacy fixture set through deserialize and reserialize identity.

### Pre-export declaration

Before any new export, save a policy document that binds:

- `native_color_master_v1` and its exact private settings listed above;
- authored fixture SHA-256 `969e22d77c0d5d2bb8aee5693254d9e17c2d06797b8ceac8f891c7f7d2aa7f04`;
- reference manifest SHA-256 `35e196ef8c041714b3eca714ca600deb9c158605fc308a9a85288bc3d1d6e011`;
- ROI manifest SHA-256 `2531487be1e4e18927e88865c6e0afd982dff075e1fb7c679489781045ba6c4f`;
- fixed 34 dB threshold;
- exact synthetic and canonical revision hashes;
- producer and independent observer identities;
- receipt schema 3 and plan schema 6 expectations.

The original 6 Mbps H.264 failures remain preserved. The later 24 Mbps failed probe remains preserved after them.

Neither result may be regenerated, replaced, or weakened for this proof.

The 6 Mbps outputs retain 58 failures across 1,366 comparisons. The failed classes are 20 fractional strips and 38 hidden regions.

The 24 Mbps probe retains 29 failures across 683 comparisons. Its failed classes are 10 fractional strips and 19 hidden regions.

The preserved 6 Mbps output hashes are `7492865d53c9326586d80b09fe73a153ed879d2709c2ee492baeb4ff8c89af95` and `9fdc96cc688eb53ebcb34ce5c0dc072d10e42f1fa73a1f53244f8ce586c09bc2`.

The preserved 24 Mbps probe hash is `a5c52104ccfc686e5cead70d97b5f09f9afd3fd4a4684ae373f8403feb2d5748`.

### Producer proof

Run the existing public prepare, export, and verify operations for both A01 variants.

The synthetic request uses revision `a7bc52df330b5a9d7e0ef8e8fe71b47963d308be393eeefa0e00d0cfbbfc24dd`.

Its source interval starts at 8,191 and contains exactly 144,000 stereo sample frames.

The canonical request uses revision `443e59aba47db24d30bb75f470f854f236ee8276497c9959061aba973dd129e3`.

Its selected canonical interval starts at zero and contains exactly 144,000 stereo sample frames.

The canonical source is 24-bit stereo PCM at 48 kHz. It is 78,624,044 bytes.

Its SHA-256 is `cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8`.

Each result must prove:

- one immutable schema-6 plan with the new profile;
- exact source closure and `presentation_ordinals` from the authored fixture;
- 72 output video frames at exact 24 fps decoded PTS;
- 144,000 output PCM frames at exact zero-based 48 kHz PTS;
- QuickTime container evidence and `.mov` receipt path;
- `ap4h` and `lpcm` track FourCC values;
- exact PCM24 layout and maximum one-code sample delta;
- full video and audio EOF;
- schema-3 receipt identity and fresh `verify_export` identity;
- completed replay with unchanged bytes and measurements.

### Independent picture proof

The independent observer must decode the actual promoted `.mov` outputs through AVFoundation.

It must independently parse the container, identify both track codecs, and measure raw and decoded PTS coverage.

It must independently confirm 144,000 PCM frames, PCM24 layout, the selected source interval, one-code tolerance, and EOF.

It must compare all 72 decoded frames against the unchanged pre-export reference.

It must reuse every existing ROI coordinate and the fixed 34 dB RGB PSNR threshold.

All 683 nonempty region comparisons per variant must pass. Empty regions remain explicitly empty.

This proof includes fractional strips, hidden regions, contain bars, signed clipping, overlap, and full-frame regions.

Raw compositor buffers cannot substitute for the encoded and reopened outputs.

The observer must bind the producer plan, receipt, output hash, source hashes, reference, ROI manifest, and its own executable hash.

### Negative controls

The proof or focused tests must reject each isolated mismatch:

1. Valid MP4 bytes renamed to `.mov`.
2. Valid QuickTime bytes placed under a `.mp4` receipt path.
3. QuickTime H.264/AAC tracks presented as the mastering profile.
4. ProRes video with AAC audio presented as the mastering profile.
5. `ap4h` and `lpcm` tracks behind a malformed or non-QuickTime `ftyp` brand.
6. A receipt schema-2/profile-mastering pair.
7. A receipt schema-3 document missing container, PCM encoding, or PCM comparison evidence.
8. One changed output byte after receipt creation.
9. One changed ROI coordinate or reference hash.
10. One changed source ordinal, decoded frame PTS, or PCM sample boundary.
11. Cancellation during an active schema-6 master export.
12. A stale epoch attempting `.mov` promotion after recovery.

These controls distinguish extension strings, container bytes, encoded tracks, and receipt claims.

### Acceptance boundary

The format is unverified until the actual combined writer finishes and both promoted outputs pass fresh and independent readback.

Passing the settings query does not satisfy this boundary.

Passing the native proof establishes a bounded technical mastering path only.

It does not establish `WATCHED`, `HEARD`, Resolve review, creative approval, final-film acceptance, maximum throughput, or maximum memory.

## Module map

| Module | Ownership after this change |
| --- | --- |
| `native_format.rs` new | public profile type; private contract; AV settings; writer session; extension; container and codec policy; mastering evidence validation |
| `plan.rs` | timeline normalization; calls profile validation; leaves schema selection picture-driven |
| `movie.rs` | format-neutral picture and PCM pump; full timeline clocks and EOF; delegates format checks |
| `media.rs` | AVURLAsset callback ownership; adds a typed explicit output-container hint |
| `export_stage.rs` | owned directory mechanics; accepts one typed payload name |
| `exports.rs` | epochs, receipt storage, promotion, replay, and recovery; asks the contract for schema and paths |
| `pcm.rs` | bounded float PCM decode; incremental PCM24 expected-code comparison support |
| `layers.rs` | unchanged bounded source workers and ordered BGRA composition |
| `pixels.rs` | unchanged opaque eight-bit BGRA ownership |
| `lib.rs` | reexports `MovieProfile` from its new owner without changing the public name |
| `legacy_hashes.rs` | exact snapshot, plan 2-6, and receipt-2 byte preservation |

The public surface grows by one enum variant. The private module hides the remaining format complexity.

A future native format adds another closed profile variant and one contract mapping.

That mapping must define its stage leaf, final extension, receipt schema, native settings, and readback rules together.

No future format receives a caller-supplied extension or a generic codec string.

## Red-flag screen

- **Shallow module:** avoided. `native_format.rs` owns settings, names, writer admission, observations, and validation behind one derivation.
- **Information leakage:** avoided. Callers never coordinate codecs, containers, audio layouts, extensions, or receipt schemas.
- **Temporal decomposition:** avoided. Format knowledge stays together across prepare, write, verify, promotion, and recovery.
- **Pass-through methods:** avoided. The writer session owns native objects and performs append and finalization policy.
- **Shared mutable native state:** avoided. One export thread owns the writer session; workers send Rust-owned payloads only.

## Rationale

### Problem

The H.264 path passes structural checks but fails fixed small-region fidelity. Format policy is also duplicated across five runtime sites.

The new path must improve encoded color detail without exposing AVFoundation choices or weakening the existing lifecycle.

### Usage (caller's view)

The usage at the start is normative. A caller chooses `native_color_master_v1` and uses the existing Project operations.

### Shape

One closed profile derives one private contract, per boundary-discipline and type-system-discipline.

The contract is the sole authority for settings, naming, receipt schema, and structural format checks.

Picture and audio clocks remain in `movie.rs` because they are timeline invariants shared by every format.

The interface is deep. One public unit variant hides QuickTime, ProRes, PCM24, extensions, AV dictionaries, and readback rules.

Plan schemas remain picture-driven. Receipt schema 3 marks the stronger output evidence without changing historical bytes.

### Synthesis decision

Candidate A selects `native_color_master_v1` as ProRes 4444 plus PCM24 in QuickTime.

It keeps plan schema 6 for the A01 mask timeline and introduces receipt schema 3 for mastering evidence.

Cross-candidate synthesis remains a later parent decision.

### Tradeoffs accepted

- We accept a fixed PCM24 choice in exchange for a closed mastering promise and no lossy audio encode.
- We accept a new receipt schema in exchange for strict evidence requirements and unambiguous readback.
- We accept ProRes file size in exchange for full-chroma mastering intent.
- We accept current opaque eight-bit BGRA limits in exchange for keeping composition and source semantics unchanged.
- We accept a new intent for every profile change in exchange for immutable request replay.
- We accept host-specific export failure in exchange for truthful native capability detection.

### Alternatives considered

1. **Caller-supplied container, codec, bitrate, and audio settings.** Rejected because callers could form unsupported combinations and must understand AVFoundation.
2. **A separate `export_master` operation.** Rejected because it duplicates ownership, cancellation, receipt, recovery, and verification behavior.
3. **AAC audio in the master.** Rejected because it adds avoidable loss to a file intended for further editing.
4. **ProRes 422 HQ.** Rejected because 4:2:2 does not directly target the observed one-pixel chroma-detail failure.
5. **Plan schema 7 for the new profile.** Rejected because no normalized picture or timeline field changes.
6. **Receipt schema 2 with optional mastering evidence.** Rejected because old and new evidence obligations would share one schema number.
7. **Image sequence plus WAV.** Rejected because it breaks the single-artifact receipt and existing Project export contract.
8. **Filename inference from codec.** Rejected because stage cleanup, receipt validation, and recovery need the same explicit authority.

### Open questions and risks

- Will this host accept both ProRes 4444 and PCM24 inputs after the first input is added?
- Will the writer accept every existing opaque 32BGRA frame without another pixel conversion requirement?
- Will the produced QuickTime file advertise `qt  ` in the bounded `ftyp` observation?
- Will PCM24 output be packed at six bytes per stereo frame as requested?
- Will source-to-output PCM quantization remain within one signed 24-bit code for both A01 variants?
- Will decoded ProRes 4444 pass every fixed 34 dB ROI after RGB and Y'CbCr conversions?
- Will ProRes writer buffering add material native memory beyond the existing Rust admission estimate?
- Is additional free-space preflight needed before longer mastering exports?

Each question requires actual native evidence. None is resolved by this design.

### Next implementation step

Freeze the exact 417,605-byte schema-6 plan fixture, then implement `native_format.rs` without changing public Project operations.
