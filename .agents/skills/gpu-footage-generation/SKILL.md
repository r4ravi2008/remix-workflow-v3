---
name: gpu-footage-generation
description: Generate and recover AI motion footage on RunPod GPUs or a local network GPU reached through Herdr. Use for anchor-to-video jobs, ComfyUI setup, pilot cost checks, resumable batches, verified transfers, and reviewed footage handoff to an editor.
---

# GPU footage generation

Turn selected anchors and shot requirements into usable local motion footage. Support RunPod and an existing local/WSL GPU reached through Herdr. Keep provider operations, model/workflow, source authority and creative acceptance explicit. Generating files alone does not complete an integrated film edit.

## Establish the run

Read the latest request and existing project state. In the remix repository, resolve `.remix-workspace-root.json` and read the selected workspace's `meta.json`. Reconcile the current source catalog, storyboard/shot timing, prior jobs, accepted takes and rejected ranges. Do not assume that the oldest “full motion” folder, largest image count, or newest filename is authoritative.

Record a compact run plan using [run-record.md](references/run-record.md): requested endpoint, exact source snapshot, shot IDs/ranges, backend/model, budget, allowed GPU/provider substitutions, concurrency, retry limit, deadlines, storage, output destination, approval mode and edit handoff. Retain the user's existing authorization. Ask only for a genuinely missing spending limit, source decision or required approval; a paid run is never implied by a planning-only request. Existing-footage-only requests skip generation entirely.

For music videos, use [music-video-director](../music-video-director/SKILL.md) for story, musical timing, anchor acceptance and final editing. This skill executes the agreed footage plan. Standalone footage requests can use the same records without creating a full song project.

For local video upscaling, first read the director's [upscaling-and-restoration.md](../music-video-director/references/upscaling-and-restoration.md). Use the existing footage as immutable input and apply this skill's host, pilot, memory, transfer and recovery controls when a separate GPU upscaler is needed. Resolve Super Scale runs on Resolve's own host; do not treat a connected Herdr GPU as an automatic remote renderer.

## Choose the execution route

| Backend | Read before connecting |
|---|---|
| RunPod | [runpod.md](references/runpod.md): account, capacity, actual price, persistent storage, transfer canary, bounded billing and shutdown |
| Local network / WSL through Herdr | [herdr-local.md](references/herdr-local.md): managed-pane requirement, saved machine discovery, existing agent/queue ownership and source staging |
| Either, using ComfyUI | [comfyui-runtime.md](references/comfyui-runtime.md): pinned runtime, live node schema, compatible workflow, save-node pilot and recovery |
| Reproduce the recorded H3 I2V workflow | [h3-recipe.md](references/h3-recipe.md): portable graph, parameterization, source bindings, and submit/collect commands |

Use the selected backend. A bigger GPU can improve memory headroom or throughput; it does not by itself improve the same model's pictures. Compare identical workflow settings and accepted footage per dollar. Honor explicit GPU/model restrictions. Do not buy credits, silently switch provider, or start multiple billed machines without authorization covering that choice.

## Stage, pilot, then batch

1. **Prepare locally before billing.** Accept the current anchors and fixed shot boundaries, separate visual prompts from editor notes, and prepare workflow/runner files. Review footage design using [shot-design-and-review.md](references/shot-design-and-review.md).
2. **Freeze the inputs.** Use [asset_snapshot.py](scripts/asset_snapshot.py) to hash the selected assets. Verify the same snapshot on the execution host. A stale `/mnt/c` mirror or iCloud placeholder is not an input. Check dimensions, active picture and model-specific constraints separately.
3. **Prove the whole path.** Verify GPU/runtime, available memory/disk, model hashes, live nodes, and both transfer directions. Run one representative pilot through sampling, decoding, final save, original download, probe/decode, and actual visual review. Include the hardest identity/action risk before bulk generation. A provider “complete” badge is insufficient.
4. **Measure cost.** Record setup/download time separately from cold and warm generation, decode/save and transfer. Project remaining spend using the actual allocated rate and accepted usable seconds, with retry and shutdown reserves. Pause billed compute during human review, research, missing inputs or failed setup once files are safe.
5. **Run bounded batches.** Use [comfy_job.py](scripts/comfy_job.py) or an equivalent existing runner with the same intent/receipt/recovery invariants. Default to one active generation per GPU until measured concurrency proves useful. Download each finished original promptly. Do not queue the entire film behind an unreviewed pilot.
6. **Review and hand off.** Keep downloaded, technically checked, visually reviewed and accepted counts separate. Reject or trim defects, update usable coverage and consumed anchor revisions, then hand off originals, accepted ranges, receipts and review evidence. If integrated editing was requested, continue into the director's Resolve replacement and preview steps; honor any explicit “generate everything before Resolve” gate.
7. **Close the provider run.** For RunPod, follow the full [resource closeout](references/runpod.md#resource-closeout) after verifying local copies: stop compute, terminate run-owned Pods and their volume disks, remove run-owned independent storage and other billable resources, then read back the complete resource inventory and spend rate. A stopped Pod can keep charging for disk, so `EXITED` is an interim state, not a completed closeout. Keep unrelated or shared resources identified in the preflight inventory. Record any exception and its ongoing cost. For Herdr, verify the owned local GPU job has stopped and preserve its host's shared resources.

## Reusable helpers

```sh
python3 <skill-dir>/scripts/asset_snapshot.py create --root <asset-root> --output <run>/inputs.json <relative-file> ...
python3 <skill-dir>/scripts/asset_snapshot.py verify --root <remote-staged-root> --manifest <run>/inputs.json
python3 <skill-dir>/scripts/comfy_job.py --help
```

The ComfyUI helper submits one already-prepared API graph, preserves a submission intent before the request, recovers prompt IDs from queue/history, and collects a completed video on the execution host with full decoding and hashes. It never allocates a GPU, builds a model graph, approves images, transfers across hosts, enforces account spend, or shuts down a pod. Those are explicit run steps. Its deadline guards admission only; supervise or arrange an authorized independent shutdown mechanism before renting compute.

For interruptions, inspect the existing job before retrying. Preserve uncertain submissions; an absent HTTP response does not mean the server received nothing. Failed generations need a new attempt ID and diagnosis, not an overwrite. Limit retries per shot, redesign within the brief when possible, and never lower the quality bar to exhaust remaining credit.
