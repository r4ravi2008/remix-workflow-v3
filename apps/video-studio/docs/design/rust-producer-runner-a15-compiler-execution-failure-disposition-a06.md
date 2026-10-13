# Runner A15 compiler A06 actual preflight failure

ROOT rejects the A06 execution result. No compiler process started. The reviewed
native A15 source remains preserved and uncompiled.

ROOT launched the exact held A06 capsule using the saved 24-key gate. The actual
caller PID and private group were 39543. The caller exited 1, was reaped, and
both PID and group are absent. Both caller streams closed. Stdout contains zero
bytes. Stderr contains 193 bytes. The attempt directory remains absent.

The capsule entered the compiler caller. The caller authenticated and imported
A04 process utility, then failed before owning an attempt. The emitted state is
`runner_a15_fixed_compile_pre_attempt_failure`, stage
`validating_fixed_arguments_and_gate`, error class `BoundFailure`, and code
`caller_value_error`. The emitted code does not identify the predicate.

ROOT independently remeasured the dependency preflight and all 66 suffix rows.
The broad `.rlib`/`.rmeta`/`.dylib` filter includes one old subject library:
`native-preparation-pure-attempt-a05/libnative_preparation_implementation_a04.rlib`.
That library is outside both fixed dependency directories and outside the
runner's source-proof rows. Exact parent-directory selection yields the declared
65 dependencies. All selected dependencies match current full identity-bearing
runner source-proof rows. This establishes the source-derived count failure;
it does not claim the caller emitted that predicate code.

A new wrapper must select the two exact fixed dependency directories. It must
preserve bounded preflight failure codes. Keep all four compiler commands,
archives, native source, schedules, runtime, and output identities unchanged.
Preserve A06 source, source reviews, gate, and actual failed launch receipts.
A new source review and exact gate are required before another caller launch.

Actual ROOT readback: `/Users/aira/projects/remix-gpt-coding-agent/artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a15-compiler-a06-preflight-failure-root-readback-a01.json` (48258 bytes,
SHA-256 `3984b93ca45528a8977f431956cf084085ff4861a5e39792933e74ad3d7326af`). Compiler, controls, native producer, native result,
product integration, WATCHED, HEARD, and creative acceptance remain false.
