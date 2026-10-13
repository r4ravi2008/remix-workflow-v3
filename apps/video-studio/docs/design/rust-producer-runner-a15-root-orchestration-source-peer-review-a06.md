# Runner A15 compile orchestration A06 peer source review

## Disposition

**Accepted for source-only gate preparation.** I found zero P1, zero P2, and
one P3 provenance note in the corrected A06 freeze.

A06 closes A05's host-entry blocker. The capsule can target the measured
bundled Python 3.12 path without relying on Apple's `/usr/bin/python3` shim.

This review is same-model-family and nonblind. I reviewed the complete A05 to
A06 caller and capsule deltas. I also read the complete A06 rationale, launch
recipe, preparation receipt, ROOT review, and current ROOT rejoin proof.

I did not import or evaluate package source. I did not run the capsule, caller,
shared utility, compiler, controls, bootstrap, producer, or native code.

## P3 provenance note

### P3.1: The first A06 handoff was not continuously immutable

After the first handoff, the author reran a combined generator. It rewrote the
A06 launch recipe and preparation receipt with byte-identical content.

The two files retained their byte counts and SHA-256 values. Their mtime and
ctime values changed. The first-handoff freeze therefore lacked continuous
identity preservation.

ROOT had not measured A06 before this rewrite. No earlier ROOT proof or gate
was silently replaced. The incident does not change source behavior or any
declared byte receipt.

ROOT subsequently reopened the corrected freeze through held descriptors.
The current rejoin proof is 20,744 bytes with SHA-256
`2ac34a9c89bb697ccb5f1e2692861f5ac9a0d0eff4d58680a632407e47041aee`.
It records 31 current inputs and stable nine-field identities.

The ROOT A06 review binds that proof and discloses the rewrite. It is 3,585
bytes with SHA-256
`ac3254b41ec0cc18ce9ccedc63570d387b1d1cd5862fc15a28c690ae808318fc`.

This is P3 because the current bytes and authority joins remain valid. A future
gate must bind the current ROOT review and this peer review. ROOT must also
remeasure the launch inputs before starting Python.

## Canonical Python host entry

The A06 recipe, capsule, caller, preparation receipt, and diagnostic use one
canonical executable path:

```text
/Users/aira/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3.12
```

I reopened that regular Mach-O file. It is 18,058,560 bytes with SHA-256
`4158f03e1bae2b759f25a1ba1fbdab8bfb7161eba4caf22e28f0915986625bbc`.
The path is not a symlink.

The capsule reads the executable with a 32 MiB cap. It checks the fixed byte
count and digest before entering the caller. The caller repeats that check.

The caller keeps the runtime receipt in its before-and-after input closure.
Its exact-size remeasurement applies before and after each compiler phase.

The saved host diagnostic is 4,265 bytes with SHA-256
`ed830612259dadca1fd930ef3ad60ad6987321aa7b0d5af24e040ae54e343e67`.
Its before and after runtime identities equal the current runtime identity.

The diagnostic records Python 3.12.14, isolated mode, optimization level zero,
and disabled bytecode writes. It records the exact executable and original
argument prefix.

The diagnostic also records a zero exit, reaped process, and absent process
group. Project code, process utility code, and the launch capsule remained
unloaded during that diagnostic.

Loaded-runtime identity remains explicitly unattested. The checks bind current
path bytes and observations. They do not prove the loaded image or dyld closure.

## Environment and argument vectors

The recipe defines exactly seven environment variables:

```text
HOME=/Users/aira
LANG=C
LC_ALL=C
PATH=/usr/bin:/bin:/usr/sbin:/sbin
TMPDIR=/private/tmp
TZ=UTC
__CF_USER_TEXT_ENCODING=0x1F5:0x0:0x0
```

The host diagnostic observed the same seven-variable environment. The capsule
requires complete dictionary equality, so extra or missing variables fail.

The capsule requires this original argument prefix:

```text
python3.12 -I -B -c <exact-capsule-source>
```

It reconstructs and compares the complete `sys.orig_argv` vector. It separately
compares the complete visible `sys.argv` vector.

The recipe exposes one role, `fixed-compile`. That role accepts exactly five
digest arguments. The capsule authenticates the selected caller bytes before
evaluating them.

## Gate and input closure

The future gate has distinct `pythonRuntime` and `pythonRuntimeDiagnostic`
receipts. The caller requires both receipts before it can own an attempt.

The caller parses the exact diagnostic bytes. It joins the runtime identity,
executable path, original argv entry, flags, environment, and false
loaded-runtime claim.

The gate still permits one operation: `fixed_four_compiles`. Native producer,
native result, and product integration permissions remain false.

The caller adds the runtime and diagnostic to its measured input closure. It
uses a 32 MiB cap only for the runtime. Other new orchestration inputs retain
the 1 MiB admission cap.

The exact-size `remeasure_input` helper preserves zero-byte support. It uses a
positive one-byte cap for an empty file. It does not relax the utility's global
512 MiB ceiling.

## Preserved A05 boundaries

I compared the full caller and capsule deltas against frozen A05. A06 changes
the host entry, successor labels, receipts, and runtime remeasurement only.

The four Rust command constructors are unchanged:

| Order | Command | Scope |
| ---: | --- | --- |
| 1 | `production_library` | production |
| 2 | `production_cli` | production |
| 3 | `controls_library` | private source controls |
| 4 | `controls_cli` | private source controls |

Each command retains edition 2024, `panic=abort`, thin LTO, fixed archives,
fixed dependency roots, fixed output paths, and the fixed source directory.

The accepted A04 process utility remains 46,572 bytes with SHA-256
`b903a9aff1cc2d8dae73b16800f177322b000b2983e5a45206a639326727d47d`.
The caller evaluates only its exact held bytes after authentication.

Each compiler invocation remains recorded before the utility call. Only a
returned positive PID proves observed compiler execution. Missing or unusable
phase evidence remains unknown.

The caller retains source and attempt directory descriptors through all four
phases and nonterminal publication. It attempts both closes before terminal
publication.

The failure path preserves invocation facts, returned phase facts, bounded
inventory, and descriptor-close results. It does not promote partial evidence.

Generated binaries remain unexecuted. Private retained controls, bootstrap,
authorization, and native production remain separate later operations.

## Current receipts

I rehashed all four source rows, the excluded preparation receipt, all 26
external rows, the Python runtime, and the host diagnostic. Every current byte
count and SHA-256 value matches.

I independently reproduced both framed aggregates.

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| `native_runner_fixed_compile_a15.py` | 43,136 | `d2dff9b12615a3fe5e6d158727ea06fd38445e22877f4bee3ca8ca15d27c553d` |
| `root_inline_launch_capsule_a06.py` | 11,393 | `3f35810353f0310b0e30cc90e1719445f025bb99a7b54aabe824aaf4c4f8afe6` |
| `orchestration-rationale-a06.md` | 5,605 | `105ec47265d65157c6156bf8040eb30e700cb8f640d66b24d847dde0866f833a` |
| `root-inline-launch-recipe-a06.json` | 2,122 | `16397d484d751322631bb0da86c0dae0de7fa4a9bc0d8b3419373bd9164794c6` |
| `preparation-receipt-a06.json` | 15,615 | `a8cd38af62390f719ab7ee764bbe7419bfc9e16f50779096d74494f1b8a5a2ed` |
| four-row source aggregate | 62,256 | `8e615693b8c2b0221f5b48f022720bf684e2f13b7d5be21390cb930dc449b3a5` |
| 26-row external aggregate | 19,127,393 | `f49438640ab655502f0bf5edac84cecaf7a031bf14e7aafa93ef9cabc519f831` |

The preparation receipt excludes itself from the source aggregate. Its external
aggregate excludes future reviews, decisions, gates, and execution records.

## Remaining verification

A06 is accepted as source only. Actual capsule entry and all four compiler
phases remain untested.

The current source decision and compile gate are absent. ROOT must create and
review those exact artifacts before any launch.

No compiler, generated binary, controls, retained supervisor, bootstrap,
authorization, producer, or native path ran during this review. No native
output, product integration, WATCHED, HEARD, or creative acceptance exists.
