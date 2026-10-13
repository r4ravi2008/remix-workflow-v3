# Payload A03 parent source review

A03 is rejected before build. A04 repairs are in progress. A01 through A03 remain preserved.

The parent read the entire 2,041-line module, binary, 570-line external runner, and all three contract documents.
The parent also checked the 58-file manifest and eleven frozen fixture declarations.
No payload build, measurement, product, media, GPU, or Resolve operation ran.

## Findings

1. P1: The runner creates `measurement-output` before launching the binary.
   The binary calls `open_output_root`, which requires a new directory through `create_dir`.
   Every otherwise valid invocation therefore fails before collection.
   Let the binary create its exclusive output directory.

2. P1: The runner verifies the executable, executable identity, and optional build manifest only before launch.
   The later checks cover package sources, runner files, and the source manifest.
   They do not establish the promised executable before/after closure.
   Recheck every authority file after success, nonzero exit, and timeout.
   Preserve completed before records and partial after records when a check fails.

3. P1: The EntityId key estimate uses a 27-byte `to_owned` template.
   The actual keys use `format!` with dynamic count and index fields.
   Rust 1.94.0 doubles the 17 literal bytes for its initial formatting capacity.
   The resulting 34-byte capacity exceeds the declared 27-byte heap estimate.
   Admit the actual construction capacity before count-sized allocations.
   This conclusion comes from the pinned primary [core formatting source](https://github.com/rust-lang/rust/blob/1.94.0/library/core/src/fmt/mod.rs) and [alloc formatting source](https://github.com/rust-lang/rust/blob/1.94.0/library/alloc/src/fmt.rs).

4. P2: `write_failure_from_report` clears completed map and precreation rows.
   A report-stream failure therefore loses completed measurement evidence.
   Preserve those bounded rows in the causal failure record.

## Accepted repairs

The missing `Serialize` implementation is present.
Canonical JSON uses a bounded count pass before reserve and a second serialization pass.
The Vec becomes the String through ownership transfer.
Map collection kinds run sequentially after checked precreation estimates.
The report requires 28 ordered map rows and seven precreation budgets before completion.
Failure output uses compact fixture identities and explicit file synchronization.

These repairs do not establish product admission, native allocations, physical memory, or RSS.
The declared scope remains application-owned Rust observations over fixed copied fixtures.
