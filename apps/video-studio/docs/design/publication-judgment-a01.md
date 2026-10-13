# Owned artifact publication judgment A01

Status: complete design judgment. No runtime, state, media, GPU, or Resolve files changed.

## Decision

Use Candidate A as the whole-shape base.

Candidate A preserves the existing `Project` interface and adds one private publication module. Its `AvailableArtifact` invariant directly prevents the observed receipt-ordering defect.

Candidate A also keeps whole-file work outside SQLite. It separates artifact visibility, receipt visibility, and completed-job publication.

Graft Candidate B's failure matrix and adversarial control inventory. Do not graft its checkpoint table, receipt draft, stage adoption, or new `finalizing` writes.

Simplify Candidate A's marker set during implementation. Keep only types that make an invalid call order impossible.

No model-family alternative was available. This judgment does not claim blind or cross-family review.

Candidate A SHA-256: `0404cd5037176d98f117bf43a07e143cc6f5dec47daa0f7f2e238cee0d141c5f`.

Candidate B SHA-256: `7f258ca1940040fde7984e3e6e0c62b0bd8c4c016b0023e0467c5f1879720c93`.

## Scores

| Criterion | Candidate A | Candidate B |
| --- | ---: | ---: |
| 1. Caller depth | 5 | 5 |
| 2. Failure and recovery clarity | 5 | 4 |
| 3. Historical compatibility | 5 | 3 |
| 4. Contention and lease behavior | 4 | 2 |
| 5. Proofability of required ordering | 5 | 4 |
| **Total** | **24/25** | **18/25** |

### 1. Caller depth

Both candidates retain `prepare_export`, `export`, `cancel_export`, `verify_export`, and staging reconciliation.

Candidate A places the cross-store invariant behind one private `publish` call. Callers do not coordinate filesystem phases or durable intermediate states.

Candidate B also hides its checkpoint from public callers. However, it creates another durable protocol that future maintainers must coordinate internally.

### 2. Failure and recovery clarity

Candidate A distinguishes final-file availability, receipt availability, and job publication. It treats an uncertain SQLite commit as a typed unknown outcome.

Candidate A also keeps new jobs in `running` until the completed commit. Legacy `finalizing` remains a read-compatible recovery input.

Candidate B has a useful failure matrix. Its `Ready` and `Published` checkpoint phases add more partially durable combinations.

Candidate B also permits stage adoption. That expands recovery authority beyond the current rerender-or-verify-final policy.

### 3. Historical compatibility

Candidate A changes no serialized document or database schema. It preserves exact snapshot, plan, receipt, and completed replay bytes.

Candidate B adds a table and migration. Its compatibility list omits the masks snapshot and one Plan 6 fixture.

Candidate B also serializes canonical `ArtifactReceipt` JSON into `ReceiptDraft` before the final artifact exists. Renaming those bytes does not satisfy the required ordering.

### 4. Contention and lease behavior

Candidate A hashes stages and shared artifacts before SQLite. It quiesces renewal before one guarded transaction.

Candidate A loses one point because receipt and directory `fsync` calls remain inside that transaction. Those calls have no reliable wall-clock bound.

Candidate B hashes the final artifact while holding the SQLite writer lock. It still describes the publication window as bounded.

Candidate B's alive-owner checkpoint rule also changes expiry takeover. That change is unnecessary for this repair.

### 5. Proofability

Candidate A exposes the required order through private capability types. Its negative controls directly observe artifact, receipt, and ledger deltas.

Candidate B's durable checkpoint makes some crash prefixes visible. The added states create a larger fault and recovery matrix.

Candidate B also names the frozen producer for a fresh proof. The repair requires a fresh producer and fresh intents.

Its first orphan receipt identifier has 62 hexadecimal characters. The retained identifier has 64 characters and must remain exact.

## Selected private shape

Keep the public `Project` operations and result types unchanged. Add one private `publication` module with this deep seam:

```rust
pub(crate) fn publish(
    project: &Project,
    claim: ActiveClaim,
    binding: ArtifactBinding,
    output: VerifiedOutput,
    lease: ExportLease,
) -> Result<PublishedArtifact, PublicationFailure>;
```

Keep these invariant-bearing private types:

- `SealedStage` owns the open, hashed, synced stage file.
- `PublicationGuard` owns the exact SQLite transaction, claim, and renewed lease ticket.
- `AvailableArtifact` proves the final pathname resolves to verified bytes.
- `PublishedArtifact` proves the exact completed commit, or confirmed readback, exists.
- `PublicationFailure` distinguishes definitive failure from `OutcomeUnknown`.

`AvailableArtifact` must be non-cloneable and non-serializable. Only `PublicationGuard` may construct it.

The receipt-CAS method must require `AvailableArtifact`. It must not accept a plain path, hash, or `StoredArtifact`.

Treat `ActiveClaim`, `ArtifactBinding`, and `VerifiedOutput` as input records. Avoid adding nominal states that enforce no additional invariant.

Fold `PublicationTicket` into `PublicationGuard` unless its ownership prevents renewal reuse. Keep one clear authority for the quiesced lease.

Do not add a public executor, publish method, recovery method, or checkpoint interface.

## Exact linearization contract

The implementation must name three separate events:

| Event | Linearization point | Consequence |
| --- | --- | --- |
| Artifact visibility | Final hard link succeeds, or the guarded pathname identity check succeeds | Exact bytes are visible at the content path. The job can remain incomplete. |
| Receipt visibility | Receipt CAS hard link succeeds and its directory sync is requested | The receipt is addressable. The job can remain incomplete. |
| Job publication | One SQLite commit completes the exact job and attempt rows | Replay and `verify_export` may report completion. |

Cancellation admission is its successful SQLite commit. Epoch admission is the successful commit that installs the newer epoch.

`BEGIN IMMEDIATE` orders both admissions against publication. Request arrival and a busy-timeout response are not admission points.

If cancellation or fencing commits before the guard, this attempt must create no final link, receipt temporary, or receipt CAS object.

The existing owned stage may remain. Historical CAS objects and a previously shared final may also remain.

If publication acquires the writer lock first, cancellation or fencing waits. After commit, those callers must observe `completed` or database busy.

A rollback after either filesystem link can leave visible files. Those files never establish completed publication.

## Mandatory implementation requirements

1. Finish writer callbacks, source validation, native verification, stage hashing, and stage `fsync` before SQLite publication.

2. Check the staging, artifact, and receipt roots for the supported same-device layout before native writing. Return `unsupported_publication_layout` without a copy fallback.

3. Seal the stage through one open descriptor. Reject symlinks, non-regular files, size drift, and metadata drift.

4. Keep `FileIdentity` to stable device and inode values. Record file type, size, mode, link count, nanosecond `mtime`, and nanosecond `ctime` in a separate descriptor observation.

5. Perform `fstat` before and after every outside-lock full hash. Hold the verified descriptor until the guarded pathname identity check.

6. A hard link legitimately changes `ctime` and link count. Refresh the held descriptor after linking, then compare the final descriptor against that simultaneous observation.

7. Never run a whole-file hash, native decode, source check, or plan check while holding SQLite's writer lock.

8. If a final path already exists, roll back before hashing it. Validate the file outside SQLite, then retry the guard at most three times.

9. Do not overwrite or delete a mismatched shared artifact. Retain the evidence and return a typed conflict.

10. Stop and join the lease-renewal worker before publication. Surface any renewal-worker failure before proceeding.

11. Recheck `ExportControl`, then synchronously renew the exact project, intent, request, epoch, owner, job, and attempt.

12. Inside `BEGIN IMMEDIATE`, require `running`, the exact request and plan, the exact epoch and owner, `cancel_requested=0`, and an unexpired lease.

13. Recheck the same claim and renewed deadline immediately before the completed update and commit.

14. Establish artifact availability by hard-linking the sealed stage. Reopen the final path without following symlinks and require the held device and inode.

15. Require a successful artifact-directory sync attempt before receipt construction. A failed sync rolls back SQLite but can leave the final file.

16. Construct and serialize `ArtifactReceipt` only after `AvailableArtifact` exists. Do not prebuild canonical receipt bytes as a draft.

17. Enforce a 64-KiB receipt limit before writing. Existing receipt verification must also remain within this admission limit.

18. Use one owner-scoped receipt temporary name. Create it exclusively and without following symlinks.

19. The stage cleanup allowlist may recognize only `owner.json`, the format-derived payload, and this exact receipt temporary.

20. Sync the receipt temporary, link it into receipt CAS, and request receipt-directory durability before the completed update.

21. An exact existing receipt may be reused only after a bounded byte-for-byte check. A conflicting receipt is retained and rejected.

22. Update exactly one job row and one matching attempt row in the same transaction. New code must transition directly from `running` to `completed`.

23. A post-commit verification failure is an observation failure. It must never demote or overwrite a completed job.

24. Any commit error requires a fresh connection and fresh readback. Discard the uncertain transaction and connection first.

25. Return success only when readback finds the exact completed receipt. Return cancellation or fencing only when that exact state is visible.

26. An exact unchanged `running` row can support guarded failure closure. Unreadable or ambiguous state returns `publication_outcome_unknown` without mutation.

27. The outer export error path must not mark an unknown or completed attempt failed. Every closure update needs exact request, epoch, owner, and state predicates.

28. CAS scans must never synthesize completion. SQLite remains the only completed-job authority.

29. Preserve legacy `finalizing` reads. New publication code must never create a `finalizing` row.

30. For a legacy finalizing row with a final artifact, validate its receipt, source, plan, renderer, full bytes, and native output outside SQLite.

31. Complete that legacy row through the guarded commit without creating another receipt. Preserve and reject any mismatch.

32. If the legacy final is absent, retain its receipt and rerender through a fresh owned attempt. Do not adopt an old stage.

33. Cleanup may remove only exact owned files after confirmed commit or definitive rollback. Unknown files, owners, stages, and outcomes remain retained.

## Useful grafts from Candidate B

Adopt Candidate B's table of crash prefixes as test vocabulary. Keep its distinction between durable filesystem objects and completed publication.

Adopt its negative controls for missing owners, symlinks, extra stage files, wrong final bytes, wrong receipt bytes, and foreign claims.

Adopt its explicit rule that arbitrary crashes and I/O errors can leave a filesystem prefix. Recovery classifies that prefix without inferring completion.

These grafts require no checkpoint table or new durable state.

## Rejected choices

Reject `publication_evidence` and its migration. The observed defect does not require another database authority.

Reject `ReceiptDraft`. Canonical `ArtifactReceipt` bytes created before final availability violate the required lifecycle, even outside receipt CAS.

Reject new writes to `finalizing`. They add a recovery state when one guarded completed commit is sufficient.

Reject retained-stage adoption. A missing final artifact must use a fresh owned render attempt.

Reject hashing the final artifact under SQLite. File size makes that lock duration unbounded.

Reject the alive-owner exception to lease expiry. It changes fencing semantics and can preserve a stuck owner indefinitely.

Reject any copy-and-rename fallback across devices. That path needs a separate ownership and durability design.

Reject completion inferred from a final file, a receipt file, or both. Only the completed SQLite commit publishes the job.

## Compatibility gate

Preserve Candidate A's eleven fixtures: four snapshot variants, six plan fixtures spanning schemas 2 through 6, and `ArtifactReceipt` schema 2.

Preserve completed receipt `2f0575ae05c1941e709d0a3c4cc2e7ee12f45b37b8b32ad5384470f190a1e3ef`.

Preserve its output `cb0a07e5099cbe5ecaf22a467e5a02439c543fe7be6cea183d79632d7d99bdbe.mov`.

Preserve the original lifecycle report with SHA-256 `5f7eaa18c2a0763618d49100cb75a86e34dbea9165dc1f7fdfe3f9ba03e5a586`.

Retain the two historical orphan receipts as evidence:

- cancellation: `7b3119b4343932cc61890bd75c822267b8fe52890d6a5d1d7af142cd7e3b14e7`;
- fencing: `cd88959dc13c444402a1a26ce1347c4d1b3928a49ecdb7bcf4ed5dc7aece6548`.

Do not repair, delete, or reinterpret those historical objects. New proof must use copied state or a fresh private root.

## Required proof before acceptance

Run storage-level fault controls at final link, artifact sync, receipt temporary write, receipt link, receipt sync, both SQL updates, and commit response loss.

For every control, record before-and-after artifact, receipt, stage, job, and attempt inventories.

Prove that admitted pre-guard cancellation and fencing add zero final or receipt files. Keep preexisting stage files and historical objects classified separately.

Exercise exact and conflicting shared artifacts, exact and conflicting receipts, cross-device layout, slow sync, database busy, and path replacement.

Exercise two publishers that produce one artifact hash. Require valid independent receipts and one immutable final file.

Use deterministic private hooks for SIGKILL after final linking and after receipt linking. Restart only after the original lease expires or exact fencing succeeds.

Exercise an uncertain commit response. Prove that fresh readback returns success, definitive failure, or `publication_outcome_unknown` without false failure closure.

Reopen legacy `finalizing` rows with present, absent, and mismatched finals. Prove guarded completion or fresh rerender as specified.

Run the complete legacy hash suite unchanged. Reopen the frozen completed schema-3 export and confirm its exact receipt and output identities.

Freeze a fresh producer after implementation. Use fresh intents for cancellation, stale-epoch fencing, SIGKILL recovery, completed export, replay, and reconciliation.

The fresh native controls must bind requests, plans, source bytes, producer, owner, epoch, stages, Receipt3 evidence, clocks, EOF, and final `.mov` bytes.

Independent mastering picture and ROI acceptance remains separate. Publication proof does not establish playback, hearing, creative acceptance, or the full film.

## Scope and residual risk

The selected design prevents new publication files after cancellation or fencing wins before the guard.

It cannot promise zero residue after an arbitrary crash or I/O failure inside the guard. Final files, receipt temporaries, or receipt CAS objects may remain.

Such residue is evidence only. Reconciliation must retain unknown ownership and never convert residue into completed publication.

The design is ready for implementation after the mandatory repairs above. Runtime correctness remains unverified until the fresh proof passes.
