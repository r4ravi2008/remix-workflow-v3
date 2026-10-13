# Comparator runner A01 no-child controls — independent source review

## Review status

I read every frozen file in `comparator-control-runner-a01/source-controls-a01/`.
I also read the bound runner contract and fixture expectations. This review did
not import, compile, execute, or run the control, runner, codec, helper, child,
compiler, native process, media process, GPU, or Resolve.

The control package is structurally reviewable, but it cannot qualify the frozen
runner. Its completed-capture canary reaches both inherited runner blockers:
ordinary `PosixPath` values fail the exact `Path` guards, and capture float
timestamps fail canonical publication.

## Frozen package identities

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `control_comparator_runner_a01.py` | 35313 | `d7ce0ad273fe251288dababe8b5af80ece26137b731403a1b97d4bb94df41458` |
| `control-contract-a01.md` | 5683 | `89721bb30970f7b72905eaa32105ce9dde717284c14fbc97943293792a0580b9` |
| `control-fixture-a01.json` | 19284 | `930ea0c99bef041cf0de380ce9d558da072f9bf6c0841cacb7b4ade8c91313c4` |
| `source-package-manifest-a01.json` | 7187 | `d0f2d9ab968ea8d5f4834f1920a8498b7c213756f49936e4fbd2a049799002ce` |

The self-excluding manifest binds the control source, contract, and fixture.
Its input rows bind the reviewed runner, A09 helper and records, codec, A13
contract and erratum, and A14 child package inputs.

## Source checks

The control reads each frozen input through `read_bound`, with an `O_NOFOLLOW`
descriptor, byte cap, exact size, exact hash, descriptor identity, and final
path identity. It loads source modules only from those measured bytes. It uses
strict duplicate-key and float rejection for the fixture.

The A09 structure cases exercise the central raw bundle binding, exact root
keys, schema type, distribution order, row duplication, overlay order,
diagnostic duplication, policy type, and comparison Boolean type. The phase
cases preserve phase labels and counters outside the domain facets. They reject
open, read-byte, path-byte, row-count, phase-label, and measured-domain changes.

The child cases require the exact A14 schema 3 loader tuple, all 59 ordered
rows, required fields, optional field types, digest, duplicate keys, and float
rejection. The required-evidence fixture checks all 12 ordered rows.

The publication cases cover canonical UTF-8 bytes, exact 1 MiB acceptance,
one-byte-over rejection, owner-cap mismatch, unknown owner, and content digest
changes. The allowlist cases cover both modes, success, failure before a
control report, failure after a control report, order, extra names, and
duplicates.

The transition cases enumerate every declared pure transition, every cleanup
failure origin, invalid pairs, and invalid state/event types. The fake capture
cases cover prelaunch cancellation, Popen failure, selector cleanup, direct
child reap, and canonical publication of a completed fake record. They never
claim real stream capture, signals, descendants, reaping, or subprocess proof.

## Findings

### Inherited P1 — the fake capture controls cannot enter the runner seam

`fake_capture_controls` passes ordinary `Path(...)` values to
`run_captured_child`. The frozen runner rejects those concrete `PosixPath`
values before it reaches cancellation, Popen failure, or completed fake capture.
This is an inherited runner defect, correctly named in `control-contract-a01.md`.
The successor control must retain the same canaries against the repaired runner.

### Inherited P1 — the completed fake capture cannot be published

The fake `Clock` returns floating monotonic values. The completed capture record
therefore contains float timestamps. The frozen runner's canonical conversion
rejects those values. This is an inherited runner defect, correctly named in the
control contract. The successor control must serialize the repaired integer-time
or omitted-time representation through a control-result owner.

### P2 — the Popen-failure canary expects a selector the runner never creates

`fake_capture_controls` creates an external `EmptySelector` and supplies it as
the backend's `selector_factory` result. The injected Popen raises before the
runner calls that factory, so the runner's local selector remains `None` and its
cleanup cannot close the external selector. The control then requires
`selector.closed is True`, which fails even after the inherited path guard is
repaired. The successor control must either assert that no selector was created
on Popen failure or inject a selector that the runner actually owns.

No other P1 or P2 was found in the control source, fixture, or manifest. The
controls use fixed, meaningful expectations and preserve their source-only
scope. They remain unexecuted and cannot be described as passing controls.

## Scope and blind status

This is same-family and nonblind review. The control source and fixture are from
the same repository and bind the same A09/A14 evidence as the runner. It is an
independent source read, not an independent runtime or implementation family.

The package proves no runner launch, child result, process-group behavior,
loaded image, native text output, media output, GPU operation, Resolve operation,
provider origin, playback, watching, hearing, or creative acceptance. Any future
control result must bind a repaired runner identity and retain these scope flags.
