# Rust producer Runner A10 staged-authorization helper A03 peer source review

## Disposition

I found no P1 or P2 source finding in the narrow A03 successor.

A03 closes the terminal receipt-ordering P2 from the A02 peer review.
The inherited authorization validation and bounded readback scope remain unchanged.

This was a read-only, same-family, nonblind peer review.
I reviewed the complete A02-to-A03 source delta and its inherited fixed scope.

I did not import or execute the helper.
I launched no compiler, child, control, native, media, or GPU process.
I created no stage, bootstrap, authorization, sidecar, proof, or state record.

## Frozen helper receipt

The reviewed helper is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a10-staged-authorization-readonly-root-a03.py`

It is 19,313 bytes and 359 lines.
Its SHA-256 is:

`a1727f68d7d441abfaf898c52cd7204fcf28f9e145a3ca0439a4285073101617`

The predecessor A02 peer review is:

`apps/video-studio/docs/design/rust-producer-runner-a10-staged-authorization-readonly-source-peer-review-a02.md`

That review is 5,503 bytes with SHA-256:

`9a37fe32ba2ee73b7c7ba5bbd0c0007dd8457d26409825909fd736aed39ac51e`

## Exact A02-to-A03 delta

The proof filename changes from `staged-authorization-parent-readback-a02.json` to `staged-authorization-parent-readback-a03.json`.

The success print moves from the protected `try` body to after the `finally` block.
No other source line changes.

The helper still writes the proof before closing the retained directory descriptors.
It preserves that proof as evidence if a later close fails.

The helper now completes every retained directory close before printing success.
The `require(not close_errors, 'directory_close_failed')` check also completes before that print.

A close failure therefore skips the success print.
The outer handler emits only the bounded failure object and exits with status 1.

The returned success receipt now unambiguously means terminal directory cleanup succeeded.

## Inherited fixed scope

A03 retains A02's active `require` checks and nonoptimized-Python requirement.
It retains strict duplicate-key JSON parsing and nonfinite-number rejection.

The helper still compares the exact 17-field provisional `AttemptAuthorization` value.
It retains exact JSON types, keys, list lengths, list order, and scalar values.

The operation remains `native_text_rust_a05_attempt`.
The implementation remains `rust_a05`, and the repetition remains `primary`.

The fixed producer path, bytes, SHA-256, identity, command, environment, and policies remain unchanged.
Both native acceptance and product integration remain false.

All four qualification references remain fixed.
Their aggregate order remains source subject, source final, runner subject, runner final, pinned manifest, trust manifest, runner manifest, then runner binary.

The bootstrap schema, source-manifest receipt, and binary receipt checks remain unchanged.

The helper retains descriptors for the output parent, staged run, and unit root.
It still rechecks their device, inode, and mode through proof publication.

Directory size, modification time, and change time remain recorded observations.
They are not part of the live directory anchor.

The output parent must contain only the staged run.
The staged run must contain only `authorization.json`.

The proof write remains exclusive and bounded.
Its byte readback, SHA-256, file identity, parent identity, and directory durability checks remain unchanged.

## Deferred applicability

Runner A10 remains provisional.
This review does not qualify an absent or future staged authorization, bootstrap record, binary, or source manifest.

Exact applicability requires final A10 source, build, control, bootstrap, and staged authorization evidence.
Those missing future artifacts are not source findings in A03.

Nothing in this review establishes helper execution, authorization acceptance, process launch, native feasibility, media output, playback, or creative acceptance.
