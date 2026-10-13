# Rust producer qualification A03 source peer review

## Result

The frozen A03 package is not ready for compilation.

All four A02 findings are repaired. I found no P1 and one new P2 metadata defect.

This review is source-only. I did not compile, import, execute, or modify the package.

## Finding

### P2 — two predecessor aggregate labels contain A03-era values

`source-package-manifest-a03.json:952-953` labels these values as A02 aggregates:

- `qualificationA02SourceAggregateSha256` = `d3bdadb014d9a572946880fae13658c4f72888106ad9c4ace9b1e8712fa2c049`
- `qualificationA02ExternalAggregateSha256` = `1428b76b9df3b6bc06c49e6e629ba43aab30189290c5219b0c38c4e9559e97e4`

Neither value is the frozen A02 aggregate.

The verified A02 values are:

- source = `babe43dc9c6eff45c905f77a49894f691a3ea2be4b0b78e9d2dfc76adf6962f8`
- external = `451ed5a3f4eb443402469b5f26d6c17731306cafd4d0133151948bc492e9388c`

The second mislabeled value is the current A03 external aggregate. Replace both predecessor fields with the verified A02 values.

The eight A02 package files and both A02 reviews are separately bound and rehash correctly. This defect is limited to the two explicit predecessor labels.

## A02 repair verification

The fixed recipe now owns `rust-producer-qualification-a03-attempt-a01/tmp`. The attempt, evidence, diagnostic, and reader-control paths all use the A03 identity.

Each runner case now depends on evidence row `0011`, the canonical report. Each case also depends on row `0006`, the actual invocation.

The manifest and contracts now declare UTF-8 row ordering and exact framing. The external aggregate reproduces after the declared role-then-path sort.

The public contract now shows `FixedReconstructionDiagnostic::publish_fixed_diagnostics`. It also states that the trust root appends Source acceptance, peer, and parent rows.

## Verified receipts

| Item | Verified result |
| --- | --- |
| `source-package-manifest-a03.json` | 64,579 bytes; `92339f65ba2554090cdd01e78ff3a22192496194c82fd1deb579b462d6f14761` |
| Package source rows | 8 of 8 matched; 133,496 bytes |
| Source aggregate | `92d6a67f158cc04a291e8c9a12d03434966ffd52203f1ccc542d6ba1592468ba` |
| External rows | 124 of 124 matched; 29,569,950 bytes |
| External aggregate | `1428b76b9df3b6bc06c49e6e629ba43aab30189290c5219b0c38c4e9559e97e4` |
| A02 package files | 8 of 8 matched their frozen receipts |
| A02 reviews | Parent and peer files matched their frozen receipts |
| A10 predecessor closure | All 65 external bindings matched bytes and SHA-256 |
| Direct dependency archives | Exact `libc`, `sha2`, `serde`, and `serde_json` archives matched |

All 15 absolute file imports in `src/lib.rs` remain bound. The complete dependency source closure remains bound.

The source candidate remains 2,068 rows. The Build, Input, and PNG projections remain 18, 25, and 8 rows.

The runner schedule remains 35 measured rows plus 28 semantic rows. All 63 role and tag pairs remain fixed.

The source evidence order remains Source, Build, Input, and PNG. The future Source subject retains nine nested evidence rows.

The bounded reader, private revalidation, and fail-closed trust behavior are unchanged from A02.

## Evidence boundary

A03 has not been compiled or executed. No diagnostic vector has been published.

The runner RoleIndex byte count and SHA-256 remain pending actual publication and independent review. Trust data must not be authored from source expectations alone.

The production pin and future evidence directory remain absent. A03 creates no acceptance, authorization, native execution, media result, or product authority.

This review is same-model-family and nonblind. No cross-family review is available or claimed.
