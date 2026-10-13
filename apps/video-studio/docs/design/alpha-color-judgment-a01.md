# Rec.709 native-master integration judgment — A01

Status: bounded design judgment. Production source, state, media, and preserved evidence remain unchanged.

## Verdict

Use Candidate A as the whole-shape base. Its explicit observation tuples, `NativeColorMasterV2`, and Receipt4 provide the clearest authority. Candidate B reaches the same main profile decision, but its count and digest protocol duplicates existing evidence.

Remove Candidate A's production recursive `colr` parser. This subtraction leaves no material gap in the **production Rec.709 tuple claim** when all conditions below hold:

- Every nonempty encoded sample reports the complete Rec.709 tuple through its `CMFormatDescription`.
- Every decoded output buffer reports the same complete tuple through propagated Core Video attachments.
- Existing counts, clocks, EOF checks, and source closure prove those loops are complete.
- An independent bounded parser checks the accepted `.mov` bytes for the observed `colr/nclc/1/1/1` representation.

The production receipt must not claim an exact MOV atom layout after this subtraction. Exact `nclc/1/1/1` remains an independently measured property of each accepted bounded proof artifact. A universal atom-representation claim would require a production parser and would restore the gap.

This judgment is same-model review. No cross-family reviewer was available.

## Independent scores

Scores use 0–5, where 5 is strongest.

| Criterion | A | B | Judgment |
| --- | ---: | ---: | --- |
| Caller clarity and depth | 5 | 4 | Both add one closed profile. B's caller example invokes crate-private `ContentHash::document`; callers should compare with `prepared.plan_id`. |
| Historical compatibility | 5 | 5 | Both preserve H.264, V1, Plan2–7, and omitted optional fields. |
| Evidence authority | 5 | 3 | A persists the measured tuple. B duplicates existing counts and hashes fixed tuple values into a new protocol. |
| Native ownership | 5 | 4 | A keeps attachment policy in `NativeWriterSession`, which owns the adaptor and format. B also assigns that policy to `movie.rs`. |
| Scope and reader load | 3 | 2 | Both add an unnecessary recursive parser. B also adds digest and count validation. |
| Feasibility grounding | 5 | 5 | Both use the complete tuple demonstrated by the retained two-arm probe. |
| Verification precision | 4 | 3 | A separates encoded and decoded observations. B's digest makes the recorded values and failure source less direct. |
| **Total** | **32/35** | **26/35** | **Candidate A ranks first.** |

Root independently scored A 32/35 and B 28/35. The selection and Candidate A score agree. My lower B score reflects its invalid external caller expression and weaker tuple evidence.

## Selected contract

Add one public profile and keep picture schemas independent from output format.

```rust
pub enum MovieProfile {
    H264AacMp4 { video_bitrate: u32, audio_bitrate: u32 },
    NativeColorMasterV1,
    NativeColorMasterV2,
}

pub struct NativeColorTupleEvidence {
    pub color_primaries: String,
    pub transfer_function: String,
    pub y_cb_cr_matrix: String,
}

pub struct NativeVideoColorEvidence {
    pub encoded_samples: NativeColorTupleEvidence,
    pub decoded_buffers: NativeColorTupleEvidence,
}

pub struct NativeMeasurements {
    // Existing fields remain in their current order.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub video_color: Option<NativeVideoColorEvidence>,
}
```

The exact persisted values are the framework's `ITU_R_709_2` strings for primaries, transfer, and matrix. Do not add container evidence, sample counts, buffer counts, or a tuple digest. Existing `video_track.sample_buffers` and `video_frames` already own the counts.

The receipt matrix is exact:

| Profile | Plan schemas | Receipt schema | `video_color` |
| --- | --- | ---: | --- |
| H.264/AAC | 2–7 | 2 | forbidden |
| `NativeColorMasterV1` | 2–7 | 3 | forbidden |
| `NativeColorMasterV2` | 2–7 | 4 | required |

Add `NativeColorMasterV2 {}` to the current strict wire deserializer. Do not add Plan8. Appending the omitted optional field preserves historical JSON bytes and hashes.

`NativeFormatContract` remains the single private authority. Its private format enum should distinguish H.264, Master V1, and Master V2. The contract derives writer settings, suffix, receipt schema, encoded observations, decoded observations, and measurement validation.

For V2, the writer adds the complete Rec.709 dictionary. `NativeWriterSession::append_picture` must attach and immediately read back all three values with `ShouldPropagate` before every append. A missing key, wrong value, or wrong attachment mode fails that frame. No native object may cross the existing Rust channels.

The encoded-track loop must examine every nonempty compressed video sample. It must require one complete, exact, stable tuple before incrementing accepted evidence. The decoded-frame loop must make the same check on every output buffer. Both loops retain their current PTS, epoch, count, cancellation, EOF, and completion checks.

V1 remains a compatibility profile without a color claim. Fresh V1 verification must omit `video_color`, even when the framework infers decoded attachments. H.264 behavior and Receipt2 remain unchanged.

## Independent atom proof boundary

The external proof must bind the exact accepted `.mov` SHA and bytes. Its parser must select the video track and the `ap4h` sample entry. It must require exactly one `colr` child with `nclc/1/1/1` and reject missing, duplicate, truncated, conflicting, misplaced, and oversized controls.

This parser is proof tooling. It is not a production reader, replay dependency, or new codec registry. A future `nclx` representation fails the bounded proof until separately reviewed. Production V2 succeeds or fails on the exact encoded and decoded framework tuples.

## Mandatory implementation and proof requirements

1. Preserve exact legacy request, plan, receipt, verification, and artifact bytes. Include the current V1 Plan7 master and all historical Plan2–6 fixtures.
2. Test the V2 writer dictionary and every input attachment. Include a middle-frame missing-key, wrong-value, and wrong-mode fault.
3. Test every encoded-sample observation. Reject missing, partial, wrong, or changing tuples.
4. Test every decoded-buffer observation. Reject missing, partial, wrong, or changing tuples.
5. Validate the complete profile and receipt cross-product. Reject Receipt4 under V1 or H.264, older receipts under V2, and color evidence under Receipt2 or Receipt3.
6. Produce a fresh ordinary V2 export with a fresh build, plan, and Receipt4. Require all 72 output PTS and epoch values, decoder EOF, opaque output alpha, and unchanged source closure.
7. Apply the unchanged pixel policy. Require all 516 nonempty ROIs at 34 dB or higher. Keep 236 empty-region comparisons metric-free. Preserve all full-frame checks.
8. Require exact PCM24 sample count, layout, codes, source interval, output interval, clocks, and EOF for the 144,000-frame audio fixture.
9. Require public verification and completed replay to reproduce `video_color` exactly.
10. Run the independent atom proof against the exact accepted output. Include parser sensitivity controls.
11. Exercise active cancellation and Receipt4 publication coverage. Exercise the profile-derived finalizing recovery/readback seam. Retain earlier publication lifecycle evidence; a broad lifecycle or H.264 resweep is unnecessary because their flow is unchanged.

Publication may store Receipt4 only after complete native verification. Cancellation, fencing, staging, lease renewal, promotion, and publication ordering remain unchanged.

## Grafts and rejections

Graft Candidate B's direct statement that V2 adds metadata, not pixel conversion or managed color. Keep its explicit rejection of caller-supplied matrices, ICC profiles, gamma, and conversion flags.

Reject these choices:

- Candidate A's production recursive MOV parser and persisted container tuple.
- Candidate B's four duplicated counters and `decoded_tuple_digest`.
- Candidate B's external use of crate-private `ContentHash::document`.
- Any silent repair of `NativeColorMasterV1`.
- Any Plan8 format schema or second persisted output recipe.
- Any caller-controlled native color dictionary or attachment mode.
- Any unrelated reader redesign, codec restriction, or broad lifecycle resweep.

The bounded unit can claim the measured Rec.709 numeric encode/decode tuple and the independently observed `nclc/1/1/1` artifact representation. It cannot claim PNG color management, source gamut conversion, natural color, full-film readiness, playback, hearing, or creative acceptance.
