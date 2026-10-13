# Publication grounding A01

The current source creates an ArtifactReceipt after staged encoding, sync, source checks, native verification and hashing.
It stores that receipt in CAS before the guarded running-to-finalizing UPDATE.
The UPDATE guards epoch, running state and cancellation. A separate immediate transaction then checks epoch/cancel before hard-link promotion.
The final transaction completes the job and attempt. A fresh verification follows completion.

Actual cancelled and fenced controls reached the pre-guard store_document call and left orphan ArtifactReceipt3 documents.
Their final .mov paths are absent. Their ledger/response receipt fields remain absent. No stale artifact was promoted.
This is a publication-order defect, not an encoder or pixel failure.

Relevant ownership and recovery facts:

- The new writer is export-thread-owned and starts before source workers.
- ExportControl renews through a Rust worker every10seconds. SQLite connections use a5second busy timeout.
- Job leases expire after240seconds. SQLite uses WAL and synchronous FULL.
- A failed renewal can set lease_unavailable in ExportControl.
- store_document writes immutable JSON through an exclusive temp file, sync, hard-link and directory sync.
- The final artifact link is content-addressed. Existing destinations require full blob verification.
- The current finalizing job contains a StoredArtifact wrapper before promotion.
- Recovery verifies a referenced promoted artifact when present. An absent artifact triggers a fresh owned render.
- Reconciliation derives payload names only after validating the stored immutable plan.
- Known retired dead stages can be reclaimed. Unknown, mismatched or unowned files remain retained.
- Stage Drop removes only the matching owner and expected payload.

Publication repairs must retain the existing exact receipt documents and legacy recovery reader.
New failed-attempt evidence must be distinguished from a published ArtifactReceipt.
Neither filesystem CAS objects nor an in-progress ledger state alone establish a completed export.
Cross-filesystem/SQLite crash outcomes require explicit recovery classification rather than a blanket atomicity claim.

The A01 native lifecycle audit is preserved. The frozen code-only review's no-receipt-publication assertion is disproved.
The main A01 master plans have not exported. Root will use a fresh producer and intents after the selected repair.
