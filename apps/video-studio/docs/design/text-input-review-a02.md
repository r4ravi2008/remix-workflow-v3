# Native text input review A02

## Disposition

A02 closes the two input-contract gaps recorded in [`text-input-review-a01.md`](text-input-review-a01.md). Every case now carries independently reproducible UTF-8, UTF-16BE, coverage-range, and Q16 size expectations. Whole-item rejection is required for the three mixed or unsupported inputs.

The raw SFNT limitation remains open by design. The new declaration explicitly says that nominal cmap data is not shaping proof. A later native feasibility gate must still prove CoreText shaping, run-face identity, glyph observations, and raster behavior.

No native call, build, runtime edit, output edit, state edit, GPU operation, or Resolve operation was performed. The A01 inputs and review remain unchanged.

## Exact successor bindings

The successor helper is `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/declare_text_cases_a02.py`, 3,619 bytes, SHA-256 `d9d331e9c2c823713e11b7159b48d77540a54849c6ffe2ef2f1a7cdfe60b04d9`.

The successor case file is `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/synthetic-text-cases-a02.json`, 14,706 bytes, SHA-256 `a461e07c803793baa688b18452287ca73f3ba0e6d0f8c172458a0158e4ab513d`.

The successor records its A01 predecessor as `synthetic-text-cases-a01.json`, 3,233 bytes, SHA-256 `00c9463acd151a652fa72df961961905aed11d18d2d839f2ec68410a3fa72a99`. The A01 review remains 12,066 bytes with SHA-256 `2f0f514da259e8f137a148d35fb3d64348fd41b9f7b44c1434ac4d98f7806429`.

The successor has schema 1, `normalization: "none"`, `direction: "ltr"`, state `source-expectations-bound-before-native-probe`, 15 cases, `nativeShapingRun: false`, and `runtimeImplemented: false`. Its guard policy sets `wholeItemFallbackRejected: true` and `nominalCmapIsNotShapingProof: true`.

## Independent recheck

I parsed A02 as a separate JSON input. I did not import or execute its declaration helper. For each case, I independently encoded the exact string as UTF-8 and UTF-16BE, counted bytes and UTF-16 code units, computed both SHA-256 values, checked the zero-based full `lineRange`, and recomputed `fontSizeQ16`.

All 15 `sourceExpectation` objects match those independent values. All 15 ranges start at zero and cover the complete UTF-16BE unit count. All sizes are within the declared 1-to-512 pixel boundary. The four distinct sizes produce the expected Q16 values: 48 → 3,145,728; 64 → 4,194,304; 512 → 33,554,432; and 48.25 → 3,162,112.

The 14 existing cases retain their exact A01 `id`, font, language, text, and `fontSizePixels` fields. The two font files remain exact manifest matches:

| Font | Bytes | SHA-256 |
|---|---:|---|
| `NotoSansTelugu-Regular.ttf` | 197,228 | `2c05072e8018a9be1cb0582953d9edf9a0cf129cdfb74e611de763b09c411f7f` |
| `NotoSansDevanagari-Regular.ttf` | 219,212 | `385e78e6359a9d88a0f243d53b1209d7548361ba2194e2b9ec779bcaa7e8949d` |

The unchanged font manifest is 9,673 bytes with SHA-256 `04916451ea952d8ada2e5ca2d1171deaa0e1e6c0acd4652cf2bba0a77c057947`. The unchanged OFL file is 4,377 bytes with SHA-256 `0dab92d0544f7b233403f14b84a663bdbfa746982eda629e7f4f9ffe1b036feb`. The unchanged pinned repository response is 11,422 bytes with SHA-256 `647171c218f322957aa53c355ccf16b46e581f3d0984e57a1ec6a83aa9cde6d6`, and its commit is `ffebf8c1ee449e544955a7e813c54f9b73848eac`.

## Per-case expectations

The hashes below are independently derived from the exact `text` value in A02. `UTF16BE` is the count and SHA-256 of the complete UTF-16BE encoding. `Range` is the declared `{start: 0, length: UTF16BE}`. `Q16` is the declared integer size.

| Case | UTF-8 bytes / SHA-256 | UTF-16BE units / SHA-256 | Range | Pixels / Q16 | Evaluation |
|---|---|---|---|---|---|
| `te-basic` | 25 / `0c72f9464218f2cdf16cb72c3f03291da539734333e6c5b45b77954f61830122` | 9 / `dd459ddc9722d21106e3078f71e6502bd483a0eed18cf9cf5cc1293ba5850835` | 0..9 | 48 / 3145728 | accepted shape, positive coverage |
| `te-conjuncts-marks` | 42 / `d31f28bd109f581a91534ad3c1e80e5d314af8de748b8a3d1b0cfe73f768e36d` | 16 / `15d1aaee783e20e0801143e5aaeef168adf79f5c518cc762f0d5c5503c055720` | 0..16 | 64 / 4194304 | accepted shape, positive coverage |
| `hi-conjuncts-marks` | 56 / `6e2a5610969b8554c5a70ebd49932cdc95a451c74602ddf788a6542185291eff` | 20 / `ae2a189b373a75cc4f6863552808176a6523b451fb285ac0842f3ec738f93aab` | 0..20 | 64 / 4194304 | accepted shape, positive coverage |
| `te-whitespace` | 22 / `46cc72e1d00925b510f55f1bd04556657c33df900719aa652744c5e53fdd7909` | 10 / `f808ee1859f544babcc893e56d93f3e65d7a61998e0c92dc46036f71821ff474` | 0..10 | 48 / 3145728 | accepted shape, positive coverage |
| `hi-whitespace` | 13 / `1af925bf5f97882308675e2081ecab4ed851d7874f95398ad0a3719da8b7a1bb` | 7 / `cd57337524704fa5b8c9829e282fe4012f54f962b16cb3b02fa79b01997ef92c` | 0..7 | 48 / 3145728 | accepted shape, positive coverage |
| `ascii-control` | 7 / `180e6e6264cdc393ea3a12f0c655c2fccd407a13103000a38dddcdd0a6ba7391` | 7 / `dd456e62a48adf38ccefb1a57032d336974dff82e743f3553d1826135514fad4` | 0..7 | 48 / 3145728 | whole-item rejection |
| `te-combining-only` | 3 / `c330d13284b96933e4586c54633fdaf20086a6caeec15b8bad0150322d26a39c` | 1 / `b107df03bf38e1309fe2f094ddb2032f7bba9df09870b0cebe0dd9757df159fe` | 0..1 | 48 / 3145728 | observation only, unqualified |
| `te-joiner` | 12 / `aa8f61004820676393584f5d581abcd23d5be194e93c9506760e560c6b6e8ff9` | 4 / `2bc9bef3ca2ac0b9df610dae7dc7259d47819a978a0865ff8a59baf50fea962d` | 0..4 | 48 / 3145728 | observation only, unqualified |
| `te-large-marks` | 12 / `78049969e3c4ee4c97972d88e5ff4cb5d834791502e4c62c64bc6ca17e39f254` | 4 / `870c8ae8e7e070e883ae69b00013a330c8faa2508c6dd1874377b7e6c9845a56` | 0..4 | 512 / 33554432 | accepted shape, positive coverage |
| `hi-large-marks` | 12 / `a299ed12e4de4c9bd68783116700d9d39b87f19971ed72701d1a83fe220a8974` | 4 / `25b0a879acefa6eb1f81860fff678d02ac96bbf121650f272656ab05d5d740bf` | 0..4 | 512 / 33554432 | accepted shape, positive coverage |
| `te-fractional-size` | 6 / `cf7abb7f6f1e5640ded7fe720c570161d399faf977204bcee469bed01b23b0bf` | 2 / `16508ba4210170af5a1af0d4f864a95a0999b0749be820dde71c6263c9b385fd` | 0..2 | 48.25 / 3162112 | accepted shape, positive coverage |
| `whitespace-only` | 3 / `0aad7da77d2ed59c396c99a74e49f3a4524dcdbcb5163251b1433d640247aeb4` | 3 / `5ee9a0f88eac027771474abbbbb90d51533a64e1edbd9125fa325b07d6f62d2b` | 0..3 | 48 / 3145728 | accepted shape, exactly zero coverage |
| `missing-emoji` | 23 / `6614c3bf59b6e0f6ade4c45f2573f807c2d10cea408ac84293f18f7d2609ef2d` | 9 / `a62fbd9acce779d97d5f1064acbeb131ca317646f93abbf54ca08387ab7a2cb8` | 0..9 | 48 / 3145728 | whole-item rejection |
| `missing-unassigned` | 12 / `b7c052dde441688272712595be631080b4b744b7fd1ebf290487481b937b1805` | 5 / `2b98aadfb61f87c4a5cac255d7c5975ecc6921093b2f1e3543bf8b1da42a39b7` | 0..5 | 48 / 3145728 | whole-item rejection |
| `ascii-digits-positive` | 3 / `a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3` | 3 / `1eb338dc93953145b05ede84b8bf8c859ac38b21936718dc4e4e2a7b59749bec` | 0..3 | 48 / 3145728 | accepted shape, positive coverage |

The resulting classes are 10 accepted-shape cases, 3 explicit rejection cases, and 2 observation-only cases. The rejected cases allow only `text_font_fallback` or `text_missing_glyph`, publish no raster, and reject silent fallback or accepted whole-item output. The combining-only and zero-width-joiner cases remain deliberately unqualified.

## Closed and open findings

**Closed P2-1 from A01.** A02 stores machine-checkable UTF-8 byte counts and hashes, UTF-16BE unit counts and hashes, full ranges, normalization, direction, and Q16 sizes for every case. The independent recheck found zero mismatches.

**Closed P2-2 from A01.** `ascii-control`, `missing-emoji`, and `missing-unassigned` now require whole-item rejection before raster publication. The new `ascii-digits-positive` case supplies a positive control for supported Devanagari digits. This closes the prior ambiguity about silently accepting a mixed or missing-glyph run.

**Open P2-3.** The declaration correctly preserves the raw SFNT boundary and states that cmap is not shaping proof. No glyph sequence, cluster, run-face, CoreText, raster, or pixel evidence exists yet. The next native feasibility gate must establish those observations using the exact font bytes and A02 source expectations.

P1 findings: none. No runtime, build, native, playback, watched, heard, or creative acceptance claim is made.

