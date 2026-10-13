# Rust producer runner controls A03 evidence peer review

## Scope and method

This is a read-only review of the saved A03 build and control evidence. It does not rerun the compiler, control binary, or any child. It does not import Rust or Python target code. It does not open the FIFO negative control.

The evidence root is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-source-controls-attempt-a01`

I reopened regular files and used `lstat` for every recorded path. I checked bytes, SHA-256, and these nine recorded identity fields: `bytes`, `ctimeNs`, `device`, `gid`, `inode`, `links`, `mode`, `mtimeNs`, and `uid`.

## Source package and assembly

The saved source-controls A03 package remains source-only. Its manifest is 2,181 bytes with SHA-256 `72218d2fb6bdcc98a4de5c7e38fedd46830111d13a09b4837cae38186a41c8e6`. Its five manifest rows all match their current files. The declared aggregate recipe recomputes to the declared aggregate:

- source aggregate: `b1997fe02e9c787cc9d658c8d56c54379a02b85285323552c74b4554a2c28a6f`;
- package aggregate domain: `native-text-rust-producer-runner-source-controls-a03-source-v1`;
- assembly recipe row: 4,871 bytes, SHA-256 `cf2ba1749bad1b7e040e1e4441c1f19e446e351f370a547c475f754532dc6605`;
- control contract row: 9,837 bytes, SHA-256 `5cd04181c74828a4dc17507b9a13420dbaa6b4c6a0346e3c5439412833ec8ac3`;
- control extension row: 60,392 bytes, SHA-256 `631bbc7b4f0e4792771ac2f383623760365ac27b0f053a4a6fca63fbb0619f21`;
- A04 runner library row: 65,284 bytes, SHA-256 `2414938b08c109d4953d11ec2962aa8095f01f7cb47e2936ed2e4dd9206e055b`;
- pure helper row: 3,969 bytes, SHA-256 `b76f4edd50ca097e7aadb458c2325b02b874f9fdb1162a3f887c1c1f08c4ed1e`.

The attempt assembly is exact. The 65,284-byte A04 library is the prefix of `src/lib.rs`, and the 60,392-byte A03 extension is the suffix. The assembled file is 125,676 bytes with SHA-256 `fe12a6a1e2ce8dc3a202636136d1ee7ff75868f26fba8528ed49e491eb95fb47`. The copied `src/pure.rs` is byte-identical to the package pure helper.

The controls intentionally target the separate frozen A04 runner. The A03 package records that authority as manifest SHA-256 `961dd0e2cd7525ec8523958a97a0ac109aabfcac3393adfb1b36d846c9280576` and source aggregate `c658f23cd62b58cfb698ee2738cecbc2bb9ac7fa8e17062dfc642d7eca9a890a`. The saved control report emits the same A04 values. All eight A04 manifest rows also match current files. The A04 manifest itself does not carry the aggregate domain and recipe; the A04 package contract documents that aggregate contract. This review binds the declared A04 aggregate and verifies its rows rather than applying the A03 package recipe.

## Corrected build evidence

The original build report remains unchanged. `report.json` is 124,811 bytes with SHA-256 `08c3ce4bfe9a1c7eb7ff448effc995a0ee5a9f6f24722feaf21e772279669b0d`. It records `compiled=false`, `reaped=false`, and no Mach-O facts.

The additive correction is `build-readback-correction-a01.json`, 2,166 bytes, SHA-256 `63253caa55927f13c434c13437783b6659caf2251b4d41c037e5acc39417dc20`. It records `compiled=true`, compiler return code `0`, a collected compiler poll status, corrected reaping, and compiler PID absence. Its explanation is consistent with the saved command record: the outer selector loop exited after EOF and did not set its separate `reaped` boolean, although a final successful `Popen.poll` had collected return code `0`. The correction preserves the original report instead of rewriting it.

The produced file is a regular arm64 Mach-O executable. It is 1,893,400 bytes with SHA-256 `02e25376860801b48d1c9d38cc3d119b203b9787775cdd6a8fa1e71345f5333a`. The corrected Mach-O record is CPU `16777228`, file type `2`, UUID `54ce63e64e50359a874b1f6b656c9a96`. Its three original generated-output rows rehash successfully. The compiler stdout and stderr logs are both empty, each with SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

Both the original report and the correction record 96 inputs totaling 75,524,974 bytes. Their two assembly rows and 96 input rows match before and after. Every row matched all nine identity fields and the recorded content hash. This establishes the saved build readback. It does not turn the source package's own `source_authored_unbuilt_unexecuted` state into a native qualification claim.

## Saved A03 control invocation

The saved invocation is `control-run-report-a01.json`, 179,415 bytes with SHA-256 `f6572b50444e0d3ea2c0ffd1b98551d0440a5afe0c957d793a242e16f1c03694`. Its exact command vector is the produced binary followed by `--control-attempt` and the absolute `control-attempt-a03` directory. The saved run has return code `0`, `reaped=true`, PID `77376`, elapsed time `2.132841` seconds, no timeout, no stream overflow, and no outer TERM or KILL.

The saved stdout is exactly 53 bytes, SHA-256 `bab3b4b6c1677460e3fe71656a35f69c19d18c35cb5f16ff1fe8d29ebdd31d96`, containing `{"schema":1,"state":"passed","passed":10,"total":10}\n`. Stderr is empty. The preflight forbids native A05 startup and records source-control-only execution.

The control report is 6,493 bytes with SHA-256 `22a92d6c64555fa047ced008b741643d8d68afb07caf5db81faca5a83b2d18ab`. It has schema `1`, state `source_controls_passed_no_native_acceptance`, the exact ten-case order, and ten passed results. Its embedded result set equals the standalone control report result set. Every native, product, audio, framework, media, GPU, Resolve, watched, heard, and creative field is false.

The outer control-run report records 71 generated-output rows. All 71 paths are regular files. Every row matched its current nine-field identity, byte count, and SHA-256. The report records empty temporary entries and no unclosed streams. The saved parent readback reopened 173 recorded rows and reports `allReopenedRowsMatched=true`.

The outer run report's `ownedPidAbsence` list is empty because its filename filter omitted `child-pid.txt` and `holder-pid.txt`. The separate parent readback supplies nine actual case child or holder PID checks. Every row has `absent=true`, including both the direct child and holder in the pipe-holder case. This review treats those saved absence rows as evidence and does not perform new process checks.

The FIFO negative control is `cases/fifo_authority_rejected_nonblocking/authority.fifo`. `lstat` reports FIFO type `4096`, zero bytes, and the recorded identity matches. I did not open or read it. The saved case took 20 milliseconds, did not start the producer, and preserved an authority-missing failure.

## Case-level causal evidence

- `unavailable_loader_no_output` records status `Some(78)`, complete stdout and stderr EOF, no overflow, a reaped loader, and no output entries.
- `normal_exact_argv` records `completed_external_qualification_pending` with exact argv matching.
- `nonzero_failure_preserved` records exit code `23` and preserves its failure evidence.
- `cancellation_process_closure` records TERM requested, attempted, and delivered, signal `15`, completed reaping, a joined control thread, a zero-byte cancel marker, and final absence of child PID `77382`.
- `log_overflow_process_closure` records a 4,194,304-byte producer log, TERM requested, attempted, and delivered, signal `15`, completed reaping, and final absence of child PID `77388`.
- `post_reap_group_pipe_cleanup` records `pipe_drain_timeout`, `reap_failure`, `kill_sent=true`, completed reaping, holder PID `77395` absent before fallback, and direct child PID `77394` absent. The persisted report does not expose a separate KILL-delivery boolean because fallback cleanup was not needed; this review claims absence and the causal failure, not syscall delivery.
- `producer_log_replacement_detected` preserves `producer_log_read_failed`. The replacement log is retained separately from the original empty log.
- `terminal_collision_fallback` retains the 29-byte `report.json` sentinel and a schema-1 fallback with code `terminal_report_name_collision`, phase `terminal_publication`, and both acceptance fields false.
- `double_terminal_collision_preserved` retains both unchanged sentinel files and records `runner_error=terminal_publication`.

## Disposition and limits

The saved evidence is internally consistent. The additive build correction supersedes the stale compiled/reaped boolean for readback, while the original report remains preserved and hash-bound. The controls passed as a finite Rust source-control invocation.

This evidence does not qualify a native producer, media output, audio, observer, comparator, Swift path, GPU, Resolve path, product integration, watched result, heard result, or creative acceptance. The control cases use fake children and source-control fixtures only. This review did not rerun any binary, compiler, control, or child. No FIFO was opened.
