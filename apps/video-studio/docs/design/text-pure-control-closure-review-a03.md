# Native text pure callback and build closure review A03

## Verdict

PASS for the two P2 findings recorded in the preserved A02 review.

The A02 runner closes both findings before any callback control execution:

1. It binds the helper and every JSON or build-record input before the control.
2. It rechecks those rows after the control.
3. It uses the bounded same-descriptor reader for compiler and test logs.
4. It checks the file size before reading and retains bounded partial observations.

No new P1 or P2 source finding was found within the reviewed path-level closure contract.
The callback control itself remains unexecuted and unaccepted by this review.

This review did not run Python, Cargo, rustc, the Rust test binary, ImageIO, or any native
framework call.

## Reviewed identities

The preserved A01 runner is:

artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/run_rust_png_control_a01.py

It is 6,718 bytes with SHA-256
401ef667732ec45fbb7c6db820bc92e646b2218649ac2cfa30a0e1e5f1fb0416.

The reviewed A02 runner is:

artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/run_rust_png_control_a02.py

It is 9,513 bytes with SHA-256
123ab399bf3c532bb1b5b23e5eba5f9af87b77f8fa858cb892f3b465df8730dd.

The A02 source-closure record remains:

control-source-closure-a02.json

It is 1,576 bytes with SHA-256
2601b8c2bda792a4d834e622189db35a563840f131c8abf505973db3b50ce7f8.

The source diff was read against A01. A01 remains byte-preserved. A02 writes to the distinct
rust-png-control-attempt-a02 directory.

## P2-1 closure: helper and build-record identities

The A01 runner only recorded its own helper descriptor at finalization. It did not include the
helper or the build records in the expected rows before execution.

The A02 runner records its helper before execution at lines 115–118. The build report and
release-build record are read through read_json_record at lines 119–127. That function observes
each file before parsing, then adds its path, byte count, and SHA-256 row to expected and
closure_records.

The initial expected-row loop at lines 133–135 rechecks every helper, JSON, source, dependency,
toolchain, framework, binary, and compile-gate row before launching the control.

The after-identity loop at lines 177–188 rechecks every expected row. The closure loop at lines
189–196 records before and after rows for the helper and every JSON or build record.

The A02 report therefore retains the missing before and after identity evidence. The runner
continues to make a path-level byte and hash claim. It does not claim loaded-vnode identity.

## P2-2 closure: bounded compiler and test log reads

The A01 runner used hashlib.file_digest for step logs and read_bytes for direct test output.
Those paths could read the entire file before applying the four MiB check.

The A02 observe function at lines 21–51 opens one descriptor, checks the initial size before
reading, reads bounded 64 KiB chunks, checks for growth, and compares stable metadata after the
read. It returns a bounded partial observation when the size or identity check fails.

The step finalizer at lines 92–99 observes each log with a four MiB maximum. A missing bounded
observation prevents the step from continuing at lines 100–103.

The compiler log is collected through observe at lines 146–155. The per-record 256 KiB check
still applies after the complete log has passed the four MiB reader cap.

The direct callback log is collected through observe at lines 166–170. A02 contains no
hashlib.file_digest call and no read_bytes call.

## Failure preservation and control boundary

BoundedObservationFailure at lines 15–18 carries the path, initial file size, bytes read,
partial SHA-256, and completion state. The main failure record retains that partial object at
lines 172–175.

The A02 runner preserves the selected test name and the explicit environment. It keeps the
control limited to the reviewed Rust callback test. Its report still excludes ImageIO, native
text production, product integration, process RSS, playback, hearing, and creative acceptance.

The output directory is intentionally fresh. The directory creation occurs before the protected
control block, so the caller must provide an unused output path. This is an existing execution
precondition and does not change the A02 verdict.

## Acceptance boundary

The A02 source is independently read and statically parsed. The two prior P2 findings are closed.
This review authorizes only the next bounded pure callback-control execution. It does not report
that execution as passed.

This is a same-model-family review. No cross-family reviewer was available.
