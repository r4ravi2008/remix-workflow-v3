# Video Studio application unit A01

Status: implemented and tested locally. This unit is bounded to `apps/video-studio/application`. It does not execute the Rust producer, a native helper, a GPU job, a provider request, or a Resolve operation.

## Boundary

The application receives an already authorized `TenantContext`. The context contains a typed `TenantId` and `ActorId`. Public operations do not accept a tenant path or a raw tenant selector.

`makeId` returns an Effect only after checking the fixed identifier grammar. IDs carry a distinct `kind` value, so a `ProjectId` cannot be passed as a `JobId`. `makeSha256` checks the lower-case 64-hex digest form. Source byte counts are finite positive safe integers.

`authorizeProject` loads the project through the tenant context. It returns an immutable `AuthorizedProjectMapping` containing the tenant, actor, project, native project, versioned native schema, and current revision. A project stored under another tenant is not visible through this operation.

The native bridge receives a `NativeSchemaVersion` and an opaque receipt. The bridge owns schema-registry lookup and native receipt validation. The application stores native timeline and source identity only after the bridge returns a validated `NativeReceipt`. The default bridge fails with `NativeUnconfigured`; this package adds no capability names or native reducer.

## Persistence

`openFileStore` creates one `state.json` file per tenant under an absolute root:

```text
<root>/tenants/<tenant-id>/state.json
```

The tenant ID is validated before it becomes a path segment. The stored document is schema version `1` and contains typed collections for projects, assets, jobs, attempts, reviews, budgets, worker claims, and submission intents. `Schema.decodeUnknownEffect` rejects malformed JSON and excess fields before domain conversion.

Writes use a fresh exclusive temporary file and an atomic rename. A process-local promise queue serializes reads and writes. A read or update also checks the tenant ID inside the document against the requested context. The local store is a bounded application test store. It is not a multi-process database and does not claim crash-fsynced durability.

Project creation, job creation, asset creation, review creation, and budget reservation use stable identifiers as idempotency keys. Repeating the same payload returns the existing record. Reusing an identifier with changed content returns a typed conflict.

Worker claims store a worker ID, fencing number, and lease expiry. An active unexpired claim for the same job blocks a different worker. Release is idempotent.

## Submission protocol

`prepareSubmission` persists the job transition, attempt, and `SubmissionIntentRecord` before the provider bridge is called. The result carries either `Created` or `Existing` so a repeated call cannot submit an existing intent again.

The provider result is a closed union: `Confirmed`, `Rejected`, or `Unknown`. `Unknown` persists `ReconciliationRequired` on the job and `Unknown` on the attempt and intent. A later `submitJob` call returns `ReconciliationRequired` without calling the provider. `reconcileJob` is the only route for an unconfirmed intent. It accepts both `Prepared` and `Unknown`, which covers a process exit before a provider response was recorded.

Provider and native bridges are injected typed adapters. The defaults return explicit unconfigured errors. No credential, token, URL, provider response, or native receipt is logged by this package.

## Effect usage

The implementation uses Effect 4.0 `Effect.gen`, `Effect.tryPromise`, `Context.Service`, `Layer`, and `Schema.decodeUnknownEffect`. `StudioApplicationService`, `ApplicationStoreService`, `ProviderBridgeService`, and `NativeBridgeService` provide typed seams for later external adapters.

The API choices follow the official Effect 4 documentation for [running effects](https://effect.website/docs/v4/getting-started/running-effects), [service layers](https://effect.website/docs/v4/requirements-management/layers), and [Schema decoding](https://effect.website/docs/v4/schema/getting-started).

## Files

- `application/src/domain.ts` defines IDs, records, state unions, bridge seams, and domain errors.
- `application/src/schema.ts` defines the versioned persisted wire document.
- `application/src/storage.ts` implements the tenant-scoped JSON store and atomic writes.
- `application/src/application.ts` exposes authorized project, record, worker, submission, reconciliation, and native receipt operations.
- `application/src/index.ts` exports the bounded public surface.
- `application/test/application.test.ts` runs tenant isolation, idempotence, persistence, and uncertain-submission checks with temporary roots.
- `application/package.json`, `tsconfig.json`, and `vitest.config.ts` keep the unit independently runnable. The test configuration aliases the repository's already installed Effect and Vitest packages. It does not install or modify repository dependencies.

## Verification

Commands run from the repository root:

```text
apps/release-kit-studio/node_modules/.bin/tsc -p apps/video-studio/application/tsconfig.json
apps/release-kit-studio/node_modules/.bin/oxlint apps/video-studio/application/src apps/video-studio/application/test
apps/release-kit-studio/node_modules/.bin/oxfmt --check apps/video-studio/application/src apps/video-studio/application/test apps/video-studio/application/*.json apps/video-studio/application/*.ts
apps/release-kit-studio/node_modules/.bin/vitest run --config apps/video-studio/application/vitest.config.ts
```

The typecheck passed. Oxlint passed. Oxfmt passed after formatting. Vitest passed three tests.

The tests confirm that tenant B cannot read tenant A records, repeated create operations return the same records, changed idempotency payloads fail, all required record collections survive reopening the store, an unknown provider response is persisted before returning, and a second submission does not call the provider again. Reconciliation then completes the same intent.

## Current limits

The store has no multi-process locking or database transaction log. A deployment needs a transactional persistence adapter before multiple application processes share a root.

The tenant context is an authorization result. Authentication, actor policy, and tenant membership are outside this unit.

Project revision remains `0` in this bounded unit. A later commit operation must advance revisions through an immutable project aggregate before export planning.

The default native and provider bridges remain unconfigured. Rust owns native timeline and source identity, and this unit does not claim native execution, provider delivery, GPU execution, or product acceptance.

