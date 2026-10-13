# Native text pure callback and build closure review A02

## Disposition

The frozen A05 Rust source and release build pass their stated path-bound closure checks.
The production callback control has not run during this review.

The control helper is not evidence-closed for execution yet.
It has two P2 evidence gaps: it does not bind every helper/build-record input before and after the
control, and two log-reading paths are not actually bounded.
The report correctly says that no active filesystem-growth cap exists.

This review did not run Cargo, rustc, rustfmt, the control helper, the Rust test binary, ImageIO,
or any native framework call.

## Frozen source and review chain

The source freeze is
`rust-source-freeze-before-build-a05.json`, SHA-256
`40e51ff72c5229493e796ee767468e87d7d0be2825b9b1c99b2d57d446f10344`.
It binds fourteen A05 source and contract files, including `Cargo.toml`, all ten Rust modules,
and the format and semantic patches. Its state is
`fourteen_reviewed_A05_source_and_contract_files_frozen_before_lock`.
It keeps `nativeExecutionAllowed: false` and `productIntegrationAllowed: false`.

The complete source review is
`apps/video-studio/docs/design/text-rust-source-review-a05.md`, SHA-256
`534a7ffd6d75843199b7c594d1cd39fd234962ecfbaef20202cfda47608f388d`.
The preserved review identifies the CGDataConsumer feature and bounded PNG sink, while leaving
callback execution unverified.

The correction record is
`rust-review-model-hash-correction-a05.json`, SHA-256
`7ec8e56defa837658ca7865395cf93711a7c31405e1281417b0d35dcb275b2cb`.
It binds the unchanged 23,434-byte `src/model.rs` to SHA-256
`0af5ec5e375a4d3ace3498e97f1cf6d01d3921bcdaed52eac2dd2dd731947fb4`.
The complete value repairs a 61-character value in the review table.

The A05 semantic patch is SHA-256
`1dcbfa7ce74a41b8eb124624f16e9a5ae2a9552e148ee4ca6c1488e7042cfdd5`.
The format patch is SHA-256
`1132034b6f2f16c341755f78a9cbf8367b9924db36b67bd474f29e61a755179b`.
The format-transfer review is
`rust-format-transfer-review-a05.json`, SHA-256
`27c74bd3e5fa8c448af8e83c7afc1c9056e90dcc755bfaf4bf0cd3132f12085d`.
It records exact reproduction of all fourteen A05 files.

## Lock and dependency closure

The A05 lock review is
`rust-lock-dependency-review-a05.json`, SHA-256
`930f421dcdc2431b3b9405d8eb9b41cbeed8359a49882d83191b66448f959592`.
It records 35 matched package records and 1,847 matched cached source files.
The only direct feature change is `objc2-core-graphics = 0.3.2` adding `CGDataConsumer`.
The resolved feature set has no other changes.

The generated A05 lock has 8,415 bytes and SHA-256
`644a972b539c9a05ed180b98c7662f829eb24ae03fd6cc063ec623c58af389af`.
The dependency source closure is
`rust-dependency-source-closure-a05.json`, SHA-256
`6e06cc43b0c23b1aa3f1c9e9577d458846fb3d7e05ed731409b27b91528f6577`.
The A08 resolution report is
`rust-build-attempt-a08/report.json`, SHA-256
`df7d0e26f89aa00a3584d88b152f04b9cb95735d677f762adc31bdfc10b4da97`.
Its 160-byte lock log records 35 packages, including `objc2 0.6.4` and `sha2 0.10.9`.

The compile gate is
`rust-compile-release-a05.json`, SHA-256
`b5218dba31a4ba4e3176d9b4fb65a75ce10c7d9f59cbe759cb63a4c632310`.
It has ten binding rows and keeps native execution and product integration false.
An independent read-only rehash matched all 14 freeze rows, 10 gate rows, 1,847 dependency
files, and 35 archives. The 1,906 row occurrences had zero mismatches.

## Release build closure

The A09 attempt report is
`rust-build-attempt-a09/report.json`, SHA-256
`4a990e76f92f8959389a4fc17cc0d05dff73512a2405f785c7d33e756874ff4b`.
Its state is `release_build_complete_probe_unexecuted`.
It records the A05 source root, target `aarch64-apple-darwin`, and `probeExecuted: false`.
The report records 1,897 post-build identity checks with an empty error list.

The release command used Cargo 1.94.0, `--offline`, `--locked`, `--release`, and the
`aarch64-apple-darwin` target. The recorded environment set `RUSTC`, `SDKROOT`,
`MACOSX_DEPLOYMENT_TARGET=26.0`, and `CARGO_INCREMENTAL=0`, after removing Rust flag wrappers.
The 2,450-byte build log has SHA-256
`040306ccb29a6b374b849aa1f2578363870eb9673cdb9015d38f8e3beb9bdf83`.
It contains three dead-code warnings and no build error.

The build record is
`rust-build-attempt-a09/release-build.json`, SHA-256
`4afc20cdaedf98a2b49b0fa8dd4bab45147acb530188e324202b11bcc3805198`.
The binary is
`rust-build-attempt-a09/target/aarch64-apple-darwin/release/native-text-feasibility-rust-a05`.
It has 1,186,064 bytes and SHA-256
`298f4e4408a4dd8dd2ff1e556cd13c1c6e2ca9cf1771796e75d56460b43f0528`.

The saved build closure is sufficient for a path-level successful compile and link.
It does not attest loaded compiler, linker, SDK, framework mappings, inherited environment,
native callback behavior, or text output.

## Callback control source and command

The exact Rust test is
`native::png_consumer_controls::bounded_png_consumer_accepts_boundary_and_rejects_overflow_before_copy`.
It is in the frozen `src/native.rs` test module at the recorded callback-control source.
The test uses only Rust filesystem, hashing, cancellation, and the private callback state.
It does not call ImageIO or a native framework.

The test covers these production callback boundaries:

- exact cap acceptance;
- overflow rejection before copying;
- unchanged partial bytes and SHA-256;
- zero writes after the first error;
- cancellation before callback entry; and
- no Rust unwind through the callback boundary.

The root runner is
`run_rust_png_control_a01.py`, SHA-256
`401ef667732ec45fbb7c6db820bc92e646b2218649ac2cfa30a0e1e5f1fb0416`.
It builds with the exact command `cargo test --offline --locked --release --target
aarch64-apple-darwin --target-dir <output>/target --manifest-path <source>/Cargo.toml
--no-run --message-format=json`, then runs one exact test with `--nocapture --test-threads=1`.
The explicit environment contains `HOME`, `PATH`, `TMPDIR`, `RUSTC`, `SDKROOT`,
`MACOSX_DEPLOYMENT_TARGET`, and `CARGO_INCREMENTAL`.
The scope correctly excludes ImageIO, native text production, product integration, RSS, playback,
hearing, and creative acceptance.

## P2 findings in the control helper

### P2-1: control closure omits helper and build-record identities

The helper verifies the frozen source rows, dependency rows, compile-gate bindings, toolchain rows,
release binary, and generated control executable before the test. Its `finally` loop rechecks those
rows after the test.

The helper itself is not in that expected list. It only records `descriptor(__file__)` in the final
report. It has no before descriptor and no equality check after execution.
The A09 report and A09 release-build record are read and the A09 state is checked, but their own
file identities are not added to the expected list.
The saved build report can therefore change without appearing in `afterIdentityErrors`.

Before execution, the runner should bind its own source, the A09 report, the release-build record,
and any declared control configuration. It should recheck every descriptor after the test and retain
before and after observations. This remains a path-level byte and metadata check, not loaded-vnode
proof.

### P2-2: log-reader cap is applied after an unbounded read

`step` hashes each log with `hashlib.file_digest` before checking its 4 MiB size.
The direct-control path then calls `test_log.read_bytes()` without a size bound.
The compiler log has a 256 KiB per-line check, but its complete-file descriptor is still unbounded.

The runner may keep the current statement that the cap is a reader cap rather than an active disk
cap. It needs a bounded chunk reader for both complete logs before hashing or parsing.
The bounded reader should check stable metadata before and after, reject a file above 4 MiB before
allocation, and preserve the exact partial observation on failure.

These findings do not imply a native or product defect. They block a fully closed control evidence
report until the runner is repaired and independently reviewed.

## Acceptance boundary

The release build is path-bound and complete for its recorded source, lock, dependency, toolchain,
and binary rows. The callback test remains unexecuted.
No native callback, ImageIO operation, text producer, product process, GPU, Resolve operation,
watching, hearing, or creative acceptance occurred in this review.

This is a same-model-family review. No cross-family reviewer was available.
