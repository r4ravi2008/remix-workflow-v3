# Rust producer subject adapter A06 build evidence peer review

## Scope and method

This review covers the saved A06 failed-build attempt only. It does not import
the adapter, rerun `rustc`, run the harness, run controls, or start native or
media work.

The evidence root is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-subject-adapter-a06-attempt-a01`

I reopened the saved regular files and used `lstat` for recorded paths. I
checked recorded content hashes, byte counts, and the nine identity fields in
each input row: `bytes`, `mtimeNs`, `ctimeNs`, `device`, `inode`, `mode`,
`links`, `uid`, and `gid`.

## Source package binding

The A06 source package remains source-only. Its manifest is 36,467 bytes with
SHA-256 `7fba1918331d5f3ad8c804ef9e0c5c680ee81006c72df631f6265b2114207480`.
All 14 manifest rows match their current package files. The declared source
aggregate recomputes to
`89e67bdee20ea8aa59391e78a5ccfcdfd904adc994fb036f24ea01f444ebf8b2` using
the published domain, one NUL terminator, big-endian row-count and total-byte
prefix, ascending UTF-8 path ordering, and raw SHA-256 row encoding.

The package declares `source_only_uncompiled_unexecuted`. Its direct compile
recipe binds `libc`, `serde`, `serde_json`, and `sha2`. The later saved command
also contains all four `--extern` arguments. This is a source-package binding,
not a successful-build claim.

## Preflight and process result

`preflight.json` is 86,080 bytes with SHA-256
`667770a35786dc93b2d38134f17ead5288031d105c4297826171942de8c494a2`.
It records 137 input rows totaling 76,815,591 bytes, a 60-second command
limit, a 4 MiB captured-stream limit, `sourceControlOnly=true`, and
`nativeProducerAllowed=false`.

The preflight lists three planned commands: library compilation, harness
compilation, and harness execution. The saved attempt executed only the
library command. No harness or control command ran.

`report.json` is 169,427 bytes with SHA-256
`b72e9fa8da8adaa91e701702d866ab88af1be5257d923f822890072597146d8bf`.
It truthfully records:

- state `fixed_attempt_failed_preserved`;
- `compiled=false`, `executed=false`, and `controlsPassed=false`;
- one `library` command with return code `1`;
- compiler PID `81884`, `reaped=true`, and elapsed time
  `0.4018192500079749` seconds;
- no timeout, stream overflow, or unclosed streams;
- zero generated outputs and no Mach-O record;
- an empty temporary-entry list;
- absent FIFO and vector fixture roots;
- false native, trust, execution, product, watched, heard, and creative
  fields.

The failed command did not create the requested library or harness output.
Both canonical `/private/tmp` output paths were absent. Both fixture roots
were absent. The attempt `tmp` directory contains no entries.

The process evidence supports the saved `reaped=true` result for this failed
library command. This review makes no stronger process-lifecycle claim.

## Compiler diagnostic truthfulness

`library.stdout.log` is empty, 0 bytes, with SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
`library.stderr.log` is 2,410 bytes with SHA-256
`ebe2046c8e5b1a488c5f890f784447f5ed269de5aca8a2fa2bd4d44f5c9d71b7`.

The compiler emitted two warnings and one error. The warnings are an unused
`SavedReportKind` import in `rust_producer_subject_adapter_v3.rs:6` and an
unused `rows` parameter in `rust_producer_subject_adapter_v3.rs:1848`.

The build-blocking error is E0599 at
`diagnostic_controls.rs:166:74`. The code calls `error.to_string()` while
mapping a `ValidationError`. The bound type at the reused `model.rs:39` does
not implement `std::fmt::Display`, so `ToString` is unavailable. The compiler
then aborts after this one error.

This is a real source compile failure. The direct four-archive recipe is now
present, so the A05 missing-extern cause does not recur. The saved report does
not claim a successful library, harness, or control result.

## 137-input readback

The preflight input rows equal `report.inputsBefore` exactly. The report
contains 137 rows in both `inputsBefore` and `inputsAfter`, with exact array
equality and total bytes `76,815,591`.

All 274 before/after rows point to regular files. Every row matched its
current nine-field `lstat` identity, recorded byte count, and SHA-256. No
input changed during the failed command. The compiler stdout and stderr
stream rows also matched their current identities and hashes.

## Documentation reconciliation

The report records the known nonblocking note that
`diagnosticHarness.fixedInputs` names `libc` and `sha2` but omits `serde` and
`serde_json` in that prose sentence. The exact compile argv and
`compileAuthority.archives` bind all four archives. The reconciliation is
recorded in
`apps/video-studio/docs/design/rust-producer-subject-adapter-parent-peer-reconciliation-a06.md`,
which is 1,259 bytes with SHA-256
`8a73fd2f4466de8158d45e43878816a71b0e5cb6d392bc94f6ef725ad492edd7`.
This prose omission does not change the saved command or input evidence.

## Disposition and limits

The saved A06 failed-build evidence is internally consistent and truthfully
bounded. The package is source-only. The separate attempt records one reaped
library compile failure caused by the missing `Display` implementation, with
complete 137-input preservation and no generated output.

This evidence does not qualify the adapter, harness, Rust producer, native
framework, media, observer, comparator, Swift path, GPU, Resolve path,
product integration, watched result, heard result, or creative acceptance.
This review did not rerun or import any target code.
