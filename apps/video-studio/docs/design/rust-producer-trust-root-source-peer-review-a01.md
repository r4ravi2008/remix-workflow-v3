# Rust producer trust root A01 peer source review

## Disposition

I found one P1 and one P2 in the frozen A01 package.

The runtime trust boundary is fail-closed and matches the selected A06/A07 shape.
The package is not ready for its declared direct control run.

Two negative controls use a stale acceptance reference.
They stop before the validators named by their expected results.

The source-package aggregate matches the current files through an externally reconstructed recipe.
The manifest does not describe that recipe without ambiguity.

This was a read-only, separate-author review.
It is same-model-family and nonblind.

I did not compile, import, assemble, or execute the package or controls.
I created no pin, authorization, attempt directory, or native process.

## P1: two mutation controls stop at the artifact-reference join

`src/source_controls.rs:269-289` changes the source acceptance bytes and updates the manifest's acceptance reference.
The control then calls `reconstructed_source(&plan, false)`.

`src/source_controls.rs:343-363` repeats the same sequence for the reference-cycle mutation.

`reconstructed_source` takes every acceptance reference from the original fixture plan at lines 538-559.
Its top reference still names the original 796-byte acceptance record and original SHA-256.

The memory backend measures the changed bytes first.
`src/trust_root.rs:561-565` compares those bytes with the stale original reference.
Both cases therefore return `artifact_reference_join`.

The controls expect later failures:

- `swapped_reviews_rejected` expects `trust_entry_join`;
- `acceptance_reference_cycle_rejected` expects `acceptance_reference_cycle`.

`expect_error` converts either mismatch into `control_error_code` at lines 663-680.
`run_fixed_source_controls` then returns before constructing its report.

Repair both controls by rebinding the reconstructed source's top acceptance reference.
The new reference must describe the exact mutated bytes used by the updated manifest.
Keep that rebind inside the feature-gated fixture boundary.

The swapped-review case will then reach the manifest-versus-record join.
The cycle case will then reach the acceptance-reference-cycle check.

This is a control blocker, not evidence that the production trust check accepts either mutation.

## P2: the source-package aggregate recipe is ambiguous

All 36 manifest rows match their current paths, byte counts, and SHA-256 values.
Their total is 129,322 bytes.

The declared aggregate is:

`416f741add9eeef84e92767dbcfdda2143162b697f19e18ced915d90b03ddea1`

I reproduced it with this external recipe:

1. Hash ASCII `rust-producer-trust-root-source-package-v1` and one `0x00` byte.
2. Sort rows by raw UTF-8 path bytes.
3. Hash each row as `u32be(path length)`, path bytes, `u64be(file bytes)`, and raw SHA-256.
4. Add no row-count, total-byte, separator, or trailing value.

The manifest's decoded `aggregate.domain` value ends with bytes `[92, 92, 48]`.
Those bytes are two literal backslashes followed by zero.
Hashing that decoded value produces a different digest.

The `algorithm` field also omits ordering and prefix or terminator rules.
No package document supplies the missing recipe.

This does not change the verified current file identities.
It prevents an independent consumer from reproducing the package digest from the manifest alone.

A successor should encode the domain unambiguously.
It should also declare ordering and every framed field in the aggregate recipe.

## Verified trust boundary

The public subject-key enum contains exactly two values:

1. `RustProducerSourceV1`;
2. `RustProducerRunnerV1`.

The evidence-class enum contains exactly five values:

1. source;
2. build;
3. input;
4. PNG control;
5. runner.

Source qualification requires source, build, input, and PNG evidence in that order.
Runner qualification requires only runner evidence.

The trust manifest requires exactly two ordered entries.
Strict JSON parsing rejects duplicate, missing, unknown, and wrong-type fields.

Each acceptance record has one closed kind, version, role schema, scope, disposition, and limitation list.
`executionAuthorizedByRecord` must remain false.

Peer and parent reviews are opaque measured artifacts.
The loader binds their exact paths, byte counts, hashes, and file identities.
It does not infer review meaning from Markdown content.

The filesystem reader uses `O_NOFOLLOW`, `O_NONBLOCK`, and `O_CLOEXEC` on Unix.
It checks regular-file type, descriptor stability, pathname stability, byte count, and SHA-256.

The source RoleIndex must contain exact nested rows for build, input, and PNG records and reviews.
The loader compares those rows with freshly measured artifacts.

`ReconstructedSubjectV1<T>` and `qualify_reconstructed` are crate-private.
`Accepted<T>` has private fields and a private constructor marker.
Its value extraction is crate-private.

The source contains no production pin and no embedded production manifest.
`open_pinned()` returns `pinned_manifest_absent` before parsing.

The package cannot create attempt authorization.
It has no Swift, observer, orientation, comparator, media, or provider prerequisite.

## Frozen package and direct recipe

The reviewed package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-trust-root-a01`

The self-excluding manifest is 13,070 bytes with SHA-256:

`2e31a83c6ecf07b8d99270e4db298892669983504a3289a3438a26459240d8a2`

All 17 external bindings match their declared 240,985 bytes and SHA-256 values.

The fixed compiler and four direct archives match the saved preflight authority.
The direct recipe binds 33 required source and fixture inputs.

The recipe declares one library build, one control-harness build, and one harness invocation.
It uses the fixed compiler, target, dependency roots, explicit extern archives, `panic=abort`, and thin LTO.

The build and control attempt roots were absent during this review.
No recipe command was executed.

The source static check is text evidence only.
It is not a Rust parse, typecheck, link result, or control result.

## Bounded conclusion

The A01 trust implementation has the selected closed ownership and fail-closed production state.
The two findings require an additive source successor before direct controls run.

A later production pin still requires reviewed real subjects, five real acceptance records, and two manifest entries.
It also requires external loader source and binary bootstrap review.

Nothing in this review establishes native feasibility, media output, playback, watching, hearing, or creative acceptance.
