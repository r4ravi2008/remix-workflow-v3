# Rust producer runner A09 parent source review

Rejected before compilation. Four P1 groups and four P2 groups remain.

Root reviewed the complete A08-to-A09 library and launch changes. Root also reviewed the focused, extension, recipe, README, contract, schema, fixture, and entrypoint changes. Unchanged source inherits the prior complete A08 read.

The separate root read-only helper measured 463 files totaling 130,517,701 bytes. All nine identity fields and all contents matched before and after. It parsed the measured bytes and checked 27 explicit import edges across 23 Rust files.

The 15 source rows total 382,092 bytes. Their framed aggregate is 95610ac0eac8f154ab32b199d1a94c7c125d0dc2061c53e3fe317efabda97aee.

The 102 external tuples total 10,651,616 bytes. Their framed aggregate is 2f8638e74a0a313cb3857b45b6668f617889cb2509b512c62061d4d2d500ee7f.

The measurement helper did not import project code or the rejected process utilities. It executed no compiler, controls, authorization, or native producer.

## P1 groups

1. In lib.rs:2875, a saved stopped wait status can make reap_completed true after unresolved termination. Stopped and consumed terminal statuses need separate fields and predicates.
2. In lib.rs:2260, Drop performs one bounded retry and then releases the last owner. The early-terminal branch at 2984 also fails to mark the child reaped. It can signal an already-reaped, potentially reused PID. Ownership must survive unresolved cleanup; already-reaped children must never be signalled again.
3. In lib.rs:3043, the REVIEW gate follows the last review verification. The mutation then occurs before SIGCONT without another review read. Rejoin the sidecar, root, and peer identities after the gate.
4. The executable replacement rows allow authority-drift codes although loaded-image validation returns vnode ambiguity first. The cwd replacement row rejects before spawning but requires a started and stopped child. Align each fixed row with its actual boundary and saved code.

## P2 groups

1. Direct kill errno is not captured. The ESRCH helper receives a fabricated retry flag, and its delivery fact controls retry. Capture result and errno together; derive delivery and retry decisions separately from those observations.
2. Truncation and cap paths discard the shared region predicate result. The zero-result path captures errno after other operations. Make predicate decisions causal and capture errno immediately after proc_pidinfo. Keep the per-call elapsed admission limit explicit.
3. Typed controls save changed paths but never compare each path with the declared variant. Their result gives only generic rejection. Bind the expected single changed path and rejection cause to each fixed variant.
4. The fixture still lists three review variants; the source, recipe, and schema list five. Correct only the successor fixture.

## Disposition

Root read the complete 8,040-byte peer report. Its SHA-256 is 4e0ec472e6a708108f9d5fc60f7915fd94583c56d24a4b2585dd1f427d70113b. The independent peer reproduced all current source and external rows and both aggregates.

Preserve A09 unchanged. Prepare one A10 source-only repair against these eight consolidated groups. Preserve the finite schedule. Do not add probes or unrelated test groups.

No build, passing controls, native output, product integration, WATCHED, HEARD, or creative approval is established.
