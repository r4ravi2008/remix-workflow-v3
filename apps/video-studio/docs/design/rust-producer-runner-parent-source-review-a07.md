# Rust producer runner A07 parent source review

State: frozen source rejected before compilation. Fresh peer review is pending.

## Measured scope

The parent reviewed the complete A07 changes against the previously read A06 closure.
The review covers the library, pure helpers, private controls, fixtures, entrypoints,
package configuration, recipe, contract, output schema, README, and rationale.
Unchanged source remains covered by the measured A06 readback.

The A07 manifest is 42,965 bytes with SHA-256
`4c96c09124cf52523e8cd8684c4f9317e7b6e3ee602eda0bdad38c40720f012d`.
Its 15 source rows total 324,957 bytes. Their framed aggregate is
`7b7e11a73c29663f639e1420855c09bf3fdf61a72a063f070e7ae1ff67d1a8d7`.
Its 93 external rows total 10,519,216 bytes. Their framed aggregate is
`d0c9b76e3cd1c9d8e8ae40ae779af93ec7ed622ee13defcbf284f6588b6aebca`.

The parent source readback measured 420 inputs totaling 128,602,593 bytes.
Every input retained its bytes, hash, and nine identity fields before and after.
The explicit import closure contains 27 edges and 23 Rust source files.
The readback is `rust-producer-runner-a07-parent-source-readback-a01.json`:
498,065 bytes, SHA-256
`3ad15b3d141d0674a3e8db56a57f70c7395706da6a8612f55a2c325b4a87e6ca`.

## Findings

1. **P1: launch controls invent process observations.**
   `a07_launch_controls.rs` explicitly starts no child. It assigns
   `observedCode=expectedCode` and returns synthetic marker, reap, and SIGCONT facts.
   These predicates cannot prove the actual suspended launch or cleanup path.
   The replacement must use private fake executables and feature-private fault hooks.
   Read observed codes and process facts from the actual runner and saved terminal.
   Check marker creation or absence on disk. Preserve the frozen fake binary.

2. **P1: a rejected stopped status can leave a child alive.**
   `darwin_wait_for_stop` returns `Ok(Some(status))` for terminal statuses and
   rejected nonzero stop signals. `run_child` treats both as reaped terminal states.
   `darwin_child_failure` also infers reaping from any present status.
   A mismatched stopped status must trigger bounded kill and actual reap without SIGCONT.
   A consumed terminal status must remain distinct from a live stopped status.

3. **P1: the loaded-cwd call references an undefined function.**
   `darwin_loaded_cwd_matches` calls unqualified `descriptor_anchor_matches`.
   The available helper is `pure::descriptor_anchor_matches`.
   The macOS production source cannot compile until the call is qualified.
   The fresh peer identified this defect; the parent confirmed the exact source call.

4. **P2: the loaded-region walk has no wall deadline.**
   The loop has 256 iterations but no `Instant` deadline check.
   The clean-end predicate always receives `deadline_elapsed=false`.
   The documentation claims deadline rejection that production source does not implement.
   Add the fixed deadline and exercise that actual branch through a private hook.

5. **P2: region validation does not enforce the complete declared selection rule.**
   The loop checks `end > cursor` but does not reject `row.address < cursor`.
   It counts only exact identity matches, so conflicting main-image candidates are ignored.
   Require a monotonic row start, checked end, and exactly one selected candidate.
   That candidate must match the full executable identity.

6. **P2: foreign groups and directory anchors need precise semantics.**
   The foreign-group branch correctly signals only the direct child.
   Its process record nevertheless publishes the foreign group as `process_group_id`.
   Record verified ownership separately, or leave the owned group absent.
   Loaded cwd uses device/inode anchors, but held cwd still compares mutable directory metadata.
   Use the declared anchor rule consistently for held and pathname cwd checks.
   Continue exact regular-file checks for executable, review, and authority files.

7. **P2: three pure repairs remain disconnected from production decisions.**
   `descriptor_read_is_allowed` still depends on a fixture's `read_attempted` value.
   `esrch_termination_facts` mostly copies fixture observation booleans.
   `pipe_drain_completion` is not called by the production deadline branch.
   Calling newly named helpers alone does not demonstrate those production decisions.
   Factor or reuse the existing production decisions within the fixed pure schedule.

8. **P2: control schedule declarations disagree with source.**
   The actual authorization/review mutation schedule contains 21 variants.
   It contains 20 authorization mutations and one sidecar run-name mutation.
   The recipe declares 20. `observedChangedKey` repeats a literal label.
   Derive the actual changed JSON paths and confirm the intended single mutation.
   The recipe and fixture also disagree on the final launch variant identifier.
   Use one finite schedule and derive all counts from that schedule.

`AttemptAuthorization` has 17 top-level fields and no `run_name` field.
Expanding its qualification field into four references yields 20 authorization mutations.
The separate sidecar run-name mutation remains valid and must stay separate.
The review does not request a new authorization field or a broader mutation matrix.

## Repairs observed in source

The production-library recipe now includes `src/lib.rs`.
All four commands carry the two dependency directories and fixed archive references.
The loaded-region clean end now recognizes the grounded EINVAL predicate.
The launch FD guard covers early executable and cwd errors.
The executable and cwd descriptors now remain owned through child closure.
The paused path remeasures all current qualification authority rows.
The process schema now exposes stopped, resume, loaded-image, cwd, and held-file facts.
The authorization mutations preserve the saved-file validation order.
The output schema now describes the actual camelCase control keys.
These source observations do not establish compilation or runtime success.

## Disposition

Preserve A07 unchanged. Author repairs separately in A08.
No compiler, controls, bootstrap, authorization, or native producer was executed for A07.
No GPU, media, Resolve, playback, listening, or creative acceptance was performed.
The goal remains active. Source and runtime gates precede the first native diagnostic.
Qualified production output additionally requires the producer's future descriptor-relative output protocol.
