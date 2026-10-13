# Native editor design task

Design a fresh general Rust media editor and direct agent CLI.
Do not copy the prior implementation.
Start with caller usage, then type sketches, signatures, module ownership and a short rationale.
Use architect/references/rationale-template.md and screen architect/references/design-red-flags.md.

The application must support immutable project revisions, explicit asset hashes, rational frame rates,
integer frame and sample intervals, multiple video and audio tracks, source retiming, layered composition,
masks, color transforms, motion curves, original-script typography and source-bound movie export.
The native library owns editing and media semantics.
CLI transport and process lifetime stay at the executable boundary.
Effect and tenant application orchestration remain separate.
No FFmpeg, libav, subprocess renderer or old runtime fallback is allowed.
Platform-native media frameworks are permitted through Rust-owned adapters.

The product target follows the referenced general editor contract.
The Panja acceptance case uses real song footage, source-derived anime transformations and generated narrative action.
Preserve exact source ranges, generated originals, transformations, accepted usable ranges and all lineage.
Review records are version-bound. Pending or failed perception cannot be promoted by measurements.
Persistent local-GPU jobs reconcile uncertain submissions before retries.
The native editor must be independently usable.
A Resolve-generated film cannot establish the Rust renderer's capabilities.

Explore two structurally distinct shapes.
One shape centers editing on a persistent project aggregate.
The other centers editing on a validated immutable evaluation plan compiled from project data.
Choose the assigned shape, develop its complete caller interface and explain its limits.
Keep the interface small enough that callers do not coordinate internal stages.
Plan the real movie/audio path first. A PNG-only foundation cannot prove the hybrid film.
Name the first executable experiment and independent acceptance expectations.
Do not implement runtime code or claim creative acceptance.

Grounding files are available in:
- apps/video-studio/docs/WORK.md
- artifacts/scratch-video-goal-20261005/requirements.md
- artifacts/scratch-video-goal-20261005/preserved/source-snapshot.json
- apps/release-kit-studio/native-editor/docs/SPEC.md, read-only reference
- .agents/skills/music-video-director/SKILL.md
- .agents/skills/gpu-footage-generation/SKILL.md

The parent will grade native movie/audio feasibility, source and time invariants,
interface depth, review truthfulness, recovery behavior and general editor extensibility.
