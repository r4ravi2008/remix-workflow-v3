# Comparator A12 source review

Status: source-only peer review. The A12 package remains unbuilt, unexecuted,
and unqualified. No comparator, control, import, compiler, native framework,
GPU, Resolve, or media process ran.

## Reviewed identities

| File | SHA-256 |
| --- | --- |
| `text-report-comparator-a12/package-manifest-a12.json` | `99094c8bb32fe61157fd021d9b6e2ee011241f484f337514dc98376102466431` |
| `text-report-comparator-a12/actual-comparator-control-a12.py` | `3df9b1dd2141c16532344f48f39ea9a561dc224a39f3a4ba864876088cc60db9` |
| `text-report-comparator-a12/README-a12.md` | `627a6eb7673f84c4e34e07fefb5f7606c34c7c4ea7235c283fa5cac4d3f90c22` |
| `text-report-comparator-a12/source-rationale-a12.md` | `be2dee460c149dcdf6134b7a7221803a9cf3c924a797e8984791fa574d063f4c` |
| A11 comparator | `e94b6ea3fb671ba66d413594060959bb5ec86f7e4fcffb8e774ababaeb438520` |
| A11 actual control | `3e1d293a57e1b617f39702d4d599f8520f6828860daba3fe59cd781f0b7c49a2` |
| A11 required control | `69c8c96d60b7b8842d6e5f55a564ea23e6853d66c8d06b006e9738e203be809c` |
| A11 package manifest, current | `fde359966503739aa5225cf911e3e75ff61e74b04396343612d5ff323ce064a8` |
| A11 source review | `0f8ac005d4fe790dbbc7a39cb602e0d8385cac6b3df1c7e0f2a3ac092fe33bd7` |
| Swift A15 source manifest | `0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e` |
| Swift A15 protocol correction | `500e2aae219efe8351c8e77d8055ecb147d128c80e6d800efaee0c7960859363` |

The A12 package manifest binds the current A11 manifest hash above. The A15
binding remains the 21-row source manifest, producer schema 5, control schema
3, and the frozen `probe.swift`, `png-consumer-shared.swift`, and
`alpha-context-shim.h` rows.

## Findings

### P1-1: the A11 predecessor manifest does not describe its current README

The current A11 `README-a11.md` is 6,802 bytes with SHA
`cacf608a6ba6a1880ea20064ed5762be89d864c60a82d2d3027df937355bbb74`.
The current A11 package manifest records the same SHA but records 6,682 bytes.
The A12 `frozenPredecessor.packageManifest` binds that inconsistent manifest.

An exact package-row preflight must reject this package. The A12 source can
still bind the comparator bytes directly, but the package and source-closure
authority cannot claim a valid A11 package while one row's byte count is false.
Preserve the current files and issue a successor manifest or an explicit drift
snapshot before any A12 runner execution.

### P1-2: the current-allocation report still skips allocation replay

The A12 control adds a complete `validate_swift_report` call and an active
producer check for the 314,231,808-byte report at lines 416-420. That closes
the A11 parser-path omission. It does not call `_reconcile_swift_allocation`
for that current report. The report carries an empty event log and zero event
bytes, so the row proves only policy-shape and report parsing. It does not
prove that the current written-file total reconciles with a bounded event
stream, owner totals, baseline, peak, and final outstanding bytes.

The separate 16 MiB row at line 411 does call `_reconcile_swift_allocation`,
but it is the old zero-written-file synthetic record. The A12 control should
either replay a current-bound event fixture for the 314,231,808-byte report or
label the row explicitly as parser-and-gate-only. The runner must not describe
it as complete current allocation evidence until this is resolved.

### P1-3: observation qualification is declared, but the case gate is not asserted

`expect_observation_unqualified` at lines 109-133 calls
`producer_internal_passed`, checks the closure declaration, and records the
string form of that structural result. It never calls
`swift_case_gate_passed(case, declared)` or requires that function to return
false. A synthetic observation-only case with a changed case-level gate could
therefore still produce an accepted control row because the helper trusts the
declared `qualified: false` value.

The A12 source rationale says observation support remains unqualified. The
control must assert the actual case-level gate is false for each non-font
observation prefix, while separately recording whether the structural report
path passed. The same distinction should be explicit for failed and outer
prefix rows, whose current `expect_gate_false` result is dominated by the
report state check before `_require_swift_case` runs.

### P2-1: the A12 manifest does not identify the control stdout schema

`package-manifest-a12.json` exposes `reportSchema: 5`, which describes the
Swift comparator report family. The A12 child emits schema 1 with `state`, a
new `loader` object, and `results`. The manifest has no `controlReportSchema`
or output-schema file. README prose and source code are the only authorities.

The runner must bind the actual A12 child wire contract explicitly. A future
manifest should distinguish comparator report schema 5 from control stdout
schema 1 and include the control output source row.

### P2-2: loader byte count is serialized as a string

`source_loader_control` validates the internal byte count as an integer, then
returns `"bytes": str(source["bytes"])` at line 598. The actual JSON therefore
contains a string byte count. The README calls it a byte count without defining
its type. This is a strict wire-contract ambiguity and must not be normalized
silently by the runner.

Either retain and document the current string type as A12 wire behavior, or
change the successor to emit an integer and rebind its manifest and output
contract. The runner must require one exact choice.

## Verified A12 repairs

The A12 control correctly addresses the A11 control defects in these areas:

* It records loader provenance from the exact bounded bytes passed to `exec`.
  The loader record has the comparator path, byte count, and computed SHA.
* It keeps separate binding and aligned-range negatives. Allocation-only
  baseline and peak mutations expect `swift_reservation_binding`; aligned
  policy-plus-allocation mutations reach `swift_reservation_baseline` and
  `swift_reservation_peak_slots`.
* The current 314,231,808-byte synthetic report now reaches
  `validate_swift_report` and the active structural producer path.
* Fractional partial prefixes at 0, 4, and 9 toggles reach full report
  validation and produce explicit false-gate rows.
* Observation-only non-font prefixes at all three terminal positions reach
  full report validation and preserve the explicit unqualified declaration.
* Outer causal failure now reaches full report validation and a false-gate
  row. Failed prefixes retain the same full parser path.
* The child stdout top-level shape is now source-defined as schema 1, state
  `executed`, loader provenance, and results. The exact field types and
  manifest binding still require the corrections above.

## Exact A12 stdout contract for a future runner

The current child emits one JSON object with exactly these top-level keys:

```python
{
    "schema": 1,                 # integer
    "state": "executed",        # string
    "loader": {
        "path": string,
        "bytes": string,         # current source emits str(int)
        "sha256": 64-hex string,
    },
    "results": [Result, ...],
}
```

Every result contains `name`, `status`, and `code`. Results from
`expect_gate_false` also contain a string `diagnostic`. Results from
`expect_observation_unqualified` also contain string `diagnostic` and string
`active_structural_gate`. The runner must allow no other keys.

The fixed result expectations are:

```text
a15-source-manifest-join                         accepted / ok
a11-allocation-baseline-16m                      accepted / ok
a11-current-allocation-314231808-under-512m      accepted / ok
a12-complete-parser-current-allocation-314231808  accepted / ok
a12-active-gate-current-allocation-314231808     accepted / ok
a12-allocation-baseline-binding-mutation          rejected / swift_reservation_binding
a12-allocation-baseline-range-mutation            rejected / swift_reservation_baseline
a12-allocation-peak-binding-mutation              rejected / swift_reservation_binding
a12-allocation-peak-range-mutation                rejected / swift_reservation_peak_slots
a11-allocation-missing-observed-peak               rejected / swift_allocation_keys
a11-rust-evidence-exact-bound                     accepted / ok
a11-rust-evidence-one-byte-over                   rejected / evidence_stored_cap
a11-swift-evidence-exact-bound                    accepted / ok
a11-swift-evidence-one-byte-over                  rejected / evidence_stored_cap
a11-complete-parser-accepted-16m-512m             accepted / ok
a11-active-gate-accepted                          accepted / ok
a11-complete-parser-observation-only              accepted / ok
a11-complete-parser-fractional-controls           accepted / ok
a11-active-gate-observation-only                  accepted / ok
a11-complete-parser-expected-rejection            accepted / ok
a11-active-gate-expected-rejection                accepted / ok
a11-complete-parser-failed-prefix-{0,1,2}         accepted / ok
a12-failed-prefix-{0,1,2}-gate-false             accepted / qualification_false
a11-complete-parser-outer-failure-no-repeats       accepted / ok
a11-negative-omitted-guard-role                   rejected / swift_case_records
a11-negative-omitted-native-image                 rejected / swift_native_image_obligation
a12-negative-omitted-fractional-control           rejected / toggle_count
a12-negative-fractional-control-order             rejected / swift_toggle_schedule
a11-negative-disallowed-error                     rejected / swift_rejection_error
a11-negative-comparator-field-in-error            rejected / object_keys
a11-negative-rejection-native-residue             rejected / swift_rejection_residue
a11-negative-omitted-clip-reference               rejected / swift_clip_reference
a11-negative-failed-zero-case-residue             rejected / swift_failure_residue
a11-negative-failed-prefix-incomplete             rejected / swift_failure_prefix
a11-negative-failed-prefix-relation               rejected / swift_guard_relation
a11-complete-parser-exact-zero-coverage            accepted / ok
a12-complete-parser-fractional-partial-prefix-{0,1,2} accepted / ok
a12-fractional-partial-prefix-{0,1,2}-gate-false  accepted / qualification_false
a12-complete-parser-observation-only-nonfont-prefix-{0,1,2} accepted / ok
a12-observation-only-nonfont-prefix-{0,1,2}-unqualified accepted / qualification_false
a12-complete-parser-outer-failure-causal-shape     accepted / ok
a12-outer-failure-causal-shape-gate-false          accepted / qualification_false
a11-rust-control-paths-excluded-only               accepted / ok
a11-rust-control-active-stability                  accepted / ok
a11-rust-control-decoded-mutation-rejected        accepted / ok
```

The brace forms expand to three distinct result names. Gate-false and
observation-unqualified rows also carry their source-derived diagnostics.

## Disposition and limitations

A12 is a meaningful successor. It fixes the A11 full parser-path omissions and
aligns binding versus range errors. It remains blocked before execution by the
A11 manifest byte-count mismatch, the missing current allocation replay, and
the missing assertion of the observation case gate. The control-output schema
and loader byte type also need an explicit frozen authority.

This review is same-family and source-only. It does not establish comparator
execution, native text rendering, PNG orientation, media support, GPU use,
Resolve behavior, playback, listening, or creative acceptance.
