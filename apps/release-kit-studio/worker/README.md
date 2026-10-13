# Optional Tailscale and Resolve pilot

This directory contains the optional GPU workstation inventory and Resolve preflight helpers.
It records the earlier Release Kit workflow.
It does not describe the standalone Rust editor.
For native editor work, start at [native-editor/AGENTS.md](../native-editor/AGENTS.md).

## Read the source by role

| Path | Role |
| --- | --- |
| `resolve_preflight.py` | Read-only host, staged-input, Resolve scripting, and GPU checks |
| `linux_inventory.py` | Read-only inventory from the managed Linux or WSL pane |
| `../agent/gpu.ts` | Tailscale provider and reservation transport |
| `../agent/resolve.py` | Historical Resolve diagnostic helper |
| `../docs/resolve-automation-diagnostic.json` | Saved pilot diagnostic receipt |

The Rust editor owns native project semantics, rendering, and artifact integrity.
The pilot does not establish native capability, Resolve parity, or a current Rust backend.

## Run read-only preflight

Run the preflight on the verified Resolve host.
Use a new receipt path for every attempt.
Keep the staged input root and manifest on the owned host.

```sh
python3 worker/resolve_preflight.py \
  --expected-hostname VERIFIED_HOST \
  --provider PROVIDER_NAME \
  --worker-id WORKER_ID \
  --sdk-dir /path/to/DaVinciResolve/Scripting/Modules \
  --input-root /path/to/staged-input \
  --manifest manifest.json \
  --receipt receipt.json
```

The script checks the host name, input hashes, and input byte counts.
It also checks the official Resolve scripting module, Resolve Studio, and the current project.
It records `renderCanary: pending`, `watched: false`, and `heard: false` until those gates pass.
The script does not render a film or approve a release.

Run `linux_inventory.py` only inside the genuine managed pane.
The script requires `HERDR_ENV=1` and the verified workstation host.
Do not create those values by hand.

```sh
python3 worker/linux_inventory.py /home/WORKER_USER/projects/remix-workflow-v3/runs/release-kit-service/inventory.json
```

The inventory is read-only.
It does not launch Resolve, submit inference, or claim a production job.

## Preserve the pilot gates

Transfer exact source files to the Mac and compare their hashes before import.
Keep the canonical WAV unchanged.
Use a separate Resolve project for the pilot.
Save the project checkpoint before a change.
Verify exported pixels, audio, hashes, and complete decode.

Release GPU and Mac reservations after the owned run reaches a terminal state.
Keep failed attempts and their reasons.
Treat queue state or a render canary as technical evidence only.
Normal-speed playback, listening, pilot acceptance, and the six output gates remain separate.

The archived pilot record preserves the observed Resolve version, host, project ID, dimensions, frame count, and audio comparison.
The saved pilot is not a completed six-output release.

## Read archived operators and receipts

- [Archived Resolve pilot runbook](../docs/archive/2026-10-05/worker/README.md)
- [Archived editor specification](../docs/archive/2026-10-05/docs/editor/SPEC.md)
- [Archived editor architecture](../docs/archive/2026-10-05/docs/editor/ARCHITECTURE.md)
- [Archived editor implementation](../docs/archive/2026-10-05/docs/editor/IMPLEMENTATION.md)
- [Archived editor progress](../docs/archive/2026-10-05/docs/editor/PROGRESS.md)
- [Resolve automation receipt](../docs/resolve-automation-diagnostic.json)
- [Editor runtime receipts](../docs/editor/)

Those records describe the Tailscale, Resolve, Cloudflare, or Python implementations that produced them.
They do not promote a Rust capability or establish hosted deployment.
