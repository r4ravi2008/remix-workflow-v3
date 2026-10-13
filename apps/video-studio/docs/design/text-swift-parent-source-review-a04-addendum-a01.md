# Swift A04 input admission addendum A01

A04 remains rejected and byte-preserved. The original parent review remains unchanged.

The parent found one additional P1 while completing the source read.
`run` loads cases, manifest, and authority bytes.
It checks the authority hash before decoding.
It decodes cases and the font manifest before checking their frozen hashes in `verifyAuthority`.

The decoded-owner bound assumes the fixed fifteen cases and two fonts.
Changed JSON could create larger typed collections before the later hash rejection.
The fixed owner bound must apply only after exact frozen input admission.

A05 must verify each case and manifest byte count and SHA-256 before typed decoding.
Keep the later cross-field authority checks as well.
The normal accepted inputs, drawing policy, and caps remain unchanged.

The parent sent this repair to the Swift author.
No Swift build, typecheck, native framework, or probe operation ran.
