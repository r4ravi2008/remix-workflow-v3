# Rust producer runner A08 parent source review

Disposition: rejected before compilation. Three P1 and four P2 findings remain.
This review permits a separate source repair. It does not authorize A08 builds,
controls, bootstrap publication, authorization, producer execution, or acceptance.

## Reviewed subject and method

The frozen provisional manifest has 47,223 bytes and SHA-256
`21775644ee59b2de369fe775d33d5c356c79cba337fd811b92b5a36191f46d78`.
The source closure has 15 files and 351,644 bytes, aggregate
`219df7f0d56ff036e49625aa4007ee0b154da3e5f42d58f54be325e65d1db1fb`.
The external closure has 97 rows and 10,580,106 bytes, aggregate
`7382780d79fe9f6632a00ee4d9791fdd8f8b7b7fd8d77dcb70477ddc470f5dca`.

Root read the complete A07-to-A08 library, focused-control, extension, recipe,
fixture and document deltas. Root read the new launch source and entrypoints.
Root followed the private ControlStage through the production run method.
Root checked the unchanged pure module and all three named helper call sites.
The A08 stable source readback records 441 inputs and 1,295,240,014 bytes.
Its 521,529-byte receipt has SHA-256
`1565648a9a4b2784e210fe021b29e4840d5bc5915191292a1b4c24de62792ff0`.
All nine recorded identity fields remained unchanged across that readback.
Root did not compile or execute project code. Source readback establishes
content and identity stability; it does not establish runtime behavior.

## Findings

### P1: Keep every launch case within the owned control attempt

`src/a08_launch_controls.rs:345` constructs a timestamp/PID directory under
`UNIT_ROOT/rust-producer-runner-a08-control-attempts`. It ignores the supplied
control-attempt path. `src/a05_focused_controls.rs:1029` calls it without a root.
The root control wrapper inventories only the declared owned attempt.
Launch reports, private binaries, markers, and direct-child PID evidence therefore
escape that inventory. Rows export selected booleans and a report pathname,
but omit the full process object needed for independent recursive closure checks.

Pass one exclusive, absent launch subdirectory from the owned attempt. Save every
case artifact there. Preserve full process and terminal references for readback.

### P1: Make launch and retained-review mutations deterministic

`src/a08_launch_controls.rs:196` waits for a reader flag. The production reader
sets the flag and continues immediately. Nothing pauses the production thread
while the fixture replaces the executable or cwd. These mutations can happen
before descriptor acquisition, after validation, or after resume.
The generic predicate at line 302 permits a failure with no child at all.
It also omits stopped, no-resume, no-SIGCONT and kill facts for several variants.
This cannot establish the declared suspended-launch boundary behavior.

Use bounded, feature-private rendezvous at the exact reviewed descriptor and
stopped-child boundaries. Production builds must retain the fixed public API.
Require actual child facts, saved causal rejection, cleanup, and marker absence.
The normal variant must record stop, resume, SIGCONT, marker and completed reap.

The focused identity mutation replaces root, peer and sidecar together.
Only the first rejected join is thereby exercised. The reader flag also races
this replacement. Record separate private identity subvariants within the existing
review group. Measure same bytes and changed inode instead of asserting labels.
Use an atomic private executable replacement with a bound replacement input.
Copying `/usr/bin/true` over the executable in place is not that observation.

### P1: Retain unresolved child ownership through failure handling

`src/lib.rs:2299` adds one bounded direct-PID kill/reap retry. That is useful,
but several launch branches still discard unresolved reap details and return
a generic launch failure. The group mismatch branch at line 2759 returns after
the initial cleanup result even when no terminal status was obtained.
No retained reaper owns a still-live stopped direct child after this return.
A `ClosedProducerRun` cannot imply closure while that ownership remains unresolved.

Use one owned-child guard across every post-spawn path. Preserve wait, signal,
retry and closure failures. Report an explicit unresolved reap failure if bounded
cleanup cannot close the child. Never present it as completed or qualification
pending. Preserve the rule that foreign groups receive no signal.

### P2: Separate injected values from kernel observations

`src/lib.rs:2253` substitutes SIGTSTP for the real stopped signal.
`execute_child` discards the returned raw status and injected flag.
`src/lib.rs:2648` substitutes `pid + 1` for the observed process group.
The report then labels that substitute as `foreign_process_group_id`.
An `injected_fault` name alone does not recover the overwritten kernel facts.

Persist raw wait status, actual stop signal and actual PGID separately from
effective injected values. Never call an injected group an observed foreign group.

### P2: Enforce the region deadline at clean-end admission

`src/lib.rs:2405` checks elapsed time only before `proc_pidinfo`.
The zero-result path at line 2428 passes `false` as the timeout fact.
A call that crosses the deadline can therefore admit a clean end.
Capture errno immediately. Recheck elapsed time after every call and before
admission. Keep EINVAL, prior validated rows and monotonic cursor requirements.
The truncation hook at line 2444 returns after one row without exercising the
actual cap decision. Share the bounded cap decision and label injected inputs.

### P2: Connect the remaining pure fixtures to production decisions

`descriptor_read_is_allowed`, `esrch_termination_facts` and
`pipe_drain_completion` remain called only from private fixture code.
The library does not use those functions for its corresponding decisions.
Executing their fixtures cannot prove production descriptor, ESRCH or drain logic.
Use the same decision implementation in production and the finite fixture set.

### P2: Prove typed validation and derive changed keys

`src/a05_focused_controls.rs:431` preserves artifact-drift rejection for mutated
authorization files. That first rejection is correct and must remain ordered.
However, the field variants still do not exercise the typed validator.
Line 434 writes the supplied label as `observedChangedKey`.
This is a declared key, not a measured before/after difference.

Keep the existing artifact-drift cases. Within the same finite variants, add a
coherent private invocation of the shared typed validator. Record the exact
changed key and its causal field rejection. Do not expose accepted-value construction.

## Repair boundary

Preserve A08 and its evidence unchanged. A09 is a separate source-only candidate.
The fresh independent A08 peer review remains required and additive.
The root orchestration wrappers also have a separate rejected source review.
No source disposition establishes native, product, watched, heard or creative
acceptance. The film and the native producer remain unverified.
