# Rust producer subject adapter A03 parent source review

A03 remains preserved, uncompiled, and unexecuted. Root rejects source readiness with one P1 and four P2 groups.

Root read all package documents, the complete A02-to-A03 source delta, vector controls, and the fixed diagnostic harness. All fourteen source rows (225,998 bytes), twenty-two external rows (353,907 bytes), and twenty fixed authority documents match their individual identities. The saved adapter, measurement session, and fixture are byte-identical to A02. The new full schedule checks 2,068 static role/tag rows after final sorting and before encoding. Scalar and FIFO summaries no longer claim an unchecked baseline. These close the original three source gaps except for the new control-coverage defect below.

## P1: Missing return-reference lifetime

`diagnostic_controls.rs` declares `fn validation_code(result: Result<()>) -> &str` without a borrowed input lifetime. `AdapterError.code` is a static string. The return type must name `&'static str`. The current signature cannot satisfy lifetime elision and should fail E0106. This is a static source finding, not a compiler result.

## P2: Aggregate identities do not reproduce

Applying the manifest's NUL-terminated domain, u32be row count, u64be total bytes, ascending UTF-8 paths, and declared row encoding yields source SHA-256 `533983b33bfbf13c8e6d8ac6d5ca6fc03345c05efeaf8832668528201227719e`, rather than `eaf8d1141b5fbd0b76fc26e8715fe0792029f3dbf6a442e4ed5d051bc14aa32f`. External SHA-256 is `f33bd24e613e4d0ce31caab335af0942f0ef42e9ee79cc2f22756ec8057e849c`, rather than `8495d21bb4bfd9153081bb9c823c54a5775b013e9a397d7814aaf6e2e5282d61`. Every individual file row matches. Fix the aggregate recipe or digests in an additive successor.

## P2: Reader seam is disconnected from the actual reader

Growth and replacement controls call `vector_controls::validate_reader_seam`, which uses caller-created booleans. `MeasurementSession` never calls that helper. These controls therefore test a duplicate predicate, not the actual post-read reader checks. Share the real post-read count/identity/hash validator and use genuine-shaped identity facts in finite controls. Concurrent filesystem-race proof remains outside that seam scope.

## P2: Harness does not enforce all success fields

The PNG control can return `Ok` with `passed=false`. The harness neither checks that flag nor validates the full expected result counts before writing its vector and exiting 0. It also ignores caller arguments despite claiming a no-argument entry point. Reject arguments before reads and require all returned pass fields and exact fixed totals.

## P2: Build recipe cannot reproduce the fixed environment

The documented command uses `rustc` through PATH, omits existing target/host dependency search roots, and omits the required abort/thin-LTO settings for existing archives. Its rlib filename lacks the lib prefix. Bind the actual observed absolute compiler, dependency preflight, fixed archives, and exact owned attempt outputs. Do not resolve new dependencies or add a launcher.

The actual scalar bytes are now returned and printed for independent readback. The old 79-row fixture remains separate evidence. Peer source review is pending. Additive A04 repairs these five concrete groups. No accepted value, pin, loader authority, native process, media, GPU, Resolve, WATCHED, HEARD, or creative acceptance exists.
