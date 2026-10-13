# Release Kit Editor specification

This document describes the Cloudflare editor. The standalone Rust editor is a separate application.

Version 1. Decision date: 2026-10-03.

## Product and deployment boundary

An artist uploads a finished song, exact native-script lyrics and an artist
profile. The hosted app must produce a cinematic, lyric-led, music-reactive release kit. The agent edits through a typed CLI/API instead of desktop application control. The editor is its own Cloudflare Worker. The editor can deploy independently of the Foldkit frontend. 

Effect owns validation and domain operations. Alchemy declares the infrastructure.

The Worker owns tenant authorization, immutable project revisions, edit tools,
render intents, progress and evidence. R2 owns private source and output bytes.
D1 owns indexes and atomic state transitions. Cloudflare Containers execute the native renderer and media-analysis engine behind the Worker. Containers are
Cloudflare compute, not the Tailscale workstation.

The GPU service is a separate provider abstraction for footage generation or inference.
Tailscale implements one transport for that abstraction.

Resolve remains an optional future interchange/backend integration. Its desktop
SDK, Linux installation, activated license and display are not prerequisites for
this service. current Resolve projects and diagnostic exports remain intact.

## What we learned from Resolve

These are workflow responsibilities. They do not promise every Resolve button, proprietary algorithm, plugin, or desktop interaction.

| Resolve area | Responsibility | Release Kit Editor requirement |
|---|---|---|
| Media | Ingest, organize, inspect, conform and relink assets | Content-addressed media, codec/stream probe, proxies, source identity, reproducible relinking |
| Cut / Edit | Build and revise time-based sequences | Frame-based placement, source trims, splits, replacements, tracks, transitions, transforms, separate aspect-ratio compositions |
| Fusion | Composite images, masks, graphics and animation | Layers, native-script lyric/title overlays, environment masks, keyframes, glow/blur and music envelopes with protected subjects |
| Color | Establish and match a visual treatment | Explicit SDR color contract, exposure/contrast/saturation, per-shot correction, reproducible LUT provenance and clipping checks |
| Fairlight | Prepare, route, meter and deliver sound | Preserve the selected master, exact source ranges for promos, waveform/bass analysis, loudness/peak checks, sync and channel verification |
| Photo / artwork | Produce still images | Separately composed landscape thumbnail and square cover, title-safe areas, legibility and identity review |
| Deliver | Render and package versions | Deterministic presets, asynchronous jobs, cancellation/reconciliation, complete decode, checksums, private downloads and manifests |
| Collaboration / project management | Maintain versions and ownership | Tenant isolation, optimistic revisions, immutable history, replayable edits, fenced attempts and artifact-bound review |

Primary references, checked 2026-10-03: [Resolve overview](https://www.blackmagicdesign.com/products/davinciresolve),
[Edit](https://www.blackmagicdesign.com/products/davinciresolve/edit),
[Fusion](https://www.blackmagicdesign.com/products/davinciresolve/fusion),
[Color](https://www.blackmagicdesign.com/products/davinciresolve/color),
[Fairlight](https://www.blackmagicdesign.com/products/davinciresolve/fairlight),
[Media and delivery](https://www.blackmagicdesign.com/products/davinciresolve/media).

Platform references: [Worker limits](https://developers.cloudflare.com/workers/platform/limits/),
[Containers](https://developers.cloudflare.com/containers/),
[Container lifecycle API](https://developers.cloudflare.com/containers/api/durable-object-container/),
[instance sizes](https://developers.cloudflare.com/containers/platform/limits/).
Our architectural conclusion is to keep native codecs outside the Worker isolate.

## Required deliverables

The release-kit-v1 contract has exactly six outputs with independent identifiers:

- `film`: 1920×1080, 24 fps, H.264 MP4 with stereo audio. The film covers the entire selected master.
- `short-1`, `short-2`, `short-3`: 1080×1920, 24 fps, H.264 MP4 with stereo audio. Each short is no longer than 30 seconds. Each short has an explicit independent composition and source interval.
- `thumbnail`: 1920×1080 JPEG with a dedicated composition.
- `artwork`: 1920×1920 JPEG with a dedicated composition.

For Pal Pal the canonical WAV is 239.68 seconds and SHA-256
`a5fa914e8f7cae9c76f7ec309ce3a60194d138baa3d2684477f361feeea5c8b3`.
The frozen artist brief fingerprint is
`b34008acaeee416d24a98d8b38de3ef8635d5aa9474ee32e682fb8389ceffd75`.
A four-second diagnostic is not a completed film or kit. A promoted render must
bind the exact source, artist brief, project revision, renderer version and preset.

## Project model

The document has a versioned schema and stable identifiers. Time uses integer frames at the declared project rate. Source audio ranges also carry source seconds to prevent silent changes from time conversion. Assets carry SHA-256, byte length, kind and
measured media properties. Remote filesystem paths and arbitrary URLs are not
project media identifiers. The service resolves only tenant-owned R2 objects.

Each output has its own timeline, canvas, audio range and composition rationale.
Clips refer to source assets and explicit source trims. There is no implicit loop
or last-frame hold to fill missing footage. Layers have an explicit order.
Transforms, color settings, title styles and masks belong to the project revision.
Lyrics retain their exact native characters and timing.

Telugu, Hindi, and Tamil must use fonts and a renderer with text shaping support. Missing fonts are errors.

The renderer applies reactive effects to environment layers or a verified environment mask.
The renderer protects people, lyrics, titles, and story-critical props. An envelope is measured data bound to the canonical audio.
An envelope does not certify that anyone heard the song or accepted the beat map. Tracking and segmentation are separate GPU tools with model and mask provenance.

## Agent tool requirements

The CLI prints JSON by default. `tools` returns supported tool names, input
schemas, feature IDs, implementation state and evidence requirements. Tools
operate on validated domain data. Unsupported features return a structured error. They never silently ignore a setting.

Callers supply tokens through private environment variables or private configuration.
Callers do not supply tokens through command arguments or project files.

| Feature | Tool family | Acceptance criterion |
|---|---|---|
| F01 | project create / commit / inspect / history | Concurrent writers cannot overwrite a newer revision. Retrying the same intent is idempotent |
| F02 | media register / upload / inspect / relink | Stored bytes match source digest. Foreign-tenant and arbitrary remote paths are rejected |
| F03 | timeline put / clip place / trim / split / remove | Frame-exact edits, valid bounds, no missing references or coverage holes |
| F04 | transform / layer / transition | Explicit portrait framing, compositing and source handles. Stable endpoint frames |
| F05 | lyrics / titles | Exact native text, timed cues, supported shaped font, no unsafe styling injection |
| F06 | color | Defined SDR output and deterministic per-shot settings. No ignored unsupported controls |
| F07 | audio inspect / envelope / conform | Correct master and range, channels, duration, sync and clipping/loudness evidence |
| F08 | environment effect / mask | Protected foreground stays unchanged. Masks and envelopes bind exact assets |
| F09 | render / status / cancel / reconcile | Persistent intent before execution. Uncertain outcomes do not duplicate work. Cancellation preserves evidence |
| F10 | verify / preview / compare / review | Independent decode, dimensions, frame count, sound-range alignment, source-bound review clips/frame samples and artifact-bound review |
| F11 | kit validate / locate / archive | Six exact outputs, immutable revision and source binding, complete ZIP CRC/hash checks and distinct review evidence |
| F12 | capabilities / progress | Feature implementation and verification are separately tracked and machine readable |

Later extensions include richer splines, optical-flow retiming, tracked masks,
subject identity comparison, scene-level grading, advanced transitions and
interchange exports. Their entries must remain planned until implementation and verification are complete. Broadcast ingest, multicam editing, RAW-camera development, surround
mixing, ADR and arbitrary OFX plugins are outside this product's initial scope.

## Verification and release gates

Validation checks the edit before compute: identifiers, references, bounds,
coverage, script, font support, six-output contract, source identity, effect masks
and executable feature support. The compiler emits a bounded native render recipe. Users cannot submit shell commands or raw filter graphs.

The verifier separately measures the actual encoded bytes: complete decode,
dimensions, rate, video/audio duration, frame count, codec, pixel format, channels,
hash and byte length. The verifier compares audio with the canonical source range.
The verifier does tests for blank or frozen frames and examines seams.

Findings include thresholds and measured
values instead of a blanket boolean. Artwork can intentionally repeat frames. A film must declare repeated frames explicitly.

Visual and sound review records bind an output SHA-256 and exact inspected range.
`measured`, `frame-inspected`, `motion-reviewed`, `heard` and `creatively-accepted`
are separate evidence kinds. A machine metric, transcript, or sample contact sheet cannot establish listening or creative acceptance.
A player that reaches its end cannot establish these reviews.
Replacement bytes invalidate earlier artifact reviews.

Kit readiness requires the
contract and technical verification. Publication and creative acceptance remain
separate user-visible states.

## Isolation, recovery and observability

Authorization derives the tenant from a valid credential or trusted service
binding. Request bodies cannot choose a tenant. Every project, asset, revision,
job and artifact lookup includes that tenant. Objects are private. The service authorizes downloads. Native engines receive only scoped asset references and bounded
recipes, with no account credentials or user-supplied commands.

Jobs have durable IDs, immutable recipe fingerprints and state transitions.
A duplicate intent with the same content returns the original result. A duplicate intent with changed content conflicts. The rendering, verifying, failed, cancelled, and uncertain job states are distinct. A crashed container's temporary files are not the project store.
1. Recover from R2 and D1.
2. Reconcile stored artifacts before you replay a render.

Progress records actual completed work and verification. There is no timer-based
fake percentage. Concurrency, duration, canvas, asset size, disk and job deadlines
are bounded. Render instances scale to zero when idle.

One shared D1 slot limits native rendering and cold verification across this
Editor deployment. Render admission rotates registered tenants with queued work. Render admission preserves FIFO order in each tenant.
Queued jobs do not start a native Container. Execution deadlines start at admission.

Cancellation must preserve another tenant's active runtime. Unknown outcomes retain capacity until reconciliation of ownership and termination is complete. Cold verification
returns explicit HTTP 503 backoff when the slot is occupied. The client retries
that response only while its production lease remains valid.

The slot is not an account spend cap. Public-cloud enforcement, tenant quotas, verification fairness, and long-render crash/deadline behavior need separate evidence. Local admission and two-tenant runtime evidence are linked in PROGRESS.md.
