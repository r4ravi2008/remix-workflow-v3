# Comparator runner A09 parent design review

A09 remains source-only and unimplemented.
Its proposed snapshot wire does not match the frozen runtime snapshot A09.
One grouped P2 blocks implementation until an exact-wire successor is reviewed.

Root read all 622 lines and 23,624 bytes.
The frozen design SHA-256 is `5f3b0c0544b659b44b115839e73caa075b2bcf43a7585074ad1c936e48244eb6`.
Root read the complete runtime snapshot source/contract/rationale change and independently checked the fixed overlay projection.

## P2: snapshot and overlay wire mismatch

The runner proposes embedded `recordDeclarationOverlay` fields and rows.
The snapshot emits `recordDeclarationComparison` and binds a separate six-key overlay artifact.
The overlay rows use declared/current byte/hash names and contain no diagnostic filesystem identity.
Installed rows are nested under each distribution and carry an `observed` file object.
Their match flags are boolean or null.

The runner's universal non-overlay declaration-equality rule cannot accept 508 unsigned rows.
The exact domain has 995 declared matches, 508 independently observed undeclared rows, and 45 fixed divergences.
A successor must bind those exact shapes and counts without synthesizing missing declarations.
It must use the exact schema-4 state and closed scope flags.

The live-domain before/after/readback requirement is otherwise retained.
It detects ordinary drift; it does not establish atomic execution from held file descriptors.
The report remains absent, so no successful runtime authority exists yet.

Two rationale statements need correction in the same successor.
A08 failed before publication and has no saved snapshot report.
The stated sequence performs four scans: preflight, immediate prelaunch, postchild, and parent readback.
The read limit applies separately to each domain observation.

A14 schema 3 and its 59 ordered result rows remain unchanged.
External authorization remains last and outside the package/source closure to avoid self-authentication.
No process, import, control, native, GPU, Resolve, playback, hearing, or creative acceptance occurred in this review.
