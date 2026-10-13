# Alpha implementation review A02

Status: read-only follow-up to `alpha-implementation-review-a01.md`. The selected
Plan7 verification and recovery repairs are present. No runtime, fixture, proof output,
metadata, or historical document was changed. Cargo, tests, Clippy, release builds,
and native output were not run in this review.

## Result

No remaining P1 implementation blocker was found in the repaired paths.

`Project::verify_export` now accepts schemas 2 through 7 at
`apps/video-studio/crates/editor/src/exports.rs:850-858`. It still verifies the plan
document hash and project identity before `verify_plan_sources`, receipt binding, and
reopened native output verification.

`Project::reconcile_export_staging` now accepts schemas 2 through 7 at
`apps/video-studio/crates/editor/src/exports.rs:1247-1255`. It sends schema 7 through
`plan::validate_decode_evidence` at lines 1257-1259. Schemas 2 through 6 retain their
previous `validate_picture_mapping_cancellable` path at lines 1259-1261.

The remaining acceptance limitation is proof scope. The full 72-frame independent
observer remains `#[ignore]` at `apps/video-studio/crates/editor/src/layers.rs:904-906`,
and its reference summary constant is still `REFERENCE_SHA_AWAITING_FREEZE` at line
909. The focused public test uses the existing H.264 profile. It does not establish
the pending NativeColorMasterV1 72-frame reference proof.

## API and test review

The public alpha test at
`apps/video-studio/crates/editor/tests/project_invariants.rs:389-497` uses the actual
workflow:

1. `Project::commit` imports one alpha PNG and canonical audio.
2. `Project::prepare_export` produces schema 7, canvas placement, one alpha evidence
   record, and no duplicated alpha fields on `VideoUse`.
3. `Project::export` writes a 24-frame public export and binds its receipt plan ID.
4. `Project::verify_export` reopens the completed artifact and returns the same receipt.
5. A second `Project::export` replays the completed intent and returns the same receipt.

The repaired staging test at
`apps/video-studio/crates/editor/src/exports.rs:583-638` creates isolated valid and
forged schema 7 plans. Valid evidence is reclaimed. Missing `source_alpha_id` retains
the stage and reports `invalid_decode_evidence`. The test therefore exercises the new
central recovery validator instead of checking only schema or mapping shape.

The source also retains the single-alpha-without-placement and unused-alpha-ancestor
checks. The former normalizes canvas placement and the latter remains schema 3 with an
opaque evidence record. Plan validation still rejects duplicate Plan7 evidence through
set cardinality and ordered asset equality. No stale `2..=6` allowlist remains in
production code; the only `2..=6` occurrence is the intentional legacy branch in
`plan.rs:594`, with the intentional mask comparison at `plan.rs:608`.

Native output checks remain frame-scoped. `movie.rs:999-1019` checks every decoded
output sample through `pixels::require_opaque_native`, then requires the planned frame
count and completed reader status. This confirms the output alpha guard exists; it does
not substitute for the pending independent native proof.

## Remaining limits

- Native_design_a reports the focused tests, Clippy, and release build passing. This
  review did not rerun those commands.
- The ignored 72-frame observer still depends on an external frozen reference. Its
  current source code claims `ordinaryCliProducer: false`, and its proof is therefore
  not an ordinary CLI acceptance result.
- The independent reference repair, ordinary native output acceptance, full 72-frame
  pixel comparison, normal-speed watch, hearing, and creative acceptance remain
  outside this follow-up.
- No new alpha arithmetic, ownership, cache lifetime, source lineage, output opacity,
  or evidence-identity defect was found in the repaired source.

## Current source hashes and drift

Native_design_a confirmed that the previous unstable files are now frozen:

- `alpha_picture.rs`: `3cbf31081a7cf0c72e71649592a4808445819b41cd58e0b24ef8c65067c381a5`
- `image.rs`: `6acb1310003874d2233a885113649f34aef69c4af14694b5357d53884269eca2`

The following files changed after A01 because of the repair and focused tests:

- `exports.rs`: `de8e3c74ee372f5aead539b6a0690639856ab4e7f82f1b9b36d62aafcc3eb1cf`
- `layers.rs`: `c3c7ce86573e3f61da8bddec830dc0eea526efb0d02cc08077a238d6fb3e9988`
- `tests/project_invariants.rs`: `b0b489854303f8093fe6cf0feff0e0b4694c2beea641581d43bab357051ebda4`

The remaining reviewed runtime hashes are stable against A01:

| File | Current SHA-256 |
| --- | --- |
| `src/composition.rs` | `426322dd9a8188bd90c93e409373a739d52edeaac6c7eded4b0a8b01f1ff4810` |
| `src/framing.rs` | `c4e6082146f276f6838af468240c8834e506aecb28cf0b01c2c9c3ac65009888` |
| `src/mask.rs` | `a1cd2c87e15f806239172a63d398e7e692a5f8ca696818ed9190afc2beb8acaf` |
| `src/media.rs` | `490fe7871d4521fbd586810bd0ae13d84ca4288bb8c610035b9cb4ea72c91b4d` |
| `src/model.rs` | `eaad52b1b1c8624654b1308c6b582a9a74cb6ae4870f461eaad2c2f057dcc9b1` |
| `src/movie.rs` | `2ccd1408c3cbb061f004c37871730c5de55c5ed5f290c1db5602fb4d72ec8780` |
| `src/plan.rs` | `af959648ae11e936bf80ce9a502eabbf50f2069f3a4ea6445930b8892aa0e1ba` |
| `src/project.rs` | `a53132da6ff9ccdc6e21a32a7b73d0c833ffb7a35ff177815d6707129480698c` |
| `src/pixels.rs` | `9f2c1d86971d28ccbb89bb4678d2ea44cb8358e9d85e46451da4b7c7a2a02216` |
| `src/lib.rs` | `59e8107ac8e9afd11c551856e4cef606d5d85476d6d294455c498afda62a0b33` |

A01 remains unchanged at SHA-256
`adf2c470059873b4c84ac615a2dfa8dffe821610db42b109cfc8e364680b68bb`.
