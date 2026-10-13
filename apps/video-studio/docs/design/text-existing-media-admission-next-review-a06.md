# Existing-media admission next design A06: independent peer review

## Scope and evidence

This is a source and design review of the frozen A06 successor.
I read the complete A05 peer and parent findings.
I read the complete 870-line A05-to-A06 patch against the preserved A05 baseline.
I then checked A06 against the current publication, export, receipt, identity, format, stage, picture, and error owners.

I did not edit product source, build, test, execute a helper, invoke native media, or change application state.
This review is same-family and nonblind because I inherited the earlier design context.

| Evidence | SHA-256 |
| --- | --- |
| A06 design | `c53ea732da16a384c71e1a3f52e65cfda2ca5c9b5bf0ba702ddb20087e858502` |
| A05 design | `2a444f8dc5c92afa7d0524a42aa83b821e13ef0281fdbf5acfc34d4c52862f57` |
| A05 independent review | `da6ac55c34ad7e69b117858bdbcf7b561e6f1d783b23165bd38d135eef793fb5` |
| A05 parent review | `49ccc85aeb4476919a8ff60e5724d7bdbd73a8aa676953a706a576708afb754c` |

All fourteen current product sources match A06's inherited and added bindings.

| Source | SHA-256 |
| --- | --- |
| `model.rs` | `eaad52b1b1c8624654b1308c6b582a9a74cb6ae4870f461eaad2c2f057dcc9b1` |
| `plan.rs` | `17973f3039bf635a02302ebcf0aab8c57d9abd99a00afbe8372ae47d14636ae1` |
| `project.rs` | `a53132da6ff9ccdc6e21a32a7b73d0c833ffb7a35ff177815d6707129480698c` |
| `composition.rs` | `88be6c764fbba6172e519a749abb3bc2651d846016b66c71313618d0461c87b5` |
| `media.rs` | `490fe7871d4521fbd586810bd0ae13d84ca4288bb8c610035b9cb4ea72c91b4d` |
| `layers.rs` | `3b698ffd94edb71e59dcc422fed1a353890c9fbee00dd1ae2d2e6df045660655` |
| `movie.rs` | `5f2a4b45bb90c55ede5708198d09bd8517d6507de2129bb3c09227b1e79c52e3` |
| `pcm.rs` | `7ff87caa9a49b3b5b78a6aacfa10e798069ccf9e7f4216a60464c2c7b20dc76a` |
| `exports.rs` | `13994abea3ae1d42fe4bb7517102cff8a97dcb0b79cb4e2af4c09bec0df6c3fc` |
| `lib.rs` | `499156ec54f3046ce2901bb01ec5361ed755739911624166c971cd42e4bc04f9` |
| `publication.rs` | `4c04efc42972b9fad8f48f4be4e025fdecc6be89876109e6cbbc049bdd15f06a` |
| `identity.rs` | `bf9c70971eb15f58c0c231fcd72722f30cf785178c96abecab0db8cfe02dfab9` |
| `native_format.rs` | `e33d9f9ff7de3e0b8793b5301a465bebcccbe3f4ab496c8454929d498cb19f23` |
| `export_stage.rs` | `83438e828d5a126f48d0240803a9f85196e059a78254996d36a5892293638e5c` |

## Result

A06 closes all three A05 findings at the design level.
It removes whole-body serialization duplication, replaces receipt readback vectors with a bounded chunk, and gives the nested receipt graph finite limits.
It also charges both live `ActiveClaim` owners and the renewal worker's cloned `Project`.
The closed error adapters and one canonical failure body remove arbitrary `Display` allocation and duplicate persistence strings.

Two new P2 ownership gaps remain before Plan8 implementation approval.
There are no P1 findings.

## P2: picture evidence is absent from its construction peak

A06 defines `M_picture_execution` correctly at design lines 1183-1191.
It charges the scope String during publication, verification, and the final `ExportResult`.
The execution formula at lines 1250-1260 does not include that owner.

The current source shows a separate construction overlap:

- `composition.rs:503-513` defines the seven-field evidence with one owned `scope: String`.
- `layers.rs:766-776` constructs that String after track-worker joins but before `decode` returns.
- The `Workers` value, port vectors, plan `Arc`, signal, budget, and PNG mutex remain in the `decode` frame at that point.
- `movie.rs:181-208` retains the outer decode-thread closure and the encoder `result` while joining and receiving the evidence result.
- Writer session and fixed result or callback state remain part of `O_execute_A06` until `write_inner` returns.

A05's execution inventory covers fixed evidence, result, closure, and callback records.
It does not cover `PictureExecutionEvidence.scope` because that is a variable String owner.
Post-write publication and verification peaks cannot account for the earlier allocation event.

Add a terminal execution peak that includes `M_picture_execution` with every still-live execution owner.
The formula must state which media payloads and worker captures have dropped at that exact point.
It must retain the fixed outer `Result` and callback records that have not dropped.

Add a control that constructs a 512-byte scope while the outer result carrier and retained execution captures remain live.
The 513-byte rejection control alone does not prove this overlap.

## P2: existing-verification hashing can own a second hash String

A06 correctly retains `C_verification` while creating `verification_id`.
The `S_hash` row at design line 1558 charges that result.
The fixed 65,536-byte chunk at line 1560 charges existing-file hashing input.

The current collision verifier has another variable owner.
`project.rs:609-627` hashes the existing file and calls `format!("{:x}", digest.finalize())`.
That call creates a second 64-byte String while the expected `verification_id` and canonical verification bytes remain live.

`C_serializer_scalar` does not close this gap as currently defined.
A06 limits that owner to serde scalar conversions during canonical serialization at lines 1339-1341.
The existing-file hash runs after serialization and has a different owner transition.

Choose one explicit Plan8 rule:

1. Compare fixed binary digest bytes against a checked decoded expected hash, without a String allocation.
2. Add one temporary `S_hash` to the existing-verification collision peak and its owner ledger.

Add a collision-path control that keeps `C_verification` and `verification_id` live during the complete file hash.
The control must reject an uncharged hexadecimal formatting allocation.

## Closed A05 findings

### Publication and serialized bodies

A06 distinguishes three bodies with different authority:

- `C_receipt` produces `receipt_id` and moves into `AvailableReceipt`.
- `C_stored` is the database body and survives uncertain-commit classification.
- `C_verification` produces `verification_id` and drops before result construction.

This removes the duplicate artifact-receipt serialization at `publication.rs:245` and `publication.rs:491`.
It retains one distinct stored-body serialization for `publication.rs:561` and removes its repeat at `publication.rs:662`.
It also removes the repeated verification serialization in `exports.rs:1009-1010`.

The current receipt checks allocate whole-body `actual` vectors at `publication.rs:277` and `publication.rs:527-530`.
A06 forbids those vectors and uses one charged 4,096-byte comparison chunk.
The normal and uncertain schedules retain the stored body at the correct commit boundary.

The wrapper terms cover `VerifiedFile`, `AvailableArtifact`, `AvailableReceipt`, and `VerifiedOutput`.
The publication formulas retain the prepared plan, stored receipt, receipt bytes, and live picture evidence where stated.

### Receipt, verification, and claim ownership

The nested receipt table matches the current source shapes.
It covers both track codec Strings, compatible brands, optional PCM and format evidence, and six color Strings.
The field counts match the current structs.

`exports.rs:1216-1223` retains the main claim and moves a clone into `ExportLease`.
`exports.rs:810-837` retains that cloned claim and one cloned `Project` in the renewal worker.
A06 charges both full claims while running and only the main claim after `quiesce` joins the worker.

The verification formulas count the stored and fresh `NativeMeasurements` graphs together.
The final result formula moves the stored receipt, verification, verification ID, and optional picture evidence without duplicate root headers.

### Error adapters and failure persistence

A06's closed adapters avoid arbitrary `Display`, `Debug`, source-chain, and panic-payload formatting.
The fixed classification rules cover I/O, JSON, SQLite, channels, callbacks, panics, and opaque sources.

`CanonicalFailureBody` replaces the two current `error.to_string()` calls in normal failure closure.
It also covers the fenced-attempt update.
The schedule retains one public error and one borrowed persistence body.

## Required repair and review boundary

Preserve A06.
Add the two missing overlap rules in a successor before implementation.
The successor should keep all A06 canonical-body, claim, receipt, compatibility, and error rules unchanged.

This review did not measure `size_of`, allocator capacities, serializer behavior, callback storage, SQLite memory, native-framework memory, or media output.
No Plan8 runtime exists at the reviewed hashes.
