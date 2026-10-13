# Implementation review A03

## Result

No P1 remains in the A02 receipt-integrity defect.

The bounded single-clip behavior unit can now support the next sequential multi-clip unit. The new unit must preserve the plan and receipt contracts described below.

`product-export-a04.json` did not succeed. It rejected a technically valid staged file because the verifier required raw compressed H.264 PTS to start at zero.

`product-export-a06.json` supersedes that failed attempt. It produced, promoted, reopened, and freshly verified the exact H.264/AAC artifact.

## A04 failure and corrected native track evidence

The raw H.264 sample interval is `50/600` through `1250/600`. Its span is exactly two seconds.

The decoded presentation interval still starts at zero. All 48 decoded frame PTS values equal `n/24`.

The current verifier names these values `raw_sample_pts_start` and `raw_sample_pts_end`. It checks their span instead of requiring a zero raw start.

This distinction is correct for reordered H.264 output. The compressed reader clock does not replace the decoded presentation clock.

The raw AAC interval is `0/48000` through `98304/48000`. Native decode trims 2,304 AAC padding frames and returns exactly 96,000 PCM frames.

The receipt records `audio_track.sample_buffers: 1`. That value is AVAssetReader callback aggregation, not an AAC packet count.

The product verifier does not use that value as packet-count evidence. Independent container inspection remains the authority for sample-table packet counts.

## Exact A06 artifact

The successful artifact has these bindings:

- Project: `panja-scratch`.
- Revision: `fe55a404b2f7af51b9f3bef1685f3313a92c7b362504ac3f86d358457f0c14ae`.
- Plan: `6a287ff05ccb41447e4732ea9e5b794672c0330b8e92380b0b7b07ddbf407225`.
- Output: `194d2c86c34674875574c99fbb00c006445674d690edcc64cf807a6be0127638`.
- Output bytes: `1,182,950`.
- Artifact receipt: `deffc98d2c3b43a750c7e5914ef76dae8bc735c78eb434fd4271949de0d315f6`.
- Producer executable: `4436311488411ce90673a4a8c02fd1632af9dd6e125c964f5b1f561c5049a4dc`.
- Initial verification: `e5eee80146c3bde5ddc37939ad53b6c1606089461d8040ba95acb9b31e6cf6db`.

The artifact receipt measures 48 video frames, 96,000 stereo PCM frames, and 1920 by 1080 pixels.

Its channel correlations are `0.9999705560560641` and `0.9999708586933663`.

`independent-product-verify-a04/report.json` passes all 21 recorded technical checks. It reports `productExport: true`.

These results are technical evidence only. Watched, heard, and creative acceptance remain false.

## Receipt and replay contract

`ArtifactReceipt` schema 2 contains project, revision, plan, renderer, output, byte count, and technical measurements.

It contains no `watched`, `heard`, `creative_accepted`, or `replayed` fields. Serde also rejects unknown fields.

`StoredArtifact.receipt_id` hashes the canonical receipt bytes. The same bytes exist in the separate `receipts` content-addressed store.

Replay recomputes the receipt identity. It also verifies the immutable receipt document, output path, output bytes, and output SHA-256.

Replay then reopens the output. It compares fresh counts, formats, dimensions, track clocks, and correlations with the producer receipt.

`ArtifactVerification` records the fresh verifier separately. `ExportResult.replayed` reports operation status outside the immutable artifact receipt.

The real `product-replay-a03.json` passes under executable `e2826d70f18e52e7f86f16576576619487c7492ccc3734f2a4c2daf742f8d038`.

That replay returns fresh verification ID `cf3ca3069988fd608ccdfd27d2d653e043fea28459d26c89fe41684482c5ce96`.

The producer and replay verifier identities differ. The replay still preserves the original artifact receipt and output hash.

The final reviewed binary is `99a28ee11a467dd6a204322f13fb8b97ba7f174bc8679e5637875b3e5144f854`.

Its new `project.verify-export` operation replayed A06 successfully in an isolated copied store.

That replay measured 48 video frames and 96,000 PCM frames. It also migrated the copied schema-3 store to schema 4.

Scoped discovery returned `Verified` for the exact completed artifact. Its scope explicitly excludes playback and creative acceptance.

The `serde_json` `float_roundtrip` feature is required here. It preserves the measured correlation doubles across receipt parsing and reserialization.

## Negative tamper verification

All negative probes used copied stores and copied artifacts. No original project state was changed.

An intact copied-state replay first passed with fresh native measurements.

Three independent mutations then produced the expected failures:

1. Changing embedded technical fields without changing `receipt_id` returned `job_tampered`.
2. Changing bytes in the immutable receipt document returned `asset_tampered`.
3. Rehashing a forged receipt and installing its matching CAS document returned `measurement_changed`.

The third probe passed document integrity checks. Fresh native verification still rejected its forged video-frame count.

These probes cover both content integrity and truthful replay. A coordinated new hash cannot convert changed claims into fresh measurements.

## P1 disposition

| A02 concern | A03 status | Evidence |
| --- | --- | --- |
| Mutable technical fields replay unchanged | Fixed | Fresh native measurements are compared with the immutable producer receipt. |
| Renderer receipt can claim human acceptance | Fixed | Human and replay flags are absent, and unknown fields fail deserialization. |
| Receipt has no content identity | Fixed | The receipt ID equals the SHA-256 of its CAS document. |
| Replay does not prove the exact output | Fixed | Replay verifies output path, byte count, SHA-256, and native decode measurements. |
| Product receipt omits encoded format evidence | Fixed for this unit | The receipt records H.264 `avc1`, AAC `aac `, raw track clocks, and audio layout. |
| Float parsing can change the receipt identity | Fixed | The final build enables exact JSON float round trips, and the historical A06 receipt replays. |
| Verified evidence is absent from capability discovery | Fixed | Scoped discovery calls `project.verify-export` and returns exact receipt and verification evidence. |
| Long exports can outlive their lease | Fixed | A fenced renewal worker extends the claim every ten seconds and stops on cancellation or epoch loss. |
| Export attempts overwrite their only history | Fixed | Schema 4 stores each epoch in `export_attempts`. |
| Handled failures leave the current staged movie | Fixed | The error path removes the owned epoch staging file. |

## Requirements for sequential multi-clip execution

Changing `validate_profile` to accept more clips is insufficient.

The next unit must keep these invariants:

- Each source asset keeps its own compressed sample index and native reader.
- Each selected range receives decode evidence before the schema-2 plan is saved.
- Timeline frame positions select output PTS. Source PTS only selects frames within its authoritative asset index.
- The renderer checks every decoded source PTS against that asset's immutable index.
- Plan source closure includes every clip asset and its transitive lineage.
- Canonical audio remains the exact bound asset and timeline-to-source interval.
- Interrupted jobs retain epoch fencing before artifact promotion.
- Each promoted output receives a new immutable artifact receipt and fresh verification record.
- Later human review binds the exact output hash, receipt, revision, plan, and renderer.

The current renderer correctly rejects multi-clip execution. No evidence in A06 proves sequential clip boundaries yet.

## Material non-P1 gaps

A late cancellation can be recorded as fencing. This race occurs after the last control check but before the `finalizing` update.

The main row becomes `cancelled`, but the caller receives `worker_fenced`. The attempt row also records `fenced`.

Promotion remains blocked. Derive the returned error and attempt state from `cancel_requested` when the guarded update changes no row.

`project.verify-export` joins the export and plan by project and intent. It does not compare their stored request hashes.

The plan, receipt, source closure, and output remain verified. A corrupted intent-to-request association could still escape this intent-only verifier.

Handled failures now remove their epoch staging file. Process death can still leave staging files, including the historical A04 and A05 files.

Failed or cancelled jobs remain terminal for the same intent. A new attempt requires a new stable intent.

Checked-in tests cover receipt identity, unknown review fields, measurement comparison, lease renewal, and cancellation signalling.

They do not run a real-media completed replay, cancellation race, migration, discovery, or CAS-tamper integration case.

Exact-file human review, authority-to-representation mapping, tenant orchestration, and general editing remain planned.

## Validation and review limits

This review is pinned to binary `99a28ee11a467dd6a204322f13fb8b97ba7f174bc8679e5637875b3e5144f854`.

Sequential multi-clip edits started after this review boundary. They are not evaluated here.

`cargo test --locked --workspace` passed 15 tests.

`cargo clippy --locked --workspace --all-targets -- -D warnings` passed.

`cargo fmt --all -- --check` passed.

I inspected the A04, A05, A06, replay, receipt-CAS, and independent-verification artifacts.

I also inspected the current editor, CLI, and receipt tests relevant to export and replay.

No normal-speed watch or listen was performed. No creative acceptance is claimed.

Cross-family model review was unavailable. This document does not claim one.
