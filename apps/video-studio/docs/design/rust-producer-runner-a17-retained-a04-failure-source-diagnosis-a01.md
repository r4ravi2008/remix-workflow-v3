# Runner A17 retained A04 failure diagnosis

## Disposition

The retained A04 attempt remains failed. It establishes no native or product acceptance.

The failure combines one caller parser omission, control publication races, and stale control expectations. The `different_executable` result does not show a production vnode-check bypass. That control never delivered its replacement at the production pre-spawn gate.

This review is source-only, same-model, and nonblind. It used the preserved failed attempt and ROOT forensic readback. It did not modify frozen source or execute a compiler, control, or native process.

## Frozen identities

The current source files match their rows in `source-manifest-a17.json`.

| File | Bytes | SHA-256 |
|---|---:|---|
| `rust-producer-runner-a17/source-manifest-a17.json` | 122137 | `4a018cbf2547b58c86993e59829a6b87fe7e40604681190bed006669e8dbd48b` |
| `rust-producer-runner-a17/src/lib.rs` | 200612 | `62974194b1544d14660ee84d102191ae7e963c15b3040a83c090dbadc05e34c8` |
| `rust-producer-runner-a17/src/a05_control_extension.rs` | 74344 | `7e58e97731229469ca7563fa6ffc66fceac3287cb835a7be887f4ecd43a676dc` |
| `rust-producer-runner-a17/src/a17_launch_controls.rs` | 21491 | `52bafc6f3617bd73e422922f4bc5fa1d41aa0ed5c26ab5efa69591638059393d` |
| `rust-producer-runner-a17/src/a17_focused_controls.rs` | 67915 | `a38994597ac1adb3ba120ec1df9095459d7668be3a382f7cda62a718c601afd6` |
| `rust-producer-runner-a17/runner-contract-a17.md` | 10209 | `a8b4443c29e3b26e7bce1219f614b7b0b4adc1e52fc9d77a75412b684bde8b07` |
| `rust-producer-runner-a17/output-schema-a17.md` | 6992 | `1f5997844e4adb17e50c611060d5465af1ee80481aa3d7a870dc1bda5764e411` |
| `rust-producer-runner-a17-retained-control-preparation-a04/native_runner_retained_controls_a17.py` | 87927 | `198f5e7a6a9213800da70a05aeb9b35c71ebabb4624d7a1224aa7bb9e6da661f` |

The preserved evidence used for this diagnosis is:

| Evidence | Bytes | SHA-256 |
|---|---:|---|
| `control-attempt-a17/control-report-a17.json` | 171054 | `1dd440119fa52a83e99ec2cb974847aa0c1533d5f9ca4104954883c3e253149e` |
| `control-attempt-a17/focused/focused-control-report-a17.json` | 170593 | `49785811e6707c03c8fafc723385eb9703a83ebae338209b6ec1ef89e6e3b53b` |
| `control-attempt-a17/a04-lifecycle/control-report-a03.json` | 6501 | `9fa57c4b8cf65fefc0ac84a79e8e3bc4133785312e1d942cc94885c966973508` |
| `rust-producer-runner-a17-retained-a04-failure-root-readback-a01.json` | 702970 | `bf6babf40e7ff00222b4453c0d33d7ca46cd26a9f886f481fb4a5e19660f49ae` |

ROOT's forensic readback held 560 regular files totaling 60,627,297 bytes. It found 315 valid JSON files, four intentional malformed sentinels, and twelve valid closure-reference joins.

## Findings

### 1. The retained caller omits one intentional malformed JSON file

`native_runner_retained_controls_a17.py:298-311` declares three malformed JSON sentinels. Lines 1217-1244 reject any undeclared malformed JSON file.

The omitted file is:

`focused/cases/authorization_path_collision/output-parent/collision-run/authorization.json`

Its exact content is `authorization-collision-sentinel\n`. The file is 33 bytes. Its SHA-256 is `a3b8e30e1f8de716401feff51dc0589442e7f4012d17905883bd24eb1a776916`.

This omission directly caused `unparsed_actual_report_json`. A successor must bind this fixed relative path and require exactly four intentional sentinels. Every other `.json` file must still parse strictly.

### 2. Final-name publication exposes incomplete authorization and sidecar bytes

Production creates `authorization.json` through `write_exclusive_bytes` at `src/lib.rs:1043`. The helper creates the final name before `write_all` and `sync_all` at lines 2219-2231.

Controls poll only `authorization.json.is_file()` at `src/a05_control_extension.rs:1058-1062`. A control can therefore read or mutate incomplete bytes. A mutation can also precede production's final identity capture at `src/lib.rs:1050-1052`.

The sidecar control has the same publication order. `control_write_new_a03` creates `authorization-review.json` before writing and syncing its bytes at `src/a05_control_extension.rs:1588-1597`.

The preserved complete sidecars parse successfully. Runtime reports contain `authorization_review_invalid`, `authorization_review_drift`, and `authorization_identity_failed`. These facts support a publication race.

The successor needs a dedicated complete-file publisher for these two concurrent artifacts. It must write and fsync staged bytes first. It must then publish the final name exclusively and atomically. Production must capture the final authorization identity before any consumer can mutate the file.

The repair must preserve existing collision sentinels. It must not weaken strict JSON parsing or change terminal-prefix evidence semantics.

### 3. Mutation controls bind review approval to the wrong authorization bytes

`src/a05_control_extension.rs:1061-1084` captures the original authorization, mutates the final file, and then recaptures mutated bytes for the sidecar.

Production therefore reports `authorization_review_mismatch` before the intended `authorization_drift` check. Mutations that race final identity capture report `authorization_identity_failed`.

The successor needs an explicit authorization-publication-complete rendezvous. The sidecar must bind the original captured authorization. The control must apply its declared mutation after that capture.

Each negative control must record that its exact mutation was delivered. An undelivered mutation cannot satisfy the control.

### 4. Executable and cwd replacements wait at the wrong gate

`src/a17_launch_controls.rs:50-55` routes same-byte replacement, different-executable replacement, and cwd replacement to `A09_GATE_STOPPED`.

Production exposes the deterministic replacement seam at `A09_GATE_PRESPAWN` in `src/lib.rs:3483`. The stopped gate occurs after the original executable has loaded.

For `different_executable`, the replacement remained at its source path. The original private executable retained SHA-256 `008fa6936c107095d0d1b3d05d7f5cdda79490860598f571ec0021ac415e03d7`. No `different-executable-original` backup existed.

The unchanged executable started, stopped, resumed, returned zero, reaped, and wrote its user-code marker. This outcome shows that the control did not deliver the intended replacement.

Map all three path replacements to `A09_GATE_PRESPAWN`. Keep paused cancellation at `A09_GATE_STOPPED`. Require delivered-mutation evidence before evaluating the expected vnode or cwd rejection.

### 5. The FIFO lifecycle control ignores the saved terminal on the expected error path

The FIFO run saved a failed `authority_missing` terminal. It started no child and completed in bounded time.

Production then returns `Err(AuthorizationNotReviewed)` because it has no authorization artifact. `src/a05_control_extension.rs:907-937` evaluates only the `Ok` result.

The successor must inspect the saved terminal on this exact `Err` path. This is a lifecycle assertion defect, not a production authority failure.

### 6. Three focused expectations do not match the intended production stage

The same-byte new-inode root, peer, and sidecar cases saved `authorization_review_drift`. Each child had started and reaped before the review-gate mutation. The generic helper incorrectly requires `started=false`.

Those cases must require `started=true`, `resumed=false`, `reaped=true`, and resolved cleanup.

The path-anchor case saved `run_root_parent_drift`. `focused_code_from_report_a05` maps this code to generic `failed`, while the case expects `authorization_path_drift`.

The successor must preserve and expect the exact saved `run_root_parent_drift` code. The postflight drift case must run again only after publication ordering is repaired.

## Corrected sidecar-schema assessment

The prior provisional diagnosis incorrectly claimed that `AuthorizationReview` lacked strict unknown-field rejection.

The current frozen source disproves that claim. `src/lib.rs:673-685` places `#[serde(deny_unknown_fields)]` directly on `AuthorizationReview`. The frozen manifest binds the exact `src/lib.rs` bytes and SHA-256 listed above.

No production schema repair is required. No duplicate attribute should be added.

The current focused mutation enum covers hash, alias, and identity changes. It does not include an unknown top-level sidecar-field negative. That is a bounded test-coverage gap only. A successor may add one strict-parser negative, but the production contract is already satisfied.

## Narrow successor scope

The runner successor needs changes only in:

- `src/lib.rs` for complete authorization publication and the publication-complete ordering point.
- `src/a05_control_extension.rs` for atomic sidecar publication, original-snapshot review binding, delivered-mutation evidence, and FIFO error-path inspection.
- `src/a17_launch_controls.rs` for the pre-spawn gate mapping and delivered-mutation check.
- `src/a17_focused_controls.rs` for exact process-shape and path-anchor expectations.
- The successor README, contract, output schema, rationale, recipe, and source manifest.

The retained-caller successor needs the fourth exact malformed sentinel in its Python source. Its contract, rationale, receipt, recipe, and manifest must bind the new runner and caller bytes.

The 21 pure controls need no semantic change. All current failed evidence must remain preserved. A new attempt requires separate source review and compilation first.
