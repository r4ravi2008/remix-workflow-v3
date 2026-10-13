# Rust producer runner A13 ROOT source review

State: **source rejected before compilation; preserved and unexecuted**.

ROOT read the complete A12-to-A13 library and remaining source/descriptive
deltas. ROOT first read the preliminary 789-line library delta, then the entire
384-line preliminary-to-frozen correction delta. ROOT also read all 759 lines
of the remaining frozen delta and the actual ownership, cleanup, stop/resume,
main lifecycle, signal recording, and outcome functions.

After review, ROOT independently reopened all 534 current measured inputs.
Every byte count, digest, and all nine identity fields matched the canonical
source proof. No package code, utility, capsule, compiler, or control executed.

## Exact measured subject

- Manifest: 73,038 bytes, SHA-256
  `55dacc3b681620113a0b617cf35aa47838ec0c353f5ec5c668928b81a874b0a0`.
- Source aggregate: 15 rows, 442,913 bytes, SHA-256
  `8d5d3c85a786f38c45033a080f248c4098e003088d4c64160b420a58919baed0`.
- External aggregate: 124 rows, 11,562,742 bytes, SHA-256
  `f4c746f3e54c2606f336c67e4cb51641126814a914994bd7a539bcc42b00c419`.
- Canonical proof: 626,904 bytes, SHA-256
  `aa9f4510d3cea5cfdd96975b65cc2c2ee6186b28095726f0fea462fed3bd6836`.
- Actual externally authenticated helper launch: 1,615 bytes, SHA-256
  `e4ffca74c9a6cc621c1b823445def3b3f46f561326dde6aec73ebca0c9e74ab0`.
- Library: 196,411 bytes, SHA-256
  `c60d2e091dca2f45d0a987be7fb30e25977ce80a3db3a7eae2d77811254cda99`.

## Findings

### P1: direct-signal absence does not always revoke direct-PID authority

The exceptional supervisor records its direct SIGKILL errno but does not revoke
either local or retained-owner direct-PID authority after ESRCH. It can later
retry the numeric PID while the owned group remains open and wait reports no
status. This bypasses the finite helper's existing direct-absence policy.

The SIGCONT failure path also enters cleanup without capturing its actual
errno or revoking direct-PID authority on ESRCH. Cleanup can then attempt a
direct SIGKILL after an actual direct-absence observation.

Revoke direct-PID authority immediately on every direct-signal ESRCH. Update
both the local retry policy and retained owner policy. Capture the SIGCONT
error before cleanup so its actual initiating errno survives later syscalls.
An unresolved wait must retain ownership and cannot fabricate terminal status.

### P2: suppressed cleanup can erase actual signal facts

The shared owned-group helper correctly suppresses a latched group. Its default
observation contains no attempt, no delivery, and no errno. Later resumed KILL,
pipe-drain KILL, and `record_cleanup` assign those defaults over previous actual
group observations. The owner latch remains true while published ESRCH evidence
can become false with a null errno.

Update observed signal facts only when the signal was actually attempted.
Preserve previous actual facts across suppressed transitions. Apply this rule
to group, direct, retry, and supervision summaries where defaults can overwrite
earlier observations.

`attempt_term` also writes a SIGTERM observation into `kill_group_errno` and
`kill_group_esrch`. The output schema describes those fields as kill facts.
Keep TERM absence in the owner latch and TERM facts. Record only actual KILL
observations in KILL fields, or explicitly define a compatible historical
meaning that identifies the actual signal. A field name must not silently
change the kind of recorded signal.

## Source repairs observed

The final failed-wait path now finishes retained supervision before selecting
the outcome. Nonretryable wait errors revoke numeric-PID retries. The group
absence latch crosses TERM, resumed KILL, pipe KILL, finite cleanup, exceptional
supervision, terminal cleanup, and Drop. Historical resumed reap failure is
separate from final unresolved cleanup. The region and initiating-cause repairs
remain present. Current fixture and control labels use A13.

These are source observations. No compilation or actual control result exists.
Preserve A13 and repair the two groups in a separate successor. Native, product,
media, watching, hearing, and creative acceptance remain false.
