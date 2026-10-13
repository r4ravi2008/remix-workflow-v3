# Rust producer runner A17 staged authorization reader peer review

## Disposition

This is a source-only peer review. I did not import, execute, compile, or run the reader.

The A17 reader has no new P1 or P2 source finding within its narrow label-adaptation scope. It remains deferred until the A17 manifest, bootstrap, binary, authorization record, and first-attempt inputs are frozen and independently joined.

## Reviewed identities

- A17 reader: `rust-producer-runner-a17-staged-authorization-readonly-root-a01.py`, 19,313 bytes, SHA-256 `e5304c1a5637c625f4580763df00f398bede920f198c3e84f3afed2a50d65ba1`.
- A16 predecessor: `rust-producer-runner-a16-staged-authorization-readonly-root-a01.py`, 19,313 bytes, SHA-256 `7f496910001bf2d8c95e297e424dfe499a13d1c45ddd144ac455e5c9c3d113d5`.
- Root source review: `rust-producer-runner-a17-staged-authorization-readonly-parent-source-review-a01.md`, 1,332 bytes, SHA-256 `14d56afca7a74f80b71180896dea9f63dc1316ab7785116b26a8388d375478fe`.

## Structural comparison

Exactly eight fixed A16 labels advance to A17. They cover the package root, first native-attempt root, bootstrap root, manifest path, bootstrap binary path, bootstrap state, and the corresponding embedded paths.

Reversing those eight substitutions reproduces the complete A16 bytes. The constant-normalized ASTs are identical, with normalized AST hash `cec809afebfaf0a607913f22f07d057ea32aa1f0a16eecbe586bca414f8d7a09`. All seven complete 64-character SHA literals are unchanged.

The A17 reader retains the same 18 top-level function bodies, `BoundFailure` class, two class methods, and `main` control flow as A16. It adds no branch beyond the fixed-label substitutions.

## Source behavior and limits

The reader accepts exactly one authorization path and two 64-character receipt digests. It requires the authorization path to be canonical, regular, and below the fixed path and JSON caps. It rejects pre-existing review, output, cancellation, report, and failure names before reading the authorization record.

It reads the authorization and bootstrap JSON through bounded held descriptors. It checks duplicate JSON keys, non-finite values, exact receipt hashes, the A17 bootstrap object, the fixed A05 producer identity, the seventeen authorization fields, the command, environment, process policy, output policy, cancellation policy, and false acceptance flags.

It holds directory descriptors for the output parent, staged run, and unit root. It checks their device, inode, mode, path identity, entries, and final anchors. It creates only the separate staged readback receipt with exclusive bounded publication. It does not create an authorization review sidecar, launch a process, invoke a compiler, or call a native framework.

The output receipt records `sidecarPublished: false`, `nativeProducerExecuted: false`, `nativeResultAccepted: false`, `productIntegrationAllowed: false`, `loadedRuntimeAttested: false`, `watched: false`, `heard: false`, and `creativeAccepted: false`. These are source-defined disposition fields, not execution evidence.

The A17 package directory, bootstrap, binary, first-attempt directory, and authorization record were not present as a frozen A17 set during this review. The source therefore does not establish an A17 staged authorization, executable identity, or producer result. The existing A05 producer and qualification references remain inherited contract data until fresh A17 bindings are reviewed.

All compiler, control, authorization, native-producer, product, media, watched, heard, and creative acceptance claims remain unproven for this review.
