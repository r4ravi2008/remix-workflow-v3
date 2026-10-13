# Runner A15 root orchestration A07 source peer review

## Disposition

I independently reviewed the frozen A07 caller, capsule, recipe, rationale,
preparation receipt, A06 to A07 source delta, and the bound A06 failure evidence.
The source-only disposition is accepted for separate gate preparation with zero
P1 and zero P2 findings.

This is a same-model-family, nonblind review. I did not import, evaluate, or
execute the caller or capsule. I did not launch Python, Rust, controls, a
producer, or native/media code.

## Frozen identities

The A07 package root is:

`/Users/aira/projects/remix-gpt-coding-agent/artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a15-root-orchestration-preparation-a07`

The preparation receipt is 21,222 bytes with SHA-256
`f289a85d5d1ab96e4f9f076a08ab36d87ac318d5a4dc6e455205db9dd9efc272`.
Its four source rows total 65,539 bytes and reproduce source aggregate
`e174d6ecaf3c679aa82bd2323d520f38ad529f0631b5295bff737576ab565b4a`.
Its 32 external rows total 19,211,739 bytes and reproduce external aggregate
`4638f0ac4f149bb6f9252622658e5b88d5fe59f07b04fd93c16e9aec3b458f47`.

The four source rows are:

| Role | Bytes | SHA-256 |
| --- | ---: | --- |
| `native_runner_fixed_compile_a15.py` | 44,858 | `e00c409651d6cf2d28b8993e5c3fd999faff3fcc52e37ad0d9ffcdd58894e11f` |
| `orchestration-rationale-a07.md` | 7,166 | `e15405705e93c832e2c81c25f82168932ab91c7b987a92f16da64e59370f87b4` |
| `root_inline_launch_capsule_a07.py` | 11,393 | `d20f8455bb5f5e1a1f1a2359f1a1d9e428f281d73122cbcaeea82f719e5234a1` |
| `root-inline-launch-recipe-a07.json` | 2,122 | `1a3dfa6054c3a3ca960262d9b9a24ce97176906ea2f24bafe94385cdf8621f0a` |

I rehashed every current file behind all four source rows and all 32 external
rows. I found zero missing files and zero byte or digest mismatches. External
roles and external paths are unique. Source and external path sets do not
overlap.

The ROOT held-source readback is 23,654 bytes with SHA-256
`f76b605af28da671c7029377f1a4ae49f2f402d36df82fad9be1e30ef213341c`.
It records four source rows, 32 external rows, 65 selected dependency rows,
stable nine-field identities, absent path and inode aliases, all four fixed
archives, and the preserved A06 failure.

## A06 failure and A07 repair

The bound A06 failure readback is 48,258 bytes with SHA-256
`3984b93ca45528a8977f431956cf084085ff4861a5e39792933e74ad3d7326af`.
The bound failure disposition is 2,302 bytes with SHA-256
`be09ba5e02c805034a3ee0b545049ebd5f12cdb9b2f3ff470b209f4fb1cd26bb`.

A06 entered the authenticated caller and imported the A04 process utility.
It exited with code one before attempt ownership and compiler launch. The
caller PID and process group were reaped and absent. The attempt directory was
absent. The observed envelope reported `caller_value_error` at
`validating_fixed_arguments_and_gate`.

The readback independently found 66 broad suffix matches. One was the prior
subject rlib outside both fixed dependency roots:

`native-preparation-pure-attempt-a05/libnative_preparation_implementation_a04.rlib`

That row is 4,262,496 bytes with SHA-256
`42723d0bc95379d69986bf621accbf62c27d51fff6ca69e4610be8c94b6605bb`.

A07 changes the caller in two bounded groups. It selects dependency rows by
exact direct parent directory and preserves a validated early failure code.
The capsule changes only A07 package paths and operation labels. The four
compiler command builders and their ownership logic remain unchanged.

## Dependency closure

The A07 caller fixes these two dependency roots:

```text
.../rust-build-attempt-a09/target/aarch64-apple-darwin/release/deps
.../rust-build-attempt-a09/target/release/deps
```

The bound preflight is 87,471 bytes with SHA-256
`2b89dcc5dc5472867c17f27ac1474726ba8230f9faa6b3a1ab405eec7eaf64f5`.
Its 138 input rows produce 65 rows whose direct parent is one of those roots.
The selected set contains 48 target rows and 17 host rows: 32 `.rlib`, 32
`.rmeta`, and one `.dylib`.

The caller requires all of the following before creating the attempt directory:

1. The selected count equals the recipe count of 65.
2. Every selected path is canonical and has an allowed suffix.
3. Selected paths are unique.
4. Selected `(device, inode)` pairs are unique.
5. Every selected row equals the complete current source-proof row.
6. The four fixed archive paths are members of that selected set.

I independently compared the 65 selected preflight rows with the A15 source
proof. All 65 paths and complete row dictionaries match. The source proof has
578 current input rows. The 15 A15 source files and 136 A15 external rows also
match their current bytes, hashes, and source-proof rows. Their aggregates are
15 rows, 456,893 bytes, SHA-256
`f1b8f356e761a96229ac8edf4a42fc897b9fecf024de0b43d34c53d0fe85d144`; and 136
rows, 13,024,572 bytes, SHA-256
`4cbaf906deef0af94b89e0e5aad5b759e4547fdbe78b7981baba37737243692b`.

The four fixed target archives are present in the selected closure:

| Crate | Bytes | SHA-256 |
| --- | ---: | --- |
| `libc` | 2,872,080 | `0078e174119b60734a509127110103155e5bc9ca95272166989292b408eb9ac9` |
| `serde` | 951,904 | `cc8867744ada281be49df160a54f1603fee68dd18ad87b9024ae8d2c76b5d216` |
| `serde_json` | 1,983,472 | `2dcbcf2abdcc1dc6591cca11fb5761fbf008353d0e291892bfa4d12468f86515` |
| `sha2` | 178,528 | `c90c44cbb67c2bac69dc3a63712f0383c562613ca851d51cd6d0298e2ca7b708` |

The caller also remeasures the complete source-proof closure before each build
phase. Its current source import walk visits 23 Rust files and reproduces all
27 explicit import edges in the bound source proof. The selected dependency
rows therefore cannot be supplied only by the declared count or by a broad
suffix scan.

## Failure code and launch boundary

The early caller hook accepts an existing `BoundFailure.code` only when it is
a string of one to 96 lowercase letters, digits, or underscores. OSError,
KeyError, value, Unicode, recursion, and other exceptions receive bounded
generic codes. The A06 source-derived predicate remains documented separately
from the code actually emitted by the failed caller.

The capsule requires the measured bundled Python 3.12 executable:

`/Users/aira/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3.12`

The executable is 18,058,560 bytes with SHA-256
`4158f03e1bae2b759f25a1ba1fbdab8bfb7161eba4caf22e28f0915986625bbc`.
The capsule requires isolated mode, optimization level zero, disabled bytecode
writes, the exact original and visible argument vectors, and complete equality
with the seven-variable environment in the recipe. Native, private-control,
source-measurement, result-acceptance, and product-integration roles remain
false or absent.

The caller authenticates the A04 process utility from held measured bytes. It
records each compiler invocation before entering that utility. It treats only
a returned positive PID as observed process execution. A raised invocation
without phase evidence remains uncertain.

## Fixed compile commands and ownership

The recipe and caller agree on exactly these commands, in order:

1. `production_library` to `lib-rust-producer-runner-a15.rlib`.
2. `production_cli` to `rust-producer-runner-a15`.
3. `controls_library` to `lib-rust-producer-runner-a15-controls.rlib`.
4. `controls_cli` to `rust-producer-runner-a15-controls`.

The caller reconstructs each argv vector from the fixed rustc, edition 2024,
arm64 target, fixed archives, two dependency roots, source paths, and attempt
outputs. It compares each reconstructed vector byte-for-byte with the recipe.
It performs the same exact comparison for the fixed environment and output
paths. The current recipe limits library and binary outputs to 64 MiB, build
logs to 1 MiB, and each ordinary compiler phase to 60 seconds.

A04 owns ordinary compiler processes and their bounded phase cleanup. The
retained-control Supervisor remains a separate owner and is not wrapped in
ordinary `run_phase`. The caller keeps source and attempt descriptors through
measurement publication, then attempts descriptor closure before terminal
publication. The terminal record remains nonaccepting and requires external
readback.

## Limits and disposition

The A07 receipt remains `frozen_source_only_root_and_peer_review_pending`.
The compile gate, current source decision, build attempt, generated binaries,
and external acceptance are absent at this review. The A07 source has not been
imported or evaluated.

The runtime byte checks do not attest loaded Python, the standard library,
dyld dependencies, or native frameworks. This review establishes no compiler
success, controls result, producer launch, native output, product integration,
WATCHED, HEARD, or creative acceptance.
