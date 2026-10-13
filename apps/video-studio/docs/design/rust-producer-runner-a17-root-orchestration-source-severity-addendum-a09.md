# A09 capsule wording severity addendum

This addendum revises the severity of one finding in the frozen A09 source review. It does not alter the A09 package, its receipt, or its source review.

## Frozen evidence

- Review: `rust-producer-runner-a17-root-orchestration-source-peer-review-a09.md`, 6,284 bytes, SHA-256 `e3e589ba9702ea6af772881b98f1a350ad72e012b51455abd60594cee3e2e2a0`.
- Capsule: `rust-producer-runner-a17-root-orchestration-preparation-a09/root_inline_launch_capsule_a09.py`, 11,393 bytes, SHA-256 `59cb08d584ae309af0bb005eea06e3820b38aee3f23e634db584c10a295fdc25`.
- Receipt: `rust-producer-runner-a17-root-orchestration-preparation-a09/preparation-receipt-a09.json`, 32,349 bytes, SHA-256 `4b4e823afdcf88cf4d34cee64cd34618e9e867be21712a82505e2abce7584998`.
- A08 predecessor capsule: 11,393 bytes, SHA-256 `4f36122feeb4230dc6b8821d2243ae000e414882613af903cd75861430d8ee6a`.

The A09 capsule contains the string `Runner A15` exactly once. It is the module docstring on line 1. The A08 predecessor contains the same inherited docstring. A09's fixed-label transformation otherwise preserves the capsule's normalized AST and executable bytes for the intended A17 substitutions.

## Selector and attestation check

The stale wording is not executable state. The capsule does not read `__doc__`, and no selector, digest, path, operation, scope, or receipt field is derived from the docstring.

The executable checks select the A17 operation `runner_a17_root_inline_launch_a09`, the A09 recipe path and digest, the A09 capsule path and digest, and the `fixed-compile` caller record. They also verify the fixed visible and original argument vectors, caller path, caller bytes, caller SHA-256, argument count, and scope flags.

The A09 recipe uses the A17 current source key `a17_external_evidence_rows=204`. Its dependency preflight is bound by SHA-256 `2b89dcc5dc5472867c17f27ac1474726ba8230f9faa6b3a1ab405eec7eaf64f5`. The independent closure rejoin found 116 scalar/path joins, zero missing paths, and 65 selected dependency rows. These checks do not use the docstring.

The recipe's `hostDiagnostic` points to a historical A15 diagnostic record by explicit path and digest. That record is separate from the A17 capsule, caller, operation, source receipt, and current recipe key. It does not make the inherited docstring an executable selector or a false A17 attestation.

## Disposition

The finding is P3 documentation drift, not P2 executable identity drift. No executable selector, source digest, authorization gate, or attestation depends on the stale text. The current A09 source remains acceptable on this issue, subject to its stated source-only and unexecuted scope.

Correct the docstring in a later successor or documentation-only revision. Do not rewrite the frozen A09 bytes to change this disposition. This addendum performed no candidate import, execution, compiler, control, or native-process action.
