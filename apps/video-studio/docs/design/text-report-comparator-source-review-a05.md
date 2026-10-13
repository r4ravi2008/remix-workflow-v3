# Native text report comparator A05 source review

## Result

Comparator A05 is not ready for a native execution gate.

The A05 changes close the four A04 parent findings in source. However, the complete schema-five path still has one P1 and three P2 findings. The bounded actual-function control also failed during the root-owned run.

This was a read-only, same-model-family review. I did not run the comparator, either producer, a native framework, an image decoder, or a control.

## Reviewed identities

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `text-report-comparator-a05/compare_text_reports_a05.py` | 264,084 | `cc320836984bf9d1e303cd9c1da8d876e2d4a60edf0616d32913953e32a05ebb` |
| `text-report-comparator-a05/actual-comparator-control-a04.py` | 29,110 | `3ca5a6d443030797c552f1fcc5f2eaa54bf0ff7ff1d05616da3f47e410b8e157` |
| `text-report-comparator-a05/required-evidence-control-a05.py` | 10,627 | `02c7e47f8fc42a943136eaf0f7057288fcdbea5d6a9c42f5a713c7fe0d99aa63` |
| `text-report-comparator-a05/output-schema-a05.md` | 10,156 | `09656dea78e992f0c59fb5d88df776d9b8f142513bc77e0e0adab865a57eb356` |
| `text-report-comparator-a05/source-rationale-a05.md` | 6,306 | `29d71c4e695b8854da00d21887ddc53a6302bccdea9fb7dba0aec0170134f8dc` |

I also rehashed the referenced Swift A07 source manifest, probe, and shared callback source. Their hashes match the A05 constants.

## Closed A04 findings

The A05 owner classifier includes `orientation-result` under the result owner. Its cumulative and signed accounting still reconcile separately (`compare_text_reports_a05.py:2356-2394`, `2407-2506`, and `4083-4107`).

The actual control registers its temporary module in `sys.modules` before executing the frozen source. This supports the comparator's dataclass definitions (`actual-comparator-control-a04.py:64-81`).

The repaired positive Swift fixture publishes case-level clip and reference fields only for `te-basic` (`actual-comparator-control-a04.py:210-246`).

The observation-only rejection gate now allows causal shape and `failureRaster` records. It rejects successful raster records, controls, and native images (`compare_text_reports_a05.py:4225-4240`).

These are source observations. The failed control run does not independently validate all four repairs.

## P1 finding

### P1-1: Swift success and failure evidence are not mutually exclusive

The schema-five validator accepts `failureRaster` on any repeat. It validates the records without checking the repeat state (`compare_text_reports_a05.py:3620-3631`). The A07 validator rejects `successfulRaster` on a failed repeat, but it does not reject `failureShape` or `failureRaster` on a successful repeat (`compare_text_reports_a05.py:3661-3708`).

The ordinary rejection branch returns after checking one failed repeat and its digest fields (`compare_text_reports_a05.py:4173-4181`). The added residue checks apply only to `observation_only_rejected` (`compare_text_reports_a05.py:4225-4240`). An ordinary rejected case can therefore retain case-level main, guard, clip, reference, comparison, or native-image records.

These contradictions can survive qualification. Common cross-producer projection ignores case-level mask objects and success-side failure records. Failure masks are compared only between the Swift primary and fresh runs (`compare_text_reports_a05.py:4442-4454`). Matching contradictory records can therefore leave `differences.total == 0` and the producer gate true (`compare_text_reports_a05.py:4496-4502`).

Enforce one explicit case-and-repeat state machine before projection:

- A successful repeat must have `successfulRaster` and no error, `failureShape`, or `failureRaster`.
- A failed repeat may have causal `failureShape` and `failureRaster`. It must have no success digests or `successfulRaster`.
- Every rejected case must have no case-level success masks, comparison, controls, or native image.
- Every accepted case must have no case-level error and no failed-repeat residue.

Add positive and negative controls for each state. A matching primary/fresh pair must not make contradictory state valid.

## P2 findings

### P2-1: Non-`te-basic` repeat evidence can publish clip and reference roles

The case gate forbids case-level clip and reference fields outside `te-basic`. The repeat loop only requires those roles for `te-basic`; it has no inverse rejection (`compare_text_reports_a05.py:4194-4203`).

The schema-five raster validator allows optional clip and reference records for every case (`compare_text_reports_a05.py:3648-3658`, `3672-3698`). A non-`te-basic` repeat can therefore carry clip/reference digests, predicates, and retained records.

The current cross-label comparison prevents this malformed input from reaching an equal final state. Rust forbids those roles, so the extra Swift labels become a difference (`compare_text_reports_a05.py:4662-4670`). The schema still contradicts its declared exact-role contract.

Require the exact role set at both levels. `te-basic` requires main, guard, clip, and reference. Every other successful case requires only main and guard. Reject the matching digest and predicate fields when clip roles are forbidden.

### P2-2: The actual-function control is failed and does not cover A05's central additions

The root-owned control run preserved `comparator-actual-control-a01/report.json`, SHA-256 `6f21fa2595b2e173ff332c8da428c4e87a6be48fb71c6356de37d2c282f2c1b9`. It returned one at `guard-relation-positive`. The log SHA-256 is `bff8acf3fa0dea95167e49576a26c60f97c94eb2a7ca379cf7f6d2e12ae50f62`.

The synthetic relation summaries place the inner row digest at array index zero (`actual-comparator-control-a04.py:288-296`). The actual relation function slices guard rows from index 32 and reference rows from index 64 (`compare_text_reports_a05.py:4589-4625`). The positive fixture therefore cannot pass.

The control also leaves two A05 repairs uncovered:

- Its result-owner event uses `case-result-retained`, not `orientation-result-retained` (`actual-comparator-control-a04.py:399-418`).
- Its positive Swift cases contain digest strings without `successfulRaster`. They call only `_require_swift_case`, so they never exercise the schema-five retained-record and digest binding (`actual-comparator-control-a04.py:210-246`, `451-478`).

The successor control must use full outer-height row-digest arrays with the inner rows at offsets 32 and 64. It must directly cover orientation-result reserve and release. It must also cover valid and invalid `successfulRaster` role, digest, and first-repeat bindings. Add the P1 state controls and the non-`te-basic` role negative.

Preserve the failed A04 control and its root runner report.

### P2-3: The A07 source-manifest hash is declared, not verified by this package

`SWIFT_A07_MANIFEST_SHA256` is defined once and copied into the output (`compare_text_reports_a05.py:3303`, `4514`). The comparator never opens that source manifest. Report validation checks the declared probe and shared-source hashes, while `manifestSha256` refers to the font manifest (`compare_text_reports_a05.py:3754-3780`).

The contracts say A05 binds the A07 source manifest (`output-schema-a05.md:7`, `104`; `source-rationale-a05.md:7`). Inside this package, that hash is only a declared expected identity.

The future outer gate must open and hash the complete accepted Swift source manifest. It must join that manifest to the report's probe and shared-source hashes. The result should label this value as externally bound or declared until that join exists.

## Compatibility and execution boundary

A05 accepts only Swift A07 schema 5. The pending Swift A08 source cannot use this comparator through a renamed report or a hash substitution. A preserved successor must bind the exact accepted A08 producer, schema, source manifest, and shared source.

The comparator main entry point remains unexecuted. The actual-function control result is failed. No native producer, CoreText, CoreGraphics, ImageIO, or PNG decoder ran during this review.

The package cannot support a native gate until P1-1 is repaired. The P2 schema and control repairs should ship in the same preserved successor. Native feasibility and product acceptance remain false.
