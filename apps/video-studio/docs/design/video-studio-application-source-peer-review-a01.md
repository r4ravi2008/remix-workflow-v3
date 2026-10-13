# Video Studio application A01 source peer review

## Disposition

The bounded Effect application has four P1 findings and five P2 finding groups.
The current native and provider adapters are unconfigured, so no external breach or submission occurred.

The review applied `principle-type-system-discipline` and `typescript-best-practices`.
It covered every application source file, all three tests, and the implementation evidence.

## P1 findings

### P1.1: a tenant can claim another tenant's native project identifier

`CreateProjectInput.native` contains a caller-supplied `NativeProjectId`.
`createProject` validates only the timestamp before storing that identifier.

The store partitions mappings by tenant, but it has no global native-project ownership claim.
Tenant B can therefore store Tenant A's `NativeProjectId` under Tenant B's mapping.
`authorizeProject` then returns that duplicate mapping as authorized for Tenant B.

References:

- `application/src/domain.ts:374-379`
- `application/src/application.ts:122-128`
- `application/src/storage.ts:736-757`

This is a dormant authorization defect.
No native CLI bridge is active in this unit, so the source does not demonstrate native access.
The defect must close before a worker derives a native CLI request from this mapping.

### P1.2: native receipts are not bound to the authorized project or declared source

`NativeReceipt` has no native-project, application-project, or revision identity.
`registerNativeAsset` verifies the opaque receipt and its schema version only.

The method does not compare `receipt.source` with `input.source`.
It also does not bind the receipt to `mapping.native.nativeProjectId`.
A valid receipt from another native project can therefore register as this project's asset.

References:

- `application/src/domain.ts:204-209`
- `application/src/application.ts:200-217`

This confused-authority path is also dormant because the native bridge is unconfigured.

### P1.3: structural tenant identifiers reach filesystem paths without validation

The identifier types are structural objects, and `TenantContext` is publicly constructible.
The file store inserts `context.tenantId.value` directly into a path.

The store does not call `makeId` or enforce a previously validated opaque context.
A forged value containing path separators can escape the tenant directory.

References:

- `application/src/domain.ts:20-23`
- `application/src/storage.ts:623-640`

The documented upstream authorization contract does not enforce this filesystem invariant.
The storage boundary must validate the path segment or accept only an opaque trusted context.

### P1.4: non-finite numeric inputs can make durable state unreadable

Most public numeric inputs are not decoded at the application boundary.
`reserveBudget` and `claimWorker` pass their values directly to the store.

For example, `requestedUnits = NaN` passes the current comparison checks.
`JSON.stringify` then writes `reservedUnits` as `null`.
The next state read fails schema decoding.

Worker fence, lease, revision, source-byte, and several timestamp values have the same boundary gap.
TypeScript's `number` type does not exclude `NaN` or infinity.

References:

- `application/src/application.ts:225-230`
- `application/src/storage.ts:908-1000`
- `application/src/schema.ts:20-25`

## P2 findings

### P2.1: job, intent, and attempt cross-joins are incomplete

`createJob` can return an existing job after checking only intent and request fingerprint.
It does not require the stored project and revision to match the new request.

`prepareSubmission` does not require the supplied fingerprint to equal the job fingerprint.
Its existing-intent check ignores `attemptId`.
Its new-attempt path does not reject an existing attempt identifier.

`recordSubmission` can update an intent when its referenced attempt or job is absent.
It also selects the first attempt with a matching identifier.

References:

- `application/src/storage.ts:818-850`
- `application/src/storage.ts:1038-1100`
- `application/src/storage.ts:1138-1187`

`ReconciliationRequired` is also absent from `isStoreFailure`.
One store reconciliation failure is consequently wrapped as `StorageError`.

References:

- `application/src/storage.ts:599-615`
- `application/src/storage.ts:1057-1061`

### P2.2: idempotence checks omit semantic fields

Asset reuse ignores revision, origin, native receipt, and declaring principal.
Review reuse ignores disposition.
Claim reuse ignores lease expiry and observation time.

The same project-creation intent can also create more than one project.
The lookup starts with `projectId`, rather than enforcing global intent uniqueness.

References:

- `application/src/storage.ts:736-790`
- `application/src/storage.ts:871-885`
- `application/src/storage.ts:961-974`

These paths can report idempotent success for changed commands.

### P2.3: worker claim ownership and fencing are incomplete

`claimWorker` does not require the referenced job to exist.
It accepts an already expired lease and does not require monotonic fencing.

The store can create several active claims for one worker and fence.
`releaseWorker` accepts only a claim identifier and timestamp.
It cannot prove that the releasing worker owns the claim.

References:

- `application/src/storage.ts:951-1028`
- `application/src/application.ts:225-230`

### P2.4: the JSON store has no enforced size bound or complete consistency check

The store reads and parses the complete tenant file.
Every record collection is an unbounded array.
No file-byte, record-count, or aggregate-payload limit is enforced.

Schema decoding checks field shapes, but not relational consistency.
It does not check nested tenant equality, unique identifiers, references, budget totals, or claim relations.

The mutation queue belongs to one `openFileStore` instance.
Two store instances for the same root can race within one process.
The documented concurrency boundary should therefore say "one store instance," not "process-local."

References:

- `application/src/schema.ts:166-181`
- `application/src/storage.ts:591-700`

The evidence correctly discloses the lack of filesystem locking and crash-fsynced durability.
Those disclosed limitations remain outside this finding.

### P2.5: delivery is absent, and two evidence claims exceed the tests

The selected architecture requires tenant-scoped delivery records.
This package has no delivery identifier, record, schema collection, store method, or application operation.
Delivery isolation is therefore not implemented or reviewable.

The submission test reads state only after `provider.submit` returns.
It does not observe durable state inside the provider callback.
Source order supports persistence before the call, but the test does not prove that claim.

The reopen test excludes attempts and submission intents.
The later submission test creates them but does not reopen the store.
The suite therefore does not prove that every required collection survives reopening.

References:

- `application/src/domain.ts:362-371`
- `application/src/application.ts:30-82`
- `application/test/application.test.ts:167-242`
- `docs/design/video-studio-application-implementation-a01.md:21-29`

## Confirmed bounded strengths

- A valid tenant context scopes all implemented records under one tenant state file.
- The submission source persists a created intent and attempt before calling the provider adapter.
- A prepared intent does not trigger another provider call.
- An unknown submission requires explicit reconciliation before another attempt.
- Native schema knowledge remains behind `NativeBridge`; the application invents no capability names.
- The application does not duplicate the Rust timeline reducer.
- The domain uses closed unions for provider results and submission states.

## Executed checks

The following checks passed on the reviewed source:

- TypeScript typecheck with the repository compiler.
- Oxlint over `src` and `test`.
- Oxfmt check over `src` and `test`.
- Vitest: one file and three tests passed.

These checks did not invoke a native CLI, provider, GPU, Resolve, or media operation.
This is a same-family, nonblind source review of an uncommitted bounded application unit.
