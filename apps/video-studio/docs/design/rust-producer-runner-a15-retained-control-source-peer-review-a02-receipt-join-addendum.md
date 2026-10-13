# Rust producer runner A15 retained-control receipt-join review A02 addendum

## Disposition

**This additive review finds one P1 preflight blocker.** The frozen retained
caller cannot accept a valid compiler terminal receipt because it drops the
receipt identity before comparing the terminal's full receipt. Preserve the
earlier A02 peer review and all frozen source bytes. This addendum covers only
the compiler measurement receipt join.

This is a same-model-family, nonblind, source-only review. I read the complete
retained caller, the compiler caller, and the pinned A04 utility. I did not
import, compile, execute, test, launch a child, or use native, media, GPU,
Resolve, playback, listening, or creative workflows.

## Exact reviewed identities

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| retained caller A02 | 55,353 | `8c82ab5eafb11f3e0639fd12ca604f5318792cd5d9df697d3962309c632fee4a` |
| compiler caller A05 | 40,067 | `c211d3134005cd5d45327a16b31c0635b98b07be4605376a6716112e69500f7a` |
| pinned A04 utility | 46,572 | `b903a9aff1cc2d8dae73b16800f177322b000b2983e5a45206a639326727d47d` |
| retained package peer review A02 | 7,847 | `f46d555c1e444c827edb970cf13a2bb3a94bf15b6f5b4edf4e9d7248f1abe74c` |

## P1.1: `compileMeasurements` cannot satisfy the retained caller join

A04 `save_at` returns a four-key receipt at
`native_runner_process_a09.py:210–211`:

```python
return dict(path=str(path), bytes=cursor, sha256=digest.hexdigest(),
            identity=identity(before))
```

The A15 compiler caller saves `compile-measurements-a01.json` through
`save_at` at `native_runner_fixed_compile_a15.py:696–698`. It stores that full
four-key `measurement_receipt` directly in
`compile-terminal-closure-a01.json` at lines 702–707:

```python
'compileMeasurements': measurement_receipt,
```

The retained caller defines `receipt_reference` at
`native_runner_retained_controls_a15.py:163–164` with only `path`, `bytes`,
and `sha256`. Its external readback comparison at lines 169–170 correctly uses
that deliberate three-key projection. The terminal comparison at line 176
incorrectly applies the same projection:

```python
terminal['compileMeasurements'] == receipt_reference(build_record)
```

`build_record` is the full four-key receipt returned when the retained caller
reads `compile-measurements-a01.json`. The compiler terminal field is also a
full four-key receipt. The left side therefore contains `identity`, while the
right side does not. Python dictionary equality fails for every valid compiler
terminal produced by the bound A04 `save_at` implementation.

The failure occurs at the retained caller's preflight validation, before the
caller opens its attempt directory and before line 515 can invoke
`run_retained_driver_phase`. A valid four-command compiler result therefore
cannot reach the retained control schedule. This is a deterministic P1 source
blocker, not an observed compiler or control failure.

The narrow repair is to compare the terminal field with the complete held
`build_record`, or with a separately named full-receipt helper that requires the
`path`, `bytes`, `sha256`, and `identity` keys and exact identity equality. Keep
the external build-readback three-key projections unchanged. Those projections
are the deliberate public readback references at lines 169–170. Do not weaken
the full terminal join or replace identity with a path-only comparison.

## Scope

This finding is separate from the earlier A02 execution-fact P2. The retained
caller source remains source-only and unexecuted. The terminal receipt defect
does not establish any compiler, control, producer, native, media, product,
WATCHED, HEARD, playback, listening, or creative result.

No frozen package file was modified. No source was imported or executed. No
compiler, control, child, process probe, native framework, media, GPU, Resolve,
playback, listening, or creative operation occurred during this review.
