# Native text report comparator A01 source review

## Review status

This is an additive, source-only review. I did not run the comparator, either producer, a probe, a font tool, CoreText, CoreGraphics, ImageIO, or a control.

The reviewed package is:

- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/text-report-comparator-a01/compare_text_reports_a01.py`
  - 172,808 bytes
  - SHA-256 `0f766e10a05eb2b6c39a4fcd339c4305f2e89ff84a7cfcd12b35c592532995fa`
- `output-schema.md`
  - 7,428 bytes
  - SHA-256 `159211a4d463617f4c90ff224b51282faa353be2d820837e8d72e4ac7091eb7a`
- `source-rationale.md`
  - 7,264 bytes
  - SHA-256 `f1745a797775e8a6429e4c9890dace1906ece6bdde1a93147a1c2b07758e6f9a`

The package remains source-only and is not ready for proof execution. The positive reader, schema, evidence, and fresh-run checks are useful. The findings below can still permit false proof credit or an unbounded failure.

## Confirmed source strengths

1. The six-file input closure is read through one descriptor, capped at `MAX_INPUT_BYTES`, hashed, and compared to fixed bytes and hashes. The parsed case order and selected font identities bind to that closure (`compare_text_reports_a01.py:1560-1588`, `1596-1642`, `1644-1705`).

2. Report JSON rejects duplicate keys and requires exact top-level and nested object keys. Integer, boolean, finite-number, hex, array, string, and tagged-state validators reject wrong JSON types (`compare_text_reports_a01.py:216-235`, `816-886`, and the report validators at `500-756` and `1073-1380`).

3. Evidence traversal is descriptor-based. It rejects symlinked final components, walks parent components with `openat` and `O_NOFOLLOW`, rejects non-regular files, rejects the report inode, and admits stored and decoded byte totals before reading (`compare_text_reports_a01.py:2286-2333`). The four report roots, report inodes, and all admitted evidence inodes are checked for uniqueness (`compare_text_reports_a01.py:3048-3057`, `3101-3109`).

4. `StoredReader` and `DecodedReader` verify expected stored bytes and hashes, stable descriptor metadata, identity or bounded RLE decoding, decoded lengths, decoded hashes, and trailing data (`compare_text_reports_a01.py:2446-2538`). The row scanner streams raw and canonical masks, checks stride padding, nonzero bounds, distinct values, reversed row binding, and embedded orientation samples (`compare_text_reports_a01.py:2735-2827`).

5. Fresh-run comparison retains complete validated report projections. It removes paths, producer labels, and timestamps only in the documented fresh projection. Cross-producer projection maps wrapper field names but does not decode or normalize PNG pixels (`compare_text_reports_a01.py:1763-1787`, `1911-2162`, `2218-2247`). The source rationale states the same boundary at `source-rationale.md:28-59` and `122-164`.

6. Swift allocation events are replayed with index, action, transition, cap, peak, final outstanding, event-log byte, and written-file checks (`compare_text_reports_a01.py:2336-2443`). Rust and Swift ledgers are kept in separate comparison scopes, and their rows are not incorrectly required to be identical (`compare_text_reports_a01.py:3083-3111`).

7. Difference retention is bounded to 2,048 records while a digest covers every ordered difference. Large values are reduced to byte count and SHA-256 references, with the original reports remaining the authority (`compare_text_reports_a01.py:1707-1750`; `source-rationale.md:131-144`).

## P1 findings

### P1-1: Mandatory case draws, controls, dispositions, and snapshots are not required

The frozen Rust schema requires three repetitions, the complete control set, a clip/reference draw for `te-basic`, and a repeat-zero ImageIO snapshot for `ascii-digits-positive` (`feasibility-rust-a05/output-schema.md:337-341` and `620-630`). The Swift schema requires the `te-basic` clip/reference comparison and exactly three accepted supported repetitions (`feasibility-swift-a05/output-schema.md:152-160`).

The comparator does not bind those obligations to the frozen input or policy. `bind_rust_inputs` and `bind_swift_inputs` bind source facts, case kind, coverage, and fonts, but they do not validate the policy case schedule, allowed rejection errors, required draw roles, required control IDs, or required native-image cases (`compare_text_reports_a01.py:1596-1705`). The policy validators check shapes and caps, but only enforce array upper bounds (`compare_text_reports_a01.py:759-799`, `1436-1491`).

The producer gates accept incomplete evidence:

- `rust_case_gate_passed` requires `standard` for accepted repetitions, but never requires `clipped` for `te-basic`, a native image for `ascii-digits-positive`, or an exact four-control set. `all(stability["control_masks_identical"].values())` also passes for an empty map (`compare_text_reports_a01.py:2885-2936`).
- `swift_case_gate_passed` requires only main/guard fields for accepted repetitions. It never checks `toggles`, clip/reference fields, an exact rejection count, allowed rejection codes, or `nativeGlyphImage` (`compare_text_reports_a01.py:2939-2974`).
- `collect_rust_masks` and `collect_swift_masks` collect only fields that happen to be present (`compare_text_reports_a01.py:2671-2728`).

If both producer reports omit the same optional-looking role, the cross projection can compare two `None` values or two empty control sets. The fresh projections can also remain equal. `producer_internal_passed` can then be true, `differences.total` can be zero, and `main` returns the exit-0 state (`compare_text_reports_a01.py:3113-3170`). A rejection can similarly use an unsupported error code because the Rust gate accepts any rejection code and the input `allowedErrors` is never checked.

This contradicts the package statement that the producer gate checks the complete control set and clip/reference obligations (`output-schema.md:140-154` and `source-rationale.md:118-120`). Derive required roles from the frozen policy and case closure. Require exact repetition counts, expected control identifiers, clip/reference fields, native-image records, and allowed error codes before producer-gate success. Keep Swift's documented repeat-zero control storage difference, but make the required repeat-zero control set explicit and fatal when absent.

### P1-2: Rust `orientation.alpha_raw` is never opened or hashed

The Rust schema defines `orientation.alpha_raw` as a 272-byte native evidence file (`feasibility-rust-a05/output-schema.md:407-418`). `validate_rust_orientation` validates only its path, size, hash string, geometry, and flags (`compare_text_reports_a01.py:1494-1512`). `collect_rust_masks` scans `alpha_canonical.native_raw` and the canonical mask, but it never constructs a `BufferSpec` for `orientation.alpha_raw` (`compare_text_reports_a01.py:2626-2645`, `2671-2690`). `verify_native_images` also does not visit it (`compare_text_reports_a01.py:2857-2874`).

Therefore a distinct `alpha_raw` file can be missing, changed, or aliased without failing evidence admission. If the producer uses the same native file for both fields, the comparator still does not compare the two declared identities. The producer gate trusts `alpha_raw.padding_unchanged` despite never reading those bytes (`compare_text_reports_a01.py:2981-2987`). Make `alpha_raw` an admitted identity buffer. If it is intentionally the same native buffer as `alpha_canonical.native_raw`, require exact path, byte, and SHA equality before scanning it once.

### P1-3: Allocation ledgers are not independently reconciled

The rationale promises internally consistent Rust representation components and independent ledger validation (`source-rationale.md:101-120`). `validate_rust_allocation` checks types, caps, a few flag-to-number relationships, and representation cap binding. It does not recompute category totals, component reservation totals, retained totals, current totals, or peak totals (`compare_text_reports_a01.py:1515-1548`). `producer_internal_passed` trusts `peak_within_limit` and `all_accounted_bytes_within_preallocation` (`compare_text_reports_a01.py:2977-3003`). Empty categories and components are also accepted because only maximum lengths are checked.

Swift event replay is stronger, but the report's structured owner fields are only type- and cap-checked. The replay starts from the self-reported fixed `eventScratchBytes` and does not reconcile the structured owner components to `peakBytes`, `finalOutstandingBytes`, or the event owner transitions (`compare_text_reports_a01.py:719-736`, `2336-2443`). A zero-event, zero-component report can pass the current structural checks when its other producer fields are similarly self-consistent.

Add producer-specific conservation rules. Require the exact expected component and event categories, positive event coverage where the policy requires it, unique labels, and formulas for current, retained, peak, final, written-file, and event-log totals. Keep Rust and Swift formulas separate. Do not compare their layouts. This comparator also cannot close the previously reviewed Swift A06 retained `CaseResult` owner defect; that source review remains an independent gate.

## P2 findings

### P2-1: Mask geometry permits a large Python object amplification

The stored and decoded evidence caps are 256 MiB and 512 MiB, but Rust and Swift width, height, and stride fields have no product-specific upper bound (`compare_text_reports_a01.py:500-522`, `1073-1098`, `802-813`, `1443-1450`). `scan_mask` stores one Python `bytes` digest per row for both the raw and canonical masks before comparing them (`compare_text_reports_a01.py:2742-2769`, `2779-2785`). A report can claim a one-pixel-wide mask with hundreds of millions of rows while remaining within the decoded-byte cap. The row digest lists then consume far more memory than the admitted evidence.

Add fixed maximum dimensions and pixel counts derived from the frozen policy before opening evidence. Check all width-times-height and stride-times-height products against those limits. Alternatively use a bounded spool or a fixed-size row digest store. The documented statement that Python object overhead is unmeasured (`output-schema.md:180-182`) does not make this reader memory-safe.

### P2-2: Output write and JSON failure paths do not preserve a structured failure

`write_output_exclusive` catches `OSError` only from `os.open`. Errors from `os.write` and `os.fsync` escape as raw exceptions, and a partial output file remains (`compare_text_reports_a01.py:3006-3025`). The outer `main` catches only `ContractError`, while the failure path also catches only `ContractError` around the writer (`compare_text_reports_a01.py:3171-3184`). This can violate the documented exit-1 and failure-result contract (`output-schema.md:112-131`).

Catch expected write, flush, and close errors. Preserve the output descriptor identity, bytes written, and partial hash in a bounded causal error. Do not overwrite or silently reuse the partial path. Consider syncing the parent directory if the package intends crash-durable publication.

`parse_json_bytes` catches only `UnicodeDecodeError` and `JSONDecodeError` (`compare_text_reports_a01.py:816-827`). Deeply nested or oversized integer JSON within the report cap can raise `RecursionError`, `MemoryError`, or a conversion `ValueError` outside `ContractError`. Allocation-event parsing has the same exposure. Convert expected parser failures into the structured invalid-input result while preserving the already-read file identity.

### P2-3: Regular-file checks occur after potentially blocking opens

`open_regular_absolute` and `ReportContext.open_evidence` open paths without `O_NONBLOCK`, then check `S_ISREG` after the open (`compare_text_reports_a01.py:152-169`, `2298-2329`). A FIFO can block before the check, and a device can be opened before rejection. Use a nonblocking open strategy or an equivalent descriptor-safe regular-file admission path before any blocking read. Keep the existing `O_NOFOLLOW` and descriptor metadata checks.

### P2-4: Report parent identity is not retained across report and evidence reads

`load_report_context` reads and closes the report descriptor, then stores only the report path and report inode. `main` later opens the report parent by pathname and uses that pathname for evidence traversal (`compare_text_reports_a01.py:2877-2882`, `3043-3061`, `2280-2333`). A concurrent directory replacement can pair a validated report with evidence from a different directory before the fresh-root check. Retain the report parent descriptor and identity from the initial open, or verify the parent identity before every evidence traversal.

### P2-5: Shaping-derived fields are trusted instead of recomputed

`validate_rust_shaping` accepts `glyph_count`, `sorted_run_ranges`, and `ranges_form_complete_partition` as reported values. It does not recompute them from `visual_runs` and the bound UTF-16 source (`compare_text_reports_a01.py:1129-1159`). The Rust run validator also does not bound ranges to the source or derive `status_unknown_bits` from `status_bits` (`compare_text_reports_a01.py:1162-1188`). The Swift projection recomputes partition status, but `swift_case_gate_passed` never requires that status to be true (`compare_text_reports_a01.py:1978-2005`, `2939-2974`).

Two matching reports can therefore carry the same incomplete partition, wrong glyph total, or stale derived flag and still pass fresh and cross comparison. Recompute source range coverage, range ordering, glyph totals, visual-index uniqueness, and status-bit relationships. Require the frozen case's complete-UTF-16-range obligation before producer-gate success. Continue preserving raw native observations without normalizing them.

## Fresh-run and comparison boundary

The comparator does reject reused report roots, reused report inodes, and reused evidence inodes. It does not prove separate process launch, executable identity, loaded-image identity, or source closure by itself. The rationale correctly assigns those claims to the parent driver (`source-rationale.md:88-99`).

The comparator also intentionally does not decode PNG pixels. Its output must remain bounded by the independent orientation decoder and the separate Rust/Swift source, dependency, binary, and host gates (`output-schema.md:184-188`).

## Verdict

The package has a strong descriptor-based evidence traversal and preserves differences without pixel normalization. It is not proof-ready until the P1 obligations are repaired. P2 reader, failure, and derived-field repairs should be included before adversarial controls or native execution.

