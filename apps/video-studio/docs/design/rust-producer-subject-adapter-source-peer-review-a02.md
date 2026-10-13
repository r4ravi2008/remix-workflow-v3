# Rust producer subject adapter A02 peer source review

## Disposition

The frozen A02 source is not ready for compilation or control execution.

I found no P1 finding and three P2 findings. A02 closes the original scalar wire failure and five original P2 groups.

The original role-schema finding is only partially closed. A02 specifies the 89 toolchain rows, but not the complete diagnostic candidate schedule.

This was a read-only, separate-author review. It is same-model-family and nonblind.

I did not compile, import, assemble, or execute the adapter or its controls. I started no child or native process.

## Reviewed authority

The frozen package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-subject-adapter-a02`

The self-excluding manifest is 19,803 bytes with SHA-256:

`df3f3c85872b6ad5b337fbb239f6b774b0fec239e9b93a82718307d34cfa6698`

All 12 source rows match their declared 208,901 bytes and SHA-256 values.

All 20 external rows match their declared 327,723 bytes and SHA-256 values.

All 20 fixed authority documents match their declared 896,936 bytes and SHA-256 values.

I independently recomputed both manifest aggregates from the declared recipes. The results match:

- source: `5f3406b677134c8688211efa42b03156bf4ab217a89ef61952536ce4a9871567`
- external: `06d1655c580708d04ca4d7e366bd5c24a75cc6a937532f71618cfe6fcb8f3ca6`

The unchanged authority fixture is 9,033 bytes with SHA-256:

`548721bcb1805bf9e11be285d1be4c0edfbbd90341e0ed5a5dbe7111cd61db61`

## P2 findings

### P2-1: The new schema still freezes only the 89 toolchain rows

`project_toolchain_rows` receives only `adapted.rows` at `rust_producer_subject_adapter_v2.rs:1025-1035`.

The manifest repeats this partial projection at `source-manifest-a02.json:352-391`. Its `rowCount` is 89.

`build_candidate` also emits every source, dependency, build, input, PNG, and toolchain-report row. Lines 351-362 append these families before encoding.

The frozen counts and push sites produce this static schedule:

| Family | Rows |
| --- | ---: |
| source | 38 |
| dependencies | 1,889 |
| build | 19 |
| toolchain, including the report row | 90 |
| input | 25 |
| PNG control | 7 |
| **complete candidate** | **2,068** |

This count is a source derivation. No candidate output was executed.

`CandidateSummary.row_count` merely copies `rows.len()` at line 371. No exact expected total, role sequence, or observation-kind sequence is checked.

A non-toolchain role can therefore change while `RustProducerDiagnosticRoleSchemaV2` and its 89-row projection still pass.

Freeze the complete 2,068-row role and tag schedule. Validate it after final sorting and before RoleIndex encoding.

The schedule must define the toolchain report row and the omitted A05 authority-row treatment. Add exact add, remove, tag-change, and order controls.

Keep this schedule diagnostic. It must not create `Accepted<T>`, a trust root, a pin, or loader authority.

### P2-2: The scalar vector control adds another blocking and unbounded fixed-path reader

`diagnostic_controls.rs:196-211` uses `File::open` before checking the file type.

This reader omits `O_NONBLOCK`, `O_NOFOLLOW`, and descriptor-to-path identity checks. A FIFO replacement can block before `metadata().is_file()` rejects it.

The reader checks the 4 MiB limit only before `read_to_end`. A growing regular file can exceed the claimed cap before the final equality failure.

The reader also lacks an after-read descriptor and pathname identity comparison.

Read the vector through the existing checked measurement path. Bind its exact path, 4,158 bytes, and SHA-256 before returning bytes.

Add FIFO, symlink, growth, and replacement controls through a disposable reader seam. Do not mutate the frozen vector.

The existing FIFO controls cover only the two measurement sessions.

### P2-3: Two control summaries report an unmeasured candidate baseline

`run_scalar_wire_controls` sets `baseline_passed = true` at `diagnostic_controls.rs:167`. It never builds the fixed candidate.

`run_fifo_rejection_controls` sets the same field at `fifo_controls.rs:84`. It also never builds the fixed candidate.

The PNG and compilation controls do build the candidate before reporting a passing baseline. The field therefore has inconsistent evidence semantics.

Remove the baseline field from the two focused summaries, or report whether a candidate baseline was actually checked.

Do not infer a complete candidate baseline from scalar bytes or FIFO rejection alone.

## Original finding reconciliation

- **Scalar wire:** closed at source level. The local adapter changes integer payloads to big-endian bytes at `saved_report_adapters_v1.rs:1016-1020`.
- **Measurement FIFO opens:** closed at source level. Both measurement sessions add `O_NONBLOCK`, and two focused FIFO controls exist.
- **Role schema:** partially closed. The new diagnostic name and 89-row toolchain projection do not cover the full 2,068-row candidate.
- **PNG callback executable:** closed at source level. `argv[0]` is joined to `controlExecutable.path`, with a two-copy mutation control.
- **Manifest aggregates:** closed. Both domain-separated recipes reproduce the saved source and external aggregate hashes.
- **Allocation wording:** closed. The contract now limits the counter to unique descriptor-read bytes and excludes clones, parsed JSON, RSS, and native allocations.
- **Compilation limitation:** closed. The candidate now uses `CompilationAndControlsRequireSeparateEvidence`.

The copied A05 adapter differs by the two endian conversions and the private scalar-control seam. The frozen A05 source remains an external lineage binding.

## Confirmed bounded properties

The public loader accepts no caller evidence path, role list, count, trust root, or permission.

The returned type is `RustProducerDiagnosticCandidateV2`. It cannot construct `Accepted<T>`, an active pin, or production loader authority.

The candidate row guard rejects Swift, observer, comparator, acceptance, and authorization roles.

The loader path selects only the Rust toolchain adapter. It binds no Swift, observer, or comparator report.

All source scope fields remain false for native execution, product integration, media, GPU, Resolve, watch, listen, and creative acceptance.

These properties do not close the three P2 source-readiness findings.
