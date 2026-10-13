# Runtime snapshot parent readback A02 source review

Status: source-only independent review. The A02 reader, preflight, output, and
all child processes remain unexecuted. No import, helper, compiler, native,
media, GPU, Resolve, or control process ran for this review.

## Reviewed identities

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `readback_runtime_snapshot_a02_parent.py` | 25,593 | `660b4871aab6381ceb3ae3905749f9fd9b99a51dc076e9eb7bb514198aa7e093` |
| A09 helper source `freeze_observer_runtime_a09.py` | 55,732 | `c2ac751a7acdc9327112fad719dab751ba844162b346ff78e296e3eba3783dc4` |
| A09 contract | 14,189 | `bb03fddb685b5a935a2a5f789ed12bcfb42c9252e8395b85e9c6054418e1341a` |
| A09 rationale | 6,202 | `01683726ff727636ac6ef28d1cf894036045cd5dcac8bc911949ea0eae815603` |
| A09 report `runtime-snapshot-a09.json` | 2,837,530 | `7a43e5606a49bab8d949444707a132b102326cb86d6236e512e0160ac5dd29e8` |
| A09 fixed divergence overlay | 25,945 | `975e9dbb05e45718c363ebac762c868cd3c85bc952757c4d3aff017dce11b22a` |
| A09 RECORD diagnostic | 1,379,634 | `094c49dc02a1933782dba58fb75eb838587b9a6e7ab357a7c45cf0c61e7405d2` |
| A09 parent preflight | 2,643 | `a812ef5cbdf9c6fd4d9f71c608e9c610779184da70e8718ba7d5db0652a63f54` |
| A09 parent execution evidence | 861,763 | `7fb498f6659d2ba89a746c7234cb3a1664151dc171b36b31e998be39565de01e` |
| Restored A10 review | 7,607 | `291404c4fc09cf9b0e8c21ae2c6972d9ab642c7295c13afb0e057160324d7358` |
| A10 correction copy | 7,706 | `7d8029fbab593726d5fcd9818839dfdfc241db0ed30a4bd363141993c59167b0` |

The A02 preflight and output paths are currently absent. The restored A10
review and its correction copy were verified before this review used them.

## Disposition

The A02 reader is rejected before execution. It contains one deterministic P1
and two P2 evidence-boundary findings. Its explicit `require` checks do close
the assertion-removal defect from the A01 review, and its source-row and
descriptor checks are materially stronger than the A01 reader.

## P1: reader invocation compares the wrong argument vector

Lines 24 and 197 define `EXPECTED_READER_ARGV` as the complete interpreter
command: `[python3, -I, -B, script]`. CPython exposes only `[script]` in
`sys.argv` for that command. The A02 reader therefore fails at line 197 before
it can validate the saved report or publish output.

The command vector belongs in `sys.orig_argv`. The script argument vector
belongs in `sys.argv`. The reader must check both vectors separately and retain
both in its evidence. The A09 helper source uses the script-only form at its
own argument check, which confirms this boundary.

## P2: historical preflight facts are mixed with unbound execution claims

Lines 212–215 accept `attemptAbsent=true` as a preflight fact, while the A09
attempt and report already exist. Lines 424–427 then emit `toolExitCode=0`,
`helperExecuted=true`, `snapshotComplete=true`, an empty tool-output string,
and the child command from the preflight. The reader launches no child and
binds no A09 process receipt, exit record, or captured stdout/stderr.

The output must separate current reader facts from historical A09 execution
facts. A completed report hash and its unqualified state can establish saved
report identity. They cannot establish a historical tool exit code or output
capture. Those fields need a bound historical receipt, or explicit values such
as `snapshotToolExecuted=false` and `snapshotExecutionEvidenceBound=false`.

## P2: the preflight closes paths, but not an independently sealed source set

`validate_preflight` enforces schema 2, the exact root key set, seven unique
absolute paths, row shape, authorization booleans, and the separate reader
source row. `observe_preflight_sources` then measures every row again and
returns fresh rows with identities. These checks repair the A01 short-row and
discarded-fresh-observation defects.

The seven rows carry hashes supplied by the preflight. A02 has no expected
hash for those seven artifacts and no expected hash for the preflight file
itself. The `readbackSource` hash is also supplied by that same preflight.
Without an external preflight seal, a rewritten preflight can select new
bytes for the seven paths and a new reader-source hash, then pass the live
comparisons. The fixed A09 report, overlay, and diagnostic hashes remain
strongly bound, but the helper, contract, rationale, and review closure does
not. A later gate must bind the preflight bytes/hash or provide equivalent
source-row authorities before treating the seven-row closure as immutable.

## Checks that are correctly repaired

The source contains no `assert` statements. `require` raises a real
`ReadbackFailure`, so `python -O` cannot remove validation. The reader also
requires CPython 3.12.14, `-I`, `-B`, isolated user-site settings, safe-path
mode, and optimization level zero. The invocation P1 above still prevents the
intended reader from reaching those checks.

The preflight key set is exact. The seven source paths are unique and equal to
the A09 helper, contract, rationale, overlay, diagnostic, parent review, and
independent source-review paths. Duplicate JSON keys and non-finite JSON
constants are rejected.

The A09 report root key set, schema 4, unqualified state, scope, invocation,
fixed report byte count, and fixed report hash are checked. The reader also
rechecks the 45-row overlay projection, 1,548 installed rows, 995 declared
matches, 508 independently observed undeclared rows, 45 fixed divergences,
historical path digests, and exact A09 limits. The overlay's top-level wire is
not parsed for every contract field, but its fixed hash and exact diagnostic
projection bind the saved overlay bytes.

`measure` reads through descriptors with `O_NOFOLLOW`, compares pathname and
descriptor identity before and after each read, enforces per-file and
cumulative read/open limits, and closes owned descriptors. Python-root files
also retain each opened parent directory through the read. Held runtime roots,
the interpreter symlink, every tracked observation, and the report directory
entry are checked again before publication.

`sourceRowsAfter` uses the fresh rows returned by `observe_preflight_sources`
at lines 254–260. It is no longer copied from `preflight['rows']`. The output
also keeps `sourceRowsExpected` separately and records the fresh row identities.

## Publication and remaining boundary

The A02 output uses exclusive creation, checks the complete write, flushes,
and calls `fsync`. The output path is not opened through a held parent
descriptor, the output is not reread through its own descriptor, and its parent
directory is not fsynced. A short-write or later publication failure leaves a
partial output path without a failure receipt; a retry then fails on the
existing path. If the output is a gate artifact, add final output identity and
readback evidence plus explicit partial-publication handling.

Rootless inputs, including the unit preflight and A09 report, hold the final
file descriptor but do not hold their parent directory descriptors. The
reader therefore proves file identity and bytes, but not parent-directory
identity across a path replacement. The current fixed hashes and final file
checks limit this risk, but the distinction must remain explicit.

The result remains unqualified. It cannot establish a loaded interpreter image,
package import behavior, native dependency closure, comparator execution,
native text execution, provider origin, playback, hearing, or creative
acceptance. No A02 execution result exists.
