# Video Studio application A02 source peer review

## Disposition

A02 closes several A01 findings, but four P1 groups and three P2 groups remain.
Two P1 groups affect native authority before any native bridge can be enabled.

This was a same-family, nonblind review.
The reviewer authored the preserved A01 review and compared every A01 finding with A02.

No native CLI, provider, GPU, media, Resolve, A17, or A18 operation ran.

## P1 findings

### P1.1: native ownership remains first-writer authority and can fail open across two files

`CreateProjectInput` still carries a caller-selected `NativeProjectId`.
`NativeBridge` verifies receipts but does not provision or authenticate that project identifier.

The ownership registry therefore proves only which application tenant claimed an identifier first.
It does not prove that the tenant owns an existing native project.
A tenant can reserve another tenant's unregistered native identifier before bridge activation.

References:

- `application/src/domain.ts:412-418`
- `application/src/domain.ts:519-524`
- `application/src/storage.ts:1155-1219`

The registry and tenant state also publish in a fail-open order.
`createProject` promotes tenant state before it writes the ownership registry.
An ownership-write failure leaves a project record without its global claim.

A disposable filesystem canary reproduced this sequence:

1. Tenant A's state promotion succeeded.
2. Its ownership publication failed with a root-directory permission error.
3. `createProject` returned `StorageError`.
4. Tenant B then claimed the same native identifier successfully.
5. Tenant A's persisted state became unreadable under the new ownership entry.

This contradicts the evidence claim that stale ownership remains conservative.
The observed residue is a missing claim, rather than a conservative stale claim.

This is a dormant native-authorization defect today.
No active bridge used either mapping.

### P1.2: the public asset path bypasses native receipt authority

`StudioApplication.createAsset` accepts the full `AssetOrigin` union.
Any caller can therefore supply `NativeOutput` directly.
That caller bypasses `registerNativeAsset` and its native bridge verification.

The store validates the receipt's field shapes only.
It does not validate the receipt against the project's mapping before persistence.

References:

- `application/src/domain.ts:248-266`
- `application/src/application.ts:42-45`
- `application/src/application.ts:151-162`
- `application/src/storage.ts:930-937`
- `application/src/storage.ts:1347-1385`

The reopen validator also compares receipt source only with asset source.
It does not compare receipt source with the authoritative project source.
A disposable canary stored and reopened that mismatched native source successfully.

References:

- `application/src/storage.ts:565-579`

The verified registration path has a second gap.
It compares receipt schema with the caller's requested schema.
It does not compare either schema with `mapping.native.schemaVersion`.

References:

- `application/src/application.ts:221-255`

A second canary registered a `cli-v2` receipt against a `cli-v1` mapping.
The operation returned success and promoted the asset.
The next state read rejected the application's own persisted bytes.

Native output creation must have one authority path.
The project mapping must control the schema used for receipt verification.

### P1.3: mutation paths can persist state that the reader rejects

`update` serializes and promotes `next` without calling `validateStateRelations`.
The separate project writer has the same central validation gap.

References:

- `application/src/storage.ts:1113-1125`
- `application/src/storage.ts:1215-1219`
- `application/src/storage.ts:1261-1293`

The 1,024-record limit runs only during state decoding.
An operation can append record 1,025 while the encoded file remains below 1 MiB.
The operation returns success, but every later read rejects the state.

References:

- `application/src/storage.ts:472-511`
- `application/src/storage.ts:129-130`

A disposable canary loaded 1,024 valid assets, then created one more asset.
The 1,025th creation succeeded.
The next read failed with `StorageError` at `decode`.

The two native receipt canaries also demonstrated this missing write barrier.
One operation must validate caps and relationships before promotion.

### P1.4: close can release the root lock before accepted work finishes

`serial` accepts work while `closed` is false.
`close` waits for the current `tail` before it sets `closed`.

An operation can replace `tail` while `close` awaits the earlier promise.
`close` then removes the root lock without awaiting that accepted operation.

References:

- `application/src/storage.ts:986-998`
- `application/src/storage.ts:1988-2002`

A disposable canary reproduced the race with a bounded 900 KiB state file.
`close` completed while the late read remained pending.
A second store acquired the same root lock before that read finished.
The late operation then completed successfully.

The same queue admits mutations, so this breaks the claimed single-store serialization boundary.
Concurrent `close` calls can also pass the pre-await `closed` check together.

## P2 findings

### P2.1: reopen validation does not cover all modeled state relationships

Worker claim validation checks only that each job exists.
It does not reject duplicate or regressing fences in persisted state.
It does not require an active lease to expire after `claimedAt`.

References:

- `application/src/storage.ts:625-627`
- `application/src/schema.ts:80-94`

Submission validation joins identifiers and fingerprints.
It does not require job, intent, and attempt state tags to describe one transition.
A confirmed intent can coexist with a submitting job and prepared attempt.

References:

- `application/src/storage.ts:581-613`

The successful operation paths enforce more rules than the reopen path.
Shape-valid external corruption can therefore pass reopening and affect later decisions.

### P2.2: two idempotence and exact-type boundaries remain incomplete

Releasing an already released claim compares worker and fence only.
It ignores the replayed `releasedAt` value.
A changed command therefore returns idempotent success.

References:

- `application/src/storage.ts:1758-1766`

`recordSubmission` returns an existing terminal state without comparing a repeated result.
A changed terminal provider result is also silently treated as success at the store boundary.

References:

- `application/src/storage.ts:1928-1929`

`validateSource` validates the hash value but not the `Sha256` kind tag.
`recordSubmission` also does not validate its `IntentId` before lookup.
These are smaller gaps in the claim that every typed identifier is checked at runtime.

References:

- `application/src/storage.ts:899-911`
- `application/src/storage.ts:1898-1907`

### P2.3: the 1 MiB read limit is an acceptance check, not an allocation admission bound

`readBoundedText` performs `stat(path)` and then `readFile(path)`.
It checks the second byte length only after `readFile` owns the complete allocation.

References:

- `application/src/storage.ts:1003-1010`

A concurrent local writer can grow or replace the file between those path operations.
The store rejects the result, but it can allocate beyond 1 MiB first.
The documented cap should describe accepted bytes unless reads use a held descriptor and bounded chunks.

The six maintained tests do not cover this race, record 1,025, or the close fence.
They also do not cover direct `NativeOutput` creation or mapping-schema mismatch.

## A01 findings that A02 closes

- Validated tenant and actor identifiers now precede tenant path construction.
- Public operation inputs reject non-finite and unsafe numeric values.
- Successful registry publication prevents a second tenant claim.
- Submission input now joins fingerprint, attempt, intent, and job identities.
- `ReconciliationRequired` remains typed through the store failure boundary.
- Most create operations compare their semantic idempotency fields.
- Worker acquisition checks job existence, lease expiry, owner conflict, and monotonic fences.
- Worker release requires the recorded owner and fence.
- Delivery has tenant-scoped create, read, persistence, and relationship validation.
- The provider test now observes submitting state inside the provider callback.
- Attempts and submission intents are reopened and checked in the submission test.
- The application still invents no native capability names or second timeline reducer.

These closures do not resolve the P1 publication and authority paths above.

## Independent source inventory

The following nine current files matched the A02 evidence identities:

```text
516f52809cb7a9744a074db69edb3197fbecc52eb5235c791478db3f2762c8ae       346  package.json
054d28ef145e907b5d19c79ee8df090ac4325c32ddcaacaea314516cda8d77c2     11322  src/application.ts
3902ffa867cf6a1e082d7b154b43bcb385d5b948a42e8f321347e6fa00c24a36     15908  src/domain.ts
752e17b551b1a21a593a5c954830d425b26d0872f4459344be2936ad6ce93356       110  src/index.ts
1883c721dbe154735d986f5be80b45a118be617d616d0c5aa785ef0be59ccbab      6192  src/schema.ts
fd9a01e6c3077d26908e83e5f31be6eaa5915d9f8b917caf079a5cc065c68b1e     84065  src/storage.ts
d89c416f817ade694b3557998baaa8336f8cb66ad7f598a13d246c786c27b24d     16220  test/application.test.ts
9f8166a1e35b751cc8f0aa562433ca5158af80d11f4a647259d225c1b2b6e59f       450  tsconfig.json
507e8e8cf10d5ac564f048aaf274a701c03b0203d93f2aa212171f6ade8cce5a       342  vitest.config.ts
```

The A02 evidence document also matched its supplied SHA-256:
`54d55764a08371e101148c16313aec5d4e74d818f108a35e273abeb9176f2891`.

## Executed checks

The raw checkout has no application-local dependency links.
The literal typecheck and Vitest commands therefore failed at module resolution.
Oxlint and Oxfmt completed successfully in the raw checkout.

The reviewer copied all nine files to a temporary directory.
Every copied file was hash-equal to the source inventory above.
The temporary package linked only the repository's installed dependencies.

The following isolated checks passed:

- TypeScript typecheck.
- Vitest: one file and six maintained tests passed.
- Oxlint over `src` and `test`.
- Oxfmt check over `src` and `test`.

Six additional disposable canaries passed their defect assertions:

1. Direct native schema mismatch promoted, then failed on read.
2. Registered mapping-schema mismatch promoted, then failed on read.
3. Record 1,025 promoted, then failed on read.
4. `close` released the lock before a pending accepted read finished.
5. Failed ownership publication allowed another tenant's later claim.
6. Direct native source mismatch promoted and reopened successfully.

The canaries used temporary directories and one fake typed native bridge.
They did not modify application source or invoke an external system.

## Scope

This review covers the bounded filesystem application source only.
Authentication and actor policy remain injected boundaries.
The review does not qualify native ownership, provider delivery, crash durability, or product acceptance.
