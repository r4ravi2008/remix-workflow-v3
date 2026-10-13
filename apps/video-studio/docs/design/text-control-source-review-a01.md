# Parent pure-control source review A01

The parent read all 346 source lines and the complete A06 contract before execution.
The runner SHA is `c4588c78263c159c08631ee608b1720a3aa7fceef21ed7b7bf377908684e10d2`.
The runner remains unexecuted. Preserve it and repair a separate A02.

## Execution blockers

1. The synthetic raw buffer never fills its 51 padding bytes with `0xA5`. Its positive orientation case therefore contradicts its own required check.
2. The optimizer control accepts any nonzero exit with an existing report. Require exact `optimized_python` failure, a failed bounded report, and the expected exit code. Verify the actual helper and runtime identities before subprocess execution.
3. `license_check` reproduces license validation in the harness. Exercise the helper's actual bounded reader with the frozen OFL count/hash, and test the real `verify_license` positive path. Do not count a duplicated harness predicate as validation of the helper.
4. The declared orientation mutation schedule lacks executed negative controls. Add raw-row, padding, canonical-byte, PNG-alpha, and PNG-dimension controls. They remain synthetic observer controls and never become native evidence.
5. Actual-proof mode does not consume a runtime binding or bind imported helper bytes. Verify the frozen runtime, helper hashes and runner hash before loading validation modules. Record those identities and mode in the report.
6. Unexpected baseline/helper exceptions can escape without a bounded failure record. Preserve completed control results, causal error, and before/after canonical input identities when a later control fails.

Keep canonical inputs unchanged. New fixtures and reports use one fresh exclusive directory.
The valid 2,049-by-2,047 padded request remains positive at 4,225,008 bytes.
The two undercharged requests remain negative. No mask allocation or product admission is proved by arithmetic alone.

## Observer labeling follow-up

The A04 helpers close the second pathname resolution and false execution/exclusivity scope.
For exact closure against the independent A03 review, add successful-path fields
`producerBinaryPathIdentityEstablishedHere: true` and `exclusiveRunDeclaredBySidecar: true`.
Keep actual producer execution, run exclusivity and source lifetime false.
Clarify the sidecar name gate so its documentation matches its actual version rule.

These are source findings, not failed executed controls. Native text, product integration,
watching, hearing and creative acceptance remain unverified.
