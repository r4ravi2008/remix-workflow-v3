# Runner A15 retained-control ROOT source review A03

ROOT rejects A03 before execution for two P2 evidence-integrity findings.
ROOT measured the manifest, three source rows, and 32 external bindings through
held descriptors. All nine identity fields match during reads and fresh reopens.
Both declared aggregates match. ROOT read the A02 to A03 source delta, contract,
rationale, changed execution-fact and failure paths, build-stream loop, and the
complete 8778-byte peer review. This is source review only.

The complete identity-bearing compiler terminal receipt now joins correctly.
The external readback deliberately keeps its three-field projection. The A06
preparation binding is byte-correct, though its later actual preflight failure
now requires a new compiler wrapper. The fixed 21/10/15/11/5 case schedule,
47 process fields, three malformed fixtures, retained ownership, and Supervisor
A02 current-byte pins remain preserved.

## P2: compiler command contaminates retained-phase evidence

A03 initializes global `phase = None`, then overwrites `phase` in the loop over
`build['commands']` before calling the retained Supervisor. The execution-fact
reader and failure hook read that same global. A preflight failure can therefore
publish a compiler command as `retainedDriverPhase`. A raised Supervisor call
can falsely claim `returnedPhaseAvailable` and `savedObservationKind` of
`returned_phase`, even when no saved observation exists. Use a distinct retained
phase variable and require an actual returned call for returned-phase evidence.

## P2: saved observation does not satisfy the declared exact schema

A03 validates only selected top-level fields in each saved observation. The
post-resume branch can accept `driverResumed: true` with `driverPid: null` and
then claim control code execution. Complete state-specific key sets and nested
typed fields are required. Resume evidence requires a positive PID and started
fact. Preserve unknown execution for raised calls without valid observation and
for uncertain resume delivery; a false stored flag alone is not proof of no
execution when delivery is explicitly uncertain.

ROOT independently confirms the peer's two findings from the frozen source.
No candidate import, compiler, control, process probe, native producer, media,
GPU, playback, listening, or creative review occurred during this source review.
Do not create an A03 execution gate. Repair only these joins in a new package.

Held readback: `/Users/aira/projects/remix-gpt-coding-agent/artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a15-retained-control-root-held-source-readback-a03.json` (22854 bytes,
SHA-256 `2f1c02b6c8758a5f1c0826dee663d7b62ed2ee67ef2e883a9fe7553f39b7df98`). Source aggregate `f9deab0e31fd63b64e1e3bdf49c8dc28dce863103ae77da15644cdd143ecb795`.
External aggregate `88e9f8a601b88cf8084be84aaec323f762f033008e5f249ae90a366c2b7f4eef`. Peer review SHA-256 `c404697d94b4e15d57b71831f8473b553ff1435d890c05fe6a5b57cae484bfc4`.
