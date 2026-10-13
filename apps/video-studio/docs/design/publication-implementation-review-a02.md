# Publication implementation review A02

## Result

Accept the current publication implementation as a code-only unit.
No identified P1 or P2 defect remains after the reviewed repairs.

The implementation follows the selected Candidate A contract.
It adds no checkpoint table, receipt draft, stage adoption, or new `finalizing` write.

This review does not accept the complete publication behavior unit.
Fresh native lifecycle, hard-kill recovery, and legacy recovery evidence remains pending.

No cross-family reviewer was available.

## Findings

P1: none.

P2: none after the reviewed repairs.

## Publication ordering and authority

`SealedStage` holds the opened stage payload through publication.
It hashes and syncs the payload before the SQLite publication transaction.

`AvailableArtifact` exists only after an exact final file is available.
It holds the reopened final descriptor, pathname, file identity, size, mode, timestamps, and link count.

The code constructs `ArtifactReceipt` only after `AvailableArtifact` exists.
It never serializes a normal receipt as a pre-publication draft.

Receipt bytes have a 64-KiB admission limit.
Exact receipt reuse reads no more than the admitted extent and requires byte equality.

`AvailableReceipt` holds the reopened receipt descriptor and canonical bytes.
Guarded completion checks both held availability tokens before updates and again before commit.

The code has three distinct authority points:

1. The final hard link establishes artifact visibility.
2. The receipt hard link and directory sync establish receipt visibility.
3. The exact SQLite commit establishes completed publication.

A filesystem prefix never synthesizes completed state.
Rollback can retain an artifact, receipt temporary, or receipt object as non-authoritative evidence.

## Exact claim, cancellation, and lease checks

The renewal predicate binds project, intent, request hash, plan ID, epoch, owner, job, and attempt.
It refuses cancelled, fenced, non-running, or mismatched claims.

The renewal worker is joined before publication acquires `BEGIN IMMEDIATE`.
Shared-final and legacy-final hashing finish while renewal remains active.

The guarded transaction requires the exact renewed deadline and an unexpired lease.
It checks the same job, attempt, owner, request, plan, and cancellation state.

Completion updates exactly one job row and one attempt row.
It checks cancellation and the renewed deadline again before commit.

If cancellation or fencing wins before the guard, no final or receipt file is created.
The owned stage can be removed by its stage guard.

If publication acquires the writer lock first, cancellation waits for the publication result.
The concurrent control confirms that the later cancellation observes `completed`.

Directory sync remains inside the writer transaction.
Those calls have no reliable wall-clock bound, as the design already records.

The final deadline check prevents a slow sync from committing after lease expiry.
Fresh slow-sync and database-busy controls remain required evidence.

## File identity and cleanup

Whole-file verification uses `O_NOFOLLOW` descriptors and before-and-after `fstat` observations.
The descriptor remains open through the guarded pathname check.

An existing shared artifact is fully hashed outside SQLite.
The guard reopens the pathname and requires the previously observed identity.

A newly linked artifact must match the held stage inode and simultaneous post-link observation.
The code retains and rejects a conflicting shared file without overwriting it.

Receipt reuse rejects links, writable files, oversized files, changed bytes, and changed identity.
Final and receipt pathname replacements cannot produce a completed commit.

`ExportStage` retains its original directory descriptor for its full lifetime.
Live cleanup compares the pathname against that descriptor before removing entries.

Cleanup opens entries with `openat` and removes them with `unlinkat`.
It verifies each entry identity and removes the owner document last.

Unknown files, changed owners, ownerless stages, substituted directories, and wrong payloads remain retained.
Reconciliation derives the expected payload from the immutable plan and exact attempt ledger.

These controls cover managed-root substitutions exercised by the tests.
They do not establish safety against an arbitrary hostile writer racing every filesystem operation.

## Commit outcomes and failure closure

An uncertain commit discards the transaction and connection before fresh readback.
Readback binds request, epoch, job owner, attempt owner, state, and exact receipt.

An exact completed job and attempt returns success.
An exact unchanged running state permits definitive failure closure.

Cancellation and a newer epoch receive their own definitive classifications.
Unreadable or inconsistent readback returns `publication_outcome_unknown` without mutation.

The outer export path never converts `publication_outcome_unknown` into a failed job.
The normal publication path retains its owned stage when readback remains unavailable.

All other failure classification and closure occurs in one `BEGIN IMMEDIATE` transaction.
That transaction requires one exact current job and one exact running attempt.

A post-commit verification failure does not demote a completed job.
The verification CAS document is stored only after guarded completion succeeds.

## Legacy recovery and compatibility

Historical `finalizing` remains a read-compatible recovery input.
New publication transitions directly from `running` to `completed`.

Legacy recovery fully hashes the final artifact while renewal remains active.
It also performs source, plan, native-output, and receipt validation before guarded completion.

The recovery path holds exact final and receipt evidence through the completed commit.
It saves the fresh verification document only after that commit succeeds.

An absent legacy final falls through to a fresh owned render.
The code does not adopt retained stage bytes or infer completion from old CAS files.

No database migration or serialized publication checkpoint was added.
Snapshot, Plans 2 through 6, and Receipt 2 retain their exact fixture hashes.

Receipt 3 publication uses the existing mastering format authority.
The publication module does not reinterpret historical H.264 plans through the new profile.

## SQLite contention boundary

Stage hashing, shared-final hashing, legacy-final hashing, native verification, and source verification occur outside SQLite.
The transaction performs metadata checks, bounded receipt checks, short serialization, links, syncs, and two row updates.

The implementation performs no whole-artifact hash while holding SQLite's writer lock.
The remaining directory sync latency is explicit and protected by the final lease check.

## Validation

I independently ran these checks against the reviewed source:

- `cargo fmt --all -- --check`: passed.
- `cargo test --workspace --locked`: 111 tests passed.
- `cargo clippy --workspace --all-targets --locked -- -D warnings`: passed.

The suite contains 16 publication controls.
They cover every declared filesystem and SQL boundary, commit rejection, lost commit response, and unavailable readback.

The controls also cover cancellation-first and guard-first ordering.
They cover shared artifacts, receipt reuse, receipt conflicts, owner substitution, and two concurrent publishers.

The saved 111-test log SHA-256 is `58d484eed6e7b48b39c5cc392a64b8c306fc049212c9c594d71717362fabc6cb`.
The saved Clippy log SHA-256 is `40ed3cffb1f29957d910210d0b4e8fb5ddc4c9c3eb59d4b875eb02ec7845173c`.

## Reviewed source identity

| File | SHA-256 |
| --- | --- |
| `publication.rs` | `c63c5b80b7b6821ddfcf25b91daf708d4a334d35f14eb146b47adcb2389ab62f` |
| `exports.rs` | `dad38033684648fc08640caf7cc50b9586a1fb82eb92470bea883ad45e4c8a22` |
| `export_stage.rs` | `83438e828d5a126f48d0240803a9f85196e059a78254996d36a5892293638e5c` |
| selected judgment | `057ff7af42cbe8b04f62746eaa2d56c8a90f088df5317abbb11be98853536a1e` |

## Remaining acceptance gates

Freeze a fresh producer from the reviewed source.
Use fresh private projects and intents for every publication control.

Complete acceptance still requires these saved results:

1. Exercise public cancellation and stale-epoch fencing before the publication guard.
2. Inject real process termination after final linking and after receipt linking.
3. Reconcile each retained prefix without inferring completion from filesystem state.
4. Exercise exact, absent, and mismatched legacy `finalizing` recovery cases.
5. Exercise slow sync, database busy, cross-device rejection, and uncertain commit readback.
6. Complete a bounded Receipt 3 `.mov` export, replay, verification, and independent reopening.
7. Bind producer, request, plan, sources, owner, epoch, stage, receipt, clocks, EOF, and final bytes.
8. Reopen the historical completed Receipt 2 artifact without changing its receipt or output identity.

Preserve the original A01 lifecycle evidence and both orphan receipt objects unchanged.
They are historical inputs, not proof for this fresh implementation.

Arbitrary crashes and I/O failures can leave filesystem residue.
The implementation promises classification and authority separation, not zero residue.

This review does not establish mastering ROI acceptance, watched playback, heard audio, creative quality, or the full film.
