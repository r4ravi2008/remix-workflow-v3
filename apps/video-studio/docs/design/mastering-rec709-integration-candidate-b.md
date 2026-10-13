# Rec.709 native master integration — Candidate B

Status: design only. This document proposes a bounded production change. It does not change
Rust source, fixtures, media, metadata, GPU state, Resolve state, or acceptance claims.

## Caller usage first

The caller opts into the repaired writer by selecting one existing-profile-shaped variant:

```rust
let request = ExportRequest {
    intent,
    revision,
    timeline,
    profile: MovieProfile::NativeColorMasterV2,
};
let prepared = project.prepare_export(request.clone())?;
let result = project.export(request)?;
let replay = project.verify_export(intent)?;
assert_eq!(result.receipt.artifact.plan_id, ContentHash::document(&prepared.plan)?);
assert_eq!(replay.receipt.receipt_id, result.receipt.receipt_id);
```

The JSON request is `"profile":{"kind":"native_color_master_v2"}`. No caller-supplied
color matrix, ICC profile, gamma, or conversion flag is accepted.

An existing V1 caller keeps using `"kind":"native_color_master_v1"`. Its plan, writer,
receipt, and verification rules remain the legacy untagged master path. H264 callers remain
unchanged and cannot receive mastering color evidence.

## Decision

Choose an explicit `NativeColorMasterV2` profile. Keep `NativeColorMasterV1` as a frozen
compatibility branch. The profile is already part of the request and immutable `ExportPlan`,
so it is the single authority for writer and receipt dispatch. Do not add a second output recipe
to the plan.

The V2 contract is SDR Rec.709 metadata only:

* `AVVideoColorPropertiesKey` carries the complete `ITU_R_709_2` primaries, transfer, and
  matrix triple.
* Every input `CVPixelBuffer` gets the matching CoreVideo attachments with
  `kCVAttachmentMode_ShouldPropagate` before its frame is appended.
* The writer remains QuickTime, ProRes 4444 (`ap4h`), 32BGRA, and packed PCM24LE stereo at
  48 kHz. No pixel transfer or managed-color conversion is added.
* The output verifier reads the bounded QuickTime `colr/nclc` sample-description atom and
  checks every decoded video sample's color attachment tuple.

The isolated AVFoundation probe is concrete feasibility evidence. Its explicit arm compiled
with Rust `objc2` AVFoundation bindings 0.3.2 and produced `colr/nclc` values `(1,1,1)`.
It decoded all 72 frames with `ITU_R_709_2` attachments, while the untagged control had no
color atom and reproduced the prior 34 dB ROI failure. The probe remains a cause experiment;
the production proof must run through the editor writer and receipt lifecycle.

### Alternative considered: repair V1 in place

A V1 repair would add the same writer settings behind `NativeColorMasterV1`. It has a smaller
caller diff, but it changes the meaning of an existing serialized profile without changing its
request or plan hash. A completed untagged V1 output could then replay under a writer contract
that expects Rec.709 metadata.

Making schema 3 require color would newly reject old V1 receipts. Making color optional would
leave the profile unable to promise the fix. A producer-hash exception could preserve history,
but would duplicate renderer compatibility inside format validation and make schema 3 ambiguous.
V2 adds one caller variant and one receipt dispatch branch, while keeping the existing
`NativeFormatContract` boundary and `BuildIdentity` binding. That interface depth buys explicit
semantics and exact old-receipt compatibility, so V1 repair is rejected.

## Typed boundary

```rust
pub enum MovieProfile {
    H264AacMp4 { video_bitrate: u32, audio_bitrate: u32 },
    NativeColorMasterV1,
    NativeColorMasterV2,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NativeColorEvidence {
    pub encoded_sample_entries: u64,
    pub encoded_rec709_entries: u64,
    pub decoded_buffers: u64,
    pub decoded_rec709_buffers: u64,
    pub decoded_tuple_digest: ContentHash,
}

pub struct NativeMeasurements {
    // existing fields remain in their current order
    pub color: Option<NativeColorEvidence>,
}

impl NativeFormatContract {
    pub(crate) fn for_profile(profile: &MovieProfile) -> Result<Self>;
    pub(crate) fn validate_receipt(&self, root: &Path, receipt: &ArtifactReceipt) -> Result<()>;
    pub(crate) fn validate_measurements(&self, value: &NativeMeasurements) -> Result<()>;
    pub(crate) fn inspect_color(&self, path: &Path) -> Result<Option<NativeColorEvidence>>;
    pub(crate) fn start_writer(
        &self, output: &Path, settings: &Settings, control: &ExportControl,
    ) -> Result<NativeWriterSession>;
}

pub(crate) fn verify_color_sample(
    ordinal: u64, pts: CMTime, image: &CVPixelBuffer, digest: &mut ColorTupleHasher,
) -> Result<()>;
```

`NativeColorEvidence` is appended as an optional, skipped field. `None` serializes exactly as
before. V1 and H264 receipts therefore retain their current bytes and do not gain a required
field. V2 requires `Some` and requires all four counts to agree, with zero non-Rec.709 tuples
represented by `decoded_rec709_buffers == decoded_buffers`.

The tuple digest covers frame ordinal, PTS, and the three attachment values. It is a compact
replay check, not a duplicate frame trace. The verifier still checks each sample before hashing.

## Module ownership and exact edits

1. `crates/editor/src/plan.rs` adds the V2 wire variant to `MovieProfile` and its explicit
   custom deserializer. `ExportPlan.schema` remains 2 through 7. A V2 profile changes the
   request and plan hashes naturally; no plan schema bump is justified.
2. `crates/editor/src/native_format.rs` adds private `Format::MasterRec709`. V1 retains its
   current `Format::Master` behavior. V2 maps to `.mov`, `movie.mov`, QuickTime, receipt schema
   4, `ap4h`, and `lpcm`. H264 stays schema 2.
3. `native_format.rs` adds the complete writer color dictionary and a scoped helper for CoreVideo
   attachments. Use generated SDK constants when available. If an objc2 binding omits a key,
   use the SDK's exact NSString key in this private helper and bind it to the observed header
   identity. No raw framework pointer may escape the writer or frame append call.
4. `crates/editor/src/movie.rs` applies the attachments to every borrowed input buffer before
   `appendPixelBuffer_withPresentationTime`. It calls `inspect_color` during verification and
   records each output sample's tuple. Native objects remain owned by the current writer,
   reader, or scoped callback; only Rust evidence crosses the boundary.
5. `native_format.rs` parses `colr` only within bounded `moov/trak/mdia/minf/stbl/stsd` atom
   extents. It rejects malformed extents, missing atoms, non-`nclc` color declarations, or
   any triple other than `(1,1,1)`. This parser is Rust code and does not invoke a renderer or
   media subprocess.
6. `crates/editor/src/publication.rs` uses the contract's schema 4 for V2. It writes the same
   immutable CAS receipt flow. `crates/editor/src/exports.rs` dispatches validation from the
   stored plan profile, so a V2 receipt cannot be accepted for a V1 plan or vice versa.
7. `crates/editor/src/identity.rs` needs no new field. `BuildIdentity` already binds the plan,
   receipt, and verifier to the executable, backend, architecture, UUID, and lock hash. The V2
   writer fix is therefore tied to the prepared renderer identity without duplicating a producer
   hash in the color evidence.

`ArtifactVerification.schema` remains 1. `StoredArtifact` remains unchanged. `NativeFormatContract`
remains the only owner of extension, stage payload, codecs, receipt schema, and measurement rules.

## Receipt and historical compatibility

| Input or stored object | Required behavior |
| --- | --- |
| Old V1 plan and schema-3 receipt | Deserialize, hash, replay, and verify under the unchanged V1 branch. Color is not required. |
| New V1 export | Uses the unchanged untagged writer and schema 3. It does not silently become V2. |
| V2 plan | Uses the new profile variant and schema-4 receipt. Missing or wrong color evidence fails before publication. |
| H264 plan or schema-2 receipt | Keeps AAC/MP4 checks. Any mastering or V2 color evidence is rejected. |
| Historical plan schemas 2–7 | Keep their bytes and dispatch. Output profile is already serialized inside each plan. |

`serde(skip_serializing_if = "Option::is_none")` on the final `color` field preserves old
`NativeMeasurements`, receipt, verification, and CAS hashes when the field is absent. The
receipt validator must branch on the plan's profile before checking schema 3 or 4. It must not
apply V2 color requirements globally. Existing V1 fixture readback is a release gate.

## Verification sequence

Pure tests:

* Deserialize and reserialize historical V1/H264 requests, plans, receipts, and verifications;
  assert exact bytes and hashes.
* Assert `NativeColorMasterV1` maps to the old contract and V2 maps only to `MasterRec709`.
* Assert V2 serde rejects unknown profile fields and V2 receipts reject schema 3.
* Test atom parsing for one valid `(1,1,1)` `colr`, missing `colr`, wrong primaries, wrong
  transfer, wrong matrix, duplicate visual entries, truncated atoms, and oversized extents.
* Test optional color omission leaves V1/H264 JSON bytes unchanged.

Native tests:

1. Run the existing native 72-frame mastering input through V2. Assert QuickTime, `ap4h`,
   schema-4 receipt, 24 fps PTS, full decode, and all 72 output tuples.
2. Assert `colr/nclc` `(1,1,1)` and `ITU_R_709_2` attachments on every decoded sample. Assert
   exact PCM24 stereo48kHz source comparison remains 144,000 frames with zero code delta.
3. Run the same frozen 34 dB ROI policy. Record technical pixel metrics only; do not label this
   watched, heard, creative, or complete-film acceptance.
4. Use negative outputs with one missing atom, one wrong atom component, one altered decoded
   attachment, and one incomplete input-buffer attachment. Each must fail before an
   `ArtifactReceipt` is published.
5. Reopen an old completed V1 output in an isolated copied state. Assert exact receipt ID,
   artifact hash, schema 3, and successful verification under the new binary.
6. Re-run H264 negative controls, cancellation, lease fencing, staging recovery, and source
   closure checks. V2 must not loosen those gates.

The production test must run after the writer change and updated build identity exist. The
isolated color probe cannot substitute for this order because it never exercised `Project::export`,
CAS publication, or ordinary V1 replay.

## A01→A02 product-rejection driver review

The A02 helper correctly adds the timeout, private copied-blob permission change, frozen A01
policy/driver bindings, explicit driver record, and canonical-state equality to the technical
result. Skipping transient `studio.sqlite-shm` bytes is consistent with a durable-state digest.
No P1 defect was found in the diff. A02 was not executed and remains a preparation artifact.

The producer expectation is intentionally frozen to the pre-Rec.709 build (`17ad...`) and the
old authored/raw-plan hashes. After V2 source and fixtures are frozen, create a successor policy
and driver with the new producer, plan, authored fixture, and policy hashes. Do not claim A02 as
the V2 rejection proof. The successor must preserve A02's isolated SQLite/blob copies and
canonical immutability gate.

## Red-flag screen and limits

This design avoids a hidden V1 semantic change, a second plan recipe, a free-form color API, and
renderer subprocess coupling. It keeps V1 acceptance and V2 acceptance separate. It does not
claim ICC management, gamma conversion, H264 color correctness, HDR, arbitrary source-color
conversion, or creative quality.

The remaining material feasibility risk is SDK binding drift. The probe proves the required
AVFoundation/CoreVideo settings on this macOS/Rust stack, but the production implementation
must confirm the exact objc2 constants and attachment calls in the target build. If the writer
cannot produce the complete triple or the reader cannot observe every tuple, V2 fails closed and
V1 remains available.
