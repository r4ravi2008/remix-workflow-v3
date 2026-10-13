# Rust producer runner A17 read-only helper peer review

## Disposition

This is a source-only peer review. I did not import, execute, compile, or control the helper.

The A17 helper has no new P1 or P2 source finding within its narrow adaptation scope. It remains unqualified until the A17 manifest and its external source rows are frozen and reviewed.

## Reviewed identities

- A17 helper: `rust-producer-runner-a17-readonly-root-source-measurement-a01.py`, 14,766 bytes, SHA-256 `71c613758f2ab9937992d45422c41a83e317edc795f25cbc912ea729f2bd9bdd`.
- A16 predecessor: `rust-producer-runner-a16-readonly-root-source-measurement-a01.py`, 14,766 bytes, SHA-256 `433cae78cdb0b09bcbfb75b90bab28f193ec0bdfd83e717e23caf2f3043e48e2`.
- Root source review: `rust-producer-runner-a17-readonly-helper-parent-source-review-a01.md`, 1,472 bytes, SHA-256 `29def15ccf5e2d2dffff66dd8766fb41e7a66bf50d4a4cce123297d4b7b033a3`.

The A16 predecessor receipt exists at `rust-producer-runner-a16-parent-source-readback-a01.json`. It is 720,492 bytes with SHA-256 `434c25d2aee42c7affe94264ede7f3207b3b1dc455617ce442cfc1680378d3af`. Its JSON records 616 inputs and `inputsMatched: true`.

## Structural comparison

The A17 source changes the package, manifest, output, state, aggregate-domain, and predecessor labels. It changes the predecessor receipt pin from A15 to the measured A16 receipt. It changes the inherited count from 578 to 616 and the inherited receipt to 720,492 bytes.

The A17 source has exactly the same 15 top-level function bodies and `BoundFailure` class structure as A16. The two class methods remain unchanged. A constant-normalized AST comparison is identical for both files, with normalized AST hash `2d20725a5206b48eb36035e5db94a2e9373c551f16982244bcf5a6316bcb2b46`.

The A17-to-A16 difference contains no new executable branch. The A17 file retains the same bounded-read, aggregate, import-closure, and publication flow.

## Source behavior and limits

`_read_at` opens only a bounded, regular, canonical path with `O_NOFOLLOW|O_NONBLOCK`. It checks the pre-open path identity, held descriptor identity, and post-read path identity. The identity includes device, inode, mode, link count, owner, group, size, modification time, and change time.

`decode_json` rejects duplicate keys and non-finite constants. `encode_bounded` checks node, depth, string, integer, floating-point, and encoded-byte limits before exclusive proof publication. `save_at` writes only a new regular file, reads it back through the same descriptor, fsyncs the file and parent, and checks the final identities.

The helper reads the A17 manifest and the measured A16 predecessor receipt. It rechecks every current source and external row, recomputes framed source and external aggregates, follows Rust `#[path]` and `include!`-family references, and rechecks the source closure after reading.

The source contains no subprocess, process, socket, compiler, native framework, or project-import API. Its filesystem operations are limited to bounded reads, identity checks, and its own exclusive readback receipt when executed.

The A17 package directory and `source-manifest-a17.json` were not present during this review. Therefore, this review does not establish current A17 row hashes, A17 aggregate values, executable identity, or a helper-authenticated readback. The A16 recipe's separate three missing base-path joins remain an A16/A08 eligibility issue; this helper source review does not repair or waive that issue.

All execution, compiler, control, authorization, native-producer, product-integration, loaded-runtime, watched, heard, and creative flags remain unproven or false for this review.
