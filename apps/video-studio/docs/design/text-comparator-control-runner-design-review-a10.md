# Comparator control runner A10 review

## Disposition

The A09 observer produced a complete current-filesystem snapshot. The snapshot is
unqualified for comparator, native, image, provider, or creative acceptance.

The saved report contains schema 4, 1,548 current rows, 45 fixed divergences,
995 declared matches, and 508 current rows without RECORD declarations. The
parent readback independently measured 10,997 opens and 69,866,277 read bytes.
It confirmed the report hash, current file identities, RECORD projections,
diagnostic overlay, roots, limits, and unqualified state.

The report and parent evidence remain separate from runtime execution and native
acceptance. No child comparator, native observer, image load, provider-origin,
or creative-acceptance claim is made here.

## Reviewed identities

| Item | Path | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| A09 snapshot report | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/observer-runtime-snapshot-attempt-a09/runtime-snapshot-a09.json` | 2,837,530 | `7a43e5606a49bab8d949444707a132b102326cb86d6236e512e0160ac5dd29e8` |
| Parent readback source | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/readback_runtime_snapshot_a09_parent.py` | 17,722 | `37995d1d1825585c2e2ff083e8edf07349173b46ae89088e3029ca2230019158` |
| Parent preflight | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/observer-runtime-snapshot-parent-preflight-a09.json` | — | `a812ef5cbdf9c6fd4d9f71c608e9c610779184da70e8718ba7d5db0652a63f54` |
| Parent execution evidence | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/observer-runtime-snapshot-parent-execution-a09.json` | 861,763 | `7fb498f6659d2ba89a746c7234cb3a1664151dc171b36b31e998be39565de01e` |
| A10 runner design | `apps/video-studio/docs/design/text-comparator-control-runner-design-a10.md` | 27,406 | `08443a784b95a46b7de7602c4f1e2cac94974026d0b5990c446f03cb5bdd30da` |
| A09 source review | `apps/video-studio/docs/design/text-observer-runtime-snapshot-source-review-a09.md` | — | `57cc2cdd0de0a02e319d2f4d8aa0b67d144df4d8634a9d7c6e329dcafcfdd12e` |

## P1 finding

### Parent readback is assertion-only

`readback_runtime_snapshot_a09_parent.py` uses `assert` for the report hash,
JSON shape, caps, row classifications, path identities, descriptor identities,
and output checks. It does not reject optimized Python or record the optimization
state. Under `python -O`, those checks are removed while the script can still
write an execution record with exit code zero.

This is P1 for any gate that consumes the parent evidence. Replace assertions
with explicit checked exceptions and failure codes. Require the intended Python
flags before opening evidence. Record the exact interpreter invocation and
optimization state in the output.

The observed A09 run itself was invoked with `-I -B` and exited zero. This review
does not infer that it used `-O`; the defect is in the reusable reader source.

## P2 findings

### Preflight input is not bounded or fully bound

The parent reader loads `observer-runtime-snapshot-parent-preflight-a09.json`
with `Path.read_bytes()`. It does not cap this read, hold a descriptor, or check
file identity before and after reading. It also accepts whatever `rows` array is
present. It does not enforce the preflight key set, the seven expected source
rows, or `attemptAbsent` before using the values.

The reader does remeasure each listed row. That is useful evidence, but a shorter
or altered preflight row set can pass its current loop. Use one bounded descriptor
read, validate the exact preflight schema and row set, and preserve the fresh
observations in the result.

### Fresh observations are reported as copied preflight rows

`sourceRowsAfter` is assigned from `preflight['rows']`. The fresh path and byte
measurements are only asserted and then discarded. `sourceRowsAfterMatched` is
set true after those assertions.

The output should distinguish `sourceRowsExpected` from
`sourceRowsAfterObserved`. The latter must contain the rows measured by the
parent readback, including the readback timestamp or phase identity.

### The independent reader is not in its own evidence closure

The parent preflight binds the A09 helper, contract, rationale, overlay,
diagnostic, parent review, and independent review. It does not bind
`readback_runtime_snapshot_a09_parent.py`, its invocation, or its source hash.

Add the parent reader source identity and intended interpreter identity to the
preflight and final evidence. This establishes source provenance. It does not
establish loaded-code attestation.

### A10 still describes the report as absent

A10 lines 45–59 and 688–689 say that the A09 report is pending or absent. The
report now exists at the path above and has the fixed hash shown in this review.
The successor must bind the report path, byte count, and SHA-256 as a completed
input. It must retain the unqualified state.

### A10 names the wrong runtime facets

A10 lines 404–409 refer to “the two A08 runtime facets.” The A09 wire has one
runtime object, distribution observations, record-declaration comparison,
historical path comparison, limits, scope, and the separate 45-row overlay.
Replace the A08 wording with the exact A09 key set and derived phase fields.

### Digest construction is not yet an exact wire rule

A10 requires `report_row_digest` and overlay or phase digests, but it does not
define the canonical bytes, row ordering, string encoding, or delimiter. Freeze
that algorithm before implementation. Otherwise two valid readers can produce
different digest authorities from the same 1,548 rows.

## Finite current-domain review

The proposed A10 domain is finite and suitable for a bounded design. It admits
the current 1,548 regular files, including current RECORD-declared `.pyc` files.
It bounds each file at 128 MiB, each observation at 1 GiB, opens at 65,536,
package rows at 4,096, total rows at 8,192, path bytes at 32 MiB, and serialized
preflight or seal output at 4 MiB. It also bounds child output and aggregate
control evidence.

The four phase observations can each consume the one-gigabyte read budget. A10
must state that the one-gigabyte limit is per phase and must retain separate
phase counters. It must not compare phase counters for byte equality. The A09
helper observed 10,990 opens and 65,536,066 bytes, while the parent readback
observed 10,997 opens and 69,866,277 bytes. Both are valid bounded observations
of changing filesystem metadata, not interchangeable totals.

The 4 MiB preflight and seal limits need a serialized-size ledger before
implementation. The current 2,837,530-byte report fits the report limit, but a
full multi-phase seal has different fields and must be measured before exclusive
publication. The limit is a logical output bound, not an allocator or RSS claim.

## Required A10 disposition

Keep the A09 report and parent evidence as completed, unqualified filesystem
observations. Do not rerun them in this review.

Before A10 implementation, repair the assertion-only reader, bind the reader
source and interpreter, validate and bounded-read the exact preflight wire,
store fresh post-readback rows, update the completed A09 report identity, replace
the A08-facet wording, and freeze digest serialization.

The current evidence supports filesystem identity and RECORD classification only.
It does not support comparator execution, CoreText or ImageIO loading, native
runtime closure, provider origin, or watched, heard, or creative approval.
