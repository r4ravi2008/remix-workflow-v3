# Specification audit

The independent reviewer used `gpt-5.6-sol`. The reviewer read the saved files and examined actual hashes and inventory.
Cross-family review was unavailable. The review does not claim runtime or provider verification.

The reviewer found no P0 specification gaps that prevented completion after these corrections.

| Finding | Saved correction |
| --- | --- |
| Artifact lookup and caller-authored receipts had unclear authority | Verification uses project ID and artifact ID. Rust loads the authoritative artifact receipt. |
| Structured hashes lacked exact bytes and versions | The specification gives JCS inputs, identity version, and raw byte hashes. |
| Create, edit, and render replay were not equally specified | Each mutation uses an intent contract and explicit interruption points. |
| The process boundary lacked exact envelopes | The specification gives request, success, error, schema handshake, and exit-code rules. |
| Acceptance evidence was confused with artifact evidence | Separate acceptance-case receipts bind cases, owning builds, verifier, and evidence files. |
| Risk of feature progress that disagreed with executability | Compiled owner registries and current acceptance results give the state. A ledger edit cannot enable tools. |
| Ownership and phase metadata conflicted with the specification | The ledger assigns Rust, Effect, and Foldkit primary owners and enforces prerequisite phase order. |
| Broad references appeared to specify exact contracts | Core entries refer to the specification that the project owns. Blackmagic links are explicitly capability-family references. |
| Risk of implementation files or symlinks that the checker did not find | The checker enforces the exact specification inventory and rejects symlinks. |
| Some decision inputs were not bound to the check | The checker calculates hashes of both candidate artifacts and the saved baseline. |

At the time of this audit, the reviewer confirmed that all 81 capabilities remained planned without runtime evidence.
The reviewer confirmed that all 21 P0 case IDs had assignments. Dependencies had no cycles and agreed with the phase order.
At the time of this audit, the reviewer confirmed that the native runtime source tree was absent.
The reviewer ran `node --check` on the document checker.

The scoped comment review found zero comments and zero suppressions in `check-spec.mjs`.
The review did not delete or restore comments. The dedicated Cursor Comment Sicko agent type was unavailable in Codex.
This manual role review was part of the independent audit.

At the time of this audit, these items remained unverified:

- Native codecs and acceptance corpora.
- Schema import and crash-recovery behavior.
- Hosted storage, cloud deployment, and GPU execution.
- Playback, listening, and creative review.

The structural receipt for the specification establishes document structure only.
