# Comparator control runner design A06: parent review

Root read the complete A06 design and its complete A12 source peer review.
A06 is 12,990 bytes with SHA-256 `045990f77f91885dc2e9f27522eee45dfeae453e6b9302ce9a14fa523421ad3e`.
No source helper, control, comparator, compiler, or native process ran.

A06 makes the finite output policy, result shapes, capture lifecycle, and pending package boundary explicit.
The attempt file allowlist includes runner records under a 16 MiB cumulative cap.
The preserved A11 and A12 manifests remain excluded authorities.

Two P2 contract defects require a narrow successor before implementation.
There are no P1 findings in this inert design artifact.

## P2: the source closure includes the authorization that seals it

The runtime/source section places the external authorization in the source closure.
The external authorization also seals the source-closure hash.
That relationship creates a hash cycle.
Excluding the closure's own row does not break the authorization cycle.

Finalize source and runtime files first.
Write the source closure without the closure itself or its authorization.
Then write a separate external authorization that pins the closure and finalized sources.
The runner must verify both records independently.

## P2: captured loader provenance is given filesystem fields it does not observe

The report and seal type `loaded_comparator_source` as `FileIdentity`.
That type requires device, inode, mode, bytes, and hash.
The child loader observes only the retained source payload's path, byte count, and hash.
It does not emit descriptor metadata for that output record.

Use a distinct `CapturedLoaderRecord` with the exact three source-defined fields.
Keep wrapper descriptor observations in `wrapper_observed_source: FileIdentity`.
Do not infer filesystem metadata for the payload passed to `exec`.

## Timing provenance correction

A06 calls its 15-second deadline an unchanged A04 value.
A04's sketched request actually declares `timeout_s = 30.0`.
The reviewed A03 capture backend uses the selected 15-second control policy.

The successor may retain a fixed 15-second deadline.
It must identify that value as the new comparator policy or explicit A03 reuse.
The concrete 2-second grace and 1-second drain/reap values remain finite requirements.

## Pending case-gate interpretation

Root found that the live A11 `swift_case_gate_passed` tests contract validity.
It can return true for a structurally valid observation-only rejected prefix.
Native support qualification remains separate and false for observation-only cases.
The A12 peer's proposed false result for every observation prefix needs reconciliation before source or schema changes.
Failed dispositions must still return false.

## Disposition

Preserve A06 and repair the cycle and loader type separately.
Freeze the final control schema only after the case-gate interpretation agrees with the actual comparator source.
Runtime snapshot source preparation remains independently useful.
No native, text, product, playback, hearing, or creative acceptance follows from this design review.
