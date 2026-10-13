# Retained-driver supervisor A02 ROOT source review

State: **source accepted within its stated boundary; peer review pending;
unimported and unexecuted**.

ROOT read the complete 33,116-byte supervisor, contract, rationale, and manifest.
The unchanged A04 dependency's relevant launch, wait, publication, bounded read,
descriptor closure, and absence functions were read during A01 review.
ROOT independently reopened all nine current manifest, source, and external
files through held no-follow descriptors. Every byte count, digest, aggregate,
and all nine before/after identity fields matched. No package code was loaded.

## Exact frozen subject

- Manifest: 3,672 bytes, SHA-256
  `e55383c79f58ac3651795b34aee2431f223088f7800a67ca6edf4fa79c9acb11`.
- Supervisor: 33,116 bytes, SHA-256
  `50600911ab331f2c2a03ea814f3783a83007e9b647318a8fe74d7ef3b477a863`.
- Source aggregate: 3 rows, 39,684 bytes, SHA-256
  `7eb84204ce205019218398c4ab41cdced99bfca59d961f53bceaca80122f0f98`.
- External aggregate: 5 rows, 62,478 bytes, SHA-256
  `38bf98df446605a0daea9160db0ca344b3d696dd9b27ad32e34fc7753b091209`.

## Four-group disposition

No remaining P1 or P2 was found within this source boundary.

Known terminal facts now return without a numeric-PID signal. A fresh poll
guards the remaining stopped-child signal. A failed observation revokes signal
authority and retains the owner. The three-second pre-resume observation guard
publishes unresolved evidence without releasing the child or its authorities.

The actual pinned A04 method has one OS operation after setting
`sigcontAttempted`: `os.kill(pid, SIGCONT)`. Its later dictionary update performs
no OS operation. The A02 stopped-child branch requires an actual `OSError`, an
observed stop, attempted SIGCONT, and both delivery and resume false. This exact
source dependency therefore distinguishes failed delivery. Other uncertain
attempts enter retained polling and draining without destructive signals.

Driver success now requires a strict integer zero return code. Nonzero exits
set a failure and preserve physical outer closure as a separate fact.

Pre-resume unresolved and failure records preserve actual launch, signal,
terminal, descriptor, and publication facts. Group evidence stays null until
the actual private-group observation succeeds. Failure records explicitly
describe observation or held-descriptor boundaries rather than completion.

The contract requires an external source and operation gate before import.
Import still executes the exact measured A04 dependency. No gate is created by
the module. Actual callers need separate source review before using it.

## Remaining gates and limits

The post-resume path retains the driver through terminal wait, PID absence,
verified group absence, and both stream EOF observations. It closes authorities
after this boundary. This is a source observation, not runtime proof.

The source cannot accept nested closure. Future callers must inspect actual
nested reports and process absence separately. Forced supervisor termination,
host termination, interpreter failure, and unbounded kernel calls remain
outside the stated closure claim. Native, product, media, watching, hearing,
and creative acceptance remain false. Peer review and caller gates are pending.
