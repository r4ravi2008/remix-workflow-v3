# RoleIndexV2 launcher A02 parent source review

Disposition: preserve A02 unexecuted. Two P2 regressions require a narrow successor.
The five original finding groups are addressed, but cleanup timing and attempt
ownership still violate the retained contract.

Root read the complete 1,150-line source delta against the previously fully read
A01 source. Root also read the complete final contract, rationale, manifest, and
current capture function. All four package rows match. An ordinary data-only
patch reconstruction checked all 34 hunk offsets, contexts, and counts. It
reproduced every final source byte. Python difflib emitted a different equivalent
patch grouping; that initial byte comparison failed before any review was saved.
No target module was imported, compiled, or executed. No attempt or authorization exists.

Source: 82,212 bytes, SHA-256
`22fce34292ea05d457c1d0698ac67d5db102d4d56ca4df0698a71dcd3511517f`.
Manifest: SHA-256
`c62e7bd6e2f207db85488091bbb9e7af83b633c21c969f039f223cc173535d65`.

## P2: the final drain happens before KILL

The capture loop starts TERM cleanup at termination, but no longer sends KILL
when TERM_GRACE expires. It waits until TERM_GRACE plus FINAL_DRAIN, then breaks.
The finally block sends KILL and immediately closes the remaining streams.
Consequently the declared final drain runs before KILL. A retained writer can
remain alive for the four-second combined interval, and output after KILL does
not receive the declared two-second drain.

Restore KILL at the TERM deadline and retain the bounded post-KILL drain before
closing streams. Exceptional capture cleanup must still attempt the group after
a dead leader, catch BaseException, retain partial facts, and keep descendant
reaping unattested. This repair requires no new process mode or framework.

## P2: failed attempt creation can write into an existing attempt

The main prepare_attempt exception handler observes the fixed attempt pathname
and writes failure-a02.json whenever it is a directory. FileExistsError is one
such path. No fact establishes that this invocation created that directory.
A repeated invocation can therefore add a failure file to a preserved earlier
attempt despite failing exclusive creation.

Record directory ownership immediately after a successful exclusive mkdir.
Write an in-attempt preparation failure only when this invocation created the
attempt. Otherwise retain only the sibling preparation failure. Do not delete,
reuse, or write into an existing attempt. Before-launch absence checks mitigate
the initial fixed run but do not repair this reusable failure path.

## Repairs that pass scoped static review

The full canonical decoder report has closed top-level and nested shapes.
All 74 results join ordinal, identifier, category, expectation, status and typed
mutation/model fields to the immutable schedule. Ten current input identities,
model identities, vector, publication and all scope flags are joined.

Caller-owned progress now retains stage and process records before operations.
Mach-O UUID parsing and hashing use one retained byte sequence. The two vector
commands receive separate exclusively created temporary directories.

This review establishes source observations only. Compiler compatibility, Rust
controls, vector bytes, independent decoder controls, loaded images, native
rendering, watching, hearing, and creative acceptance remain unverified.
