# Application A02 source disposition

A02 remains rejected for integration. Four P1 groups and three P2 groups require correction.
The A02 source, configuration, tests, and author evidence are preserved separately.
The native and provider bridges remain unconfigured.

## Preserved candidate and review

The candidate snapshot is `artifacts/scratch-video-goal-20261005/application-a02-candidate-preserved`.
Its preservation manifest contains 7,537 bytes and has SHA-256 `a9a7b2948926a83f7cbe09c59620c3adf021d84d733c35b334ca1a8c4342792b`.
The manifest covers ten source, configuration, test, and author-evidence files totaling 141,243 bytes.
The fresh peer report is preserved as an additional evidence file.
Its framed aggregate is `38134b6105495e92d2c39d77ac1540100bf1742e07a2340064bd5e603803e6ed`.

ROOT fully read the fresh peer report, `video-studio-application-source-peer-review-a02.md`.
The report contains 11,208 bytes and has SHA-256 `35fb2dfc004d675a7466947922d2f9c3299db08d3c0a9ed8c97362ca5d65056e`.
ROOT also read the author evidence, all six maintained tests, and the relevant ownership, receipt, write, validation, and close paths.
The reviewer matched every source, configuration, and test identity against A02 evidence.

The maintained tests and static checks passed in an isolated, byte-identical package with the repository dependency cache linked.
The raw checkout lacked application-local dependency links, so raw typecheck and Vitest failed module resolution.
This dependency limitation remains distinct from the reproduced source defects.

## Required repair groups

1. Bind native project ownership through trusted provisioning. Caller-selected identifiers and first claims cannot prove existing native ownership. Publish ownership conservatively before tenant state can become visible without its claim.
2. Give native output one verified registration path. Public client imports cannot assert `NativeOutput`. The authoritative mapping controls receipt schema, project, revision, and source joins.
3. Validate collection limits and complete state relationships before each state promotion. A successful operation must not create state that reopening rejects.
4. Fence store closure before awaiting queued work. Reject new work after closure begins. Retain the root lock until all accepted work ends, and make concurrent closure share one owner.
5. Validate persisted worker fences and leases. Validate job, submission-intent, and attempt states as one coherent transition.
6. Compare released timestamps and terminal provider results during idempotent replay. Check exact source-kind and identifier tags at runtime.
7. Admit bounded reads through a retained descriptor before allocation. Keep accepted-byte limits distinct from allocation limits.

The peer used six disposable local canaries to reproduce material failures.
Those canaries include a second tenant claiming a native identifier after the first ownership publication failed.
They also include direct native-output bypass, schema mismatch, record 1,025, and root-lock release before accepted work ended.
The sixth canary stored and reopened a native source that differed from the authoritative project source.
ROOT's targeted source reads support the central authority, write-validation, and close-fence findings.

## Scope and next action

Prepare A03 source corrections and meaningful regression coverage for these seven groups.
Preserve A01, A02, and both reviews unchanged.
Keep actual native, provider, GPU, media, and Resolve execution deferred.
This source disposition establishes no product, watched, heard, or creative acceptance.
The general editor and complete 273-second Panja film remain required.
