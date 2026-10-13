# Rust producer runner A10 root orchestration source peer review A02

## Disposition

**Rejected for execution pending repair.** The A02 wrappers close the four
bounded A01 repair groups in part. One P1 and five P2 findings remain. The
accepted A04 process utility remains a separate source-only dependency. The
native A10 writer and its candidate review are outside this review.

This is a same-model-family, nonblind source review. I read the complete A02
helper, inline capsule, compile caller, controls caller, receipt, rationale,
recipe, A01 peer review and disposition, A04 utility reviews, A09 contract and
schema, and the frozen A10 manifest and contract. I did not import, compile,
execute, test, launch a child, run a probe, or use native, media, GPU, Resolve,
playback, listening, or creative workflows.

## Frozen identities

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `rust-producer-runner-a10-readonly-root-source-measurement-a02.py` | 15,940 | `8ad0f874b88da75fe8498d106001cdc5dfda27a925871b3dcba8085037c62331` |
| `native_runner_fixed_compile_a10.py` | 26,111 | `4113774649574f8588561619ccc24cd3088c8ddc3c19ff9a7b2146bf29c3ef73` |
| `native_runner_fixed_controls_a10.py` | 36,439 | `f26f1ac9f7a71ca37e828593b86d4290201dfc3a4bf6977c8c92ba883982c153` |
| `root_inline_launch_capsule_a02.py` | 10,066 | `dd05ca2911ce28365d949a20aee48b896318b83f723f1d60e374ffcb3f56978d` |
| `root-inline-launch-recipe-a02.json` | 3,085 | `07a69ac46520b27e04c9d940ee55081140d7a2263beb7170f00a830e1717f98b` |
| `orchestration-rationale-a02.md` | 3,861 | `f69b2b416d648825de00740bd5afb39de8d39b8f5b10b5426271ba1b889f4002` |
| `preparation-receipt-a02.json` | 7,451 | `4e61789e28142d9575ee1f43056085536ba33db8419b7153646f7785de72e4ab` |

The A10 source manifest is 55,008 bytes with SHA
`4341874179dd193ad23b5b9d0e9ea03eab37db09e533261c0d5d3d3b6dfd77ed`. It
declares 15 source files, 417,283 source bytes, and source aggregate
`8ee9a5750d0ef5c72b53df7a8668c9eadae1450989d1b7cb555e64c5757da82c`.
Its external aggregate is 106 rows, 10,714,908 bytes, and
`0a0315f760aedc4b761bf09fd00bab00d0fbd0a070f2d411b7f9222a0ff043b3`.

The A04 utility remains 46,572 bytes with SHA
`b903a9aff1cc2d8dae73b16800f177322b000b2983e5a45206a639326727d47d`.
Its source and receipt reviews remain accepted with no P1 or P2 finding. The
utility's exceptional cleanup supervision may exceed ordinary deadlines. That
does not establish arbitrary host security or a caller guarantee.

The A02 receipt records `callerSourceAccepted=false`, `rootGatePresent=false`,
and false compiler, controls, authorization, native, product, watched, heard,
and creative flags. It records the A10 source handoff as
`sourceReviewPending=true`. No A10 root gate or execution evidence exists.

## P1 findings

### P1.1: The wrapper does not enforce the frozen A10 source-review state

The A10 manifest currently declares `source_manifest_provisional=true`,
`actual_peer_receipt_pending=true`, and
`root_and_peer_review_required_before_compile=true`. The preparation receipt
records `peerReviewPending=true`, and its `nativeA10SourceHandoff` records
`sourceReviewPending=true`.

The compile caller checks only the external gate's
`rootPeerSourceAccepted=true` and hashes the manifest and review files. It does
not compare the manifest review gate or preparation handoff state with that
decision. An external gate could therefore claim acceptance while the bound
A10 subject still declares itself provisional and pending review.

Require the source manifest and preparation receipt to carry a closed source
review state, or make the gate contain an explicit, semantically validated
override whose source-review receipts match the current A10 manifest. A hash
join alone is insufficient for this state transition.

## P2 findings

### P2.1: The inline capsule does not enforce its complete fixed argv

The recipe pins the prefix `/usr/bin/python3 -I -B -c`, but the capsule checks
only Python flags, executable, recipe path, digest shape, role, and caller
argument count. It does not require `sys.argv[0] == "-c"` or compare the full
interpreter vector with the recipe. Its broad `4 <= len(sys.argv) <= 9` check
is weaker than the three role-specific vectors.

Require the capsule or the external root launcher to validate the exact
`sys.orig_argv` and role-specific argument vector. Bind the capsule bytes,
recipe bytes, and interpreter vector before Python starts. Keep loaded-image and
standard-library attestation explicitly outside this source scope.

### P2.2: Success publication precedes descriptor-closure proof

Both callers save their apparent success or failure report before closing the
caller descriptors. A later close failure raises after a success report has
already been published. The failure hook can then save a second causal file.
The saved failure record calls the closure state `descriptorClosurePending` and
does not contain the actual close results.

This can leave `report.json` or `controls-run-report-a01.json` claiming
`compiled=true` or `candidateControlsPassed=true` beside a close failure.
Publish a terminal record only after closure facts are known, or publish an
explicit nonterminal record and atomically finalize it after closure. Persist
the actual close attempts and errors in the causal record.

### P2.3: The source-readback report is not semantically joined to the A10 manifest

The compile caller requires `source_proof.inputsMatched=true` and stable input
rows. It does not require `source_proof.manifest` to equal the current parsed
manifest, nor does it compare the source and external aggregate objects or the
complete current manifest row set with `source_proof.inputsAfter`.

The caller therefore trusts a gate-bound but semantically stale source
readback if its listed files remain stable. Require exact manifest receipt,
aggregate, row-set, and imported-source joins before constructing the fixed
compile input set. Preserve the helper's held-byte and before/after identity
checks.

### P2.4: Per-launch joins do not require strict process field types or case identity

The controls caller requires strict Boolean types for the wrapper row, but the
`process` object values are compared without strict Boolean checks. The normal
`return_code == 0` check also accepts JSON `false` because Python compares it
equal to zero. The join does not validate `injectedFault` and
`injectedFaultMatchesSaved`, or require unique report and run-root paths for
the eleven launch rows.

Two variants share an expected code and can therefore pass with a duplicated or
swapped saved report unless their case identity and path provenance are checked.
Require strict process Boolean, integer, nullable-signal, PID, and wait-status
types. Require one report/run root per launch ID, and join the saved fault and
mutation evidence to the expected variant. Preserve the intentional
`stopped=None` rule for `verified_private_group_mismatch`; the A10 source makes
that fact intentionally unconstrained.

### P2.5: The focused report join omits several declared false-scope fields

The A10 focused schema emits `audioReviewed`, `nativeFrameworkLoaded`,
`mediaProcessStarted`, `gpuProcessStarted`, and `resolveProcessStarted` as
false. The controls caller checks only
`nativeResultAccepted`, `productIntegrationAllowed`, `watched`, `heard`, and
`creativeAccepted` in the focused report. It also does not join the complete
false-scope object from the fake producer invocation.

Require every false-scope field declared by the focused A10 schema and fake
invocation schema. Do not invent fields for the combined report or the
AttemptReport, which intentionally expose smaller field sets. Keep all
runtime, native, media, playback, and creative claims false.

## Closed A01 repairs and bounded behavior

The inline capsule now authenticates the recipe and selected caller through
one bounded held-byte read before executing the caller bytes with `optimize=0`.
The callers authenticate the unchanged A04 utility before using its
`run_phase`, `save_at`, inventory, and descriptor-relative publication seams.

The compile caller now uses explicit `require` checks, fixed four command
vectors, the cleared ten-variable Rust environment, fixed output paths, fixed
limits, input rechecks before every phase, Mach-O checks, and PID/group absence
checks. The controls caller now binds the ten lifecycle, fifteen focused,
eleven launch, twenty-one pure, and five nested review schedules.

The controls caller correctly permits only the three receipt-bound malformed
private JSON paths. It rejects every other unparsed JSON artifact. It joins
the current A10 combined, focused, lifecycle, pure, and launch report shapes
without requiring fields that the combined schema does not emit.

The three deliberate malformed fixtures are exactly these receipt-bound files:

1. `a04-lifecycle/cases/terminal_collision_fallback/output-parent/rust-native-run-primary-*/report.json`, 29 bytes, SHA-256 `a6f38dbfe66a446687ce5a95fbe7202d1f808824b26791267b00ab25517dfc4b`.
2. `a04-lifecycle/cases/double_terminal_collision_preserved/output-parent/rust-native-run-fresh-*/report.json`, 29 bytes, the same SHA-256.
3. `a04-lifecycle/cases/double_terminal_collision_preserved/output-parent/rust-native-run-fresh-*/report-failure.json`, 31 bytes, SHA-256 `a8ebc6f871fd25b405c0ce1c5a5b9184abc9f75646c990b59ef81329efda4aa2`.

The wildcard is the contract's run-directory prefix. The controls must verify
the concrete private path and bytes against this list, then reject every other
malformed report. They must not blanket-reject these bound collision fixtures.

The callers install bounded early hooks, retain partial inventory, and attempt
descriptor closure. These are source properties only. They do not establish a
compiled wrapper, a private control result, a producer child, native output,
media output, product integration, loaded-runtime attestation, WATCHED, HEARD,
playback, listening, or creative acceptance.

## Finite schedule and scope

The recipe allows four fixed Rust compile phases. Each phase has a 60-second
utility deadline, 1 MiB build streams, and 64 MiB library or binary output.
The private control has one 360-second phase, 21 pure cases, 10 preserved A04
lifecycle cases, 15 focused cases, 11 launch variants, and five nested review
variants. The A10 launch contract retains three eight-second rendezvous phases.

The A04 utility's exceptional cleanup supervision can exceed ordinary
deadlines. Forced orchestration termination and arbitrary host security remain
outside the guarantee. The A10 native source writer remains outside this peer
review while its own source review is pending.
