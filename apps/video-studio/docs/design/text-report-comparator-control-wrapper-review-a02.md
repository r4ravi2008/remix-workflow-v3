# Comparator A05 pure-control wrapper A02 review

## Result

`run_comparator_controls_a02.py` is not ready for the root-owned bounded run.

The wrapper has no P1 finding. Two P2 findings affect failure reporting and the authority of parsed control results.

This was a read-only, same-model-family source review. I did not run the wrapper, comparator, control, producer, decoder, or native framework.

## Reviewed identities

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `run_comparator_controls_a02.py` | 6,010 | `fc7bb163b08c855042ae0246009cfda077bd4d14083547815990d82818a6c577` |
| `text-report-comparator-a05/actual-comparator-control-a05.py` | 30,396 | `6a2d86c224a2e1f9fa81748868e585d88642e1cef027a484182bac456d526551` |
| `text-report-comparator-a05/compare_text_reports_a05.py` | 264,084 | `cc320836984bf9d1e303cd9c1da8d876e2d4a60edf0616d32913953e32a05ebb` |

The package document and required-control hashes also match the wrapper constants.

## Source findings

### P2-1: parsed control bytes are not the observed log bytes

The wrapper observes `control.log` through one bounded descriptor at line 59. It then reopens the pathname with `read_bytes()` at line 61.

The parsed controls therefore lack an exact join to the saved log observation. A pathname replacement between those reads can change the evaluated bytes.

Read, hash, and parse one bounded byte buffer from one descriptor. Save that same hash and identity as `r.log`.

### P2-2: an early wrapper failure can break its terminal report path

The initial report object has no `returncode` or `timedOut` fields at line 53. Some exceptions can occur before either field is assigned.

The exception branch preserves `report.json`. The final print then indexes `r['returncode']` at line 77 and raises `KeyError`.

Initialize both fields before entering the run block. Use total report fields for every failure state.

## Correct fixture and bounded scope

The A05 control now pads guard and reference row summaries to offsets 32 and 64. It also exercises `orientation-result-retained` reserve and release.

The exact frozen control source makes a zero return code meaningful. Every scheduled positive and negative check must complete before its main returns zero.

The wrapper correctly retains `sourceComparatorGateAccepted: false`. It does not invoke the comparator main entry point or a native producer.

Its 1 MiB log limit is a postprocess read cap. The wrapper does not bound active child log growth.

The wrapper rechecks ten source/runtime rows and 1,042 installed Pillow and NumPy files before and after the child.

## Disposition

Repair both P2 findings in a preserved successor before execution. Then the wrapper can qualify only the corrected synthetic actual-function controls.

The run cannot qualify Comparator A05, native text feasibility, image decoding, producer execution, or product integration.
