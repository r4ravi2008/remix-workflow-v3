# Publication parent comparison A01

The parent read both completed candidates end to end. No source change followed a partial draft.

| Criterion | A | B |
| --- | ---: | ---: |
| Caller depth | 5 | 5 |
| Failure and recovery clarity | 5 | 4 |
| Historical compatibility | 5 | 3 |
| Contention and lease behavior | 4 | 2 |
| Proofability of required ordering | 5 | 4 |
| Total | 24 | 18 |

A is the preferred base. Its availability token closes the receipt-ordering mistake without a new durable state.
A hashes large files outside SQLite, quiesces renewal, and guards every filesystem publication against admitted cancellation and epoch transfer.
A distinguishes available files, receipt CAS, completed ledger publication, and unknown commit outcomes.
A retains legacy finalizing recovery while new writes transition directly from running to completed.
Filesystem residue after rollback remains explicit and cannot alone establish completion.

B provides useful phase and failure terminology. Its checkpoint is private, source-bound evidence rather than a published ArtifactReceipt.
B adds a table, migration, mutable checkpoint phase, stage adoption and new cleanup semantics.
Those changes expand this repair beyond the observed publication-order defect.
B still hashes the final artifact inside the write transaction and implies a bounded window despite blocking sync operations.
B's alive-owner rule changes expiry takeover. Its recovery example mentions a field absent from its sketched checkpoint.
B incorrectly names reconcile_export_staging as the recovery entry point and names the old producer for the fresh rerun.

Mandatory synthesis details: bound small receipt writes, avoid whole-file work under SQLite, revalidate held file identity,
preserve a typed unknown publication outcome, and do not demote completed jobs after observation failure.
Keep exact historical document bytes and retain all original P1 receipts and native observations.
Use a fresh producer and intents after repair. No playback, hearing, creative or full-film acceptance follows this selection.

A SHA256: 0404cd5037176d98f117bf43a07e143cc6f5dec47daa0f7f2e238cee0d141c5f.
B SHA256: 7f258ca1940040fde7984e3e6e0c62b0bd8c4c016b0023e0467c5f1879720c93.
