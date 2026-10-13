# Native Rec.709 mastering integration — Candidate A

Status: design only. Production source and preserved evidence remain unchanged.

## Problem

`NativeColorMasterV1` writes opaque `32BGRA` frames to ProRes 4444 without an explicit color tuple. The saved 72-frame alpha export therefore decoded with a systematic matrix error. The isolated two-arm probe reproduced the same 34 failing regions. Its explicit arm added a complete Rec.709 writer tuple and matching propagating input-buffer attachments. That arm emitted `colr/nclc/1/1/1` and passed all 752 unchanged comparisons.

The default arm reached 32.180 dB minimum ROI PSNR. The explicit arm reached 48.253 dB minimum ROI PSNR and 49.942 dB minimum full-frame PSNR. The bound probe manifest is `7ac0f65efc2f4ecf69a88086b24c69f8229d4506bea94ed640c6e45eab03eace`.

The integration must fix new mastering exports without changing what historical V1 plans and Receipt3 documents claim. Picture plan schemas 2–7 remain independent from the output format. PNG values remain unmanaged source samples; this unit defines only the native numeric encode/decode mapping.

## Usage (caller's view)

The caller selects one new closed profile. Existing `Project` operations remain the whole public workflow.

```json
{
  "intent": "export-alpha-rec709-master-a01",
  "revision": "f14f6969245cd817875fcfe9163db19b92b743deded0e0ad8c94026e5cbe4f30",
  "timeline": "alpha-picture",
  "profile": { "kind": "native_color_master_v2" }
}
```

```rust
let request = ExportRequest {
    intent: EntityId::parse("export-alpha-rec709-master-a01")?,
    revision,
    timeline: EntityId::parse("alpha-picture")?,
    profile: MovieProfile::NativeColorMasterV2,
};

let prepared = project.prepare_export(request.clone())?;
assert_eq!(prepared.plan.schema, 7); // alpha selects the picture schema

let exported = project.export(request)?;
assert_eq!(exported.receipt.artifact.schema, 4);
assert!(exported.receipt.artifact.technical.video_color.is_some());

let reopened = project.verify_export(EntityId::parse(
    "export-alpha-rec709-master-a01",
)?)?;
assert_eq!(reopened.receipt.receipt_id, exported.receipt.receipt_id);
```

Historical V1 readback uses the same public operation. It returns the original receipt identity and makes no new color claim.

```rust
let historical = project.verify_export(EntityId::parse("export-alpha-master-a01")?)?;
assert_eq!(
    historical.receipt.receipt_id.as_str(),
    "032552643ea7dac7f76b81bc4938a810b590674e0f3a621a3e8bd2e34648a30f",
);
assert_eq!(historical.receipt.artifact.schema, 3);
assert!(historical.receipt.artifact.technical.video_color.is_none());
```

H.264 callers keep their existing request and Receipt2 behavior.

```rust
let request = ExportRequest {
    intent: EntityId::parse("review-copy")?,
    revision,
    timeline: EntityId::parse("main")?,
    profile: MovieProfile::H264AacMp4 {
        video_bitrate: 8_000_000,
        audio_bitrate: 192_000,
    },
};
let prepared = project.prepare_export(request.clone())?;
let result = project.export(request)?;
assert!((2..=7).contains(&prepared.plan.schema));
assert_eq!(result.receipt.artifact.schema, 2);
assert!(result.receipt.artifact.technical.video_color.is_none());
```

## Decision

Add `MovieProfile::NativeColorMasterV2`. Keep the V1 writer and verifier semantics unchanged.

`NativeColorMasterV2` is the V1 QuickTime, ProRes 4444, and PCM24 contract plus one closed video-color contract:

- `AVVideoColorPropertiesKey` contains the complete Rec.709 primaries, transfer, and YCbCr matrix tuple.
- Every input `CVPixelBuffer` carries the matching Core Video tuple with `ShouldPropagate`.
- Every encoded video sample description reports the matching Core Media tuple.
- Every decoded output buffer reports the matching Core Video tuple.
- The ProRes sample entry contains one `colr` atom with `nclc` values `1/1/1`.

V1 remains a no-color-claim profile. New V1 writes retain the current settings and attachment behavior. Fresh V1 verification deliberately omits `video_color`, even when AVFoundation supplies inferred decoded attachments. This preserves historical Receipt3 meaning and bytes.

Repairing V1 in place loses because the same public profile and receipt schema would describe two different writer policies. Existing Receipt3 documents contain no color observations. A silent repair would make a successful fresh verification appear to extend their original evidence.

## Shape

### Public and persisted types

```rust
#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum MovieProfile {
    H264AacMp4 { video_bitrate: u32, audio_bitrate: u32 },
    NativeColorMasterV1,
    NativeColorMasterV2,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NativeColorTupleEvidence {
    pub color_primaries: String,   // exact framework value: ITU_R_709_2
    pub transfer_function: String, // exact framework value: ITU_R_709_2
    pub y_cb_cr_matrix: String,    // exact framework value: ITU_R_709_2
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NativeContainerColorEvidence {
    pub atom: FourCc,           // colr
    pub parameter_type: FourCc, // nclc
    pub primaries: u16,         // 1
    pub transfer: u16,          // 1
    pub matrix: u16,            // 1
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NativeVideoColorEvidence {
    pub container: NativeContainerColorEvidence,
    pub encoded_samples: NativeColorTupleEvidence,
    pub decoded_buffers: NativeColorTupleEvidence,
}

pub struct NativeMeasurements {
    // Existing fields remain in their existing order.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub video_color: Option<NativeVideoColorEvidence>,
}
```

The new field is appended to `NativeMeasurements`. Absent values deserialize as `None` and serialize omitted. Existing plan and receipt bytes therefore remain identical.

The evidence does not duplicate sample counts. `video_track.sample_buffers` already records the complete encoded count. `video_frames` already records the complete decoded count. The observation loops check every sample or buffer and require EOF before constructing one tuple.

### Private format authority

```rust
#[derive(Clone, Copy)]
enum Format {
    H264 { video: u32, audio: u32 },
    MasterV1,
    MasterV2,
}

#[derive(Clone, Copy)]
pub(crate) struct NativeFormatContract(Format);

struct ContainerInspection {
    format: Option<NativeFormatEvidence>,
    color: Option<NativeContainerColorEvidence>,
}

impl NativeFormatContract {
    pub(crate) fn for_profile(profile: &MovieProfile) -> Result<Self> {
        unimplemented!("exhaustive profile-to-format authority")
    }

    pub(crate) fn receipt_schema(self) -> u32 {
        unimplemented!("H264=2, MasterV1=3, MasterV2=4")
    }

    pub(crate) fn start_writer(
        self,
        output: &Path,
        settings: &Settings,
        control: &ExportControl,
    ) -> Result<NativeWriterSession> {
        unimplemented!("closed AVFoundation settings per format")
    }

    pub(crate) fn inspect_container(
        self,
        path: &Path,
        control: Option<&ExportControl>,
    ) -> Result<ContainerInspection> {
        unimplemented!("bounded ftyp and V2 video-sample-entry colr inspection")
    }

    pub(crate) fn observe_encoded_video_color(
        self,
        description: &CMFormatDescription,
    ) -> Result<Option<NativeColorTupleEvidence>> {
        unimplemented!("V2 requires the exact tuple; other profiles return None")
    }

    pub(crate) fn observe_decoded_video_color(
        self,
        image: &CVPixelBuffer,
    ) -> Result<Option<NativeColorTupleEvidence>> {
        unimplemented!("V2 requires the exact tuple; other profiles return None")
    }

    pub(crate) fn validate_measurements(self, value: &NativeMeasurements) -> Result<()> {
        unimplemented!("existing checks plus profile-specific color evidence")
    }
}
```

`NativeFormatContract` remains the single authority for settings, attachments, names, receipt schemas, and reopened observations. Callers do not receive color knobs.

### Writer path

For V2, `start_writer` adds this exact nested dictionary to the current `ap4h` settings:

```text
AVVideoColorPropertiesKey = {
  AVVideoColorPrimariesKey:       AVVideoColorPrimaries_ITU_R_709_2,
  AVVideoTransferFunctionKey:     AVVideoTransferFunction_ITU_R_709_2,
  AVVideoYCbCrMatrixKey:           AVVideoYCbCrMatrix_ITU_R_709_2
}
```

Missing constants, rejected settings, or rejected combined inputs fail V2 before worker startup. V1 and H.264 do not add this dictionary.

`NativeWriterSession::append_picture` owns attachment policy because it already owns the selected contract and the adaptor. `pixels.rs` remains a generic BGRA allocator.

```rust
impl NativeWriterSession {
    pub(crate) fn append_picture(
        &self,
        image: &CVPixelBuffer,
        pts: CMTime,
        finished: bool,
    ) -> Result<()> {
        if self.format.is_master_v2() {
            attach_and_read_back_rec709(image, CVAttachmentMode::ShouldPropagate)?;
        }
        // Existing adaptor append and finish behavior follows.
        unimplemented!()
    }
}
```

`attach_and_read_back_rec709` sets and immediately reads all three Core Video attachments. It requires the exact value and `ShouldPropagate` mode for every input frame. No retained framework object crosses a worker channel.

### Reopen path

`movie::inspect_encoded_track` calls `observe_encoded_video_color` for every nonempty encoded video sample. A missing, partial, changing, or non-Rec.709 tuple fails verification.

The full decoded-frame loop calls `observe_decoded_video_color` for every output buffer. A missing, partial, changing, or non-Rec.709 tuple fails before that frame increments `video_frames`.

The existing EOF, frame count, PTS, dimensions, opaque-alpha scan, audio clocks, and PCM24 comparison remain unchanged. After both loops complete, `movie::verify_inner` assembles `NativeVideoColorEvidence` from the container, encoded, and decoded observations.

The container reader extends the existing bounded atom parser. V2 requires one `ap4h` video sample entry and one bounded `colr` child with the exact ten-byte `nclc/1/1/1` payload. It rejects duplicate, truncated, misplaced, conflicting, or oversized tags. V1 parses only its existing `ftyp` evidence and makes no tag claim.

### Receipt and plan compatibility

| Profile | Plan schemas admitted | Receipt | `video_color` |
| --- | --- | ---: | --- |
| H.264/AAC | 2–7 | 2 | forbidden |
| NativeColorMasterV1 | 2–7 | 3 | forbidden |
| NativeColorMasterV2 | 2–7 | 4 | required |

Plan schemas remain picture-feature schemas. `plan.rs` keeps the current selector: cuts 2, static PNG 3, layers 4, motion 5, masks 6, transparent PNG 7. V2 does not create Plan8.

The profile variant and `BuildIdentity` already participate in the canonical plan document. A V2 plan therefore has a distinct plan ID and renderer identity without another persisted field. Existing `2..=7` admission gates in `plan.rs`, `project.rs`, and `exports.rs` remain unchanged.

`validate_receipt` derives the contract from the receipt-bound plan. It rejects Receipt4 under V1 or H.264. It also rejects Receipt2 or Receipt3 under V2. Publication continues to derive the receipt schema and `.mov` path from the contract.

`NativeMeasurements::compare` includes `video_color`. V2 fresh verification must reproduce all three observations. V1 fresh verification returns `None`, matching historical Receipt3. Verification does not require the historical producer executable to be current. Export still requires `prepared.plan.renderer == BuildIdentity::current()`.

## Module map

| Module | Exact change |
| --- | --- |
| `plan.rs` | Add `NativeColorMasterV2` to public and wire enums. Keep schema selection and 2–7 validation unchanged. |
| `native_format.rs` | Split `Master` into V1 and V2. Own V2 settings, input attachments, `colr` parsing, color observation, Receipt4, and profile validation. |
| `movie.rs` | Add optional evidence types. Observe every encoded sample and decoded buffer. Assemble evidence only after complete loops and EOF. Compare the field on reverify. |
| `lib.rs` | Re-export the three evidence types used by public `NativeMeasurements`. |
| `publication.rs` | No production flow change. Add Receipt4 contract tests around the existing derived schema/path boundary. |
| `project.rs` | No production change. Add replay tests proving schemas 2–7 remain admitted with V2. |
| `exports.rs` | No schema-gate change. Add V2 export, verify, completed replay, finalizing recovery, and forged-receipt tests. |
| `pixels.rs` | No change. BGRA allocation stays profile-independent. |
| `crates/cli/src/main.rs` | Describe V1 as compatibility/no-color-claim and V2 as the closed Rec.709 master. Do not claim managed source color or creative acceptance. |

## Ownership, cancellation, and recovery

The existing export thread owns writer settings, attachments, adaptor, and color readback. Attachment work occurs immediately before the existing synchronous append. Existing control checks bound the surrounding pump; row workers and channels do not change.

Reopen observation uses the existing cancellable native readers. Each sample or buffer iteration keeps its current `ExportControl::check`, deadline, and reader guard. The bounded container parser performs cancellation checks between boxes when called from owned verification.

Publication stores Receipt4 only after native verification succeeds. Cancellation, fencing, staging, lease renewal, finalizing recovery, and content-addressed promotion keep their current order. Recovery derives V2 from the hashed stored plan, then requires Receipt4 and the full color evidence before completing.

## Verification plan

1. Preserve the eleven exact legacy fixtures and hashes. This includes Plan2 `97fdd9…`, Plan3 `4e5a89…`, Plan4 `5cf032…`, Plan5 `8ca51e…`, both Plan6 fixtures, and Receipt2 `44c0c2…`.
2. Preserve and reverify the actual V1 Plan7 receipt `032552…` and artifact `7f316c…`. Require Receipt3 and absent `video_color`. This is historical technical readback, not alpha-output acceptance.
3. Compile representative V2 cuts, static PNG, layers, motion, masks, and alpha projects. Require unchanged schema choices 2–7 and distinct V2 plan IDs.
4. Unit-test the exact AV writer dictionary and all three input attachments. Missing one key, a wrong value, or `ShouldNotPropagate` must fail.
5. Parse valid `colr/nclc/1/1/1`. Reject absent, duplicate, truncated, conflicting, oversized, wrong-track, `nclx`, and non-`1/1/1` controls.
6. Require the encoded tuple on every sample. Mutate a middle sample observation in a test seam and require failure.
7. Require the decoded tuple on every buffer. Mutate a middle buffer observation and require failure.
8. Reject forged Receipt4 evidence, V2 Receipt3, V1 Receipt4, and color evidence on Receipt2 or Receipt3.
9. Run a fresh ordinary V2 export from the unchanged 72-frame authored alpha timeline. Require all private pre-encode hashes unchanged, all 752 independent comparisons at the unchanged 34 dB floor, exact PCM24, complete clocks and EOF, public verify, and completed replay.
10. Repeat active cancellation, stale-epoch fencing, retained-stage recovery, and finalizing recovery with V2. Preserve failures and bind plan, renderer, receipt, output, and executable hashes.

The existing probe is causal feasibility evidence. It is not the production V2 proof. The fresh ordinary export remains unaccepted until these checks complete.

## Tradeoffs accepted

- We accept a new caller-visible profile in exchange for permanent, honest V1 semantics.
- We accept Receipt4 in exchange for evidence that distinguishes the corrected mapping from historical Receipt3.
- We accept strict `nclc/1/1/1` output in exchange for matching the tested framework result exactly.
- We accept per-sample and per-buffer attachment inspection in exchange for rejecting midstream metadata changes.
- We accept closed Rec.709 policy in exchange for keeping framework choices away from callers.

## Alternatives considered

### Repair `NativeColorMasterV1` in place

This keeps the smallest caller surface. It changes the meaning of an existing profile and leaves old Receipt3 documents unable to show which writer policy produced them. It also makes V1 replay behavior depend on producer generation. The shallow API is not worth the evidence ambiguity.

### Add optional color settings to the caller request

This could support more standards. It exposes AVFoundation policy, invalid tuple combinations, and tag compatibility to every caller. The first unit has only one tested coherent tuple, so the interface would be wider than the proven capability.

### Add Plan8 for Rec.709

This would mix picture execution with output format. The profile is already canonical plan data. Schemas 2–7 must continue to describe the picture path, so Plan8 would duplicate the format decision and create invalid combinations.

## Red-flag screen

- The public surface adds one enum variant and no operation.
- `NativeFormatContract` hides all AVFoundation keys, attachment modes, tag parsing, and receipt rules.
- `pixels.rs`, workers, and callers do not learn the selected color policy.
- One contract derives writer behavior, evidence requirements, naming, and receipt schema.
- Existing movie loops gain validation calls rather than new pass-through modules.
- Plan schema and output profile remain separate axes.

## Bounded risks

- A future macOS release may emit `nclx` instead of the tested `nclc`. V2 must fail closed until that output receives a separate bounded proof.
- Framework format-description or decoded-attachment strings may drift. Exact V2 verification will reject that drift instead of weakening the claim.
- The recursive sample-entry parser is security-sensitive. It needs strict extents, depth, count, and allocation bounds.
- Per-buffer attachment readback adds native calls. This unit makes no maximum-throughput claim.
- Rec.709 tagging does not color-manage PNG ICC, gamma, movie primaries, transfer, gamut, or creative intent.
- Passing the unchanged 34 dB ROI gate proves only the bounded native round trip. It does not prove playback, hearing, creative acceptance, or full-film readiness.

## Next implementation step

Add the V2 enum and private contract branch with pure receipt and observation tests before changing the writer path.
