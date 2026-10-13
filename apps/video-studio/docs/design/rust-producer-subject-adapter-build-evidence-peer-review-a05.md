# Rust producer subject adapter A05 build evidence peer review

## Scope and method

This review covers the saved A05 failed-build attempt only. It does not import the adapter, rerun `rustc`, run the harness, run controls, or start native/media work.

The evidence root is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-subject-adapter-a05-attempt-a01`

I reopened regular files and used `lstat` for recorded paths. I checked recorded content hashes, byte counts, and the nine identity fields present in each input row: `bytes`, `mtimeNs`, `ctimeNs`, `device`, `inode`, `mode`, `links`, `uid`, and `gid`.

## Source package binding

The source package remains source-only. Its manifest is 33,701 bytes with SHA-256 `3c198d24784a6da2911898dd1609ed5387d771b30d32c6d59b8a248f4092e54a`. All 14 manifest rows match their current package files. The declared source aggregate recomputes to `3b81fbe1e3642f1d1bb5c4d80983767b44d7c2e21c9d18f4fe7d5567d5cc7af9` using its published domain, row-count and total-byte prefix, UTF-8 path ordering, and raw SHA-256 row encoding.

The package manifest is `source_only_uncompiled_unexecuted`. Its compile authority lists only `libc` and `sha2` archives. It does not list `serde` or `serde_json` archives. This omission matches the saved direct compile command and explains the primary failure.

## Preflight and process result

`preflight.json` is 82,056 bytes with SHA-256 `d59b77f095bf68a274c29b53d5ae028e1c5f55c83a55df88c6aacf8e990329b7`. It records 131 input rows totaling 76,512,015 bytes, a 60-second command limit, a 4 MiB captured-stream limit, `sourceControlOnly=true`, and `nativeProducerAllowed=false`.

The preflight lists three planned commands: library compilation, harness compilation, and harness execution. The saved attempt executed only the library command. No harness or control command ran.

`report.json` is 171,772 bytes with SHA-256 `3123a43451b3b9f2bfdbd1e2aab417cb3a383292bd3f55bb9b4ecd3b08ee23f2`. It truthfully records:

- state `fixed_attempt_failed_preserved`;
- `compiled=false`, `executed=false`, and `controlsPassed=false`;
- one `library` command with return code `1`;
- `reaped=true`, elapsed time `0.30199545800860506` seconds;
- no timeout, stream overflow, or unclosed streams;
- zero generated outputs and no Mach-O record;
- empty temporary entries;
- absent FIFO and vector fixture roots;
- all native, trust, execution, product, watched, heard, and creative fields false.

The failed command did not create the requested library or harness output. The two canonical `/private/tmp` output paths were absent. The two fixture roots were also absent. The attempt `tmp` directory contains no entries.

The saved process closure is sufficient for this failed attempt. `rustc` PID `80575` returned `1` and was reaped. This review makes no stronger process-lifecycle claim than the saved `reaped=true` result.

## Compiler diagnostic truthfulness

`library.stdout.log` is empty, 0 bytes, with SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. `library.stderr.log` is 12,106 bytes with SHA-256 `b790acca38c73544503040d6fd5d0adffb49d6a6a733bd0316291f38da0ee84d`.

The diagnostic contains 18 compiler errors and one unused-import warning. The first errors are unresolved `serde` and `serde_json` imports in the reused `strict_json.rs`, plus a `serde_json::Number` use in `fixture_controls.rs`. The remaining associated-type and ambiguous-associated-type errors are cascades from those missing crates. The command supplies `--extern sha2` and `--extern libc`, but no `--extern serde` or `--extern serde_json`.

The failure is therefore a real compile failure with a concrete dependency-recipe cause. The saved report does not claim a successful build or any later harness result.

## 131-input readback

The preflight input rows equal `report.inputsBefore` exactly. The report contains 131 rows in both `inputsBefore` and `inputsAfter`, with exact array equality and total bytes `76,512,015`.

All 262 before/after rows point to regular files. Every row matched its current nine-field `lstat` identity, recorded byte count, and SHA-256. No input changed during the failed command. The compiler stdout and stderr stream rows also matched their current identities and hashes.

## Disposition and limits

The saved A05 failed-build evidence is internally consistent and truthfully bounded. The package source remains uncompiled. The separate attempt records a reaped compiler failure caused by omitted `serde` and `serde_json` externs, with complete 131-input preservation and no generated output.

This evidence does not qualify the adapter, harness, Rust producer, native framework, media, observer, comparator, Swift path, GPU, Resolve path, product integration, watched result, heard result, or creative acceptance. This review did not rerun or import any target code.
