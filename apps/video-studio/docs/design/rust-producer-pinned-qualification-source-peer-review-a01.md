# Rust producer pinned qualification A01 source peer review

Disposition: one P2 blocks the frozen A01 build recipe. I found no P1 and no additional source-code defect in this bounded review.

This is a same-model-family, nonblind source review. I did not compile, import, test, invoke, or change the package. No native child or media process ran.

## P2 — stale external-closure receipt in the build recipe

`direct-build-recipe-a01.json` identifies `source-package-manifest-a01.json` as its current frozen source closure. Its `sourceClosure` block still records:

- `externalBindingCount=205`;
- `externalAggregateSha256=4ce92a37a831a478725a420e4aa2ce1b570eedd4a4f1eb073c8368518ccbff85`.

The frozen manifest contains 207 external rows. Its independently reproduced external aggregate is `8eccf632114b209be23890338d5d7bf29b30bad4fcf7044c661708443d8d5036`.

The mismatch is at `direct-build-recipe-a01.json:214-215`. It reflects an earlier closure before the final data review and root disposition were added.

The compiler commands do not consume these two fields. The defect therefore does not change Rust semantics. It prevents this exact recipe from serving as truthful build-closure evidence.

A successor must remove the stale receipt or bind the exact 207-row external authority. Do not run the two compiles from frozen A01 as a qualifying build.

## Frozen package receipts

I rehashed all eight source rows and all 207 external rows through retained no-follow file descriptors. Every row matches its current byte count and SHA-256.

The reproduced package receipts are:

| Set | Rows | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Source manifest | — | 90,182 | `2cb9d7e25718a458ccf4788962190d66aca7c78a70602f24888bed1f8bf5c460` |
| Source aggregate | 8 | 177,441 | `9da21e8b8ed15985808611d5d053f0149a78959fb7b113b22740dffe38e05bc9` |
| External aggregate | 207 | 33,335,081 | `8eccf632114b209be23890338d5d7bf29b30bad4fcf7044c661708443d8d5036` |

Both aggregate digests reproduce under their declared domains and row framing. The frozen A06 predecessor manifest and aggregate receipts also match their bound rows.

## Source delta

The local `qualification.rs` differs from frozen qualification A06 by 186 inserted lines. Existing reconstruction, evidence parsing, runner validation, and private revalidation code remain byte-identical.

The additions are limited to:

- fixed trust-data and output paths;
- four included RoleIndex vectors and their row and byte constants;
- the no-argument `run_pinned_positive_diagnostic` seam;
- final-vector checks and diagnostic publication helpers.

The local `trust_root.rs` differs from trust-root A02 only at the production pin. It replaces the absent pin with schema 1, byte count 2,664, and SHA-256 `ddd6614afb7879905e3941e18269979728e57d92ffb43df84c49beb41c2f7707`. Its `include_bytes!` path resolves to that exact manifest.

The local `lib.rs` changes only the trust-root module path and two public diagnostic reexports. The no-argument harness calls only `run_pinned_positive_diagnostic`.

## Trust and reconstruction boundary

The compiled manifest bytes contain exactly `RustProducerSourceV1` followed by `RustProducerRunnerV1`. The trust loader retains the reviewed strict parser, two-entry order, noncycle checks, and five-class acceptance validation.

The four fixed vectors match current files:

| Vector | Rows | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Source subject | 2,077 | 539,734 | `16333c79eb18f41a8c2ed95777866be293ebd1ceec06865584ff14e853705bbf` |
| Source final | 2,080 | 540,669 | `c60e7e88aafff3d63bb7110ccf887974c732104a58d23f755000d31d7f3c902f` |
| Runner subject | 63 | 15,579 | `2c0a3b98623c9af3cf1d7a060efc53d3ea0793252b4d98ef90b0488925153fc2` |
| Runner final | 66 | 16,514 | `1f98263dd736b5f30d1906fe15b3a91ef8db6032a0e9f5fc1a02c5732536f77b` |

The source manifest binds all fifteen current acceptance and review files. Initial loading reconstructs and qualifies both subjects. Private `full_revalidate` repeats reconstruction and filesystem evidence reads. It compares fresh and retained subject references, final references, final bytes, and value summaries.

The positive diagnostic checks all four references against included vectors. It also compares both accepted final byte buffers byte-for-byte. Publication uses a package-owned exclusive directory and create-new files.

The public positive seam has no arguments. Callers cannot supply a path, role, hash, expected vector, command, disposition, or output root. `OpaqueRustQualification` fields remain private. The `Accepted<T>` construction path and value extraction remain inaccessible outside the private crate boundary.

The public A06 control function remains compiled for historical source compatibility. The positive diagnostic does not call it. The build recipe has no control command.

## Planned build sequence and limits

The recipe defines exactly two commands: one library compile and one diagnostic compile. It binds the measured compiler, four dependency archives, fixed target, and ten environment entries. `TMPDIR` is inside the exclusive A01 attempt root.

The attempt root and diagnostic output root are currently absent. The declared sequence is:

1. complete root and peer source reviews;
2. run the two direct compiles;
3. create and review an external bootstrap that binds source, exact binary, and compiled pin;
4. run one positive diagnostic invocation.

The external bootstrap does not exist yet. The source has not compiled. The positive path has not executed. The final output files and runtime evidence therefore remain unverified.

This package establishes no execution authorization, native producer result, media result, product integration, loaded-image attestation, `WATCHED`, `HEARD`, or creative acceptance. No cross-family reviewer was available.
