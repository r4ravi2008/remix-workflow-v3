# Reproduce and verify the inference runtime

Treat a saved API workflow as executable code bound to a runtime. Record the ComfyUI commit, custom nodes, Python/Torch/CUDA versions, model names/hashes, graph and GPU. Confirm actual device visibility, free VRAM, disk capacity and queue ownership. Resolve model names through the real repository and live node schema; do not turn historical H3/Hunyuan labels into a universal recipe.

Inspect `/system_stats` and `/object_info`, then verify every graph node class, required input, model filename and output/save option. Check the graph's accepted width/height and frame-count lattice; do not round an arbitrary requested duration into an unsupported native length. Generate enough native frames for the usable range and transition handles, then record the exact conform separately.

ComfyUI's `/prompt` validates and queues a graph; `/queue` and `/history/{prompt_id}` observe its lifecycle. A successful submission is not a completed encode. These routes are documented by [ComfyUI](https://docs.comfy.org/development/comfyui-server/comms_routes); inspect the current node definitions for model/save-specific fields.

## End-to-end pilot

Test loading the actual accepted anchor, conditioning, sampling, decode, save, transfer, probe and full decode before a batch. Confirm native dimensions, frame count/fps, playable output and lack of unintended generated audio in the eventual edit. Save original bytes once; create mezzanines or review proxies as separately identified derivatives.

Urvashi's first H3 pilot sampled successfully but needed a save-node codec/schema repair. The repair reused cached generation nodes and wrote the video without repeating diffusion. Diagnose the failed stage first. If cached tensors/frames survive, repair only encoding or save; verify the output still binds to the same graph inputs and record the repair. Do not charge for a full rerun just because the final file is missing.

## Idempotent jobs

Use one stable shot ID and a distinct immutable attempt ID. Before POSTing, atomically save an intent with a unique token, input fingerprint and workflow hash. Save the returned prompt ID immediately. The helper [comfy_job.py](../scripts/comfy_job.py) refuses an existing intent/receipt; use its `status` or `reconcile` command after interruption.

`reconcile` searches the live queue/history for the exact token and graph hash. Multiple matches or no retained evidence remain unresolved; absence from a cleared history is not proof of non-submission. A client token is a correlation key, not server-enforced idempotency. Do not automatically resubmit an unknown job. A diagnosed failed attempt gets a new attempt ID after verifying it is terminal.

Poll the known prompt. Inspect both status and output metadata; wait for save completion. Do not download a still-growing MP4 or trust a nonzero file size when `moov`/decode is incomplete. Collect output from the successful history, not a glob for the newest file. Keep completion and quality states separate.

Run the helper on the execution host so its input verification reads the files that ComfyUI will actually load. A forwarded API is suitable only when the verified input and output roots are the server's actual shared filesystems; hashing a different local copy does not verify remote inputs. It only collects history-named videos inside an explicit output root. Copy the archived result across hosts through the chosen transfer route, then verify bytes and hash again. It never clears queues or interrupts unrelated work.
