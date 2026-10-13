# Rust producer pinned qualification A02 source peer review

Disposition: `accepted_no_p1_or_p2` for the bounded source review. The package is ready for its two declared direct compiles.

This is a same-model-family, nonblind review. I did not compile, import, test, invoke, or change the frozen package.

## Frozen receipts

I read all eight A02 package files. I rehashed every A02 source row and direct external row through stable, no-follow file descriptors.

| Set | Rows | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Source manifest | — | 12,090 | `3a5cf1db90f57a53b1988c09b2bb6a8dfde9c8609f5ac3dea07a0f62510c5199` |
| Source aggregate | 8 | 179,143 | `7009ab7ef3546020149560cf92e915f02dd2bfbc14a7afe044c5309629a16f45` |
| Direct external aggregate | 3 | 99,156 | `c3b5cbad895c66631387dc7cb69d324bda371b971020bed63a365c245aca630d` |

Both aggregate digests reproduce under their declared domains, row ordering, and binary framing.

The three-row direct closure is a transitive authority. It binds the exact A01 manifest, parent review, and peer review.

I followed that authority and rehashed all A01 rows. Every row remains current.

| A01 transitive set | Rows | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| A01 source manifest | — | 90,182 | `2cb9d7e25718a458ccf4788962190d66aca7c78a70602f24888bed1f8bf5c460` |
| A01 source aggregate | 8 | 177,441 | `9da21e8b8ed15985808611d5d053f0149a78959fb7b113b22740dffe38e05bc9` |
| A01 external aggregate | 207 | 33,335,081 | `8eccf632114b209be23890338d5d7bf29b30bad4fcf7044c661708443d8d5036` |

The A02 recipe does not use A01's stale build-recipe receipt. Its current closure records three rows and aggregate `c3b5cbad…a630d`.

The A02 recipe separately binds the four expected vectors. All four current files match those receipts.

| Vector | Rows | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Source subject | 2,077 | 539,734 | `16333c79eb18f41a8c2ed95777866be293ebd1ceec06865584ff14e853705bbf` |
| Source final | 2,080 | 540,669 | `c60e7e88aafff3d63bb7110ccf887974c732104a58d23f755000d31d7f3c902f` |
| Runner subject | 63 | 15,579 | `2c0a3b98623c9af3cf1d7a060efc53d3ea0793252b4d98ef90b0488925153fc2` |
| Runner final | 66 | 16,514 | `1f98263dd736b5f30d1906fe15b3a91ef8db6032a0e9f5fc1a02c5732536f77b` |

The runner-subject vector is an explicit recipe leaf outside A01's 207-row external aggregate. A build preflight must measure that leaf directly.

## Narrow source delta

The Rust behavior remains the reviewed A01 behavior.

- `trust_root.rs` is byte-identical to A01.
- `qualification.rs` changes only the package-owned diagnostic output directory.
- `lib.rs` changes only the local `trust_root.rs` path from A01 to A02.
- The harness changes only the crate name from A01 to A02.

The pinned manifest remains schema 1, 2,664 bytes, and SHA-256 `ddd6614afb7879905e3941e18269979728e57d92ffb43df84c49beb41c2f7707`.

Its entries remain exactly `RustProducerSourceV1` followed by `RustProducerRunnerV1`. The trust-root parser, class validation, cycle checks, and private constructor remain unchanged.

## Authority and caller boundary

The no-argument diagnostic reconstructs and qualifies both fixed subjects. Private `full_revalidate` repeats the reconstruction and filesystem evidence reads.

The revalidation compares fresh and retained subject references, final references, final bytes, and value summaries. It also checks the four included vectors.

`OpaqueRustQualification` retains private fields. `Accepted<T>` construction and value extraction remain private to the crate.

Callers cannot supply paths, roles, hashes, commands, dispositions, expected vectors, or the output root. Publication remains an exclusive package-owned diagnostic operation.

## Build sequence and limits

The recipe declares exactly two commands: one library compile and one diagnostic compile. It binds four dependency archives and ten environment entries.

`TMPDIR` belongs to the absent A02 attempt root. The A02 attempt root and diagnostic output root are both absent at review time.

The required sequence remains:

1. complete the root and peer source reviews;
2. run the two direct compiles;
3. create and review an external bootstrap for source, binary, and compiled pin;
4. run one positive diagnostic invocation.

The external bootstrap is absent. The source has not compiled, and the diagnostic has not run.

This review establishes source consistency only. It does not establish a loaded binary, active pin, native execution, media output, product integration, or execution authorization.

It also establishes no `WATCHED`, `HEARD`, or creative acceptance. No cross-family reviewer was available.
