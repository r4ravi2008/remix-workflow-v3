# Rust producer qualification A01 source peer review

## Disposition

**Rejected before build. Four P1 and three P2 finding groups remain.**

A01 is a bounded, source-only draft. Its fixed receipts and direct-build recipe
are internally consistent. The current source cannot compile, cannot construct
the selected two-key acceptance graph, and cannot perform the required fresh
revalidation. Preserve A01 as unbuilt evidence and repair it in a successor.

This review is same-model-family and nonblind. I received the parent's initial
source findings before completing this independent read.

## Bound package

| Item | Observed value |
|---|---:|
| Package | `rust-producer-qualification-a01` |
| Manifest bytes | 15,595 |
| Manifest SHA-256 | `e49d89db261bcd0c642844652de3fa886d7974c261fd5fc58c3946b084034be0` |
| Source rows | 8 |
| Source bytes | 63,524 |
| Source aggregate | `21f8a20079f38effb5223e66e130dcb51038c2de05785a40d94ccaef98cd256b` |
| External rows | 31 |
| External bytes | 13,711,189 |
| Direct-build recipe bytes | 8,174 |
| Direct-build recipe SHA-256 | `5ff030326ab5a0bd4b99d6d1d154ed254d172d35aee452a28c9b98630ccaefb4` |

I re-read and rehashed all eight source rows and all 31 external rows. Every
receipt matches. The package inventory contains exactly those eight rows plus
the self-excluding manifest. Interpreting the declared domain suffix as one NUL
byte reproduces the source aggregate. The manifest declares no external
aggregate, so only its individual external receipts can be verified.

The recipe's compiler, four archives, dependency closure, package root, source
paths, outputs, and absent attempt root match the manifest and saved files. I
did not invoke the recipe, compiler, harness, runner, or any imported source.

## P1 findings

### P1 — `validate_runner_manifest` borrows a temporary

`qualification.rs:595` assigns the result of
`parse(&bytes)?.object("runner manifest")?` to `root`. The `StrictJson` temporary
is dropped at the end of that statement while `root` is used later. This is the
standard borrowed-temporary `E0716` shape. Store the parsed document in a local
owner before taking the object reference.

### P1 — the selected acceptance graph cannot be constructed

`reconstruct_fixed_source` partitions the 2,068-row candidate into four prefix
classes. It uses the 2,017-row Source prefix as the top source subject. The
selected contract requires the complete 2,068-row candidate plus nine freshly
measured nested acceptance, peer, and parent rows for Build, Input, and PNG.

`source_subject` also rejects the first unconditional missing slot before it
constructs any evidence. If those slots were merely removed, it would still
supply an empty evidence vector. `runner_subject` always supplies an empty
vector. The trust root requires four ordered source evidence classes and one
runner evidence class. Therefore a future valid pin and records cannot make
this A01 path succeed.

Repair the subject shapes with freshly observed record and review rows. Do not
turn the current missing states into fabricated references.

### P1 — `full_revalidate` does not perform fresh revalidation

`OpaqueRustQualification::full_revalidate` hashes only bytes already retained
inside `Accepted<T>`. It does not rerun `reconstruct_fixed_source` or
`reconstruct_fixed_runner`, reopen any authority, or compare fresh bytes with
the accepted values. It joins only Source and Runner subject references.

The retained full 2,068-row candidate bytes are never checked here. The Build,
Input, and PNG digests in `SourceValueSummary` are also not joined to accepted
nested records. This cannot satisfy the required pre-authorization and
post-closure revalidation boundaries.

### P1 — fixed-file reads can block and miss pathname substitution

`open_nofollow` uses `O_CLOEXEC | O_NOFOLLOW`, but omits `O_NONBLOCK`. A FIFO at
a fixed path can block during `open` before `is_file` rejects it. The reader
also compares only metadata from the held descriptor. It does not require an
exact canonical path or compare pathname identity before and after the read.
A pathname replacement can therefore leave the descriptor checks unchanged.

Use the reviewed nonblocking, no-follow reader. Bind the exact canonical path,
compare descriptor and pathname identities before and after reading, and retain
the bounded EOF and content checks.

## P2 findings

### P2 — runner bytes are measured, but the typed runner graph is incomplete

The code measures all 19 declared runner files and checks the fixed manifest,
build report, output receipts, and ten control IDs. Those byte bindings are
useful. The resulting RoleIndex has no separately frozen expected role/tag
schedule, row count, encoded byte count, or digest. The harness checks only the
19-file and ten-case counts.

The ten case booleans depend only on the result-count and passed-count scalars.
They do not reference the measured control report or case-specific evidence.
The build validator requires phase argv to be nonempty and `streams` to be an
object, but does not project the exact commands, environment, stream receipts,
or return-code joins into the RoleIndex. A future acceptance record would bind
an underspecified runner subject.

Freeze the complete runner role/tag vector and encoded digest. Add the minimal
semantic dependencies that join the ordered cases and build facts to their
measured reports. Avoid a broader process redesign.

### P2 — the harness publishes no independently reviewable vectors

`diagnostic_harness_a01.rs` reconstructs the values and prints one summary
line. It does not exclusively publish the full candidate vector, four class
vectors, runner vector, or a canonical report with their byte counts and
SHA-256 values. The package therefore has no separately qualified actual class
bytes. Add bounded, exclusive outputs and an exact canonical report before a
control result can qualify the reconstruction.

### P2 — closure metadata mixes A08 and A10 and omits an external aggregate

The manifest's `predecessors.subject_adapter_manifest_sha256` is
`4088075b25f74e74350cd575075ce561b82cbffa3a762a4048b15cebd05d2ec0`, the exact A08 manifest digest. The bound implementation and
current source manifest are A10, whose digest is `f9542ea9eda14c8892dc2cb246ee448fd176a60083fb83d9f5d8b3b1dbaa06fe`. The adjacent
peer-review digest refers to A10 evidence, but that review has no corresponding
external-binding row. This mixes predecessor generations in one authority
block.

The manifest also provides an external row count without a domain-separated
external aggregate or total-byte field. Add the exact A10 lineage rows and one
framed external aggregate. Bind the package manifest and both aggregates in the
future build preflight.

## Verified limits and remaining boundary

The current A02 trust root still has no compiled pin. That fail-closed state is
correct. A01 creates no `Accepted<T>`, authorization, attempt, child process,
native result, media result, product integration, playback, hearing, or
creative acceptance.

The next source successor must close these findings before compilation. After a
clean source review, compile and run only the fixed diagnostic controls. Actual
acceptance records, the trust manifest, bootstrap authority, runner successor,
and attempt authorization remain separate later gates.
