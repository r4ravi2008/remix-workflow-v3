# Swift compiler-only wrapper A02 source review

## Result

`run_swift_typechecks_a02.py` is a source-only compiler wrapper. It invokes `swiftc` with `-typecheck` and never builds or starts the producer or control. It does not establish native framework behavior, loaded compiler identity, text shaping, raster output, or creative acceptance.

The wrapper has useful path-bound closure checks. Two source changes remain advisable before treating it as a strong compiler-evidence gate: bind the initial manifest read to the observed descriptor, and compare manifest compile-unit lists in order. Early failures also need an explicit report-preservation boundary.

## Reviewed identity

| file | bytes | SHA-256 |
| --- | ---: | --- |
| `run_swift_typechecks_a02.py` | 7,313 | `320d288734d4d64ee3a8f25acb42dacb32d757ea7a41894243c541400bec2428` |

The wrapper source was read through line 141. This review did not run it, invoke Swift, compile Swift, call ImageIO/CoreText, or inspect native output.

## Findings

### P2 — Initial manifest read is outside the bounded descriptor observer

Lines 58–62 use `manifest_path.read_bytes()` before `observe()` verifies the manifest. This path-based read has no wrapper cap, stable descriptor check, or special-file protection. It can read different bytes from the later closure or allocate beyond the intended observation bound.

The wrapper should read the manifest through the same bounded descriptor path used by `observe()`. It should hash and parse that exact byte buffer, then retain its identity for the initial validation. The later closure correctly rechecks the manifest against its pinned SHA, but it cannot repair an unsafe or unbounded first read.

### P2 — Compile-unit joins are set comparisons, not ordered joins

Lines 75–79 compare `compileUnits.producer` and `compileUnits.control` through sets. The checks reject missing and extra names, but accept a reordered manifest list. The compiler commands use the CLI order at lines 105–106. If the manifest order is provenance, compare the lists directly with the requested order, including the header position.

### P2 — Failures before the main `try` have no structured preserved report

The existing-attempt check, initial closure, output-directory creation, and report initialization run before line 108. A failure in those operations can raise without `report.json`. The final report write at line 137 is also outside a preservation guard. The wrapper therefore preserves failures after the main `try`, but does not prove preservation for setup or report-publication failures.

The contract should either create an exclusive attempt directory and minimal failure record before closure, or state that preservation begins only after the report is initialized. A final write or sync failure should retain the partial-file identity when the contract requires durable causal evidence.

### Documented limit — Log cap is postprocess only

The child process writes stdout and stderr directly to each log at lines 110–114. `observe(log, 4 * 1024 * 1024)` limits the later read and identity check at line 122. The report correctly labels this as `postprocess read cap only`. It does not cap child disk writes or prove a bounded subprocess log file during execution.

## Confirmed source controls

`observe()` opens one descriptor with `O_NOFOLLOW`, checks regular-file type and size, streams bounded reads, hashes the bytes, and compares device, inode, mode, size, modification time, and change time before closing. The closure includes the wrapper, Python executable, pinned manifest, compiler, SDK settings, and every manifest source row. It rechecks each manifest row's bytes and hash before and after the typechecks.

The wrapper refuses a pre-existing attempt directory and uses exclusive log and report creation. It fixes the environment, SDK, target, working directory, compiler arguments, timeout, and stdin. The only child commands are `swiftc --version` and `swiftc -typecheck`; no binary or native producer process is launched. `producerStarted`, `controlStarted`, and `nativeFrameworkCalledByProducer` remain explicit false report fields, while `loadedCompilerAttested` remains false.

The wrapper records command results, timeout or launch errors, bounded postprocess log identities, and before/after closure drift. These checks support compiler-source and filesystem-integrity evidence only. They do not qualify a future Swift A10 producer, its manifest, or any native run.

## Disposition

Keep this review additive. Preserve the wrapper and its hash unchanged. Repair the manifest read, ordered compile-unit join, and setup-failure preservation in a successor before using the wrapper as a stronger gate. Bind any later successor to the final Swift A10 source manifest and exact file identities. Same-model-family source review is recorded here; no independent compiler or native execution was performed.
