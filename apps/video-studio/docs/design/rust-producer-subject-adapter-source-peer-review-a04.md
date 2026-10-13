# Rust producer subject adapter A04 peer source review

## Disposition

The frozen A04 source is not ready for compilation or control execution.

I found three P1 blockers and one P2 build-recipe finding. None changes RoleIndex wire semantics.

A04 closes the A03 lifetime, aggregate, `/tmp` alias, no-argument, PNG gate, canonical-report, and shared-reader design gaps. New deterministic source defects prevent the harness from compiling or completing.

This was a read-only, separate-author review. It is same-model-family and nonblind.

I did not compile, import, assemble, or execute the adapter, harness, or controls. I started no child or native process.

## Reviewed authority

The frozen package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-subject-adapter-a04`

The self-excluding manifest is 33,207 bytes with SHA-256:

`25b6d353001e0c3ba98d615574084bd071ddbe5af08b185aee87102ec9fc7f36`

All 14 source rows match their declared 248,549 bytes and SHA-256 values.

All 24 external rows match their declared 388,559 bytes and SHA-256 values.

All 20 fixed authority documents match their declared 896,936 bytes and SHA-256 values.

Both manifest aggregates reproduce from the documented recipe:

- source: `c2b86f690fead6584c986483046a9630cceb42e8f3382990ce3012530820151f`
- external: `9d908febd83ee276d71ab02edfad698706c90fb9da467d3931e19cd541e57e39`

The bound compiler, preflight, dependency closure, `libc` archive, and `sha2` archive match their declared byte counts and hashes.

The declared attempt directory and both `/private/tmp` outputs are absent. These are pathname observations only.

## A03 severity history

The parent A03 review classified the missing return lifetime as one P1. It grouped the remaining concrete gaps into four P2 findings.

The peer A03 review found no new wire-semantic P1. It classified seven source-readiness gaps as P2.

A04's `&'static str` repair closes the shared lifetime finding. This review preserves both earlier classifications rather than rewriting either frozen review.

## P1 findings

### P1-1: The canonical-report format string has an unmatched closing brace

`diagnostic-harness-a04.rs:372-380` builds the report tail with `write!`.

The final format literal ends with:

```text
"controlCaseCount":{} }
```

The last `}` is a literal JSON brace, but it is not escaped as `}}` for Rust's format syntax.

The format parser should reject the harness source before code generation. Escape the final brace while preserving the intended JSON object closure.

### P1-2: Both real reader-mutation controls expect obsolete error codes

Growth calls the real `MeasurementSession` hook at `vector_controls.rs:75-90`. Replacement calls the same hook at lines 92-109.

Both mutations reach `validate_readback` through `MeasurementSession::measure`. That call supplies `subject_file_changed` as the identity-change code in `subject_observation.rs:356-369`.

Append changes the descriptor size. Replacement changes the pathname identity. Both therefore return `subject_file_changed`.

The controls still expect `vector_reader_growth` and `vector_reader_replacement` at `vector_controls.rs:111-128`. The manifest repeats those obsolete codes.

`all_controls_passed` becomes false, and `run_vector_reader_controls` returns `vector_reader_control`. A valid fixed reader can never satisfy the frozen control schedule.

Align the expected codes with the shared production validator. Keep the case IDs distinct for growth and replacement.

### P1-3: `require_candidate` compares resource counts with role-family totals

`CandidateSummary` copies the fixture's resource counts at `rust_producer_subject_adapter_v3.rs:369-384`.

The fixed fixture declares:

| Summary field | Actual fixed value |
| --- | ---: |
| `source_files` | 15 |
| `dependency_files` | 1,847 |
| `dependency_archives` | 35 |
| `toolchain_rows` | 89 |
| `input_control_ids` | 21 |
| `png_identity_checks` | 1,921 |

`diagnostic-harness-a04.rs:240-265` instead requires 38 source files, 1,889 dependency files, 25 input controls, and 7 PNG checks. Those values are diagnostic role-family totals, not summary resource counts.

Every valid fixed candidate therefore fails `require_candidate` before report or vector publication.

Require the fixed summary values above. Keep the separate 2,068-row schedule assertion for role-family coverage.

## P2 finding

### P2-1: The direct build arguments are relative to the wrong declared working directory

`source-manifest-a04.json:553-557` declares the package directory as the compiler working directory.

Both compiler commands then use repository-relative source and dependency paths at lines 566-579 and 593-605.

Under the declared working directory, these paths resolve below the package directory and do not exist. The same paths exist only when resolved from the repository root.

The compiler path, archive identities, dependency roots, panic settings, thin-LTO setting, and `lib*.rlib` output name are otherwise explicit and bound.

Set the declared working directory to the repository root, or make every source, dependency, and archive argument absolute.

## A03 finding reconciliation

### Return lifetime: closed

`diagnostic_controls.rs:289-293` now returns `&'static str`.

### Aggregate identities: closed

The 14 source and 24 external rows match individually. Both domain-separated aggregate recipes reproduce the declared values.

### Reader coverage: implementation closed, frozen expectations broken

`ReaderMutation` is crate-private. Normal reader calls pass no mutation.

The control-only path mutates disposable files after the actual read. Both ordinary and streaming reads use the shared `validate_readback` function.

This removes A03's duplicate boolean predicate. Finding P1-2 explains why the new controls still cannot pass.

### `/tmp` alias: closed

The current host resolves `/tmp` through the `private/tmp` symlink. `/private/tmp` resolves to itself.

A04 uses `/private/tmp` for FIFO, vector, report, and candidate paths. `MeasurementSession` can therefore retain its exact canonical-path check.

### No-argument and output admission: closed at source level

`diagnostic-harness-a04.rs:34-39` rejects extra arguments before authority reads. It also requires both output paths to be absent.

Both outputs use `create_new` and `sync_all`. The control report has a 1 MiB write cap. The candidate encoding retains its existing 4 MiB cap.

### Fresh reconstruction equality: closed at source level

Lines 41-51 perform two independent fixed-candidate loads. They compare the complete encoded RoleIndex byte strings before any control output.

The report schema records reconstruction count two and byte equality. The first candidate also receives the later candidate checks.

### Control result gating: structurally complete, values broken

The harness checks 12 fixture, 3 scalar, 2 FIFO, 4 vector, 5 schedule, 1 PNG, and 1 compilation-boundary case.

It requires aggregate and per-result pass fields before output. The PNG false-pass gap is closed.

The total is 28. Findings P1-2 and P1-3 prevent a valid run from reaching publication.

### Canonical report and scalar readback: structurally closed

The report is separate from the candidate RoleIndex output. It has fixed top-level key order, bounded size, exact result arrays, and ordered scalar IDs with hexadecimal bytes.

An independent strict JSON reader can decode those scalar results after a future bound run. Finding P1-1 currently prevents that harness from compiling.

### Direct compile recipe: partially closed

The recipe binds the observed absolute compiler, target and host dependency roots, exact archives, edition 2024, panic-abort, thin LTO, and owned attempt outputs.

Finding P2-1 leaves its declared path resolution unusable.

## Confirmed bounded properties

The complete 2,068-row schedule remains validated after sorting and before RoleIndex encoding.

The loader accepts no caller evidence path, role list, count, trust root, or permission.

The candidate cannot construct `Accepted<T>`, an active pin, a trust root, or loader authority.

The package adds no Swift, observer, comparator, native, media, GPU, Resolve, watch, listen, or creative authority.

These properties do not close the three P1 blockers or the P2 build-recipe finding.
