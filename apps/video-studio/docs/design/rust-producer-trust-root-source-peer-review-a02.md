# Rust producer trust root A02 peer source review

## Disposition

I found no P1 or P2 source finding in the frozen A02 package.

A02 closes both findings from the A01 peer review.
The production trust implementation and all synthetic fixture bytes remain unchanged.

The package is source-ready for its declared direct build and control recipe.
Compilation and control execution remain separate, unverified steps.

This was a read-only, separate-author review.
It is same-model-family and nonblind.

I did not compile, import, assemble, or execute the package or controls.
I created no pin, authorization, attempt directory, child process, or native process.

## Frozen authority

The reviewed package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-trust-root-a02`

The self-excluding manifest is 15,734 bytes with SHA-256:

`f6f18d6d79c5d579aab937572bc60435faaf5b8a6769b5ef5217f03d59b602b9`

All 36 source rows match their declared paths, byte counts, and SHA-256 values.
Their total is 132,549 bytes.

All 20 external bindings match their declared 263,714 bytes and SHA-256 values.
Those bindings include the A01 manifest and both corrected A01 source reviews.

The A02 source aggregate independently reproduces as:

`fe7a9b7fadad0bc9296d62573e807419c6ef4a74b2b8f9844f636c1b20652234`

## A01 P1 closure: exact changed-record references

`src/source_controls.rs:269-293` creates the swapped-review record first.
It derives `swapped_acceptance` from the exact changed record bytes at lines 271-274.

The updated manifest derives its acceptance-record reference from those same bytes.
The in-memory evidence map also stores those same bytes at the fixed source path.

The reconstructed source receives `swapped_acceptance` at line 289.
The artifact-reference join can therefore complete before the manifest comparison.
The changed peer and parent ordering then reaches the expected `trust_entry_join` check.

`src/source_controls.rs:347-371` applies the same ownership sequence to the cycle case.
It derives `cyclic_acceptance` from the exact changed record bytes at lines 349-352.

The reconstructed source receives that exact reference at line 367.
The acceptance record can therefore reach the expected `acceptance_reference_cycle` check.

`reconstructed_source_with_acceptance` is private and feature-gated.
It replaces only the top source acceptance reference.
Build, input, and PNG-control references still come from the frozen fixture plan.

The ordinary `reconstructed_source` helper retains the original fixture reference.
No production reconstruction or trust API changed.

These conclusions are source-path findings.
The controls have not yet run.

## A01 P2 closure: explicit aggregate recipe

The A02 manifest describes every aggregate framing decision:

1. The domain is ASCII `rust-producer-trust-root-a02-source-package-v1`.
2. One `0x00` byte terminates the domain.
3. Rows sort by ascending raw UTF-8 path bytes.
4. Each row starts with a big-endian 32-bit path-byte count.
5. The path bytes follow the count.
6. A big-endian 64-bit file-byte count follows the path.
7. The raw 32-byte SHA-256 follows the file-byte count.
8. The recipe uses no count prefix, total-byte prefix, row separator, or trailer.

Applying that declared recipe to the 36 measured rows produces the declared aggregate.
No external convention is needed to interpret the domain or row framing.

## Inherited production boundary

`src/trust_root.rs` is byte-identical to A01:

`969c70ac61782cc449806831a8d0179a10dea43616a810443257659ba1c131ec`

`src/lib.rs` is also byte-identical to A01:

`f228ab1de376abffb9ae85162566ffa213ae499d1eeefb329bb1d11a1d08b9ee`

The package still exposes exactly two accepted subject keys:

1. `RustProducerSourceV1`;
2. `RustProducerRunnerV1`.

It still accepts exactly five evidence classes:

1. source;
2. build;
3. input;
4. PNG control;
5. runner.

The manifest and acceptance records retain strict field, type, order, and disposition checks.
Review files remain opaque artifacts bound by exact path, bytes, hash, and file identity.

`Accepted<T>` retains private fields and a private constructor marker.
Reconstruction and accepted-value extraction remain crate-private.

Filesystem evidence keeps bounded, no-follow, nonblocking descriptor reads.
It retains exact descriptor, pathname, byte-count, and SHA-256 joins.

The production pin remains `None`.
The production manifest bytes remain empty.
`open_pinned()` still fails with `pinned_manifest_absent` before parsing.

The trust root creates no attempt authorization.
It has no Swift, observer, orientation, comparator, media, or provider prerequisite.

## Preserved fixtures

All 24 files under `fixtures/` are byte-identical to A01.
This includes all five acceptance records, ten reviews, and seven RoleIndex fixtures.

The fixture trust manifest and control plan also remain unchanged.
Their saved counts, hashes, roles, and synthetic file identities retain A01 authority.

Only the private control wiring changed.
No fixture was rewritten to make a control pass.

## Direct build and control recipe

The direct recipe is 19,545 bytes with SHA-256:

`8d36fc97f086a468cbf1af0d58e54563b0ade2f33734534da459327e014cbf1f`

All 33 source inputs match their declared byte counts and SHA-256 values.
The fixed compiler and four explicit dependency archives match the saved preflight authority.

The recipe declares three fixed commands:

1. build the A02 control-enabled library;
2. build the A02 direct control harness;
3. invoke that harness with no arguments.

The library and harness use the fixed target, dependency roots, and explicit extern archives.
Both compile commands use `panic=abort`.
The final harness build also uses thin LTO.

The harness rejects arguments before running the controls.
It owns one fixed A02 attempt directory and one fixed A02 report name.
It uses exclusive directory and report creation.
The report remains capped at 64 KiB, including its trailing newline.

The A02 build and control attempt roots were absent during this review.
No recipe command was executed.

## Bounded conclusion

A02 is a narrow source successor to A01.
It repairs both stale changed-record references and fully specifies the package aggregate.

The package does not qualify a real producer or runner.
A later production pin still requires reviewed real evidence and external loader bootstrap review.

Nothing in this review establishes native feasibility, media output, playback, watching, hearing, or creative acceptance.
