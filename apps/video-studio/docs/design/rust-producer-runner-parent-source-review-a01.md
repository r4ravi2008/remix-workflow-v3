# Rust producer stage runner A01 parent source review

A01 remains source-only and rejected before compilation or execution.
Root read all 1,400 library lines, 90 pure-module lines, five main lines,
the contract, output schema, fixtures, Cargo metadata, README, and manifest.
Rust qualification remains independent of Swift and comparator evidence.

The library SHA-256 is
`f0ef0b119c041f80fb56b06c5b8c7d54af95bf84cc712ba0955ea9b3adc1afb3`.
The frozen manifest declares eight rows and 70,129 bytes.
No source, compiler, native producer, or media operation ran during this review.

## P1: compile blockers

`StableIdentity` derives Eq and PartialEq and separately implements both traits.
Those duplicate implementations cannot compile.
The macOS `raw_stat` also assigns `st_mode` directly to a u32 field.
The macOS libc field needs explicit conversion.
Preserve A01 and correct these exact declarations in A02.

## P1: process closure can exceed its deadline

The `Command` still owns pipe write handles after spawn.
Keeping those handles prevents the reader from observing EOF.
Drop the parent command immediately after spawning its child.

`cleanup_child`, the invalid-PID branch, and the reap-deadline branch call
blocking `child.wait()` without a deadline.
The latter explicitly waits after its one-second deadline expires.
Use bounded polling and record unresolved direct-child closure as a failure.
All exception paths must retain actual PID, group, signal, and reap facts.

When the direct child exits, timeout and cancellation are no longer checked.
A descendant can keep the pipe readable indefinitely.
An unresponsive pipe must receive a finite closure deadline and failure disposition.
Closing the pipe after its deadline must not become completed evidence.

## P1: fresh run ownership rejects the expected writes

The runner compares the entire initial directory identity after creating
`producer.log`, `probe-output`, and possibly `cancel-marker`.
Those legitimate writes change directory size, mtime, and ctime.
This check prevents an ordinary successful run from completing.
Separate stable object ownership from expected mutable directory observations.
Join the retained run descriptor to the parent entry before publication.

Repeated directory scans use `dup` before `fdopendir`.
The duplicate shares the directory offset with the retained descriptor.
Use a fresh descriptor-relative directory stream for each scan.
Do not turn directory-reading errors into an empty entry list.

## P1: fallback publication retains a pending completion

`save_terminal_report` can return a fallback reference after the primary write fails.
The returned `ClosedProducerRun` still copies the earlier pending completion.
Return the publication disposition and replace completion with terminal failure.
Serialization overflow also needs the contract's bounded causal fallback.
The fallback schema must consistently include the declared false acceptance fields.

## P2: resource and pathname ownership remain incomplete

The terminal-publication `?` exits without closing raw parent and run descriptors.
Adopt narrow owned-descriptor guards for all paths, including prelaunch pipe failures.

`observe_fd` compares descriptor facts only.
Authority reads and output file inventory do not join the final pathname to that descriptor.
Output files also omit the pre-open stat-to-descriptor comparison used for directories.
Keep no-follow descriptor-relative path joins before and after reads.
Reject ordinary file hard links if the promised link exclusion includes them.

## P2: closed result is publicly mutable

`ClosedProducerRun` exposes mutable public lifecycle and completion fields.
A caller can change the returned completion to pending and serialize the change.
Keep the trusted result fields private and provide read-only accessors.
The current loader remains unavailable and cannot authorize a run.

## Disposition

Preserve the exact A01 package and author a narrow A02 repair.
Add finite pure cases for the corrected completion and ownership seams.
Root will perform a fixed build only after successor source review.
This review establishes no process capture, signal delivery, reaping,
native output, loaded code, product integration, watched, heard, or creative acceptance.
