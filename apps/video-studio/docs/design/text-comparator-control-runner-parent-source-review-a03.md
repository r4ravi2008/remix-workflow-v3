# Comparator control runner A03 — parent source review

Root found no new P1/P2 within the five selected source repairs. A03 is frozen
and unexecuted. Independent source review and no-child controls remain pending.
This source result does not qualify the runner or its child controls.

## Reviewed source and identities

Root read the complete A02-to-A03 changed-source delta and the full source seams
covering receipts, attempt creation, capture summaries, seals, inventory,
post-seal rejection, and final cleanup. Root read all three A03 documents and
the complete manifest. The ordinary delta reconstruction matches all 59 changed
blocks and the complete 3,487-line source.

The four A03 package rows match their byte counts and SHA-256 values. All twelve
rows across preserved A01, A02, and A03 packages still match.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| run_comparator_controls_a03.py | 174446 | f5a2b4c74d8a6658c3c1e299f41fbb44d59a78d7648dfeb686a183258819f95a |
| runner-contract-a03.md | 11073 | 9e418a76c8ff10b5b652e59f7f07e5d6f005072fee23d87da4efbd0eecaac35b |
| output-schema-a03.md | 4557 | 5c303d76d53c0bb6ee40835e5c9a3f93b53857d538b61e2ae6f546af2cb5fa45 |
| source-rationale-a03.md | 4054 | 4cb1c722835e18d233dcbf73e65c169c413426b01d0653200edd4446afdb1eb3 |
| source-package-manifest-a03.json | 4114 | 3168af7ddd7e43b36dc8962b0caa1583dbc2f8f8fd099e2eb12e38233f3f9054 |

## Selected repairs

The control and failure reports retain the complete capture. capture_summary
removes the event array and error text while retaining bounded event accounting,
stream hashes, timing, group observations, and terminal facts. build_seal_value
requires its measured report reference to equal the corresponding entry in
entriesBeforeSeal. Available prelaunch and post-child domains remain complete.
The 4 MiB seal and 1 MiB report caps are unchanged. An actual maximum fixture
control is still required to verify their combined representation.

SourceClosureAuthority retains each measured closure receipt. Later runner,
codec, and manifest reads join the closure receipts and authorization receipts
recursively. The join includes content, nine stat fields, and four path checks.
The authorization wire now carries those complete receipts. Source reads remain
current filesystem observations without loaded-image attestation.

The success and failure paths check the expected inventory before sealing.
Both paths check the final inventory again. After a completed seal write,
classify_post_seal_failure produces terminal outer failure. It preserves the
exclusive files and does not enter the earlier-ranked failure publication path.
A partial seal write still remains incomplete publication, without qualification.

AttemptPublisher.create tracks its raw descriptor before constructing the held
child directory. Setup failure closes either the raw or transferred descriptor.
It records whether exclusive creation, descriptor identity, pathname equality,
and empty inventory were observed. It preserves incomplete directory evidence
and never deletes an unverified path.

Final cleanup collects publisher and unit-root close failures independently.
One failed close cannot suppress the other close attempt. A cleanup failure
invalidates the prepared result through terminal outer failure. Existing
published evidence is not rewritten.

## Retained boundaries

The four A01 repairs remain: concrete Path values, integer nanoseconds,
PID-derived group ownership before live getpgid, and recursive exact types.
Fixed children, caps, seven-name union allowlist, bounded waits, and six-value
environment remain unchanged. Successful cleanup covers the direct child and
pipes. descendantsReapedAttested remains false.

The exact fixed -I -B invocation is an external root-launch requirement.
No new generic launcher or wrapper is needed. External closure, authorization,
control source, control reviews, and final parent readback remain uncreated.

No target module, codec, helper, source control, compiler, child, native,
media, GPU, or Resolve process was imported or run. No listening, watching,
provider provenance, or creative acceptance was established. Rust native
producer qualification remains independent of comparator evidence.
