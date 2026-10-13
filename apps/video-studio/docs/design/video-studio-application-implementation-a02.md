# Video Studio application unit A02

Status: source implementation completed and checked locally. This is a bounded filesystem application unit. It does not execute the Rust producer, a native helper, a provider, a GPU job, or Resolve.

## Scope and predecessor

A02 preserves the A01 source review and evidence. The preserved review is:

```text
apps/video-studio/docs/design/video-studio-application-source-peer-review-a01.md
SHA-256 d66034cd949caa50e6f939b4267278b5e2262e2c8dd3233867a66bb032447fb1
```

The preserved A01 package is under `artifacts/scratch-video-goal-20261005/application-a01-rejected-preserved/`. Its preservation manifest has SHA-256 `3b9c46baec5a4d53b4637092bfbcae05392e7433820b573db0618200d7f14b8a`. A01 remains unchanged.

## A02 corrections

- `NativeProjectId` ownership is claimed in a root-scoped registry. A second tenant cannot claim the same native project identifier.
- Native receipts carry native project, application project, revision, schema, timeline, and source identity. Registration checks every join against the authorized mapping and input source.
- Context identifiers, record identifiers, provider names, source hashes, source bytes, text, timestamps, revisions, fences, and leases are checked at the storage boundary.
- Tenant identifiers use the fixed identifier grammar before they become path segments. The store root must be an absolute normalized path.
- The JSON state file is limited to 1 MiB. Each collection is limited to 1,024 records. Source metadata is limited to 1 TiB and text values to 4,096 schema characters. Numbers are finite non-negative or positive safe integers according to the field.
- A root-local exclusive `.application-store.lock` permits one open store for a root. The lock serializes all reads and writes for that store. The native ownership registry is updated under the same lock.
- State loading checks tenant ownership, unique identifiers, project and revision joins, native receipt joins, job and submission intent joins, attempt joins, review joins, budget totals, worker job references, and delivery joins.
- Project, job, asset, review, budget, submission, worker, and delivery operations compare all semantic fields needed for idempotent replay. Changed payloads return typed conflicts.
- Worker claims require an existing job, an unexpired lease, a worker owner, and a strictly increasing fence. Release requires the worker and fence that own the claim.
- Submission preparation persists the job transition, attempt, and intent before the provider callback. An unknown result requires reconciliation and blocks blind retry.
- Delivery records are tenant-scoped and bind a delivery to one project, revision, and asset. Reopening the store preserves the record.

## Tests and evidence

The test file uses fresh temporary directories for every test. It covers six cases:

1. All collections persist across close and reopen, including delivery and released worker records.
2. Project idempotence includes native mapping, source identity, and globally unique intent within a tenant.
3. The provider callback reads the durable submitting state, then an unknown result requires reconciliation.
4. Malformed JSON, foreign tenant state, non-finite numbers, and unsafe identifiers fail at the boundary.
5. One store is allowed per root, while the same local identifiers work in separate tenants. A native project cannot cross tenant ownership.
6. A native receipt with a changed source is rejected before asset creation.

The tests use fake typed provider and native bridges. They do not invoke external systems. The temporary filesystem is the measured persistence boundary for these checks.

Commands run from the repository root:

```text
apps/release-kit-studio/node_modules/.bin/tsc -p apps/video-studio/application/tsconfig.json
apps/release-kit-studio/node_modules/.bin/vitest run --config apps/video-studio/application/vitest.config.ts --reporter=dot
apps/release-kit-studio/node_modules/.bin/oxlint apps/video-studio/application/src apps/video-studio/application/test
apps/release-kit-studio/node_modules/.bin/oxfmt --check apps/video-studio/application/src apps/video-studio/application/test
```

Observed results: typecheck passed, six Vitest tests passed, Oxlint passed, and Oxfmt passed. The checks reused temporary symlinks to the repository's installed Effect, TypeScript, Vitest, and Node type packages. The application package retains normal dependency and script declarations for an independent install.

## Current source identities

```text
apps/video-studio/application/src/domain.ts       15908 bytes  3902ffa867cf6a1e082d7b154b43bcb385d5b948a42e8f321347e6fa00c24a36
apps/video-studio/application/src/schema.ts        6192 bytes  1883c721dbe154735d986f5be80b45a118be617d616d0c5aa785ef0be59ccbab
apps/video-studio/application/src/storage.ts      84065 bytes  fd9a01e6c3077d26908e83e5f31be6eaa5915d9f8b917caf079a5cc065c68b1e
apps/video-studio/application/src/application.ts  11322 bytes  054d28ef145e907b5d19c79ee8df090ac4325c32ddcaacaea314516cda8d77c2
apps/video-studio/application/src/index.ts          110 bytes  752e17b551b1a21a593a5c954830d425b26d0872f4459344be2936ad6ce93356
apps/video-studio/application/test/application.test.ts
                                                   16220 bytes  d89c416f817ade694b3557998baaa8336f8cb66ad7f598a13d246c786c27b24d
apps/video-studio/application/package.json          346 bytes  516f52809cb7a9744a074db69edb3197fbecc52eb5235c791478db3f2762c8ae
apps/video-studio/application/tsconfig.json         450 bytes  9f8166a1e35b751cc8f0aa562433ca5158af80d11f4a647259d225c1b2b6e59f
apps/video-studio/application/vitest.config.ts      342 bytes  507e8e8cf10d5ac564f048aaf274a701c03b0203d93f2aa212171f6ade8cce5a
```

## Limits

The file lock is local to one root and does not provide a distributed lease. Writes use exclusive temporary files and rename, without crash-fsynced transaction logging. The ownership registry has no deletion path in this bounded unit, so stale claims remain conservative. Authentication and actor policy remain an injected boundary. Provider and native adapters default to explicit unconfigured errors. This evidence does not qualify native execution, provider delivery, GPU execution, Resolve mutation, or product acceptance.
