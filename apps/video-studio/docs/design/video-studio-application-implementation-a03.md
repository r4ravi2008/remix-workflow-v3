# Video Studio application A03 implementation

## Scope and status

This source package is an additive successor to the rejected A02 application package.
It owns only `apps/video-studio/application` and this evidence document.

The A01 package remains preserved at
`artifacts/scratch-video-goal-20261005/application-a01-rejected-preserved/`.
The A02 package remains preserved at
`artifacts/scratch-video-goal-20261005/application-a02-candidate-preserved/`.

The A02 peer review is
`apps/video-studio/docs/design/video-studio-application-source-peer-review-a02.md`.
Its SHA-256 is
`35fb2dfc004d675a7466947922d2f9c3299db08d3c0a9ed8c97362ca5d65056e`.

The current package passed the application typecheck, eight Vitest tests, Oxlint,
and Oxfmt checks. These checks cover the local application store only.
They do not qualify a native producer, provider, GPU, Resolve, or product bridge.

## A03 source changes

`domain.ts` adds a trusted `NativeProjectProvisioner` seam and a
`CreateProjectRequest` without caller-supplied native identifiers.
The default provisioner fails with `NativeProvisioningUnavailable`.
The public client asset input creates only `ClientImport` origins.

`storage.ts` provisions a native binding while holding the store lock.
It checks idempotent existing projects before provisioning again.
It writes the ownership registry before the tenant state.
The state write validates every relation and collection cap before promotion.
A failed state write leaves a conservative ownership claim.

The store rejects direct native asset writes through `createAsset`.
`createNativeAsset` requires a private runtime verification marker.
It verifies project, mapping, revision, schema, native identifier, source,
and receipt joins before it persists a `NativeOutput` record.
`application.ts` calls that path only after the injected `NativeBridge` verifies the receipt.
The mapping supplies the schema version; callers cannot select it.

The write barrier now validates job, attempt, submission-intent, and job-state tags.
It validates worker fence monotonicity, one active claim per job, and lease ordering.
Released claims require an exact release timestamp on replay.
Terminal provider results require exact semantic replay equality.
Source hashes require the `Sha256` runtime kind.

The serial fence rejects new work before close waits for accepted work.
Concurrent close calls share one close promise.
The lock remains held until the accepted queue drains and the lock handle closes.

State and ownership reads open a held descriptor with `O_NONBLOCK` and `O_NOFOLLOW`.
They reject non-regular files and sizes above the state cap before allocation.
They read the held descriptor into a bounded buffer and recheck identity and size.

## Read-only Rust grounding

The implementation does not claim a native capability from Rust.
The read-only source review covered:

- `apps/video-studio/crates/cli/src/main.rs`
  SHA-256 `6bc90118bf22fe74e8ae01caef9d7783cc76d210b6d9a8da30a60a161f1fe369`
- `apps/video-studio/crates/editor/src/project.rs`
  SHA-256 `a53132da6ff9ccdc6e21a32a7b73d0c833ffb7a35ff177815d6707129480698c`
- `apps/video-studio/crates/editor/src/lib.rs`
  SHA-256 `499156ec54f3046ce2901bb01ec5361ed755739911624166c971cd42e4bc04f9`

The source exposes `discover`, `project.create`, `project.inspect`, `project.commit`,
`asset.verify`, `asset.inspect-frame`, `asset.verify-frame-inspection`,
`project.prepare-export`, `project.export`, `project.cancel-export`,
`project.verify-export`, and `project.reconcile-export-staging`.
It does not expose a native project provisioning operation or a native receipt schema.
The application keeps that boundary as an injected, unconfigured authority.

## Current source identities

The following SHA-256 values were measured after formatting and the final local checks:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `src/application.ts` | 12,089 | `1acc9ff5546c82fbd442e9a50fe8d2ab9ddfba31aa9483cdf5c19f58ffaf0d46` |
| `src/domain.ts` | 17,036 | `7f8d7d910597f8ed1663cdc0dfd3de24cf16445cb580c74968cb5af314bed24c` |
| `src/index.ts` | 110 | `752e17b551b1a21a593a5c954830d425b26d0872f4459344be2936ad6ce93356` |
| `src/native-authority.ts` | 642 | `ccb1d982a6d43131d021bc66f0baadc2a66110b8e5199ac5188ac0548a09093a` |
| `src/schema.ts` | 6,192 | `1883c721dbe154735d986f5be80b45a118be617d616d0c5aa785ef0be59ccbab` |
| `src/storage.ts` | 91,312 | `587d7519f40fee27b3b1430f1f2628be9025345f8a96f32329c9649cd2c2227a` |
| `test/application.test.ts` | 20,060 | `e6f86a1c12105f92a954ec6cc74d0ddb867579f183b32961a426b0ce52d112be` |
| `package.json` | 346 | `516f52809cb7a9744a074db69edb3197fbecc52eb5235c791478db3f2762c8ae` |
| `tsconfig.json` | 450 | `9f8166a1e35b751cc8f0aa562433ca5158af80d11f4a647259d225c1b2b6e59f` |
| `vitest.config.ts` | 342 | `507e8e8cf10d5ac564f048aaf274a701c03b0203d93f2aa212171f6ade8cce5a` |

## Validation record

The checks used the existing bundled workspace dependency installation:

```text
tsc -p apps/video-studio/application/tsconfig.json --noEmit: passed
vitest run --config apps/video-studio/application/vitest.config.ts --reporter=dot: 8 passed
oxlint apps/video-studio/application/src apps/video-studio/application/test: passed
oxfmt --check apps/video-studio/application/src apps/video-studio/application/test: passed
```

The collection-cap test persists 1,024 assets, then rejects the 1,025th mutation.
The test suite also checks the unconfigured provisioning boundary, native-output bypass,
terminal-result replay, close fencing, tenant isolation, and ownership collision handling.

## Remaining limits

The default native provisioner remains unconfigured.
The default provider and native receipt verifier remain unconfigured.
The fake provisioner and fake bridges exist only in local tests.
No native receipt, Rust execution, provider call, GPU job, Resolve mutation,
or product deployment was performed by this package.

The application store is a single-process local JSON store.
It uses one root lock and does not claim distributed consensus or crash recovery.
The ownership registry is conservative after a state-write failure and may require repair.
The held read protects the opened file from pathname replacement.
It does not claim protection against arbitrary filesystem or host compromise.
