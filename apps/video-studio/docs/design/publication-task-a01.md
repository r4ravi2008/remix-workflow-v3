# Owned artifact publication repair A01

Frozen mastering producer636e5afb publishes ArtifactReceipt CAS documents before its ownership guard.
Actual public cancellation and injected stale fencing each left an unreferenced receipt pointing to an absent .mov.
Neither job completed and neither stale artifact was promoted. Retain every failed observation and receipt.

Design the smallest complete publication boundary through existing Project export/cancel/verify/reconcile operations.
Keep historical serialized plans, snapshots, ArtifactReceipt2 and completed replay exact.
Keep NativeColorMasterV1, Receipt3 evidence, source/output clocks and bounded writer behavior unchanged.
No app mutation belongs to the design candidates. No provider, GPU, Resolve or film mutation belongs to this repair.

State a precise publication linearization point and distinguish content-addressed filesystem objects from completed job publication.
Cancellation or epoch loss admitted before publication must prevent new artifact promotion and ArtifactReceipt CAS publication.
An ArtifactReceipt must never be created while its final artifact is absent or unverified.
Crash and filesystem/SQLite failures can create unknown outcomes. Describe them honestly and preserve recoverable evidence.
Do not claim atomicity across SQLite and the filesystem, or globally no filesystem objects after any process crash.
Do not weaken public cancellation, adopt unknown stage bytes, delete retained failures, or infer completion from a CAS file alone.
Define behavior for cancellation/fence races, existing shared artifacts, promotion failure, receipt-write failure,
database-commit failure, real SIGKILL and legacy/new finalizing recovery. Include lock and lease-renewal behavior.

Explore two complete shapes: a short guarded publication transaction and a separate durable staged-evidence checkpoint.
Compare public depth, failure/recovery clarity, compatibility, contention and proofability.
Provide caller usage, types/signatures, exact sequence, file ownership, schema choices and required negatives.
Read actual exports.rs store_document/read_artifact/export/finish_export and export_stage.rs before proposing a shape.

Evidence: artifacts/scratch-video-goal-20261005/native-project-a01/mastering-native-unit-a01/lifecycle-a01/lifecycle-report-a01.md,
SHA5f7eaa18c2a0763618d49100cb75a86e34dbea9165dc1f7fdfe3f9ba03e5a586.
Code-only mastering review A01 remains frozen and is superseded for acceptance by this actual P1 finding.
Main72frame master plans remain prepared but unexported. A fresh producer and new intents are required after repair.
