# Existing-media payload source review A03

## Disposition

The frozen A03 package is **not ready for a proof-capable build freeze or path-bound observation**.

Three P1 defects block the deferred measurement. Two P2 defects leave collection and failure evidence incomplete.
An isolated compiler-only diagnostic could still expose syntax or API errors. It would not close this review.

This was a source-only review of the complete 2,041-line module, 185-line binary, three contract documents, and 570-line closure verifier.
I did not format, build, typecheck, test, link, or execute the package or closure verifier.
I did not call native frameworks, inspect a process, open project state, read media, start workers, use the GPU, or operate Resolve.

## P1 — the deferred runner always collides with the binary's exclusive output-root creation

`verify_payload_closure_a03.py:474-477` creates `measurement-output` before launching the binary.
The binary calls `open_output_root` at `package/crates/editor/src/bin/payload_measure.rs:128-132`.
That operation calls `create_dir` at `payload_measure.rs:1977-1983` and requires an absent path.

The runner therefore reaches `AlreadyExists` before fixture collection.
This is deterministic from the reviewed source and does not require execution to establish.

Keep the parent output directory exclusive, but pass an absent child path to the binary.
Alternatively, redesign the binary around a descriptor-bound, empty directory supplied by the runner.
Do not weaken exclusive ownership to an unchecked existing pathname.

## P1 — executable authority is only checked before the subprocess

`verify_identity` reads the identity document, executable, and optional build manifest at
`verify_payload_closure_a03.py:321-359`.
`run_verified` invokes it only before the subprocess at lines 467-473.

The post-run path checks the package, runner files, and source manifest at lines 484-493.
It does not re-read the identity document, executable, or build manifest.
The returned `executable_identity` at line 516 is only the first observation.

Timeouts, subprocess errors, and early postcheck failures also bypass those later checks.
There is no `finally`-style reconciliation around lines 474-501.
The outer failure record at lines 551-563 omits the retained before observations.

This contradicts the before-and-after executable/source closure promised by the A03 contract.
Retain the before observations, then always attempt bounded postchecks on every outcome.
Compare the identity document, executable, build manifest, source manifest, package, and runner files.
Record each postcheck result in the bounded success or failure document.

The resulting claim must remain path-level identity.
It must not claim loaded-vnode or executed-byte authority.

## P1 — generated `EntityId` key capacity is undercharged before allocation

`map_precreation_context` measures one key created with
`"payload-a03-precreation-key".to_owned()` at `payload_measure.rs:1267-1281`.
The budget multiplies that observed capacity at lines 1319-1327.

Actual `EntityId` keys come from `format!` at lines 1726-1733 and 1763-1769.
The representative string has 27 bytes. The longest generated text has 26 bytes.
Text length does not bound `String` capacity across these two construction paths.

For the declared Rust 1.94 implementation, the format machinery preallocates 34 bytes for these keys.
That exceeds the representative `to_owned()` capacity used by the budget.
The code therefore allocates before establishing its claimed 512 MiB upper bound.

Charge a conservative per-key capacity before construction, or construct every key through a bound-preserving path.
The report should retain the actual generated-key capacities and reject any capacity above the admitted bound.
Include the one-at-a-time formatting scratch used for `ContentHash` keys where it overlaps the returned key.

## P2 — map rows record requested counts instead of actual collection cardinality

`insert_map_phase` inserts every input at `payload_measure.rs:1523-1525`.
`insert_set_phase` inserts every input at lines 1556-1558.
Neither function checks `map.len()` or `set.len()`.

Both functions pass the caller's requested `entries` to `finish_map_phase`.
That function publishes the requested value at lines 1477-1481.
The later row validator can therefore validate a requested count without validating the resulting collection count.

Check the actual collection length before ending each phase.
Record the observed length and require equality with the requested count.
Preserve a causal mismatch record when comparison fails.

## P2 — report-stream failure loses completed map evidence and does not durably close the partial report

After `set_map_probe`, the report contains 28 validated rows and seven precreation budgets.
If complete-report serialization fails, the binary calls `write_failure_from_report` at
`package/crates/editor/src/bin/payload_measure.rs:173-181`.

That function replaces both completed collections with empty vectors at
`payload_measure.rs:1997-2015`.
This discards the completed map evidence that the A03 documents say failures preserve.

`stream_json` only flushes, extracts, and synchronizes the file after serialization succeeds at lines 1962-1974.
A serialization or cap failure returns before those steps.
The partial `report.json` can remain, but its durable byte identity is neither established nor recorded.
This contradicts `output-schema-a03.md:46-50`.

Retain compact completed map and precreation evidence in `failure.json`.
If that evidence could exceed the failure cap, retain a fixed causal summary plus an exact partial-file identity.
Attempt flush and sync during failure reconciliation, and record whether each operation succeeded.

## Closed A02 findings

A03 closes several earlier source defects:

- `FailureFromReport` now derives `Serialize` at `payload_measure.rs:1917-1932`.
- Compact JSON observation uses a count pass, checked reserve, and capped writer.
- Success and ordinary failure JSON use exclusive files and a bounded streaming writer.
- `set_map_probe` requires exactly 28 ordered map rows and seven precreation budgets.
- Map-probe failures retain completed rows, a partial counter, and precreation context.
- The probe constructs one collection input vector at a time.
- Fixture reads retain one descriptor, bounded bytes, stable metadata, and exact hashes.
- The source-only documents avoid native, physical-memory, RSS, playback, and creative claims.

The P1 key-capacity finding means the precreation admission itself is not closed.
The P1 authority finding means the new external wrapper does not yet satisfy its documented lifecycle.

## Static closure checks

I independently rehashed all 58 entries in `source-copy-manifest-a03.json`.
Every byte count and SHA-256 matches the copied package.
The package contains exactly the 58 declared regular files, with no missing or extra file.

I also rehashed all five `runner_files` entries.
Every recorded byte count and SHA-256 matches.

These checks validate the frozen source copy only.
They do not build or execute it, and they do not cure the findings above.

## Required successor gate

1. Preserve A01, A02, and A03 unchanged.
2. Repair the runner and binary output-root ownership contract.
3. Recheck executable and build identities on every terminal path.
4. Charge the actual key-construction capacity before allocation.
5. Record and validate actual map and set cardinality.
6. Preserve completed map evidence and partial-report durability outcomes.
7. Freeze and review a successor source package before any proof execution.
8. Run build, typecheck, formatting, lint, and static tests only against that reviewed successor.

A later green source review would authorize an isolated build gate.
It would not establish product admission, native text feasibility, process memory, playback, hearing, full-film completion, or creative acceptance.

## Exact reviewed identities

| File | SHA-256 |
| --- | --- |
| `source-binding-before-copy-a03.json` | `42448e511e5b606d396828b0cb3a93fb0fa046dc25843049512c0e8be279bc14` |
| `source-copy-manifest-a03.json` | `4bf81d344bd4ca14103de47061aaaebed6fe7874a1a380d233f7dda75b5b8130` |
| `source-stage-a03.json` | `62e21f3d312d0c54b1eff9e466508e937123e436f6f85707e8efa560b5b302eb` |
| `package/crates/editor/src/payload_measure.rs` | `6f4df20aa972d18c52c73fa073c9f431871495567d7910d0fdd4b9e4fa12510e` |
| `package/crates/editor/src/bin/payload_measure.rs` | `835db4e58aed2ec6f7f48c3edbce6bd627686b5c2f81a9ab33600af47126f847` |
| `allocation-ledger-a03.md` | `df53988319155d71a88c6b3cb29c14340bbf9a2e77966f8adb269624cdc9133f` |
| `output-schema-a03.md` | `27c4d7e9bd23aef5147acd1fecf80bbe41621d628324170332e1fd749c0343c9` |
| `source-rationale-a03.md` | `079a68e5583ac0d64b16ada99128894404ebc9a9e5803a776779d6df66a122de` |
| `verify_payload_closure_a03.py` | `2263c62a7675d7ff84ed180ff347a33a0e344f6bc84e5916d1e075534d46309c` |

This review is within the same model family. No cross-family reviewer was available.
