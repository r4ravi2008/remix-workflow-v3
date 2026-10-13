# Implementation plan

This document describes the Cloudflare editor. The standalone Rust editor is a separate application.

Each milestone completes only when PROGRESS.md and the machine-readable feature ledger link its acceptance tests and provider evidence. Implementation and
verification are separate fields. The agent can query the ledger through the CLI.

These files separately track source-bound perception qualification:
`../lyric-evidence-qualification.json` and
`../gpu-observation-transport-receipt.json`.
`../pal-vocal-alignment-qualification.json` tracks the existing-vocal comparison. The observer CLI uses the GPU
abstraction. The Editor Worker has no workstation dependency. Failed perception
qualification does not authorize bulk production.

## 1. Domain and tool surface

1. Define a versioned project document.
2. Define content-addressed assets and per-output timelines.
3. Define bounded edits and native-script captions.
4. Define explicit audio ranges, render intents, and artifact evidence.
5. Generate JSON schemas from Effect schemas.
6. Before cloud credentials are necessary, expose validation, capabilities, and progress locally through the CLI.
7. Before a render, reject malformed projects and unsupported controls.

Acceptance needs real fixtures for the six-output contract. Negative cases must cover:

- Gaps and bad trims.
- Missing sources and mixed/romanized lyric text.
- Wrong source hash and unsafe effects.
- Duplicated outputs and incompatible renderer controls.

## 2. Separate Cloudflare service

1. Use Alchemy to declare an Editor Worker beside the Foldkit Website Worker.
2. For the first version, share the tenant database and private media bucket.
3. Add editor tables through a new migration.
4. Forward same-origin editor routes through a Worker service binding.
5. Authenticate browser sessions and scoped agent tokens.
6. Derive the tenant on the server.
7. Store immutable revisions.
8. Only when the expected revision matches, atomically update the head.
9. Before dispatch, persist render intent.
10. Reject a reused intent with changed content.

Acceptance needs actual Worker health/tool readback. Tests must cover:

- Tenant isolation and replay.
- Revision conflicts and invalid/missing credentials.
- Bounded payloads and private artifact downloads.

The service API must contain no workstation addresses or local paths.

## 3. Native engine on Cloudflare

1. Build a pinned Cloudflare Container image with the product renderer, FFmpeg/FFprobe, shaped native-script text support, and approved fonts.
2. Route bounded recipes through a container-backed Durable Object.
3. Resolve source references through authorized Worker/R2 endpoints.
4. Use job-specific scratch directories, bounded concurrency, and execution deadlines.
5. Before you promote a successful job, persist artifacts to R2.
6. After work, terminate or idle the run-owned container.
7. Preserve immutable receipts for reconciliation.

1. Implement video/image conform, source trims, and sequenced clips.
2. Implement transforms, portrait framing, and color.
3. Implement lyric/title overlays, fades, and environment-only reactivity.
4. Expose actual engine capabilities.
5. Reject unavailable advanced operations.
6. Add one engine feature at a time with fixture-output verification.

Tenants have no arbitrary shell, URL, path, or filter-graph tool.

For acceptance:

1. Render a synthetic landscape canary and portrait canary.
2. Render a native-script caption canary, JPEG pair, and source-aligned audio.
3. Retrieve actual output bytes from the cloud.
4. Verify full decode and hashes.

A local container test is not a cloud-production receipt.

## 4. Verification and review

1. Create an independent artifact verifier with stream/duration/frame/format/hash checks, source-audio correlation, and clipping/loudness reports.
2. Generate boundary frames.
3. Generate review proxies.
4. Export findings and a manifest that the current completion contract can use.

Review evidence binds bytes, range, reviewer, and method.
Machine verification cannot claim full motion review, listening, or creative acceptance.

Acceptance: corrupt output, wrong portrait dimensions, silent/missing/swapped
audio, shortened film, source drift and stale artifact review all fail. After download, an independent verifier can verify the same manifest without trust in the renderer's claims.

The locally implemented `artifact.verify` measures every encoded frame at a 32-by-18
RGB-derived grayscale resolution. It reports near-black, flat and near-static
ranges, abrupt changes and every planned join's pixel delta. Explicit image holds
and fades provide limited exemptions. Measurements retain thresholds, complete
counts and omitted-finding counts.

The output schema is available through
`editor tools`. `frameDiagnostics` also survives kit manifest export.

The six-output native regression detected deliberate black and frozen video.
It distinguished an explicit image hold and measured the planned join. Cold
verification reproduced all findings from private stored bytes. The real archive
CLI preserved all six diagnostic records without another render. See
[native diagnostics](frame-diagnostics-runtime-receipt.json) and
[manifest export](frame-diagnostics-archive-runtime-receipt.json).
Reduced spatial measurements do not establish semantic inspection, full motion
review, listening or creative acceptance.

The locally implemented `artifact.preview` generates a private review video or still
from a completed artifact. The command also generates up to eight full-resolution JPEG frames. Requests
select exact source frames, with at most 240 video frames. The preview descriptor
binds source SHA-256, method version, range, derivatives and their measurements.

Independent source verification precedes generation. The engine calculates hashes of stored R2 bytes before it publishes the descriptor. Cached requests return identical derivatives
without another native operation. The shared verification slot covers generation.

The agent's `preview` command independently locates the original and verifies the descriptor.
The command streams all files into a new private directory with exact hashes.

Eleven local runtime checks verified video/audio ranges, full-resolution source
frame correspondence, still-image support, private downloads, tenant isolation and
cache replay. Five Studio session checks verified service-binding access, ranges,
HEAD and origin/session protection. JPEG conversion explicitly changes the color
matrix instead of only a tag change. Its versioned identity preserves earlier
diagnostic derivatives. See [preview proof](review-preview-runtime-receipt.json)
and [Studio session proof](review-preview-session-runtime-receipt.json).

The full-length ending check exposed a separate Bun socket idle timeout. The owned native operation completed after the caller stopped observation.
Recovery retrieved stored derivatives without another native operation. The client disables
that idle timer and preserves explicit request deadlines and lease cancellation.

Native generation retains complete source verification and extracts all JPEG
samples in one decode pass. A fresh ten-second ending from the current
5,753-frame film passed eight checks in 348.642 seconds. Last-frame correspondence,
stereo source correlation, complete decode, hashes and cached replay passed.
See [failure](review-preview-long-timeout-receipt.json),
[recovery](review-preview-long-recovery-runtime-receipt.json),
[fixed native proof](review-preview-long-runtime-receipt.json) and
[Bun HTTP proof](request-client-runtime-receipt.json).

Semantic seam inspection, complete motion/listening evidence, and public-cloud verification remain incomplete.

## 5. Web-to-editor integration

1. Replace the opaque machine-local Resolve plan with a serializable editor project reference in a versioned production plan.
2. Introduce an Editor service beside GPU.
3. Preserve old plan/receipt versions as historical evidence.
4. Connect real editor progress and private downloads to the Foldkit flow.
5. Keep held direction/review states accurate.
6. Retain the frozen brief and outer production attempt fence throughout the handoff.

The cloud adapter starts, polls, and reconciles an editor intent.
The adapter retrieves immutable output receipts.

Acceptance: hosted upload → canonical source readback → project revision → cloud
render → independent output verification → six assets in review. Replayed start,
worker restart, expired attempt and cancellation cannot promote stale results.

The implemented schema-v2 production plans bind an immutable project and explicit
source/shot/file inputs. `/api/worker/jobs/:id/editor/*` forwards to the separate
Editor Worker. The enrolled device and exact live lease derive the assigned
tenant and release on the server. Production assets use `p_<releaseId>_` IDs. Project and render access stays in the assignment.

Agents cannot issue
tenant credentials or record creative acceptance through this route.

Schema-v3 plans bind a generated-media recipe instead of predicted footage hashes before inference. Preflight checks the complete release, every planned
shot and all six output timelines. The supervisor validates the recipe before it resumes a reviewed hold. After collection, the materializer measures hashes, bytes, streams, dimensions, and duration.
Then, the materializer creates the immutable project.
Changed canonical audio, animated masks and insufficient source coverage fail.

The CLI exposes both schemas and creates measured projects without replacement of current files. Five tests use actual FFmpeg media. A supervisor test proves
missing and incomplete recipes cannot resume held work.

The adapter validates source bytes and uploads immutable media. The adapter commits a stable revision intent and renders all six outputs.
The adapter independently verifies each stored artifact. Then, the adapter promotes current private R2 objects into the outer review ledger.

Promotion validates the stored receipt hash, frozen source and complete output
contract. It rechecks ownership before the atomic completion transaction.
Stable asset IDs permit reconciliation across attempts without duplicate objects.
Legacy schema-v1 Resolve plans remain readable but cannot resume production.

Seven SQL/API tests cover lease authentication and expiry, cross-release access,
altered or incomplete receipts, partial recovery and concurrent promotion.
The local Workerd production canary passed six-output promotion, tenant private
downloads, full/ranged HTTP responses, exact hashes and complete downloaded
decodes. Final checks resumed the stored kit without another render. Hosted
acceptance remains a separate gate.

The generated-media adapter passed fifteen more local Workerd checks.
The adapter measured collected synthetic footage before commit.
All six outputs reached review and passed independent verification, private range downloads, and complete downloaded decode. This canary submitted no GPU inference and proves no Pal Pal
or hosted production completion.

The implemented packaging uses the separate Editor Worker to stream all six private R2
outputs. The Worker also streams an editable project checkpoint and a source-bound review manifest.
ZIP64 preserves large archive lengths without full-output buffers.
Per-entry SHA-256, byte counts and CRCs gate archive completion.
`kit.locate` exposes the descriptor. `archive` downloads and independently
verifies its eight entries without extraction or third-party Python packages.

Current destinations remain unchanged. Failed downloads remove their partial
file. The Studio resolves the completed Editor job and offers one kit download.

The local native canary archive passed full entry verification and six complete
media decodes. The actual Foldkit browser download matched CLI bytes exactly.
The reviewer inspected desktop and 390-pixel layouts. The reviewer revoked diagnostic tokens and closed browser sessions.

The reviewer submitted no render or GPU inference.
See `archive-runtime-receipt.json`. Multi-gigabyte transfer performance and
public-cloud behavior remain unverified.

## 6. Pal Pal production

1. Bind the selected audio, lyrics, and saved artist identity.
2. Build a complete heard song map.
3. Build a coverage plan.
4. Produce a bounded motion pilot.
5. Review the motion pilot.
6. Before bulk generation, get approved coverage.
7. Compose the full film, three separate portrait promos, and two stills in the editor.
8. Run technical verification.
9. Inspect seams and late frames.
10. Review full motion and sound.
11. Present exact artifacts for creative acceptance.
12. Do not reuse a diagnostic plate as full cinematic coverage.

Acceptance: all six outputs satisfy the source-bound contract and carry distinct
technical and perceptual review evidence. Publication remains separately scoped.

## Extension order

After the complete basic kit, add extensions in this order:

1. Add keyframe splines and transitions.
2. Add segmentation and tracked masks through GPU.
3. Add scene/color matching.
4. Add a proxy cache and resumable chunk rendering.
5. Add richer audio/visual comparison.
6. Add optional Resolve interchange.

Each extension adds catalog schema, domain validation, compiler support, verifier fixtures, and progress evidence together.
Unsupported fields never receive a successful no-op response.

## Shared native capacity: implemented and locally verified

Migration `0004_editor_capacity.sql` adds one deployment-wide D1 slot, a tenant
rotation cursor and registered render waiters. Alchemy applied the migration in
the local runtime. Render actors register before admission, rotate tenants with queued work, and preserve FIFO order in each tenant. Unattached queued jobs do not block registered actors.
Time in the queue does not start native execution or consume the execution deadline.

The slot also covers cold artifact verification. Its HTTP 503 response includes
`render_capacity_busy` and `Retry-After`. The production client retries only
that result, preserves the original request and stops when its lease is lost.
Cancellation of a queued job leaves the active tenant unchanged. Active cleanup
releases only an exact grant after confirmed native termination. Unknown native
outcomes retain the grant.

Six SQLite admission tests and three client tests passed. Seven actual local Workerd checks rendered two tenants and cancelled a third queued job.
The checks exercised verification backoff and decoded both downloaded outputs. Physical samples showed one native Container at peak and zero after cleanup. See
[capacity-runtime-receipt.json](capacity-runtime-receipt.json).

Full-length synthetic performance passed for a previous saved engine hash.
Decoded duration and frame diagnostics passed separate short regressions. See
[full-length evidence](long-kit-runtime-receipt.json) and
[compressed-source evidence](compressed-kit-runtime-receipt.json). The current
engine is bound by the [diagnostic receipt](frame-diagnostics-runtime-receipt.json).

Public-cloud enforcement, tenant quotas, verification fairness, and long-render crash/deadline stress tests remain incomplete. This deployment gate is not an account spend
limit.
