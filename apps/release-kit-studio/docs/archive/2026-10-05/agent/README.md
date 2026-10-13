# Production agent

This trusted Mac agent claims jobs from the studio API. The browser does not control its filesystem paths, workstation, pane, executable commands or GPU graph.

Run from the app directory with an ignored private configuration:

```sh
bun agent/probe.ts .local/workstation.json
bun agent/worker.ts .local/worker.json
bun agent/reconcile-transport.ts .local/workstation.json
bun run observe schema
bun run observe .local/workstation.json .local/observation.json
```

The installed Mac service uses `agent/service.ts` and the label `com.dabbitech.release-kit-studio.worker`. It currently connects to the native local Alchemy API, not the hosted preview. After you complete the private configuration, install the service:

```sh
python3 agent/install-service.py .local/worker.json
launchctl print gui/$(id -u)/com.dabbitech.release-kit-studio.worker
```

The installer preserves any current service or launch-agent file. It writes a mode-600 plist with configuration paths, keeps credentials in the private configuration, and records registration readback. `service-status.json` records the live process's polls. Verify the launchd PID too.

To stop this owned service, use `launchctl bootout gui/$(id -u)/com.dabbitech.release-kit-studio.worker`. Bootstrap the saved plist to start it again. Before you run smoke scripts that claim queued jobs, stop the service. The isolated production canary seeds its own test lease outside the shared queue.

Workstation configuration contains `machine`, `pane`, `sshAlias`, `expectedTailscaleHost`, `remoteRoot` and `localState`. The remote root must be under the workstation project's `runs/` directory. Install `remote_gpu.py` plus the installed GPU skill's `comfy_job.py` and `asset_snapshot.py` helpers there through the verified route. Create a genuine managed pane.

Never synthesize `HERDR_ENV`.

Worker configuration contains `baseUrl`, `token`, `workstationConfig`, `localState` and `planRegistry`. Enroll the device through the operator API. Save the returned token locally with mode 600.

Never place the token in a browser, URL, repository, or log. HTTPS is required outside localhost. The service checks held plans and queued work every 20 seconds.

A one-job CLI remains available for isolated operation. Operator device revocation disables the token. It does not clear provider or renderer ownership.

Direction and pilot-review holds clear the active lease and remain assigned to their worker, so repeated polls cannot claim them. The service resumes a hold only after its reviewed plan matches the complete frozen brief. The API checks that binding and worker ownership again. A reconciliation hold is excluded from automatic resume.

If an interrupted attempt cannot be reconciled against the API, `worker-attention.json` fences local dispatch. It can clear automatically only after the exact attempt has six verified review assets. Other uncertain states require inspection of the saved attempt and native resources.

The plan registry uses `<releaseId>.json`. Current plans finish through the separate Cloudflare editor Worker. Schema v2 binds an already measured immutable project and source files. Schema v3 binds an editor recipe whose footage hashes become known after GPU collection.

Legacy Resolve schema v1 remains readable for history. The supervisor does not resume it. Both current schemas contain `releaseId`, `briefSha256`, `audioSha256`, `approvedForBulk`, `reviewEvidence`, `shots` and `editor`. Use `briefFingerprint` from `plan.ts` for the complete server-owned brief.

Its canonical JSON sorts object fields. The release and full brief must match before inference. Do not reuse another artist's plan only because the audio hash matches. A shot defines an immutable attempt ID, remote ledger, graph, verified input snapshot/bindings, input/output roots, archive and save node.

The agent calls `ensure`, which reconciles known inference before it submits a new intent. An unknown inference state is a hold, not a retry.

A schema v3 plan declares `editor.projectId`, `expectedRevision` and `recipePath`. The recipe binds canonical audio, collected shot IDs and trusted local files to all six compositions. Preflight rejects foreign briefs, unknown or unused shot attempts, incomplete outputs and timeline gaps before inference. After collection, materialization hashes and probes the actual media.

It rejects changed masters, missing streams, animated masks and footage trims beyond the measured duration. The immutable project then enters upload, commit, render, independent verification and private R2 promotion.

Discover strict schemas or measure a recipe offline:

```sh
bun run editor -- schema generated-production-plan
bun run editor -- schema recipe
bun run editor -- materialize recipe.json inputs.json measured-project.json
```

The materialization input contains `releaseId`, the frozen `brief`, `canonicalSource` and collected `shots` with `id` and `path`. The operation creates the destination with mode 600. The destination must not exist.

Materialization measures media. It does not submit GPU work or establish creative acceptance.

A shared Mac reservation protects the configured Herdr pane throughout each RPC. A lost response keeps its exact request reserved. `reconcile-transport.ts` downloads and validates that request's saved terminal response before it releases the reservation. It submits no inference and does not delete an active GPU lease.

If the response is absent or invalid, preserve the reservation and inspect the managed pane and ledger.

Job leases renew every 45 seconds throughout source download, generation, collection, finishing and promotion. A failed renewal interrupts local I/O and prevents subsequent publication. Remote inference or Cloudflare renders that the agent already submitted can continue. Reconcile their saved ownership and receipts before a retry.

The production promotion endpoint rechecks the exact worker and lease before the atomic completion transaction.

Source downloads and readback of stored outputs use streams with SHA-256 checks. Partial downloads never replace the verified copy. The native editor renders four videos and two stills, then independently verifies the stored outputs. Promotion binds the private R2 receipt, immutable project, complete master and exact six-output contract.

It reuses stored R2 objects without another download and upload of the outputs.

The separate Editor shares one native capacity slot across its tenants. Renders without a capacity slot remain queued. Render admission rotates tenants and preserves FIFO order
within each tenant. Cold verification uses the same slot.

The production client
retries only HTTP 503 with `render_capacity_busy`, with bounded `Retry-After` delays while the lease remains live. It does not retry render starts or unknown failures. Artifact verification, review previews and render status/reconciliation have a ten-minute request
budget. Lease cancellation still interrupts the request and any busy-slot retry.

Other CLI requests retain thirty seconds. Production requests retain two minutes. The Bun client disables its separate socket idle timer. Explicit request
deadlines and lease cancellation still apply.

If observation ends while native
work remains live, reconcile the current operation before you submit another.

The Editor CLI can download source-bound review clips and full-resolution frame
samples. Save a request that selects a ready job and an in-bounds range:

```json
{
  "jobId": "READY_JOB_ID",
  "outputId": "film",
  "startFrame": 0,
  "frames": 240,
  "sampleFrames": [0, 119, 239]
}
```

```sh
bun run editor -- preview preview.json new-review-directory
```

The command independently locates the original output, validates its preview
descriptor and streams each file through a hash check. It refuses directories that already exist. Video ranges contain at most 240 frames, and sample lists contain at
most eight unique in-range frames. Empty lists select the first, middle and last
frames.

Still requests use `startFrame: 0`, `frames: 1` and one sample. Downloads
include the exact source hash and derivative hash. Generation shares native
verification capacity. Cached replay needs no native compute.

The saved receipt
does not claim semantic inspection, complete motion review, listening or creative
acceptance. The CLI runs no local renderer.

With the local runtime and its saved synthetic diagnostic kit available, run:

```sh
python3 agent/check-editor-preview.py
python3 agent/check-editor-preview-session.py
```

The first checker expects uncached derivative requests. For a repeated completed check, account for cache reuse. The session checker uses
stored derivatives and submits no native compute. Both checks revoke their
diagnostic credentials and preserve the source job.

See the source-bound receipts
in `docs/editor/`. Public-cloud and browser playback proof remain separate.

To verify an ending from the saved full-length synthetic kit, run:

```sh
python3 agent/check-editor-preview-long.py
bun run test:editor-bun
```

The ending checker downloads the original 140 MB film. It requests 240 ending
frames and four full-resolution samples, with the last encoded frame among them. It verifies hashes, complete decode, independent source seeks, exact stereo
audio range and cache replay. A repeat of the same request verifies stored derivatives without native compute.

It creates no new film or GPU operation. The fresh local run took 348.642 seconds. Cloud performance remains unverified. The Bun check verifies actual HTTP deadlines and owning-lease cancellation.

With local Alchemy active on ports 1337/1339, run the isolated native scheduling
check from the app directory:

```sh
python3 agent/check-editor-capacity.py
```

The check uses fresh tenants and scoped credentials. It renders two synthetic
outputs, cancels a queued job, verifies downloaded bytes, and records actual
Container counts. It revokes its tokens and logs out its sessions. It submits no
GPU inference and does not resume assigned production holds.

This proves local
runtime behavior. Public-cloud and real-song acceptance remain separate.

Run the full-length synthetic benchmark only when long-film behavior needs
verification. Its local x64 render can take more than twenty minutes:

```sh
python3 agent/check-editor-long-kit.py
```

After you change how audio duration works, run the short compressed-source regression:

```sh
python3 agent/check-editor-long-kit.py compressed
```

Both checks verify all six private outputs and eight archive entries. They record
source hashes, revoke diagnostic credentials and confirm native termination.
Each receipt applies to its saved engine revision. Neither completes a real song.

The editor project declares canonical audio/hash/duration, language, 24 fps envelope and exactly six output compositions. Each scene declares its original hash, source trim, timeline range, framing and bounded effects. The full film covers the complete audio. Vertical outputs have their own scene, framing and cue plans.

Reactive masks must exclude people, lyrics and story props. Final acceptance needs a full watch and listen.

`resolve.py` preserves the earlier diagnostic path. A provisional Mac Resolve diagnostic stalled in a native Fusion render lock. Sources, the earlier Pal Pal pilot and diagnostic ownership records remain preserved.

Current finishing uses Cloudflare. No Linux Resolve worker is requested or configured.

With no production plan, `direction.ts` automatically prepares `direction-v2-<briefSha256>/direction-input.json` and `audio-analysis.json` beneath the assigned job directory. Initial claims and later held-job polls both use this step. It checks the complete frozen brief and canonical bytes, preserves the native lyric lines, and commits private artifacts atomically. Repeat polls reuse artifacts that match.

Corrupted evidence is held for attention rather than silently replaced. The packet names Cloudflare finishing and the Tailscale GPU transport. Version 1 packets remain historical evidence. These packets are director inputs.

Storyboard and pilot acceptance remain separate.

`analyze_audio.py` requires Python 3.11+, FFprobe and FFmpeg. NumPy is no longer required. Duration comes from decoded PCM samples.

Browser uploads and native observer/renderer preflight use the same decoded-duration basis. Compressed container padding does not extend the song. The original file bytes and SHA-256 remain authoritative.

The helper also measures per-channel RMS and band-filtered bass response. It records a coarse beat candidate when the measurement permits one. Silence has no invented beat grid.

Media manifests and network protocols are excluded. Listening, lyric alignment, storyboard review and pilot watch/listen remain separate. A complete audio/video director has not been verified.

Node worker lint keeps type checks, import ordering and the remaining shared rules. Its asynchronous execution helpers do not use Foldkit's UI decision-time purity rule. UI code continues to enforce that rule.

`audio-perception.py` is a fixed local model runner under verification. It pins
Qwen2-Audio-7B-Instruct to revision `0a095220c30b7b31434169c3086508ef3ea5bf0a`
and uses NF4 quantization. `windows DURATION` works offline.

`download`, `inspect`
and `inspect-song` require the genuine managed GPU pane and owned service paths. The isolated director environment installs `requirements-director.txt`. It reads
installed Torch/Transformers files without a change to the ComfyUI environment.

Each perception request binds job/release IDs and the exact source hash, bytes, and duration.
Each request binds one range of at most 30 seconds and a new receipt path. The runner checks actual decoded sample coverage and reserves the active shared GPU lease. It rejects an occupied ComfyUI queue.

It records the pinned model, prompt hash, and raw response. Complete-song mode uses overlapping windows without silent truncation of the tail. Each window runs in a separate process so CUDA memory is released before the next.

It preserves terminal window evidence and refuses changed or failed observations. Model audio coverage, lyric timing, full watch/listen and creative acceptance
remain separate. This runner does not resume jobs or approve bulk generation.

The eight-second local GPU canary passed actual feature/token checks. Known speech
and silence fixtures also passed. Full-precision audio encoding fits the RTX 4070 Ti. The text decoder uses NF4.

The complete 239.68-second Pal Pal master reached the
model in ten overlapping windows. An independent execution-host audit re-decoded
every range and checked its checksum. Six responses contain unmeasured numeric
claims. Interpretation remains unverified, so automatic musical-direction
qualification still fails.

Earlier failed receipts remain preserved. See
`docs/audio-perception-complete-coverage.json` and the historical qualification.

`observe.ts` exposes fixed `audio-window` and `speech` operations through the
configured Effect GPU service. The trusted JSON input binds the job, release,
complete brief fingerprint, native lyrics, source checksum and measured range. The browser cannot choose a command or workstation path.

The provider stages a
hash-verified immutable audio snapshot and runs the fixed isolated interpreter. Each operation preserves its input and runner hashes. A replay reuses the terminal receipt without another inference.

An inference intent without a receipt remains fenced. Returned receipts are bounded, checksum-verified and saved with mode 600. Changed source bytes or a foreign receipt prevent acceptance.

Keep failed and
unusable observations distinct from uncertain transport outcomes.

Audio windows optionally select `audioBackend: "qwen2.5-omni"` in the trusted
observation intent. The default remains `qwen2-audio`. The Omni backend loads
only the pinned Qwen2.5-Omni-7B thinker. Audio and vision encoders remain BF16.

The text decoder uses NF4. Missing or mismatched thinker weights fail the load
contract. The operation binds both native runner hashes, the questionnaire,
decoded PCM, attended features and expanded audio tokens. A receipt from another
backend cannot satisfy the selected operation.

This backend remains unqualified
for automatic direction until real GPU controls pass. See
`docs/omni-observation-qualification.json` for provisioning and processor evidence.

`speech-evidence.py` uses the pinned local faster-whisper-large-v3 snapshot with
the isolated `requirements-speech.txt` environment. It records recognized words
and timing candidates without changes to supplied lyrics. Known speech passed.
This included numeric normalization from `seven` to `7`.

Pal Pal's source-bound pass
preserved 23 raw segments and 176 words, but a word exceeded its segment boundary. Timing qualification failed. No repair or exact lyric alignment was invented.

See `docs/speech-evidence-qualification.json`.

`perception.ts` prepares complete-song observation receipts for assigned holds. The optional trusted worker field `audioObservations: { attempt: "r01" }` enables
this diagnostic preparation in the supervisor. It covers the complete source,
reuses checked window receipts and preserves failed windows.

It never sets
`automaticDirectionQualified`, `fullSongHeard` or pilot approval. The installed
configuration leaves this option disabled while model qualification is unresolved. The optional `backend` field selects the same fixed audio backend.

For example,
`audioObservations: { attempt: "omni-r01", backend: "qwen2.5-omni" }` prepares
Omni evidence under a fresh attempt. Backend selection changes operation IDs. A backend change cannot reuse a preserved attempt summary.

Audit complete-song evidence without inference:

```sh
python3 agent/audio-perception.py audit-song song-receipt.json canonical-audio
```

Place the original `window-00.json` and later window receipts beside the song
receipt. The audit ignores recorded host paths and verifies those adjacent files. Exact decoded checksums require the execution-host decoder. The Mac and workstation
FFmpeg decoders produced different floating-point sample checksums.

The audit
preserves original observations and applies the current numeric-claim filter. Processing coverage, mechanically valid observations, interpretation, lyric
timing and creative acceptance remain distinct.

Local API checks:

```sh
python3 agent/http_smoke.py
python3 agent/storage-smoke.py
```

These create private test tenants and a canonical Pal Pal job in local Alchemy bindings. Credentials remain in `.local/`. The storage check recovers an expired smoke lease and uploads a known short original. The check confirms that the original cannot complete the full release. It is not a release-kit producer.
