# Rust producer runner A04 build evidence peer review

## Disposition

The saved A04 build evidence is internally consistent for its declared scope:
one library compile, one CLI compile, and one unavailable-qualification CLI
probe. I found no P1 or P2 evidence-integrity finding.

This review is read-only and same-family. I inspected the saved report,
preflight, output receipts, logs, and current input rows. I did not compile,
import, execute, or invoke the binary during this review.

The evidence does not establish a Rust A05 producer run, native output, media,
audio, GPU, Resolve, product integration, WATCHED, HEARD, or creative
acceptance. No Clippy result is claimed.

## Attempt and input closure

The attempt is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-build-attempt-a02`

`report.json` is 112,072 bytes with SHA-256
`af18f1f39714d80dfbef3f26b0701a975e9bf3b6a4128d9e49096555843051db`.
Its state is `rust_producer_runner_a04_built_and_unavailable_cli_verified`.

The report records 83 input rows totaling 75,295,604 bytes. The before and
after arrays are equal. `inputsMatched` is true. Every row carries these nine
identity fields:

```text
bytes, device, inode, mode, mtimeNs, ctimeNs, uid, gid, links
```

The saved preflight contains the same 83 input rows. The eight A04 manifest
rows and their hashes are present in the report input set, with aggregate
`c658f23cd62b58cfb698ee2738cecbc2bb9ac7fa8e17062dfc642d7eca9a890a`.

The preflight records three commands, a 60-second timeout per command, a
4 MiB captured-stream cap, and an attempt-private `TMPDIR`. Its environment
includes the exact fixed values `LANG=C`, `LC_ALL=C`, `PATH=/usr/bin:/bin:/usr/sbin:/sbin`,
`TZ=UTC`, `MACOSX_DEPLOYMENT_TARGET=26.0`, the stable AArch64 toolchain, and
the MacOSX26.1 SDK. The saved input and output rows retain descriptor facts
before and after the three commands.

## Command results

1. The library rustc phase targets `aarch64-apple-darwin`, uses edition 2024,
   panic abort, the fixed dependency archives, and A04 `src/lib.rs`. It returns
   code 0. Its output is `librust_producer_runner_a04.rlib`, 2,972,048 bytes,
   SHA-256 `3c697bea9b5369109498637dedd649de177e15af4c1cb0fed32c85b115d34dad`.
   Its stderr contains exactly two dead-code warnings. Its stdout is empty.

2. The CLI rustc phase compiles A04 `src/main.rs`, links the saved A04 rlib,
   uses thin LTO, and returns code 0. Its output is
   `rust-producer-runner-a04`, 1,531,272 bytes, SHA-256
   `4533f514e9fb5f44755a8713a952a2b5976b81c79e21cc6d58049f2ebb836659`.
   Its stdout and stderr are empty.

3. The saved CLI probe invokes that path with an absolute output parent and
   `--repetition primary`. It returns code 78. Its stdout is exactly:

   ```json
   {"schema":1,"state":"rust_stage_acceptance_unavailable","nativeAccepted":false}
   ```

   The probe stderr is empty. The report records no temporary entries, no
   created output parent, `rustA05NativeChildStarted=false`, and
   `nativeAccepted=false`.

The report records the compiled CLI as arm64, Mach-O file type 2, UUID
`b5911de1224f3ca6beede0cbd2ca6265`. The two output receipts match the report
output rows and current file bytes.

The saved stream identities are also consistent: the library stderr is 1,079
bytes and contains the two warnings; library stdout, CLI stdout, and CLI stderr
are empty; the unavailable-loader stdout is 80 bytes; and the attempt directory
contains no extra temporary entries.

## Scope limits

This is compilation and unavailable-loader evidence only. The saved probe did
not construct an accepted qualification, create an output parent, or launch
the Rust A05 native child. No source tests, Clippy run, subprocess lifecycle
test, codec test, media proof, audio proof, GPU proof, Resolve proof, or product
acceptance is established.

