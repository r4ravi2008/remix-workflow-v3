# Run plan and evidence

Use the existing production ledger when one exists. One run directory can contain `run.json`, `inputs.json`, shot plans, runtime/workflow snapshots, per-attempt intents/receipts/results, originals and review evidence. Keep secrets in the configured credential store or environment, never in these records.

Record:

- Project/run ID, requested endpoint, latest source catalog path/revision/hash, approval mode and allowed actions.
- Backend, verified account/project identifier, machine/pod ID, GPU and actual allocated hourly rate; ownership and current state.
- RunPod baseline and final resource inventories: all Pods including stopped/failed, their volume disks, network/global volumes, Serverless endpoints, clusters, and any shared-resource owners. Record resource IDs created or reused by this run, deletion/readback timestamps, and any explicitly retained resource with cost and removal deadline.
- Total authorized budget, observed balance/time, already spent estimate, actual charges when available, storage estimate, retry reserve, setup deadline, final shutdown deadline and who enforces it. Do not use catalog minimum prices as the allocated price.
- Runtime container/digest or install lock, ComfyUI commit, Python/Torch/CUDA versions, custom-node commits, model filenames/hashes and graph hash. Hardware substitutions keep the quality recipe fixed until a new pilot is reviewed.
- Per shot: stable ID, narrative or abstract role, anchor IDs/revisions/hashes, provider-input derivatives/crops, visual prompt, separate editor notes, seed, conditioning mode, native width/height/fps/frame count, usable target duration, protected invariants, handle requirements, placements and retry count.
- Per attempt: unique ID, intent token/time, workflow and input fingerprints, prompt ID, server history, errors, sampling/decode/save times, source output path/size/hash, local download path/size/hash, technical QC and perceptual disposition with accepted in/out ranges.
- Closeout: local transfer/hash/decode evidence, uncertain-job reconciliation, provider stop and deletion receipts, final all-resource inventory, current spend-rate readback, and billing-category readback with its observation time and any reporting lag. Mark closeout `verified` only when no run-owned billable resources remain; otherwise `pending` with an owner, cost, and deadline.

Use explicit states: `planned`, `ready`, `submitting-unknown`, `submitted`, `running`, `generated-unreviewed`, `downloaded-unreviewed`, `technically-checked`, `accepted`, `rejected`, `superseded`. Preserve evidence when advancing state. No metric can promote a clip to `accepted` without the applicable visual review. Source-snapshot changes invalidate dependent jobs; completed old jobs remain recoverable but do not enter the new edit automatically.

Calculate timeline coverage from interval unions after trim, retime and overlaps, not from job count or raw file duration. Distinguish generated originals, accepted unique motion, repeated source ranges, and editorially animated stills. Zero-duration anchor boundaries are cuts with an explicit seam decision. Cover the final audio tail; `N-1` adjacent pairs do not necessarily fill the whole requested duration.

At handoff, provide a simple chronological browse view with shot ID, origin, local original, accepted range, intended placement and review status. Keep canonical media paths stable; a renamed review copy must not strand Resolve references. Record remaining gaps and rejected takes explicitly. A hybrid or zero-spend fallback can be used only within the current brief; an older allowance for stills does not override a later no-static instruction.
