# Native text report comparator A07 source review

## Result

Comparator A07 is not ready for a native execution gate.

One P1 makes every complete A10 report fail owner reconciliation. The same event-label pattern remains in the forthcoming A11 producer.

Four P2 findings weaken failed-state preservation, disposition typing, owner bounds, and repeat-stability proof.

This was a read-only, same-model-family source review. I did not run a helper, comparator, producer, compiler, decoder, or native framework.

The separately recorded 256 MiB evidence-admission defect is excluded as instructed. This review does not restate or rescore that defect.

## Reviewed identities

| File | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `text-report-comparator-a07/compare_text_reports_a07.py` | 4,852 | 275,708 | `41b655c2e9fdda7f1d9770201b144e26246d4854fdc9187c24503cfd77f299fb` |
| `text-report-comparator-a07/actual-comparator-control-a07.py` | 632 | 36,669 | `d9d70f22567b71646c4374647aabf7bafeef09fcf2ccab5704624a16aa41ed4c` |
| `text-report-comparator-a07/actual-comparator-control-a08.py` | 150 | 5,763 | `465be36bcf26b596725fdcd4c36d0432dd601dff567d5bf84d1de7f17499a05e` |
| `text-report-comparator-a07/required-evidence-control-a07.py` | 216 | 10,627 | `93f12f2aaeed25fff2ca3b9b8db21cf78f16baf6b6f8ea3bf008da084e8d82ad` |
| `text-report-comparator-a07/output-schema-a07.md` | 104 | 11,297 | `1d94a41774320bdafa5fdc896ca382f18430d7cb601d08dc689dbedd9b1f5e80` |
| `text-report-comparator-a07/source-rationale-a07.md` | 59 | 7,628 | `5f6e5971628f454151974319fc4ebb8c9a7d4383367f67674978cde70d34fb99` |

I read the full A07 comparator and both actual-control schedules. I also read the complete package schema and rationale.

I compared A07 with the A10 producer's report construction, allocation ledger, and output schema. I inspected the A11 source manifest and storage correction.

## P1 finding

### P1-1: the result-owner prefix includes temporary serialization leases

A07 classifies every label beginning with `case-result` as a retained result owner (`compare_text_reports_a07.py:2363-2373`).

The classifier therefore includes `case-result-serialization:<case>`. A10 creates this temporary 262,144-byte lease for every case (`probe.swift:4081-4088`).

A10 increments `resultOwnerBytes` only through `reserveResultOwner` and `reserveResultOwners` (`probe.swift:1113-1131`). The generic serialization lease does not increment that counter.

A07 compares cumulative classified reserves with `resultOwnerBytes` exactly (`compare_text_reports_a07.py:4246-4259`). With 15 cases, replay adds 3,932,160 bytes absent from the producer summary.

The reserve and release balance in the signed view. The cumulative owner view still remains 3,932,160 bytes too high.

The A07 actual control tests `case-result-retained:control` and `orientation-result-retained:control` (`actual-comparator-control-a07.py:418-446`). It never tests `case-result-serialization:`.

A11 retains the same `case-result-serialization:` labels. Retargeting constants cannot repair this semantic mismatch.

Classify only producer counter labels. Exclude serialization leases explicitly. Add a control using the complete retained and temporary result-label schedule.

The repair must prove both cumulative counters and signed outstanding balances. A synthetic one-label reserve-and-release control is insufficient.

## P2 findings

### P2-1: a failed later repetition is rejected as malformed input

A10 preserves the first successful repetition when a later repetition fails. Its schema requires the first masks and the later causal failure records (`output-schema.md:172-180`).

The producer sets `rasterPublished` after a successful repetition. A later failure changes the disposition to `failed` without deleting prior success evidence (`probe.swift:3635-3803`).

A07 treats every nonaccepted case like a pre-raster rejection. It requires `rasterPublished == false` and forbids all successful case and repeat evidence (`compare_text_reports_a07.py:3827-3840`).

An honest `completed_with_unexpected_failures` report therefore becomes `input_or_evidence_invalid`. A07 cannot preserve the producer failure as a typed, nonqualifying result.

Model the repeat sequence directly. Permit completed success records before one terminal failed repeat. Forbid success and failure evidence within the same repeat.

Keep case-level first-repeat evidence for a failed-later case. The producer gate must remain false, with the causal report still structurally valid.

Add controls for failure at repetitions zero, one, and two. Include success-before-failure, same-repeat residue, and failure-without-error cases.

### P2-2: declared evaluation kinds do not determine exact disposition labels

A07 permits either rejection label for a declared `rejection` (`compare_text_reports_a07.py:4332-4344`). It also permits either accepted label for supported cases (`compare_text_reports_a07.py:4345-4369`).

The producer's labels encode distinct contract states. `accepted_shape`, `observation_only`, and `rejection` must not share interchangeable labels.

The common projection normalizes any label containing `rejected` to `rejected`. A declared rejection with `observation_only_rejected` can therefore escape as equal evidence.

Require this exact mapping:

- `accepted_shape` success uses `accepted`.
- `observation_only` success uses `observation_only_accepted`.
- `observation_only` allowed rejection uses `observation_only_rejected`.
- `rejection` uses `rejected`.
- Unexpected producer errors use `failed` and remain nonqualifying.

The actual controls exercise normal labels only. Add one negative control for every cross-kind label substitution.

### P2-3: the Swift error validator does not enforce A10 owner bounds

A07 gives error codes, details, evidence keys, and evidence values the generic 64 KiB string limit (`compare_text_reports_a07.py:395-409`).

A10 limits these owners to 128, 1,024, 128, and 3,072 UTF-8 bytes (`probe.swift:44-55`, `3415-3432`).

A07 also permits 128 `partialFace.observedTables` entries (`compare_text_reports_a07.py:375-385`). A10 permits 17 retained table records (`probe.swift:3433-3442`).

A forged schema-five report can therefore pass A07 with owners the A10 producer must reject. These fields are not all projected into common evidence.

The A08 standalone control reaches the real validator at the 23/24 entry boundary (`actual-comparator-control-a08.py:107-128`). It uses only short strings.

Keep the 23/24 control. Add exact boundary and overflow cases for code, detail, evidence keys, evidence values, and observed-table count.

### P2-4: repeat-stability claims are trusted instead of derived

A10 derives `allSupportedRepeatsEqual` from complete repeat masks and digest sets (`probe.swift:3872-3904`, `4103-4110`).

A07 requires the Boolean but does not recompute it. Its Swift gate checks only digest presence and per-repeat mask binding (`compare_text_reports_a07.py:4332-4371`).

The Rust gate checks `shaping_identical` and `dispositions_identical`. It omits the four mask-stability fields and the control-stability map (`compare_text_reports_a07.py:4270-4329`).

A07 opens every raster and compares matching labels across producers. It does not compare repeat zero with repeats one and two inside each producer.

A matching mutation across both reports and both fresh runs could preserve cross-producer equality while contradicting both stability summaries.

Derive repeat stability from the opened summaries. Require equal main and guard rasters across three repeats, plus clip, reference, and controls when scheduled.

Require the three Swift `shapeSha256` values to match. Recompute Rust shape and raster stability from its retained repetition records.

Add repeat-one raster, shape-digest, and control mutations. Each mutation must fail even when copied into every supplied report.

## Confirmed strengths

A07 enforces exact `successfulRaster` roles. `te-basic` requires main, guard, clip, and reference; other successful cases require main and guard.

Every successful mask digest binds to its retained record (`compare_text_reports_a07.py:3770-3794`). Repeat zero also binds to the case-level record.

The scanner opens retained mask files and verifies their stored identities. It rederives guard, clip, reference, binary-control, and difference predicates from pixels.

The A10 source join opens the exact manifest and every named row. It verifies producer, shared callback, bridge, compile-unit, and source-control identities.

The report roots remain held by descriptors. Evidence opens use relative components, `O_NOFOLLOW`, regular-file checks, and duplicate-inode accounting.

The A08 control correctly reaches the actual A07 error validator. It proves only the scheduled 23-entry acceptance and 24-entry rejection behavior in source.

## A11 successor boundary

A07 is deliberately closed to A10. A11 must use a preserved successor with its own exact source branch.

The successor must bind `independent-swift-coretext-a11`, its 15-row manifest, and its exact producer compile units. It must also bind both source-control compile-unit schedules.

The join must include `persisted-output-budget-shared.swift` and `persisted-output-budget-control.swift`. It must verify their manifest rows and caller bindings.

A11 retains schema 5 and the A10 raster graph. The exact successful-raster role and digest validation should remain unchanged.

A11 adds four policy caps: `persistedOutputBytes`, `persistedOutputBoundBytes`, `allocationEventLogBytes`, and `qualificationFileCount`.

Those values bind 512 MiB, 396,071,265 bytes, 16 MiB, and 201 files. The comparator must not silently reinterpret A10 caps as A11 caps.

The owner-classifier repair must precede either A10 use or A11 retargeting. The known total evidence-admission repair remains a separate recorded requirement.

## Verification boundary

This review establishes source findings only. No actual A07 control result exists from this review.

No A10 or A11 native report was supplied or executed here. Native feasibility, cross-language equality, and text acceptance remain unverified.
