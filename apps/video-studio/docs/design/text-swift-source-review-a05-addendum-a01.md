# Swift native text probe source review A05 addendum A01

## Scope

This addendum preserves the frozen A05 review at SHA-256 `e3ff8dec0441066d006ce95c8b1823fba9f911bbbb48e4c66df1da71e7ba7ebc`.

Later source inspection found one additional P1 blocker and one additional P2 evidence defect.

The Swift A05 package remains source-only, unbuilt, unexecuted, and unchanged.

## P1 — retained `CaseResult` ownership exceeds the charged envelope

`CaseResult` retains nested shapes, masks, controls, repeats, errors, strings, arrays, and native-image records at `probe.swift:460–479`.

`reserveResultOwners` charges a caller-supplied byte count at lines 1010–1013.

The caller derives that count from the fixed `MemoryLayout<CaseResult>.stride` at line 3040.

That fixed stride excludes heap storage owned by the nested values.

The temporary `case-result-serialization` reservation at lines 3065–3073 ends before `results.append(result)` at line 3074.

The nested result storage remains live after that reservation ends.

`output-schema.md:209–213` says the envelope and result owner cover retained results.

The source does not charge the complete retained ownership described by that contract.

This violates the 4 MiB retained-evidence cap and 16 MiB live-allocation cap before native execution can qualify.

Measure every retained nested owner before `results.append`.

Transfer those charges into a result owner that lives exactly as long as the retained value.

Reject the result before append when the complete checked sum exceeds either cap.

## P2 — setter controls cover only the first repetition

The main drawing loop runs three repetitions at `probe.swift:2690–2844`.

The setter controls run only when `repeatIndex == 0` at lines 2778–2796.

`text-probe-protocol-a01.md:90–91` requires every complete supported draw three times in fresh contexts and buffers.

One case-level toggle record cannot bind three independent control draws.

It cannot preserve each control's raw mask, canonical mask, hash, count, or bounds.

Run every setter control for all three repetitions.

Retain the repetition index and complete raw and canonical observations for each control draw.

Compare controls without copying repeat-zero evidence into later repetitions.

## Updated disposition

The frozen review's two P1 blockers and three P2 defects remain valid.

This addendum raises the total to three P1 blockers and four P2 evidence defects.

Repair a separate successor. Re-review its complete source and contracts before any build or native call.

This addendum records source findings only. It does not establish Swift API compatibility or native feasibility.
