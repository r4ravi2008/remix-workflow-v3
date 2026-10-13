# Optional Release Kit agent

This directory contains the TypeScript and Python helpers for the optional Release Kit workflow.
It does not implement the standalone Rust editor.
For native editor work, start at [native-editor/AGENTS.md](../native-editor/AGENTS.md).

## Read the source by role

| Path | Role |
| --- | --- |
| `config.ts` | Private worker and workstation schemas |
| `probe.ts` and `gpu.ts` | Tailscale and Herdr provider checks |
| `worker.ts` and `service.ts` | One-job worker and Mac launchd supervisor |
| `supervisor.ts` and `production.ts` | Lease ownership, recovery, and workflow execution |
| `plan.ts` and `direction.ts` | Release plans, source fingerprints, and direction records |
| `editor-cli.ts` | Optional TypeScript client for the Cloudflare editor adapter |
| `resolve.py` | Historical Resolve diagnostic helper |
| `check-*.py` and `check-*.ts` | Optional workflow checks and receipts |

The native editor has separate ownership in `native-editor/`.
The agent does not call the native Rust binary or write the native SQLite store.

## Run the optional worker

Run these commands from `apps/release-kit-studio` with private configuration files:

```sh
bun agent/probe.ts .local/workstation.json
bun agent/worker.ts .local/worker.json
bun agent/reconcile-transport.ts .local/workstation.json
```

The workstation configuration names the managed machine, Herdr pane, SSH alias, and expected Tailscale host.
It also names the remote run root and local state directory.
The worker configuration names the API base URL, token, workstation configuration, local state, and plan registry.
Use mode `600` for both configuration files.
Never put a token in a URL, browser, repository, or log.
Never invent `HERDR_ENV=1` or a managed pane.

Install the owned Mac service only after the private worker configuration passes its checks:

```sh
python3 agent/install-service.py .local/worker.json
launchctl print gui/$(id -u)/com.dabbitech.release-kit-studio.worker
```

Stop the service before a smoke check that claims a queued job:

```sh
launchctl bootout gui/$(id -u)/com.dabbitech.release-kit-studio.worker
```

The service label is `com.dabbitech.release-kit-studio.worker`.
The installer writes a mode-600 launch agent and records registration readback.
Inspect the service and its saved state before you start it again.

## Preserve source and lease identity

Every Release Kit plan binds the release ID, full brief fingerprint, canonical audio hash, and attempt IDs.
The submitted brief must retain the exact native-script lyrics and measured audio duration.
Do not reuse a plan because its audio hash matches another brief.

The worker owns a lease while it reads source files, calls the GPU provider, collects footage, and submits finishing work.
An unknown response keeps the exact request fenced until reconciliation.
Do not retry an unknown inference or render outcome.
The worker checks the plan, attempt, lease, and saved receipt before a retry.

Direction and pilot-review holds remain assigned to their worker.
The worker resumes a hold only when the reviewed plan matches the complete frozen brief.
A reconciliation hold requires operator inspection.

The optional profile targets six outputs.
It requires independent source checks, output measurements, and private receipts.
Playback, listening, and creative approval remain separate gates.
No completed native six-output release is established.

## Use the optional editor adapter

The `bun run editor` command calls `agent/editor-cli.ts`.
It targets the optional Cloudflare or legacy TypeScript editor adapter.
It does not target `native-editor`.

Use the adapter only when the optional workflow task requires its schema or materialization commands:

```sh
bun run editor -- schema generated-production-plan
bun run editor -- schema recipe
bun run editor -- materialize recipe.json inputs.json measured-project.json
```

The materialization input binds `releaseId`, the frozen brief, canonical source, and collected shot IDs.
The destination must be new and mode `600`.
Materialization measures media and does not submit GPU work or establish creative acceptance.

## Read archived operators and receipts

Use these records for the detailed optional workflow history:

- [Archived local CLI guide](../docs/archive/2026-10-05/agent/LOCAL_CLI.md)
- [Archived production architecture](../docs/archive/2026-10-05/docs/production-architecture.md)
- [Archived director implementation](../docs/archive/2026-10-05/docs/director-implementation.md)
- [Archived implementation progress](../docs/archive/2026-10-05/docs/implementation-progress.md)
- [Optional editor receipts](../docs/editor/)
- [Service runtime receipt](../docs/service-runtime-receipt.json)
- [Browser worker receipt](../docs/browser-worker-receipt.json)

The archived local CLI uses Bun, SQLite, Python, and FFmpeg.
It documents an earlier implementation.
It does not establish Rust capability or define the native editor entry path.
