# Rust producer runner source controls A01 peer review

## Disposition

This is a read-only, same-family source review. I read the complete control
extension, assembly recipe, contract, manifest, and the copied A04 runner and
pure helper. The control package remains source-authored, unassembled,
uncompiled, and unexecuted.

The package does not weaken the A04 production source. Its private control
boundary, fake child modes, and report fields keep native, product, audio,
watched, heard, creative, GPU, Resolve, and media claims false.

## Manifest and source identity

The package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-source-controls-a01`

`source-manifest-a01.json` is 2,093 bytes with SHA-256
`27284199aa950bb1c1fc11fc9fd13a2c8582df0713d860a05ebb6d1cd7f5a12b`.
All five rows match current bytes. They total 127,161 bytes.

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| `assembly-recipe-a01.json` | 4,871 | `d6d8b2f42d75f90450a09a39c05174e13e373b45764f585753d9fcd79fd69989` |
| `control-contract-a01.md` | 7,668 | `5e2a075acdca075f143cb8bd1283286ea645f74edd409f5202b66c2b29cd5125` |
| `control-extension-a01.rs` | 45,369 | `fcbdc0617dd5ecbea9e9c83eb24ff723b1a49bae061f7c83a7fa8924ca482b65` |
| `pure.rs` | 3,969 | `b76f4edd50ca097e7aadb458c2325b02b874f9fdb1162a3f887c1c1f08c4ed1e` |
| `runner-lib-a04.rs` | 65,284 | `2414938b08c109d4953d11ec2962aa8095f01f7cb47e2936ed2e4dd9206e055b` |

The copied `runner-lib-a04.rs` is byte-identical to A04 `src/lib.rs`. The
copied `pure.rs` is byte-identical to A04 `src/pure.rs`. The A04 bindings are:

- manifest SHA-256 `961dd0e2cd7525ec8523958a97a0ac109aabfcac3393adfb1b36d846c9280576`;
- source aggregate `c658f23cd62b58cfb698ee2738cecbc2bb9ac7fa8e17062dfc642d7eca9a890a`;
- library SHA-256 `2414938b08c109d4953d11ec2962aa8095f01f7cb47e2936ed2e4dd9206e055b`;
- pure helper SHA-256 `b76f4edd50ca097e7aadb458c2325b02b874f9fdb1162a3f887c1c1f08c4ed1e`.

The recipe declares a 65,284-byte prefix plus a 45,369-byte extension. Their
declared sum is 110,653 bytes, with no inserted separator. The expected crate
root is `0247fe9c383c4f496170e8960bd75c199c00cb21e6cce14e1ea868075ab32e21`.
I did not create or hash the assembled target because this review forbids
assembly.

## Findings

### P2 — the package aggregate domain is not recorded

`source-manifest-a01.json:2` defines the recipe with a `domain_utf8`
placeholder, but it records no domain value. The declared aggregate is
`fe0a9c582e35c0874a42b25cc44d123fe8bd7158954ed360ac44d4c54fd98fe7`.
The only matching candidate I found is the undocumented domain
`native-text-rust-producer-runner-source-controls-a01-source-v1`.

A future source successor should record that exact domain in the manifest and
contract. Without it, an independent reader cannot reproduce the aggregate
from the package rows alone. This is a provenance defect, not a runtime defect.

### P2 — the unavailable-loader self-child has no independent bound

`control-extension-a01.rs:196-229` invokes the current executable with
`Command::output()`. The call has no timeout and no stdout or stderr cap.
The expected A04 missing-acceptance path returns immediately, but a regression
before that path could hang the complete ten-case control or grow both output
buffers without the control's 256 KiB report bound.

Use the same bounded child polling and capped pipe reader used by the other
control paths. Keep the exact exit, JSON, stderr, and output-parent checks.

### P2 — cancellation and overflow do not require signal delivery

`control-extension-a01.rs:387-394` and `:430-435` require
`term_requested` and `term_attempted`, but do not require
`process.term_delivered`. A runner can record an attempted TERM with an
`ESRCH` result and still satisfy these predicates if the remaining fields
match. The A04 `TerminationFacts` type exposes delivery separately.

Require `term_delivered == true` for both cancellation and log-overflow cases.
Retain the existing completion, reap, marker, log-size, and false-scope checks.

### P2 — cleanup fallback does not prove the final child is gone

When cancellation does not return within the two bounded receives,
`control-extension-a01.rs:371-379` sends group and direct `SIGKILL` through
`control_kill_case_child_a01`, but does not wait for or recheck process exit.
The pipe-holder case measures `holder_gone` before its fallback direct kill at
`:465-470`; it does not record that kill result or perform a final bounded
absence check. `control_kill_case_child_a01` also ignores both signal results at
`:1106-1113`.

The cases correctly fail when the first absence check fails, so this does not
create a false acceptance. It leaves failed-control cleanup unproven and can
leave an orphan child if both kill attempts fail. Record signal outcomes and
perform one final bounded absence check before publishing the case result.

### P2 — terminal fallback assertions are not causal-exact

`control-extension-a01.rs:568-578` checks the terminal fallback state,
acceptance booleans, and fallback path. It does not check `schema`,
`error.code == "terminal_report_name_collision"`, or
`error.phase == "terminal_publication"`.

A malformed fallback with the same state and false booleans could therefore
pass the collision case. Add those exact fields to the predicate. Keep the
double-collision sentinel and `RunnerError::TerminalPublication` check.

## Positive source observations

The extension keeps all ten case IDs in a fixed order. It requires ten results,
ten passes, and exact order before returning success. It writes the outer
control report with exclusive creation and a 256 KiB serialization cap.

The fake producer validates all ten argument values, absolute paths, working
directory, and the four-variable environment. Fixture, fake-output, sentinel,
and fallback files use exclusive creation. The A04 runner retains descriptor
relative traversal and exclusive terminal publication.

The private `AcceptedRustQualification::from_reviewed_boundary` constructor is
`pub(crate)` in the copied A04 source. The extension calls it inside the same
assembled crate only. No public constructor or loader is added, and the fake
qualification is not a production trust root.

The cancellation, overflow, pipe-holder, FIFO, log-replacement, and terminal
cases exercise distinct A04 lifecycle and publication paths. The source does
not start a native framework, media process, observer, comparator, Swift,
GPU, Resolve, FFmpeg, or libav process.

## Limits

This review did not assemble the crate, compile it, import it, run controls,
spawn a child, or invoke a native or media operation. It does not establish
that the extension compiles, that all ten controls pass, that process cleanup
works at runtime, or that A04 production qualification, media, audio, GPU,
Resolve, WATCHED, HEARD, or creative behavior works.
