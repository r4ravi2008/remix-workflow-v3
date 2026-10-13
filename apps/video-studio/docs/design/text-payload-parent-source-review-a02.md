# Payload parent source review A02

The parent read the complete 1,337-line module, complete binary, rationale, schema, and ledger.
A02 remains unbuilt and unexecuted. A01 is preserved.

The reader now uses one opened regular file and an exact boxed byte allocation.
The reader checks stable descriptor metadata and all eleven frozen hashes before deserialization.
The aggregate correctly excludes diagnostic headers from its lower bound.
The actual BTree insertion observer limits its claim to requested allocator layouts on the current thread.
These source repairs close those parts of A01.

## Remaining source blockers

1. `FailureFromReport` lacks `Serialize`, but `stream_json` requires that trait.
   This is an apparent compile blocker identified without a compiler run.
2. `json_observation` still calls uncapped `serde_json::to_vec` and `to_string`.
   Both buffers coexist while parsed and cloned owners remain live.
   Admit encoded length and buffer capacity before allocation or growth.
3. Map-probe failure loses completed insertion observations and the failing counter.
   Preserve completed observations and causal counter evidence in a successor.

## Execution authority gate

The report does not bind the source-copy manifest or its executable.
No source-closure before/after execution check exists in A02.
An independently frozen runner can supply those checks without a circular binary hash.
Review its source before building, then seal the actual build and binary before execution.
Path-level identity must not be described as a loaded executable or physical-memory proof.

The inherited A01 `originalBuildManifestSha256` field contains the executable SHA.
Correct the interpretation in the successor without editing the preserved A01 record.
The module also retains four unused imports identified in the independent A01 review.

The streamed output cap closes the final serialized report duplication.
Flush and synchronize the opened output descriptor when claiming preserved publication.
The executed report must keep source authoring status separate from measurement success.

## Disposition

Create A03 as a separate source-only successor.
Do not build, format, typecheck, execute, or integrate A02.
This review establishes no product admission, native text result, hearing, or creative acceptance.

Reviewed module SHA-256: `4b6250fa20393c76f5235e5af78fae0bc5a82d54ba89b59e00a1ced23d9eb2ea`.
Reviewed binary source SHA-256: `481e2435095c2e6e1b952170638d28053105578dc5e9c039f6ba417a9a73da77`.
