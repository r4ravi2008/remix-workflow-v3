# Implementation review A01

## Result

The first product behavior unit is not ready for acceptance.

The project aggregate has a sound revision transaction and a real native sample index. Three P1 defects can still produce a false export success or an incorrectly bound plan. Capability discovery also reports implemented behavior inaccurately.

P1 findings block this unit. P2 findings should be fixed before export execution or alternate representations are added.

## P1 findings

### 1. Replayed plans bypass current source verification

`Project::prepare_export` returns a stored plan at `crates/editor/src/project.rs:197-199`. This return occurs before `verify_assets` at line 200.

`replay_plan` verifies the request hash, plan hash, and project ID. It does not reopen or hash any blob in `source_closure`.

I reproduced the defect in an isolated copy of the A01 project state:

1. I truncated the imported AV1 blob after the original plan was stored.
2. I repeated the same `prepare-export` intent.
3. The command returned the stored plan with `replayed: true`.
4. A new intent rejected the same state with `asset_tampered`.

This behavior violates exact-source replay. An interrupted or externally damaged store can receive a successful replay receipt for unavailable bytes.

Required change:

- Verify every stored `source_closure` entry before returning a replayed plan.
- Check both byte length and SHA-256 against the plan entry.
- Add a negative test that damages a blob between preparation and replay.

### 2. Canonical audio does not constrain the timeline audio

The compiler accepts every valid audio clip at `crates/editor/src/plan.rs:224-240`. It later adds the canonical asset to `used` at lines 259-261.

No check requires an audio clip to use the canonical asset. No check binds the consumed source interval to `AudioBinding.source_samples`.

A plan can therefore play WAV B while declaring WAV A as canonical. Both assets then appear in `source_closure`, which hides the mismatch.

The current A01 receipt happens to use the same WAV for both roles. The invariant is absent from the aggregate and compiler.

Required change:

- For this behavior unit, require the timeline master audio to use `canonical_audio.asset`.
- Require each consumed source interval to remain inside the canonical source interval.
- Model an explicit mix or replacement relationship before supporting different assets.
- Add a negative two-WAV test for a mismatched canonical binding.

### 3. First-sample decode is reported as range decode capability

`media::probe` calls `decode_first` at `crates/editor/src/media.rs:249`. That probe requests one BGRA sample and then stops.

The result becomes the asset-wide `native_decode` boolean. The plan compiler treats that boolean as authority for every selected sample at `crates/editor/src/plan.rs:145-161`.

The A01 AV1 receipt contains a real 2,277-sample presentation index. Its warning states that native decode covered only the first sample. The prepared plan selects 48 ordinals.

The separate A02 experiment proves 24 reopened H.264 frames and 48,000 decoded audio frames. It does not prove decoding those 48 AV1 source ordinals. It is not bound to the A01 asset, revision, or plan.

Required change:

- Replace `native_decode: bool` with scoped evidence.
- Record `FirstSample`, verified ordinal ranges, or `FullAsset` with a receipt identity.
- Require evidence that covers every selected ordinal before declaring the plan executable.
- Keep indexing support separate from decode support in capability output.

## P2 findings

### 4. Capability discovery is internally inconsistent

`crates/cli/src/main.rs:11` omits `project.prepare-export` from `operations`. The CLI dispatch implements that operation at lines 32-35.

The same response lists `immutable_export_plan` as planned. A01 already compiles, persists, hashes, and replays immutable plans.

The response cannot express verified or unsupported scope. It also omits the bounded AV1 probe and the unsupported VP9 result.

Required change:

- List every callable operation, including `project.prepare-export`.
- Report each capability as `Planned`, `Implemented`, `Verified`, or `Unsupported`.
- Attach fixture, receipt, build, host, and coverage scope to verified claims.
- Report plan preparation separately from future plan execution.

`BuildIdentity` also records only `macos` and a static backend label. Add the macOS build and framework identity before native execution receipts depend on it.

### 5. The explicit authority-to-representation map is missing

The synthesis requires an explicit map between authoritative sources and native representations. The implemented model has lineage through `Origin`, but no representation binding or time map.

The current AV1 identity path does not expose the gap. A future proxy or transcode could become a clip asset without preserving source authority.

Required change:

- Add a `SourceBinding` or `RepresentationMap` aggregate value before proxy support.
- Bind authority hash, representation hash, source interval, representation interval, and verification receipt.
- Make clips refer to that binding when the authority and decoded representation differ.

### 6. Failed imports leave staging files

`stage_import` removes its staging file only when the import succeeds at `crates/editor/src/project.rs:185-188`.

Size, hash, probe, and hard-link failures leave an intentless file in `staging`. The accepted design allows orphan content-addressed blobs with garbage collection. It does not justify untracked staging files.

Required change:

- Attempt staging cleanup on both success and failure.
- Preserve the original import error when cleanup also fails.
- Add failure tests that assert the staging directory is empty.

### 7. Commit replay trusts an unvalidated receipt body

The `replay` helper at `crates/editor/src/project.rs:396-415` checks only the stored request hash. It deserializes the receipt and returns it without checking project identity or referenced revision.

The store detects revision and plan tampering elsewhere. Stable intent replay should apply the same standard.

Required change:

- Verify the receipt project and revision against the current project store.
- Recompute or inspect the referenced revision before returning the replay receipt.
- Add a tampered-receipt replay test.

### 8. The append-only decision log is stale

`docs/decisions.tsv:5` still reports the native experiment as `runtime pending`. The synthesis and A02 measurements record successful decode, encode, and independent reopen checks.

Required change:

- Append a new experiment outcome row.
- Preserve the earlier row as historical state.
- State the exact bounded measurements and keep `watched: false` and `heard: false`.

## Contract checks that pass

- Project creation produces a stable initial immutable revision.
- A commit stages imports before the database transaction.
- The transaction rechecks the head before appending the revision, intent, and new head.
- Concurrent edits produce one winner. Invalid edits do not advance the head or consume the intent.
- Stable commit intent replay survives later head movement. Changed requests produce `intent_conflict`.
- Movie indexing reads the compressed sample stream to completion.
- The index stores rational PTS, DTS, duration, and presentation order.
- The A01 receipt contains 2,277 unique presentation samples from the actual AV1 asset.
- Source samples and timeline samples remain distinct fields.
- Fresh plan preparation verifies project blobs before compiling.
- Plans bind revision, timeline, settings, source closure, selected ordinals, audio uses, and renderer identity.
- Plan IDs are content hashes. Stable plan intents replay the same plan ID.
- Persisted asset origins retain source lineage and generated-receipt fields.

## Evidence assessment

`native-project-a01` proves project creation, import, canonical binding, timeline commit, plan preparation, and stable plan replay. The initial failed bind receipt remains useful failure evidence.

`native-encode-a02/independent-measurements.json` proves a bounded native round trip:

- 24 reopened video samples with exact `n/24` presentation timestamps.
- 48,000 decoded stereo PCM frames after AAC trim.
- Zero-sample waveform lag.
- Channel correlations of 0.9999769 and 0.9999687.
- First-frame PSNR of 42.70 dB.

These measurements do not establish watched, heard, or creative acceptance. They also do not establish arbitrary source codec support or full A01 selected-range decoding.

## Validation and review limits

`cargo test --locked --workspace` passed all current tests. `cargo clippy --locked --workspace --all-targets -- -D warnings` also passed.

Cross-family model review was unavailable. This document does not claim one.
