# Rust producer runner A13 source peer review

## Disposition

**Rejected before compilation.** One P1 ownership group and one P2 evidence
group remain.

A13 closes the two explicit A12 ownership gaps in its ordinary transitions.
It completes failed resumed reap supervision before selecting `ChildOutcome`.
It also carries one monotonic owned-group absence latch through cleanup and
`Drop`.

The exceptional supervisor does not revoke direct-PID authority after its own
direct `SIGKILL` returns `ESRCH`. The resume-failure path has the same missing
revocation boundary. A later suppressed group signal or cleanup pass can also
erase the saved group `ESRCH` observation.

This review is source-only, same-model-family, and nonblind. I read both A12
source reviews and the A12 rejection disposition. I traced the complete
A12-to-A13 source and descriptive delta.

I did not import, compile, test, bootstrap, authorize, stage, or execute this
package. I did not start a child, native framework, media tool, GPU, or Resolve.

## P1 finding

### P1.1: Two direct-signal `ESRCH` paths retain direct-PID authority

`darwin_supervise_exceptional_owner` retries an unconsumed direct PID at fixed
intervals. It saves each direct signal result at `src/lib.rs:2532-2537`.

When that direct `SIGKILL` returns `ESRCH`, the code records the errno only.
It does not clear local `direct_signal_allowed` or
`owner.direct_signal_allowed`. If `waitpid` still returns no status and the
owned group remains present, the next interval can signal the same numeric PID
again. That numeric PID is no longer an owned direct-child authority.

The pre-resume signal path has the same boundary. The direct `SIGCONT` call at
`src/lib.rs:3870-3875` discards its errno. On failure, it enters cleanup with
`child.direct_signal_allowed` unchanged. An `ESRCH` observation therefore does
not revoke later direct `SIGKILL` authority.

A13 correctly revokes direct authority after nonretryable wait errors, group
absence, and finite direct-kill `ESRCH`. See `src/lib.rs:2476-2483`,
`2486-2490`, `2567-2571`, and `3041-3050`. The two paths above bypass that
policy.

Capture the resume signal errno. Revoke direct-PID authority immediately after
either direct-signal `ESRCH`. The exceptional owner must update both its local
policy and the retained owner policy before its next retry interval.

This repair does not need a new public schema or lifecycle matrix. It completes
the A13 direct-PID ownership rule already declared by the contract.

## P2 finding

### P2.1: Later no-attempt transitions erase an actual group `ESRCH`

`attempt_term` records the group errno and `ESRCH` at
`src/lib.rs:4246-4255`. Resumed KILL and pipe-drain KILL record the same facts
at `src/lib.rs:3923-3932` and `4050-4059`.

After the absence latch is set, `darwin_signal_owned_group` returns a default,
unattempted observation. See `src/lib.rs:2891-2893`. The resumed KILL branch
then writes that default over the earlier TERM observation.

`DarwinLaunchFacts::record_cleanup` also unconditionally replaces
`kill_group_errno` and `kill_group_esrch`. See `src/lib.rs:2666-2674`.
Cleanup that correctly suppresses a latched group therefore replaces an actual
`ESRCH` with `None` and `false`.

The safety latch remains intact. The published signal evidence does not.
`output-schema-a13.md` describes observed group errno and `ESRCH` facts, and
`source-rationale-a13.md` says production records actual signal facts.

Update the report fields only when a signal was attempted. Preserve the last
actual observation when a later transition is suppressed by the latch.

## Three-group accounting

1. **Final resumed ownership:** closed in the ordinary source path. A failed
   wait now enters `darwin_cleanup_child` before `ChildOutcome` construction at
   `src/lib.rs:4085-4106`. Terminal status and supervision facts are available
   before report fields are selected.
2. **Historical failure versus final closure:** closed in source.
   `reap_failure_observed` retains the historical failed wait. Final
   `cleanup_unresolved` comes only from the retained cleanup outcome. See
   `src/lib.rs:4087-4099` and `4145-4156`.
3. **Owned-group absence:** closed for the reviewed group transitions. TERM,
   resumed KILL, pipe-drain KILL, finite cleanup, terminal-group supervision,
   and `Drop` share or merge the monotonic latch. P1.1 concerns the separate
   direct-PID authority.

The region-cause repair and initiating-cause repair remain present. Production
still calls `descriptor_read_is_allowed` and `pipe_drain_completion`.
`esrch_termination_facts` remains private model evidence.

The current metadata uses A13 fixture, report, binary, focused-source, and
launch-source names. The process schedule includes `reap_wait_errno`,
`reap_failure_observed`, and all eight cleanup-supervision fields. P2.1 limits
the truthfulness of two existing signal fields.

The static schedules remain ten lifecycle cases, fifteen focused cases,
twenty-one pure cases, eleven launch variants, and five review variants. No A13
control result exists.

## Frozen source receipt

I rehashed every source row and every external `(role,path)` row. I reproduced
both framed aggregates from the declared domains and encodings. Every byte
count and SHA-256 matches. Source paths are unique. External role-path pairs
are unique.

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| `source-manifest-a13.json` | 73,038 | `55dacc3b681620113a0b617cf35aa47838ec0c353f5ec5c668928b81a874b0a0` |
| 15 source rows | 442,913 | `8d5d3c85a786f38c45033a080f248c4098e003088d4c64160b420a58919baed0` |
| 124 external `(role,path)` rows | 11,562,742 | `f4c746f3e54c2606f336c67e4cb51641126814a914994bd7a539bcc42b00c419` |
| `src/lib.rs` | 196,411 | `c60d2e091dca2f45d0a987be7fb30e25977ce80a3db3a7eae2d77811254cda99` |
| `src/pure.rs` | 7,187 | `cc79345d6a994eeb860814aa84ca220f6a6f471ad6f9c28b864ee44742f47f7a` |
| `src/a13_focused_controls.rs` | 67,411 | `bf42c896ea4f9aef21edf2c53981bdc0a486aa6d75f0ce34365ea7afc8b21b33` |
| `src/a13_launch_controls.rs` | 21,491 | `c4cc0dc5b77cd2acb03d9d8f946ca9cf9de821bae9dacabbffb7141168639f20` |
| `direct-build-recipe-a13.json` | 25,273 | `28252040f73d2bdae9869153be7f83b4201b31c892fde8b718b00305bac01db1` |
| `pure-fixtures-a13.json` | 15,816 | `8a37820d7bed097d3aa9c1d23fb0d6e05306692cc5db81275ee142bde832a82c` |

The package remains uncompiled, unstaged, and unexecuted. This review proves no
bootstrap, authorization, child lifecycle, producer output, native behavior,
media output, playback, hearing, or creative acceptance.
