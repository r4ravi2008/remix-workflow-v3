# Native mastering output judgment A01

Status: complete design judgment. No runtime, project, media, GPU, or Resolve state changed.

## Decision

Use Candidate A as the whole-shape base.

Candidate A adds one closed caller profile and derives one private format contract. It preserves the existing `Project` operations and picture-plan schemas.

Use receipt schema 3 for the new observed container and PCM evidence. Keep every historical H.264 receipt at schema 2 with exact bytes.

Graft Candidate B's explicit PCM24 quantizer and its two actual Plan 6 fixture bindings. Do not graft its persisted recipe or Plan 7.

Candidate B's recipe repeats constants already fixed by its profile and renderer identity. Its Plan 7 also replaces the current picture-feature version axis.

That replacement cannot distinguish cuts, images, layers, motion, and masks without adding another picture-version field or inference rules.

No model-family alternative was available. This judgment does not claim cross-family review.

## Scores

| Criterion | Candidate A | Candidate B |
| --- | ---: | ---: |
| 1. Caller depth | 5 | 4 |
| 2. Fidelity | 4 | 5 |
| 3. Authority | 5 | 2 |
| 4. Compatibility | 5 | 2 |
| 5. Native ownership | 5 | 4 |
| **Total** | **24/25** | **17/25** |

### 1. Caller depth

Candidate A adds only `MovieProfile::NativeColorMasterV1`. Callers retain `prepare_export`, `export`, `verify_export`, `cancel_export`, and staging reconciliation.

The caller does not coordinate a container, codec, bitrate, audio packing, suffix, writer, or verifier.

Candidate B keeps the same operations. However, its public plan gains a large recipe that exposes internal execution policy.

Its caller profile also names the current codec, audio layout, and container. Candidate A's versioned product profile hides that mapping.

### 2. Fidelity

Both candidates preserve the failed 6 Mbps H.264 proof, the failed 24 Mbps probe, every ROI, and the 34 dB threshold.

Both require a real combined write, reopened video and audio, complete clocks, EOF, and independent pixel comparison.

Candidate B is stronger on PCM24. It defines finite-input checks, signed quantization, byte order, channel order, and exact code comparison.

Candidate A only proposes an unspecified source quantization and a one-code tolerance. The selected design must adopt the exact quantizer below.

### 3. Authority

Candidate A has one exhaustive, nonserialized `NativeFormatContract`. The immutable profile and renderer identity bind its versioned behavior.

The same contract owns native settings, stage name, artifact extension, receipt schema, container hint, and structural verification rules.

Receipt schema 3 records the original observed container and PCM encoding. Fresh verification can compare those observations with the stored receipt.

Candidate B persists both a profile and its deterministic expansion. Container, codecs, dimensions, clocks, naming, and verification rules appear twice.

Its `ExecutionRecipe` then repeats the compiled recipe with borrowed plan values. This is another representation without new authority.

Candidate B keeps receipt schema 2 and omits new format observations. The output hash binds bytes, but the receipt cannot compare original format evidence with fresh evidence.

### 4. Compatibility

Candidate A leaves plan schemas 2 through 6 on their existing picture-feature axis. The profile already participates in request and plan hashes.

Historical plans remain H.264 because their stored profile remains `h264_aac_mp4`. A new profile never changes those bytes or meanings.

Candidate B preserves absent-field serialization for old documents. Its new Plan 7 still collapses every picture shape into one format schema.

Current validation uses schema 2 for cuts, 3 for images, 4 for layers, 5 for motion, and 6 for masks.

A Plan 7 master cannot preserve those exclusivity rules without a second version field. Future picture features would create more product combinations.

### 5. Native ownership

Candidate A matches the current writer shape. One export thread owns the writer, inputs, adaptor, and `WriterGuard`.

The finish callback sends only a unit signal. Source callbacks keep retained tracks inside their callback-owned operation.

Candidate A also runs format admission before starting PCM or picture workers. Existing bounded channels and cancellation checks remain intact.

Candidate B preserves those important limits. Its proposal to verify a retained complete stage during recovery adds an unproved recovery path.

The current lifecycle verifies a promoted artifact from an immutable receipt. Otherwise, a new epoch renders a fresh owned stage.

## Selected contract

### Caller and plan

Keep the existing public request shape and add one unit variant:

```rust
pub enum MovieProfile {
    H264AacMp4 {
        video_bitrate: u32,
        audio_bitrate: u32,
    },
    NativeColorMasterV1,
}
```

`NativeColorMasterV1` permanently means this contract:

- QuickTime movie container;
- Apple ProRes 4444 video, observed as `ap4h`;
- opaque 32BGRA compositor input;
- signed, little-endian, interleaved 24-bit PCM;
- stereo at 48 kHz;
- `.mov` stage and artifact names;
- no caller bitrate or encoder settings.

The plan schema remains picture-derived:

| Picture execution | Plan schema |
| --- | ---: |
| cuts | 2 |
| static images | 3 |
| layers | 4 |
| motion | 5 |
| masks | 6 |

Both output profiles can appear in a newly compiled plan. Runtime code must never infer output format from the plan schema.

Old software safely rejects the unknown profile variant. New software must preserve every historical H.264 plan exactly.

### Private authority

Use Candidate A's private `NativeFormatContract`. Construct it only through an exhaustive `for_profile` function.

```rust
pub(crate) struct NativeFormatContract {
    key: NativeFormatKey,
    container: ContainerPolicy,
    video: VideoPolicy,
    audio: AudioPolicy,
    naming: ArtifactNaming,
    receipt: ReceiptPolicy,
}

impl NativeFormatContract {
    pub(crate) fn for_profile(profile: &MovieProfile) -> Result<Self>;
    pub(crate) fn validate_plan(&self, plan: &ExportPlan) -> Result<()>;
    pub(crate) fn stage_payload_name(&self) -> StagePayloadName;
    pub(crate) fn artifact_path(&self, root: &Path, hash: &ContentHash) -> PathBuf;
    pub(crate) fn start_writer(
        &self,
        output: &Path,
        settings: &Settings,
        control: &ExportControl,
    ) -> Result<NativeWriterSession>;
    pub(crate) fn inspect_container(
        &self,
        output: &Path,
        control: Option<&ExportControl>,
    ) -> Result<NativeFormatEvidence>;
    pub(crate) fn validate_format_measurements(
        &self,
        output: &Path,
        measurements: &NativeMeasurements,
    ) -> Result<()>;
    pub(crate) fn validate_receipt(
        &self,
        root: &Path,
        receipt: &ArtifactReceipt,
    ) -> Result<()>;
}
```

Derive the contract once after validating the immutable plan. Pass that value through one operation instead of rematching `MovieProfile` at each site.

Recovery may derive it again only after hashing and validating the stored plan. No caller or persisted document can construct its fields directly.

Keep generic timeline verification in `movie::verify_inner`. It owns frame and audio clocks, coverage, source comparison, and EOF.

Use a strict `FourCc` value for new brand evidence. Parse existing codec strings strictly without changing their historical JSON representation.

### Runtime

`NativeWriterSession` remains private and export-thread-owned. Its retained AVFoundation objects never cross a Rust channel.

Perform this sequence before starting source workers:

1. Create the writer with `AVFileTypeQuickTimeMovie`.
2. Build fixed ProRes 4444 and PCM24 settings.
3. Require both `canApplyOutputSettings` results.
4. Add the video input only after `canAddInput(video)` succeeds.
5. Require `canAddInput(audio)` in that combined writer state, then add it.
6. Create the 32BGRA adaptor.
7. Start writing and start the zero-based session.
8. Start the existing bounded picture and PCM workers.

The settings query is dependency evidence only. Steps 4 through 8 still require an actual successful writer.

Keep the current stream pump and backpressure. Video PTS remains exact `n / frame_rate` output time.

Audio output PTS remains exact `i / 48000`. Source selection remains a separate plan and source-evidence fact.

Do not describe the zero-based output clock as a source clock. The synthetic source starts at sample 8,191; the canonical source starts at zero.

### PCM24 graft from Candidate B

Add one private, pure PCM24 quantizer. Use it for each bounded input chunk and for independent expected-code calculation.

For each finite `f32` sample `x`:

```text
bounded = clamp(x, -1.0, 1.0)
code = round_ties_even(bounded * 8_388_608)
code = clamp(code, -8_388_608, 8_388_607)
```

Reject non-finite samples. Pack each signed code into three little-endian bytes in interleaved left-right order.

The writer input and requested output must both declare that PCM24 layout. The reopened output must contain the same codes.

Record all 144,000 compared sample frames and require `maximum_code_delta == 0`. Correlation can remain a diagnostic measurement.

If this exact path is unavailable, fail the selected profile. Do not silently switch to float PCM or AAC.

### Receipt and verification

Keep schema 2 byte-for-byte for H.264/AAC. All added optional measurement fields must deserialize absent and serialize omitted.

Use receipt schema 3 for `NativeColorMasterV1`. Require these observations:

- QuickTime major and compatible brands from bounded file parsing;
- `ap4h` on every encoded video sample description;
- `lpcm` on every encoded audio sample description;
- exact signed, non-float, little-endian, interleaved PCM24 ASBD;
- 48 kHz stereo and the observed bytes-per-frame;
- complete video and audio clocks and EOF;
- exact PCM24 comparison evidence.

Reject schema 2 with the mastering profile. Reject schema 3 with H.264 or missing mastering observations.

The content-addressed receipt remains the original evidence record. `verify_export` produces a separate fresh verification identity.

Fresh verification must compare all stored format, track, clock, PCM, hash, and source observations.

Use the contract's explicit QuickTime media hint when reopening output. Do not use the source importer's generic `ftyp`-to-MP4 guess.

### Stage, promotion, and recovery

`ExportStage` accepts one typed payload name. It does not choose `movie.mp4` or `movie.mov` itself.

Stage cleanup may remove only `owner.json` and the contract-derived payload. Unknown, mismatched, unreadable, or unowned files remain retained.

Promotion must derive `<output-sha256>.mov` from the same contract. Receipt validation requires that exact rooted path.

Finalizing recovery loads and validates the immutable plan and receipt. It verifies an existing promoted artifact before completing the job.

If the artifact is absent, recovery starts a fresh owned render under a new epoch. It does not adopt arbitrary retained stage bytes.

Cancellation and epoch loss must prevent receipt publication and promotion. No failure may fall back to H.264.

### Future formats

A future format adds another closed `MovieProfile` variant and one exhaustive private mapping.

The mapping owns its container, codec, audio layout, suffix, settings, and verifier expectations together.

Plan schemas continue to version picture execution. Receipt schemas version the stored evidence shape.

A new codec does not automatically require a new receipt schema. New mandatory evidence fields do.

Do not add caller codec strings, extensions, settings dictionaries, a generic codec registry, or a persisted compiled recipe.

## Required compatibility set

Preserve the existing eight golden documents from A15. Add both actual H.264 Plan 6 bodies as exact fixtures.

| Added Plan 6 document | Bytes | SHA-256 |
| --- | ---: | --- |
| synthetic | 417,605 | `5f9556fa7085bcd668d45cbc0564ff905adaf9b7f3d2e23b7fbed21ea65c5b28` |
| canonical | 417,888 | `507038af46a4b5c970734a0c3738f034038b8228674c2058f9c1cb41b8ea7eb0` |

The new enum variant and optional evidence fields must not change any existing serialized byte.

Fresh legacy readback must preserve schemas 2 through 6, their receipt identities, and their output hashes.

The H.264 Plan 6 outputs remain failed mastering evidence. Their hashes remain `7492865d53c9326586d80b09fe73a153ed879d2709c2ee492baeb4ff8c89af95` and `9fdc96cc688eb53ebcb34ce5c0dc072d10e42f1fa73a1f53244f8ce586c09bc2`.

The 24 Mbps probe remains a later failed experiment with output hash `a5c52104ccfc686e5cead70d97b5f09f9afd3fd4a4684ae373f8403feb2d5748`.

## Required native proof

Save the profile policy before exporting. Bind the fixed writer settings, fresh producer, two revisions, reference, ROI manifest, and 34 dB threshold.

Use the unchanged A01 72-frame picture timeline for both audio variants. Do not regenerate or alter the fixed references or ROI coordinates.

The product proof must establish:

- schema-6 plans with `native_color_master_v1`;
- exact request, plan, revision, renderer, source closure, and receipt identities;
- a combined ProRes 4444 and PCM24 writer with actual BGRA and PCM appends;
- 72 decoded video frames with epoch-zero `n/24` PTS and EOF;
- 144,000 exact PCM24 frames with continuous epoch-zero PTS and EOF;
- synthetic source interval `[8191,152191)`;
- canonical source interval `[0,144000)` and exact canonical WAV identity;
- QuickTime brand, `.mov` path, `ap4h`, `lpcm`, and PCM24 layout;
- product `verify_export`, completed replay, cancellation, and stale-epoch fencing;
- unchanged schemas 2 through 6 and historical receipts.

The independent observer must decode the promoted `.mov` files. It must bind its executable, producer, plans, receipts, sources, outputs, and fixed references.

It must compare every output frame and all 683 nonempty ROIs per variant. Every fixed ROI must meet the existing 34 dB RGB policy.

It must compare PCM24 codes exactly and prove both stream endpoints and EOF. Product-library verification is additional evidence, not independence.

Retain all failures. Raw compositor vectors and settings queries cannot substitute for the encoded, reopened outputs.

Negative controls must cover container brands, suffixes, codecs, PCM layout, receipt/profile pairing, output tampering, source clocks, output clocks, EOF, cancellation, and stale promotion.

## Grafts from Candidate B

- Use Candidate B's explicit finite-sample PCM24 quantizer and exact three-byte packing.
- Require exact reopened PCM24 code equality instead of an unspecified one-code conversion tolerance.
- Preserve both actual Plan 6 bodies, not only the synthetic plan.
- Keep Candidate B's explicit separation between source intervals and zero-based output clocks.
- Retain its requirement that settings acceptance never substitutes for start, append, finish, reopen, and fidelity proof.

## Rejected choices and red flags

- Reject Candidate B's persisted `CompiledOutputRecipe`. It duplicates a fixed profile mapping and creates profile/recipe coherence work.
- Reject Candidate B's `ExecutionRecipe`. It repeats the compiled value with plan dimensions and acts as a pass-through representation.
- Reject Plan 7 for an output format. It mixes format versioning with picture execution and breaks the current schema invariants.
- Reject receipt schema 2 for the new mastering evidence. The original receipt must bind observed container and PCM facts.
- Reject recovery that adopts an unpromoted retained stage. Preserve the existing receipt-bound promoted-artifact recovery order.
- Reject Candidate B's source codec registry work. The exact measured source closure already owns selected source capability.
- Reject AAC output, float-PCM output, ProRes 422, H.264 fallback, FFmpeg, libav, subprocess rendering, and image-sequence output for this profile.
- Reject caller-provided codecs, extensions, bitrates, PCM flags, or native dictionaries.
- Reject a weaker ROI threshold or post-result ROI exclusions.

Candidate A avoids the architect red flags after the required repairs. Its contract is deep and keeps format policy private.

Candidate B retains a deep `Project` caller boundary. Its recipe creates information leakage and a second persisted authority.

Its Plan 7 also couples two independent version axes. That coupling would force special cases as either axis grows.

## Acceptance boundary

This judgment selects a design only. It does not accept a native mastering implementation or close the masks native proof.

The A15 code-only review remains frozen. The failed H.264 evidence and 24 Mbps probe remain authoritative failures.

Only a fresh combined writer and independent reopened proof can establish this bounded mastering dependency.

That proof cannot establish watched playback, heard audio, Resolve suitability, managed color, creative approval, full-film acceptance, maximum throughput, or native peak memory.
