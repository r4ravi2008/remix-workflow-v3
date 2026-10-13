# Rust producer runner A06 source peer review

Date: 2026-10-11

## Disposition

**Rejected before compilation or execution.** The frozen source has three P1 defects and four P2 defect groups.

The region walker rejects the normal Darwin scan endpoint. The build recipe also omits the production library input.

The process-group mismatch path can signal an untrusted process group. That safety defect also blocks a native attempt.

This is a same-model-family, nonblind review. I reviewed A05 and received root findings while this review was active.

## Frozen scope and receipts

The reviewed package is `rust-producer-runner-a06` under `native-text-unit-a01`.

| item | rows | bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `source-manifest-a06.json` | 1 | 37,785 | `98d225bed7f2dde75d0bd882292a30b3f26cf421da61bd2938d917a2f2976fe1` |
| source aggregate | 14 | 293,236 | `2c3e3ed40c2a19bb04c3e02f078ac23e122f465a721fc09807f6f274ce403293` |
| external aggregate | 84 | 10,317,267 | `d4a9f9aad65b7f4c2acdebac0a6e50c2ef90fbe4418d6a5699b595f92af4f773` |

I re-read every source and external row. Each saved byte count and SHA-256 matches its current file.

I independently reproduced both declared aggregate encodings. The external `(role, path)` pairs are unique.

Literal source imports and includes resolve through direct rows or the frozen transitive manifests. The recipe binds four dependency archives.

No compiler, module import, control, probe, child, native producer, media operation, or state mutation ran.

## P1 findings

### P1.1 — The production library command has no Rust input

`direct-build-recipe-a06.json:52-80` defines `production_library`. Its `argv` contains flags, archives, and the output path.

The command contains no `.rs` input. The other three commands name `src/main.rs`, `src/lib.rs`, or `src/control_main.rs`.

The fixed recipe therefore cannot build the library. Add the exact frozen `src/lib.rs` input before any compilation.

### P1.2 — The loaded-region walker rejects normal completion

`src/lib.rs:2172-2189` clears `errno` before each `proc_pidinfo` call. It accepts zero only when `errno` remains clear.

Apple's region lookup returns `EINVAL` when no later region exists. The user-space wrapper returns zero and preserves that error.

A normal completed scan therefore emits `loaded_region_walk_failed`. The child never reaches the approved `SIGCONT` path.

The separate [Darwin region-end review](rust-producer-runner-darwin-region-end-review-a01.md) records the primary-source trace. Its SHA-256 is `68aacdfbfb089878545392ce4d82d588c91c35934e25941413e6b2f3277a4737`.

Classify `EINVAL` as the endpoint only after a valid row and nonzero cursor. Keep first-call zero, `ESRCH`, permission failures, and cap exhaustion as failures.

### P1.3 — A process-group mismatch can signal an untrusted group

`src/lib.rs:2410-2416` reads `getpgid(pid)`. A positive value unequal to `pid` enters `darwin_kill_and_reap(pid, pgid)`.

`darwin_kill_and_reap` calls `kill(-pgid, SIGKILL)` before killing the direct child. The mismatched group has not been established as private.

This path can signal the runner's group or another unrelated group. Kill only the direct child until `pgid == pid` is proven.

## P2 findings

### P2.1 — Terminal evidence cannot prove the stopped-to-resumed boundary

`darwin_wait_for_stop` at `src/lib.rs:2045-2066` accepts any `WIFSTOPPED` status. It neither requires nor returns the stop signal.

The selected suspended-spawn route expects the observed `WSTOPSIG == 0` state. An ordinary signal stop must not satisfy that fact silently.

`ProcessObservation` at `src/lib.rs:350-363` has no stopped, stop-signal, loaded-vnode, cwd-check, or resumed fields.

Both pre-resume failure and completed paths set `started: true`. A saved report cannot show whether user code received `SIGCONT`.

Return the exact stopped-state facts. Persist the executable check, cwd check, and `SIGCONT` disposition separately from process creation.

### P2.2 — The private controls do not cover the selected authorization and launch seams

`AttemptAuthorization` has 17 fields at `src/lib.rs:452-470`. The focused mutation enum directly changes only six stored authorization groups.

The suite lacks independent mutations for schema, operation, implementation, repetition, run directory, four qualification references, and aggregate.

It also lacks independent cases for working directory, process policy, cancellation policy, and each false acceptance field.

Several mutations replace `authorization.json`. They primarily exercise `authorization_drift`, rather than each typed field check.

No focused case exercises the stopped-launch seams. Missing cases include executable inode replacement, wrong executable, and cwd replacement.

The suite also omits suspended cancellation, region query errors, scan truncation, stop-state mismatch, and kill-without-resume evidence.

Three claimed pure cases do not exercise their named production logic:

- `nonregular_descriptor_rejected_before_read` computes a fixture expression at `a05_focused_controls.rs:758-760`.
- `term_esrch_is_attempted_not_delivered_and_not_retried` copies three fixture booleans at lines 761-765.
- `pipe_drain_deadline_forces_reap_failure` hard-codes `ReapFailure` at lines 766-774.

Keep the 10 lifecycle and 15 focused groups. Add meaningful cases for every selected seam before qualifying the source.

### P2.3 — Early suspended-spawn errors leak owned descriptors

`execute_child` creates three pipe descriptors at `src/lib.rs:2485-2489`. It transfers their cleanup to `darwin_spawn_suspended`.

`darwin_spawn_suspended` uses `?` at lines 2258-2261 before installing cleanup ownership.

An executable-open failure leaks all three pipe descriptors. An executable-readback failure also leaks the opened executable descriptor.

Use an owned descriptor guard from function entry. Release descriptors only when the returned `DarwinSpawned` takes ownership.

### P2.4 — The cwd check uses mutable metadata instead of the selected object anchor

`darwin_loaded_cwd_matches` at `src/lib.rs:2224-2246` compares all six `StableIdentity` fields.

The held cwd recheck at lines 2510-2513 repeats the full comparison. Directory size, mtime, and ctime can change without object replacement.

Unrelated activity in the held unit root can therefore reject the correct cwd. The selected cwd contract is device and inode identity.

Use `same_directory_anchor` for the loaded and held cwd object. Mutable metadata may remain recorded diagnostic evidence.

## Correctly retained boundaries

A06 does preserve several useful A05 repairs:

- The private qualification constructor remains unavailable to public callers.
- The runner revalidates the opaque A02 qualification around authorization and child handling.
- Root and peer authorization-review identities remain distinct and exact.
- The run directory allowlist remains five entries.
- The spawn request uses `START_SUSPENDED`, `SETSID`, `CLOEXEC_DEFAULT`, and descriptor-relative cwd setup.
- The executable is held, rehashed, checked as thin arm64, and compared with its loaded vnode before resume.
- Authorization, review, qualification, anchors, and cancellation are rechecked before `SIGCONT`.
- Non-macOS execution fails closed.
- `nativeResultAccepted`, `productIntegrationAllowed`, `watched`, `heard`, and `creativeAccepted` remain false.

These properties do not overcome the P1 defects. The source is not ready for the fixed diagnostic build.

## Review limits

This review establishes source and file-closure facts only. It does not establish compilation, control success, or native execution.

The saved Darwin probes establish API feasibility for their own Python actors. They do not execute the frozen Rust route.

The route does not attest dyld or loaded dependencies. It also lacks producer-side descriptor binding after resume.

Native output, cancellation after resume, product integration, playback, hearing, and creative acceptance remain pending.
