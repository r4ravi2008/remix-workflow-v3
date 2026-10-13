# Implementation review A02

## Result

The exact A02 artifact passes the bounded technical export checks.

All three A01 P1 fixes are present and passed isolated behavioral checks. Export fencing, finalization recovery, and intact completed replay also passed.

The behavior unit is still not ready for aggregate acceptance. Completed replay trusts mutable receipt fields and can return false technical and human-acceptance claims.

## Blocking finding

### [P1] Completed replay trusts an unhashed receipt payload

`ArtifactReceipt` contains technical measurements and mutable acceptance booleans at `crates/editor/src/exports.rs:17-30`.

Completed replay checks project, plan, revision, and renderer at lines 97-111. It rehashes and reopens the output at lines 113-122.

The fresh `movie::verify` result is discarded. The stored `technical`, `watched`, `heard`, and `creative_accepted` values are returned unchanged.

The finalization-recovery branch has the same issue at lines 166-190.

I reproduced this defect in an isolated copy:

1. I changed the stored video and audio counts to `1`.
2. I changed both channel correlations to `0.0`.
3. I changed `watched`, `heard`, and `creative_accepted` to `true`.
4. I replayed the same completed export intent.
5. The command rehashed and reopened the correct movie.
6. The command returned every forged field with `replayed: true`.

This violates the selected design. Candidate A explicitly rejects a trusted mutable acceptance flag.

Required change:

- Remove watched, heard, and creative acceptance from the export receipt.
- Store human review as immutable records bound to revision, plan, output hash, renderer, actor, and evidence class.
- Give the stored artifact receipt its own content identity and verify it before replay.
- Compare structural measurements with fresh verification before returning a completed receipt.
- Return fresh measurements as a separate verification record when floating measurements can vary slightly.
- Add a replay test that mutates technical and review fields in the stored receipt.

The genuine A02 receipt keeps all three acceptance fields false. This defect does not invalidate that file's measured technical result.

## A01 finding disposition

| A01 finding | A02 status | Evidence |
| --- | --- | --- |
| Replayed plans bypass source verification | Fixed | `prepare_export` calls `verify_plan_sources` on both replay paths. A truncated copied AV1 blob returned `asset_tampered`. |
| Canonical audio does not constrain timeline audio | Fixed | `plan.rs:271-309` requires the exact asset and exact timeline-to-source offset. Isolated asset and offset mismatches returned `canonical_audio_mismatch`. |
| First-sample decode authorizes a selected range | Fixed for schema 2 | `prepare_export` measures selected ranges before hashing and saving the plan. The persisted A02 plan binds 48 decoded samples and exact PTS checks. |
| Capability discovery is inconsistent | Partly fixed | Both export operations are listed. Verification receipts and unsupported states remain absent. |
| Authority-to-representation map is missing | Open | `Origin` preserves lineage, but the aggregate still lacks an authority/representation/time-map binding. |
| Failed imports leave staging files | Retracted | `fs::remove_file(&staging)` is evaluated unconditionally at `project.rs:187`. An isolated `asset_size` failure left the staging directory empty. |
| Commit replay trusts its receipt body | Fixed | `project.rs:436-459` verifies project, revision body, sequence, parent, hash, and snapshot validity. |
| Decision log remains stale | Fixed | `docs/decisions.tsv` now appends the bounded product verification and preserves the historical row. |

The coarse import-time `native_decode` boolean remains in `MediaDescriptor`. Schema-2 preparation no longer treats it as selected-range evidence by itself.

## Schema-2 plan verification

The stored A02 plan has schema `2`. Its recomputed SHA-256 equals plan ID `cdeadd63dd1c30743a07dc2c7abc0a37f4de4b5e8217fc0a1f3cc1d06f169afb`.

The plan stores one decode-evidence record:

- Asset: `a2247e96ab4335eb6b365ef52b6203e53377c6cf317ebb2e156789e6bd470b7f`.
- Source range: presentation ordinals `0..48`.
- Decoded samples: `48`.
- Indexed PTS comparison: passed.
- Decoder executable: `6f79ea34e8a2bf95e7e030e9b98672156e8ca05d5052d64106d61bfc9e7c8f6a`.

`project.rs:203-225` compiles the plan, measures selected decode coverage, rehashes the plan, verifies source bytes, and then inserts it.

The import-time sample index remains authoritative for source timing. Both decode proof and export execution compare decoded PTS against that immutable index.

## Export lifecycle verification

All behavioral probes used copied stores and copied artifacts.

- An intact completed export replayed successfully and set `replayed: true`.
- An active owner with a future lease returned `export_in_progress`.
- A paused worker lost its epoch after a simulated takeover and returned `worker_fenced`.
- The newer epoch remained unchanged after the stale worker failed.
- A stale finalizing job adopted an existing verified artifact and completed at the next epoch.
- A stale finalizing job with no promoted artifact rerendered and completed at the next epoch.

The rerender produced a different output hash for the same plan. Native H.264/AAC encoding is not byte-deterministic here. Exact-file review must therefore bind the completed output hash.

### Remaining recovery limits

The job lease is fixed at 240 seconds at `exports.rs:158`. There is no lease renewal or cancellation checkpoint.

Fencing preserves promotion correctness after lease expiry. Longer future renders can still duplicate expensive work.

A fenced worker also leaves its staged MP4. The isolated takeover left `export-panja-scratch-export-native-roundtrip-v3-21.mp4` in staging.

Failed jobs are terminal for the same intent at `exports.rs:126-133`. The current API requires a new intent for every retry.

Required follow-up before longer exports:

- Renew active leases through fenced compare-and-update operations.
- Add cancellation checks during decode, encode, and reopen loops.
- Reconcile or collect staged files from old epochs.
- Define which failure classes permit another attempt under the same logical intent.
- Preserve attempt history instead of overwriting one job row.

## Product-bound native evidence

`product-export-a02.json` binds the artifact to the project, revision, plan, renderer, output hash, and output size.

The product reopened the exact file and measured:

- 48 video frames at 1920 by 1080.
- 96,000 decoded stereo PCM frames.
- Channel correlations of 0.9999705561 and 0.9999708587.
- Full output-video decode completion.

Independent inspection confirms:

- MP4 video codec `avc1` with 48 samples and exact two-second timing.
- MP4 audio codec `mp4a` with 96 AAC packets and 98,304 encoded ticks.
- Native-reader trim to 96,000 presentation samples.
- Zero-sample best lag on both channels.
- The recorded output SHA-256 and 1,182,950-byte size.

These are technical measurements only. Watched, heard, and creative acceptance remain false.

The independent report contains `productExport: false`. That field conflicts with the report name and the linked product receipt. Its meaning needs a schema or correction before capability discovery cites it.

## Material remaining gaps

### Product verification does not measure the output codecs

`movie::verify` decodes frames and PCM but does not read output codec identifiers. `NativeMeasurements` also omits codec and sample-table fields.

The independent report proves `avc1` and `mp4a` for this file. The product receipt alone does not prove those encoded formats.

Add codec, track count, duration, sample-table coverage, and audio lag to a linked technical-verification record.

### Capability discovery does not expose verified evidence

`discover` now reports implemented operations and scopes. It still returns an empty `verifiedCapabilityReceipts` array.

It does not report VP9 as unsupported. Its native-export scope also omits identity geometry, unity gain, zero pan, and complete-coverage restrictions.

Report exact `Verified` and `Unsupported` states with receipt, build, host, fixture, and coverage identities.

### The canonical master remains partly declarative

The bound master is the 24-bit stereo 48 kHz WAV with 13,104,000 frames. The A02 timeline consumes its first 96,000 frames.

Channel labels remain unmeasured. The plan records an explicit left/right interpretation instead.

The different 16-bit, 261.56-second metadata WAV is absent from the stored lineage. The bounded export does not reconcile that historical source.

### General editor and review behavior remain planned

The authority-to-representation map is still absent. Proxy or transcode work must not bypass the authoritative source clock.

Masks, motion, color, typography, retiming, layered composition, and general audio mixing are not implemented.

`Project::execute_plan`, `record_review`, and `evaluate_policy` from the synthesis are not exposed yet. Tenant-aware Effect and GPU orchestration also remain planned.

### Regression coverage is incomplete

The checked-in tests do not cover the three A01 P1 fixes or export job transitions.

Add automated tests for source-closure replay, canonical mismatch, decode-evidence persistence, fencing, finalization recovery, completed replay, and receipt tampering.

## Validation and review limits

I reviewed every current Rust runtime file in `crates/editor/src` and `crates/cli/src/main.rs`.

`cargo test --locked --workspace` passed. `cargo clippy --locked --workspace --all-targets -- -D warnings` passed. `cargo fmt --all -- --check` passed.

The successful product receipt, completed replay receipt, independent report, container report, stored plan, and copied job states were inspected.

The Objective-C exception boundary now encloses native operations inside the asynchronous track callback. A02 did not force a new native exception, so structured exception conversion is code-inspected rather than failure-injected.

Cross-family model review was unavailable. This document does not claim one.
