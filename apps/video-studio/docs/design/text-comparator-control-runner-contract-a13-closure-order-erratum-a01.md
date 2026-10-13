# A13 closure-order erratum

## Status and authority

This is a compact additive erratum for the frozen A13 contract. It does not
edit the A13 contract or regenerate its source-closure manifest.

The original contract is bound by SHA-256
`f09b1ae8a8cc9dbbdf2166c386901e70a5d0d75166050cfb5602ebea61dd0603`.
The frozen closure is bound by SHA-256
`7131ee06d72c255442ee30f6e00f6d9ea93c13f28bd929883af398256c3f25a9`.

The closure contains 60 unique rows and 7,504,476 bytes. Every row has nine
recorded size or filesystem identity values. Root and judge readback found no
aliases. These facts are preimplementation filesystem evidence only.

## Correction

The A13 contract's numbered source-closure blocks total 58 rows. That count
omits the historical A09 parent preflight and the A03 reader tool result.
It also places the A03 scoped acceptance review inside the A03 block.

The frozen 60-row closure is the authoritative order for this A13 snapshot.
Its first five rows are the A10 design, A11 wire, A12 design, A12 review, and
A12 A03-binding erratum. Row 6 is the A03 scoped acceptance review. Rows 7
through 13 are the seven A09 rows, including the historical A09 parent
preflight at row 13. Rows 14 through 19 are the six A03 rows, including the
A03 reader tool result at row 18. Rows 20 through 35 are the A14 manifest,
nine manifest files, and six manifest inputs. Rows 36 through 57 are the A15
manifest and its 21 files. Rows 58 through 60 are the A13 recipe, vector
artifact, and contract.

The exact 60-row sequence is:

```text
01 apps/video-studio/docs/design/text-comparator-control-runner-design-a10.md
02 apps/video-studio/docs/design/text-comparator-control-runner-design-a11.md
03 apps/video-studio/docs/design/text-comparator-control-runner-design-a12.md
04 apps/video-studio/docs/design/text-comparator-control-runner-design-review-a12.md
05 apps/video-studio/docs/design/text-comparator-control-runner-design-review-a12-erratum-a01.md
06 apps/video-studio/docs/design/text-runtime-readback-parent-scope-acceptance-a03.md
07 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/freeze_observer_runtime_a09.py
08 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/observer-runtime-snapshot-contract-a09.md
09 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/observer-runtime-snapshot-rationale-a09.md
10 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/observer-runtime-snapshot-attempt-a09/runtime-snapshot-a09.json
11 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/runtime-record-declaration-diagnostic-a01.json
12 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/observer-runtime-record-divergence-overlay-a09.json
13 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/observer-runtime-snapshot-parent-preflight-a09.json
14 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/readback_runtime_snapshot_a03_parent.py
15 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/readback-launch-receipt-a03.json
16 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/observer-runtime-snapshot-parent-preflight-a03.json
17 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/observer-runtime-snapshot-parent-execution-a03.json
18 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/readback-runtime-a03-tool-result.json
19 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/readback-runtime-a03-root-postcheck.json
20 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/text-report-comparator-a14/package-manifest-a14.json
21 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/text-report-comparator-a11/compare_text_reports_a11.py
22 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/text-report-comparator-a11/required-evidence-control-a11.py
23 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/text-report-comparator-a11/original-snapshot-root-reviewed-a11/README-a11.md
24 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/text-report-comparator-a11/output-schema-a11.md
25 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/text-report-comparator-a11/source-rationale-a11.md
26 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/text-report-comparator-a14/actual-comparator-control-a14.py
27 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/text-report-comparator-a14/README-a14.md
28 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/text-report-comparator-a14/output-schema-a14.md
29 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/text-report-comparator-a14/source-rationale-a14.md
30 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/synthetic-text-cases-a02.json
31 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/font-fixtures-a01/manifest.json
32 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/input-authority-a01.json
33 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/font-fixtures-a01/OFL.txt
34 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/font-fixtures-a01/NotoSansTelugu-Regular.ttf
35 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/font-fixtures-a01/NotoSansDevanagari-Regular.ttf
36 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/source-manifest-a15.json
37 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/probe.swift
38 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/persisted-output-budget-shared.swift
39 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/png-consumer-shared.swift
40 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/png-consumer-control.swift
41 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/persisted-output-budget-control.swift
42 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/terminal-publication-control.swift
43 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/failed-publication-control.swift
44 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/output-schema.md
45 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/source-rationale.md
46 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/allocation-ledger.md
47 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/png-consumer-control-schema.md
48 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/persisted-output-budget-control.md
49 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/terminal-publication-control.md
50 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/failed-publication-control.md
51 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/protocol-bound-correction-a11.md
52 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/protocol-bound-correction-a12.md
53 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/protocol-bound-correction-a14.md
54 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/protocol-bound-correction-a13.md
55 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/contract-correction-a10.md
56 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/alpha-context-shim.h
57 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/protocol-bound-correction-a15.md
58 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/canonical_vectors_a13_recipe.py
59 artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/canonical-vectors-a13.json
60 apps/video-studio/docs/design/text-comparator-control-runner-contract-a13.md
```

Rows 20 through 35, and rows 36 through 57, retain the nested manifest order
stored in the frozen closure. The order correction is metadata only. It does
not alter any row bytes, row SHA, vector, contract, or closure content.

## Future binding boundary

The current 60-row closure is a preimplementation expectation. It does not
include a future runner, shared comparator module, new source-control files,
the erratum itself, an external authorization, or runtime output.

Before authorization, the future runner must open and hash the future
runner/shared-module source rows and this erratum in a separately bound source
closure. It must not silently treat the current 60 rows as complete for those
later files. The current closure remains addressable by its original SHA.
