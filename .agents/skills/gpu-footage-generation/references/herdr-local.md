# Local network GPU through Herdr

Load the installed `herdr` skill before any Herdr control. The current backend is `herdr-core` (`hc`); legacy `herdr` is only a fallback. Discover, never assume, the host:

```sh
hc machine ls                      # saved machines and state; use the exact name, e.g. aira-workstation
hc ls --all --json                 # live terminals here and on connected machines (address: machine/tN)
hc exec --on <machine> -- nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv
```

An explicit user request to use the workstation authorizes control of that machine through `hc`; it does not authorize touching other agents' terminals there. Inspect live terminals, GPU processes, listening ports and queues before changing anything. Do not restart Herdr, reinstall a working stack, clear another owner's queue or type into a busy foreground program.

## Own a named terminal for long work

Run installs, model downloads and the ComfyUI server in your own named terminal so the user can watch it and you can resume it:

```sh
hc run --bg --on <machine> --cwd <root> --name <task>-setup --no-parent --outlive-parent --label task=<project> -- bash -lc '<cmd>; exec bash'
hc read <machine>/<name-or-tN> --lines 20
hc send <machine>/<name-or-tN> '<next command>'     # only when that shell is idle
```

Use `hc exec --on <machine> --timeout N -- <argv>` for short bounded commands; it is not a shell unless you run `bash -lc`. Write small text files with `hc file write --on <machine> <path> < local-file`. Move binary media with `scp` to the host's SSH target shown by `hc machine ls`, then compare SHA-256 on both sides. Never overwrite a script that a running `bash` is still executing; write a new filename instead.

## Transfer from the authoritative machine

An observed Urvashi failure exposed an old 55-entry catalog through WSL `/mnt/c` while the Mac's selected catalog had 47 current anchors. Those historical counts are examples, not expected values.

Create a run-specific snapshot on the authoritative host. Stage it in a new remote run directory, preferably on the host's native filesystem for active inference. Verify the same snapshot there: compare IDs, file count, bytes and hashes, then check the workflow's actual load-image paths against those files. Stop on mismatches. Never merge stale files by basename or infer synchronization from a mounted path. iCloud files can be evicted placeholders on the Mac (`Resource deadlock avoided`): `brctl download` them and re-hash before staging.

Keep generation metadata on the execution host and copy each completed original plus its receipt/graph/history back promptly. Verify bytes and SHA-256 after the transfer. Preserve failed originals and generated-vs-derived provenance. A local worker has no rental bill, but it can be shared: do not clear its queue or stop another owner's process. Stop only processes you started, and record when you release the GPU.

## Current workstation profile (verify before relying on it)

Recorded 2026-11-12; re-measure on each new run.

| Item | Observed |
|---|---|
| Host | `aira-workstation`, NixOS, RTX 4070 Ti 12 GB, ~128 GB RAM, root disk ~97% full (check free space before downloads) |
| Stack | `~/projects/comfyui-ltx` built by [comfyui_ltx_setup.sh](../scripts/comfyui_ltx_setup.sh): ComfyUI v0.45.0, ComfyUI-GGUF, Torch 2.14 cu130, LTX-2.5 distilled GGUF + FLUX.2 [klein] 4B; see [local-ltx-flux-recipe.md](local-ltx-flux-recipe.md) |
| Server | `serve` in a named Herdr terminal on `127.0.0.1:8188` (`--lowvram --cache-none --reserve-vram 2`) |
| Resolve | Whatever edition the host has. Free Resolve cannot be scripted externally; see video-director [workstation.md](../../video-director/references/workstation.md) |
| Older stacks | The pre-NixOS WSL ComfyUI/LTX Q3_K_M install no longer exists; `~/projects/video-generation` is a separate official-LTX runtime without weights |
