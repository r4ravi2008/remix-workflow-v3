# Comparator A12 review correction: observation gate semantics

Status: additive source-only correction. The preserved A12 review remains
unchanged. No comparator, control, import, compiler, native framework, GPU,
Resolve, or media process ran.

## Reviewed identities

| File | SHA-256 |
| --- | --- |
| A11 comparator `compare_text_reports_a11.py` | `e94b6ea3fb671ba66d413594060959bb5ec86f7e4fcffb8e774ababaeb438520` |
| Preserved A12 review | `b9d8d4bd5fdd04acf63680c1097d000213ded2eaf586b2c44a86dc03fa2df243` |
| A12 control `actual-comparator-control-a12.py` | `3df9b1dd2141c16532344f48f39ea9a561dc224a39f3a4ba864876088cc60db9` |

## Correction to A12 P1-3

The preserved review required the case gate to be false for every non-font
observation prefix. That outcome is incorrect for a valid
`observation_only_rejected` record.

The active A11 implementation first runs `_require_swift_case`. That function
runs `_a10_validate_swift_case` and the historical structural adapter. The
`swift_case_gate_passed` function then returns `case.disposition != "failed"`.
Therefore a structurally valid observation-only rejection has this meaning:

```text
evaluation kind       observation_only
disposition            observation_only_rejected
declared qualification false
structural case gate   true
qualification          false
```

The `true` gate means that the report passed the structural contract. It does
not mean that the observation is a qualified native result. Requiring false
would reject the valid observation boundary that the design intends to keep.

## Correct control obligation

The control must keep the two predicates separate:

| Case semantics | Required structural gate | Required qualification evidence |
| --- | ---: | --- |
| accepted shape | `true` | accepted shape evidence |
| observation-only accepted | `true` | declared `qualified: false` and no native qualification |
| observation-only rejected | `true` | declared `qualified: false`, terminal observation error, no native image |
| failed fractional or outer prefix | `false` | causal failure and no successful qualification |

The current A12 `expect_observation_unqualified` path calls
`producer_internal_passed`, which invokes `_require_swift_case`. It records the
returned structural result as `active_structural_gate`. It separately requires
the closure declaration to be `observation_only` with `qualified: false`,
requires `observation_only_rejected` or `failed`, and rejects retained native
image evidence. This is the correct semantic split.

The current A12 `expect_gate_false` path uses a report with
`unexpectedFailures == 1` for fractional and outer failures. The producer gate
therefore fails before a failed case can be treated as a successful result.
Those rows should continue to require a false structural gate. A future
successor may additionally call `swift_case_gate_passed(case, declared)` for
those rows, but it must not require that result to be false for a valid
observation-only rejection.

## Disposition

This correction withdraws only the false-gate requirement from preserved A12
finding P1-3. P1-1, the stale A11 predecessor manifest byte count, and P1-2,
the missing current allocation replay, remain actionable. The control-output
schema and loader-byte-type findings remain unchanged. A12 remains unexecuted
and cannot qualify native text, PNG orientation, media support, GPU use,
Resolve behavior, playback, listening, or creative acceptance.
