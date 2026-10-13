# Rust producer subject adapter A06 peer source review

## Disposition

A06 closes the A05 compiler-input defect at source level.

I found no P1 source defect. I found one P2 manifest claim defect.

The fixed library command binds every direct external crate used by the complete inherited source closure. Those crates are `libc`, `serde`, `serde_json`, and `sha2`.

A06 remains uncompiled and unexecuted. This review does not establish build success, control success, native execution, or acceptance.

This was a read-only review by a separate author. It is same-model-family and nonblind.

## P2: `fixedInputs` omits two bound direct archives

`source-manifest-a06.json:660` names the bound `libc` and `sha2` archives. It omits the also-bound `serde` and `serde_json` archives.

The library command at lines 618–625 correctly binds `serde`, `serde_json`, `sha2`, and `libc`. The `compileAuthority.archives` array also binds all four exact archives.

`README.md:84-89` and `subject-contract-a06.md:100-102` correctly describe all four direct archives.

The stale `fixedInputs` sentence contradicts those authoritative fields. A narrow successor should name all four archives in that sentence.

This defect does not change compiler arguments or production semantics. It must be corrected before the manifest is treated as a self-consistent build recipe.

## Frozen package and aggregate verification

The reviewed package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-subject-adapter-a06`

The self-excluding manifest is 36,467 bytes with SHA-256:

`7fba1918331d5f3ad8c804ef9e0c5c680ee81006c72df631f6265b2114207480`

All 14 source rows match their declared 249,358 bytes and hashes.

All 31 external rows match their declared 729,758 bytes and hashes.

Both aggregates reproduce from the documented domain, row-count, byte-count, and row encoding:

- source: `89e67bdee20ea8aa59391e78a5ccfcdfd904adc994fb036f24ea01f444ebf8b2`
- external: `5ec275af1d05210e44a4a7467235a57135ee26ad4376565bbbbc2508cb0e1a45`

The package inventory exactly matches the 14 self-excluding source rows.

The A06 attempt directory and both declared `/private/tmp` outputs are absent. These are pathname observations only.

## Direct dependency repair

The A05 preserved build failed because `serde` and `serde_json` were not passed to `rustc`.

I followed every local and `#[path]` module imported by `src/lib.rs`. The complete source closure has these direct external uses:

- `serde` and `serde_json` in the inherited strict JSON parser and fixture mutation control
- `sha2` in report, subject, vector, and artifact observations
- `libc` in descriptor, FIFO, vector, and subject observations

I found no fifth direct external crate import.

The A06 library command supplies all four `--extern` arguments. Its two dependency roots retain transitive archive discovery.

The four archive files match the manifest byte counts and SHA-256 values:

- `libc`: 2,872,080 bytes, `0078e174119b60734a509127110103155e5bc9ca95272166989292b408eb9ac9`
- `serde`: 951,904 bytes, `cc8867744ada281be49df160a54f1603fee68dd18ad87b9024ae8d2c76b5d216`
- `serde_json`: 1,983,472 bytes, `2dcbcf2abdcc1dc6591cca11fb5761fbf008353d0e291892bfa4d12468f86515`
- `sha2`: 178,528 bytes, `c90c44cbb67c2bac69dc3a63712f0383c562613ca851d51cd6d0298e2ca7b708`

The compiler, dependency closure, and preflight files also match their declared bytes and hashes.

The compiler working directory remains the repository root. Every relative source, dependency, and archive path resolves from that directory.

## Successor and semantic comparison

The fixture and these production modules are byte-identical to A05:

- `src/diagnostic_controls.rs`
- `src/fixture_controls.rs`
- `src/rust_producer_subject_adapter_v3.rs`
- `src/subject_observation.rs`

The FIFO and vector modules change only their disposable A06 paths. `src/lib.rs` and `src/saved_report_adapters_v1.rs` change only comments.

The A06 harness is byte-identical to A05 after exact A05-to-A06 label substitution. Both control contracts have the same property.

The 28-case control schedule, expected codes, resource counts, format-brace repair, canonical report, reconstruction checks, and publication order remain unchanged.

The manifest preserves the A05 failed attempt and its exact stderr. It also binds the A05 predecessor and prior reviews as external lineage.

I found no production candidate, RoleIndex, measurement, control, or publication semantic change.

## Review boundary

I did not compile, import, assemble, or execute the library, harness, or controls.

I started no child, native, media, GPU, or Resolve process.

This review creates no `Accepted<T>`, trust root, active pin, execution authorization, or native evidence.
