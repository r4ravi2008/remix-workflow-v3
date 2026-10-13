# Selected publication repair A01

Status: selected; implementation and native proof pending.

Use Candidate A with publication-judgment-a01.md as the contract. The parent and judge both scored A24/B18.
Keep public Project operations, serialized receipts, plans, and database schema unchanged.
Add a private publication module. SealedStage owns the hashed descriptor and ExportStage cleanup authority.
PublicationGuard orders admitted cancellation and fencing against final linking, receipt creation, and the completed commit.
AvailableArtifact is the sole authority for constructing and storing an ArtifactReceipt.
New attempts transition running to completed. Legacy finalizing recovery retains its existing receipt and verifies the final outside SQLite.
Stop lease renewal, join it, then renew and validate the exact request, plan, owner, epoch, job and attempt.
Whole-file hashing and native verification stay outside the writer lock. Existing final-file races permit at most three retries.
Artifact visibility, receipt visibility and SQLite completion are separate events. Rollback can retain filesystem evidence.
Commit errors require fresh readback. Unknown outcomes retain ownership evidence and bypass failure closure.
Use B's crash-prefix vocabulary and negative controls. Reject checkpoint migration, receipt drafts, stage adoption and new finalizing writes.
Keep only private types that enforce these invariants. Fold nominal ticket/binding markers into input records and the guard.
Freeze a new producer and use new intents after repair. Preserve all A01 evidence, including both orphan receipts.
