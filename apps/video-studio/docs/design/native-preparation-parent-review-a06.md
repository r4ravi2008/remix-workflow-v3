# Native preparation A06 parent review

Status: complete source-only read of the 686-line design.
A06 remains unimplemented and creates no execution authority.

Design SHA-256:
`260e83d2b5fb8474b3ef04801b5f28f764ee08e4e94ea648352679cedc2b6eb5`.

A06 replaces the universal file row with seven typed observation variants.
It defines saved-report expansions instead of copying dictionary key counts.
The parent checked current Swift file and directory identities; their six
saved identity fields match the proposed stable identity representation.
Complete adapter cardinality verification remains in the independent peer scope.

The compiled trust pin and separate external loader bootstrap close the
caller-selected acceptance claim at the design level.
No trust manifest, pin, accepted value, or bootstrap authorization exists today.

Two P2 findings remain before implementation.

## P2: current observer terminal shapes are incorrect

The unchanged observer's `main` prints only `result["report"]` after normal parsing.
That object has exactly `path`, `bytes`, and `sha256`.
It contains neither the full observation report nor a nested `report` member.
This applies to passed pixel checks and parsed-but-failed pixel checks.
The return code is zero for passed state and one for failed state.

Only exception branches print the `state`, `error`, and `report` envelope.
A07 must specify both exact shapes and classify them against the saved report.
It must preserve child-owned publication and the actual A06 filename contract.
No observer source change is required for this design repair.

## P2: nested enum wire tags are undefined

The seven observation-kind tags are explicit.
The numeric tags for `ScalarKindV2`, `DirectoryAuthorityModeV2`,
`DirectoryIdentityV2`, and `AliasRelationV2` are not defined.
The instruction to use closed tags does not select those values.

The successor must provide exact nested tag mappings and reject unknown tags.
The independent encoder and decoder must then agree on one complete wire format.

## Disposition

Preserve A06 and both reviews. Repair these two contracts in A07 after peer review.
The comparator accepted enum remains empty and the Rust-first stage split remains required.
No helper, gate, compiler, native, GPU, or Resolve process ran.
