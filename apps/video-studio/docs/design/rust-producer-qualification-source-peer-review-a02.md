# Rust producer qualification A02 source peer review

## Result

The frozen A02 package is not ready for compilation.

I found one P1 build-recipe blocker and three P2 contract defects. The remaining Rust-only qualification shape is coherent.

This review is source-only. I did not compile, import, execute, or modify the package.

## Findings

### P1 — the fixed build recipe uses the A01 temporary directory

`direct-build-recipe-a02.json:124` sets `TMPDIR` to
`rust-producer-qualification-a01-attempt-a01/tmp`.

The library, diagnostic, and attempt paths all target A02. Both A01 and A02 attempt roots are currently absent.

The declared A02 recipe can therefore fail at the first temporary-file use. It can also place A02 compiler state under an older generation.

Set `TMPDIR` to the create-new A02 attempt directory. Keep the directory inside the same exclusive attempt ownership boundary.

### P2 — case booleans depend on stale evidence indexes

`src/qualification.rs:511-521` makes every case boolean depend on these rows:

- `rust.runner.evidence.file:0010`, the source-control executable;
- `rust.runner.evidence.file:0005`, the source-control stdout file;
- the result count;
- the passed count.

The canonical report is row `0011`. The actual invocation is row `0006`.

The current graph therefore does not implement the contract at `qualification-contract-a02.md:63-66`. The manifest repeats the unsupported claim at `source-package-manifest-a02.json:1276`.

Make each case depend on the measured canonical report and invocation. A dependency on a corrected `rust.runner.control.semantic_join` is also sufficient when that join retains both rows and the case facts.

### P2 — the external aggregate omits its row-order rule

All 114 external rows match their current files. Their total is 29,427,849 bytes.

The declared framing reproduces the saved aggregate only after sorting by `(role UTF-8, path UTF-8)`. The manifest does not declare that ordering.

Using the listed array order gives:

`85aecf6d7cdac978ad4913740e696e88230e113b5e3f65d661940970703a87ed`

Sorting by role and path gives the declared digest:

`451ed5a3f4eb443402469b5f26d6c17731306cafd4d0133151948bc492e9388c`

The visible inversion is between `trust_root_source_controls` and `subject_adapter_subject_observation` at `source-package-manifest-a02.json:821-832`.

Declare the ordering in `externalAggregate.encoding`, or store rows in that exact order. A verifier must not infer a hidden sort.

### P2 — the public contract differs from the compiled API and final Source graph

The contract advertises this free function at `qualification-contract-a02.md:10`:

```rust
pub fn publish_fixed_diagnostics(
    value: &FixedReconstructionDiagnostic,
) -> Result<QualificationControlSummary>;
```

The free function is private at `src/qualification.rs:1756`. The public API is the method at `src/qualification.rs:276-278`.

The contract also says the trust root appends only the top Source peer and parent rows. The implementation appends acceptance, peer, and parent rows at `trust_root.rs:429-443`.

Correct the contract to show the actual method call and all three appended rows. These changes affect documentation only.

## Verified receipts

| Item | Verified result |
| --- | --- |
| `source-package-manifest-a02.json` | 58,807 bytes; `fbb55583077c83023b3653d156afe487aabad047b0d4b56de6dac2458267c757` |
| Package source rows | 8 of 8 matched; 132,058 bytes |
| Source aggregate | `babe43dc9c6eff45c905f77a49894f691a3ea2be4b0b78e9d2dfc76adf6962f8` |
| External rows | 114 of 114 matched; 29,427,849 bytes |
| External aggregate | Matches only with the undeclared role/path ordering above |
| A10 external closure | All 65 predecessor bindings matched bytes and SHA-256 |
| Direct dependency archives | Exact `libc`, `sha2`, `serde`, and `serde_json` archives matched |
| Dependency source closure | 35 packages and 1,847 files remain bound by `6e06cc43b0c23b1aa3f1c9e9577d458846fb3d7e05ed731409b27b91528f6577` |

All 15 absolute file imports in `src/lib.rs` have matching external bindings. The imported code uses only the four declared direct external crates.

## Verified qualification shape

The source candidate remains the complete 2,068-row A10 graph. The Build, Input, and PNG projections remain 18, 25, and 8 rows.

The future Source subject adds nine measured nested rows. These rows cover Build, Input, and PNG acceptance, peer review, and parent review.

The evidence order is Source, Build, Input, and PNG. The runner evidence vector contains exactly one Runner entry.

The runner schedule has 35 measured file rows and 28 semantic rows. Its 63 roles are unique and sorted by UTF-8 role bytes.

The runner file closure includes eight source files, one source manifest, ten build files, two output receipts, and fourteen control files.

The reader uses canonical paths, `O_NOFOLLOW`, `O_NONBLOCK`, bounded reads, and before-and-after identity checks. Its four controls exercise FIFO, symlink, growth, and replacement paths.

`full_revalidate` reconstructs both subjects. It compares subject references, final references, final bytes, counts, digests, and summaries.

The production pin and all future acceptance files remain absent. `open_pinned` therefore fails closed before constructing `Accepted<T>`.

## Remaining evidence boundary

A02 has not been compiled or executed. The runner RoleIndex byte count and SHA-256 are not independently qualified yet.

The fixed diagnostic must publish those bytes first. A separate review must bind the published runner receipt before trust data is authored.

The package does not create trust data, execution authorization, a native child, media output, or product integration.

This review is same-model-family and nonblind. No cross-family review is available or claimed.
