# Native editor implementation sequence

The implementation follows the general DaVinci Resolve reference contract.
The phases add native behavior in bounded slices.
Release Kit is one optional workflow profile.

P0 is the current standalone Rust foundation.
Effect and UI adapters stay outside native execution.
An absent registry implementation leaves a family planned.
A compiled implementation without an acceptance receipt for the same feature is implemented.
A family becomes verified only after its acceptance cases pass for the same build.

## Phase plan

| Phase | Native or application result | Acceptance boundary |
| --- | --- | --- |
| P0 | Rust library, direct Rust CLI, local revision store, capability ledger, and development verifier | Real local commands, conflict and replay checks, exact PNG pixels, and altered-byte rejection |
| P1 | Native media ingest, metadata, codecs, and export | Decode and encode a versioned golden corpus on each supported platform without FFmpeg or libav |
| P2 | Timeline, trimming, synchronization, and audio core | Rational-rate edits, track composition, sample alignment, split edits, fades, and PCM export |
| P3 | Typography, motion, masks, graphs, and effects | Native Indic shaping, declared animation behavior, masks, composition graphs, and bounded tracking |
| P4 | Color management and still-image work | Declared color spaces, transforms, LUTs, scopes, crop, artwork, and reference-image comparisons |
| P5 | General local editor workflows and optional output profiles | General projects and timelines use declared output targets. The Release Kit profile keeps one film, three promos, one thumbnail, and one artwork file with separate review gates. |
| P6 | Separate hosted application and optional UI adapters | Hosted authorization, native execution host, tenant isolation, cancellation, recovery, and adapter evidence |
| P7 | Extended Resolve parity | Multicamera and live editing, full 3D workflows, camera solving, advanced AI operators, plugins, interchange, and hardware integration |

The phase table describes planned work.
It does not claim that a phase is complete.

## Current boundary

The source implements eight CORE families.
The other 73 families remain planned.
The current P0 renderer accepts one visual track of solid RGBA clips with no overlap and writes CPU PNG frames.
P0 does not prove movie codecs, audio, Indic typography, layers, GPU execution, hosted execution, playback, listening, or creative acceptance.

The capability ledger has 81 family IDs, 74 Rust owners, six Effect owners, and one UI owner.
These owner values describe planned implementation boundaries.
Application-owned queue, preset, and remote workflow records do not imply native counterparts.

## Coverage work

The current family catalog is an initial breakdown.
Complete parity needs a versioned Resolve reference inventory that covers individual controls, formats, effects, parameters, and interaction behavior.
Each inventory item needs a stable link to a feature contract, an implementation piece, a fixture corpus, and acceptance cases.
The inventory must also record reference-version changes and local coverage gaps.

The next coverage work must identify missing media, cut, edit, Fusion, Color, Fairlight, Photo, Deliver, collaboration, AI, and extension behavior.
The next implementation work must select one bounded local slice and its acceptance cases before code changes.
Do not add feature IDs in this documentation cleanup.

## Work unit rules

`capabilities.json` records each feature ID, owner, phase, dependency, command, and acceptance criterion.
The [feature guide](FEATURES.md) links every detailed contract.
The [workflow](WORKFLOW.md) defines scenario, implementation, and acceptance steps.

Name the feature ID and exact files before implementation.
Keep coupled protocol, storage, and CLI changes under one owner.
Give independent tasks separate state and evidence paths.
End each unit with a saved check result before the next unit starts.

## Dependency rules

Use native Rust implementations for native features.
Keep Effect, UI, hosted services, and workflow adapters in separate applications.
Do not add FFmpeg executables, libav dependencies, bindings, or hidden fallback renderers.
Reject unsupported requests before execution.

The historical Bun, Python, and Cloudflare editor remains evidence for its original workflow.
It cannot establish Rust capability or native parity.

## Evidence rules

Build success does not prove feature behavior.
Document coverage does not prove runtime behavior.
A queue, render percentage, or receipt does not replace frame inspection, playback, listening, or creative approval.
Record measured output, human review, and creative approval as separate states.
