# Rust producer runner A05 source peer review

## Disposition

**Rejected before compilation.** Two P1 groups and four P2 groups remain in the frozen A05 package.

The declared build cannot complete as written. The launch boundary also does not bind the spawned child to the measured executable.

The private controls contain compile errors and stale assertions. They cannot qualify the production runner in their current form.

This is a source-only review. I did not compile, import, test, stage, invoke, or start any child process.

## Frozen receipts

| Item | Count | Bytes | SHA-256 |
|---|---:|---:|---|
| `source-manifest-a05.json` | 1 | 30,306 | `e0f4b89579ee5675611b02eeddaae9059d7b325c2d81e128cbd465c71a5f7253` |
| source rows | 13 | 250,148 | `0307a9d6dc9996ebd728b850f0f3c7f6e14441ffe0ccd49c7ec62499756c4e94` |
| external rows | 64 | 9,917,501 | `b6e6a5ae0d487b54a0bf3cc60731f30d69b6c9ef5a81885f8f41676a31301d80` |

I rehashed every listed source and external file through stable, no-follow reads. I also reproduced both framed aggregate digests.

The manifest permits the same role at different paths. Its uniqueness domain is `(role, path)`, which the current rows satisfy.

The 19 literal Rust imports and includes resolve through direct rows or the frozen transitive manifests. I found no unbound literal edge.

## P1 findings

### P1-1 — the declared build cannot compile and link the complete package

Three independent defects block the fixed build:

1. `src/a05_control_extension.rs:1226-1236` initializes `QualificationData` with an `authorization` field. `src/lib.rs:288-297` defines no such field. The controls library cannot typecheck.
2. `src/a05_control_extension.rs:1176` moves `layout` into the tuple. It then borrows `layout` for `layout.clone()`. Construct the stage before moving `layout`.
3. `direct-build-recipe-a05.json:85-108` and `146-171` give both CLI builds only `-L dependency=${ATTEMPT}`. The library builds use two external dependency paths and four exact archives. The CLI links cannot resolve the runner rlib's transitive crates from the attempt directory alone.

Repair the two Rust expressions. Add both fixed dependency search paths to both CLI commands.

### P1-2 — pathname swaps can redirect the authorized child

`src/lib.rs:1324-1385` revalidates evidence and path anchors before launch. `execute_child` then uses strings at `src/lib.rs:2005-2024` for the executable and working directory.

No descriptor-bound launch joins those strings to the measured executable or retained directories. A rename or replacement after the last check can redirect the child. Restoring the original paths before postflight can hide that change.

This contradicts `runner-contract-a05.md:74-77`, which says string paths cannot redirect the child.

Bind the launched executable to a held descriptor or equivalent loaded-vnode check. Bind the working and run paths at the launch boundary too.

If A05 remains an untrusted diagnostic, lower this claim in the contract. The exact-producer qualification path still needs the stronger binding.

## P2 findings

### P2-1 — review file identities are discarded after the first read

`AuthorizationReviewEvidence` stores only path, length, and SHA-256 at `src/lib.rs:411-416`.

`read_authorization_review` measures sidecar and review identities at `src/lib.rs:872-935`. `validate_review_artifact` discards those identities at `src/lib.rs:938-953`.

Later checks at `src/lib.rs:989-999` compare only the reduced values. A same-byte inode replacement therefore passes.

This conflicts with `README.md:119-124`, which claims retained device and inode joins.

Retain each `StableIdentity` in `AuthorizationReviewEvidence`. Compare it during every prelaunch and post-child reread.

### P2-2 — a valid cancellation layout exceeds the run-entry cap

`src/pure.rs:71-92` allows five entries:

- `authorization.json`
- `authorization-review.json`
- `producer.log`
- `probe-output`
- `cancel-marker`

`src/lib.rs:2382-2398` rejects the fifth entry because it caps the vector at four.

A post-launch cancellation can contain all five entries. The runner then records `run_entries_read_failed` and loses output inventory.

Derive the cap from the exact allowlist. Add a cancellation control that requires the complete five-entry inventory.

### P2-3 — the inherited and focused controls do not match current runner behavior

Several cases cannot establish their declared result after the compile errors are fixed:

- `src/a05_control_extension.rs:419-430` launches the controls binary with production CLI arguments. `src/a05_focused_controls.rs:518-561` returns 64 for those arguments. The expected unavailable-loader output at `src/a05_control_extension.rs:264-268` also uses the obsolete `rust_stage_acceptance_unavailable` record. Production now prints `rust_stage_qualification_unavailable` with `productIntegrationAllowed:false` at `src/lib.rs:1102-1112`.
- Six authorization mutations replace `authorization.json` at `src/a05_focused_controls.rs:64-97`. `verify_authorization_file` detects identity and byte drift before typed validation. Those cases expect `authorization_invalid`, but current ordering yields `authorization_drift`.
- Missing or rejected sidecars still produce a saved terminal report. `run_accepted` then returns `AuthorizationNotReviewed` at `src/lib.rs:1519`. The focused error branch reads only the coarse `RunnerError` at `src/a05_focused_controls.rs:244-255`. It misses the causal saved `attempt_error`.
- The same error-path mismatch affects prelaunch cancellation and the FIFO authority case. Their controls expect an `Ok(ClosedProducerRun)` or a direct `cancelled` error.
- `focused_postflight_drift_a05` treats any `Err` as passing once its mutation occurred at `src/a05_focused_controls.rs:373-379`. It does not verify the saved terminal code.

Read the saved terminal report on every error path. Align each expected code with actual validation order.

### P2-4 — three claimed controls do not exercise or derive their evidence

The collision case calls `control_write_new_a03` twice at `src/a05_focused_controls.rs:316-334`. It never calls the production authorization writer at `src/lib.rs:768-839`.

The top-level report hardcodes `positiveTwoEntryQualification:true` at `src/a05_focused_controls.rs:480-515`. The field is not derived from the corresponding case result.

The combined report records 21 copied pure cases at `src/a05_focused_controls.rs:532-547`. No A05 dispatch path loads or evaluates `pure-fixtures-a05.json`.

Exercise the production collision seam and preserve its exact error. Derive the positive flag from the observed case. Execute the bounded 21-case pure schedule, or label it explicitly as unexecuted fixture metadata.

## Verified source properties

The following source properties remain useful after the findings are repaired:

- `AcceptedRustQualification` has a private payload and crate-private constructor.
- The production stage has no caller-controlled qualification constructor.
- The focused positive case loads the real pinned A02 qualification. It is not a synthetic opaque qualification.
- Qualification revalidation occurs before authorization, before launch, and after child closure.
- The saved typed authorization carries the fixed command, environment, policies, and qualification references.
- The authorization file retains its own byte and identity checks.
- Root and peer review references must be distinct during each individual read.
- The fake producer and pipe holder remain behind `a05-controls`.
- Production reports keep native, product, watched, heard, and creative acceptance false.

These checks do not offset the P1 build and launch-authority blockers.

## Review limits

This review establishes source and file-closure facts only. It does not establish compilation, control success, process lifecycle behavior, native framework execution, or producer correctness.

It does not accept a native result, product integration, playback, hearing, or creative quality.

The review used the same model family as the authors. It was not blind. Parent findings arrived during the review, and I independently checked their cited source paths.
