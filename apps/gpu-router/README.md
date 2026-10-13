# GPU Router

A separate Effect TypeScript service for submitting GPU jobs through one API.
The service selects an eligible provider, tracks the job, returns artifact receipts, and confirms resource cleanup.
Customers submit containers or ComfyUI workflow bundles rather than rent machines directly.

**Current state: tested local simulation. No live GPU provider, customer payments, or cloud deployment is connected.**
The local API uses SQLite and two explicitly named simulated providers.
The Alchemy stack defines a Cloudflare Worker and D1 database.
The cloud Worker has an empty provider registry and refuses job creation with `503 no_capacity`.
The stack has been typechecked. Cloud resource creation has not been verified.

## Run locally

1. Run `cd /Users/aira/projects/remix-gpt-coding-agent/apps/gpu-router`.
2. Run `bun install --frozen-lockfile`.
3. Run `bun run check`.
4. Run `bun run dev`.

The API listens on `http://127.0.0.1:1341` while the development process runs.
Use `GPU_ROUTER_PORT` to choose another port.
The local demo key is `gpu-router-local-demo`. Use `GPU_ROUTER_DEV_TOKEN` to configure a different local key.
SQLite persists jobs and simulation resources in `.state/router.sqlite` across restarts.
The development process advances active jobs every 500 ms.

While the development server runs, use `bun run smoke` for an HTTP canary.
After restarting the server, use `bun run smoke --replay` to verify that the same intent still returns the original job.
The canary also checks output bytes, SHA-256, simulation disclosure, and confirmed resource release.

Submit the saved example:

```sh
curl http://127.0.0.1:1341/v1/jobs \
  -H 'Authorization: Bearer gpu-router-local-demo' \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: demo-one' \
  --data-binary @examples/container-job.json
```

The example image and digest are placeholders. The simulation does not pull or execute them.
Copy the returned job `id` into the status request:

```sh
curl http://127.0.0.1:1341/v1/jobs/JOB_ID \
  -H 'Authorization: Bearer gpu-router-local-demo'
```

The completed simulation returns a text artifact explicitly stating that no GPU ran.
No MP4, model output, or real container execution is implied.

## API

| Method | Path                  | Result                                                                 |
| ------ | --------------------- | ---------------------------------------------------------------------- |
| GET    | `/health`             | Connected capabilities and simulation status                           |
| POST   | `/v1/quotes`          | Eligible offers sorted by the requested strategy                       |
| POST   | `/v1/jobs`            | Persist an idempotent job and return `202`                             |
| GET    | `/v1/jobs/:id`        | Read a job belonging to the API key's tenant                           |
| POST   | `/v1/jobs/:id/cancel` | Record cancellation; wait for reconciliation and cleanup when required |

Every route except `/health` requires a tenant API key.
Job creation also requires `Idempotency-Key`.
Reusing the key with the same decoded request returns the original job.
Reusing the key with different content returns `409`.
API keys are stored as SHA-256 hashes. Tenant identity comes from the key, never the request body.
Request bodies are limited to 1 MiB. Large files belong in object storage.

Container images require a digest. Workflow bundles require a URL and SHA-256.
`minVramGb` describes memory on each GPU. Multiple GPUs do not implicitly pool memory.
An empty region or provider array permits any eligible entry in that category.
`lowest_cost` and `fastest_start` remain subject to workload, hardware, region, interruption, and estimated cost constraints.

Quotes include startup time, fixed costs, and the maximum requested runtime.
Money in quotes uses integer microdollars: `1,000,000` microdollars equals `1 USD`.
The request's `maxCostUsd` filters estimates. **It is not a verified hard billing cap.**
Local prices are fictional test values. No provider prices were measured.

## Job ownership and cleanup

```mermaid
stateDiagram-v2
  Queued --> Dispatching: persist intent and claim
  Dispatching --> Running: provider accepts
  Dispatching --> Queued: definitive rejection
  Dispatching --> Uncertain: response lost
  Uncertain --> Running: original resource found
  Uncertain --> Queued: authoritative absence
  Running --> CleanupPending: success, failure, cancellation, or timeout
  CleanupPending --> Finished: resource release confirmed
  Queued --> Finished: cancellation or queue deadline
```

Optimistic version checks prevent concurrent dispatchers from claiming the same job.
Each attempt receives a saved reconciliation token before provider submission.
Lost responses and typed submission failures block fallback.
Cancellation remains recorded if it races with submission.
Attempt receipts retain provider, quote, token, reference, and confirmed release time after completion.

Effect scopes alone cannot recover resources after a process dies.
Durable job records and authoritative provider reconciliation must handle that recovery.
The simulated resources also persist in SQLite, so a development-process restart preserves recovery evidence.

`Succeeded` currently validates artifact receipt structure. It does not independently fetch a live artifact or verify its bytes.
The test suite verifies the simulated artifact's digest and byte count.
Live artifact integrity verification belongs in the real adapter and collection path.

## Connect a real provider

The provider contract is in `src/providers.ts`.
An adapter must implement inventory, submission, reconciliation, status, and release through Effect.
The contract has deliberate requirements:

- `Rejected` means submission created no resource and incurred no billable work.
- `Unknown` means resources may exist. The router must keep reconciling the saved token.
- `Absent` requires authoritative evidence that this attempt created no billable resource. A missing inventory item alone is insufficient.
- `release(true)` requires confirmed cleanup of all attempt-owned compute, disks, volumes, and endpoints.
- Operations must respect deadlines. Worker interruption cannot serve as the provider's remote runtime limit.
- Artifact bytes must be collected and checked before claiming a verified live output.

The first real adapter should target RunPod. Vast.ai provides a second route for the same tested runner protocol.
Provider-specific container startup, networking, minimum billing, storage, credentials, and cleanup remain adapter responsibilities.
Live adapters must recheck offer availability and quote validity before spending.

Production work remains:

1. Package and verify a portable GPU runner with an input manifest and output receipt protocol.
2. Implement RunPod submission, token reconciliation, remote deadlines, artifact collection, and cleanup readback.
3. Add a second provider and prove portability with the same image and inputs.
4. Add private object storage and scoped input/output access.
5. Add durable immediate dispatch, queue fairness, concurrency limits, and recovery monitoring.
6. Implement credential onboarding and decide between customer provider keys and service-owned billing.
7. Implement a usage ledger and verify all cost components against provider billing records.
8. Deploy an isolated preview and complete a budgeted real GPU pilot.

The current Worker uses a one-minute cron as a recovery foundation.
The active-job scan is limited to 100 rows. It is not a production scheduler and can starve later rows.
External account selection and an explicit pilot spend cap remain unset.

## Sources and stack

Effect `4.0.0` and Alchemy `2.0.0-beta.80` match the existing Release Kit Studio package.
This service has its own dependency lockfile and does not modify Release Kit Studio.

- [OpenRouter provider selection](https://openrouter.ai/docs/guides/routing/provider-selection): the unified API and policy-driven routing reference.
- [Alchemy](https://alchemy.run/): Effect-based application infrastructure and Cloudflare resources.
- [RunPod create Pod API](https://docs.runpod.io/api-reference/pods/POST/pods): container, GPU, region, and storage configuration.
- [RunPod Pod lifecycle](https://docs.runpod.io/pods/manage-pods): stopping retains billable volume storage; termination and independent storage need separate handling.
- [Vast.ai official CLI](https://github.com/vast-ai/vast-cli): offer discovery and instance lifecycle.

Release Kit Studio can become an early client for video generation and upscaling once live execution is verified.
