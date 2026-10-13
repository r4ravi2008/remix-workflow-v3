# RoleIndexV2 launcher A01 parent source findings

Root read all 1,383 frozen source lines, the complete final contract, rationale,
and three-row manifest. All three current package files match their declared
bytes and hashes. The source SHA-256 is
`f238c02a6e8efc6543b575d578a1d22c8a83d3352dd26f76c4438aec4ad6614d`.
The source remains unexecuted. No compiler, binary, vector, control, review
marker, or runtime-closure marker was created.

A01 is preserved and requires a source successor before execution.

## P2: control success uses a reduced projection

`validate_decoder_control_report` checks the passing state, count 74, schedule
hash, and vector hash. It never validates the 74 result identities, order,
statuses, rejection fields, complete top-level keys, canonical bytes, or exact
scope/model fields. A count-preserving wrong result table can pass.

Validate the exact frozen schedule and each result's closed field set and
types. Join all input observations and vector identities. Check separate model
identities and the complete scope. Preserve the source's lack of authority.

## P2: failed process and stage evidence is lost

`process_success` raises after `run_bounded` returns its process record. The
failure publisher receives neither that record nor completed stage results.
Log publication can also raise before the record returns. The failure record
then lacks launch, capture, termination, and reap observations. Unexpected
exceptions receive main's constant `dispatch` stage instead of the current
handler stage.

Retain stage and process records in caller-owned progress before operations.
Publish causal failure and partial-log facts without dropping the cleanup
record. Storage failure may still prevent publication; do not infer success.

## P2: exceptional cleanup depends on a live leader

The capture exception handler signals the process group only while the direct
leader is running. An exception after leader exit can leave descendants with
retained pipes unsignaled. `BaseException` also bypasses that handler. Final
wait can immediately return for a dead leader without cleaning that group.

Run bounded process-group cleanup for every post-launch abnormal exit,
including cancellation and a leader that already exited. Keep descendant
reaping unverified and direct-child reaping separate.

## P2: Mach-O facts lack one observed-file join

`observe_macho` hashes one descriptor observation, then `macho_uuid` reopens
the pathname. It joins neither descriptor identities nor retained raw bytes.
The resulting hash and UUID can refer to different observed files.

Parse the Mach-O fields from the same retained bytes used for hashing, or
explicitly join the complete observations. Keep launch atomicity unclaimed.

Independent review is pending. These findings concern the fixed source paths
and failure behavior. They do not require a new generic runner framework.
