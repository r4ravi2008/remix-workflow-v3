# Runner A12 parent source review

ROOT rejects A12 before compilation. Preserve the frozen package and actual read-only source proof unchanged. Two P1 groups and one P2 group remain from the existing A10 repair scope.

## Measured current closure

Manifest: 65,795 bytes, SHA-256 `61257967d62eb3ed62726dfdfce8166fce48e3e27923fff33ed297e074eb080d`. Fifteen source rows contain 426,436 bytes, aggregate `9cc2f86b26bbced320f16c399c796a89ca53eb83fba820bb64ec375ecee0bf76`. The 117 external rows contain 10,863,165 bytes, aggregate `e340b8a379a08fd3cb9ff3cfde1a69ffd34f66a03b4e9137fbb6d4f59a90a056`.

ROOT executed only its externally authenticated read-only source helper. Its bounded functions and classes are unchanged from the actual A10 helper. The helper read 512 files containing 132,734,195 bytes. Every before/after identity matched across nine fields. The 601,948-byte proof hashes to `7965248f00c35fa802fbc2b51a10e307f831f5830a65933348028c76d4ba39de`. It checks 27 literal import edges and 23 Rust source files. The 1,418-byte external authenticated-launch receipt hashes to `dd641ad8b84462f9cc734dd8b5a139ec070121f2db3e596fb5885537c361db5e`.

ROOT read all A10-to-A11 source and descriptive deltas, then all A11-to-A12 source and descriptive deltas. The complete A11-to-A12 library delta contains 368 lines; the remaining delta contains 710 lines. ROOT checked the current latch and production predicate call sites. After source inspection, ROOT independently reopened all 512 current files and matched their bytes, hashes, and nine identity fields.

## P1: exceptional final-loop closure still occurs after outcome construction

The resumed loop can set `reap_failed=true` with no terminal status. If the pipe reaches EOF, the loop exits because its condition excludes a failed reap. The final block around lib.rs 3869 calls `darwin_supervise_terminal_group`, but that helper immediately returns when terminal status is absent.

The function then constructs ChildOutcome with no consumed direct terminal status. Drop completes retained exceptional ownership afterward, so the outcome cannot contain that later status, signal facts, or supervision facts. This is the original A10 final-loop finding. Immediate retention repairs successful waits but does not close this failed-wait path.

Before constructing any outcome, finish direct-child and group supervision when terminal status remains absent. Transfer its terminal status and actual supervision observations into the same report facts. Preserve the initiating cancellation, timeout, or log-overflow failure after eventual closure. Do not use Drop to fill missing outcome facts.

The final `cleanup_unresolved` still ORs `reap_failed` around line 3924. Historical deadline failure and final unresolved ownership are separate states. Keep the historical failure as failure evidence; report final cleanup closure from actual final ownership facts.

## P1: the absence latch is not applied across every signal and cleanup transition

The resumed SIGKILL around line 3740 and pipe-drain SIGKILL around line 3843 record ESRCH but do not transfer that absence into the child owner. A later signal or cleanup can therefore target the same numeric PGID after observed absence.

The no-terminal-status fallback in `darwin_cleanup_child` around line 2917 passes `owned_pgid` to finite cleanup even when the child latch is already true. Drop's finite cleanup around line 2527 also fails to merge the returned `group_absent_latched` before its next absence probe and exceptional handoff. A later numeric reuse can be admitted through those paths.

Route all owned-group signals through the same retained first-absence rule. Carry actual ESRCH and absence observations across resumed, finite, final, exceptional, and Drop paths. Once latched, never re-probe to re-admit that numeric group. Direct-child terminal consumption remains a separate ownership fact.

## P2: the rationale overcorrects production predicate scope

Rationale lines 91–94 now label `descriptor_read_is_allowed`, `esrch_termination_facts`, and `pipe_drain_completion` model-only. Production still calls the first predicate around lib.rs 1988 and the third around line 3836. Only `esrch_termination_facts` has the model-only scope described by the earlier finding.

Correct each predicate's actual scope separately. Also remove the final-closure claim until the first P1 path is repaired. Keep the repaired A05 authorization labels, renamed focused-source description, and all eight process supervision fields.

## Closed source repairs and boundary

The region cause classifier now emits injected truncation and real cap causes separately. The fixed truncation control expects the same code. The initiating failure survives the formerly overwriting assignments and resumed error returns. These are source observations, not executed control results.

No A12 compiler, private control, bootstrap, authorization, native producer, media, GPU, or Resolve operation ran. The A04 process utility and ROOT capsules remain unexecuted. Native, product, WATCHED, HEARD, and creative acceptance remain false. The finite schedules remain ten lifecycle, fifteen focused, twenty-one pure, eleven launch, and five review variants. Peer source review is still pending.
