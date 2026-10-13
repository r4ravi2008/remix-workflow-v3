# Video Studio application A03 source peer review

## Disposition

A03 closes four of A02's seven repair groups and materially improves the other three.
Two P1 groups still block activation of a native project provisioner or native-output bridge.
Three P2 groups remain in worker recovery, durable transition consistency, and native artifact modeling.

This was a same-family, nonblind review.
The reviewer authored the preserved A01 and A02 peer reviews.

No native CLI, provider, GPU, media, Resolve, A18, compiler, or external helper operation ran.

## P1 findings

### P1.1: the native receipt marker is transferable and mutable

The native registration path adds a private `Symbol` property to a shallow receipt copy.
`isVerifiedNativeReceipt` accepts any object carrying that property with value `true`.

The symbol is private by TypeScript name only.
JavaScript exposes it through `Object.getOwnPropertySymbols` on a returned native asset.
The public `ApplicationStore` also exposes `createNativeAsset` through the package barrel.

A disposable canary reproduced an authority bypass:

1. One fake `NativeBridge` call verified Project A's receipt.
2. The returned asset exposed the marked receipt.
3. The canary extracted the symbol and attached it to a new Project B receipt.
4. The forged receipt matched Project B's stored identifiers and source.
5. `store.createNativeAsset` accepted the second asset without another bridge call.

The runtime marker therefore proves possession of a transferable property.
It does not prove that `NativeBridge` verified the submitted receipt object.

This does not demonstrate a remote JSON-client breach.
JSON cannot carry a symbol property.
It is an in-process authority defect in the directly exported store API.

The verified path needs non-transferable private membership and an immutable, deeply owned receipt snapshot.
The native-only insertion capability should not remain on the general public store surface.

References:

- `application/src/native-authority.ts:3-16`
- `application/src/application.ts:242-282`
- `application/src/storage.ts:59-77`
- `application/src/storage.ts:1438-1517`
- `application/src/index.ts:1-4`

### P1.2: provisioning can repeat an uncertain external side effect

`createProject` calls `NativeProjectProvisioner.provision` before it stores a durable creation intent.
The provisioning request omits `createIntentId`.
The provisioner contract does not require a read-only or idempotent lookup.

If provisioning creates native state and local publication then fails, a retry calls the provisioner again.
The store cannot reconcile an uncertain first result.

A disposable canary forced tenant-state publication to fail after provisioning and ownership publication.
The ownership claim remained conservative, which is correct.
After filesystem repair, the same create request called the provisioner a second time.

The default provisioner is unconfigured, so no external duplicate occurred.
This path blocks a side-effecting native provisioner from activation.

Either persist a stable provisioning intent before the call, then model unknown results and reconciliation.
Alternatively, define this seam as a pure attestation lookup with no external side effect.

References:

- `application/src/domain.ts:214-228`
- `application/src/domain.ts:433-443`
- `application/src/storage.ts:1248-1323`

## P2 findings

### P2.1: an expired active worker claim cannot be superseded

Claim creation validates that `leaseExpiresAt` is after `now`.
Persisted validation also requires a forward lease.

No operation expires an active claim.
`claimWorker` rejects every later claimant while the old claim remains `Active`.
It does not compare the old `leaseExpiresAt` with the new request's `now`.

A disposable canary created a claim ending at time 10.
A second worker requested fence 2 at time 11.
The store returned `WorkerLeaseConflict` for the expired worker.

The lease field therefore cannot support worker-loss recovery.
The unit needs a fenced expiry transition or an atomic expired-claim takeover rule.

References:

- `application/src/storage.ts:677-695`
- `application/src/storage.ts:1780-1867`

### P2.2: transition tags agree while their provider payloads can disagree

The reopen validator joins jobs, attempts, and submission intents.
It now requires compatible transition tags.

It does not compare the corresponding provider references or reasons.
A running job, submitted attempt, and confirmed intent can contain three different references.
Unknown and rejected transition reasons have the same gap.

A disposable canary changed only the persisted running job's provider reference.
The attempt and intent retained the original reference.
The store reopened this inconsistent state successfully.

The write path currently creates matching values.
The read barrier should validate exact payload equality across each durable transition.

References:

- `application/src/storage.ts:590-665`
- `application/src/storage.ts:2026-2128`

### P2.3: one `SourceIdentity` cannot represent both lineage and output artifact bytes

`ProjectRecord.source`, `NativeReceipt.source`, and `AssetRecord.source` use one shape.
Native registration requires all three values to be equal.

That equality is a sound input-lineage check.
It must remain strict.

The Rust `ArtifactReceipt` separately records its input revision and exported output hash and bytes.
A rendered native asset normally differs from the project's canonical input bytes.
The application model has no separate native output artifact identity.

This is a bounded adapter limitation while `NativeBridge` remains unconfigured.
It blocks a truthful native-output and delivery adapter.
A future adapter needs distinct input-lineage and output-artifact fields.

References:

- `application/src/domain.ts:230-286`
- `application/src/application.ts:267-281`
- `application/src/storage.ts:573-588`
- `crates/editor/src/exports.rs:20-32`

## A02 repair-group disposition

1. **Native ownership: partially closed.** Callers no longer supply native identifiers. Ownership publishes before tenant state, so a failed state write leaves a conservative claim. P1.2 remains.
2. **Native output authority: partially closed.** Client imports cannot assert `NativeOutput`. Mapping schema, project, revision, native identifier, and source joins are checked. P1.1 remains.
3. **Write validation: closed.** `persistState` validates collection caps and state relations before every state promotion. The maintained 1,025th-record test passes.
4. **Close lifecycle: closed for the stated single-process scope.** `closing` fences new work before the accepted tail drains. Concurrent closes share one promise.
5. **Worker and submission consistency: partially closed.** Fence ordering, one active claim, forward leases, and transition tags are validated. P2.1 and P2.2 remain.
6. **Exact replay and runtime tags: closed.** Release replay includes `releasedAt`. Terminal provider replay compares exact values. Source and identifier kind tags are checked.
7. **Bounded reads: closed for accepted Rust-owned bytes.** Reads use a held nonblocking, no-follow descriptor. Size admission precedes allocation, and identity is rechecked.

The close canary held provisioning open after the operation entered the queue.
`close` rejected new work, retained the root lock, and waited for the accepted operation.
The store reopened only after the accepted operation and close completed.

## Evidence accuracy

The implementation evidence lists `project.create`, then says no native project provisioning operation exists.
The precise statement is narrower.
Rust exposes project creation, but it exposes no tenant-aware ownership provisioner or application `NativeReceipt` schema.

This is a P3 documentation correction.
It does not change the unconfigured adapter state.

## Independent source inventory

The current package has ten files, rather than the requested nine.
A03 adds `src/native-authority.ts`.
All ten files match the implementation evidence:

```text
516f52809cb7a9744a074db69edb3197fbecc52eb5235c791478db3f2762c8ae       346  package.json
1acc9ff5546c82fbd442e9a50fe8d2ab9ddfba31aa9483cdf5c19f58ffaf0d46     12089  src/application.ts
7f8d7d910597f8ed1663cdc0dfd3de24cf16445cb580c74968cb5af314bed24c     17036  src/domain.ts
752e17b551b1a21a593a5c954830d425b26d0872f4459344be2936ad6ce93356       110  src/index.ts
ccb1d982a6d43131d021bc66f0baadc2a66110b8e5199ac5188ac0548a09093a       642  src/native-authority.ts
1883c721dbe154735d986f5be80b45a118be617d616d0c5aa785ef0be59ccbab      6192  src/schema.ts
587d7519f40fee27b3b1430f1f2628be9025345f8a96f32329c9649cd2c2227a     91312  src/storage.ts
e6f86a1c12105f92a954ec6cc74d0ddb867579f183b32961a426b0ce52d112be     20060  test/application.test.ts
9f8166a1e35b751cc8f0aa562433ca5158af80d11f4a647259d225c1b2b6e59f       450  tsconfig.json
507e8e8cf10d5ac564f048aaf274a701c03b0203d93f2aa212171f6ade8cce5a       342  vitest.config.ts
```

The evidence document contains 6,291 bytes.
Its supplied SHA-256 is
`0132bce982bfabd013aa09acb928168a641d3bece786e077b60c3492c549f898`.

## Executed application-only checks

The raw package has no local `node_modules` link.
The reviewer copied all ten files into an isolated temporary package.
Every copied file was hash-equal to the inventory above.
The temporary package linked the repository's existing dependency installation.

The resolved environment was:

- Node.js 24.9.0.
- Effect 4.0.0.
- TypeScript 7.0.2.
- Vitest 5.0.3. The package declares 5.0.2.
- Oxlint 1.86.0.
- Oxfmt 0.66.0.

The following checks passed:

- TypeScript typecheck.
- Vitest: one maintained file and 8 tests passed.
- Oxlint over `src` and `test`.
- Oxfmt check over `src` and `test`.

Five disposable canaries also passed their assertions:

1. Close fencing retained the root lock until accepted work finished.
2. A borrowed receipt marker authorized an unverified second native asset.
3. A failed local publication caused the provisioner to run again on retry.
4. An expired active worker claim blocked a higher-fence successor.
5. Mismatched provider references reopened when transition tags agreed.

The canaries used temporary directories and fake typed adapters.
They did not modify the application package or invoke an external system.

## Scope

This review covers the bounded single-process filesystem application.
Authentication, actor policy, native provisioning, native receipt decoding, and provider behavior remain injected boundaries.

The review does not qualify distributed locking, crash recovery, native execution, provider delivery, output media, or product acceptance.
