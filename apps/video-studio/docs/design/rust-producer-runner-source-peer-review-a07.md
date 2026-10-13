# Rust producer runner A07 source peer review

## Disposition

**Rejected before compilation.** Four P1 findings and five P2 findings remain.

The package cannot produce build evidence in its current form. Two source errors prevent compilation. Two launch paths can also return without reaping a stopped child.

This review is source-only. I did not compile, import, test, launch, or execute any package code. I did not run a child, probe, bootstrap, native framework, media tool, GPU, or Resolve.

## Frozen receipts

I read all 15 package files and the complete A06-to-A07 source changes. I rehashed every source and external row.

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| `source-manifest-a07.json` | 42,965 | `4c96c09124cf52523e8cd8684c4f9317e7b6e3ee602eda0bdad38c40720f012d` |
| `src/lib.rs` | 134,767 | `c821380a85599676b219c04e9d3aec965b58308ab12f3e47e71939e2b708c081` |
| `src/a05_focused_controls.rs` | 53,850 | `7fef8ea41412fe7edd8a426c7bd06510a5b14b789a78766cffad74a80b7e3a01` |
| `src/a07_launch_controls.rs` | 7,321 | `92d8c7d8e76b3339c3c42a07cf86d2b4617a36f067102a83336bb53014e4904e` |
| `src/pure.rs` | 6,459 | `c2a6ab8948b2762034007cd50c5188c622b48a7ec9f5242e72ca13a7b06a8739` |
| `direct-build-recipe-a07.json` | 17,100 | `9746c51a0782f03772b5bdf24427ec9bdb14254bb51cc9560b49ee2d9d172c68` |
| `pure-fixtures-a07.json` | 13,145 | `a178ba8d050afaa0252b8cf3dd5e28c4e5e10f8ca53ca2d654f4bb6d4729855c` |
| `runner-contract-a07.md` | 6,974 | `117f5f058525790040f031c52e46a4e1d70c42250828465b56ac4ef4e276543c` |

The 15 source rows total 324,957 bytes. Their framed aggregate is `7b7e11a73c29663f639e1420855c09bf3fdf61a72a063f070e7ae1ff67d1a8d7`.

The 93 external rows total 10,519,216 bytes. Their framed aggregate is `d0c9b76e3cd1c9d8e8ae40ae779af93ec7ed622ee13defcbf284f6588b6aebca`.

Every row matches its current file. Every `(role, path)` pair is unique. I independently reproduced both documented aggregate encodings.

## P1 findings

### P1.1: The production library cannot resolve the cwd anchor predicate

`src/lib.rs:2374` calls `descriptor_anchor_matches` without a module qualifier. No function with that name exists in the local scope.

The available function is `pure::descriptor_anchor_matches` at `src/pure.rs:103`. The local wrapper is `same_directory_anchor` at `src/lib.rs:3040`.

The macOS production-library command compiles this branch. The call therefore produces an unresolved-name error.

Use one existing qualified predicate. Do not add a third cwd identity authority.

### P1.2: The controls library assigns a Boolean directly into `serde_json::Value`

`src/a05_focused_controls.rs:436-438` assigns a Rust `bool` through a `serde_json::Value` index.

The index assignment requires a `serde_json::Value`. Rust does not apply `From<bool>` implicitly for assignment.

Wrap the conjunction with `serde_json::Value::Bool` or `serde_json::Value::from`.

### P1.3: A rejected nonzero stop can remain alive while the report says it was reaped

`darwin_wait_for_stop` returns `Some(status)` for every status except the accepted zero-signal stop. See `src/lib.rs:2152-2164`.

`execute_child` treats every `Some(status)` as a terminal status. See `src/lib.rs:2635-2643`.

A `WIFSTOPPED` status with a nonzero signal is not terminal. `waitpid(..., WUNTRACED)` has not reaped that child.

The path sends no kill and performs no later wait. `darwin_child_failure` then sets `reap_completed=true` because `status.is_some()` at `src/lib.rs:2571`.

Separate exited or signalled statuses from rejected stopped statuses. Kill and reap a rejected stopped child before returning.

### P1.4: Process-group mismatch can return with the direct child unreaped

`darwin_spawn_suspended` gives direct-child cleanup one bounded second. See `src/lib.rs:2508-2528`.

When that wait expires, `initial_reaped` is false. `execute_child` closes the pipe and returns immediately at `src/lib.rs:2613-2627`.

No second bounded cleanup or final absence check exists. The direct child can remain alive, stopped, or zombie-owned by the runner.

This contradicts the contract statement that a mismatch kills and reaps without resume.

Keep the foreign-group restriction. Add a terminal direct-child cleanup state that cannot be reported as closed while the child remains owned.

## P2 findings

### P2.1: The nine launch controls are self-fulfilling predicate examples

`src/a07_launch_controls.rs` starts no child and calls no production launch seam.

`launch_variant_controls_a07` writes `observedCode` from `expectedCode` at line 165. The rows also invent marker, reap, SIGCONT, and user-code facts.

The `sourceFaultHook` field is true, but the production launcher has no corresponding fault hook.

The `region_deadline` row expects `loaded_region_walk_timeout`. Production has no region-walk deadline or that error code.

These rows can validate small pure predicates. They cannot qualify descriptor retention, suspended spawn, proc inspection, cancellation, SIGCONT suppression, kill, reap, or marker absence.

Use finite private production seams for the declared variants. Report measured outcomes from those seams rather than copying expected values.

### P2.2: The authorization variants test file drift, not field validation

The 17 grouped field variants rewrite `authorization.json` after the retained `AuthorizationArtifact` was created. See `src/a05_focused_controls.rs:82-179`.

`verify_authorization_file` detects the byte or identity change first. The variants therefore stop at `authorization_drift`.

They do not reach `validate_typed_authorization` for schema, operation, implementation, repetition, qualification references, policies, or false flags.

Keep the drift controls. Add coherent private inputs that reach the typed validator without weakening the artifact readback join.

### P2.3: Three repaired pure controls are disconnected from production decisions

`descriptor_read_is_allowed`, `esrch_termination_facts`, and `pipe_drain_completion` are called only from private controls.

Production file opening, signal handling, and pipe draining do not call these helpers. A passing control can therefore disagree with production behavior.

Move each decision behind a shared production predicate, or exercise the real production decision through a bounded private seam.

### P2.4: Cwd authority still rejects mutable metadata changes

The loaded-process cwd correctly compares device and inode. The surrounding checks still require all six `StableIdentity` fields.

The full comparisons occur during typed authorization, initial cwd opening, and the pre-SIGCONT held-fd check. See `src/lib.rs:1084-1101`, `2422`, and `2663-2666`.

Directory size, modification time, or change time can change while the descriptor still names the authorized directory.

Use the one device-and-inode directory-anchor rule for cwd ownership. Retain other fields as observations.

### P2.5: The fixed launch schedule has two names for its final case

`direct-build-recipe-a07.json:243` names `mismatch_kill_reap_user_code_marker_absent`.

The source, fixture, and recipe control-scope list use `mismatch_kill_reap_user_marker_absent`.

Normalize the exact ID before a control report becomes evidence.

## Verified repairs and retained limits

The direct recipe now includes `src/lib.rs`, both dependency paths, and all four direct archives. The region scan now recognizes the measured `EINVAL` end condition.

`DarwinSpawnFdGuard` closes early-error descriptors. The stopped path rereads all nine fixed authority artifacts before `SIGCONT`.

The process schema now has stopped, resume, vnode, cwd, executable, and region-end fields. These fields remain unobserved until compiled controls exercise real paths.

A07 remains source-only, uncompiled, and unexecuted. It proves no producer launch, native result, output binding, cancellation behavior, product integration, playback, hearing, or creative acceptance.

This is a same-model-family, nonblind review. The parent disclosed the synthetic launch-control concern before completion. No cross-family reviewer was available.
