# Rust producer subject adapter A05 peer source review

## Disposition

I found no P1 or P2 source finding in the frozen A05 package.

A05 closes all four findings from the frozen A04 peer review. The package is source-ready for its declared direct build recipe.

This conclusion is limited to source readiness. A05 remains uncompiled, unassembled, and unexecuted.

This was a read-only, separate-author review. It is same-model-family and nonblind.

I did not compile, import, assemble, or execute the adapter, harness, or controls. I started no child or native process.

## Reviewed authority

The frozen package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-subject-adapter-a05`

The self-excluding manifest is 33,701 bytes with SHA-256:

`3c198d24784a6da2911898dd1609ed5387d771b30d32c6d59b8a248f4092e54a`

All 14 source rows match their declared 249,228 bytes and SHA-256 values.

All 26 external rows match their declared 430,123 bytes and SHA-256 values.

All 20 fixed authority documents match their declared byte counts and hashes.

Both aggregates reproduce from the documented domain-separated recipe:

- source: `3b81fbe1e3642f1d1bb5c4d80983767b44d7c2e21c9d18f4fe7d5567d5cc7af9`
- external: `a638c6d4e48dc2878360b9ca87414171a66075a5f9147c16a090c2f8084c4e60`

The compiler, preflight, dependency closure, `libc` archive, and `sha2` archive match their manifest bindings.

The declared attempt directory and both `/private/tmp` outputs are absent. These are pathname observations only.

## A04 finding closure

### Canonical-report format strings: closed

`diagnostic-harness-a05.rs:376-385` escapes the final literal JSON brace as `}}`.

I inspected every `format!` and `write!` format string in the complete harness. Their placeholders and literal braces are balanced at source level.

This static inspection does not replace a future compiler result.

### Reader-mutation result codes: closed

`src/vector_controls.rs:111-128` expects `subject_file_changed` for both identity mutations.

That code matches the shared production validator used through `MeasurementSession`. The manifest and control contract declare the same two expectations.

The growth and replacement case identifiers remain distinct.

### Candidate summary mapping: closed

`diagnostic-harness-a05.rs:240-269` now checks the fixed fixture resource counts:

- 15 source files
- 1,847 dependency files
- 35 dependency archives
- 89 toolchain rows
- 21 input control identifiers
- 1,921 PNG identity checks

These values match `fixtures/subject-authority-a01.json:111-128` and the unchanged `CandidateSummary` construction.

The complete diagnostic schedule remains separate. Its families total 2,068 rows as 38, 1,889, 19, 90, 25, and 7.

### Direct build path closure: closed

`source-manifest-a05.json:565-624` declares the repository root as the compiler working directory.

The library source, harness source, dependency roots, and both archive arguments resolve from that directory.

The recipe retains the absolute compiler path, edition 2024, target triple, `panic=abort`, and thin LTO for the harness.

The library output keeps the required `lib` prefix. Every output stays under the absent A05 attempt directory.

## Successor binding and inherited behavior

The A05 manifest binds the frozen A04 manifest and peer review with their exact current hashes.

The source and external aggregate domains advance to A05. The package, crate, roots, outputs, contracts, and report operation also advance consistently.

The following production modules are byte-identical to A04:

- `src/diagnostic_controls.rs`
- `src/fixture_controls.rs`
- `src/rust_producer_subject_adapter_v3.rs`
- `src/subject_observation.rs`

Other inherited module changes are successor labels or documentation. The only control-semantic change is the corrected reader result expectation.

No RoleIndex encoding, measurement, report-adapter, or candidate-construction behavior changed.

## Fixed control and publication schedule

The harness requires 12 fixture, 3 scalar, 2 FIFO, 4 vector, 5 schedule, 1 PNG, and 1 compilation-boundary case.

Those families total 28. Their manifest schedule and harness checks agree.

The harness checks every available result and aggregate pass field before publication.

It reconstructs the full candidate twice. It requires exact encoded-byte equality before any output write.

The canonical report remains separate from the candidate RoleIndex bytes. Both outputs use exclusive creation.

The package still cannot construct `Accepted<T>`, create an active pin, or authorize execution.

No native, media, GPU, Resolve, watch, listen, or creative acceptance follows from this source review.
