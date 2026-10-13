# Rust producer runner A12 source peer review

## Disposition

**Rejected before compilation.** Two P1 groups and one P2 metadata group remain.

A12 closes the region-cause mapping and preserves the initiating failure in the
edited error paths. It does not complete child supervision before every outcome.
It also does not carry group absence across every signal and cleanup transition.

This review is source-only, same-model-family, and nonblind. I read the final
A10 root review, peer review, rejection disposition, and the A11 incomplete
handoff disposition. I traced the complete A11-to-A12 source and document delta.
Root disclosed its separate A12 findings after my initial lifecycle trace.

I did not import, compile, test, bootstrap, authorize, stage, or execute this
package. I did not start a child, native framework, media tool, GPU, or Resolve.

## P1 findings

### P1.1: A failed resumed reap can finish supervision after outcome construction

The resumed loop can reach `reap_failed=true` while `status` remains absent.
`src/lib.rs:3755-3769` combines `Ok(None)` and every wait error into that state.
If the pipe then reaches EOF, the condition at `src/lib.rs:3719` ends the loop.

The final block copies the absent status at `src/lib.rs:3873-3875`.
`darwin_supervise_terminal_group` immediately returns for that absent status at
`src/lib.rs:2971-2974`. The function then constructs `ChildOutcome` at
`src/lib.rs:3877-3932`.

`DarwinSpawned::drop` can run finite cleanup and exceptional supervision after
the outcome fields have been selected. Any terminal status, signal evidence, or
supervision evidence learned there cannot enter that outcome. The output keeps
`cleanup_unresolved=true` because `src/lib.rs:3924` ORs the historical
`reap_failed` flag into the final ownership fact.

This path also loses the distinction between `Ok(None)` and a nonretryable wait
error. Drop can call `darwin_kill_and_reap_observed` at
`src/lib.rs:2522-2533`. That helper signals the direct PID before waiting. A
nonretryable wait did not prove that the numeric PID still identifies the owned
child.

Complete the retained supervision before constructing `ChildOutcome`. Merge
its terminal status and actual cleanup evidence into `DarwinLaunchFacts`.
Retain the historical reap failure separately from final ownership closure.

### P1.2: The absence latch does not cover every owned-group transition

The local latch works inside `darwin_supervise_exceptional_owner`. Several
paths lose an earlier absence observation before entering that helper.

- `send_group_signal` returns `false` only for `ESRCH` at
  `src/lib.rs:4006-4013`. `attempt_term` records only delivery at
  `src/lib.rs:4016-4023`. It does not latch absence on the child. The resumed
  loop can later send `SIGKILL` to the same numeric group.
- The resumed `SIGKILL` at `src/lib.rs:3740-3753` records `ESRCH` in launch
  facts. It does not update `child.group_absent_latched`.
- The pipe-drain `SIGKILL` at `src/lib.rs:3843-3846` has the same gap. It then
  enters cleanup, which can signal the group again.
- `darwin_cleanup_child` filters only ownership and numeric equality at
  `src/lib.rs:2906`. Its no-status branch passes that group into finite cleanup
  at `src/lib.rs:2917`, even when the child latch is already true.
- `darwin_supervise_terminal_group` receives a latched result from exceptional
  supervision. It records report facts at `src/lib.rs:2982-2989`, but does not
  transfer the latch back to the child owner before Drop.
- Drop receives `group_absent_latched` from finite cleanup at
  `src/lib.rs:2527-2533`. It does not merge that value before the new absence
  probe at `src/lib.rs:2535-2539`.

A group can disappear, produce `ESRCH`, and later reuse the same numeric PGID.
These paths can treat the reused group as owned and signal it. Carry one
monotonic owner-side latch through TERM, resumed KILL, pipe cleanup, finite
cleanup, exceptional supervision, terminal-group cleanup, and Drop. Never
re-probe a latched numeric group to make it eligible again.

## P2 finding

### P2.1: Descriptive metadata still disagrees with the frozen source

`source-rationale-a12.md:91-94` calls three predicates model-only.
Production calls `descriptor_read_is_allowed` at `src/lib.rs:1988` and
`pipe_drain_completion` at `src/lib.rs:3836`. Only
`esrch_termination_facts` remains confined to private controls.

The rationale also says final `cleanup_unresolved` reflects final owner closure
at `source-rationale-a12.md:83-90`. P1.1 shows that Drop can learn closure only
after the outcome fields are selected.

The manifest's `control_scope` retains A11 names. It names
`pure-fixtures-a11.json`, A11 report paths, the A11 control binary, and A11
focused and launch source files at `source-manifest-a12.json:1021-1028` and
`source-manifest-a12.json:1080-1085`. The frozen package uses the A12 fixture,
binary, reports, and renamed source leaves.

The measured A05 authorization labels are correct elsewhere. The direct recipe
also lists all eight cleanup-supervision fields. Keep those repairs and correct
only the remaining scope statements and A11 control metadata.

## Five-group accounting

1. **Resumed terminal ownership:** partially repaired. Successful waits call
   `darwin_retain_terminal_status` immediately. P1.1 leaves the failed-wait,
   early-EOF path open.
2. **Owned-group absence:** partially repaired. Exceptional supervision holds
   a monotonic local latch. P1.2 leaves resumed, finite, terminal, and Drop
   transfers open.
3. **Region causes:** closed in source. `region_scan_failure_code` separates
   timeout, injected truncation, real cap exhaustion, and other failure. The
   eleven-row launch schedule expects `loaded_region_walk_truncated` for its
   truncation row.
4. **Initiating failure:** closed in the edited source paths. Cancellation,
   timeout, and log overflow survive reap and pipe failures. P1.1 still blocks
   truthful final cleanup evidence.
5. **Descriptive metadata:** partially repaired. Authorization labels, the A12
   focused leaf, and the eight supervision fields are correct in the main
   contracts. P2.1 identifies the remaining rationale and manifest drift.

The static schedules remain ten lifecycle cases, fifteen focused cases,
twenty-one pure cases, eleven launch variants, and five review variants. This
count check is source evidence. No control result exists for A12.

## Frozen source receipt

I rehashed every source row and every external `(role,path)` row. I reproduced
both framed aggregates from the declared domains and recipes. Every byte count
and SHA-256 matches. Source paths are unique. External role-path pairs are
unique.

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| `source-manifest-a12.json` | 65,795 | `61257967d62eb3ed62726dfdfce8166fce48e3e27923fff33ed297e074eb080d` |
| 15 source rows | 426,436 | `9cc2f86b26bbced320f16c399c796a89ca53eb83fba820bb64ec375ecee0bf76` |
| 117 external `(role,path)` rows | 10,863,165 | `e340b8a379a08fd3cb9ff3cfde1a69ffd34f66a03b4e9137fbb6d4f59a90a056` |
| `src/lib.rs` | 185,253 | `3a695544d1425bb4c50021bf459ac34071a4c6aad0165311c4795826ebf13701` |
| `src/pure.rs` | 7,187 | `cc79345d6a994eeb860814aa84ca220f6a6f471ad6f9c28b864ee44742f47f7a` |
| `src/a12_launch_controls.rs` | 21,491 | `52d1cf68855901eb9225c8c8585ec5c5cf894e9070e5eaa54b915f08adeee597` |
| `src/a12_focused_controls.rs` | 67,411 | `7c29b3f2fbb37b037f44eacca64024621c851578d7b0d72962a1dc282c02d3e0` |
| `direct-build-recipe-a12.json` | 22,264 | `ec2438cd3384ad9144abe9e0ddb5bcc691a753d2eb07ec465695537225cb8e89` |
| `pure-fixtures-a12.json` | 15,816 | `2ed8a9926babc2237387f60869fa4fc077b68f08f022b7f728a80d0c29604199` |

The package remains uncompiled, unstaged, and unexecuted. This review proves no
bootstrap, authorization, child lifecycle, producer output, native behavior,
media output, playback, hearing, or creative acceptance.
