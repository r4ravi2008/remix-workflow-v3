# Rust producer runner A02 source peer review

## Scope and manifest verification

This was a read-only, same-family source review. I read the manifest and all
 eight manifest-bound files. The package remains source-authored, unbuilt, and
unexecuted.

| path | bytes | SHA-256 |
| --- | ---: | --- |
| `Cargo.toml` | 490 | `be667c95f7e6c7be680379294c08a5a1caae96f503a3fc7b62a62f758a1bd18c` |
| `README.md` | 1,436 | `55fa9b6637fcb2f3f8dc1cc1e03d1108df2c67040eafc58150f6441535d07786` |
| `output-schema-a02.md` | 2,363 | `2575c2ed4868fc39080b530b31579f8a725ee99af343252a7ce1e9eddaa8bdbd` |
| `pure-fixtures-a02.json` | 4,371 | `fc7ad06497e6616d529775beca74b8fd17246b561dcc0c2b894ce85878dfd785` |
| `runner-contract-a02.md` | 9,608 | `6bcfa0fbda0e49832e2fdcf4838d3228b30369c89c04a12778c901756a289611` |
| `src/lib.rs` | 63,292 | `342274b9fd9b832ec29fa06bf61fccd90d31fb6a3c43049c09806e4ad8270c57` |
| `src/main.rs` | 96 | `8b6a6668260a3a5406eae08c04ead8a9f77cb673c342aa2dd02bf139e05f1125` |
| `src/pure.rs` | 3,268 | `392728f8120ec327729e9beefa8ccc7479b84cad4737c8fa14b327c6ae491a33` |

The manifest aggregate is
`3b01bf68b103588e73e02bc99fd8117a5e451029546d71d6edf4638de62fd99a`.
The eight rows and aggregate matched the current bytes.

## Findings

### P1 — status extraction uses a non-existent `ExitStatusExt::code`

`src/lib.rs:1062` and `src/lib.rs:1375` call
`status.as_ref().and_then(ExitStatusExt::code)`. On Unix, `code` is an
inherent `ExitStatus` method; it is not a member of `ExitStatusExt`. The source
therefore has a compile error in both failure and normal completion paths.
Use `ExitStatus::code` or a closure, while keeping `ExitStatusExt::signal` for
signal extraction.

### P1 — authority and output opens can block indefinitely on a FIFO

`open_path_readonly` at `src/lib.rs:1567-1571` and `open_file_at` at
`src/lib.rs:1587-1590` use blocking `O_RDONLY` before proving that the object is
regular. They serve authority reads through `read_regular_path` at
`src/lib.rs:749-752` and output inventory reads at `src/lib.rs:890-892`.
A path replaced by a FIFO can block before the bounded read, wall clock, or
child cleanup logic starts. Open nonblocking and then validate the descriptor,
or use an equivalent bounded descriptor acquisition path.

### P1 — `producer.log` is reopened without joining the writer descriptor

The runner creates the log descriptor at `src/lib.rs:507-513`, passes that
file to the child loop, then reopens `producer.log` by name at
`src/lib.rs:545-549`. It never records the original writer descriptor's
identity or compares the reopened descriptor with it. A child that replaces
that path can cause the final report to hash a different file than the one
written by the runner. The closure read must retain or compare the original
file identity before accepting the reopened observation.

### P2 — direct-child pipe drain can leave the process group alive

When the direct child exits, the loop sets a one-second pipe deadline at
`src/lib.rs:1341-1363`. At `src/lib.rs:1368-1373`, the deadline only closes the
parent pipe and records `ReapFailure`; it never sends `SIGKILL` to the recorded
process group. A descendant that retains a pipe end can therefore remain alive
after the runner returns. The contract honestly disclaims reaping escaped
descendants, but the implementation also lacks bounded group termination after
the drain deadline. Record this as an explicit lifecycle failure or terminate
the group before closing the pipe.

### P2 — `send_group_signal` delivery failure is treated as successful TERM

`send_group_signal` returns `Ok(false)` for `ESRCH` at `src/lib.rs:1444-1451`.
The cancellation and timeout branches at `src/lib.rs:1193-1227` test only
`.is_err()`, then set `term_sent = true`. The report can therefore claim TERM
was sent when no signal was delivered, and the normal path has no direct-child
fallback for that result. Preserve the boolean and distinguish delivery from
an absent group before proceeding to the KILL and reap phases.

### P2 — post-read path checks compare only device and inode

`read_regular_path` accepts the path-after observation when
`same_directory_anchor` matches at `src/lib.rs:749-756`. Output file inventory
uses the same anchor-only path check at `src/lib.rs:899-902`, even though the
opened descriptor observation includes mode, size, and timestamps. A same-inode
path with changed metadata, or content changed after descriptor observation,
can pass the descriptor-to-name join. The contract should either define the
anchor-only rule explicitly or compare the required full identity and content
state before accepting the row.

### P2 — pure fixtures are not connected to executable source controls

`pure-fixtures-a02.json` declares command, lifecycle, inventory, terminal, and
identity cases. `src/pure.rs` only provides helper functions, and neither
`src/lib.rs` nor `src/main.rs` parses or runs the fixture cases. The CLI exits
at `rust_stage_acceptance_unavailable` before the helpers are used. The package
therefore has no current executable pure-control entry point; later controls
must bind the fixture bytes and assert the helper results before claiming that
coverage.

## Positive observations and limits

The private accepted-qualification boundary is unconstructible to external
callers, and the current pinned loader returns `MissingAcceptance` without
launching a child. The exact command vector, cleared environment, descriptor
relative output traversal, report fallback, acceptance booleans, and closed
completion enum are source-visible.

The source review does not establish compilation, process cleanup, native
execution, codecs, media, audio, GPU, Resolve, or product acceptance. No
source, compiler, helper, child, or native process was executed.
