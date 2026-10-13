# Generic Swift build helper source review A01

## Result

`prepare_swift_build_a01.py` needs a preserved successor before it builds the final Swift package.

I found no P1 defect in the intended compiler command or Mach-O sealing flow. Three P2 defects leave the build evidence less authoritative than its contract suggests.

This was a source-only, same-model-family review. I did not invoke Python, the helper, `swiftc`, a control, or a produced executable.

## P2 — the attempt root and preflight are not preserved by identity

The helper creates the attempt directory at lines 682-692. It never opens that directory or records its device and inode.

Later logs, module caches, binaries, `preflight.json`, and `report.json` use pathname operations. `O_EXCL` and `O_NOFOLLOW` protect the final file component only.

A parent-directory substitution can redirect later writes or observations. The report has no attempt-root before/after identity check to detect that change.

The helper observes `preflight.json` once at lines 753-755. It never reopens that file or compares its final identity and hash.

Keep a descriptor for the new attempt directory. Use descriptor-relative exclusive writes where practical. Check the pathname against the held directory before and after each compiler step.

Reobserve `preflight.json` before final report publication. Require exact equality with the saved observation.

## P2 — manifest validation omits report-schema and empty-binding joins

`validate_manifest` verifies the ordered compile units and exact `sourceControls` versus `sourceControlCompileUnits` keys. This correctly rejects Swift A12's omitted terminal control.

However, the validator never reads these manifest fields:

- `producerReportSchema`;
- `controlReportSchema`;
- `sourceControlReportSchemas`.

A manifest can omit, duplicate, mistype, or misassign those schema declarations and still produce a successful `manifestContract`.

The caller control-source check at lines 299-303 is also conditional. A nonempty control set with no `*ControlSource` bindings passes because the derived set is empty.

Require positive integer schemas and an explicit filename-to-schema mapping for every produced binary. Require control-source binding equality unconditionally.

The build report should retain this exact ordered mapping. A later execution gate can then join each binary to one declared report contract.

## P2 — helper and Python observations need a narrower authority label

`build_closure` hashes the helper pathname and `sys.executable` before and after the builds. Those observations detect persistent pathname drift.

Python has already loaded the script and interpreter before either observation. The hashes do not attest the bytes which the running process loaded.

The report correctly says the loaded compiler is not attested. It does not state the equivalent helper and Python limitation.

Add explicit boundaries such as:

- `loadedHelperAttested: false`;
- `loadedPythonAttested: false`;
- `helperAndPythonPathObservedBeforeAfter: true`;
- `completeCompilerDependencyClosure: false`;
- `completeSdkContentClosure: false`.

The current SDK evidence binds the invocation entry, resolved directory, `SDKSettings.json`, target triple, and command arguments. It is not a complete SDK header or library closure.

## Confirmed source behavior

The helper has no default package. The caller must provide a safe package, manifest, manifest hash, and fresh attempt name.

The manifest hash is verified before JSON parsing. Duplicate JSON keys fail. Every declared source row is size-capped, rehashed, and checked for inode aliasing.

The ordered producer, PNG-control, and source-control compile units come from the manifest. The producer requires Swift sources followed by one bridging header.

The helper runs only the fixed `swiftc` invocation path. Produced binaries are never launched.

Each build has a separate binary, log, and module-cache path. The subprocess environment is explicit. The compiler target and SDK arguments are recorded.

Timeout handling sends `SIGTERM`, escalates to `SIGKILL`, and reaps the compiler process group.

Successful outputs are parsed and hashed through one descriptor. The parser requires one thin arm64 executable Mach-O and exactly one `LC_UUID`.

The helper repeats binary and log observations before final classification. It also repeats the helper, Python, compiler, SDK, manifest, source-directory, and source-row observations.

The report accurately discloses these limits:

- compiler logs have only a post-run read cap;
- binary size has only a post-run read cap;
- module-cache and temporary trees have no byte cap or recursive inventory;
- the produced binary and native frameworks remain unexecuted.

No additional P2 is assigned to those disclosed limits.

## Required successor gate

1. Preserve A01 and this review unchanged.
2. Bind and recheck the attempt-root and preflight identities.
3. Validate every report-schema and control-source mapping.
4. State the helper, Python, compiler, and SDK authority boundaries precisely.
5. Freeze and re-review the successor against the final qualified Swift package.
6. Run no compiler until that review is green.

This review grants no build, typecheck, control, native, product, playback, hearing, or creative acceptance.

## Reviewed identity

| File | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `prepare_swift_build_a01.py` | 998 | 42,119 | `3b78c6a3fd04ba1776c57f65a5c8112cdef93714d80b6cfd9ed222cd1ea937bd` |
