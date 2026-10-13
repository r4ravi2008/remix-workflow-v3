# Rust producer Runner A10 staged-authorization helper A02 peer source review

## Disposition

I found no P1 source finding and one P2 source finding.

The A02 helper closes the substantive A01 validation gaps.
It matches the provisional Runner A10 authorization schema and fixed policy values.

The remaining P2 concerns terminal receipt ordering after proof publication.
It does not weaken the saved proof bytes or the authorization comparisons.

This was a read-only, same-family, nonblind peer review.
I reviewed source that another author prepared after earlier findings were known.

I did not import or execute the helper.
I launched no compiler, child, control, media, GPU, or native process.
I did not create an authorization, bootstrap, attempt, sidecar, or proof file.

## Frozen helper receipt

The reviewed helper is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a10-staged-authorization-readonly-root-a02.py`

It is 19,317 bytes and 359 lines.
Its SHA-256 is:

`72279ba451114acc90688d3971fe2e902bd5518650c06bca2938a5897267decf`

Static source inspection found no Python `assert` statement.
The helper imports only Python standard-library modules.
Its source contains no subprocess launch API.

## P2: success is printed before retained directory descriptors close

Lines 334–340 publish and recheck the proof.
Line 340 then prints the success object to standard output.

Lines 341–348 close the retained directory descriptors afterward.
The `finally` block raises `directory_close_failed` when any close fails.

The outer handler then prints a failure object to standard error and exits with status 1.
This path can therefore emit both a success receipt and a terminal failure receipt.

The saved proof remains exclusive and measured.
The ambiguity affects the root execution receipt that qualifies that proof.

Move the success print after successful retained-directory cleanup.
Retain the success value in memory until every close completes.
On cleanup failure, emit only the bounded failure object and return failure.

The published proof can remain preserved when cleanup fails.
Its later qualification must still require a successful terminal execution receipt.

## A01 repair verification

A02 replaces every A01 `assert` with an active `require` check.
It also rejects optimized Python with `sys.flags.optimize == 0`.

The helper uses strict duplicate-key JSON parsing.
It rejects nonfinite JSON numbers and enforces bounded reads.

The recursive `same_json` comparison requires exact JSON types.
It also requires exact dictionary keys, list lengths, list order, and scalar values.

The helper retains descriptors for the output parent, staged run, and unit root.
It rechecks each held descriptor against its pathname before and after proof publication.

The current directory anchor uses device, inode, and mode.
Directory size, modification time, and change time remain recorded observations.

The helper requires output-parent inventory to contain only the staged run.
It requires the staged run to contain only `authorization.json`.
It repeats both inventory checks before and after proof publication.

The proof write uses exclusive creation.
The helper verifies written bytes, SHA-256, leaf identity, parent identity, and directory durability.

The outer error path emits a bounded code, exception class, and optional errno.
It states that no sidecar or native producer was published by this helper.

## Provisional Runner A10 schema match

The provisional Rust `AttemptAuthorization` has exactly 17 top-level fields.
The helper requires the same closed field set through recursive comparison.

The operation is `native_text_rust_a05_attempt`.
The implementation is `rust_a05`.
The repetition is `primary`.

The helper matches the fixed producer path, byte count, SHA-256, and six-field file identity.
It matches the producer command and its fixed argument order.

The four-value child environment matches the Rust authorization writer.
The process, output, and cancellation policy values also match.

Both acceptance booleans must be false.
Unknown fields, type substitutions, missing fields, and reordered list values fail comparison.

The helper matches all four qualification references.
It reconstructs the qualification aggregate in the Rust implementation's exact order.

That order is source subject, source final, runner subject, runner final, pinned manifest, trust manifest, runner manifest, then runner binary.

The bootstrap schema and state match the provisional Rust loader.
The helper also binds the bootstrap source manifest and bootstrap binary by path, bytes, and SHA-256.

The Rust `DirectoryObservation` contains an exact path and six-field identity.
The helper requires that shape for parent, run, and working-directory observations.

## Scope and deferred applicability

The Runner A10 source package remains provisional.
The staged authorization, bootstrap record, and current compiled Runner A10 binary were absent during this source review.

Their absence is not a helper-source finding.
Exact applicability requires the final A10 source, build, control, bootstrap, and staged authorization evidence.

This helper is read-only with respect to the producer attempt.
Its only planned write is the separate parent readback proof.

Nothing in this review establishes helper execution, authorization acceptance, process launch, native feasibility, media output, playback, or creative acceptance.
