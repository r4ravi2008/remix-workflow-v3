# Runner A15 compile orchestration A05 peer source review

## Disposition

**Rejected before capsule launch.** I found zero P1, one P2, and zero P3
findings in the frozen A05 wrapper package.

The fixed `/usr/bin/python3` contract cannot pass its own checks on this macOS
host. The capsule therefore cannot reach the authenticated compile caller.

This review is source-only, same-model-family, and nonblind. I read the complete
caller, capsule, rationale, launch recipe, and preparation receipt. I checked
the accepted A04 process-utility reviews and the fixed A15 source receipts.
I read the ROOT A05 review after completing my initial source assessment. A
later ROOT host diagnostic exposed the P2 below. I assessed its effect against
the frozen capsule and recipe.

I did not import or evaluate candidate source. I did not run the capsule,
caller, shared utility, compiler, controls, bootstrap, producer, or native code.

## P2 finding

### P2.1: The fixed Apple Python shim cannot satisfy the capsule contract

`root_inline_launch_capsule_a05.py:172-175` requires:

```text
sys.executable == /usr/bin/python3
sys.orig_argv[:4] == [/usr/bin/python3, -I, -B, -c]
```

`root-inline-launch-recipe-a05.json:4-14` fixes the same interpreter path and
argument prefix. The recipe also requires exactly six environment variables at
lines 16-22. The capsule compares the complete process environment at
`root_inline_launch_capsule_a05.py:210-211`.

On this host, `/usr/bin/python3` is an Apple launcher shim. ROOT's read-only
host diagnostic observed Python 3.9.6 with this executable value:

```text
/Library/Developer/CommandLineTools/usr/bin/python3
```

That runtime has no `sys.orig_argv`. The shim also adds `CPATH`,
`LIBRARY_PATH`, `MANPATH`, `SDKROOT`, and `__CF_USER_TEXT_ENCODING` to the
six-variable launch environment.

The capsule fails at the executable check before it can authenticate the
recipe or caller. Even without that check, the missing `sys.orig_argv` and
expanded environment would fail later checks. A valid ROOT gate cannot make
this frozen launch path reach the compiler caller.

The available canonical Python 3.12.14 executable is:

```text
/Users/aira/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3.12
```

I rehashed that 18,058,560-byte regular file as
`4158f03e1bae2b759f25a1ba1fbdab8bfb7161eba4caf22e28f0915986625bbc`.
ROOT observed that its `sys.executable` and `sys.orig_argv[0]` both retain this
canonical path. Core Foundation still adds
`__CF_USER_TEXT_ENCODING=0x1F5:0x0:0x0`.

A successor must bind that exact interpreter receipt and canonical path. Its
closed environment must include the observed Core Foundation variable. The
capsule, launch recipe, preparation receipt, and external launcher contract
must agree on the successor values.

This is P2 because the defect blocks the sole allowed operation. It does not
alter the four compile commands or the accepted A04 process-owner logic.

## Remaining held-byte and operation checks

Apart from P2.1, the capsule requires the exact measured capsule text. It
checks `sys.orig_argv`, visible `sys.argv`, and the complete environment.

The capsule reads the launch recipe and selected caller through canonical,
nonblocking, no-follow descriptors. It checks their byte counts, SHA-256
values, full identities, stable pathnames, and end-of-file boundaries.

The launch recipe exposes one caller role: `fixed-compile`. The caller accepts
exactly five digest arguments. The future gate permits only
`fixed_four_compiles`. Native producer, native result, and product integration
permissions remain false.

The caller separately authenticates the accepted 46,572-byte A04 utility before
evaluating its held bytes. The utility receipt is
`b903a9aff1cc2d8dae73b16800f177322b000b2983e5a45206a639326727d47d`.
That evaluation supplies bounded measurement, publication, and process-owner
functions. It does not create operation authority.

## Source and recipe closure

Before creating the compile attempt, the caller requires exact receipts for:

1. The A15 manifest and direct recipe.
2. Both accepted A15 source reviews.
3. The current source decision and canonical source readback.
4. The read-only helper and authenticated helper-launch receipt.
5. The A05 caller, capsule, rationale, receipt, and launch recipe.
6. Both A05 orchestration reviews and the accepted A04 utility.

The current decision must name the same manifest, source proof, reviews, and
aggregates. It must preserve the historical pending state. Its only allowed
operation is `fixed_four_compiles`.

The caller recomputes both A15 framed aggregates. It checks every manifest row,
recipe closure byte count and digest, literal Rust import, fixed archive, and
toolchain receipt against the canonical proof.

The caller rebuilds the four command vectors rather than trusting recipe text.
It then requires byte-for-byte equality with the recipe vectors.

| Order | Command | Scope | Output |
| ---: | --- | --- | --- |
| 1 | `production_library` | production | `lib-rust-producer-runner-a15.rlib` |
| 2 | `production_cli` | production | `rust-producer-runner-a15` |
| 3 | `controls_library` | private source controls | `lib-rust-producer-runner-a15-controls.rlib` |
| 4 | `controls_cli` | private source controls | `rust-producer-runner-a15-controls` |

All commands use the fixed arm64 compiler, edition 2024, `panic=abort`, thin
LTO, four fixed archives, and two fixed dependency search roots. The caller
uses the fixed source directory and a fresh attempt-local `TMPDIR`.

The wrapper never invokes either generated binary. No private-control caller
or source-measurement role exists in the capsule.

## Ownership and failure truth

The caller creates one absent fixed attempt directory with mode `0700`. It
holds the attempt and source directory descriptors during preflight, all four
phases, measurement publication, and final anchor checks.

The accepted A04 utility owns each compiler process, private process group,
held executable and cwd descriptors, streams, logs, and phase-attempt
descriptor. A phase result cannot report closure until the direct child and
owned group are absent and all retained authorities are closed.

The caller records an invocation attempt before entering `run_phase`. Only a
returned positive PID establishes observed compiler process execution. A
raised or unusable phase result records uncertainty. Earlier positive PID
evidence remains observed if a later invocation becomes uncertain.

The caller measures every input before and after each phase. It preserves the
returned bounded phase facts, bounded logs, generated-file receipts, Mach-O UUIDs,
process absence checks, and attempt inventory in a nonterminal report.

The caller publishes that report through the held attempt descriptor. It then
attempts both caller descriptor closes. Only after both attempts does it create
the exclusive terminal record. The terminal record preserves each close result
and requires external readback. It never accepts the candidate itself.

The failure hook follows the same order after descriptor ownership begins. It
records attempted invocations, positive PID evidence, uncertainty, completed
phase facts, bounded inventory, and false native and product claims. A
pre-attempt failure emits only a bounded stderr envelope.

The ordinary phase deadline is 60 seconds with 1 MiB stdout and stderr caps.
The accepted utility retains an unresolved process owner beyond that ordinary
deadline. Forced host or interpreter termination remains outside its
in-process guarantee.

## Frozen source receipt

I rehashed all four aggregate source rows, the excluded preparation receipt,
and all sixteen external bindings. Every byte count and SHA-256 value matches.
I reproduced both declared framed aggregates. I parsed both Python files as
source without importing or evaluating them.

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| `native_runner_fixed_compile_a15.py` | 40,067 | `c211d3134005cd5d45327a16b31c0635b98b07be4605376a6716112e69500f7a` |
| `root_inline_launch_capsule_a05.py` | 10,120 | `7d6c00317f1e2665d840b10384f177746989f27090b134dfd393c08fb0480d53` |
| `orchestration-rationale-a05.md` | 4,721 | `16ee87be20f5bfc1ecb4fc7e394ebbfc756120c7d1f4e77508f5fb2eedc3357c` |
| `root-inline-launch-recipe-a05.json` | 1,484 | `b758e08372d276e996f1b22e791fec8083dacebdae2d72dc2cead84cbc60db38` |
| `preparation-receipt-a05.json` | 13,690 | `2f89417f1a7d798396d717ad2460b9f5e1c77f1953f33b833e54d8c429689a77` |
| four-row source aggregate | 56,392 | `8977a8fbce42a7a4c6203325e582ffa5ab809ff0ffd3a6b8c30b89d686f48c55` |
| sixteen-row external aggregate | 968,531 | `b2345ecb544b1df8c60e394cc61bbdbdf93f29c7879da6d37aa311b720991cb6` |
| ROOT held-source readback | 20,431 | `712e773d97c1c10a980bb79a3fd658380b7ae88c24ca8e88c8858a10fd080acc` |
| ROOT A05 source review before host diagnostic | 3,616 | `6eb26449a2c3cd602149e4cfcd3b76f648c90c6dfab91791480e064c8734c64e` |

The external aggregate byte total is the sum of its sixteen fixed rows. It does
not include the preparation receipt or future review and gate files.

The frozen A05 launcher is rejected before execution. No compiler result,
control result, bootstrap, authorization, native output, product integration,
WATCHED result, HEARD result, or creative acceptance is established.
