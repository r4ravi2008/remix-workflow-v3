# Comparator A13 allocation-log review addendum

Status: independent source-only addendum. This preserves
`text-report-comparator-source-review-a13.md`. A13 remains unbuilt,
unexecuted, and unqualified. No comparator import, control, compiler, native
framework, media, GPU, Resolve, or helper process ran.

## Reviewed identities

| File | SHA-256 |
| --- | --- |
| `text-report-comparator-a13/actual-comparator-control-a13.py` | `4ac29f6f708938059f19f00f574a6212828c22873daa80e1d3d915c3ed4c8100` |
| `text-report-comparator-a13/package-manifest-a13.json` | `239e9f7be13cd63a4058b9b64f245185939840362650d9e1e212281424b2a01e` |
| `text-report-comparator-a11/compare_text_reports_a11.py` | `e94b6ea3fb671ba66d413594060959bb5ec86f7e4fcffb8e774ababaeb438520` |
| preserved A13 review | `6465c6389e460404cc139de646e6bb93be8868c119562af871ea012202f7b5fad` |

## P1: the current allocation control bypasses the actual event-log validator

`current_allocation_replay_control` at A13 source lines 458–529 builds eight
in-memory tuples. It updates `outstanding`, `peak`, owner totals, and a list of
diagnostic transitions. It then sets `environment.allocationEventCount` to 8
but sets `environment.allocationEventBytes` to 0 (lines 501–502). It calls
`validate_swift_report` and `_reconcile_swift_allocation` (lines 503–511).
It never calls `validate_swift_allocation_log` and never creates `events.jsonl`.

This matters because `validate_swift_report` calls only
`_validate_a10_allocation_shape` for allocation fields. That shape check binds
the summary fields, caps, and `eventLogBytes` to the zero environment byte
count. `_reconcile_swift_allocation` then accepts the caller-supplied replay
dictionary. Neither function parses or opens an allocation event file.
Therefore the accepted A13 result can prove only that a hand-built summary
matches another hand-built summary. It does not prove the source's JSONL
reader, descriptor evidence, event transitions, or file accounting.

The frozen A11 `validate_swift_allocation_log` is materially stricter. It calls
`ReportContext.open_evidence` for the declared path and byte count, checks the
held file size, streams and hashes the descriptor, requires newline-terminated
records, and rejects growth. Each record must have exactly the typed fields
`index`, `label`, `action`, `bytes`, `outstanding`, and `writtenFiles`. The
validator checks sequential indices, per-record scratch limits, reserve and
release underflow, write and rollback file totals, baseline retention, event
count and byte bindings, final outstanding bytes, `writtenFilesBytes`, peak
bytes, owner totals, and canonical event hashes (A11 lines 2448–2529).

A13's tuples do not contain the required `outstanding` or `writtenFiles`
record fields. They exercise no `write` or `rollback` action. They do not test
JSON decoding, final-newline handling, descriptor stability, raw/canonical
hashes, event-record limits, or the relation
`written_files + event_log_bytes == writtenFilesBytes`. The source rationale
correctly calls the sequence synthetic evidence, but the control still labels
the result accepted without the required adjacent real-log control.

## Required A14 successor boundary

A14 must retain the current-allocation semantic intent while constructing a
bounded, private `events.jsonl` fixture through the same source-defined record
shape consumed by the comparator. The fixture must include at least one
reserve/release owner transition and explicit write/rollback accounting, with
every line carrying all six validator fields. Derive the report summary,
event count, event byte count, allocation `eventLogBytes`, peak, final
outstanding, owner totals, and `writtenFilesBytes` from that exact fixture.

The control must create the private evidence context and call
`validate_swift_allocation_log` on the fixture. It may then pass that returned
replay to `_reconcile_swift_allocation`, but it must not synthesize a second
replay dictionary. The accepted diagnostic should retain the validator's raw
SHA-256, canonical-events SHA-256, bytes, event count, first transition, peak,
final outstanding, written-file payload, owner totals, and owner-net totals.

The successor should also keep bounded negative cases for malformed JSONL,
wrong event count or byte binding, a missing final newline, a transition
mismatch, and a record exceeding the event-scratch allowance. Each negative
must report the validator's specific contract error. These controls stay
source-only and must not imply native execution.

The successor must also resolve the separate original A13 result-count issue.
The source emits 59 result rows while the A13 output schema and manifest bind
58. The accepted schema, manifest, ordered names, and runner expectation must
all bind the exact 59-row result after the new allocation-log row is included.

## Review limit

This addendum does not establish comparator execution, event-log execution,
native shaping, loaded-image identity, media support, playback, listening,
GPU use, Resolve behavior, or creative acceptance. It identifies a source
control gap that blocks qualification until an A14 successor is reviewed and
then run under its own bounded evidence policy.
