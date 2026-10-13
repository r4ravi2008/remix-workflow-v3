# Existing-media payload source review A01

## Disposition

The A01 payload package is **not ready for a proof build or execution**.

The copied source closure is internally consistent. Two P1 findings prevent a truthful, bounded report.
One P2 finding prevents the aggregates from closing an old-media ownership derivation.

This was a source-only review. I did not format, build, typecheck, test, link, or execute the package.
I did not call native frameworks, open project state, read media, start workers, use the GPU, or operate Resolve.

## P1 — an executed report would retain an unbuilt state and lacks authority binding

`payload_measure.rs:893-914` always emits `state: source_measurement_authored_unbuilt`.
It also says the measurement seam remains unbuilt.
Those statements become false when this exact binary executes successfully.

`measure_package` accepts any `PACKAGE_ROOT` and reads eleven relative fixture paths.
It does not read or validate `source-copy-manifest-a01.json` before parsing.
It does not compare fixture hashes with the bound authority set before producing a success report.
The report also lacks its executable identity and the source-copy manifest identity.

The per-fixture SHA-256 values are useful evidence about the bytes actually parsed.
They do not independently connect the report to the reviewed source closure.
An external closure could make that connection, but no such frozen execution wrapper exists in A01.

Before a proof build, create a successor with these properties:

1. Emit a truthful executed-state value and remove the stale unbuilt finding.
2. Bind the exact source-copy manifest and frozen executable identity in the report.
3. Enforce the expected fixture set and exact hashes before deserialization.
4. Recheck bound inputs before success, or bind equivalent before-and-after checks in a frozen driver.
5. Keep the parsed-byte hashes so the final closure can join each observation to exact bytes.

`source-rationale-a01.md:112-118` already requires the run to bind the source-copy manifest.
The current implementation does not satisfy that gate.

One provenance label also needs correction.
`source-binding-before-copy.json:13` names `ff89563d...` as `originalBuildManifestSha256`.
That value is the producer executable SHA-256 inside `build-a03.json`.
The actual build-manifest file SHA-256 is `0e59a361...` at lines 2-5.
Rename the field to identify the producer, or remove the duplicate field.

## P1 — input, report, and failure persistence are not bounded as documented

`read_bounded` at `payload_measure.rs:269-283` checks only file length before and after the read.
It does not compare file type, device, inode, modification time, or change time.
A same-length in-place change can therefore pass its metadata test.

The function reserves the initial length, then calls `take(64 MiB + 1).read_to_end`.
The vector can grow beyond the initial reservation before the function rejects a changed file.
Even an exact-limit file can require spare capacity for the EOF probe.
`max_json_bytes` is therefore a read-length limit, not an owned-capacity limit.

Use one opened descriptor and a fixed exact-length allocation.
Read exactly the admitted length, then probe EOF with fixed scratch storage.
Compare a stable descriptor identity and metadata tuple before and after the read.
Continue to hash the exact bytes passed to Serde.

`json_observation` creates an uncapped serialized `Vec` and `String` at `payload_measure.rs:289-303`.
`measure_package` then duplicates the complete report into `serde_json::Value`.
`write_report` serializes that value into another uncapped `Vec` at lines 917-924.
No encoded report-byte cap or bounded streaming writer covers these owners.

The row and fixture limits bound record counts.
They do not bound serialized capacity or all simultaneously retained report copies.
Add checked encoded-byte limits and stream the final report through a bounded writer.
Record the actual retained capacities if they inform the later Plan8 ownership calculation.

The binary writes failures only to stderr at `src/bin/payload_measure.rs:11-13`.
A write or sync failure can leave an ambiguous partial `OUTPUT_JSON`.
This contradicts the preserved-failure requirement in `source-rationale-a01.md:114-116`.
Use an exclusive bounded failure record and keep partial output distinct from a completed success report.

## P2 — aggregate columns overlap and omit map storage

The traversal covers every heap-owning `String` and `Vec` field currently reachable from `Snapshot` and `ExportPlan`.
I found no missing current model field in that traversal.

The aggregate columns are not additive:

- `root_layout_bytes` includes direct `String`, `Vec`, and map headers in the root value.
- `vector_capacity_bytes` includes complete inline element layouts, including nested container headers.
- `container_header_bytes` counts those same observed headers again.
- BTree node storage and inline key/value placement remain absent.

Therefore, summing the three fields double-counts many headers and still omits BTree storage.
This conflicts with the additive formulas in `allocation-ledger-a01.md:8-14` and lines 23-40.

`push_map` records one `Layout::new::<(K, V)>()` size at `payload_measure.rs:224-245`.
It does not record `Layout::array::<(K, V)>(actual_entries)` for each observed map.
The separate growth table does that arithmetic only for seven fixed counts.
The shared field name `requested_pair_layout_bytes` therefore has two different units.

Keep the observations non-additive, or classify each header by its containing allocation.
If a derived total is added, count each inline owner once and label map storage as a proxy.
Do not describe the proxy as an actual BTree allocation.

The report also retains observation-owned vectors, row strings, and the `serde_json::Value` tree.
Those owners are outside the typed `parsed` and `cloned` aggregates.
That boundary is acceptable only when it remains explicit and separately bounded.

`PcmChunk` and `Stream` each appear twice in `type_layouts`.
They are listed directly at `payload_measure.rs:796-798` and again through `pcm::payload_measurement_layouts`.
Remove one copy so layout row identity is unique.

These corrections make the output useful as field-level capacity evidence.
They still do not establish the simultaneous product lifetime required by Plan8.
The later lifecycle proof must retain the actual Snapshot, plan clones, JSON owners, queues, frames, PCM, and writer owners.

## Accepted source boundaries

The bounded `MapGrowthObservation` is truthful pure `Layout::array` arithmetic.
It does not measure BTree nodes, and the source says so.

Native AVFoundation, CoreMedia, CoreVideo, CoreText, and CoreGraphics allocations remain excluded.
This review does not require a native allocation or process-RSS measurement.

Private worker and native wrapper rows provide Rust layout sizes only.
They do not prove queue contents, callback ownership, drop order, or peak runtime ownership.

The current 512 MiB picture budget remains the product admission authority.
This observer cannot replace that budget or close the downstream old-media envelope.

## Static closure checks

I rehashed all 58 entries in `source-copy-manifest-a01.json`.
Every recorded byte count and SHA-256 matches the copied file.

The copied package differs from the current product in the six declared, feature-gated files.
It also adds the two declared measurement source files.
I found no undeclared copied-source difference in the manifest comparison.

The module has four unused imports: `Cadence`, `MediaTime`, `Span`, and `PropertyCurve`.
Remove them before a warnings-as-errors Clippy gate.
No build was run to discover other compiler or lint findings.

## Required next gate

1. Preserve A01 unchanged.
2. Repair both P1 findings and the P2 aggregate semantics in a successor.
3. Re-review the successor source, output schema, rationale, and ledger.
4. Only then authorize lock generation, build, typecheck, formatting, and static tests.
5. Review the frozen runner and structured success/failure records before executing fixtures.

A green successor would establish source readiness for an isolated build.
It would not establish Plan8 admission, native text feasibility, product integration, playback, hearing, film completion, or creative acceptance.

## Exact reviewed identities

| File | SHA-256 |
| --- | --- |
| `source-binding-before-copy.json` | `67d8b41b54ceee4f1205de32d2a8990614e438cc898ea25bec5c7fa2051c3e9f` |
| `source-copy-manifest-a01.json` | `1d1e301032d73dffd53d31f7cf2e26608cba94931ed2bee1d800e29c21714fab` |
| `package/crates/editor/src/payload_measure.rs` | `41c5845ad500ce5da2113595fae6a83af8a30f63d67ca459bf3cf8902beaebc6` |
| `package/crates/editor/src/bin/payload_measure.rs` | `9dfc93853bd9a9a9872cbd1eda50219df6b1d1eb562a99ce7045f4d8bdb8832d` |
| `allocation-ledger-a01.md` | `123255daea8be64ff6e6d98c6875d78da96197eb28f840ad124678a35436bd27` |
| `output-schema-a01.md` | `5e9298a035d15a2b2e1539568b1d3ea1d6ff6116519df656b0463f996f2d5816` |
| `source-rationale-a01.md` | `7cdc48ed0d5bcd7f94fcff7fa56ecc70fa5449f959c50951aa8680e94d984d19` |

This review is within the same model family. No cross-family reviewer was available.
