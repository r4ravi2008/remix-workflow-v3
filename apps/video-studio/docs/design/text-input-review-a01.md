# Native text input review A01

## Result

The preserved text inputs are internally consistent and remain pre-runtime evidence. I found no P1 integrity failure. The review has three P2 input-contract findings described below.

This review covers the task brief, font acquisition, raw TrueType containers, repository provenance, preserved alpha documents, synthetic Unicode cases, and the pre-text project records. It does not run shaping, rasterization, CoreText, CoreGraphics, compilation, or native export.

The raw checks used a standalone Python parser. The parser did not import the acquisition or preservation helpers. It checked file bytes, SHA-256 values, SFNT directory bounds, table overlap, required tables, selected `head`, `maxp`, and `cmap` fields, and the recorded source relationships.

All review agents share one model family. Independence here means separate task and artifact inspection. It does not claim model-family diversity.

## Exact input identities

The task brief is [`text-unit-task-a01.md`](text-unit-task-a01.md), 4,114 bytes, SHA-256 `bcfd8c2d1b6366fcbdaafce88d8d0300b2e687c4accd46e5f2df309c57c13048`.

The font fixture directory is `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/font-fixtures-a01`.

| Artifact | Bytes | SHA-256 | Independent result |
|---|---:|---|---|
| `font-fixtures-a01/manifest.json` | 9,673 | `04916451ea952d8ada2e5ca2d1171deaa0e1e6c0acd4652cf2bba0a77c057947` | Manifest values match the files and table observations. |
| `NotoSansTelugu-Regular.ttf` | 197,228 | `2c05072e8018a9be1cb0582953d9edf9a0cf129cdfb74e611de763b09c411f7f` | Exact file and all 17 recorded table entries match. |
| `NotoSansDevanagari-Regular.ttf` | 219,212 | `385e78e6359a9d88a0f243d53b1209d7548361ba2194e2b9ec779bcaa7e8949d` | Exact file and all 17 recorded table entries match. |
| `OFL.txt` | 4,377 | `0dab92d0544f7b233403f14b84a663bdbfa746982eda629e7f4f9ffe1b036feb` | File begins with the SIL Open Font License, Version 1.1. |
| `repository-commit.json` | 11,422 | `647171c218f322957aa53c355ccf16b46e581f3d0984e57a1ec6a83aa9cde6d6` | Raw GitHub commit response matches the pinned commit. |
| `acquire_font_fixtures_a01.py` | 4,875 | `593dffb030aa945d50d4e080eafe669782c90b8f3403fc513a75885087bd440f` | Acquisition logic is bound by the font manifest. |

The pinned repository is `notofonts/noto-fonts` at commit `ffebf8c1ee449e544955a7e813c54f9b73848eac`. The preserved GitHub response reports a verified signature with reason `valid`, tree `38aaac139d3bdffb7d015ce4d3ea1d3e7216688b`, one parent, author Simon Cozens, and commit message `And we're done here.` The two font URLs and the license URL contain this exact commit. The commit is historical, not a floating `main` checkout.

The license file is copied from the pinned repository `LICENSE` path. This review records file provenance. It does not issue a separate legal opinion about distribution.

## Raw SFNT observations

Both files have scalar `0x00010000`, one TrueType face, 17 non-overlapping in-bounds tables, `unitsPerEm = 1000`, `head.indexToLocFormat = 1`, and `maxp.version = 0x00010000`. The directory parser found no duplicate tags or overlapping table ranges. The observed table set is:

`GDEF`, `GPOS`, `GSUB`, `OS/2`, `cmap`, `cvt `, `fpgm`, `gasp`, `glyf`, `head`, `hhea`, `hmtx`, `loca`, `maxp`, `name`, `post`, and `prep`.

The Telugu face has 791 glyphs. Its `GDEF`, `GPOS`, `GSUB`, `cmap`, `glyf`, `head`, `loca`, and `maxp` table identities match the manifest, including these offsets and lengths: `GDEF@284+176`, `GPOS@460+13558`, `GSUB@14020+9752`, `cmap@23868+340`, `glyf@24208+148460`, `head@172668+54`, `loca@175924+3168`, and `maxp@179092+32`.

The Devanagari face has 954 glyphs. Its corresponding key ranges are `GDEF@284+906`, `GPOS@1192+7198`, `GSUB@8392+27236`, `cmap@35724+282`, `glyf@36008+153048`, `head@189056+54`, `loca@192964+3820`, and `maxp@196784+32`.

Both `cmap` tables contain platform 0 encoding 3 and platform 3 encoding 1 format 4 records. The raw directory contains no `fvar`, `gvar`, `CFF2`, `COLR`, `CPAL`, `CBDT`, `CBLC`, `sbix`, or `SVG ` table. This supports the requested static TrueType fixture boundary. It does not prove shaping behavior.

The direct format 4 cmap observations are useful input facts, not shaped glyph results. Telugu maps `U+0C15` to glyph 23, `U+0C37` to 56, `U+0C48` to 69, and `U+200D` to 675. Devanagari maps `U+0915` to 25, `U+0925` to 41, `U+093E` to 66, `U+094D` to 81, and `U+200D` to 133. Both faces have no direct mapping for `U+1F600` or `U+0378`. The Devanagari face maps digit `U+0031` to glyph 804 but has no direct mappings for `A`, `B`, or `C`; the Telugu face also has no direct mappings for those letters.

## Preserved alpha documents

The preservation manifest is `legacy-alpha-a01/manifest.json`, 2,181 bytes, SHA-256 `db2b05ea4f80f4b5005dbd05fff62aced7c80ec3c1bc6d7684ffd97da982d288`. It records state `preserved-before-text-runtime-integration`, baseline `build-a03.json`, and the baseline SHA-256 `0e59a36134e93e947c6263f57f94f0d50edcacd54c069f0adb37192f9b552932`.

The preserved documents are byte-equal to their source files:

| Preserved document | Schema | Bytes | SHA-256 |
|---|---:|---:|---|
| `legacy-alpha-a01/plan-schema7-alpha-v2.json` | 7 | 32,539 | `a771942c48dc0e9b1832bb81bccb56fe21e074fe58546f9c49a3bc95a1ec91a2` |
| `legacy-alpha-a01/snapshot-schema1-alpha.json` | 1 | 27,938 | `22619ba0bae6681d1da67cb65b3c850ecacef31a05c2d8ab13d082eae1af9e73` |
| `legacy-alpha-a01/receipt-schema4-alpha-v2.json` | 4 | 2,364 | `ba96d0b9d262bd424b4785324c38d3609ed3d5a563fe784382e3a988a6cfd259` |

The plan and receipt identify project `native-alpha-proof-a01`. The preservation helper records 30 Rust source files and 18 existing fixture files. I rehashed all 30 source entries and all 18 fixture entries from `build-a03.json`; every recorded hash matched. The build file is 104,751 bytes with SHA-256 `0e59a36134e93e947c6263f57f94f0d50edcacd54c069f0adb37192f9b552932`.

The two preservation helper files are retained separately. `preserve_alpha_legacy_a01.py` is 2,877 bytes with SHA-256 `1cf4e3ed7015c8bf7fd2224f1cf91f71ae0b6273fd376796c9b974a548c89901`. `preserve_alpha_legacy_a02.py` is 2,742 bytes with SHA-256 `64f179e2be821e3e57e25b71880845c3cdf0a3af2e6247919b0848f1809ae4ce`. The manifest points to the A02 helper. Both helpers preserve the same three documents and refuse an existing destination.

This verifies preservation and source identity only. It does not establish that a future text plan can reuse the alpha plan, snapshot, receipt, or renderer semantics.

## Synthetic text cases

The case file is `synthetic-text-cases-a01.json`, 3,233 bytes, SHA-256 `00c9463acd151a652fa72df961961905aed11d18d2d839f2ec68410a3fa72a99`. It has schema 1, `normalization: "none"`, `direction: "ltr"`, 14 cases, and `nativeShapingRun: false`. Runtime implementation, watched, heard, and creative acceptance are all false.

The cases use nine Telugu inputs and five Devanagari inputs. Sizes are 48, 64, 512, and 48.25 pixels. They include conjuncts, marks, preserved surrounding spaces, a combining-only string, a zero-width joiner, whitespace-only text, an emoji, an unassigned scalar, and an ASCII control.

The following hashes are independently derived from each case's exact JSON string value encoded as UTF-8. `UTF16` is the count of UTF-16 code units, before any shaping or normalization.

| Case | UTF-8 bytes | UTF-8 SHA-256 | UTF-16 units | Expected class |
|---|---:|---|---:|---|
| `te-basic` | 25 | `0c72f9464218f2cdf16cb72c3f03291da539734333e6c5b45b77954f61830122` | 9 | bound face, shaping, nonempty coverage |
| `te-conjuncts-marks` | 42 | `d31f28bd109f581a91534ad3c1e80e5d314af8de748b8a3d1b0cfe73f768e36d` | 16 | bound face, shaping, nonempty coverage |
| `hi-conjuncts-marks` | 56 | `6e2a5610969b8554c5a70ebd49932cdc95a451c74602ddf788a6542185291eff` | 20 | bound face, shaping, nonempty coverage |
| `te-whitespace` | 22 | `46cc72e1d00925b510f55f1bd04556657c33df900719aa652744c5e53fdd7909` | 10 | exact spaces and bound shaping |
| `hi-whitespace` | 13 | `1af925bf5f97882308675e2081ecab4ed851d7874f95398ad0a3719da8b7a1bb` | 7 | exact spaces and bound shaping |
| `ascii-control` | 7 | `180e6e6264cdc393ea3a12f0c655c2fccd407a13103000a38dddcdd0a6ba7391` | 7 | simple shaping or explicit rejection |
| `te-combining-only` | 3 | `c330d13284b96933e4586c54633fdaf20086a6caeec15b8bad0150322d26a39c` | 1 | cluster observation without scalar/glyph assumption |
| `te-joiner` | 12 | `aa8f61004820676393584f5d581abcd23d5be194e93c9506760e560c6b6e8ff9` | 4 | joiner coverage and bound face |
| `te-large-marks` | 12 | `78049969e3c4ee4c97972d88e5ff4cb5d834791502e4c62c64bc6ca17e39f254` | 4 | bound face and unclipped coverage |
| `hi-large-marks` | 12 | `a299ed12e4de4c9bd68783116700d9d39b87f19971ed72701d1a83fe220a8974` | 4 | bound face and unclipped coverage |
| `te-fractional-size` | 6 | `cf7abb7f6f1e5640ded7fe720c570161d399faf977204bcee469bed01b23b0bf` | 2 | finite quantized geometry and shaping |
| `whitespace-only` | 3 | `0aad7da77d2ed59c396c99a74e49f3a4524dcdbcb5163251b1433d640247aeb4` | 3 | zero coverage with exact input |
| `missing-emoji` | 23 | `6614c3bf59b6e0f6ade4c45f2573f807c2d10cea408ac84293f18f7d2609ef2d` | 9 | explicit mismatch or missing-glyph rejection |
| `missing-unassigned` | 12 | `b7c052dde441688272712595be631080b4b744b7fd1ebf290487481b937b1805` | 5 | explicit mismatch or missing-glyph rejection |

The JSON has no per-case UTF-8 hash, UTF-16 coverage range, expected glyph count, expected glyph IDs, or expected raster hash. Those values must be derived and bound by a later shaping probe. The file's qualitative `expected` labels cannot serve as pass criteria by themselves.

## Findings and limits

**P1 findings: none.** Every acquired file, pinned source relationship, preserved alpha document, build-bound source entry, and case-file hash checked in this review matched its recorded identity.

**P2-1 — synthetic cases do not carry machine-checkable byte and coverage expectations.** The cases preserve literal UTF-8 strings and the task requires UTF-16 coverage, but the case file stores neither derived hash nor coverage range. A later probe must bind raw UTF-8 bytes, UTF-16 unit ranges, language, direction, and the exact face before treating shaping observations as evidence.

**P2-2 — fallback behavior is underspecified for mixed supported and unsupported scalars.** `ascii-control` uses Devanagari with `ABC 123`; the face maps the digits but not `A`, `B`, or `C`. `missing-emoji` includes `U+1F600`, and `missing-unassigned` includes `U+0378`; neither face maps those scalars. The expected labels allow either observation or rejection. The acceptance rule must explicitly reject silent fallback and record whether the complete run is rejected, emits `.notdef`, or remains a bounded run with an explicit missing-glyph result.

**P2-3 — raw SFNT checks stop at container and selected face facts.** The acquisition helper validates scalar, table bounds, overlaps, required tags, and forbidden variable/color tags. It does not parse GSUB or GPOS semantics, validate glyph outlines against `loca`, or establish CoreText face identity. The table directory and full file hash are suitable pre-shaping identity inputs. They are not shaping or raster proof.

The preserved alpha records and pre-text film records do not prove text support. `film-meta-before-text-design-a01.json` is 59,211 bytes with SHA-256 `2b72985dcc13dfd1f9f4a949616b70b1a6a1c8eef2f9f62bc79b7561cd4b5232`; it records the native editor and prior diagnostic state with no text runtime claim. `goal-status-before-text-design-a01.json` is 58,675 bytes with SHA-256 `7b4d080b5e287228cb1354f39546dbb5e4736f08a6538c9ac4ea4e835e4e5620`; it records text as remaining capability work and keeps watched, heard, and creative acceptance false.

No shaping, raster, compilation, output, playback, or human acceptance claim is made by this review. The next phase must add those observations without changing these frozen input bytes.
