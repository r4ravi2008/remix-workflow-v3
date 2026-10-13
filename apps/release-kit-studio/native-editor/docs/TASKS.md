# Native editor implementation backlog

This backlog covers the general Rust editor.
Release Kit remains one optional workflow profile.
The backlog does not change feature IDs, owner values, phases, states, or CORE bindings.

## Current state

| Area | Current fact |
| --- | --- |
| Capability catalog | 81 families across 11 Resolve reference areas |
| Native implementation | Eight CORE families are `implemented` |
| Planned coverage | 73 families remain `planned` |
| Owners | 74 Rust, six Effect, and one UI |
| Trusted verification | No family is `verified` without a current acceptance receipt |
| P0 output | One non-overlapping solid RGBA track and CPU PNG frames |

## Next work

1. Build a versioned DaVinci Resolve reference inventory. Record controls, formats, effect parameters, interaction behavior, version changes, and source references.
2. Map every inventory item to a current feature contract or record the local coverage gap. Add feature IDs only through a versioned catalog change.
3. Define the P1 media corpus and native codec experiments. Record platform, codec, pixel format, bit depth, and decode or encode evidence without FFmpeg or libav.
4. Extend `editor-core` for the next bounded media or timeline slice. Add its command contract, fixture corpus, independent acceptance cases, and failure behavior.
5. Add sample-accurate audio and native Indic text contracts. Keep audio measurement, text shaping, frame inspection, playback, listening, and creative review separate.
6. Add color, still-image, composition, motion, and export slices by phase. Keep each slice tied to its feature IDs, owner, dependencies, and acceptance cases.
7. Define the general local output workflow before the optional Release Kit profile. Bind source media, output targets, artifact receipts, and review states separately.
8. Design hosted and UI adapters as separate applications. Prove authorization, tenant isolation, cancellation, recovery, and schema compatibility before deployment claims.

## Rules for each task

Name the feature IDs, owner crate, source files, fixture inputs, and acceptance cases before implementation.
Keep `planned`, `implemented`, and `verified` distinct.
Save a check result before the next unit.
Keep historical application receipts separate from native Rust evidence.
