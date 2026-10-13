# A16 recipe receipt-closure rejection addendum

ROOT rejects A16 compilation eligibility for one P2 recipe-integrity finding. This addendum supersedes the earlier zero-P1/P2 compilation-preparation disposition for this finding. The controls-only Rust source repairs remain observed in source. A16 and A08 remain frozen and unexecuted.

The fixed A08 caller requires every recipe source_closure byte or digest scalar to have a corresponding absolute path in the current source proof. A trusted ROOT standard-library data check reproduced that exact loop without importing or executing the caller. Fifty-five scalar receipts match. Three digest fields have no companion path:

- `a15_controls_failure_log_sha256` lacks `a15_controls_failure_log`.
- `a15_compile_measurements_sha256` lacks `a15_compile_measurements`.
- `a15_compile_terminal_closure_sha256` lacks `a15_compile_terminal_closure`.

The preserved A15 attempt already supplies all three evidence files, and the A16 proof already measures them. The repair is to add their exact paths in a separate successor recipe. Do not weaken or skip the caller join. Production logic, control repairs, schemas, schedules, compiler commands, environment and limits must remain unchanged after fixed package-label advancement.

ROOT's earlier 68 path/hash joins checked only fields with existing paths. That check missed these three missing path keys. This correction preserves the measured source evidence but withdraws compilation eligibility. No A08 decision, gate, caller, compiler, controls, bootstrap, authorization, or native producer ran. Peer addendum remains pending.
