# Publication Candidate A: guarded artifact publication

Status: design complete; no runtime code is implemented or tested by this document.

This candidate changes no public `Project` operation and adds no persisted job state.

## Caller usage first

### Prepare, publish, and verify a native master

```rust
use video_studio::{EntityId, ExportRequest, MovieProfile, Project, Result};

fn publish_master(
    project: &Project,
    revision: video_studio::ContentHash,
) -> Result<video_studio::ExportResult> {
    let request = ExportRequest {
        intent: EntityId::parse("release-master-publication-a01")?,
        revision,
        timeline: EntityId::parse("picture-masks")?,
        profile: MovieProfile::NativeColorMasterV1,
    };

    let prepared = project.prepare_export(request.clone())?;
    let exported = project.export(request.clone())?;
    let reopened = project.verify_export(request.intent)?;

    assert_eq!(exported.receipt.receipt_id, reopened.receipt.receipt_id);
    assert_eq!(prepared.plan_id, reopened.receipt.artifact.plan_id);
    Ok(reopened)
}
```

`export` returns success only after the completed job transaction commits.
The returned artifact has already passed the existing fresh native verification.

### Cancel an active export from another caller

```rust
use video_studio::{EntityId, ExportCancellation, Project, Result};

fn cancel_active_export(project: &Project) -> Result<ExportCancellation> {
    project.cancel_export(EntityId::parse(
        "release-master-publication-a01",
    )?)
}
```

The export can run in another thread or process. SQLite commit order decides the race.

A successful `cancellation_requested` response means no job publication committed.
It does not alone prove that a failed publication attempt left no filesystem residue.

If cancellation commits before the guarded transaction starts, that worker creates no final link or receipt CAS entry.

A `completed` response means publication committed first. Cancellation does not rewrite the completed job.

### Resolve an uncertain publication response

```rust
use video_studio::{ExportRequest, Project, Result};

fn publish_with_readback(project: &Project, request: &ExportRequest) -> Result<()> {
    match project.export(request.clone()) {
        Ok(_) => Ok(()),
        Err(error) if error.code == "publication_outcome_unknown" => match project
            .verify_export(request.intent.clone())
        {
            Ok(_) => Ok(()),
            // The caller retains request and schedules a replay after lease expiry.
            Err(readback) => Err(readback),
        },
        Err(error) => Err(error),
    }
}
```

The uncertain error is reserved for an unreadable SQLite commit outcome.
It does not mean the job failed.

The caller uses the existing intent and operations for readback and replay.
`reconcile_export_staging` remains available after an attempt becomes terminal.

## Problem

Producer `636e5afb8035eb67f7ec7ec3584182ab69ac77e8ff2b95e824bd2312a1c92d11` stores `ArtifactReceipt` too early.

The cancellation created receipt `7b3119b4343932cc61890bd75c822267b8fe52890d6a5d1d7af142cd7e3b14e7`.
It points to absent artifact `1d66cb6924750b72fd6eb3d6bebe472f300ecc2d81dc90efae61935df37b530c.mov`.

The fence created receipt `cd88959dc13c444402a1a26ce1347c4d1b3928a49ecdb7bcf4ed5dc7aece6548`.
It points to absent artifact `4546d60498f50b439da87c9754932d3cba6dafb527e7661f763ff8e534b3b60f.mov`.

Neither attempt completed. Neither attempt promoted an artifact.
Those observations and immutable receipts remain preserved.

The repair must order three independent stores:

1. The content-addressed artifact path.
2. The immutable `ArtifactReceipt` document.
3. The SQLite completed job and attempt rows.

No filesystem operation can commit atomically with SQLite.
The design therefore defines separate visibility points and one job publication point.

## Decision and invariants

`publication.rs` owns one short `BEGIN IMMEDIATE` transaction.
The transaction guards artifact linking, receipt CAS publication, and SQLite completion.

All whole-output work finishes before the transaction:

- native writer completion and callback teardown;
- source revalidation;
- native output verification;
- output hashing and byte counting;
- stage file sealing and file `fsync`;
- existing shared-artifact hashing.

The guarded transaction performs only bounded metadata work and small receipt work.
It can still block on directory or receipt `fsync` calls.

These invariants define the shape:

1. `AvailableArtifact` is required to publish an `ArtifactReceipt` through the internal CAS entrypoint.
2. The final artifact is a verified regular file before receipt construction.
3. Artifact directory durability is requested before receipt CAS publication.
4. A completed row always contains the exact `StoredArtifact` wrapper.
5. A CAS file alone never implies job completion.
6. Cancellation and epoch transfer serialize against publication through SQLite.
7. New code reads `finalizing` rows but never creates one.
8. Unknown stage bytes are never adopted or deleted.
9. Historical orphan artifacts and receipts are never deleted automatically.

The first invariant is process-local. It prevents the faulty call order in code.
It cannot repair the two preserved historical orphan receipts.

## Linearization points

The design uses exact terms for three different events.

| Event | Linearization point | Meaning |
| --- | --- | --- |
| Artifact availability | successful final hard link, or guarded identity recheck | Exact bytes exist at the format-derived final path. |
| Receipt availability | successful receipt CAS hard link and requested directory sync | The immutable document is addressable. The job may remain incomplete. |
| Job publication | successful SQLite `COMMIT` of both completed rows | Public replay and `verify_export` may report completion. |

Cancellation admission is the commit that sets `cancel_requested=1`.
Epoch admission is the commit that installs the newer epoch.

`BEGIN IMMEDIATE` orders both admissions against job publication.

If cancellation commits first, the publication guard rejects the worker.
If publication acquires the write transaction first, cancellation waits or returns database busy.
After publication commits, `cancel_export` reads `completed`.

If that transaction rolls back after linking files, cancellation may commit afterward.
The cancelled job can then coexist with retained filesystem residue.

Request arrival time is not an admission point.
A timed-out `cancel_export` call has not committed cancellation and must be retried.

## Type sketch

The public types and signatures remain unchanged.

```rust
impl Project {
    pub fn prepare_export(&self, request: ExportRequest) -> Result<PreparedExport> {
        unimplemented!("existing public operation")
    }

    pub fn export(&self, request: ExportRequest) -> Result<ExportResult> {
        unimplemented!("claim, execute, publish, then observe")
    }

    pub fn cancel_export(&self, intent: EntityId) -> Result<ExportCancellation> {
        unimplemented!("existing immediate transaction")
    }

    pub fn verify_export(&self, intent: EntityId) -> Result<ExportResult> {
        unimplemented!("completed-row readback remains authoritative")
    }

    pub fn reconcile_export_staging(&self) -> Result<StagingReconciliation> {
        unimplemented!("existing owner-based cleanup policy")
    }
}
```

The following types are crate-private.

```rust
// publication.rs
pub(crate) struct ActiveClaim {
    project: EntityId,
    intent: EntityId,
    request_hash: ContentHash,
    epoch: u64,
    owner_pid: u32,
}

pub(crate) struct ArtifactBinding {
    project: EntityId,
    revision: ContentHash,
    plan_id: ContentHash,
    renderer: BuildIdentity,
    format: NativeFormatContract,
}

pub(crate) struct VerifiedOutput {
    stage: SealedStage,
    technical: NativeMeasurements,
}

struct VerifiedSharedArtifact {
    file: std::fs::File,
    identity: FileIdentity,
    path: PathBuf,
    sha256: ContentHash,
    bytes: u64,
}

/// Its constructors are private to the guarded transaction.
struct AvailableArtifact {
    file: std::fs::File,
    identity: FileIdentity,
    path: PathBuf,
    sha256: ContentHash,
    bytes: u64,
}

pub(crate) struct PublishedArtifact(StoredArtifact);

impl PublishedArtifact {
    pub(crate) fn into_stored(self) -> StoredArtifact {
        unimplemented!("available only after confirmed commit")
    }
}

pub(crate) enum PublicationFailure {
    /// Fresh SQLite readback proved that this epoch did not publish.
    Definitive(StudioError),

    /// SQLite could not reveal whether COMMIT took effect.
    OutcomeUnknown {
        cause: StudioError,
        expected_receipt: Option<ContentHash>,
    },
}

pub(crate) fn publish(
    project: &Project,
    claim: ActiveClaim,
    binding: ArtifactBinding,
    output: VerifiedOutput,
    lease: ExportLease,
) -> std::result::Result<PublishedArtifact, PublicationFailure> {
    unimplemented!("guarded publication transaction")
}

pub(crate) fn complete_legacy_finalizing(
    project: &Project,
    claim: ActiveClaim,
    stored: StoredArtifact,
    verified: VerifiedSharedArtifact,
    lease: ExportLease,
) -> std::result::Result<PublishedArtifact, PublicationFailure> {
    unimplemented!("guarded completion without a new receipt CAS write")
}

fn store_artifact_receipt(
    available: &AvailableArtifact,
    binding: &ArtifactBinding,
    technical: NativeMeasurements,
) -> Result<StoredArtifact> {
    unimplemented!("construct and publish only after artifact availability")
}

pub(crate) fn store_verification_document(
    project: &Project,
    verification: &ArtifactVerification,
) -> Result<ContentHash> {
    unimplemented!("typed CAS entrypoint for post-publication observation")
}
```

`AvailableArtifact` is deliberately non-serializable and non-cloneable.
Only a verified final pathname can produce it.

`Project::store_document<T>` no longer accepts arbitrary internal receipt types.
Artifact publication and verification documents use separate private entrypoints.

`ArtifactReceipt` stays publicly readable and byte-compatible.
The exporter does not instantiate or store one before artifact availability.

`PublishedArtifact` proves that SQLite completion committed or fresh readback confirmed it.
Post-publication verification accepts this marker instead of an uncommitted `StoredArtifact`.

```rust
// export_stage.rs
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct FileIdentity {
    device: u64,
    inode: u64,
    bytes: u64,
    modified_seconds: i64,
    modified_nanoseconds: i64,
}

pub(crate) struct SealedStage {
    owned: ExportStage,
    file: std::fs::File,
    identity: FileIdentity,
    sha256: ContentHash,
    bytes: u64,
}

impl ExportStage {
    pub(crate) fn seal(
        self,
        control: &ExportControl,
    ) -> Result<SealedStage> {
        unimplemented!("hash one open regular file, set read-only, and sync it")
    }
}

impl SealedStage {
    pub(crate) fn receipt_stage_path(&self) -> PathBuf {
        unimplemented!("one fixed, owner-scoped temporary receipt pathname")
    }
}
```

`seal` hashes through one open descriptor and checks control between chunks.
It rejects symlinks, non-regular files, size changes, and metadata changes during hashing.

The owner cleanup allowlist gains one exact `artifact-receipt.json.tmp` name.
Cleanup removes that regular file with the owned payload and owner document.

```rust
// exports.rs
impl ExportLease {
    fn quiesce_and_renew(
        self,
        project: &Project,
        claim: &ActiveClaim,
    ) -> Result<PublicationTicket> {
        unimplemented!("join renewal worker, check control, then renew synchronously")
    }
}

pub(crate) struct PublicationTicket {
    control: ExportControl,
    renewed_through_ms: u64,
}
```

`PublicationTicket` prevents the renewal worker from contending with its own publication transaction.
It contains no framework object and crosses no native callback boundary.

## Module map and ownership

| Module | Owns | Does not own |
| --- | --- | --- |
| `exports.rs` | Public lifecycle, claim creation, cancellation, replay, error disposition | Artifact or receipt publication order |
| new `publication.rs` | Final-path availability, receipt construction, CAS order, SQLite completion, uncertain-outcome readback | Encoding, native verification, public API |
| `export_stage.rs` | Stage owner document, payload sealing, exact cleanup allowlist | Job state and receipt meaning |
| `native_format.rs` | Extension, rooted artifact path, receipt schema, codec/container measurement validation | Publication timing |
| `project.rs` | SQLite connection policy and generic blob verification | Export-specific transaction choreography |

The call chain is `Project::export` to `publication::publish`.
The publication module completes the cross-store invariant behind one private interface.

This is a deliberate shared-state merge point.
Two publishers, cancellation, and epoch transfer can write the same job or CAS path.

## Exact phase order

### 1. Execute and seal outside SQLite

1. Claim the existing `running` epoch and start its renewal worker.
2. Reconcile only retired, dead, exactly owned stages.
3. Write the native payload into the new owned stage.
4. Close the native writer, callbacks, decode workers, and bounded channels.
5. Check `ExportControl`.
6. Sync the staged payload file.
7. Revalidate immutable sources and the prepared plan.
8. Run the existing full native output verification.
9. Validate the measurements through `NativeFormatContract`.
10. Hash one open stage descriptor with cancellable chunks.
11. Set the stage inode read-only and sync the inode and stage directory.
12. Derive the final path from the measured hash and format contract.

No `ArtifactReceipt` value exists during this phase.

The layout check requires `staging`, `artifacts`, and `receipts` on one device.
An unsupported nested mount fails before native writing where possible.

SQLite may reside on another device.
No design can make that database commit atomic with filesystem links.

### 2. Prepare a possible shared artifact outside SQLite

If the final path exists, open it without following a symlink.

The verifier requires a regular, read-only file with the expected byte count.
It hashes the held descriptor and checks stable identity before and after hashing.

The verifier syncs the file and artifact directory before guarded revalidation.
It never overwrites, chmods, deletes, or adopts a mismatching path.

If the path is absent, the sealed stage remains the candidate.

### 3. Quiesce renewal and enter the guard

1. Stop and join the ten-second renewal worker.
2. Check its `ExportControl` result.
3. Renew the exact claim synchronously for the existing 240-second lease.
4. Open the configured SQLite connection.
5. Acquire `BEGIN IMMEDIATE` under the existing five-second busy timeout.
6. Read and validate the job and current attempt.

The guard requires all of these values:

- exact project, intent, request hash, epoch, and owner PID;
- job state `running`;
- attempt state `running`;
- `cancel_requested=0`;
- an unexpired lease at the guarded read.

No newer epoch or admitted cancellation can appear while this transaction holds the write lock.

### 4. Establish final artifact availability

For an absent final path, call `hard_link(stage, final)`.
The sealed stage is already read-only and synced.

After a successful link, open the final path without following symlinks.
Require the stage and final descriptors to share device, inode, and byte count.
Then sync the artifact directory.

For a preverified shared path, reopen the final path inside the transaction.
Require its identity to match the held, fully hashed descriptor.

If `hard_link` returns `AlreadyExists` for another inode, roll back immediately.
Resume lease renewal and hash that shared artifact outside SQLite.

The publication module permits three such race retries.
Further replacement returns `artifact_publication_race` without a receipt write.

Any successful branch now creates the private `AvailableArtifact` token.

### 5. Publish the receipt after the artifact

1. Check the quiesced control once more.
2. Construct `ArtifactReceipt` from `AvailableArtifact` and `ArtifactBinding`.
3. Validate the complete receipt through `NativeFormatContract`.
4. Serialize the receipt and enforce a private 64-KiB admission limit.
5. Write it to the owner-scoped receipt temporary file.
6. Set the temporary inode read-only, then sync it.
7. Hard-link it to `receipts/<receipt_id>.json`.
8. If that CAS path exists, reject a length mismatch before reading it.
9. Verify its exact bounded bytes.
10. Sync the receipts directory.
11. Construct `StoredArtifact`.

The 64-KiB limit does not change serialized bytes or receipt hashes.
The completed A01 schema-3 receipt is 2,123 bytes.
Current fixed evidence and the bounded QuickTime brand list fit below the limit.

An error after the receipt hard link may leave an orphan receipt.
Its final artifact already exists and passed verification.

### 6. Complete the job in the same SQLite transaction

Use one conditional update for the job:

```sql
UPDATE exports
SET state='completed', receipt=?stored, expires_at=0
WHERE project=?project
  AND intent=?intent
  AND request_hash=?request_hash
  AND epoch=?epoch
  AND owner_pid=?owner_pid
  AND state='running'
  AND cancel_requested=0
  AND expires_at>?now;
```

Exactly one row must change.

Update the matching `export_attempts` row from `running` to `completed`.
Bind the same epoch, owner PID, receipt ID, and close time.
Exactly one attempt row must change.

Check the control and lease time immediately before `COMMIT`.
The successful SQLite commit is the job publication linearization point.

The guarded transaction never writes `finalizing`.

### 7. Observe after publication

Drop the owned stage after a confirmed commit.
Then run the existing fresh `verify_artifact` path and store `ArtifactVerification` schema 1.

A post-publication observation failure does not demote the completed job.
`verify_export` can repeat that observation from the completed row.

The outer error handler must not mark an uncertain or completed publication as failed.

## Lease and lock behavior

The current renewal worker writes every ten seconds and extends the lease by 240 seconds.
It must not run concurrently with the guarded transaction.

`quiesce_and_renew` joins that worker before one synchronous renewal.
This avoids a false `lease_unavailable` caused by the worker's own SQLite busy timeout.

The guard retains the current WAL journal, `synchronous=FULL`, and five-second busy timeout.
Those settings do not make filesystem changes atomic with SQLite.

The transaction admits no long hash, native decode, source verification, or movie inspection.
It still includes two directory syncs, one small file sync, and SQLite commit.

Those operations have no reliable wall-clock upper bound.
A storage stall can block cancellation and epoch acquisition beyond five seconds.

During that stall, neither competing operation is admitted.
After process death, SQLite releases the lock and rolls the transaction back.

The final SQL update rejects publication after the renewed lease deadline.
Rollback can leave filesystem objects, but it cannot leave a completed row.

## Existing shared artifacts

Content addressing permits independent intents to share an exact output file.
It does not permit trusting a filename.

A shared path is accepted only after a full hash outside SQLite.
The guarded identity recheck prevents an app-managed race between that hash and completion.

This replaces the current full `verify_blob` read inside the promotion transaction.

The held descriptor keeps the verified inode alive.
The final pathname must still identify that inode inside the guard.

The design assumes the studio root is app-managed, as current code does.
It does not claim protection from a hostile process mutating directories during publication.

A wrong file at the expected hash path is retained and reported as tampered.
The publisher never replaces it.

## Crash and failure outcomes

| Last completed action | Filesystem outcome | SQLite outcome | Required response or recovery |
| --- | --- | --- | --- |
| Stage verification only | Owned stage may remain after process death | `running` | Expiry takeover abandons the attempt and applies existing owner cleanup. It rerenders. |
| Cancellation or new epoch commits before the guard | This worker creates no later final link or receipt | Cancelled or newer epoch | Old worker returns cancelled or fenced. Earlier or shared objects remain untouched. |
| Guard acquired, before artifact link | Stage only | Transaction rolls back | Close only the exact old claim after fresh readback. |
| Final hard link succeeds, before artifact directory sync | Final path may exist | Transaction rolls back | Preserve the orphan artifact. A later publisher must hash it fully. |
| Artifact directory sync succeeds, before receipt link | Verified final path exists | Transaction rolls back | Preserve and permit exact shared reuse. |
| Receipt write or link fails | Final exists; receipt may be absent | Transaction rolls back | Never infer completion. Preserve the final and any temporary evidence. |
| Receipt link succeeds, before receipt directory sync | Final and receipt may exist | Transaction rolls back | Receipt can be orphaned, but it cannot point to an absent final created by this producer. |
| Both CAS objects exist, SQL update fails | Final and receipt remain | Transaction rolls back | Fresh readback proves non-publication before closing the exact attempt. |
| SQLite `COMMIT` returns an error | Final and receipt remain | Committed or rolled back | Reopen SQLite. Return success if exact completion is visible. Otherwise return definitive failure or `publication_outcome_unknown`. |
| SIGKILL during guarded transaction | Stage, final, receipt temporary, and receipt CAS may form a prefix | SQLite rolls back, unless commit already completed | Next call trusts only SQLite. It validates any shared final before reuse. |
| Commit succeeds, response is lost | Final and receipt exist | `completed` | `verify_export` or identical `export` replay returns the stored receipt. |
| Post-commit verification fails | Final and receipt exist | `completed` | Return the observation error. Keep completion and allow `verify_export` retry. |
| `EXDEV` or layout mismatch | No cross-device fallback copy | Not completed | Return `unsupported_publication_layout`; retain owned evidence under current cleanup rules. |

Process-crash prefix ordering relies on successful file and directory sync calls.
This is not a promise against media loss, kernel failure, or storage hardware failure.

### Resolving a commit error

After any commit error, drop the transaction and open a fresh connection.

1. Exact completed row and receipt: return `PublishedArtifact`.
2. Same running epoch without receipt: publication did not commit.
3. Cancelled row: return `export_cancelled`.
4. Newer epoch: return `worker_fenced`.
5. Unreadable database: return `publication_outcome_unknown` and make no mutation.

An unknown outcome stops renewal and leaves the row for readback or lease-expiry recovery.
It never runs the current unconditional failed-attempt cleanup.

## Recovery and `finalizing`

The new publisher transitions directly from `running` to `completed`.
It produces no new `finalizing` rows.

The reader retains current support for a legacy `finalizing` row:

1. Claim a new epoch as today and retain the legacy `StoredArtifact` in memory.
2. Validate its receipt CAS, plan binding, format, and final path.
3. If the final exists, verify its full bytes and native measurements outside SQLite.
4. Complete through `complete_legacy_finalizing` under the same guarded ordering.
5. If the final is absent, retain the receipt and rerender through the new publisher.
6. If the final exists but fails verification, preserve it and fail the new attempt.

Legacy completion stores no new `ArtifactReceipt` document.
Its existing receipt must already match the verified final artifact.

The immutable plan renderer must equal the running build, as today.
A different producer returns `renderer_changed` and preserves the row for its original producer.

A new crash before job commit leaves `running`, not `finalizing`.
Recovery never infers completion from an orphan final or receipt.

## Compatibility

This repair changes transaction order and private ownership types only.

It changes no snapshot, plan, `ArtifactReceipt`, `StoredArtifact`, or verification schema.
It adds no SQLite column or state value.

The implementation must retain exact bytes and hashes for these fixtures:

| Fixture | SHA-256 |
| --- | --- |
| snapshot schema 1 | `a4afc9237cdc477ddc0c62023b7e0ed185a9f39bd3f72fd3f6596964d1c82423` |
| placement snapshot schema 1 | `00d8a0eb3bbf0cd6290e68fffaa8c4d8b5a654446fb2220f5d084da17944e1ea` |
| motion snapshot schema 1 | `1947fcb6939dbec40f13ae23b87a156f5d6e1758fa18e058aaa1f810abc313d3` |
| masks snapshot schema 1 | `a7bc52df330b5a9d7e0ef8e8fe71b47963d308be393eeefa0e00d0cfbbfc24dd` |
| plan schema 2 | `97fdd9f63d48ee3b600ee37a845c302e79815bd1870b20dae376f9c4a957e025` |
| plan schema 3 | `4e5a89b00e7b5fabaafb4bf1335c1a5c3538c593765b4f5e5c818ff6bcede219` |
| plan schema 4 | `5cf0320f82bfc19839c5a06ffec15449fcdb80b97be15e2b4fb4105517ef0687` |
| plan schema 5 | `8ca51e03d048971a86cb598990fabd2f93f839c98b1b6c5fda3eb7aa90c3ee06` |
| plan schema 6 synthetic masks | `5f9556fa7085bcd668d45cbc0564ff905adaf9b7f3d2e23b7fbed21ea65c5b28` |
| plan schema 6 canonical masks | `507038af46a4b5c970734a0c3738f034038b8228674c2058f9c1cb41b8ea7eb0` |
| `ArtifactReceipt` schema 2 | `44c0c27ad1a58f22746011673d8e4d4a211c5b5cdeffcb18172d6cc73fc73be2` |

The completed schema-3 receipt remains `2f0575ae05c1941e709d0a3c4cc2e7ee12f45b37b8b32ad5384470f190a1e3ef`.
It binds output `cb0a07e5099cbe5ecaf22a467e5a02439c543fe7be6cea183d79632d7d99bdbe.mov`.

The two P1 orphan receipts remain present and unreferenced.
A compatibility test must confirm that the repair does not delete them.

New exports require a fresh producer identity and fresh intents.
No new receipt is expected to retain the frozen producer's hash.

## Verification plan

### Pure and storage-level controls

Use temporary studio roots and deterministic files.

1. Prove the internal artifact-receipt CAS entrypoint requires `AvailableArtifact` at compile time.
2. Inject cancellation before `BEGIN IMMEDIATE`; assert no final link and no receipt CAS.
3. Inject an epoch increment before the guard; assert the same negatives.
4. Hold the publication transaction briefly; start cancellation; then commit publication.
5. Assert that cancellation returns `completed` in that ordering.
6. Inject artifact-link failure; assert no receipt and no completed row.
7. Inject receipt-link and receipt-sync failures; assert no completed row.
8. Inject both SQLite updates independently; assert transaction rollback.
9. Simulate commit success with a lost response; assert fresh readback returns success.
10. Simulate rollback with a commit error; assert fresh readback closes only the exact epoch.
11. Make readback fail; assert `publication_outcome_unknown` leaves the row unchanged.
12. Race two intents producing one hash; assert one artifact and valid completed receipts.
13. Place wrong bytes at the expected hash path; assert no overwrite or deletion.
14. Replace a shared path between preverification and guard; assert rollback and bounded retry.
15. Put directories on different devices; assert `unsupported_publication_layout` before receipt creation.
16. Reopen a legacy `finalizing` row with an existing artifact; assert guarded completion.
17. Reopen one with an absent artifact; assert rerender and no inference from its receipt.
18. Keep an unknown file in an owned stage; assert reconciliation retains the directory.

Each fault point audits the before-and-after artifact and receipt inventories.
The audit classifies retained historical P1 receipts separately from new-producer receipts.

### Real process controls

Run these controls in a new private state with a fresh binary and fresh intents.

1. Repeat public active cancellation after the writer has produced a stage.
2. Repeat injected stale-epoch fencing at the same boundary.
3. Send real SIGKILL after final linking and before receipt linking.
4. Send real SIGKILL after receipt linking and before SQLite commit.
5. Restart with the identical request after lease expiry.
6. Verify that replay trusts only the completed row.

The native control uses source fixture `969e22d77c0d5d2bb8aee5693254d9e17c2d06797b8ceac8f891c7f7d2aa7f04`.
It must again produce 72 frames and 144,000 stereo sample frames.

The selected PCM source interval remains `[8191, 152191)` at 48 kHz.
The output must report `ap4h`, packed signed PCM24LE `lpcm`, and zero code delta.

The control must verify source and output clocks, full decode, streaming EOF, and bounded chunks.
It does not establish picture ROI quality, watching, hearing, or creative acceptance.

### Historical controls

Run `legacy_hashes.rs` unchanged for snapshots, plans 2 through 6, and receipt 2.

Open a copy of the frozen lifecycle state.
Verify exact readback of completed receipt `2f0575ae05c1941e709d0a3c4cc2e7ee12f45b37b8b32ad5384470f190a1e3ef`.

Confirm the original cancellation and fence remain non-completed.
Confirm their two retained receipts still point to absent outputs.

The repair proof must not edit that frozen state.

## Rationale

The public surface already expresses the complete lifecycle.
Adding publish, finalize, or recover methods would make callers coordinate internal states.

The private availability token encodes the missing invariant.
The guarded transaction concentrates policy at the only shared-state merge point.

Hashing stays outside SQLite because master files are large.
Receipt creation stays inside because its ordering is the defect being repaired.

Direct `running` to `completed` removes a new crash window.
Legacy `finalizing` remains a read-compatible recovery input.

The design accepts filesystem orphans after rollback.
That evidence is safer than deleting an object whose database outcome is uncertain.

## Graftable strengths

- The non-serializable `AvailableArtifact` token makes receipt ordering hard to misuse.
- Separate filesystem and job linearization points prevent false completion claims.
- Shared-file verification moves whole-file hashing outside the SQLite lock.
- `AlreadyExists` rollback avoids trusting a concurrent filename inside the lock.
- Typed unknown outcomes prevent the failed-attempt handler from overwriting possible completion.
- Read-only support for legacy `finalizing` preserves current recovery without extending new state.

## Tradeoffs accepted

- We accept orphan artifacts and receipts after rollback in exchange for preserving uncertain evidence.
- We accept a global SQLite write lock during three sync operations in exchange for exact cancellation ordering.
- We accept cancellation latency during that boundary in exchange for one authoritative publication order.
- We accept same-device layout enforcement in exchange for atomic no-replace hard links.
- We accept rerender after an uncheckpointed crash in exchange for no new persisted state or stage adoption.
- We accept bounded shared-path retries in exchange for avoiding unbounded contention.

## Alternatives considered and rejected

### Durable staged-evidence checkpoint

A checkpoint would persist the stage hash, measurements, owner, and path before publication.
It could resume without rerender after process death.

It requires a new durable state or document, stage adoption rules, and new reconciliation semantics.
That storage surface is larger than this repair and exposes another recovery protocol.

This candidate rejects it for the smallest compatible fix.
Its typed evidence idea remains useful if rerender cost later justifies a migration.

### Guard, release SQLite, then publish files

This shape keeps database transactions shorter.
Cancellation can commit after the guard and before receipt publication.

It violates the required admission ordering and therefore is not viable.

### Store `finalizing` before filesystem work

This shape preserves the current two-step state machine.
It permits a visible database receipt before artifact availability.

Recovery then has to distinguish more partial states.
It repeats the defect instead of encoding the missing invariant.

### Filesystem lock as publication authority

A lock file can serialize artifact writers.
It cannot atomically order public cancellation or epoch transfer stored in SQLite.

Callers would still need the database result.
The extra authority would deepen the call chain without closing the race.

### Cross-device copy and rename fallback

A fallback needs another temporary-file ownership and cleanup protocol under `artifacts`.
It still cannot commit atomically with SQLite.

The current studio layout already depends on hard links.
This repair reports the unsupported layout instead of adding another recovery system.

## Red-flag screen

- **Shallow module:** avoided. One private call hides artifact, receipt, lock, lease, and outcome policy.
- **Information leakage:** avoided. Public callers see existing requests, results, cancellation, and verification only.
- **Temporal decomposition:** avoided. `publication.rs` owns one invariant across all of its phases.
- **Pass-through method:** avoided. `publish` completes the cross-store operation and resolves commit ambiguity.
- **Duplicated truth:** avoided. SQLite completion is authoritative; CAS scans never synthesize completion.

## Open questions and risks

1. Does the implementation environment permit a supported cross-device studio layout?
   If yes, that layout needs its own staged-copy design before implementation.
2. Is a 64-KiB private receipt admission cap acceptable for all planned evidence fields?
   Raising it later changes no stored bytes.
3. Can real fault injection distinguish commit-response loss from commit rollback on the supported SQLite build?
   Both branches still require fresh readback.
4. Is five seconds an acceptable cancellation busy timeout during slow directory sync?
   Increasing it changes responsiveness, not ordering.

## Next implementation step

Add fault-driven publication tests and the private `AvailableArtifact` type before moving any existing filesystem operation.
