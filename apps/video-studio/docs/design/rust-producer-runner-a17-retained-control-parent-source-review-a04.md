# A17 retained-control A04 ROOT source review

ROOT accepts frozen A04 source with zero P1/P2 findings. This source review permits preparation of the separate retained-control gate. It grants no control execution by itself.

Bound source manifest has 45050 bytes and SHA-256 `e3401393028553f925b6ab4ac7c40ecc2a5bfa4bc43b1bf1776a6bf31daafbaf`. Caller has 87927 bytes and SHA-256 `198f5e7a6a9213800da70a05aeb9b35c71ebabb4624d7a1224aa7bb9e6da661f`. Contract, rationale, and saved A03-to-A04 patch match the manifest's other three source rows.

ROOT's trusted standard-library held reader remeasured all 98 manifest/source/external records. Every byte/hash pin and all nine identity fields matched during held reads and fresh reopens. Both framed aggregates match. Source has 4 rows and 161314 bytes with SHA-256 `1d18e6c36621b7190d98f5f8d383ec1b89e58a4bdbae9d86e859f7dacda8e126`. External evidence has 93 rows and 77121587 bytes with SHA-256 `3571d894464848163d965fdd9c518400c685d96b0cc81e3ea08769de389541ea`. ROOT proof has 60254 bytes and SHA-256 `be8f4e522647eaa0e526d13c0782ee0623f7d57e4ae98ac626cc575cd6e7478b`.

ROOT read the complete contract and rationale, current authority/gate setup, all 16 added observation validators, both changed failure/evidence functions, and the retained invocation and nested-report verification flow. Eleven inherited function ASTs match A03 after fixed subject labels. The two changed functions are `retained_control_execution_facts` and `caller_failure_hook`.

The compiler loop owns `build_command`. No assignment targets `phase`. `retained_phase` has exactly two stores: initialization and the synchronous Supervisor result. There is no ordinary `run_phase` call. Failure publication cannot reuse compiler-loop evidence.

The exact observation schemas have 49 returned, 21 pre-resume failure, 18 pre-resume unresolved, and 16 post-resume failure fields. Validators check all nested identities, receipts, cwd/executable/group joins, wait status, signal relations, failure counters and prefixes, stream caps, deadline, closure relations, and false scope fields. Invalid or absent evidence yields null process/resume/execution facts. Attempted SIGCONT without proven delivery preserves unknown control execution. Failed evidence cannot satisfy the successful candidate gate.

The actual four-build measurements and terminal are joined by complete identity-bearing receipts. The accepted compilation readback is the existing UNIT-level 13-key record. The caller requires four closed successful compiler commands and the exact A09 compile gate. Accepted A17 source reviews, current proof, recipe, helper evidence, A09 original peer review, severity addendum, combined source acceptance, and ROOT/peer build evidence remain bound.

Supervisor A02 owns the driver synchronously. All eight accepted authorities include its post-drift rejoin and disposition. Continuous immutability remains false. The 900-second deadline observes failure without destructive outer signals after resume. The caller checks nested reports only after Supervisor returns and closes its own descriptors before terminal publication.

The schedules remain 21 pure, 10 lifecycle, 15 focused, 11 suspended-launch, and 5 nested review variants. All three malformed collision fixtures retain their exact bytes and hashes. The launch process schema has all 47 fields. Actual output reports, marker rules, input stability, current files, nested PIDs, owned groups, and process absence must pass before a candidate can be reported.

An authenticated external launcher must bind current held caller bytes, canonical isolated Python, the exact accepted build readback, and the new gate. Actual controls still require independent ROOT and peer readback. This review imports or executes no candidate. Native producer output, loaded dependencies, maintained editor integration, tenant application behavior, full-film playback, listening, and creative acceptance remain pending.
