# Focused comparator control runner A01 — independent source review

## Review status

This is an independent read-only source review. I read the complete frozen runner,
its four top-level package documents, the three no-child control inputs, and the
fixed A09/A14 bindings listed below. I did not import, compile, execute, or run
the runner, codec, helper, controls, children, compiler, native process, media
process, GPU, or Resolve.

A01 is **not source-ready**. Two P1 findings prevent the ordinary path from
reaching a sealed attempt. Two P2 findings weaken the declared capture and strict
wire contracts. The source remains frozen.

## Frozen package identities

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `run_comparator_controls_a01.py` | 147302 | `f8dee802b2e673c8819ecccf3daef6d9eef0d0ea0522df8ff92154d971c4d3eb` |
| `runner-contract-a01.md` | 8138 | `4c1c48a12500ec5ddc9705fd99b3dc688abbae3654d0a645def3d7c1549c79d5` |
| `output-schema-a01.md` | 3108 | `86ced09a43efcd55283d1edbb51204c56e03fff97e0bc34268de9dd841638e52` |
| `source-rationale-a01.md` | 2780 | `10a66f8982bb593c5e218e676e044ffc921c34f55b4c746ab348a52f100ef0b4` |
| `source-package-manifest-a01.json` | 2679 | `e47bb19f385ab07bccc4795b2f8eb27fbf18ead3b565a6018593dce914708877` |

## Independent no-child package identities

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `source-controls-a01/control_comparator_runner_a01.py` | 35313 | `d7ce0ad273fe251288dababe8b5af80ece26137b731403a1b97d4bb94df41458` |
| `source-controls-a01/control-contract-a01.md` | 5683 | `89721bb30970f7b72905eaa32105ce9dde717284c14fbc97943293792a0580b9` |
| `source-controls-a01/control-fixture-a01.json` | 19284 | `930ea0c99bef041cf0de380ce9d558da072f9bf6c0841cacb7b4ade8c91313c4` |
| `source-controls-a01/source-package-manifest-a01.json` | 7187 | `d0f2d9ab968ea8d5f4834f1920a8498b7c213756f49936e4fbd2a049799002ce` |

The control package manifest is self-excluding and binds its three source-control
files plus the runner, A09, A13, codec, and A14 inputs. Its claims remain source-only.

## Bound predecessor and input identities

The reviewed source binds these exact inputs:

- A13 contract: `f09b1ae8a8cc9dbbdf2166c386901e70a5d0d75166050cfb5602ebea61dd0603`.
- A13 closure-order erratum: `cc6271f8804d3596bf8c9e533a519bd3e6614885ec41b971ccc4aff670e71aaf`.
- A09 helper: `c2ac751a7acdc9327112fad719dab751ba844162b346ff78e296e3eba3783dc4`.
- A09 report: `7a43e5606a49bab8d949444707a132b102326cb86d6236e512e0160ac5dd29e8`.
- A09 divergence overlay: `975e9dbb05e45718c363ebac762c868cd3c85bc952757c4d3aff017dce11b22a`.
- A09 diagnostic: `094c49dc02a1933782dba58fb75eb838587b9a6e7ab357a7c45cf0c61e7405d2`.
- Canonical codec: `76afa37d87fcb2e610a38d8e1f620cc6709b344d382e9a205e01e3b3f419e85e`.
- A14 package manifest: `b8e0422d8c2737009978c7fe2a71c6d5a59430ae116afc399b0bf9c69cad7d31`.

The package correctly keeps A09 filesystem facts unqualified. It does not turn
those facts into loaded-image, native, media, provider, or creative evidence.

## Findings

### P1 — concrete filesystem paths fail the runner's exact `Path` guards

`BoundDirectory.open` requires `type(path) is Path` at line 2197. On macOS,
`Path("...")` produces the concrete `PosixPath` type. `UNIT` therefore fails
before the attempt directory is created. `run_captured_child` repeats the same
guard for its temporary path at line 1951. The fixed public and production paths
cannot reach publication. The successor must accept the concrete absolute path
type while keeping the absolute-path check. A pure control must pass an ordinary
`Path(...)` through both the held-directory and fake-capture seams.

### P1 — capture timestamps make every result publication fail canonicalization

`_capture_event` stores `atMonotonicSeconds` from the float clock at line 1833.
`run_captured_child` stores float `startedMonotonicSeconds` and
`finishedMonotonicSeconds` at lines 1994 and 2176. `_to_codec_json` only accepts
`None`, exact booleans, exact integers, strings, arrays, and objects at lines
1588–1595. It rejects every capture float before the canonical codec runs.

The successful control report includes `capture`. The failure report and seal
also include the same capture record. Therefore a completed child reaches
`canonical_publication`, fails with `canonical_json_type`, then fails again in
failure publication. The runner cannot produce a sealed success or a sealed
failure. Preserve the no-float codec and represent retained time with a declared
exact integer unit, or omit it under an explicit bounded schema. Pure controls
must serialize successful, cancellation, setup-failure, and deadline records
through every applicable publication owner.

### P2 — a direct-child exit can lose the owned process-group target

The runner calls `Popen(..., start_new_session=True)` and records the PID, but it
creates a selector before calling `getpgid` at line 2045. `process_group` remains
`None` until that lookup succeeds. If the child exits during this window while a
descendant keeps a pipe open, `getpgid` can fail. Fatal cleanup then has no group
target. `_signal_owned_group` can only try the direct child, which has already
exited, so the descendant can retain the pipe and survive the intended bounded
cleanup.

Record the owned group as the positive PID immediately after successful
`start_new_session=True`, then observe and compare the live PGID when available.
Keep the direct-child fallback as a separate observation. Add a fake backend case
for an exited parent with a retained descendant pipe. This remains a filesystem
and process-control test only; it must not claim descendant reaping.

### P2 — `typed_equal` does not enforce nested scalar types

`typed_equal` checks only the outer Python type before using equality at lines
434–436. Python treats `True == 1` and `False == 0` inside dictionaries, lists, and
tuples. For example, the A09 runtime flags check at line 1123 accepts an integer
`safePath: 1` in place of boolean `True`. The same shortcut affects nested scope,
flag, closure, authorization, and comparison objects.

The fixed raw A09 hash prevents this mutation in the normal bundle path, but the
public structural validator does not meet the strict nested JSON contract. Use a
recursive exact-type comparator for nested values. Add no-child cases for a
nested Boolean/integer substitution in report flags and authorization scope.

## Source readiness and limits

The source-control package checks exact A09 shape, phase owner limits, the A14
59-row child schedule, publication boundaries, allowlists, state transitions,
prelaunch cancellation, Popen failure, and a completed fake capture. Those are
useful pure controls, but the control contract correctly identifies the two P1
runner blockers. They must not be reported as passing until a successor binds a
repaired runner and the controls run against that successor.

This review is same-family and nonblind. It inspects source and frozen JSON from
the same repository. It is independent of runtime execution, external process
capture, loaded-image inspection, native text output, media output, and creative
approval. No control, runner, child, helper, compiler, native process, GPU,
Resolve process, or media process ran for this review.

The current result is source rejection, not execution evidence or acceptance.
