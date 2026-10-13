# Swift compiler-only wrapper A03 source review

## Result

`run_swift_typechecks_a03.py` is a source-only compiler wrapper. It invokes
`swiftc --version` and `swiftc -typecheck`. It does not build or launch the
Swift producer or control, call ImageIO or CoreText, or establish native text
output.

A03 closes the three A02 source findings. The manifest is observed through one
bounded descriptor before parsing. The initial descriptor is joined to the
closure record. Manifest compile-unit lists are compared in order. The wrapper
creates an exclusive attempt directory and durable preflight record before
source and compiler checks. Failures after that record remain reportable.

## Reviewed identity

| file | bytes | SHA-256 |
| --- | ---: | --- |
| `run_swift_typechecks_a03.py` | 9,226 | `3e320de4bdfa0ca3c1420eaa92e48053a50714dd33a14d9068e0e7632090ffe2` |

This review read the complete 176-line source. It did not run the wrapper,
invoke Swift, compile Swift, call a native framework, or inspect native output.

## Confirmed repairs

Lines 17–45 open each observed file with `O_NOFOLLOW` and `O_NONBLOCK`, require
a regular file within the cap, stream from one descriptor, hash the bytes, and
compare device, inode, mode, size, modification time, and change time before
closing. The retained manifest bytes are the same bytes that are parsed.

Lines 100–126 validate the retained manifest bytes and then compare the
initial manifest observation with the first closure row. The wrapper checks
unique single-component manifest paths, listed Swift and header inputs,
duplicate-free arguments, and exact ordered producer and control lists.

Lines 80–99 define the preservation boundary. A pre-existing attempt is
rejected. The wrapper creates a fresh mode-0700 directory, writes
`preflight.json` exclusively, flushes it, and calls `fsync` before manifest
validation or compiler launch. CLI validation, the existing-attempt check, and
attempt-directory creation remain outside this boundary by design.

Lines 127–147 run only the pinned version and `-typecheck` commands. Each log
uses exclusive creation and records arguments, environment, return status,
timeout or launch failure, and a bounded postprocess observation. The log cap
remains explicitly postprocess-only; it does not cap child disk writes.

Lines 148–176 preserve wrapper errors and source drift. The final report uses
exclusive creation, flush, and `fsync`. A final publication failure emits the
failure state and a bounded partial-report identity to stderr while retaining
the preflight path. The before/after closure includes the wrapper, Python
executable, manifest, compiler, SDK settings, and every manifest file row.

## Scope limits

The report keeps `producerStarted`, `controlStarted`,
`nativeFrameworkCalledByProducer`, and `loadedCompilerAttested` false. The
closure proves file identities and the command records prove attempted
compiler checks. It does not prove the loaded compiler implementation, Swift
type semantics, framework behavior, shaping, raster output, or acceptance.

The final partial-report observation reopens the report path after the writer
closes. It provides causal file identity when the path remains stable. It is
not a same-descriptor publication proof under a concurrent pathname swap.

## Disposition

Accept A03 as the reviewed source successor for the compiler-only preparation
gate. Bind any later run to this exact wrapper hash and the exact Swift A10
manifest, source rows, compiler, SDK settings, ordered command inputs, and
fresh attempt directory. Execution and all native claims remain unverified.

