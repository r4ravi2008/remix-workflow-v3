# Rust producer subject adapter A03 peer source review

## Disposition

The frozen A03 source is not ready for compilation or diagnostic control execution.

I found no new RoleIndex wire-semantics P1. I found seven P2 source-readiness findings.

A03 closes the complete 2,068-row schedule repair and the false scalar/FIFO baseline claims. The checked reader now owns the actual 4,158-byte vector read. Its growth and replacement controls remain incomplete because they do not call that reader.

This was a read-only, separate-author review. It is same-model-family and nonblind.

I did not compile, import, assemble, or execute the adapter, harness, or controls. I started no child or native process.

## Reviewed authority

The frozen package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-subject-adapter-a03`

The self-excluding manifest is 25,945 bytes with SHA-256:

`4fcd4a324e0e337ce74069cb0feae2a3dbde7eed1ac22b953ff6755eb400b7db`

All 14 source rows match their declared 225,998 bytes and SHA-256 values.

All 22 external rows match their declared 353,907 bytes and SHA-256 values.

All 20 fixed authority documents match their declared 896,936 bytes and SHA-256 values.

The unchanged authority fixture is 9,033 bytes with SHA-256:

`548721bcb1805bf9e11be285d1be4c0edfbbd90341e0ed5a5dbe7111cd61db61`

The manifest aggregate values do not reproduce. Finding P2-1 records the exact mismatch.

## P2 findings

### P2-1: Both manifest aggregate digests are incorrect

`source-manifest-a03.json:84-91` declares source aggregate `eaf8d114...`.

Applying `aggregateRecipe` at lines 598-603 to the 14 matching source rows produces:

`533983b33bfbf13c8e6d8ac6d5ca6fc03345c05efeaf8832668528201227719e`

`source-manifest-a03.json:227-234` declares external aggregate `8495d21b...`.

Applying the same recipe to the 22 matching external rows produces:

`f33bd24e613e4d0ce31caab335af0942f0ef42e9ee79cc2f22756ec8057e849c`

The row count, total bytes, individual hashes, sorting, domains, prefix, and row encoding were included in both recomputations. A later build cannot bind this frozen source package through the declared aggregate values.

Regenerate both values from the documented recipe. Preserve the existing row identities and domains.

### P2-2: `validation_code` has no valid return lifetime

`diagnostic_controls.rs:289-293` declares:

```rust
fn validation_code(result: Result<()>) -> &str
```

The function has no borrowed input from which Rust can elide the returned reference lifetime. `AdapterError.code` is static, but the signature does not state that fact.

This is a source-level compile error. Change the return type to `&'static str`, or return an owned value.

### P2-3: The declared harness build route is neither fixed nor complete

`source-manifest-a03.json:538-580` invokes `rustc` through `PATH`. It does not bind the measured compiler executable.

The commands omit the fixed dependency search root needed by transitive archive dependencies. They also omit the required panic-abort and thin-LTO options.

The library output is `/tmp/native-text-feasibility-rust-subject-adapter-a03.rlib`. The harness then supplies that path through `--extern`. The basename does not follow Rust's required `lib*.rlib` extern-file form.

The manifest therefore does not define a reproducible two-step build for the claimed harness. Bind the measured compiler, dependency roots, flags, and a valid library filename.

### P2-4: Growth and replacement controls do not exercise `MeasurementSession`

The actual vector read uses `MeasurementSession` at `diagnostic_controls.rs:174-191`. That closes A02's blocking and unbounded vector-reader implementation.

FIFO and symlink cases call `MeasurementSession::measure_regular` at `vector_controls.rs:65-83`.

Growth and replacement instead pass invented `ReaderSeamFacts` to `validate_reader_seam` at `vector_controls.rs:85-112`. The helper exists only in `vector_controls.rs:165-185`.

`MeasurementSession::measure` does not call this helper. The two cases can pass if the production post-read checks regress.

Exercise the production reader through an injected, private mutation seam. Keep the frozen vector unchanged and use disposable files.

### P2-5: The no-argument harness accepts arbitrary arguments

The README calls the harness a fixed no-argument entry point at `README.md:66-69`. The manifest repeats that precondition at `source-manifest-a03.json:583-584`.

`diagnostic-harness-a03.rs:15-22` enters `run()` without inspecting `std::env::args_os()`. Extra caller arguments are silently accepted.

Reject every argument after `argv[0]` before reading authority or creating output.

### P2-6: A failed PNG control can still publish the candidate output

`run_png_argv0_control` computes `passed` at `diagnostic_controls.rs:85-97`. It returns `Ok(DiagnosticControlSummary)` even when `passed` is false.

The harness stores that summary at `diagnostic-harness-a03.rs:36-37`. It never requires `png.passed` before opening the output at lines 41-49.

The fixed candidate encoding can therefore be published after the required PNG mutation observed the wrong result.

Make the control return an error on mismatch, or gate publication on every required summary's pass field.

### P2-7: Harness control results have no canonical, independently decodable form

The scalar control retains exact ordered hexadecimal bytes in `ScalarWireControlSummary.scalar_wire_hex` at `diagnostic_controls.rs:39-54` and lines 132-208.

The harness writes only the candidate RoleIndex bytes to its exclusive file. It prints scalar and other control summaries with Rust `Debug` formatting at `diagnostic-harness-a03.rs:60-66`.

Rust `Debug` text is not a versioned wire schema. The candidate RoleIndex file does not contain the three scalar-control outcomes.

An independent reader could decode the candidate RoleIndex after a future bound run. It cannot strictly decode or authenticate the scalar and control results from the current harness output contract.

Publish a bounded canonical control report with exact keys, result order, scalar hex strings, pass fields, and false scope fields. Keep the candidate encoding as a separate exclusive output.

## A02 repair reconciliation

### Complete diagnostic schedule: closed at source level

`build_candidate` sorts rows, checks uniqueness, validates the complete schedule, and only then encodes at `rust_producer_subject_adapter_v3.rs:344-368`.

`expected_diagnostic_role_tags` constructs the expectation without reading candidate output at lines 1230-1363. It covers:

| Family | Rows |
| --- | ---: |
| source | 38 |
| dependencies | 1,889 |
| build phase | 19 |
| toolchain projection and report | 90 |
| input | 25 |
| PNG control | 7 |
| **total** | **2,068** |

The source-derived sorted sequence reproduces manifest digest:

`a5ff306ed57b7e4ef44818674efeb03a7950f855d1d30a5e05be1e46f4c05bcf`

`validate_diagnostic_role_tags` checks count, ordinal, role, and tag at lines 1365-1388. The control source includes exact baseline, remove, add, tag-change, and order-change cases at `diagnostic_controls.rs:211-277`.

The toolchain report row is explicit. A05 authority rows remain lineage inputs and are absent from the candidate schedule.

### Checked vector read: implementation closed, negative coverage partial

`run_scalar_wire_controls` binds the vector's exact path, 4,158 bytes, and SHA-256. It reads through `MeasurementSession` only.

`MeasurementSession::measure` uses no-follow and nonblocking flags. It checks regular type, admitted size, descriptor identity, pathname identity, bounded read length, after-read identity, and SHA-256 at `subject_observation.rs:221-345`.

This replaces A02's unsafe fixed-path reader. Finding P2-4 explains why two requested regression controls remain unproven.

### Scalar and FIFO baseline claims: closed

`ScalarWireControlSummary`, `FifoControlSummary`, and `VectorReaderControlSummary` contain no `baseline_passed` field.

Their scope fields remain source-only. Compiler, native producer, and permission fields remain false.

## Confirmed bounded properties

The harness output path is fixed. `diagnostic-harness-a03.rs:41-49` uses `create_new`, writes after the controls return, and calls `sync_all`.

The loader accepts no caller evidence path, role list, count, trust root, or permission.

The candidate remains `RustProducerDiagnosticCandidateV2`. It cannot construct `Accepted<T>`, an active pin, a trust root, or loader authority.

The package adds no Swift, observer, comparator, media, GPU, Resolve, watch, listen, or creative authority.

These properties do not close the seven P2 source-readiness findings.
