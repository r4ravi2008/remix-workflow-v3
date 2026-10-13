# Owned artifact publication repair: candidate B

Status: design only. Candidate B adds a durable, source-bound staged-evidence checkpoint. It does not change the native mastering contract or claim SQLite and the filesystem are atomic.

## Usage (caller's view)

The public surface stays `Project::prepare_export`, `export`, `verify_export`, `cancel_export`, and `reconcile_export_staging`. A mastering caller still submits the existing profile:

```json
{
  "intent": "export-active-cancel-a01",
  "revision": "74196485f70ead520cf80d4227e61786119b51a9b4737e18c821b8b7b66d11d7",
  "timeline": "picture-masks-lifecycle",
  "profile": {"kind": "native_color_master_v1"}
}
```

Normal export and completed replay remain direct calls:

```rust
let request: ExportRequest = serde_json::from_str(request_json)?;
let prepared = project.prepare_export(request.clone())?;
let first = project.export(request.clone())?;
assert_eq!(first.receipt.artifact.schema, 3);
let replay = project.export(request.clone())?;
assert_eq!(replay.receipt.receipt_id, first.receipt.receipt_id);
let checked = project.verify_export(request.intent.clone())?;
```

Another process can request cancellation while the export owns its epoch:

```rust
let cancellation = project.cancel_export(request.intent.clone())?;
let reconciliation = project.reconcile_export_staging()?;
```

The caller learns no checkpoint, receipt CAS, lock, or stage protocol. `reconcile_export_staging` remains the recovery entry point.

## Problem

The frozen producer calls `store_document(&receipt)` before checking the live epoch and cancellation flag. The cancel and stale-fence controls left receipt CAS files `7b3119b4343932cc61890bd75c822267b8fe52890d6a1d7af142cd7e3b14e7` and `cd88959dc13c444402a1a26ce1347c4d1b3928a49ecdb7bcf4ed5dc7aece6548` pointing to absent `.mov` files. No failed job completed and no stale artifact was promoted, but the immutable receipt directory now contains objects with no publication owner. A repair must make this ordering unreachable for new attempts while retaining honest recovery for cross-store crashes and arbitrary I/O residue.

## Shape

After native stage verification, the export writes a typed checkpoint to a new SQLite table. The checkpoint contains the expected stage hash, content-addressed artifact hash, receipt draft bytes and hash, plan/request/renderer identities, owner, epoch, and format-derived names. It is evidence, not a published `ArtifactReceipt` CAS document.

```rust
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct PublicationCheckpoint {
    pub schema: u32,
    pub kind: CheckpointKind,                // "staged_evidence_v1"
    pub phase: CheckpointPhase,             // Ready or Published
    pub project: EntityId,
    pub intent: EntityId,
    pub epoch: u64,
    pub owner_pid: u32,
    pub request_hash: ContentHash,
    pub plan_id: ContentHash,
    pub revision: ContentHash,
    pub renderer: BuildIdentity,
    pub stage: StageEvidence,
    pub artifact: ArtifactEvidence,
    pub receipt_draft: ReceiptDraft,
}

pub(crate) enum CheckpointKind { StagedEvidenceV1 }
pub(crate) enum CheckpointPhase { Ready, Published }
pub(crate) struct StageEvidence {
    pub owner: StageOwner,
    pub payload: StagePayloadName,           // movie.mov or movie.mp4
    pub sha256: ContentHash,
    pub bytes: u64,
}
pub(crate) struct ArtifactEvidence {
    pub sha256: ContentHash,
    pub bytes: u64,
    pub suffix: ArtifactSuffix,              // derived from NativeFormatContract
}
pub(crate) struct ReceiptDraft {
    pub id: ContentHash,
    pub body: String,                        // canonical ArtifactReceipt JSON, not yet in receipts/
}
```

`publication_evidence(project,intent,epoch,body_hash,body)` is the private table key. The stored checkpoint body hash must equal `ContentHash::document(&checkpoint)`. `ReceiptDraft.id` must equal `ContentHash::bytes(receipt_draft.body.as_bytes())`, matching the existing receipt CAS bytes. The `kind` tag is mandatory for the new path; an untagged or unknown row is retained as unknown evidence and is never adopted. A row is never deleted by this repair. A published row is historical evidence of the completed transaction; a ready row is recoverable evidence. The table is durable across a process crash, but its commit is not atomic with any file operation.

The public `MovieProfile::NativeColorMasterV1`, `NativeFormatContract`, Receipt3 evidence, source/output clocks, and bounded writer remain unchanged. `ArtifactReceipt` continues to use schema 2 for H.264 and schema 3 for mastering. The checkpoint records a draft of the existing Receipt3 JSON; it does not add fields or change the receipt hash.

```rust
pub(crate) fn record_verified_stage(
    project: &Project,
    tx: &rusqlite::Transaction<'_>,
    owner: &StageOwner,
    plan: &ExportPlan,
    request_hash: &ContentHash,
    stage: &Path,
    technical: &NativeMeasurements,
) -> Result<PublicationCheckpoint> { todo!() }

pub(crate) fn publish_checkpoint_locked(
    project: &Project,
    tx: &rusqlite::Transaction<'_>,
    checkpoint: &PublicationCheckpoint,
    control: &ExportControl,
) -> Result<StoredArtifact> { todo!() }

pub(crate) fn recover_checkpoint(
    project: &Project,
    old: &PublicationCheckpoint,
    new_owner: &StageOwner,
    control: &ExportControl,
) -> Result<RecoveryDecision> { todo!() }

pub(crate) fn store_verified_receipt(
    root: &Path,
    draft: &ReceiptDraft,
    final_path: &Path,
    expected_sha256: &ContentHash,
    expected_bytes: u64,
) -> Result<ContentHash> { todo!() }
```

`store_verified_receipt` is the only new caller of the receipt CAS helper. It first verifies the final path exists, has the expected hash and size, and has passed profile-specific native verification. A draft can be serialized before publication, but an `ArtifactReceipt` CAS object cannot be created before those checks.

The checkpoint is private staged evidence. It is not an `ArtifactReceipt`, is not a receipt-CAS publication, and cannot satisfy completed replay. Only the final artifact check, verified receipt CAS, and completed ledger commit together publish the job.

The interface is deep: callers coordinate only the existing five `Project` operations, while one private publication owner hides checkpoint serialization, source binding, lock ordering, filesystem recovery, and receipt admission. No checkpoint or transport type is added to the public surface.

## Publication order and linearization

1. Keep the current writer, source workers, bounded channels, source verification, native readback, stage fsync, and stage hash behavior. Do not run native work inside the publication lock.
2. Begin an immediate SQLite transaction. Check the live `(project,intent,epoch)`, `state='running'`, `cancel_requested=0`, plan identity, and renderer. Insert the tagged `kind='staged_evidence_v1'`, `Ready` checkpoint and set the job to `finalizing` in this same transaction. Commit it.
3. Stop creating new stage bytes. Recheck the lease control. Begin a second immediate transaction. It must find the same epoch, `state='finalizing'`, `cancel_requested=0`, and the matching ready checkpoint.
4. Hold this SQLite write transaction while deriving the final path, hard-linking the stage, setting the final file read-only, syncing `artifacts/`, and verifying final hash and byte count. An existing final path is reusable only when its hash and size match. Never overwrite a mismatch.
5. While the same transaction remains open, call `store_verified_receipt`. It may link the immutable receipt CAS file or validate an identical existing file. It must not run native encoding or native decode while the SQLite lock is held.
6. Update `exports` to `completed` with the stored receipt, mark the attempt completed, set checkpoint phase `Published`, and commit the transaction. Only this successful SQLite commit is the **job publication linearization point**.
7. After the commit, explicitly remove the owned stage payload and owner document. A cleanup failure leaves the completed artifact and checkpoint intact for later reconciliation.

Content-addressed files are durable objects, not completed publication. A final artifact or receipt CAS file can exist after a crash and still have no completed job. Recovery must validate the checkpoint, plan, hashes, format, and fresh output evidence before completing the job. It must never infer completion from either CAS object alone.

The lock gives cancellation and fencing a precise order. `cancel_export` opens `BEGIN IMMEDIATE`, re-reads the target row, and commits `cancel_requested=1` only while the target remains cancellable. A fence opens the same transaction, checks its expected live epoch, and commits the epoch advance only while that epoch still owns the attempt. If either mutation commits before step 3, the publication transaction fails its precondition before linking the artifact or storing the receipt. If step 3 acquires the SQLite write lock first, the competing call waits; after the commit it observes `completed` and cannot retroactively cancel or fence that publication. A real filesystem or process crash can still leave files after SQLite rolls back. The checkpoint makes that outcome recoverable without claiming cross-system atomicity.

## Ownership, leases, and recovery

The store keeps its existing WAL/FULL durability and five-second busy timeout. The lease renewer runs every ten seconds against a 240-second expiry while stage rendering and checkpoint creation proceed. Before step 3, it is quiesced for a bounded publication window shorter than the lease TTL. The window contains only filesystem links, fsyncs, hash checks, and the small receipt CAS write. If it exceeds its deadline, the transaction rolls back and the checkpoint remains `Ready`; no receipt or completion is claimed. Normal lease renewal resumes on a retry. This avoids a renewal thread waiting on the same SQLite writer lock and falsely fencing a healthy publication.

`cancel_export` still uses `BEGIN IMMEDIATE`. A request committed while the job is `running` or `finalizing` sets `cancel_requested`; a busy-timeout failure makes no cancellation claim. A request blocked behind the publication transaction sees `completed` after the linearization commit. Epoch advancement uses the same lock and expected-epoch preconditions; a stale caller cannot fence a newer owner. An alive owner with a ready checkpoint blocks a new epoch even after the nominal expiry; a dead owner can be recovered after the old attempt is marked abandoned.

Recovery loads the plan by project and intent, verifies its stored hash and revision, checks the request hash and renderer, and validates `NativeFormatContract` before reading a checkpoint. It requires the checkpoint owner, payload, stage hash, receipt draft ID, output suffix, and plan ID to agree. For a new epoch, it copies the checkpoint with a `recovered_from_epoch` value and keeps the old stage locator. It may use an old stage only after the old owner is dead, the owner document matches, the payload allowlist is exact, and fresh source/output verification succeeds.

`ExportStage::Drop` must stop deleting a stage after an uncertain publication attempt. Cleanup becomes explicit and is allowed only after a terminal ledger decision or a successful completed commit. `reconcile_export_staging` retains unknown stages, unknown owners, links, extra files, invalid checkpoint bodies, hash conflicts, and any stage with an ambiguous final or receipt observation. It may reclaim a known owner’s exact payload after a cancelled or fenced pre-publication attempt, while preserving the checkpoint row and its failure reason.

## Crash and failure outcomes

| Failure point | Durable facts | Required result |
| --- | --- | --- |
| Writer or native verification fails | No checkpoint; stage may exist | Mark failed after claim; retain until dead-owner reconciliation; publish no artifact or receipt. |
| Checkpoint transaction rolls back or is ambiguous | Stage may exist; checkpoint may or may not exist | Retain the stage. Do not infer that native evidence was stored. Reconcile only with owner, ledger, and hash proof. |
| Cancellation or fence before publication transaction | Ready checkpoint, no publication lock | Guard precondition fails; no new final link and no receipt CAS. Mark cancelled/fenced and retain evidence. |
| Hard-link or artifact fsync fails | Checkpoint remains Ready; final may be absent or present | Roll back SQLite; never store receipt. Recovery verifies exact final state or retries from the owned stage. |
| Final path already exists with exact bytes | Shared content-addressed artifact is present | Verify hash, size, and profile output; reuse it. The job is still incomplete until receipt CAS and DB commit succeed. |
| Final path exists with different bytes | Hash conflict | Do not overwrite or delete. Retain the checkpoint and return a publication conflict. |
| Receipt CAS write fails | Final artifact may be valid; checkpoint remains Ready | Do not complete. Retry only after final verification; retain any ambiguous receipt file for hash audit. |
| SQLite commit fails after artifact/receipt writes | Files may exist; DB is still finalizing or rolled back | Treat as unknown. Inspect checkpoint, final hash, and receipt body. Complete only through a later guarded commit. |
| SIGKILL during the locked transaction | SQLite transaction rolls back; files may remain | New owner verifies every object and source binding, then resumes or rerenders. No CAS-only completion. |
| Receipt CAS exists but final artifact is absent | Unreferenced immutable receipt is evidence, not publication | Retain it and the checkpoint. Do not read it as a completed artifact or delete it automatically. |

The same table applies to `.mp4` and `.mov`. A content-addressed artifact shared by another intent is reusable only after exact hash, format, and fresh native verification. A receipt from another plan is never adopted merely because its output hash matches.

## Historical compatibility and old recovery

No serialized snapshot, plan, or `ArtifactReceipt` document changes. The exact retained hashes remain: snapshot schema 1 `a4afc9237cdc477ddc0c62023b7e0ed185a9f39bd3f72fd3f6596964d1c82423`; placement snapshot `00d8a0eb3bbf0cd6290e68fffaa8c4d8b5a654446fb2220f5d084da17944e1ea`; motion snapshot `1947fcb6939dbec40f13ae23b87a156f5d6e1758fa18e058aaa1f810abc313d3`; plans 2–5 `97fdd9f63d48ee3b600ee37a845c302e79815bd1870b20dae376f9c4a957e025`, `4e5a89b00e7b5fabaafb4bf1335c1a5c3538c593765b4f5e5c818ff6bcede219`, `5cf0320f82bfc19839c5a06ffec15449fcdb80b97be15e2b4fb4105517ef0687`, `8ca51e03d048971a86cb598990fabd2f93f839c98b1b6c5fda3eb7aa90c3ee06`; actual Plan6 masks `5f9556fa7085bcd668d45cbc0564ff905adaf9b7f3d2e23b7fbed21ea65c5b28`; and Receipt2 `44c0c27ad1a58f22746011673d8e4d4a211c5b5cdeffcb18172d6cc73fc73be2`.

Completed replay remains unchanged: it reads `exports.receipt`, validates the immutable Receipt2 or Receipt3 CAS document, reopens the final artifact, and returns the same receipt identity. New successful exports also store the same `StoredArtifact` JSON in `exports.receipt`; the checkpoint is private evidence only. The actual completed lifecycle receipt `2f0575ae05c1941e709d0a3c4cc2e7ee12f45b37b8b32ad5384470f190a1e3ef` and output `cb0a07e5099cbe5ecaf22a467e5a02439c543fe7be6cea183d79632d7d99bdbe` remain valid evidence.

Old finalizing rows have `exports.receipt` populated by the previous producer and no `staged_evidence_v1` checkpoint tag. Preserve their current recovery: validate the receipt, adopt and verify an existing final artifact, then call `finish_export`; if the final artifact is absent, retain the receipt as historical evidence and render a fresh owned epoch. Never treat the two known orphan receipts as completed publication. New finalizing rows have `exports.receipt=NULL` and a tagged `staged_evidence_v1` ready checkpoint, so recovery follows the source-bound checkpoint path. A row with both a legacy receipt and a checkpoint, or with neither, is ambiguous and remains unreconciled until an explicit migration decision.

The SQLite migration adds only `publication_evidence` and increments the store version. It does not rewrite existing document bytes or receipt files. Receipt3’s QuickTime brand, `ap4h`/`lpcm`, signed packed PCM24LE stereo layout, streaming intervals, zero code delta, and output clocks stay under `NativeFormatContract` and `movie` verification.

## Proof and negative controls

The fresh lifecycle rerun must bind producer `636e5afb8035eb67f7ec7ec3584182ab69ac77e8ff2b95e824bd2312a1c92d11`, lifecycle report SHA `5f7eaa18c2a0763618d49100cb75a86e34dbea9165dc1f7fdfe3f9ba03e5a586`, exact source closure, plan, renderer, and Receipt3 evidence. It must repeat active cancellation, stale-epoch fencing, real SIGKILL recovery, promoted finalizing recovery, unknown-stage retention, completed replay, and receipt audit. It must show that a cancelled or fenced attempt creates neither a final artifact nor a new receipt CAS object.

Inject failures before checkpoint commit, after checkpoint commit, before and after the publication lock, during hard-link, after artifact fsync, during receipt CAS linking, and immediately before SQLite commit. Exercise an existing exact artifact, a mismatched artifact, an existing exact receipt, a mismatched receipt body, missing checkpoint, foreign project/intent/epoch, changed plan, changed source, missing owner, symlink payload, extra stage file, and false terminal ledger state. Assert that CAS files alone never produce `completed`.

## Tradeoffs accepted

- We accept one private SQLite table and durable rows in exchange for source-bound recovery after filesystem or process failure.
- We accept a bounded write lock across small filesystem operations in exchange for an exact cancellation and fencing order.
- We accept retained evidence and later reconciliation in exchange for never inferring completion from a CAS file.
- We accept explicit stage cleanup after completion in exchange for preserving uncertain stages through owner teardown.

## Alternatives considered

The smaller alternative omits `publication_evidence`. After native stage verification it opens one immediate SQLite transaction, checks epoch and cancellation, hard-links and verifies the final artifact, stores the receipt CAS, writes `completed`, and commits. It keeps the public interface and historical schemas unchanged and has fewer rows and recovery branches.

It loses the durable description of what was verified before the filesystem work. A crash after a hard-link or receipt CAS write leaves recovery to infer intent from stage names and hashes. Adding enough scans, draft receipt data, and source checks recreates a checkpoint without its explicit identity. Calling `store_document` before the guard reproduces the actual orphan receipt defect. Candidate B accepts the extra private table and reconciliation work because it makes the failure boundary source-bound and auditable while preserving the same public calls.

## Rejected alternatives

- Storing evidence beside `movie.mov` exposes a new stage file to the existing unknown-file policy and loses the checkpoint if cleanup runs. The private SQLite row keeps the stage payload allowlist unchanged.
- Deleting every receipt CAS or stage after any failure hides unknown outcomes and breaks the required audit trail. Retain and classify them.
- Treating an existing final artifact or receipt as completion bypasses plan binding, native verification, and the job linearization point.
- Holding the SQLite lock during native writing would create lease starvation and a long cross-system critical section. Only the bounded link, fsync, hash, and receipt CAS operations run under the publication lock.

## Synthesis decision

This is an independent Candidate B package. The sibling publication draft was not read; arena synthesis remains pending.

## Open questions and risks

Remaining risks are honest: SQLite can commit while a directory fsync fails, a process can die after either filesystem mutation, and an external actor can create hash conflicts. A crash or arbitrary I/O failure can leave a final file, a receipt CAS object, a ready checkpoint, or any combination of these stores. Recovery can classify these outcomes and preserve evidence; it cannot promise globally that no object remains, and it cannot claim atomicity across SQLite and the filesystem.

## Next implementation step

Add the private checkpoint migration and race-focused publication tests first, then move Receipt CAS creation behind the guarded final-artifact verification without changing native writer or Receipt3 code.
