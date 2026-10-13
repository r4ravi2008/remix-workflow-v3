# Rust producer runner source controls A03 peer review

## Disposition

This is an independent, read-only, same-family source review. I read the
complete A03 extension, contract, assembly recipe, manifest, copied A04
runner, and copied pure helper. I compared the A02 extension and its residual
blocking-wait finding with the A03 source delta.

The package remains source-authored, unassembled, uncompiled, and unexecuted.
It starts no native, media, observer, comparator, Swift, GPU, Resolve, FFmpeg,
libav, or product process. It makes no WATCHED, HEARD, audio, creative, or
native-acceptance claim.

A03 closes the A02 blocking-wait finding in the source control paths. I found
no new P1 or P2 source defect within the requested bounded reap scope. A
failed reap can still leave an uncooperative process alive after its explicit
three-second bound. The control records that failure and does not accept it.
That is a bounded failed-path limitation, not a false acceptance.

## Source identity and aggregate verification

The package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-source-controls-a03`

`source-manifest-a03.json` is 2,181 bytes with SHA-256
`72218d2fb6bdcc98a4de5c7e38fedd46830111d13a09b4837cae38186a41c8e6`.
All five manifest rows match the current files:

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| `assembly-recipe-a03.json` | 4,871 | `cf2ba1749bad1b7e040e1e4441c1f19e446e351f370a547c475f754532dc6605` |
| `control-contract-a03.md` | 9,837 | `5cd04181c74828a4dc17507b9a13420dbaa6b4c6a0346e3c5439412833ec8ac3` |
| `control-extension-a03.rs` | 60,392 | `631bbc7b4f0e4792771ac2f383623760365ac27b0f053a4a6fca63fbb0619f21` |
| `pure.rs` | 3,969 | `b76f4edd50ca097e7aadb458c2325b02b874f9fdb1162a3f887c1c1f08c4ed1e` |
| `runner-lib-a04.rs` | 65,284 | `2414938b08c109d4953d11ec2962aa8095f01f7cb47e2936ed2e4dd9206e055b` |

The declared aggregate domain is
`native-text-rust-producer-runner-source-controls-a03-source-v1`.
I independently recomputed the declared recipe:

```text
sha256(domain_utf8 || 0x00 || each_sorted(
  u32be(path_bytes) || path_utf8 || u64be(file_bytes) || raw_sha256
))
```

The recomputed aggregate is
`b1997fe02e9c787cc9d658c8d56c54379a02b85285323552c74b4554a2c28a6f`.
It matches `source_aggregate_sha256`.

The copied A04 library and pure helper are byte-identical to A04 `src/lib.rs`
and `src/pure.rs`. The fixed A04 authority remains manifest
`961dd0e2cd7525ec8523958a97a0ac109aabfcac3393adfb1b36d846c9280576`, source
aggregate
`c658f23cd62b58cfb698ee2738cecbc2bb9ac7fa8e17062dfc642d7eca9a890a`, and
library and pure hashes listed above.

The A03 recipe specifies a 65,284-byte A04 prefix, a 60,392-byte extension,
no separator, and a 125,676-byte expected crate root with SHA-256
`fe12a6a1e2ce8dc3a202636136d1ee7ff75868f26fba8528ed49e491eb95fb47`.
The lengths add exactly. I did not assemble or hash that target because this
review is source-only.

## A02 residual finding review

### Bounded loader reap — closed in source

A03 adds `control_reap_loader_child_a03` at
`control-extension-a03.rs:303-336`. It calls `Child::try_wait()` only, sleeps
in 20 ms increments, and stops after `CONTROL_CLEANUP_WAIT_A03` at three
seconds. It returns separate `status`, `timed_out`, and `wait_error` fields.
The extension contains no `.wait()` call.

`control_run_unavailable_loader_a03` at `:417-579` uses this helper after a
poll timeout, stream error, overflow, missing stdout or stderr, and failed
nonblocking setup. The normal status path preserves the status returned by
`try_wait()`. It derives the exit code and terminating signal from the same
status. A timeout or reap error becomes an observed failure. The unavailable
case requires exit 78, no terminating signal, exact JSON, both EOF flags, no
overflow, no timeout, no direct kill, successful reap, no reap error, and zero
output entries at `:262-277`.

The fake pipe-holder PID-write failure at `:1231-1242` uses the same bounded
abort helper. It no longer calls blocking `holder.wait()`.

`control_abort_control_child_a03` at `:338-352` records kill delivery,
reaped status, exit code, terminating signal, reap timeout, and wait error in
the returned causal string. A failed reap returns an error and cannot satisfy
the unavailable success predicate. An uncooperative process can remain after
the three-second bound because the helper deliberately returns rather than
blocking. The source records that condition instead of accepting it.

### Loader status and timeout semantics — closed

A normal `try_wait() == Some(status)` result becomes a reaped status without a
second wait. A poll deadline with no status sets `timed_out` before the direct
kill and bounded reap. A stream error or overflow sets a causal error and
still attempts kill and bounded reap. The success predicate rejects all these
non-normal states.

The terminating signal is recorded separately from the exit code. This avoids
mistaking signal termination for the expected unavailable exit 78.

### Cancellation join disposition — closed for pass qualification

`control_finish_thread_a03` at `:354-383` handles every cancellation thread
outcome. It records `joined` and `detached_after_timeout`. When a result is
received, it polls `JoinHandle::is_finished()` for at most three seconds and
joins only after completion. If the result remains unavailable, it detaches
explicitly rather than blocking.

The cancellation predicate at `:731-745` requires a joined thread and forbids
the detached state. A double receive timeout remains a failed case. The
fallback cleanup is recorded before that disposition, and the child PID gets
a bounded final absence check whenever the result is available. This source
cannot turn a detached or incomplete cancellation thread into a passing case.

## Control schedule and ownership observations

The ten A02 case IDs and order remain unchanged at
`control-extension-a03.rs:20-30`. A03 renames only the control operation,
report, helper symbols, and fixture source marker to A03.

`control_main_a03` at `:148-224` still requires ten ordered results, exact
counts, a 256 KiB-capped exclusive report, and false native/product/audio/
watch/heard/creative/framework/media/GPU/Resolve fields.

The normal and nonzero cases still check the exact producer vector, working
directory, environment, output inventory, pending or nonzero completion, and
false acceptance scope. The FIFO, log replacement, and terminal collision
predicates remain the A02 predicates. A03 does not widen any acceptance path.

The A04 prefix and pure helper remain exact. The A03 extension changes only
private source-control code. The private accepted value remains confined to
the assembled control crate. No public constructor or production trust loader
is added.

## Limits

This review did not assemble the crate, compile it, import it, run controls,
spawn a child, invoke a subprocess, or invoke native or media APIs. It does
not establish that the extension compiles, that controls pass, that cleanup
works at runtime, or that A04 qualification, media, audio, GPU, Resolve,
WATCHED, HEARD, or creative behavior works.

A failed three-second reap records a bounded failure but does not prove
kernel-wide descendant cleanup or absence after the bound. The package states
that limitation and does not qualify such a result.
