# Publication implementation review A03

## Result

Accept the current publication crash controls as a code-only extension to A02.
No identified P1 or P2 defect remains after the proof-harness repair.

The production publication algorithm is unchanged from the accepted A02 source.
The new kill points and child driver exist only under `cfg(test)`.

The tests perform real native writes and real process termination on private state.
The retained frozen-producer proof has not run yet.

No cross-family reviewer was available.

## Findings

P1: none.

P2: none after one evidence repair.

### The crash record now binds both ledger rows and the exact stage

The initial parent test checked only the `exports` row before recovery.
It did not bind the matching attempt or the stage that reconciliation removed.

The repaired test records the epoch-1 job and attempt before recovery.
It requires the same owner PID, `running`, no receipt, and no close time.

It derives the stage key from project, intent, and epoch.
It parses the owner document and requires the exact project, intent, epoch, and child PID.

The test inventories every stage entry before recovery.
It requires `movie.mov` for both prefixes and the receipt temporary only after the receipt link.

After recovery, the test requires exactly two attempts.
Epoch 1 must be abandoned with no receipt, while epoch 2 must be completed with the published receipt.

The final record inventories artifacts, receipts, and staging.
It requires the retired stage and the complete staging root to be absent.

This closes the evidence gap without changing production behavior.

## Test-only crash points

`CrashAfterFinalLink` runs immediately after the new final hard link succeeds.
It runs before artifact-directory sync and before receipt construction.

`CrashAfterReceiptLink` runs after the receipt hard link succeeds.
It runs before receipt-directory sync and before either completed update.

Both points send `SIGKILL` to the current test process.
The fallback panic prevents a false pass if the signal does not terminate the child.

The `Point` variants, thread-local selector, signal branch, pause, environment reads, and driver are test-only.
Production builds contain no active environment-controlled crash seam.

I built the release CLI and searched its strings for every private hook identifier.
No crash-point name, pause name, or publication test environment variable was present.

The production and instrumented test executables still require separate frozen identities.
Evidence from the instrumented binary must never be labeled as a production CLI run.

## Native child and recovery shape

The child creates a fresh private `Studio`, project, imports, revision, plan, and export request.
Its fixture contains eight 16-by-16 frames and 16,000 stereo PCM sample frames.

The child saves raw request and plan bytes before export.
It also saves plan ID, producer identity, source hashes, and the selected crash point.

The parent launches its exact current libtest executable with one exact test filter.
It asserts termination by `SIGKILL`, rather than accepting a nonzero exit code.

For each crash point, the parent requires one actual native final artifact.
It requires zero receipts after the final link and one receipt after the receipt link.

Product native verification reopens the prefix artifact.
It observes eight video frames and 16,000 audio sample frames.

The parent then calls the public export operation with the same request.
The dead epoch becomes abandoned, the fresh epoch completes, and staging becomes empty.

Product verification and completed replay must return the same published receipt.
The replay must identify itself as replayed.

An optional exclusive proof root retains fixture inputs, child output, bindings, and both state records.
The default test root is temporary and is removed after success.

## Additional storage controls

The short-lease control links artifact and receipt prefixes under a 200-millisecond injected deadline.
It pauses before commit until the deadline expires.

The completion method returns `worker_fenced` and rolls back both completed updates.
The linked artifact and receipt remain as unpublished evidence.

This is a controlled clock-path test.
It does not claim that a real directory sync stalled for the production 240-second lease.

The SQLite-busy control holds a real `BEGIN IMMEDIATE` writer transaction.
Publication returns a storage failure without creating artifact or receipt files.

The existing job and attempt remain running.
The owned stage guard removes its private stage after the rejected attempt.

## Production invariants retained from A02

The new controls do not change receipt ordering, held final evidence, or held receipt evidence.
They do not change exact claim guards, lease renewal, commit readback, or failure closure.

Production still creates no `ArtifactReceipt` before exact final availability.
Only the exact job-and-attempt commit establishes completed publication.

Whole-file hashing and native verification remain outside SQLite.
Legacy `finalizing` stays read-only compatibility input.

The stage directory remains descriptor-pinned.
Cleanup remains descriptor-relative, owner-last, and conservative around unknown entries.

## Validation

I independently ran these checks against the reviewed source:

- `cargo fmt --all -- --check`: passed.
- `cargo test --workspace --locked`: 115 tests passed.
- `cargo clippy --workspace --all-targets --locked -- -D warnings`: passed.
- `cargo build --release --locked`: passed.
- Production hook-identifier scan: no private test identifier was present.

The saved 115-test log SHA-256 is `8adf971554144da462fd112b6a86434d7af5bd2e7283a106257657828f99f381`.
The saved Clippy log SHA-256 is `acb921d37b216f704af97ba2c126e4f0255024577bcc806a918bd6de6ce651eb`.

## Reviewed source identity

| File | SHA-256 |
| --- | --- |
| `publication.rs` | `7ed1a388e5cbd464603a13390c171070f8f9809efb2a8c3c09e3e81c490caf3f` |
| `exports.rs` | `dad38033684648fc08640caf7cc50b9586a1fb82eb92470bea883ad45e4c8a22` |
| `export_stage.rs` | `83438e828d5a126f48d0240803a9f85196e059a78254996d36a5892293638e5c` |
| A02 review | `ff7d4c1b77d5d502bb708b6ff8f9382044d2390a23ff3579875831b5045d758e` |

## Remaining proof boundary

Freeze the production CLI and instrumented libtest executable as different producers.
Run the parent test once with a fresh retained proof root.

The retained proof must hash the executable, driver, request, plan, inputs, and before-and-after records.
It must preserve both crash prefixes and identify the exact cleanup and recovery actor.

The product-native verifier is not an independent observer.
An independent reader must bind the retained final movie, clocks, EOF, Receipt 3, and source bytes.

The two checkpoints prove process termination after exact link operations.
They do not prove power-loss durability or every possible crash instruction.

Arbitrary crashes can still leave artifact, receipt, temporary, or stage residue.
Such residue remains evidence and never establishes completed publication.

Fresh legacy `finalizing` present, absent, and mismatched controls remain required.
The historical Receipt 2 artifact still requires exact replay under the fresh production verifier.

This review does not establish independent mastering pixels, watched playback, heard audio, creative quality, or the full film.
