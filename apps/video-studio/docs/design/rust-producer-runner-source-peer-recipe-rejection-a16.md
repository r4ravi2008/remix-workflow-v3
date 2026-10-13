# Runner A16 recipe closure rejection

This is an additive source-only peer finding. I did not import or execute any
caller, capsule, utility, compiler, controls, or producer.

The reviewed A16 direct recipe is
`rust-producer-runner-a16/direct-build-recipe-a16.json`, 35,773 bytes, SHA-256
`39b54ddceb0e56635b011cbaaca4f36f5ae094d29f1995648eca2af311eebbc1`.
The A08 caller is 44,844 bytes, SHA-256
`6d0402ecce0de988cb33d848eaed93ea09cfe9e288818c053e652e106a4557c8`.
The bound current A16 source proof is 720,492 bytes, SHA-256
`434c25d2aee42c7affe94264ede7f3207b3b1dc455617ce442cfc1680378d3af`.

The caller's source-closure loop derives a path key for every `*_sha256` key.
It requires that path to be a current source-proof row. The recipe has three
digest-only entries with no corresponding base path:

| digest key | current proof file | bytes | digest |
| --- | --- | ---: | --- |
| `a15_controls_failure_log_sha256` | `rust-producer-runner-a15-build-attempt-a01/2-stderr.log` | 13,844 | `4796480e8524cbc9700996fabfd12f4bd88df9f55c387589fa17ed09f22363e9` |
| `a15_compile_measurements_sha256` | `rust-producer-runner-a15-build-attempt-a01/compile-measurements-a01.json` | 716,266 | `ad691555e69d9cf2bfcd5a1d4f0c9da56cdf54ef9d04c1b9c618e50e0918ebe7` |
| `a15_compile_terminal_closure_sha256` | `rust-producer-runner-a15-build-attempt-a01/compile-terminal-closure-a01.json` | 1,248 | `795946bfbae78a3500ec2a627c8dee9af0aa14321bdf9ebe2a574a7520e735cd` |

Static application of the exact caller rule found these three missing base
paths and no others. The first runtime rejection would be
`recipe_source_closure_digest_mismatch:a15_controls_failure_log_sha256`.
The files already exist in the external binding and source-proof closure, so
the repair is a recipe-only binding addition. Add the three exact path keys,
then rebind the A08 recipe receipt and aggregate. Keep A08 source and capsule
bytes unchanged.

The separate metadata rename is correct: `a15_source_manifest_external_rows`
is historical A15 metadata, while `a15_external_evidence_rows` is the current
A16 value 159. It does not repair the three missing path keys.

Disposition: P1 package eligibility failure. The A08 source and capsule label
advance remains byte- and AST-equivalent to A07 after reversal. A16 compilation,
controls, native production, and product integration remain unexecuted and
unqualified.
