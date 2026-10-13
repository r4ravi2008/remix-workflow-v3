# Rust producer subject adapter A08 peer source review

## Disposition

A08 is rejected for one P1 source defect.

The fixed-document model now stores `Option<StrictJson>`. The unchanged fixture mutation accessor still returns the option container as a JSON value.

That mismatch prevents the library from compiling. A successor must unwrap the optional JSON with an explicit error before any build or control attempt.

I found no additional P1 or P2 source defect in the requested scope.

A08 remains uncompiled and unexecuted. This review establishes no control, native, trust, or acceptance result.

This was a read-only review by a separate author. It is same-model-family and nonblind.

## P1: fixture mutation accessor returns the wrong type

`src/rust_producer_subject_adapter_v3.rs` changes `MeasuredDocument.json` from `StrictJson` to `Option<StrictJson>`.

`src/fixture_controls.rs:178-184` remains unchanged from A07:

```rust
fn document_root<'a>(documents: &'a mut SubjectDocuments, name: &str) -> Result<&'a mut StrictJson> {
    documents
        .values
        .get_mut(name)
        .map(|value| &mut value.json)
        .ok_or_else(|| AdapterError::new("fixture_mutation_document", name))
}
```

The closure returns `&mut Option<StrictJson>`. The function promises `&mut StrictJson`.

Rust has no coercion from the option container to its contained value. This is a compile-time type mismatch.

The correction must call `as_mut()` or otherwise unwrap the option. The `None` branch must return a bounded adapter error.

All twelve fixture mutations target declared JSON documents. Neither non-JSON helper appears in the mutation schedule. Therefore, the repair does not require a placeholder JSON value or a new helper mutation.

## Intended helper split

The remaining helper design is internally coherent at source level.

`NON_JSON_HELPER_KEYS` contains exactly:

- `buildManifestHelper`
- `inputRawBridgeHelper`

`measure_fixed_documents` uses `MeasurementSession::measure_regular` for those two files. It retains each measured row and its exact bytes.

The two frozen helper descriptors remain:

- `prepare_rust_native_manifest_a02.py`: 7,236 bytes, `07f72dcbf64a5f3b5bf96384005f88e189b72bbac1c10f53082800b406ba382c`
- `verify_raw_authority_bridge_a01.py`: 5,295 bytes, `4d24bbe0880863e376338e82f33b2f6ee4486034f385c79b5855aa1304b2679f`

The regular-file measurement path checks the fixed path, size, SHA-256, descriptor identity, pathname identity, and post-read stability. Both helper rows remain in the 2,068-row schedule.

The raw-bridge report still joins its helper descriptor to `inputRawBridgeHelper`. The build manifest helper retains its fixed measured descriptor and emitted row.

The other 18 fixed files still use `measure_json` and the duplicate-key-rejecting parser. `SubjectDocuments::json` returns `subject_document_not_json` for a helper instead of fabricating JSON.

The toolchain projection now obtains its JSON through that checked accessor. I found no other direct access to `MeasuredDocument.json` outside the broken fixture mutation accessor.

## Package and aggregate verification

The reviewed package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-subject-adapter-a08`

The current self-excluding manifest is 42,187 bytes with SHA-256:

`4088075b25f74e74350cd575075ce561b82cbffa3a762a4048b15cebd05d2ec0`

The handoff named `077ac2252f74e74350cd575075ce561b82cbffa3a762a4048b15cebd05d2ec0`. That hash does not match the current file.

I treated this as a handoff bookkeeping discrepancy. The current manifest is internally consistent and is the file reviewed here.

I rehashed every declared file and reconstructed both documented aggregates:

- 14 source rows, 252,080 bytes, `c22732aa25a26f43625f8631140adb3f9861200c85a74e5cc212163b6959e0e0`
- 48 external rows, 1,435,416 bytes, `5b6c1ec749fe75db56efaef77ed88a594a62698348a9441f8b433195deed371a`

Both aggregates match the declared domain, NUL terminator, row and byte prefix, UTF-8 path order, and framed rows.

The package inventory contains the 14 source rows plus the self-excluding manifest. I found no undeclared package file.

The declared A08 attempt directory, publication paths, FIFO root, and vector root were absent. These are pathname observations only.

## Preserved behavior and evidence

Outside the fixed-document split, A08 preserves A07 behavior.

The harness and unchanged contracts retain the 28-case control schedule:

- 12 historical fixture mutations
- 3 scalar-wire controls
- 2 FIFO rejections
- 4 reader controls
- 5 schedule controls
- 1 PNG join control
- 1 compilation-boundary control

The source-owned role schedule remains 2,068 rows. Its family totals and sequence hash are unchanged.

The fixed compile recipe still binds `libc`, `serde`, `serde_json`, and `sha2`. It retains the measured compiler, dependency roots, preflight, repository working directory, and no-Cargo-resolution boundary.

A08 binds the complete A07 failed attempt lineage. The bound files include the predecessor manifest, preflight, report, six logs, parent readback, and actual-evidence peer review.

That evidence truthfully records successful A07 compilation followed by one failed no-argument control invocation. The invocation stopped with `json_parse: trailing characters at line 1 column 3` and published no canonical output.

A08 does not represent the A07 failure as successful control evidence.

## Review boundary

I did not compile, import, assemble, or execute A08 or its controls.

I started no child, native framework, media, GPU, or Resolve process.

This review creates no `Accepted<T>`, trust root, active pin, execution authorization, or product authority.
