# Rust producer qualification A04 build evidence peer review

This is a finite saved-evidence review of the A04 Rust qualification attempt. It is a same-model-family, nonblind review. I inspected and rehashed the saved package and attempt files. I did not import the target package, compile it, rerun the failed command, launch a child, or perform a native, media, product, WATCHED, HEARD, or creative action.

## Source and recipe bindings

The source package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-qualification-a04`

Its source manifest is `69908` bytes with SHA-256 `4177c764bd87305bb77b02444ead3fa9896847f84b2fc1ffba7fbfcc3ff46c99`. The manifest declares eight package rows totaling `133854` bytes. I rehashed all eight rows and recomputed the documented source aggregate:

`898fc6c37c62f7d7c82beadacd3ffdd9e453a5d64184335a4b3565d43ff1feb2`

The package rows and aggregate matched. The manifest binds 135 external rows totaling `29776046` bytes. I rehashed every external path and recomputed the role-plus-path aggregate:

`d39dafc1fce33f0bb97df21daddc42f8c5501708487d1c1eba49fe33a0e0fd77`

The external rows and aggregate matched. The direct build recipe is `8296` bytes with SHA-256 `52e38c7148fa9954780d28e3ae2672f9f644fcad5d7bb14d7698ca516ffb7bcc`.

The recipe binds the stable AArch64 macOS compiler, four fixed dependency archives, two dependency roots, ten environment variables, and the declared output paths. It defines two compiler vectors: library compilation and diagnostic compilation. The saved preflight adds their exact ordering, the no-argument diagnostic invocation, and the 60-second and stream guards. The package state remains source-only. The later attempt is a separate failed execution record.

## Saved failed attempt

The attempt directory is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-qualification-a04-attempt-a01`

- `preflight.json`: `146578` bytes, SHA-256 `ed45862270f83edb950e98a111218038448d4235e502c2771259951ea08a807f`
- `report.json`: `285183` bytes, SHA-256 `3ac64c1de32552d0933faf26cc858bb58bb3013de5789ee03fcf2479aa34c64e`
- `0-stderr.log`: `2299` bytes, SHA-256 `b9d9cc9de1359f3d71d7a2b5ab7172afb8d644d3bcb0e8f871f086b059a01099`
- `0-stdout.log`: `0` bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `parent-current-readback-a01.json`: `143361` bytes, SHA-256 `a2f74686e2ab7ac70dcae77f59f9273024071911041894bcf8882d8849a439a9`

The report state is `rust_producer_qualification_a04_diagnostic_failed`. It records `sourceControlOnly=true`, `compiled=false`, `executed=false`, and `controlsPassed=false`. The report has `239` input rows totaling `98993398` bytes and `inputsMatched=true`.

The preflight records the two recipe compiler vectors plus the no-argument diagnostic invocation. The report contains only the library command because that command failed. Its 25-token `rustc` argument vector equals preflight command zero exactly. The diagnostic compile and diagnostic invocation have no result records, which is consistent with fail-fast ordering.

The parent readback independently records the exact fixed argument vector and environment match. It reports one command return code, PID `90339` reaped and absent, no timeout, no termination request, no overflow, and no held stream. The current readback confirms the library process ended with return code `1`.

## Compiler failure

The compiler stderr is `2299` bytes with SHA-256 `b9d9cc9de1359f3d71d7a2b5ab7172afb8d644d3bcb0e8f871f086b059a01099`. It contains two E0425 errors:

- `qualification.rs:1249`: `CHILD_LOG_BYTES` is not in scope.
- `qualification.rs:1292`: `CHILD_LOG_BYTES` is not in scope.

Both uses are in the qualification module. The compiler suggests importing the existing crate-root constant. The same stderr contains two inherited warnings for an unused import and unused variable. No binary was produced, no diagnostic harness was compiled, and no control ran.

The stdout log is empty. The report records no binary Mach-O and no generated outputs. The seven canonical diagnostic paths are absent. The parent readback also records absent reader-control and future-evidence roots. The attempt temporary directory exists only as an empty directory.

## Input and absence readback

I compared the 239 preflight rows with report `inputsBefore`, report `inputsAfter`, and parent `currentInputs`. All sets have 239 rows. Before and after rows are equal. Every current path is a regular file with matching byte count, SHA-256, and all nine recorded identity fields. No current row mismatched.

The report has no generated outputs and no temporary entries. The parent readback has no generated outputs. Every declared canonical output path is absent. The reader-control root and future-evidence root are absent. The compiler log rows match their current files, including the empty stdout and 2299-byte stderr.

## Scope disposition

The report and parent readback keep these fields false: `nativeProducerExecuted`, `acceptedValueConstructible`, `executionAuthorized`, `trustPinPresent`, `productIntegrationAllowed`, `watched`, `heard`, and `creativeAccepted`.

The saved evidence proves one bounded compiler failure and its cleanup. It does not prove diagnostic compilation, control behavior, native producer qualification, an active pin, authorization, product integration, media output, or human WATCHED, HEARD, or creative approval. The failure is a missing `CHILD_LOG_BYTES` import or qualification at the two reported uses. No source repair was applied during this review.

