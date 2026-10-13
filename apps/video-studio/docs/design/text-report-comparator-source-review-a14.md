# Comparator A14 source review

Status: source-only independent review. The A14 control, comparator, compiler,
native framework, media, GPU, Resolve, and Python control process have not run.

## Reviewed identities

| Item | SHA-256 |
| --- | --- |
| `text-report-comparator-a14/actual-comparator-control-a14.py` | `b43e3ada668f150a52ce7c77c7028fdf91b0447a7f15fc08cb040d0ea98617c1` |
| `text-report-comparator-a14/package-manifest-a14.json` | `b8e0422d8c2737009978c7fe2a71c6d5a59430ae116afc399b0bf9c69cad7d31` |
| `text-report-comparator-a14/README-a14.md` | `9640d7439602e26e7d32a52fcfe2e1c78401967e4ff118d3506cef13fd659e10` |
| `text-report-comparator-a14/output-schema-a14.md` | `cb638935ad79e212fd5eaf0a560c32ea49a7b015cbe6c8d386fa72c84bcab04a` |
| `text-report-comparator-a14/source-rationale-a14.md` | `ec9eacbf80364ab18194773a644b8b90da8f6a9c5b7bc3dc59d97bc482cd14bc` |
| A11 comparator source | `e94b6ea3fb671ba66d413594060959bb5ec86f7e4fcffb8e774ababaeb438520` |
| A11 required control | `69c8c96d60b7b8842d6e5f55a564ea23e6853d66c8d06b006e9738e203be809c` |
| A15 source manifest | `0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e` |

The manifest binds six comparator inputs, all 21 A15 source rows, and the
review authority rows. It explicitly excludes the invalid current A11 and A12
manifests. The package remains authored, unbuilt, unexecuted, and unqualified.

## Result

No P1 or P2 finding remains in the A14 source, output schema, rationale, or
manifest. A14 closes the A13 result-count and event-replay blockers.

## Verified source paths

### Exact loader provenance

`load_frozen_comparator` reads one bounded comparator payload, checks descriptor
identity before and after the read, rejects growth, hashes the exact bytes
passed to `exec`, and stores `{path, bytes, sha256}` on the loaded module.
`source_loader_control` requires integer byte count, the fixed path, and the
manifested A11 hash. It does not invent filesystem metadata for loaded bytes.

The fixture font manifest is read through a separate path in `_font_fixture`.
The A14 package manifest and later runner must bind that file and all six input
rows through independent bounded observations. The control source does not
claim that its own `read_text` call is a package-wide input seal.

### A15 source join

`source_join_control` calls the comparator's `_open_joined_a15_manifest` and
requires the frozen A15 manifest hash and exactly 21 joined rows. The package
manifest separately binds the manifest and every referenced source row.

### Current allocation replay

`current_allocation_replay_control` builds a ten-record JSONL fixture with five
reserves, three releases, one write, and one rollback. It solves the write
payload against the event-log byte count, writes report and log exclusively,
and reopens the report through the comparator's `load_report_context`.

The control then calls the actual `validate_swift_report`, active producer gate,
`validate_swift_allocation_log`, and `_reconcile_swift_allocation` functions.
It preserves the reader's raw and canonical event hashes, count, actions,
scratch-inclusive peak, final outstanding bytes, owner totals, and reconciliation
return in the result diagnostic. The fixture is explicitly synthetic contract
evidence and is not native producer evidence.

The event reader owns the descriptor-stability checks. The control closes the
report context after validation. The temporary directory and exclusive writes
keep the fixture isolated from project state.

### Parser and qualification controls

The source includes complete parser and active-gate paths for accepted,
observation-only, rejection, exact-zero, failed-prefix, fractional-prefix,
non-font observation-prefix, and outer-causal-failure cases. It keeps
structural validity separate from native qualification. Observation-only rows
may pass `swift_case_gate_passed` while remaining explicitly unqualified.

The eleven negative controls target omitted fields, disallowed errors, residue,
incomplete prefixes, guard relations, and toggle order. Their expected codes
match the validator order. The three Rust controls check path-independent
stability and reject a changed decoded control digest.

The ordered output contract is schema 3 with 59 results. The source produces
the 59 rows listed in `output-schema-a14.md`, including the preserved outer
failure parser row. The manifest records the same schema and count.

## Compatibility and limits

- A14 keeps the A11 comparator source and A15 source binding unchanged.
- A14 uses integer `loader.bytes`, matching the source and schema.
- A14 changes only the control output schema from the predecessor's stale
  declaration and records the missing 59th row.
- The control does not establish CoreText, CoreGraphics, ImageIO, shaping,
  raster, PNG orientation, allocation behavior of a native producer, playback,
  listening, or creative acceptance.
- Package execution still requires a later runner to reobserve every manifest,
  input, review, and A15 row before and after the child process.

## Review limit

This review did not import or execute any Python source. It establishes source,
contract, and manifest consistency only. It does not establish that the 59
rows pass at runtime or that any native output exists.
