# Runner A16 ROOT orchestration A08 peer review

## Disposition

This was an independent source and evidence review. I did not import or execute
the caller, capsule, utility, compiler, controls, or producer. I did not create
an authorization or a qualification gate.

The A08 caller and capsule contain no new behavioral difference from A07 after
their declared label substitutions. The bound A16 direct recipe has one
package-level eligibility blocker. The recipe cannot pass the caller's own
source-closure validator. A08 remains source-only and unqualified.

## Frozen A08 inputs

The four package rows and their measured identities are:

| role | bytes | SHA-256 |
| --- | ---: | --- |
| `native_runner_fixed_compile_a16.py` | 44,844 | `6d0402ecce0de988cb33d848eaed93ea09cfe9e288818c053e652e106a4557c8` |
| `root_inline_launch_capsule_a08.py` | 11,393 | `4f36122feeb4230dc6b8821d2243ae000e414882613af903cd75861430d8ee6a` |
| `root-inline-launch-recipe-a08.json` | 2,122 | `0c6c580e20d4e1e04be659a5805748216be59c1956876916bbe533a43902c66a` |
| `orchestration-rationale-a08.md` | 7,137 | `b81ae180b35c0bf9e64b88742cd41ed177047ba4932aa98c736ebf9711e353f5` |

The preparation receipt is 36,947 bytes with SHA-256
`4b3c00145b275c32e8d14a0c839791d59e4997fef7d82e04b7f0d5ed2319958f`.
Its state is `frozen_source_only_root_and_peer_review_pending`.

The four source rows total 65,496 bytes. I independently recomputed the
declared source aggregate as
`0d954e901db9141130a1804d3c9ba5ffe55bd9eef35c286447fa35218b481a44`.
The 47 external rows total 45,101,691 bytes. Their recomputed aggregate is
`24f7dcdd87e3a9fcab7da70880f523770b8fa7847ff7d63ddb00c7e01c83523c`.
All 47 current external files matched their recorded byte counts and hashes.

## A07-to-A08 source comparison

I reverse-applied every declared caller substitution to A08. The result is
byte-identical to A07 caller `native_runner_fixed_compile_a15.py`:

- A07: 44,858 bytes, SHA-256 `e00c409651d6cf2d28b8993e5c3fd999faff3fcc52e37ad0d9ffcdd58894e11f`.
- A08: 44,844 bytes, SHA-256 `6d0402ecce0de988cb33d848eaed93ea09cfe9e288818c053e652e106a4557c8`.
- Every declared replacement count matched.
- The twelve function ASTs matched after reversal.
- The three embedded 64-hex hash literals kept the same multiset.

I repeated the comparison for the capsule. Reversal is byte-identical to A07
`root_inline_launch_capsule_a07.py`:

- A07: 11,393 bytes, SHA-256 `d20f8455bb5f5e1a1f1a2359f1a1d9e428f281d73122cbcaeea82f719e5234a1`.
- A08: 11,393 bytes, SHA-256 `4f36122feeb4230dc6b8821d2243ae000e414882613af903cd75861430d8ee6a`.
- The nine function ASTs matched after reversal.
- The two embedded 64-hex hash literals kept the same multiset.

The A08 receipt reports the same normalized-byte and normalized-AST results.
The capsule header still describes the historical A15 orchestration caller.
That text is inherited and has no execution effect; it does not change the
source comparison or the A08 operation identity.

The recipe metadata rename is narrow and measured. A15's
`a15_source_manifest_external_rows` becomes A08's
`a15_external_evidence_rows`. The A16 source manifest and current source proof
both report 159 external rows. The A08 recipe uses the value 159.

## Dependency and source-proof joins

The fixed dependency preflight selects exactly 65 rows. The selected rows have
unique canonical paths and unique device/inode identities. Every selected row
matches one of the 616 current A16 source-proof rows byte-for-byte and by
SHA-256. The two accepted parent roots are:

```text
.../rust-build-attempt-a09/target/aarch64-apple-darwin/release/deps
.../rust-build-attempt-a09/target/release/deps
```

The four required fixed archives are `libc`, `serde`, `serde_json`, and `sha2`.
Each archive is present in the selected 65-row set. The selected suffix counts
are 32 `.rlib`, 32 `.rmeta`, and 1 `.dylib`.

The current A16 source proof is 720,492 bytes with SHA-256
`434c25d2aee42c7affe94264ede7f3207b3b1dc455617ce442cfc1680378d3af`.
It records 616 rows and 163,472,808 input bytes. Its source aggregate is
15 rows, 463,576 bytes, SHA-256
`b4eef131436e37f8461b9e5350abab572eedffcc4e62d388a62fb2b7c51a2a07`.
Its external aggregate is 159 rows, 39,721,126 bytes, SHA-256
`760b5988448e5ec3e204342bf0216fb2ca56a80e9712bc177e14fbcf8345712c`.
All execution, authorization, native, product, loaded-runtime, watched,
heard, and creative flags in that proof are false.

The A08 external closure also rehashed the A16 manifest, recipe, source proof,
helper, helper authentication, ROOT and peer source reviews, current peer
readback addendum, and current acceptance disposition. These rows matched.

## Bound A15 failure evidence

The A08 receipt binds the complete A15/A07 failed compile attempt. Independent
file checks matched the following key records:

- `compile-failure-root-readback-a01.json`: 354,407 bytes, SHA-256
  `5c516da8ee82b4825af52f3be679fbcf58f24ae173cace44a9c08b2b82a49856`.
- `compile-measurements-a01.json`: 716,266 bytes, SHA-256
  `ad691555e69d9cf2bfcd5a1d4f0c9da56cdf54ef9d04c1b9c618e50e0918ebe7`.
- `compile-terminal-closure-a01.json`: 1,248 bytes, SHA-256
  `795946bfbae78a3500ec2a627c8dee9af0aa14321bdf9ebe2a574a7520e735cd`.
- controls-library stderr: 13,844 bytes, SHA-256
  `4796480e8524cbc9700996fabfd12f4bd88df9f55c387589fa17ed09f22363e9`.
- combined ROOT and peer disposition: 1,524 bytes, SHA-256
  `7dcf4ba98af827b953c6e4d11be2037b8c6958e0ffb21b6cff72ef9b060eeebb`.

The failure record has nine controls-library compiler errors. The production
library and production CLI compiled. The controls library failed. The controls
CLI was not invoked. The three observed compiler processes were reaped and
absent with absent process groups. The candidate remained rejected.

## Eligibility blocker: three unbound recipe paths

The A08 caller validates every `*_sha256` entry in `source_closure` at lines
500–508. It derives the base path key, requires that path to exist in the
current source-proof map, then compares the recorded digest.

The A16 direct recipe contains these three digest-only entries:

| recipe key | required source-proof path | bytes | SHA-256 |
| --- | --- | ---: | --- |
| `a15_controls_failure_log_sha256` | `.../rust-producer-runner-a15-build-attempt-a01/2-stderr.log` | 13,844 | `4796480e8524cbc9700996fabfd12f4bd88df9f55c387589fa17ed09f22363e9` |
| `a15_compile_measurements_sha256` | `.../rust-producer-runner-a15-build-attempt-a01/compile-measurements-a01.json` | 716,266 | `ad691555e69d9cf2bfcd5a1d4f0c9da56cdf54ef9d04c1b9c618e50e0918ebe7` |
| `a15_compile_terminal_closure_sha256` | `.../rust-producer-runner-a15-build-attempt-a01/compile-terminal-closure-a01.json` | 1,248 | `795946bfbae78a3500ec2a627c8dee9af0aa14321bdf9ebe2a574a7520e735cd` |

The corresponding base path keys are absent. I independently applied the
caller rule to the current recipe and proof. It found exactly these three
missing paths. The first failure would be
`recipe_source_closure_digest_mismatch:a15_controls_failure_log_sha256`.

The three files are present in the A08 external binding and current A16
source-proof rows. That does not satisfy the caller, because the caller reads
the path from `source_closure` before it consults the external binding list.
Therefore the A16 recipe is ineligible for the A08 fixed-compile operation.
A narrow successor should add the three exact path keys and preserve their
existing byte and digest values. No caller or capsule behavior change is
needed for this repair.

This is a package-binding P1. The A07-to-A08 caller and capsule source delta
has no P1 or P2 behavior finding. The A08 package must remain unqualified until
the recipe closure is repaired and reviewed.

## Scope boundary

The package is source-only. `capsuleExecuted`, `compilerExecuted`,
`controlsExecuted`, `authorizationCreated`, `nativeProducerExecuted`,
`nativeResultAccepted`, and `productIntegrationAllowed` are false. No claim is
made about loaded Python, Rustc, dyld, frameworks, native media, product use,
WATCHED, HEARD, or creative acceptance.
