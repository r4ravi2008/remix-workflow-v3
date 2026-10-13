# Payload A09 peer source review

## Disposition

The minimal A09 source repair has no remaining P1 or P2 finding.
It is ready for a fresh isolated compile attempt.

This verdict covers source readiness only.
It does not establish compilation, typechecking, formatting, tests, execution, measurement, or native behavior.

I did not run a helper, parser, Cargo command, compiler, test, binary, native framework, GPU process, or Resolve process.
This was a same-model-family peer review.

## Compile-error repairs

### `BuildIdentity` ownership

`BuildIdentity` is defined in `identity.rs` and re-exported from the crate root.
A09 imports that re-export through `crate::BuildIdentity`.

The invalid A08 `crate::model::BuildIdentity` import is gone.
The repair matches the existing public ownership boundary.

### Retained UUID capacity

`BuildIdentity::executable_uuid` is `Option<String>`.
A09 calls `as_ref()` before matching the value.

The matched value is therefore `&String`.
Its `capacity()` is the owned allocation capacity required by the logical ledger.

The repair does not substitute string length for capacity.
It does not clone or allocate another UUID string.

### Private layer layout forwarding

`layers.rs` is a private child module of `movie.rs`.
The new forwarding function remains feature-gated and `pub(crate)`.

`movie.rs` can call its private child directly.
`payload_measure.rs` can call the existing crate-visible `movie` seam.

The returned layout rows remain unchanged.
Their order remains layer rows, movie rows, then PCM rows.
The existing name deduplication remains after all three extensions.

This repair does not expose the private layers module or its native worker seams.

### Pure-control label

The temporary directory label advances from A08 to A09.
No test behavior, cap, output rule, or acceptance rule changes.

## Copy and authority checks

The A08-to-A09 package comparison changes exactly two Rust files:

- `package/crates/editor/src/payload_measure.rs`;
- `package/crates/editor/src/movie.rs`.

The semantic patch matches those file differences.
It includes all three compile repairs and the temporary-directory label change.

The deferred runner differs from A08 only in its source-only generation sentence.
Its verification logic is unchanged.

The contracts preserve schema 1, output caps, partial-output evidence, and allocation scope.
They keep loaded-vnode, RSS, native-memory, media, and product claims excluded.

The source manifest records 58 package rows and six runner rows.
The parent fixture record binds those 64 rows.
It records eleven Rust and eleven deferred-runner fixture authorities.

The manifest, stage, semantic patch, and parent record hashes match the supplied identities.
The future A10 preparation paths were absent during this review.

## Required next gate

A fresh external compile must use the A09 manifest and copied package.
The failed A08 compile remains historical evidence only.

The future build preparation must also retain the accepted helper repairs:

- build the libtest harness inside its control-owned target directory;
- verify the harness path identity after the direct test;
- verify the Python interpreter path identity after the measurement runner.

Those helper conditions come from the preserved A09 preparation review.
This source repair does not itself satisfy them.

No control or measurement should start before a successful compile is separately reviewed.

## Exact reviewed identities

| File | SHA-256 |
| --- | --- |
| `source-copy-manifest-a09.json` | `a86bda9e74c7d9ce10406e95d6e225d56ab36d086e75b7e97dcc6923fd799d59` |
| `source-stage-a09.json` | `113f52b2e683680960cdf78a640e43d684ecb356934a65f7f51d53df68036ecb` |
| `semantic-delta-a09.patch` | `0c21fd2f0f429161efce2d25736aa83714d073a77cfba707f185673cc8e8c3ac` |
| `payload-parent-fixture-verification-a09.json` | `fc60214d8aead8cd4bade7bebc8a0e16b7078bcd41bd3c9a82fa7a57e8c2beac` |
| `package/crates/editor/src/payload_measure.rs` | `2a0e1d4846fb4eaa1b4a93eb2bac414879d74f9eea93e4c4247750609373ca6a` |
| `package/crates/editor/src/movie.rs` | `8e738cb89f0dbc76dbd10e039ba66f59f919a5a39405bc2ddb20ae269135010c` |
| `verify_payload_closure_a09.py` | `175244895a76e18a8f84b36350f375b6b612837f85cd0d48c2819cd62723c3e3` |
| `source-rationale-a09.md` | `f5016a408dc57db82372871e71408640d3a9fe3f2a467ee796d152f6af878b9b` |
| `output-schema-a09.md` | `54b23d0e8f30e78fdc7877922bc0e3148e03566d567d360f9eb910e5cbbf0d9a` |
| `allocation-ledger-a09.md` | `9a5918e87bc9d2a69d53783690e25c32640713cce14e829e5006c24095911877` |
