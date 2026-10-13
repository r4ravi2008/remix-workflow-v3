# Rust producer subject adapter A07 peer source review

## Disposition

A07 closes the preserved A06 `E0599` compiler defect at source level.

I found no P1 or P2 source defect in the requested bounded scope.

The repair uses the existing `ValidationError.code` and `ValidationError.detail` fields. It does not require `Display` or change RoleIndex validation behavior.

A07 remains uncompiled and unexecuted. This review does not establish build success, control success, native execution, trust, or acceptance.

This was a read-only review by a separate author. It is same-model-family and nonblind.

## Frozen package and closure

The reviewed package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-subject-adapter-a07`

The self-excluding manifest is 38,040 bytes with SHA-256:

`47c01337bc4703deddf7a948ba88f39146a1eaca02d7b65ca2b81f067463ed68`

I rehashed every declared file and reconstructed both documented aggregates:

- 14 source rows, 249,455 bytes, `3d2dc8c4d5c073ce54cf50f0cd430fc3e83c1a7b1d53c68e533609395dedde76`
- 36 external rows, 1,024,142 bytes, `85183b601a919950af18d2afacc26fed0ade933282b5a52c7528a1a29f6020b2`

Both aggregates use the declared ASCII domain, one NUL byte, row and byte totals, UTF-8 path order, and framed rows.

The package inventory contains the 14 source rows plus the self-excluding manifest. I found no undeclared package file.

The declared A07 attempt directory and four disposable output/control paths were absent during this review. These are pathname observations only.

## `E0599` repair and error formatting

The preserved A06 stderr contains one compiler error. Rust reports that `ValidationError` does not implement `Display` at `diagnostic_controls.rs:166`.

A07 replaces only that failing expression:

```rust
AdapterError::new(
    "scalar_vector_encode",
    format!("{}: {}", error.code, error.detail),
)
```

`ValidationError` publicly owns those two fields. The new expression preserves both values and remains bounded by `AdapterError::new`.

I traced the other encoding and validation conversions in the complete source closure:

- candidate and saved-report RoleIndex encoding use `AdapterError::from(ValidationError)`
- semantic-baseline adapters move the bounded validation `detail`
- control expectations compare the validation `code`
- remaining `error.to_string()` calls format types that implement `Display`, including I/O, UTF-8, integer-parse, NUL, JSON, and formatting errors
- path and integer `to_string()` calls do not format validation errors

I found no second `ValidationError.to_string()` or equivalent unsupported formatter.

## Successor comparison

The only executable A06-to-A07 semantic edit is the scalar-vector error conversion above.

The FIFO and vector modules change only their fixed disposable `a06` paths to `a07`. `src/lib.rs` and `src/saved_report_adapters_v1.rs` change only lineage comments.

These production files remain byte-identical to A06:

- `fixtures/subject-authority-a01.json`
- `src/fixture_controls.rs`
- `src/rust_producer_subject_adapter_v3.rs`
- `src/subject_observation.rs`

The harness and three contracts match A06 after exact A06-to-A07 label substitution. The manifest also updates the crate, library, harness, attempt, and output identities consistently.

I found no candidate-row, validation, measurement, publication, or serialization change.

## Compile recipe and predecessor failure

The fixed library command binds all four direct external archives:

- `libc`: 2,872,080 bytes
- `serde`: 951,904 bytes
- `serde_json`: 1,983,472 bytes
- `sha2`: 178,528 bytes

Each archive matches its manifest hash. The compiler, preflight, and dependency closure also match their declared bytes and hashes.

`diagnosticHarness.fixedInputs`, `README.md`, and `subject-contract-a07.md` now name all four archives. This closes the A06 prose omission.

The recipe retains the repository working directory, both measured dependency roots, edition 2024, `panic=abort`, and thin LTO for the harness. It performs no Cargo resolution.

A07 binds the A06 manifest plus its report, preflight, stdout, and stderr. The preserved report records return code 1, no completed library, no harness execution, and no controls. The preserved stderr contains the single `E0599` error and two warnings.

A07 does not rewrite the failed attempt or represent it as successful evidence.

## Controls and schedule

The fixed control count remains 28:

- 12 historical fixture mutations
- 3 scalar-wire controls
- 2 FIFO rejections
- 4 reader controls
- 5 schedule controls
- 1 PNG join control
- 1 compilation-boundary control

The complete source-owned schedule remains 2,068 rows:

- source: 38
- dependencies: 1,889
- build phase: 19
- toolchain projection and report: 90
- input: 25
- PNG control: 7

The unchanged validator sorts by UTF-8 role bytes, rejects duplicates, and compares every role, tag, and ordinal before encoding. The schedule-control mutations remain remove, add, retag, and reorder.

The 4,158-byte diagnostic vector identity remains unchanged. Scalar wire expectations remain fixed-width big-endian values for unsigned 42, signed -42, and unsigned zero.

These controls are still source declarations. No control or diagnostic harness ran during this review.

## Review boundary

I did not compile, import, assemble, or execute the library, harness, or controls.

I started no child, native framework, media, GPU, or Resolve process.

This review creates no `Accepted<T>`, trust root, active pin, execution authorization, or product authority.
