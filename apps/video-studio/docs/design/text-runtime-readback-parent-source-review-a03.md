# Runtime snapshot parent readback A03 source review

Status: source-only independent review. The A03 reader, preflight, output, and
child processes remain unexecuted. No import, helper, compiler, native, media,
GPU, Resolve, or control process ran.

## Reviewed identities

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| A03 reader source | 28,044 | `857724047478e614389f7d93de3f4d8d7cca906d432eb3aa0845982b99c8f810` |
| A03 rationale | 2,615 | `360848409a85f6dc3390d532ce37dec3df5a816bbd9985bf7d0499edf12878d4` |
| A02 to A03 normalized patch | 9,422 | `fa57a5619e42cae7fd7c3d55b7cdb8b09d5bba3d7241e9f1f2c6528e0f0c6799` |
| A02 source | 25,593 | `660b4871aab6381ceb3ae3905749f9fd9b99a51dc076e9eb7bb514198aa7e093` |
| A09 report | 2,837,530 | `7a43e5606a49bab8d949444707a132b102326cb86d6236e512e0160ac5dd29e8` |
| A09 historical parent preflight | 2,643 | `a812ef5cbdf9c6fd4d9f71c608e9c610779184da70e8718ba7d5db0652a63f54` |
| A02 independent source review | 7,569 | `46acd18dac2300508328711eadb638c0988f3efcc80bd7151e207910c703c918` |

The A03 preflight and output paths are absent. The A09 report remains an
unqualified schema-4 filesystem observation, not runtime or native acceptance.

## Disposition

A03 closes the A02 invocation P1 and the historical-execution P2. One source
authority P2 remains. A03 is not ready for a readback acceptance claim until a
root-created launch receipt seals the current preflight and fixed reader
identity without entering the reader's own hash closure.

## A02 findings closed

The A03 source separates `sys.argv` and `sys.orig_argv` at lines 24–25 and
190–205. It requires the script-only `sys.argv` and the full fixed
`python3 -I -B script` `sys.orig_argv`. It records both in live reader facts.

The A03 schema-3 preflight removes the current `attemptAbsent` field. Its
`currentAttempt` binds the existing A09 report path, existence, report hash,
and completed unqualified state. Its `historicalA09Preflight` binds the old
pre-execution preflight path, bytes, hash, state, and `attemptAbsent=true`.
The reader remeasures that historical file before readback.

The output now has a separate `readerExecution` object. It records parent
readback completion and explicitly records that the snapshot tool was not run
and no snapshot execution evidence was bound. It no longer invents a tool exit
code, captured output, or helper execution result.

The normalized patch contains these intended changes only. It preserves the
A09 report, seven source paths, bounded descriptor reads, explicit `require`
checks, fresh source rows, and unqualified output boundary from A02.

## Remaining P2: preflight source authority needs an external seal

The A03 preflight validates its exact schema-3 keys, seven unique expected
paths, reader facts, current report identity, historical A09 preflight, and
authorization flags. It remeasures every source row and returns fresh rows
with identities. The A03 source still accepts the seven row hashes and the
`readbackSource` hash from the current preflight itself.

A03 does not contain a fixed SHA-256 for the current preflight. A rewritten
preflight can therefore supply different hashes for the helper, contract,
rationale, overlay, diagnostic, and review rows. The reader will measure those
current files and accept them. The fixed report, diagnostic, and overlay
constants protect only the report path and the two separately fixed inputs.

This is a source-closure P2 when the readback result is used as an authority
for the seven-row closure. The design below closes it with an external root
launch receipt. It does not add the receipt hash to the preflight or reader
output, so it avoids a self-hash cycle.

## External root launch receipt

The root launcher should create one private, exclusive receipt after authoring
the A03 preflight and before launching the reader. The receipt can be named
`readback-launch-receipt-a03.json` and should use a new fixed schema.

Its required fields are:

```text
schema: 1
state: "root_sealed_parent_readback_launch"
readerSource: {path, bytes, sha256, identity}
interpreter: {path, bytes, sha256, identity}
readerArgv: [script_path]
readerOrigArgv: [python_path, "-I", "-B", script_path]
preflight: {path, bytes, sha256, identity}
childSnapshotInvocation: [python_path, "-I", "-B", helper_path]
report: {path, bytes, sha256}
authorizesComparator: false
authorizesNative: false
loadedImageAttestation: false
creativeAcceptance: false
```

The receipt excludes its own path, bytes, hash, and identity. The receipt also
does not claim loaded-code attestation. It binds launch inputs and the expected
interpreter command only.

The root launcher must perform this order:

1. Read and hash the fixed A03 source through one bounded descriptor. Recheck
   its pathname and descriptor identity before closing it.
2. Read and hash the fixed interpreter executable through a bounded descriptor.
   Record its path, bytes, SHA-256, and identity. Do not infer loaded images.
3. Read the root-created A03 preflight through a bounded descriptor. Validate
   its schema, key set, seven rows, reader facts, and all false authorization
   fields. Compute the raw preflight bytes, size, SHA-256, and identity.
4. Reopen the A03 source, interpreter, and preflight. Require the exact source
   hash, executable hash, preflight raw hash, and exact two argument vectors.
5. Write the receipt with exclusive creation, canonical bounded JSON, flush,
   descriptor fsync, and parent-directory fsync. Reopen it and verify its raw
   bytes and identity. Only then launch the A03 reader.

After the reader exits, the root launcher must reopen and rehash the receipt,
reader source, interpreter, and preflight before accepting A03 output. It must
also require the A03 output's `reader`, `preflight`, `readbackSource`,
`historicalA09Preflight`, `currentAttempt`, and `readerExecution` objects to
match the receipt's fixed inputs. The receipt remains external evidence and is
not copied into A03 output.

The launch receipt is a root fact about the files and requested command. It is
not proof that the requested source was loaded into the running interpreter.
The A03 live reader facts and the root receipt must preserve that distinction.

## Descriptor, publication, and limits

A03 retains the A02 residual boundary for rootless paths. It holds the final
file descriptor and checks file identity, but it does not hold parent
directory descriptors for the unit preflight, report, or source rows. The
receipt's root checks reduce substitution risk; they do not create an atomic
filesystem snapshot across the reader launch.

A03 output publication remains exclusive, full-write checked, flushed, and
fsynced. It still lacks a held parent-directory descriptor, final output
reread, directory fsync, and a structured partial-output receipt. These are
publication durability limits, separate from the source-sealing P2.

No A03 file establishes package imports, loaded interpreter images, native
dependency closure, comparator execution, native text execution, provider
origin, playback, hearing, or creative acceptance.
