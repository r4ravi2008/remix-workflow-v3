# Comparator A05 pure-control wrapper A03 addendum

## Result

`run_comparator_controls_a03.py` closes both P2 findings from the A02 wrapper review.

No P1 or P2 source finding remains within this bounded pure-control scope. Root may execute this exact wrapper after its independent source check.

This was a read-only, same-model-family review. I did not run the wrapper, comparator, control, producer, decoder, or native framework.

## Reviewed identity

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `run_comparator_controls_a03.py` | 6,131 | `165844e8d66c2ec3f0af502fb0c3b20090d7e4a449739fb4908871eddb8a9327` |

## Closed findings

`observe(..., retain=True)` now hashes and retains `control.log` through one descriptor. JSON parsing uses those exact retained bytes.

The initial report now defines `returncode: null` and `timedOut: false`. Every caught failure has total fields for terminal reporting.

The remaining A02 authority, dependency, timeout, and after-state checks are unchanged.

## Scope

A successful run can qualify only the frozen synthetic actual-function controls. The report retains `sourceComparatorGateAccepted: false`.

The run cannot qualify Comparator A05, a native producer, image decoding, text feasibility, or product integration.

The 1 MiB log limit remains a postprocess read cap. Active child log growth remains outside this wrapper's claim.
