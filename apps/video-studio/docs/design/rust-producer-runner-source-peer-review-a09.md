# Rust producer runner A09 source peer review

## Disposition

**Rejected before compilation.** Four P1 groups and four P2 groups remain.

A09 closes several A08 design gaps. It does not establish safe child closure or a passing private control schedule.

This review is source-only. I did not compile, import, test, bootstrap, launch, or execute package code.

I did not start a child, native framework, media tool, GPU, or Resolve.

## Frozen subject

I read all 15 package files and the complete A08-to-A09 changes.

I rehashed every source and external row. I independently reproduced both framed aggregates.

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| `source-manifest-a09.json` | 51,013 | `e0433445a7f9c782a7ed7a729844451d77853a0a8dac251b688b5aea18609943` |
| 15 source rows | 382,092 | `95610ac0eac8f154ab32b199d1a94c7c125d0dc2061c53e3fe317efabda97aee` |
| 102 external `(role,path)` rows | 10,651,616 | `2f8638e74a0a313cb3857b45b6668f617889cb2509b512c62061d4d2d500ee7f` |
| `src/lib.rs` | 154,224 | `0fd9ad5a3fbf5a52652571ab5de0267b90abf605f2db66801ae0614a47b85f94` |
| `src/a09_launch_controls.rs` | 21,186 | `c1f4a67e50359da24d8ba63bf66f72cdb365bab9486178318e07a19c5bc863c0` |
| `src/a05_focused_controls.rs` | 64,269 | `44e5b486619585d741c59c481bc8f9635a6fbe22a14af05ff015d5f7c4502c80` |
| `src/a05_control_extension.rs` | 73,505 | `a28f122cf791eddbbe58de0ec5269be86d207f2b5c298daf4a1f628c4df6e467` |
| `direct-build-recipe-a09.json` | 18,827 | `3b5b1e9d2be1c6e90fb601d43774f96750a5b01f4001c70a1d68b7283e2054c4` |
| `pure-fixtures-a09.json` | 14,514 | `547774c54c8244042f59c3e787e9e1ce24ab5c81c82f0d1164ceb9fbe05eb7e2` |

All current rows match their saved byte counts and hashes. Source-row paths and external `(role,path)` pairs are unique.

The recipe supplies both dependency paths and all four fixed archives to each direct Rust command. Every command also names its source input.

## P1 findings

### P1.1: A stopped wait status is reported as a completed reap

`DarwinLaunchFacts.wait_status` stores the `waitpid(..., WUNTRACED)` stopped status. See `src/lib.rs:2989-3008`.

`darwin_child_failure` then uses `status.or(facts.wait_status)`. Any stopped status makes `reap_completed=true`. See `src/lib.rs:2875-2877`.

An unresolved kill and reap can therefore produce a saved process record with `reap_completed=true`.

Store stopped and terminal wait statuses separately. Only a consumed terminal status may prove reap completion.

### P1.2: The final cleanup guard loses ownership in both failure directions

`DarwinSpawned::drop` makes one more bounded kill-and-reap attempt. It then closes the retained descriptors regardless of the result. See `src/lib.rs:2260-2281`.

If that attempt remains unresolved, the last direct-child owner disappears. The saved run can no longer perform or prove terminal cleanup.

The early-terminal branch has the opposite state error. It consumes a terminal status but never sets `child.initial_reaped=true`. See `src/lib.rs:2984-2988`.

`Drop` can therefore signal and wait on a PID that was already reaped. PID reuse makes that extra signal unsafe.

Retain an unresolved owner outside the closed result. Mark the early-terminal child reaped before the guard drops.

### P1.3: Review identities can change after the last pre-resume verification

The stopped-child path verifies `authorization-review.json` and its root and peer files. It then enters the `REVIEW` control gate. See `src/lib.rs:3043-3046`.

After the gate, the code checks qualification, typed authorization, path anchors, and cancellation. It does not reread the review files before `SIGCONT`.

The three same-byte replacement controls mutate root, peer, or sidecar while the gate is open. See `src/a05_control_extension.rs:1093-1118`.

Those rows can resume user code. Drift is detected only during postflight. The rows require `childStarted=false`, so they also fail their own contract.

Reread the sidecar, root review, and peer review after the gate and immediately before the resume decision.

### P1.4: Three suspended-launch controls require impossible codes or process shapes

The same-byte executable row replaces the pathname after the old file descriptor is held. `posix_spawn` loads the new inode.

The loaded image cannot match the held identity. The scanner returns `loaded_executable_vnode_ambiguous`, outside that row's allowed codes. See `src/lib.rs:2638-2643` and `src/a09_launch_controls.rs:297-302`.

The different-executable row installs `/usr/bin/true`. That file is a universal binary with a nonzero ARM64 slice offset on this host.

The offset-zero scanner again cannot produce either allowed drift code.

The cwd-swap row fails `working_directory_path_drift` before `posix_spawn`. The row instead requires a started and stopped child. See `src/lib.rs:2724-2732` and `src/a09_launch_controls.rs:350-356`.

Give each row the actual intended boundary. Align its allowed code and required process shape with that boundary.

## P2 findings

### P2.1: The ESRCH predicate receives invented retry facts

`darwin_kill_and_reap` does not capture `errno` after a failed direct `kill`. It passes `!direct_sent` as `retry_allowed`. See `src/lib.rs:2443-2471`.

The production path retries every failed direct signal, including ESRCH. The fixture claims ESRCH is not retried.

Capture the signal result and errno together. Make the production retry decision and fixture expectation use those exact facts.

### P2.2: Region truncation and cap controls discard the shared predicate result

The injected truncation and cap paths call `region_scan_end_is_valid` and ignore its result. See `src/lib.rs:2595-2600` and `2629-2636`.

Both branches return fixed errors independently. They do not qualify the production predicate they claim to exercise.

Use the predicate result to select the production outcome. Preserve the injected input as a separate observation.

### P2.3: Typed mutation controls do not verify the claimed changed field

The controls compute changed JSON paths and save them. The group copies the first path into `observedChangedKey`. See `src/a05_focused_controls.rs:507-549`.

No row compares those paths with its expected field. The typed check records only a generic rejection boolean. See `src/a05_control_extension.rs:1151-1170`.

A mutation can reach the validator and still qualify under the wrong label. Bind each variant to its exact expected changed path and rejection cause.

### P2.4: The frozen fixture describes only three of five review variants

The executable control has separate root, peer, and sidecar identity rows. See `src/a05_focused_controls.rs:829-891`.

`pure-fixtures-a09.json:474-478` still names one combined `same_byte_new_inode_review_files` row.

The manifest, recipe, schema, and rationale describe five rows. The fixture contract therefore disagrees with the source schedule.

Update the successor fixture to list all five exact variants. Keep the preserved A09 fixture unchanged.

## A08 repair accounting

The caller-owned launch-root repair is present. `focused_run_a05` places `launch` below the exclusive control attempt.

The process schema now separates observed PGID and stop facts from injected values. This closes the structural part of A08 group 4.

The region loop checks elapsed time after each `proc_pidinfo` call. It also checks the clean-end predicate before admission.

The production path now calls the descriptor and pipe-drain pure predicates. The ESRCH and region-injection evidence remains defective.

Root, peer, and sidecar replacement rows are separate. Their pre-resume reread ordering remains defective.

## Scope

A09 remains uncompiled and unexecuted. Hash stability proves only the reviewed source and external closure.

This review does not establish a passing control run, child lifecycle, producer output, native result, product integration, playback, hearing, or creative acceptance.

The review is same-model-family and nonblind. Root disclosed several launch concerns while the independent source read was underway.
