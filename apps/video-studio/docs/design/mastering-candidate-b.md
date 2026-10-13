# Native mastering output: candidate B

Status: design only. This candidate makes a compiled output recipe the authority for a new mastering plan. It does not claim that this host can yet write or preserve ProRes pixels.

## Usage (caller's view)

The existing `Project` boundary remains the only public export boundary. A caller selects the new profile in the ordinary request JSON:

```json
{
  "intent": "mastering-prores-a01",
  "revision": "443e59aba47db24d30bb75f470f854f236ee8276497c9959061aba973dd129e3",
  "timeline": "picture-motion",
  "profile": {"kind": "prores4444_pcm24_quicktime"}
}
```

```rust
let request: ExportRequest = serde_json::from_str(request_json)?;
let prepared = project.prepare_export(request.clone())?;
assert_eq!(prepared.plan.schema, 7);
assert!(prepared.plan.output_recipe.is_some());

let result = project.export(request.clone())?;
let verified = project.verify_export(request.intent.clone())?;
```

While that export is running, another owner uses the same public intent:

```rust
let cancellation = project.cancel_export(request.intent.clone())?;
let recovery = project.reconcile_export_staging()?;
```

An unchanged H.264 caller still uses the old shape and receives the old plan schema:

```rust
let legacy: ExportRequest = serde_json::from_str(legacy_request_json)?;
let replay = project.prepare_export(legacy.clone())?;
assert!((2..=6).contains(&replay.plan.schema));
assert!(replay.plan.output_recipe.is_none());
let legacy_result = project.export(legacy)?;
```

`export`, `verify_export`, cancellation, and reconciliation retain their current lease and epoch behavior. Cancellation is an independent call; the example does not imply that a completed export can be cancelled.

## Problem

The current profile is copied into the plan, but writer settings, FourCC checks, stage names, and receipt suffix checks interpret it separately. A QuickTime mastering output also needs an explicit audio choice, source and output clocks, and native readback. The shape must preserve old plan and receipt bytes while making one new format impossible to publish under a different name or verifier.

## Shape

Candidate B selects **QuickTime Movie + Apple ProRes 4444 + 24-bit integer LPCM** for mastering. It keeps H.264/AAC MP4 unchanged for the existing profile. PCM24 avoids AAC generation loss and gives the verifier an exact integer sample contract. It costs more bytes, requires an explicit float-to-PCM24 conversion, and has only settings-query evidence today.

The compiler writes `CompiledOutputRecipe` into a new plan schema 7. It is a value-only wire type. No `AVAssetWriter`, `AVAssetTrack`, callback block, pointer, or framework lifetime is persisted.

```rust
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CompiledOutputRecipe {
    pub kind: RecipeKind,                 // ProRes4444Pcm24QuickTime
    pub container: ContainerContract,     // AVFileTypeQuickTimeMovie, brand checked on reopen
    pub video: VideoContract,             // ap4h, 32BGRA input, plan settings dimensions
    pub audio: AudioContract,             // lpcm, 48 kHz, 2 channels, signed LE 24-bit
    pub naming: ArtifactNamingContract,   // movie.mov and <sha256>.mov
    pub verification: TechnicalContract, // FourCC, clocks, EOF, PCM and decode rules
}

pub enum ContainerContract { QuickTimeMovie { expected_brand: FourCc } }
pub struct VideoContract {
    pub codec: FourCc,                    // ap4h
    pub input_pixel_format: FourCc,       // 32BGRA
    pub dimensions: DimensionsBinding,    // exact ExportPlan.settings
}
pub struct AudioContract {
    pub codec: FourCc,                    // lpcm
    pub sample_rate: u32,                 // 48_000
    pub channels: u16,                    // 2
    pub bits_per_sample: u16,             // 24
    pub signed: bool,
    pub big_endian: bool,                 // false
    pub non_interleaved: bool,            // false
}
pub struct TechnicalContract {
    pub expected_video: FourCc,
    pub expected_audio: FourCc,
    pub video_clock: FrameClock,          // n/24, epoch 0, contiguous
    pub audio_clock: SampleClock,         // i/48_000, epoch 0, contiguous
    pub require_video_eof: bool,
    pub require_audio_eof: bool,
}

pub enum MovieProfile {
    H264AacMp4 { video_bitrate: u32, audio_bitrate: u32 },
    ProRes4444Pcm24QuickTime,
}

pub struct ExportPlan {
    // Existing fields remain in their current order and meaning.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    // This field is appended after existing fields.
    pub output_recipe: Option<CompiledOutputRecipe>,
}
```

`compile_output_recipe` fills every field from the selected profile and plan settings, then rejects a mismatched hand-built recipe. `RecipeKind` fixes QuickTime, `ap4h`, `lpcm`, and `.mov`; callers cannot provide a free-form extension or codec string. Runtime code maps these value types to AVFoundation constants.

```rust
pub(crate) fn compile_output_recipe(
    profile: &MovieProfile,
    settings: &Settings,
) -> Result<Option<CompiledOutputRecipe>> { todo!() }

pub(crate) fn validate_plan_recipe(plan: &ExportPlan) -> Result<()> { todo!() }
pub(crate) fn recipe_for_execution(plan: &ExportPlan) -> Result<ExecutionRecipe> { todo!() }
pub(crate) fn preflight_native_recipe(
    recipe: &ExecutionRecipe,
    dimensions: PixelSize,
    cancel: &ExportControl,
) -> Result<NativeAvailability> { todo!() }
pub(crate) fn write_native(
    plan: &ExportPlan,
    recipe: &ExecutionRecipe,
    stage: &Path,
    pictures: PictureReceiver,
    pcm: PcmReceiver,
    cancel: ExportControl,
) -> Result<NativeWriteObservation> { todo!() }
pub(crate) fn verify_native_recipe(
    plan: &ExportPlan,
    recipe: &ExecutionRecipe,
    path: &Path,
    cancel: Option<ExportControl>,
) -> Result<(NativeMeasurements, FormatObservation)> { todo!() }
```

`ExecutionRecipe` owns the same value contract plus borrowed plan dimensions. `FormatObservation` is fresh native readback, including container brand and PCM bit depth; it is not an AVFoundation object.

The interface is deliberately deep: JSON is parsed before `Project`, and callers provide only a typed profile, revision, timeline, and intent. The compiler hides native settings, suffixes, PCM packing, clocks, and format-specific verification. No caller supplies a recipe or an Objective-C value. Boundary validation rejects malformed profiles and plans; trusted execution receives only the compiled contract.

## Plan, receipt, and module ownership

`MovieProfile::ProRes4444Pcm24QuickTime` is a caller intent. `CompiledOutputRecipe` is the operational authority after compilation. The plan stores both, and central validation requires the profile and recipe kind to agree. Writer, stage, promotion, receipt path validation, and verifier consume the recipe. They never re-derive format settings independently.

`ExportPlan` gains an optional, last-position `output_recipe` field. Schemas 2 through 6 serialize it as absent and retain their current H.264 meaning. A mastering request selects schema 7, even when its picture timeline would otherwise select schema 6. Replay accepts 2 through 7, rejects a schema 7 plan without its recipe, and rejects a schema 2–6 plan containing one.

`ArtifactReceipt` remains schema 2. Its `plan_id` transitively binds the recipe, so copying the recipe or a recipe hash into the receipt would add a second authority without detecting a new failure. Receipt validation loads the plan, asks its recipe for the required suffix, and still requires `.mp4` for every historical H.264 receipt. New native observations are compared during fresh verification; they are not optional receipt fields. This preserves the exact receipt-2 bytes.

| Owner | Responsibility |
| --- | --- |
| `plan.rs` | public profile, recipe compilation, schema 7, profile/recipe coherence, request and plan hashes |
| `project.rs` | immutable plan storage, replay allowlist 2..=7, source closure and recipe revalidation |
| `movie.rs` | AVAssetWriter settings from recipe, PCM24 packing, output track inspection and fresh readback |
| `layers.rs`, `composition.rs`, `pcm.rs` | existing bounded opaque BGRA and 48 kHz stereo source streams |
| `media.rs` | QuickTime brand classification and callback lifetime boundary |
| `export_stage.rs` | recipe-derived `movie.mov` staging and cleanup allowlist |
| `exports.rs` | recipe-derived artifact naming, schema-2 receipt, leases, epochs, promotion, recovery |
| `legacy_hashes.rs` | byte-for-byte historical roundtrips |

The current profile-derived design has one public profile but several interpreters: `movie.rs` hardcodes FourCCs, `export_stage.rs` hardcodes `.mp4`, and `exports.rs` hardcodes the receipt suffix. Candidate B moves the operational authority into one immutable plan value. The deliberate duplication is the caller profile plus its compiled result. The profile identifies intent; the recipe freezes execution. Receipt duplication is rejected because `plan_id` already binds both.

## Tradeoffs accepted

- We accept a larger QuickTime file in exchange for a lossless integer audio stage and full-resolution ProRes picture coding.
- We accept a new plan schema in exchange for preserving every old plan byte and rejecting a recipe-less mastering replay.
- We accept one profile-to-recipe compilation step in exchange for simpler writer, naming, and verifier call sites.
- We accept a separate native PCM24 conversion in exchange for a declared, testable sample contract.
- We accept that the persisted receipt remains less descriptive than the recipe in exchange for one authority; fresh verification must reopen the output.

## Native feasibility and proof order

The locked `objc2-av-foundation` 0.3.2 bindings expose `AVFileTypeQuickTimeMovie`, `AVVideoCodecTypeAppleProRes4444`, `AVVideoCodecTypeAppleProRes4444XQ`, and Core Media `ap4h`/`lpcm`. On the observed arm64 macOS 26.0.1 host, the saved query accepted QuickTime + `ap4h` + PCM24: combined `canApply` was true and each input reported `canAdd` true. Query manifest SHA is `f9ee98981347fcf559957e2d9b2f2e954344f53cde74d2f11f3585057d6274cd`; report SHA is `5849d71eb7a359e1215ceb0bb8d190a6be0ea536b92ee528fc117e51cf848193`.

The query did not start a writer, append BGRA or PCM, finish, reopen, inspect a brand, or measure ROI fidelity. **Direct native ProRes fidelity remains unverified until this actual write and readback succeeds.** A settings query cannot publish an output or justify a fallback.

The proof sequence is:

1. Compile schema 7, validate all source blobs, and preflight both native inputs before starting picture or PCM workers. Check `canApplyOutputSettings` and combined `canAddInput` for the recipe.
2. Open an owned `.mov` stage. Append 72 opaque 32BGRA frames at PTS `n/24`. Append PCM24 sample frames at PTS `i/48_000`. Finish the writer and fsync the stage.
3. Reopen the stage with an independent `AVAssetReader`. Check QuickTime brand, `ap4h`, `lpcm`, 24-bit signed little-endian stereo, dimensions, frame/sample counts, continuous epoch-0 clocks, and both EOFs.
4. Decode every frame to BGRA. Compare against the unchanged A01 reference and every original ROI at the fixed 34 dB RGB threshold. Retain every failure.
5. Compare output PCM against the declared source interval after the exact conversion below. Store the normal schema-2 receipt only after readback, source recheck, and epoch fencing.

PCM24 conversion is explicit: reject non-finite source floats, clamp each remaining value to `[-1, 1)`, multiply by `8_388_608`, round ties to even, clamp to `[-8_388_608, 8_388_607]`, and pack the signed value as three little-endian bytes. No resampling, mixing, gain, or pan is permitted. A native reader must report the same quantized values or the attempt fails.

AVFoundation objects stay inside the worker or callback that owns them. An asynchronous load callback retains its `AVAssetTrack` until completion and sends only Rust-owned decode evidence. `WriterGuard` and `ReaderGuard` cancel incomplete operations on drop. The finish callback sends a unit result, never an Objective-C pointer. No framework object crosses a Rust channel or enters the plan, receipt, or recovery store.

## Source lineage, clocks, and bounded execution

The plan remains the source authority: each `VideoUse.presentation_ordinals` entry binds a selected source sample, while `source_closure` binds the descriptor and measured source range. The actual Plan6 A01 fixture has two movie readers (`c925…` H.264 and `a224…` AV1 held ordinal 1560) plus two opaque PNGs. The registry must enumerate measured `av01` and `vp09` representations where they are selected, then reject any unsupported downloaded codec explicitly; native decoding is not assumed for every YouTube representation.

The synthetic Plan6 audio interval is `[8191, 152191)` at 48 kHz stereo. The canonical interval is `[0, 144000)`. Both output intervals begin at sample zero and end at the plan sample count. Video lineage records timeline ordinal, source asset hash, source ordinal, and measured source PTS in the independent proof. Output video uses integer `n/24` PTS; output PCM uses integer `i/48000` PTS. Any missing epoch, duplicate PTS, gap, negative duration, false EOF, or extra sample is a failure.

Admission remains conservative and application-owned. Before execution, bound nonempty track workers, channel capacity, one output frame, two PCM chunks, and the known BGRA payload estimate. Do not claim a process-wide native peak: ProRes encoder buffers, AVAssetReader buffers, compressed PNG bytes, and framework internals require separate measurement. The writer must apply backpressure and never accumulate the full movie or PCM stream in Rust.

Lease renewal and cancellation retain the current rules. Every worker wait checks `ExportControl`; writer failure interrupts the control before joins. Cancellation cancels reader and writer, closes bounded channels, joins workers, removes the stage, and writes no receipt. The finalizing transaction checks cancellation and epoch again before promotion. Recovery reclaims only a dead or expired owner, loads the immutable plan recipe, verifies a complete stage with that recipe, or discards it and retries under a new epoch. It never changes a failed ProRes request into H.264.

## Historical fixtures and the A01 baseline

`legacy_hashes.rs` must keep these exact bytes and hashes: snapshot schema 1 `a4afc9237cdc477ddc0c62023b7e0ed185a9f39bd3f72fd3f6596964d1c82423`; placement snapshot `00d8a0eb3bbf0cd6290e68fffaa8c4d8b5a654446fb2220f5d084da17944e1ea`; motion snapshot `1947fcb6939dbec40f13ae23b87a156f5d6e1758fa18e058aaa1f810abc313d3`; plan schema 2 `97fdd9f63d48ee3b600ee37a845c302e79815bd1870b20dae376f9c4a957e025`; plan schema 3 `4e5a89b00e7b5fabaafb4bf1335c1a5c3538c593765b4f5e5c818ff6bcede219`; plan schema 4 `5cf0320f82bfc19839c5a06ffec15449fcdb80b97be15e2b4fb4105517ef0687`; plan schema 5 `8ca51e03d048971a86cb598990fabd2f93f839c98b1b6c5fda3eb7aa90c3ee06`; receipt schema 2 `44c0c27ad1a58f22746011673d8e4d4a211c5b5cdeffcb18172d6cc73fc73be2`.

The actual Plan6 proof fixtures are retained independently: `plan-synthetic-a01.json` is 417,605 bytes, SHA `5f9556fa7085bcd668d45cbc0564ff905adaf9b7f3d2e23b7fbed21ea65c5b28`, and its existing H.264 output is `7492865d53c9326586d80b09fe73a153ed879d2709c2ee492baeb4ff8c89af95`; `plan-canonical-a01.json` is 417,888 bytes, SHA `507038af46a4b5c970734a0c3738f034038b8228674c2058f9c1cb41b8ea7eb0`, and its existing H.264 output is `9fdc96cc688eb53ebcb34ce5c0dc072d10e42f1fa73a1f53244f8ce586c09bc2`. A new schema-7 plan must preserve the same source closure, ordinals, 72-frame timeline, and audio clocks while changing only the output profile and compiled recipe.

The H.264 baseline remains visible and failed under its original policy. Authored fixture SHA is `969e22d77c0d5d2bb8aee5693254d9e17c2d06797b8ceac8f891c7f7d2aa7f04`; policy SHA is `ba5f639c4c2c94f1cc307057bf99758bfcedb8deee61181d7da46fc1182f736f`; reference SHA is `35e196ef8c041714b3eca714ca600deb9c158605fc308a9a85288bc3d1d6e011`; ROI SHA is `2531487be1e4e18927e88865c6e0afd982dff075e1fb7c679489781045ba6c4f`. The 6 Mbps output retains 58 failures, including fractional strips and hidden lower-layer regions. The post-failure 24 Mbps probe retains 29 failures and has output SHA `a5c52104ccfc686e5cead70d97b5f09f9afd3fd4a4684ae373f8403feb2d5748` with plan ID `308b6ae9aa83c6a587824def27e727ab2b53f72acc606bb86cc46a97cf2b5aae`. The ProRes proof must use the same 72-frame reference, every ROI coordinate, and 34 dB threshold. It must not rewrite the H.264 failure record.

## Tamper controls

Independent controls must reject: QuickTime bytes named `.mp4`; MP4 `ftyp` bytes named `.mov`; a fake brand with `ap4h` absent; `avc1` or `aac ` where `ap4h`/`lpcm` is required; PCM16, float, big-endian, non-interleaved, or wrong rate/channel count; a settings probe that reports `canApply` without a completed file; wrong recipe/profile coherence; output paths not derived from the recipe; changed source ordinals, source PTS, output PTS, EOF, or audio endpoint; a tampered plan or receipt; and a staged output promoted after cancellation or epoch loss. These controls inspect actual bytes and fresh AVAssetReader observations rather than trusting filename, receipt JSON, or mocked availability.

## Alternatives considered

- Deriving every setting from `MovieProfile` at each call site keeps old types small but recreates the current extension/FourCC drift.
- Copying the full recipe into a new receipt schema makes offline inspection convenient but creates two mutable-looking authorities. Plan identity already binds the recipe.
- ProRes plus AAC reuses the proven writer path, but it discards mastering samples and leaves no reason to prefer the larger container.
- H.264 at a higher bitrate is rejected by the retained 34 dB failures; the result is a new observation, not a universal codec claim.
- FFmpeg, libav, a renderer subprocess, or silent H.264 fallback violates the native path and would conceal the selected recipe’s failure.

## Synthesis decision

This is an independent Candidate B package. No sibling mastering candidate was read while drafting it; arena synthesis remains pending.

## Open questions and risks

- Will this exact macOS host finish a combined `ap4h` and PCM24 writer with the existing 32BGRA adaptor?
- Will the reopened QuickTime file expose the declared brand and 24-bit LPCM layout without a format-specific reader exception?
- Does native ProRes preserve every A01 ROI at 34 dB after the opaque eight-bit BGRA composition?
- Does the source codec registry have measured AV1 and VP9 paths for each selected downloaded representation?
- What native encoder memory peak must be added to the current application-owned admission estimate?

The proof remains technical. It cannot establish watched playback, heard audio, Resolve acceptance, color-management correctness, or creative approval. ProRes availability, actual PCM24 writing, container identity, and pixel fidelity remain material feasibility risks until the bounded native write and independent reopen are completed.

## Next implementation step

First implement recipe compilation and schema-7 validation, then run the actual two-input ProRes/PCM24 write and independent reopen before changing any acceptance claim.
