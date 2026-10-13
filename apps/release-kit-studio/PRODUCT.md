# Native editor product

<!-- impeccable:product-schema 1 -->

The product is an agent-first standalone media editor.
It uses DaVinci Resolve feature behavior as its reference for general media projects.
Rust owns the editor library and the direct agent CLI.
Release Kit is one optional workflow built on that editor.

The normative contract lives in [native `SPEC.md`](native-editor/docs/SPEC.md).
The feature catalog lives in [native `FEATURES.md`](native-editor/docs/FEATURES.md).
This page records scope and ownership.

## Product contract

The editor supports independent projects, source media, timelines, and output requests.
Agents discover capabilities, inspect schemas, submit typed commands, inspect results, and verify artifacts.
The editor runs locally without a browser, Cloudflare credentials, or an optional UI.

Resolve is the behavior reference.
Resolve is not a runtime dependency of the native editor.
The native editor does not call Resolve and does not use a Resolve worker.

The initial capability mapping covers Media, Cut, Edit, Fusion, Color, Fairlight, Photo, Deliver, collaboration, AI, and extension interfaces.
The 81-family mapping is an initial scope map.
It does not claim a complete inventory of Resolve menu items or parameters.
Each mapped family needs a behavior contract, an implementation, and current acceptance evidence.

## Authority and ownership

| Owner | Responsibility |
| --- | --- |
| `editor-core` | Typed editing semantics, local SQLite state, immutable revisions, native processing, receipts, and artifact integrity |
| `editor-cli` | Direct process arguments, JSON framing, schemas, deadlines, discovery, command dispatch, and exit codes |
| `editor-devcheck` | Development-only architecture checks, source policy, bounded subprocesses, and evidence reports |
| Optional applications | UI, Effect orchestration, remote adapters, authentication, and hosted deployment |

Rust types define the native protocol.
Generated JSON schemas expose the same transport shapes.
An optional application adapter consumes those schemas and does not create a second timeline reducer.

Project revisions are immutable.
Mutations carry an expected revision and a project-scoped intent identifier.
An identical intent replays its original result.
The same intent with changed content returns an intent conflict.
Artifact receipts bind the project revision, command intent, renderer version, output hash, and measured properties.

## Current native status

The capability ledger has 81 initial families.
Eight `CORE` families are implemented.
Seventy-three families are planned.
Zero families are promoted to `verified`.

The current P0 implementation provides local project revisions and stable intents.
It also provides one non-overlapping solid RGBA visual track, CPU PNG frames, and artifact verification.
The six compiled runtime tools are `engine.capabilities`, `project.create`, `project.inspect`, `project.commit`, `frame.render`, and `artifact.verify`.

Native movie ingest, native movie codecs, audio, and Indic text shaping remain planned.
Color management, layered composition, GPU execution, and the full Release Kit profile remain planned.
The current P0 implementation does not use FFmpeg executables, libav dependencies, Python renderer fallbacks, or hidden fallback paths.

The state names have separate meanings:

- `planned` means that the ledger maps the family but no compiled implementation exists.
- `implemented` means that the compiled registry exposes the family.
- `verified` means that current acceptance evidence matches the implementation, protocol, schema, and feature contract.

An edited ledger, a document, or an old receipt cannot promote a Rust capability.

## Optional Release Kit profile

The optional profile accepts canonical audio, native-script lyrics, and an artist profile.
It combines cinematic scenes, lyric-led passages, and music-reactive environments in one release workflow.
The profile does not define the general editor API or the native timeline model.

| Output ID | Target |
| --- | --- |
| `film` | 1,920 × 1,080 at 24 fps, full canonical song, stereo MP4 |
| `short-1`, `short-2`, `short-3` | 1,080 × 1,920, up to 30 seconds each |
| `thumbnail` | 1,920 × 1,080 JPEG |
| `artwork` | 1,920 × 1,920 JPEG |

The profile binds the exact master hash and measured song duration.
Each vertical output binds declared source intervals and the exact song hash.
The still outputs bind accepted visual direction and source references.
The profile uses H.264 video and AAC audio when its selected encoder supports them.
The platform-specific native encoder remains unresolved.

The workflow preserves lyrics in the submitted native script.
Transliteration does not satisfy the workflow input rule.
The profile requires source checks, output measurements, full playback, listening, and creative review before user acceptance.
No completed native six-output release is established.

## Optional applications

The root TypeScript application under `src/` owns the optional Foldkit UI and Effect workflow state.
The `editor/` directory contains optional TypeScript and Cloudflare editor adapters.
The `agent/` directory contains the optional Release Kit production agent.
The `worker/` directory contains the optional Tailscale and local Resolve pilot helpers.

These applications can coordinate workflow services later.
They do not own native timeline semantics or direct access to the native SQLite store.
Their receipts prove only the implementation that produced each receipt.

Use the [native editor specification](native-editor/docs/SPEC.md) for native behavior.
Use the [Release Kit agent runbook](agent/README.md) and [Resolve pilot runbook](worker/README.md) for optional workflow operations.
