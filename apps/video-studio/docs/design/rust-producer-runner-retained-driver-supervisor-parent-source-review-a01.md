# Retained-driver supervisor A01 ROOT source review

State: **source rejected; unimported and unexecuted**.

ROOT read the complete 20,037-byte supervisor, contract, rationale, and manifest.
ROOT inspected the unchanged A04 dependency's actual suspended launch, terminal
wait, descriptor closure, bounded reads, publication, and absence functions.
ROOT independently checked every manifest row and both aggregates. This review
does not grant control or native execution authority.

## Exact frozen subject

- Manifest: 2,305 bytes, SHA-256
  `a5f530b71de4eb8989b9b2959a968fd0551f247b37c633b96af0544dae2e936d`.
- Supervisor: 20,037 bytes, SHA-256
  `084484e3f443dde25e5a9dd561b86840efd47496f965ec43e3c9a595cfc2a7f3`.
- Source aggregate: 3 rows, 25,054 bytes, SHA-256
  `e93680b389f47f4a4bdaac65deb10e49b49491263b8786f4d29c56802dc655af`.
- External A04 utility: 46,572 bytes, SHA-256
  `b903a9aff1cc2d8dae73b16800f177322b000b2983e5a45206a639326727d47d`.

## Findings

### P1: pre-resume cleanup can signal an already reaped PID

`_terminate_stopped_child` checks only the PID and `sigcontAttempted` before
calling `os.kill(pid, SIGKILL)`. The accepted A04 `attest_and_resume` records
`terminal_wait_status` and `returncode` when `waitpid` reports a terminal child
before the stop boundary. It then raises `child_terminal_before_stop`.
The supervisor's setup handler calls `_terminate_stopped_child` on that path.
The helper therefore signals the numeric PID after the direct child was reaped.
PID reuse can make that signal target another process.

Guard known terminal status before every direct signal. Preserve terminal facts
and finish readback without signalling a reaped child. An uncertain wait
observation must not create new numeric-PID signal authority.

### P2: a nonzero driver exit can report `phaseFailed=false`

The returned `phaseFailed` expression includes setup, deadline, overflow, and
observation errors. It omits the actual driver return code. A driver that exits
with a nonzero code and closes normally can return `outerClosureComplete=true`
and `phaseFailed=false`. The contract supplies no accepted-exit-code parameter
or alternative definition of success. The generic phase result therefore
misstates the driver's failure.

Define the accepted return-code policy in the contract and enforce it in the
result. For the current positive control and native driver, a nonzero exit must
remain failed even when all outer ownership facts close successfully.

## Bounded conclusions

The post-resume loop sends no TERM or KILL. It retains the driver and bounded
stream buffers after ordinary deadline and observation failures. Its returned
object keeps nested report, nested process, native, and product acceptance false.
These source observations do not establish runtime closure. Peer review remains
separate. Preserve A01 and repair the two findings in a new source successor.
