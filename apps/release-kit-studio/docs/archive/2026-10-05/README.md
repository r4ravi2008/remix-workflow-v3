# Release Kit Studio

Foldkit 0.165 and Effect 4 frontend, packaged for Cloudflare Workers with Alchemy 2.

```sh
bun install
bun run dev
bun run check
bun run build
```

The implementation supports audio inspection and playback, native-script lyrics, device drafts, and invitation sign-in. It also supports studio artist profiles, private source uploads, durable production jobs, and exact release readback. The selected file uploads only when production is requested.

Queued releases preserve their submitted audio metadata, lyrics and artist direction. The preview artwork is illustrative.

The service stores artist identity per tenant with revision checks. A save conflict preserves the unsaved fields until an explicit reload. Device drafts contain metadata and lyrics, with audio reselected after a draft reopens. Actual files and preview URLs are not persisted in drafts.

Before a production plan exists, the worker automatically prepares a private director input from the verified source and frozen brief. It decodes WAV/MP3 audio into measured response curves and preserves the native lyric lines. It records the six required deliverables and pending review gates. Both Pal Pal submissions completed this preparation without another claim. The model-backed director, heard song map, storyboard and accepted pilot remain pending.

See `docs/direction-handoff-receipt.json`.

## Standalone Rust editor foundation

The native editor uses Rust for its library and direct agent CLI. Effect and optional UI adapters belong in separate applications. Start at [the native editor agent map](native-editor/AGENTS.md). The [native specification](native-editor/docs/SPEC.md) preserves the release-kit contract.

The [capability ledger](native-editor/capabilities.json) tracks planned, implemented, and verified work separately. The [development workflow](native-editor/docs/WORKFLOW.md) supports the installed `poteto-mode` skills.

The native CLI has an independent Rust process path. Its bounded P0 implementation renders solid RGBA PNG previews. Use [the local Rust CLI exercise](native-editor/docs/CLI-EXAMPLES.md) for tests of project edits, retries, and artifact verification. The [scenario-first feature guide](native-editor/docs/FEATURES.md) expands all 81 mapped families.

Most remain planned. Native movie codecs, audio, Indic typography, complete release kits, and hosted deployment remain later phases.

## Historical standalone editor

The earlier Bun, SQLite, and Python standalone renderer depends on FFmpeg.
Its [historical local CLI guide](agent/LOCAL_CLI.md) and receipts document that implementation.
Those receipts do not verify the Rust editor. Use the separate native binary and its current acceptance evidence.

The local and Cloudflare adapters share project validation, immutable revisions,
render coordination, output verification, preview contracts, and the CLI.
Local measurements do not establish cloud production or creative acceptance.

## Cloudflare editor

The replacement editor is its own Worker, `release-kit-editor-preview`, with a
Cloudflare Container for native rendering and verification. The Foldkit Worker
forwards `/api/editor/*` through a service binding. Tailscale belongs to the GPU
provider abstraction. The editor has no workstation or Resolve dependency.

Read the [specification](docs/editor/SPEC.md),
[implementation plan](docs/editor/IMPLEMENTATION.md),
[architecture decision](docs/editor/ARCHITECTURE.md) and
[progress tracker](docs/editor/PROGRESS.md). The machine-readable feature ledger
is `editor/feature-ledger.json`. Advanced compositing and full Pal Pal production
remain incomplete. The schema-v2 production adapter targets the Cloudflare editor.

```sh
bun run editor -- tools
bun run editor -- schema project
bun run editor -- schema edits
bun run editor -- schema production-plan
bun run editor -- validate project.json kit
bun run editor -- edit project.json edits.json
bun run editor -- progress
```

Remote commands require `EDITOR_URL` and a tenant-scoped `EDITOR_TOKEN` from
private configuration. Operator-only `/v1/operator/tokens` issues seven-day
credentials for a tenant that already exists. `/v1/operator/tokens/revoke` revokes them.
Browser calls use the studio session through the same-origin service binding.

```sh
bun run editor -- health
bun run editor -- upload asset.json source.mp4
bun run editor -- call project.commit commit.json
bun run editor -- call project.edit edit-request.json
bun run editor -- call render.start render-request.json
bun run editor -- call render.status job.json
bun run editor -- call render.cancel job.json
bun run editor -- call render.reconcile job.json
bun run editor -- call artifact.verify artifact.json
bun run editor -- preview preview.json review-directory
bun run editor -- download JOB_ID film output.mp4
bun run editor -- archive JOB_ID release-kit.zip
```

Tool schemas use JSON Schema 2020-12. The server additionally enforces source
identity, native script, media coverage, frame bounds and supported controls. The real CLI passed a fresh ten-second tail preview from a 5,753-frame
synthetic film. The last frame, stereo range, hashes and complete decode passed.

See the [local runtime proof](docs/editor/review-preview-long-runtime-receipt.json). Commit requests carry `projectId`, `expectedRevision`, `intentId` and `project`. Render requests carry `projectId`, `revision`, `intentId`, `mode` and `outputId`:
`diagnostic` selects one output. `kit` requires exactly six.

Reuse a stable intent
to reconcile a lost response. Changed content needs a new intent. Unknown
outcomes retain a release fence until reconciled or explicitly cancelled. Cancellation terminates the owned container while verified R2 artifacts and
receipts are retained.

Downloads refuse to overwrite files that already exist.

Local verification passed 129 app tests and 48 Python checks, plus a six-format native canary. It also passed 11 engine HTTP
checks and 18 Workerd/D1/R2/container checks. See `docs/editor/*receipt.json`.
These synthetic technical tests do not complete Pal Pal or certify normal-speed
playback, listening or creative acceptance. Public-cloud deployment remains pending.

`artifact.verify` returns frame diagnostics with thresholds, measured ranges and
planned-join deltas. Explicit image holds and fades remain separate from unwanted
freezes and blanks. Every encoded frame contributes a 32-by-18 RGB-derived
grayscale measurement.

Findings survive the downloadable kit manifest and retain
`semanticReviewed: false`. These reduced measurements cannot certify text
legibility or creative quality. See the [diagnostic receipt](docs/editor/frame-diagnostics-runtime-receipt.json).

`artifact.preview` produces a private review clip and full-resolution frame
samples from the exact completed output. Video requests select at most 240 frames
(ten seconds at 24 fps) and eight sample frames. A still request selects frame zero
with `frames: 1`.

The `preview` CLI verifies source binding and downloaded hashes. It creates a new directory and refuses destinations that already exist. Cached requests
reuse identical derivatives without native compute.

Preview generation preserves
separate motion, sound and creative review states. See the
[local preview receipt](docs/editor/review-preview-runtime-receipt.json) and
[Studio session receipt](docs/editor/review-preview-session-runtime-receipt.json).

The schema-v2 adapter also completed a local six-output production canary. All outputs entered review. Full and ranged private downloads matched the stored
hashes, and all downloaded files decoded completely. Final verification resumed
the stored kit without another render.

See
[production receipt](docs/editor/production-runtime-receipt.json).

The schema-v3 generated-media recipe also completed six synthetic outputs.
It measured collected footage before immutable commit and passed fifteen local
checks. The checks included independent verification, private downloads, and complete
decode. This canary submitted no GPU inference. See the
[generated-media receipt](docs/editor/generated-production-runtime-receipt.json).

The release archive contains six deliverables, `project.json` and `manifest.json`. The separate Editor Worker streams a ZIP64 archive from private R2 storage. Every entry must match its verified byte count and SHA-256 before completion. The CLI independently checks ZIP CRCs, entry hashes, and manifest bindings with
Python's standard library.

Failed downloads remove only their new partial file. The Foldkit download appears for a complete verified Editor kit in review. The editable project references original private media. Source files are not
embedded.

Packaging does not establish motion review, listening, or acceptance. The native synthetic archive and browser download passed local verification. See [archive evidence](docs/editor/archive-runtime-receipt.json).

## Native development and legacy pilot

```sh
bun alchemy dev --stage local-worker --profile release-kit-studio --no-input
```

The native Alchemy stack serves the studio at [localhost:1337](http://localhost:1337/)
and the separate editor at [localhost:1339](http://localhost:1339/v1/health). The Mac launchd worker polls the studio API with the updated adapter. It
uses the GPU abstraction for footage and the separate Cloudflare editor for
post-production. Schema-v1 Resolve plans cannot resume production.

Schema-v2 plans
bind a source-checked project and explicit canonical-audio, shot or file inputs. Schema-v3 plans bind a recipe and measure newly collected footage after generation. The production route derives tenant and release from the device's exact live
job lease. Six verified R2 outputs enter review in one transaction, with no
download/reupload step.

The live service now prepares direction-v2 packets for
both held Pal Pal jobs. Hosted configuration remains pending deployment. The
browser-created Pal Pal attempt has not been resumed or promoted.

The actual Pal Pal browser upload reached the service with its exact 239.68-second WAV and Telugu lyrics. It entered a durable direction hold on attempt 1. See `docs/browser-worker-receipt.json` and `docs/artist-profile-receipt.json`.

There are no completed release outputs yet. A trusted production plan and perceptually reviewed pilot are still required before full generation.

The native checks can be run against an already configured local stack:

```sh
python3 agent/check-artist.py
python3 agent/check-browser-release.py 92a6e687-e9ec-4325-a767-f44a56c73d84
```

These checks preserve production work. Before independent upload/storage smoke tests or the one-job CLI, stop the owned supervisor. This prevents two consumers from a claim on the same test queue. See `docs/production-architecture.md` for ownership and recovery.

## Source-bound audio and lyric tools

Model observations use the Effect GPU abstraction and its reserved
Herdr/Tailscale transport. Each operation binds the frozen job, brief, exact
source hash, measured duration and requested range. Terminal replay reads the
same receipt without another inference. Unknown outcomes retain their fence.

```sh
bun run observe schema
bun run observe .local/workstation.json OBSERVATION_JSON
python3 agent/lyric-candidates.py DIRECTION_INPUT SPEECH_RECEIPT NEW_PROPOSALS_JSON
python3 agent/lyric-audit.py DIRECTION_INPUT PROPOSALS_JSON WHISPER_ALIGNMENT_JSON CTC_ALIGNMENT_JSON NEW_AUDIT_JSON
```

These are trusted operator commands. Machine configuration stays private. `audio-window` observes at most 30 seconds. `speech` processes the whole source.

`lyric-alignment` selects exact canonical `lineIndices`. Repeated lines keep
distinct chronological indices. Missing word observations retain null timings. Neither recognition nor alignment replaces the submitted native lyrics.

Whisper alignment defaults to CUDA. Its explicitly selected CPU mode uses four
threads and a separate owned alignment lease. The pinned Telugu CTC backend
requires `alignmentBackend: "indic-conformer-ctc"` and
`alignmentDevice: "cpu"`. It uses native vocabulary pieces without transliteration.

CTC timestamps describe token emissions. Exact word onsets and sung dwell remain
unverified. CPU execution never silently substitutes for requested CUDA execution.

The independent audit detects crop-edge ambiguity, spelling uncertainty, missing
observations, and timing disagreement. Agreement alone cannot certify listening,
lyric timing or creative acceptance. See
[lyric qualification](docs/lyric-evidence-qualification.json) and
[GPU transport evidence](docs/gpu-observation-transport-receipt.json). Optional held-job audio preparation remains disabled in the installed service.

The current music observer and Pal Pal's lyric timing remain unqualified.

## Deployment

The hosted worker is [release-kit-studio-preview.dabbitech.workers.dev](https://release-kit-studio-preview.dabbitech.workers.dev), deployed with the `release-kit-studio` Alchemy profile in the verified Dabbitech account. It still serves the earlier frontend-only preview: authentication and production routes are unavailable there. The approved OAuth permission expansion is saved.

The subsequent deployment attempt stopped at the plan stage. R2 is not activated, and Containers require Workers Paid.

Approval for those new subscriptions, displayed terms and metered usage remains pending. Hosted submission has not been verified. `/api/health` reports the capabilities of the actual environment.

```sh
bun alchemy deploy --stage preview --profile release-kit-studio --dry-run
bun alchemy deploy --stage preview --profile release-kit-studio --no-input
```

The current grant contains D1, Containers, R2 and Workers Scripts read/write,
Account Settings read, Memberships read, and refresh access. Keep tokens and
license keys out of this repository. Deployment state lives under ignored
`.alchemy/`. Verify provider state, HTTP health and browser behavior after
deployment.

See [deployment receipt](docs/editor/deployment-receipt.json).

## Production pilot

The external Pal Pal workspace contains the canonical audio and planned kit under `music-video/release-kit-cloud-pilot/`. Its `resolve-local/` folder preserves the technically checked 3.875-second Telugu/environment-response pilot. The six-format automation diagnostic stalled in a native Fusion project-settings/render lock. The application and reservation were preserved, without a restart.

The pilot still needs normal-speed watch/listen review. The earlier full movie belongs to a previous workflow. No paid GPU was allocated.

Deployment of the new cloud editor remains incomplete. The declaration bounds the pilot to one
`standard-3` container, zero warm instances, internet disabled and termination
after verified R2 handoff. Resource limits bound capacity. They do not establish
an account-wide cost cap.

The Cloudflare editor supersedes the earlier
proposed Linux Resolve post-production path. 
