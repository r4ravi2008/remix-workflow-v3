# Swift parent source review A03

The parent read the complete A02 baseline and every A03 changed-source hunk.
The parent also read both complete A03 contract documents.
A03 remains unbuilt and unexecuted. A01 and A02 remain preserved.

## P1: mandatory PNG admission always fails

`finalizeNativePNG` reserves `ledger.cap - ledger.outstanding`.
`reserve` calls `appendEvent` before updating its outstanding total.
That event requires space after the proposed reservation.
The proposed reservation leaves zero space, so the event cannot fit.
The mandatory orientation PNG therefore cannot pass this path.

Derive the PNG bound from its image geometry and retain finite event headroom.
Do not enlarge the shared 16 MiB limit.

## P1: the large glyph image lacks a fitting snapshot owner

The 2048 by 1024 RGBA glyph buffer owns 8,388,608 bytes.
A separately charged logical image snapshot of that size makes their overlap 16 MiB before existing owners.
The current source does not reserve the snapshot owner.
Use a fitting, separately reviewed image representation with explicit owner lifetimes.
The shared text geometry and orientation hypothesis must remain unchanged.

## P2: native observations still allocate before admission

`copiedNativeString` bridges the complete CFString before checking or reserving its bytes.
PostScript names still lack the shared 128-byte ASCII admission rule.
The native tag inventory bridges and sorts every tag before enforcing the 128-tag cap.
Count and admit these owners before copying.

The allocation event encoder also creates its Data before checking remaining capacity.
Reserve fixed event scratch and bound the strings that enter each event.
The encoded-length check alone does not establish preallocation admission.

## P2: initial native metrics are raw values

`selectedFace` fills `InitialNativeFaceRecord.glyphs` and `unitsPerEm` from parsed SFNT values.
Read the actual CTFont metrics into those native observation fields.
Preserve raw and native facts separately.

## Causal evidence and policy checks

Nonfinite matrix observations retain raw `Double` values.
The default JSONEncoder cannot publish NaN or infinity.
Declare a bounded lossless representation for those causal values before execution.

The schema describes nonmonotonic runs as nonqualifying.
The shared protocol permits nonmonotonic indices and records them.
Keep the source and schema consistent with that contract.

The source now retains the exact attributed-string owner, publishes raster evidence before padding checks,
and uses exclusive descriptor-relative output creation.
Those repairs are useful. They do not close the remaining source blockers.

## Disposition

Preserve A03 and repair these findings in A04.
A separate peer review is in progress.
No build, native observation, product text support, hearing, or creative result is accepted here.

Reviewed Swift source SHA-256: `ab8dd6b8b52334ac3a11cd9f81507d8ae0d503ead3aad0dbff4af93ec9023ac6`.
Reviewed schema SHA-256: `be44bf8a59d0524f2791c2a976b031c1657daa3141bcd587a0402f1da022fcba`.
Reviewed rationale SHA-256: `c29d28e4dcafeb7cc64cfbc18d9988956f7adf220a5dbd7c9e275455632eacc3`.
