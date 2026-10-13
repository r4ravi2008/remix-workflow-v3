# Swift native text probe source review A09

## Result

A09 is not ready for the isolated producer typecheck freeze. One expected Swift importer blocker remains. Three P2 contract defects also remain.

This review is source-only. I did not build, typecheck, run a control, start a producer, or call any native framework.

The A09 manifest and all eight listed file rows match the current package bytes. The C shim replaces A08's rejected `_silgen_name` declaration with a real imported header.

This is a same-model-family review. It does not provide independent model-family confirmation.

## P1 — the matrix setter still uses an unavailable Swift spelling

`probe.swift:2135`, `:2823`, and `:2986` call `CGContextSetTextMatrix` directly.

The pinned SDK maps that C function to the `CGContext.textMatrix` property setter. `CoreGraphics.apinotes:903-906` defines the setter and getter imports.

A07 already showed the related method spelling was unavailable. The global C spelling is also expected to be unavailable after the API-note rename.

Use `context.textMatrix = CGAffineTransform.identity` at all three sites. Then typecheck the exact A09 producer with `-import-objc-header alpha-context-shim.h`.

This finding is source-derived. A09 has not been typechecked, so no A09 compiler result exists yet.

## P2 — failed-write evidence exceeds its own retained-entry cap

`captureNativePNGBeforeDestroy` creates 13 evidence entries at `probe.swift:2512-2528`.

A failed `.partial` write can add six prefix fields through `mergeFailedFilePrefixEvidence`. It also adds `partialPath` and `partialWriteError` at `probe.swift:2533-2540`.

The post-destroy path then adds one or two more fields at `probe.swift:2681-2702`. The complete-file failure path can retain 23 entries at `probe.swift:2750-2759`.

`maxEvidenceEntries` remains 16. `validateErrorOwners` rejects any larger dictionary at `probe.swift:3413-3423`.

The new prefix branch can therefore replace its causal write failure with `result_owner_cap`. It can also stop case-result publication.

Raise the admitted evidence maximum and its owner formula, or reduce the retained failure fields. Add controls for failed partial-file and failed complete-file publication.

## P2 — two validated state strings remain outside the owner formulas

`matrixOwnerBound` charges `MatrixRecord` and its arrays at `probe.swift:3076-3082`. It omits the separately validated `MatrixRecord.state` payload.

`imageBoundsOwnerBound` has the same omission for `ImageBoundsRecord.state` at `probe.swift:3084-3088`.

The validators enforce both limits at `probe.swift:3275-3292`. The formulas do not add `stringOwnerBound(maxQ16StateBytes)` for either field.

Add that string owner to both formulas. This closes the remaining named nested-owner gap for the declared logical-payload model.

The new validators contain literal `(label)` and `(index)` text in several diagnostics. That only reduces diagnostic specificity and is not a P1 or P2 defect.

## P2 — the report and caller contracts omit new A09 authority facts

`output-schema.md:73-76` says `policy.caps` includes the 64 KiB failed-file-prefix scratch owner. The actual map at `probe.swift:4110` omits that entry.

Add `failedFilePrefixScratch` with value 65,536. The event ledger already records each live reservation.

The source manifest calls `alphaContextShimSha256` a caller binding at `source-manifest-a09.json:19-24`. The CLI, report inputs, and environment do not carry that hash.

The exact binary hash can transitively bind the header through a checked build closure. That closure does not exist in this source-only package.

Either add the header hash to the request and report, or revise the manifest wording. A later gate must bind the exact header, compile command, binary, and report.

## Confirmed repairs

- A09 removes A08's `_silgen_name` declaration.
- `alpha-context-shim.h` uses SDK C types, nullable data, `NULL`, and `CF_RETURNS_RETAINED`.
- The header is a named producer compile unit in `source-manifest-a09.json`.
- The Swift helper uses the imported wrapper for all three alpha-only contexts.
- The wrapper keeps `kCGImageAlphaOnly` and does not substitute gray or RGBA storage.
- The wrapper returns one retained context. The active raster lease already covers its backing bytes.
- A08 corrected the A07 compiler diagnostics for table APIs, direction, scalar construction, consumer construction, expression complexity, and argument labels.
- Output descriptors now use `O_RDWR`. Failed writes inspect the still-owned descriptor before close.
- Prefix count, digest, identity, completeness, and status remain separate from the intended sealed stream.
- Cumulative component counters are now documented separately from live peak and final outstanding bytes.
- Successful repeats retain their actual main, guard, clipped, and reference mask records.
- The shared PNG callback source is unchanged at its previously reviewed hash.

The C shim's imported spelling and Core Foundation ownership remain unverified until the exact typecheck and build succeed. Native lifetime and alpha output remain unverified until execution.

## Package identities

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `source-manifest-a09.json` | 3,805 | `2b5f4bcc697c7a4160ddf73fca55924a97ce1eb8272d6e601de456a725e59c76` |
| `probe.swift` | 238,933 | `deee25b0f4b783153e20b9f2c601647a035da0385d6ad89b997c8bec513d8c98` |
| `alpha-context-shim.h` | 936 | `45bab2f2be3022da7fda10884197d4e98b709bf9ce60dcb983d7f13d6aac4144` |
| `png-consumer-shared.swift` | 6,693 | `22c66166890efc6dfd2e2076d1117139e1b7481f71a4e63df676ab9b2e185866` |
| `png-consumer-control.swift` | 12,513 | `ef5a4ff38b6c548e016c949665c36411eb90f2fb8d0d2c72657e1826a3825921` |
| `output-schema.md` | 20,029 | `bdda49801dfe05ca44a6253fbceb327d7b30e37782ab46be7c43cf9d0dc61d7c` |
| `source-rationale.md` | 22,814 | `24681c1d3b84174b240b3baca1992b3e64542b16a0e2d4cf0d06df086d7186b7` |
| `allocation-ledger.md` | 5,894 | `119a78633d427524d26e2ce7ff19c24f00dc9750153058cd3c20d7af03706590` |
| `png-consumer-control-schema.md` | 2,931 | `7ee4fd6bb7751aed272aafa6f89ad7df2eee99ce58123329465bd475e89c6b2f` |

The preserved A07 compiler report is `32ab9bb62ecc2856a351c88bedefd4580055adec42ec6c8d978dea3b4540a858`. It records producer typecheck failure and control typecheck success.

## Scope boundary

This review does not establish compilation, callback behavior, CoreText shaping, CoreGraphics alpha semantics, ImageIO output, loaded producer identity, or native release timing.

It provides no playback, watching, hearing, creative, product, or full-film acceptance.
