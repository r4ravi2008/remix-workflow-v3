# Rust producer runner source controls A02 peer review

## Disposition

This is an independent, read-only, same-family source review. I read the
complete A02 control extension, contract, assembly recipe, manifest, copied
A04 runner, and copied pure helper. I compared the A01 extension and its five
separate P2 findings with the A02 source delta.

The package remains source-authored, unassembled, uncompiled, and unexecuted.
It starts no native, media, observer, comparator, Swift, GPU, Resolve, FFmpeg,
libav, or product process. It makes no WATCHED, HEARD, audio, creative, or
native-acceptance claim.

A02 closes the five A01 findings as follows:

1. The aggregate-domain finding is closed.
2. The unavailable-loader bound is materially repaired, but one P2 remains
   for unbounded child waits after kill.
3. Cancellation and overflow now require delivered TERM signals.
4. Cleanup fallback now records signal outcomes and checks final absence.
5. Terminal fallback assertions now check schema, error code, and phase.

## Source identity and aggregate verification

The package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-source-controls-a02`

`source-manifest-a02.json` is 2,181 bytes with SHA-256
`b50c1abe5a136b5a26dd7f0ff7222cea580c7b3b923eef963cf93ede8053a065`.
The five manifest rows match the current files:

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| `assembly-recipe-a02.json` | 4,871 | `44cf418e4a65d0fdd285e7bcd7cb6cada69901d8ecc14f6c8e098ce27d8a1cf6` |
| `control-contract-a02.md` | 9,018 | `726cb8b8bb6605b8fb19aa348b32d9d63007cd297a699cb3116d3f598e739a69` |
| `control-extension-a02.rs` | 56,001 | `6e4746116b6e711afc4501c7f516d1505e55a46d8822180196eb8fe5033f9d41` |
| `pure.rs` | 3,969 | `b76f4edd50ca097e7aadb458c2325b02b874f9fdb1162a3f887c1c1f08c4ed1e` |
| `runner-lib-a04.rs` | 65,284 | `2414938b08c109d4953d11ec2962aa8095f01f7cb47e2936ed2e4dd9206e055b` |

The declared aggregate domain is
`native-text-rust-producer-runner-source-controls-a02-source-v1`.
I independently recomputed the declared recipe:

```text
sha256(domain_utf8 || 0x00 || each_sorted(
  u32be(path_bytes) || path_utf8 || u64be(file_bytes) || raw_sha256
))
```

The recomputed aggregate is
`7421ed2533053ebe893dcebc809017d1ab4db27318f1038bb607d5fbb90b762d`.
It matches `source_aggregate_sha256`.

The copied A04 files are byte-identical to A04 `src/lib.rs` and `src/pure.rs`.
Their A04 authority remains manifest
`961dd0e2cd7525ec8523958a97a0ac109aabfcac3393adfb1b36d846c9280576`, source
aggregate
`c658f23cd62b58cfb698ee2738cecbc2bb9ac7fa8e17062dfc642d7eca9a890a`, and
library and pure hashes listed above.

The A02 assembly recipe specifies a 65,284-byte A04 prefix, a 56,001-byte
extension, no separator, and a 121,285-byte expected crate root with SHA-256
`ea13054c96d220bff55b386ef6cde6ce4537ef46951b93514e13e1b0af45e0ef`.
I did not assemble or hash that target because this review is source-only.

## A01 finding reconciliation

### Aggregate domain — closed

A01 used a `domain_utf8` placeholder. A02 records the exact domain in both the
manifest and contract. The independent recomputation above reproduces the
aggregate. The manifest is excluded from its own five-row input set.

### Unavailable-loader child bound — repaired with one residual P2

`control_run_unavailable_loader_a02` at
`control-extension-a02.rs:314-459` replaces `Command::output()` with spawned
pipes, nonblocking descriptors, an eight-second polling deadline, 64 KiB
retention caps per stream, and a 64 KiB per-poll drain cap. The success
predicate at `:214-268` requires the exact unavailable JSON, empty stderr,
zero output entries, both EOF flags, no overflow, no timeout, no direct kill,
no stream error, and a successful reap.

A residual P2 remains. After timeout, stream error, or overflow, the function
calls `child.kill()` and then calls `child.wait()` unconditionally at
`:402-413`. The missing-pipe and failed-nonblocking branches also call
`kill()` followed by `wait()` at `:333-355`. `Child::wait()` has no deadline.
If kill fails or the child does not reap, the control can block beyond its
8-second polling and 3-second drain bounds. The fake-holder write-error path
has the same unbounded `holder.wait()` after `holder.kill()` at `:1108-1116`.

A successor should poll `try_wait()` until a fixed cleanup deadline, retain the
actual kill and reap outcomes, and publish a bounded failure when the child
remains. It should not convert an incomplete reap into a successful loader
case. This finding is source-only; no runtime hang was executed here.

The cancellation helper has a separate failed-path limitation. If both
bounded receives expire, `control_cancellation_a02` drops the thread handle
without joining it at `:589-599`. The case then fails and does not qualify a
result, so this is not a false pass. A later control repair should record a
bounded thread-completion disposition if it needs to claim complete teardown.

### TERM delivery — closed

`control_cancellation_a02` at `:610-622` requires `term_requested`,
`term_attempted`, `term_delivered`, and `reap_completed`, plus a zero-byte
cancel marker, final child absence, preserved readiness, and false acceptance
scope. `control_log_overflow_a02` at `:659-666` requires the same three TERM
facts, direct-child reap, the exact 4 MiB report byte count, and false scope.
This closes A01's attempted-versus-delivered gap.

### Cleanup fallback — closed for the published case predicates

`ControlCleanupObservationA02` at `:94-101` records PID, process group,
group-signal delivery, direct-signal delivery, and final absence.
`control_signal_and_observe_absence_a02` at `:1355-1374` avoids killing the
controller's own process group and performs a bounded absence check.
Cancellation records fallback facts at `:590-602` and requires final absence
when fallback occurred. The pipe-holder case records its fallback at
`:696-718`, requires disappearance before the normal pass, and retains the
fallback result when cleanup was needed. These controls preserve failed
cleanup evidence instead of accepting it.

The source does not prove kernel-wide descendant cleanup. Its pipe-holder
case is a bounded direct/group process check and states that scope explicitly
in the contract.

### Terminal causal assertions — closed

`control_terminal_collision_a02` at `:792-828` now requires runner schema,
`native_attempt_terminal_report_failure_preserved`,
`error.code == "terminal_report_name_collision"`,
`error.phase == "terminal_publication"`, both acceptance fields false, the
unchanged sentinel, and the expected failure report path. The double-collision
case still requires `RunnerError::TerminalPublication` and both unchanged
sentinels. This closes A01's non-causal fallback acceptance risk.

## Control schedule and ownership observations

The extension preserves the ten A01 case IDs and order at
`control-extension-a02.rs:20-30`:

1. `unavailable_loader_no_output`
2. `normal_exact_argv`
3. `nonzero_failure_preserved`
4. `cancellation_process_closure`
5. `log_overflow_process_closure`
6. `post_reap_group_pipe_cleanup`
7. `producer_log_replacement_detected`
8. `fifo_authority_rejected_nonblocking`
9. `terminal_collision_fallback`
10. `double_terminal_collision_preserved`

`control_main_a02` at `:118-211` requires ten ordered results, counts passed
results, serializes a 256 KiB-capped report, writes it exclusively, and prints
a summary only after the report write succeeds. Native, product, audio,
watched, heard, creative, framework, media, GPU, and Resolve fields are false.

`control_stage_fixture_a02` and `control_qualification_a02` at `:859-947`
create private fixture authorities and use only the private A04 accepted
boundary. The fake producer at `:961-1179` checks the exact ten argument
positions, absolute paths, current directory, and four-variable environment.
Fixture outputs and sentinels use exclusive creation. The control extension
provides no production constructor or trust loader.

The FIFO case uses a real FIFO authority row and requires bounded preflight
failure before producer start. The log replacement case preserves the moved
original and rejects the replacement pathname. These cases remain negative
controls; they do not establish production output validity.

## Limits

This review did not assemble the crate, compile it, import it, run the ten
controls, spawn a child, invoke a subprocess, or invoke native or media APIs.
It does not establish that the extension compiles, that controls pass, that
cleanup works at runtime, or that A04 qualification, media, audio, GPU,
Resolve, WATCHED, HEARD, or creative behavior works.

The open P2 is the unbounded `wait()` cleanup path described above. The
cancellation detached-thread note is a failed-path teardown limitation. A
future bounded repair must preserve the A02 manifest recipe, exact A04 prefix,
all ten case IDs, and the false native/product scope.
