# Runtime readback A03 scoped evidence review

Status: bounded, read-only review of the one completed A03 reader attempt.
This review did not run or import the reader, a helper, a child, a compiler,
codec, native framework, media process, GPU process, or Resolve.

## Scope disposition

The saved evidence supports a scoped filesystem result:

```text
root_external_launch_and_current_readback_passed_unqualified
```

Within that scope, I found no P1 or P2 finding. The root launch receipt,
external preflight seal, reader output, and root post-check agree on the fixed
reader source, interpreter, exact arguments, current A03 preflight, A09 report,
seven source rows, and current regular-file observations.

This result remains unqualified. It does not establish loaded code, atomic
launch, parent-directory retention, native execution, comparator execution,
audio or visual acceptance, playback, listening, or creative approval.

## Reviewed evidence

| Evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| root launch receipt | 2,480 | `681dd4515dab592477336d21da9f2a75a791669a41ca302890b8d17f7514c6c0` |
| root-created A03 preflight | 4,105 | `d24e5d6222511f6044a023df2e86465de429333a209654ceff7bd8faba042d90` |
| reader tool result | 1,092 | `33e1df50d0dcf78785d185a57d5a341d398b0832139f31dcc19e8da69d8f6d79` |
| A03 execution output | 870,446 | `931a6359701c8586341763c6e1128e0360c1367fc54f2e7e4d23504bbb147e8b` |
| root post-check | 858,951 | `cb04626dd19ec505cf5f1bb285e9bab35dc8fb8a9069da59fb65196349d30545` |

The reviewed fixed identities are:

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| A03 reader source | 28,044 | `857724047478e614389f7d93de3f4d8d7cca906d432eb3aa0845982b99c8f810` |
| Python 3.12 executable | 18,058,560 | `4158f03e1bae2b759f25a1ba1fbdab8bfb7161eba4caf22e28f0915986625bbc` |
| A09 runtime report | 2,837,530 | `7a43e5606a49bab8d949444707a132b102326cb86d6236e512e0160ac5dd29e8` |
| historical A09 preflight | 2,643 | `a812ef5cbdf9c6fd4d9f71c608e9c610779184da70e8718ba7d5db0652a63f54` |

The receipt has schema `1` and state
`root_sealed_parent_readback_launch`. Its authorization flags are all false:
`authorizesComparator`, `authorizesNative`, `loadedImageAttestation`, and
`creativeAcceptance`. Its reader vectors are exact:

```text
readerArgv = [readback_runtime_snapshot_a03_parent.py]
readerOrigArgv = [python3, -I, -B, readback_runtime_snapshot_a03_parent.py]
```

The receipt binds the 4,105-byte preflight raw SHA and the existing A09 report
raw SHA. The root post-check reports both receipt and preflight identities as
matching those saved files.

## Reader result

The tool result records exit code `0`, wall time `0.356286625` seconds, and the
exact command with Python `-I -B`. Its output identifies the 870,446-byte A03
execution file and reports:

```text
installedRows = 1548
fixed_measured_divergence = 45
strict_declared_match = 995
independently_observed_undeclared = 508
inputOpens = 11000
readBytes = 69901069
```

The A03 execution file has schema `3` and state
`parent_current_files_readback_passed_unqualified`. It records:

```text
readerExecution.readbackCompleted = true
readerExecution.snapshotToolExecuted = false
readerExecution.snapshotExecutionEvidenceBound = false
authorizesExecution = false
comparatorExecuted = false
packageImports = false
nativeExecution = false
loadedImageAttestation = false
providerOriginVerified = false
divergenceCauseVerified = false
sourceRowsAfterMatched = true
```

The seven expected A09 source rows retain their fixed paths, sizes, and hashes.
The current attempt retains the exact A09 report path, size, SHA, and state.
The historical preflight retains `attemptAbsent=true`, its fixed path, size,
SHA, and prior state. The execution record reports all 1,548 installed rows
and 45,567,887 installed bytes.

## Root post-check

The root post-check has schema `1` and state
`root_external_launch_and_current_readback_passed_unqualified`. It records:

```text
externalPreflightSealMatched = true
readerArgumentVectorsMatched = true
readerSourceAndInterpreterMatched = true
freshSourceRowsMatched = 7
rootUniqueRegularFilesMatched = 1562
rootRegularBytesRead = 68299969
```

It retains false values for `authorizesExecution`, `comparatorExecuted`,
`nativeExecution`, `loadedImageAttestation`, `creativeAcceptance`, `heard`,
and `watched`. Its material-limit text correctly excludes atomic launch,
loaded-code identity, held parent directories, and native or audiovisual
acceptance.

I checked the saved post-check table structurally. It contains 1,562 unique
paths. Every row has `path`, `bytes`, a 64-character lower-case SHA-256, and
all nine stat fields: bytes, device, inode, mode, links, uid, gid, mtimeNs,
and ctimeNs. No row has a negative numeric identity field. The sum of all
1,562 saved byte counts is exactly 68,299,969, matching the reported total.

The seven source rows and the fixed A09 report, diagnostic, overlay, helper,
contract, rationale, interpreter, historical preflight, receipt, reader
output, and tool-result identities independently match their current bytes.
The post-check also records the exact reader output identity and tool-result
identity.

## Remaining limits

The tool-result record says `streamSeparationEstablished=false`. The saved
result therefore cannot establish that no stderr bytes existed or that the
reported output was a pure stdout channel.

The root receipt and post-check reduce substitution risk. They do not create
an atomic filesystem snapshot across the last prelaunch observation and the
reader launch. They also do not prove that the interpreter loaded the hashed
reader source or that a particular native image was loaded.

The reader reused the saved A09 runtime report. It did not execute the A09
snapshot helper, and its execution record explicitly says that no snapshot
execution evidence was bound. The result remains a current filesystem
readback against that fixed report.

No comparator, package import, native framework, text raster, media decode,
audio capture, GPU, Resolve, playback, listening, or creative acceptance was
performed or established.

## Conclusion

The root receipt, A03 preflight, A03 output, and root post-check are coherent
for the stated unqualified filesystem scope. The evidence is ready for use as
that bounded input authority, subject to preserving the listed limitations.
