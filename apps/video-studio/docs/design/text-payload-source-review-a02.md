# Existing-media payload source review A02

## Disposition

The frozen A02 package is **not ready for a proof build or execution**.

A02 closes the A01 file-reader, non-additive aggregate, map-unit, and duplicate-layout defects.
One source-level compile blocker remains. Two P1 execution gates and one P2 failure/completion defect also remain.

This was a source-only review of the complete 1,337-line module, 175-line binary, three documents, and closure files.
I did not format, build, typecheck, test, link, or execute the package.
I did not call native frameworks, inspect a process, open project state, read media, start workers, use the GPU, or operate Resolve.

## P1 — `FailureFromReport` does not implement `Serialize`

`payload_measure.rs:1251-1261` declares `FailureFromReport` without a `Serialize` implementation.
`write_failure_from_report` passes that value to `stream_json` at lines 1321-1335.
`stream_json` requires `T: serde::Serialize`.

This is a direct source-level compile blocker for the measurement feature.
Add `#[derive(Serialize)]` to `FailureFromReport` before any build or typecheck freeze.

This finding is based on the trait boundary in source.
No compiler was run during this review.

## P1 — the report still lacks source and executable authority

The frozen fixture table correctly enforces eleven exact byte counts and SHA-256 values before deserialization.
The report also retains the exact same byte slice's hash and descriptor metadata.

`MeasurementReport` at `payload_measure.rs:207-224` still lacks these identities:

- the A02 source-copy manifest path, byte count, and SHA-256;
- the frozen measurement executable path, byte count, SHA-256, and native UUID when available;
- stable executable descriptor or loaded-image authority; and
- before-and-after source-closure checks around the complete run.

`source_stage` is a fixed label. It is not an authority join.
`package_root` is caller-selected and does not prove which reviewed source produced the executable.

A separately frozen wrapper can close this finding without broadening the measurement module.
The wrapper must bind the exact A02 manifest and executable before work.
It must recheck both after publication and bind the report or failure identity.
The wrapper must preserve its own bounded failure record.

Until that wrapper exists and receives separate review, A02 cannot support an accepted measurement claim.

## P1 — important Rust-owned temporaries remain outside checked admission

`json_observation` at `payload_measure.rs:433-445` still calls `serde_json::to_vec` and `to_string` directly.
Neither allocation has a checked preallocation bound.
The later 32 MiB report writer does not bound these earlier buffers.

The fixtures are exact and small enough to make this risk predictable.
That fact does not create an explicit owned-capacity contract.
Derive a checked serialization bound before both calls, or replace them with a bounded measurement method.
Retain the observed length and capacity evidence required by the unit.

The map probe has a larger retained-owner gap.
`map_insertion_probe` retains the parsed plan, parsed snapshot, asset template, and timeline template.
For each count, lines 1099-1109 precreate four input vectors at once.
The 10,000-entry case deep-clones 10,000 `StoredAsset` values and 10,000 `Timeline` values.

Those allocations occur before `begin_phase`.
They are therefore absent from the 64 MiB requested-callback counter.
The counter is an observation limit after allocation, not a memory-admission mechanism.

Add a checked logical charge for every precreated vector and deep-cloned value.
Report the retained high-water bound.
Construct one collection's inputs at a time where possible.
Drop parsed owners and completed input collections at their last use.

This finding concerns Rust-owned payloads inside the stated scope.
It does not require native-framework or process-RSS measurement.

## P2 — map completion and failure evidence are not self-validating

`collect_package` creates a report with `state: measurement_complete` and an empty `map_allocations` vector.
`set_map_allocations` accepts any vector without validation.
`write_complete_report` then writes the report without checking the map evidence.

The provided binary calls these functions in the intended order.
The public interface still permits a complete report with absent, partial, reordered, or overflowing map rows.

Finalize through one consuming operation or validate before publication.
Require exactly 28 rows in the declared owner-and-count order.
Require `overflowed == false` for every row.
Require zero callback bytes for zero entries and positive callback evidence for positive entries.
Check each actual map or set length against the declared entry count.

`map_insertion_probe` returns only `StudioError` on failure.
It discards completed map observations and the failing owner/count.
`FailureFromReport` also omits `map_allocations`.
The resulting failure phase is only `actual_btree_insertion_probe`.

Return a structured map failure with completed rows, failing owner, count, and counter state.
Include those fields in `failure.json`.
This is necessary to distinguish instrumentation failure from a specific bounded insertion failure.

The same 32 MiB cap applies to success and detailed failure serialization.
A report-size failure can therefore cause the detailed failure record to exceed its cap too.
Keep a fixed-size causal summary that always fits independently of retained completed observations.
Large completed observations can remain in separate partial files with exact hashes.

## Closed A01 findings

### Exact one-descriptor fixture reads

`read_bounded` now opens one regular-file descriptor.
It captures device, inode, size, modification time, and change time before and after the read.

The function allocates an exact-size boxed slice and reads fixed 64 KiB chunks.
It performs a one-byte EOF probe and rejects changed descriptor metadata.
The exact owned bytes supply both SHA-256 and Serde input.

The eleven frozen byte counts and hashes match the copied fixtures.
This closes the A01 input-cap and same-length-change finding for the declared byte-authority boundary.

### Truthful state split

`source-stage-a02.json` remains `source_authored_unbuilt`.
The future persisted success state is `measurement_complete`.
No persisted report currently claims execution.

The P2 finalization issue above must still prevent incomplete map evidence from receiving that state.

### Streaming success and failure output

The complete report no longer builds a `serde_json::Value` or final encoded `Vec`.
`BoundedWriter` applies a 32 MiB byte cap while streaming JSON.

The binary creates an exclusive output directory.
It uses exclusive `report.json` and `failure.json` creation.
A partial report remains distinguishable from the causal failure file.

The missing `Serialize` implementation currently blocks the report-derived failure path.
The P2 findings above also limit the claimed failure completeness.

### Non-additive aggregate semantics

`non_additive_container_header_bytes` now labels overlapping header observations correctly.
`owned_heap_lower_bound_bytes` excludes that diagnostic column and excludes BTree nodes.

Observed map rows distinguish one-entry layout from contiguous `Layout::array` arithmetic.
The separate map probe describes requested allocator callbacks during actual insertion.
It does not claim allocator bookkeeping, physical pages, RSS, or native memory.

`type_layouts` now removes duplicate names after combining public and private rows.
This closes the duplicate `PcmChunk` and `Stream` output defect.

## Actual BTree observation boundary

The allocator phase is narrow and correctly described as requested-layout evidence.
Keys and values are created before each active phase.
Collection destruction occurs after the phase ends.

The callback delegates to `System` and records current-thread requests through atomics.
It does not establish physical allocation size, allocator metadata, or production peak memory.

The 64 MiB counter marks an overflow after `System` has handled a request.
It does not prevent the request or bound the precreated inputs.
The P1 admission repair must retain that distinction.

## Static closure checks

I rehashed all 58 entries in `source-copy-manifest-a02.json`.
Every recorded byte count and SHA-256 matches the copied package.

The A02 package differs from A01 only in the declared module and measurement binary.
The before-copy binding matches all 58 A01 package records.
The source-stage sidecar binds the exact A02 copy-manifest SHA-256.

The module still imports `Cadence`, `MediaTime`, `Span`, and `PropertyCurve` without using them.
Remove those imports before a warnings-as-errors Clippy gate.
No build was run to discover other compiler or lint findings.

## Required next gate

1. Preserve A01 and A02 unchanged.
2. Add the missing `Serialize` implementation in a successor.
3. Bound JSON observation and all precreated map-probe owners.
4. Make complete-report finalization validate the exact map evidence shape.
5. Preserve completed map evidence and a fixed-size failure summary.
6. Author and review the frozen executable/source closure before execution.
7. Only then generate build, typecheck, formatting, Clippy, and static-test evidence.

A green successor would authorize only the isolated build and typecheck freeze.
It would not establish Plan8 admission, native text feasibility, product integration, playback, hearing, film completion, or creative acceptance.

## Exact reviewed identities

| File | SHA-256 |
| --- | --- |
| `source-binding-before-copy-a02.json` | `b82e5e52298cbe73133f91780e415502596f9ec3ec8daf96fc6ae096d8d0deb9` |
| `source-copy-manifest-a02.json` | `aacdbe91ca164abe6abab9a5bf3e54f8b804c0fda5bd2ff8ffc66293fae59ce7` |
| `source-stage-a02.json` | `feae3144b557e9179e0d0f6ec8ccc61038cf0afac9885f0cc8a37be566e2e0df` |
| `package/crates/editor/src/payload_measure.rs` | `4b6250fa20393c76f5235e5af78fae0bc5a82d54ba89b59e00a1ced23d9eb2ea` |
| `package/crates/editor/src/bin/payload_measure.rs` | `481e2435095c2e6e1b952170638d28053105578dc5e9c039f6ba417a9a73da77` |
| `allocation-ledger-a02.md` | `b7b3ebfbd6e3fd3b2d99a8f17efdbbccfdc25f7437b64e553f9634ae78fe0425` |
| `output-schema-a02.md` | `9f72319a227723c6b3e09df101e37fc581d634f36661af74796e4457926a93f4` |
| `source-rationale-a02.md` | `e12164c6e7b04b2081defad9ad31bbf5814ac7d6bb7116d2ae23e8c04ab2a2fd` |
| `text-payload-source-review-a01.md` | `7773673d21b90738a8f3cdc7144649143384032cc8f313676f8c4b36b6d4a701` |

This review is within the same model family. No cross-family reviewer was available.
