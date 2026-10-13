# Implementation review A05

## Result

No P1 defect remains in the reviewed export-staging unit.

The hashed owner directory fixes the former `a-b`/`c` and `a`/`b-c` collision.

The final source also fixes both recovery races found during this review.

A killed producer's complete owned stage is now reclaimed before the next render or promoted-file recovery.

Ownerless, mismatched, unreadable, and structurally unknown stages remain preserved without blocking later epochs.

This prospectively addresses A04's hard-kill disk leak for every stage created by the new owner protocol.

One P2 operational gap remains. Historical flat stages are preserved but absent from reconciliation inventory.

The bounded staging work is ready for the next sequential multi-clip unit.

This result does not establish a general compositor or the completed Panja film.

## Review boundary

The reviewed binary SHA-256 is `359da6e364d6864f8d80995a87be761e225d063679ddaf92d193b697f2c6d93e`.

The reviewed source hashes are:

- `export_stage.rs`: `e96827f6ba5163b9f9b7227c3edaeccc55527d28649b871bdd1b94ea76faef2c`.
- `exports.rs`: `58391682a242b544d8d821c42cb3e021f8cb67f4bea69624586c2d29021335cd`.
- `main.rs`: `0755d6fe92ccbe80678a5ab371c4b5135857d5af299c1a03feb6b52c33bb034a`.
- `Cargo.lock`: `8493110f33b9aad347ce49b2a0389d16fc8998829e94ad997bce9c4bc0919f8d`.

All destructive probes used copied stores under the system temporary directory.

No probe changed the original project database, receipt store, artifact, or source file.

## Stage identity and ownership

Each new directory name hashes the serialized `(project, intent, epoch)` tuple.

This encoding removes delimiter ambiguity before hashing.

The old colliding pairs now produce distinct paths. Cleanup of one path does not affect the other.

`create_dir` exclusively claims the exact stage directory. A second claimant receives `staging_conflict`.

The owner document binds project, intent, epoch, and process identifier.

The creator synchronizes the owner document and directories before native writing begins.

Therefore, a stage containing movie bytes already has durable cleanup authority.

Normal completion and handled failure use the same owner-checking cleanup through `Drop`.

Cleanup accepts only `owner.json` and `movie.mp4`. It rejects links, extra entries, and changed owner documents.

These checks preserve unknown ownership instead of guessing from a filename.

## Recovery and race evidence

I killed the reviewed producer after its stage reached 1,346 bytes.

The copied job still showed epoch 1 as `running`. I expired only that copied lease.

Epoch 2 then completed the same immutable request.

Epoch 1 became `abandoned`, and epoch 2 became `completed`.

Neither hashed stage remained. The recovered output SHA-256 was `fcf878a6cbc30a9c074ed06b414eb433686d00a4e718e3eacc18ef911c206f71`.

I then simulated a crash after promotion with that exact output and receipt.

Epoch 3 returned `replayed: true`, completed the job, and removed epoch 2's recreated stage.

This confirms that reconciliation now runs before the promoted-file recovery return.

I also ran 24 concurrent reconciliation processes against one dead, owned stage.

All 24 processes succeeded. One reported reclamation, none reported false retention, and the stage disappeared.

The original implementation could fail this race when another process removed the owner document first.

`Reclamation::Missing`, `Reclaimed`, and `Retained(reason)` now make the race idempotent.

A crash between directory creation and owner persistence leaves an empty ownerless directory.

Reconciliation reports that directory as retained. A later epoch uses another path and continues.

This conservative residue cannot contain movie bytes because writing starts after owner persistence.

## Project and tenant boundaries

Reconciliation queries terminal attempts for one exact project.

It derives each candidate path from that project, intent, and epoch.

A copied-store probe reclaimed each formerly colliding project independently.

The other project's stage remained until its own project operation ran.

Live owner processes remain protected. A terminal attempt without a stage no longer creates a false retained record.

The editor still has no tenant model. Effect authorization and tenant orchestration remain outside this crate.

The current behavior proves project isolation inside one trusted `Studio` root.

It does not prove hostile multi-tenant filesystem isolation.

## P2: historical flat stages remain outside inventory

The original store still contains these historical files:

- `export-panja-scratch-export-native-roundtrip-v5-1.mp4`, 1,182,950 bytes.
- `export-panja-scratch-export-native-roundtrip-v6-1.mp4`, 1,182,950 bytes.

The public reconciliation operation preserves both files and returns no record for them.

Preservation is correct because the old delimiter-based name cannot establish unique ownership.

However, an operator cannot discover this retained disk usage through the new report.

Add a non-destructive `unowned` inventory for legacy files and unknown directories.

Require explicit migration evidence before quarantining or deleting any legacy entry.

This gap does not affect new hashed stages or block the next rendering unit.

## Capability inventory

The live `discover` output now describes adjacent movie clips on one picture track.

It retains the 240-frame limit, one PCM audio clip, complete coverage, and limited framing modes.

`export_ownership` now scopes cleanup to owner-recorded hashed stages from retired dead owners.

That wording no longer implies cleanup of ambiguous legacy files.

The inventory lists general composition, exact-file creative review, and tenant orchestration as `Planned`.

It exposes no verified capability receipt without an exact completed export intent.

These declarations are factual for the reviewed unit.

## Remaining product boundary

This change does not resolve A04's missing product-level semantic cut-map measurement.

It also adds no layers, transitions, masks, motion, color, text, mixing, or arbitrary retiming.

The canonical audio and source-clock conclusions remain limited to the previously measured selected ranges.

No normal-speed watch or listen occurred. Watched, heard, and creative acceptance remain false.

The Panja hybrid film remains unproduced and unaccepted.

## Validation

`cargo fmt --manifest-path apps/video-studio/Cargo.toml --all -- --check` passed.

`cargo clippy --manifest-path apps/video-studio/Cargo.toml --workspace --all-targets -- -D warnings` passed.

`cargo test --manifest-path apps/video-studio/Cargo.toml --workspace` passed all 24 tests.

The 24 tests comprise 14 library tests, seven project-invariant tests, and three cleanup tests.

The behavioral probes covered hard kill, promoted recovery, concurrent reconciliation, project isolation, ownerless creation, and unknown-file preservation.

No GPU or Resolve operation ran during this review.

Cross-family model review was unavailable. This document does not claim one.
