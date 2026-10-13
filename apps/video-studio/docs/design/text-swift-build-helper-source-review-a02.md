# Generic Swift build helper source review A02

## Result

`prepare_swift_build_a02.py` still needs a preserved successor before it builds the final Swift package.

I found no P1. Two P2 manifest joins remain incomplete.

A02 closes the attempt-root, preflight, and authority-label findings from A01. It also adds useful schema and binary-contract records.

This was a source-only, same-model-family review. I did not invoke Python, the helper, `swiftc`, any control, or a produced executable.

## P2 — duplicate PNG contracts can disagree

The manifest describes the PNG control in two places:

- `compileUnits.control` with `controlReportSchema`;
- the matching `sourceControls` entry with `sourceControlReportSchemas`.

`validate_manifest` accepts positive schemas and valid ordered units for both locations. It never cross-joins the duplicate PNG primary.

The same primary can therefore receive different schemas or different ordered units. Both contradictory contracts can pass `manifestContract`.

The helper would then build two binaries from the conflicting declarations. `binaryContractsMatched` only proves that execution followed those declarations.

Require all these relationships:

- the PNG primary appears in `sourceControls`;
- its source-control units exactly equal `compileUnits.control`;
- its source-control schema exactly equals `controlReportSchema`.

Keeping two separately sealed PNG binaries is acceptable. Their declared source and report contract must be identical.

## P2 — the shared and PNG caller bindings are not exact

`callerBindings.sourceSha256` is required and matched to the first producer Swift unit at `prepare_swift_build_a02.py:412-414`.

`callerBindings.sharedSourceSha256` is never required or validated. It is only copied if its value happens to name a manifest row.

The `*ControlSource` check at lines 444-459 compares an unordered value set. It does not bind `pngConsumerControlSource` to the PNG primary.

A manifest can omit the shared binding or swap semantic control keys while still passing the manifest contract.

For the selected text package, require these exact joins:

- `sharedSourceSha256` names one row shared by the producer and PNG-control units;
- `pngConsumerControlSource` equals `png-consumer-control.swift` and `compileUnits.control[0]`;
- `failedPublicationControlSource` equals `failed-publication-control.swift`;
- `persistedOutputBudgetControlSource` equals `persisted-output-budget-control.swift`;
- `terminalPublicationControlSource` equals `terminal-publication-control.swift`.

Reject missing, extra, renamed, or semantically swapped `*ControlSource` keys. A generic value inventory is insufficient for this fixed four-control package.

A14's intended filenames may satisfy these rules. A02 does not enforce them.

## Closed A01 findings

A02 retains one descriptor for the fresh attempt root. It checks device, inode, type, and mode against the pathname.

Compiler logs and JSON records use descriptor-relative exclusive creation. The helper checks the attempt root before and after every compiler step.

The final preflight observation must equal its initial identity, byte count, and SHA-256. The report and publication seal retain that fact.

The helper now requires positive producer, PNG-control, and source-control report schemas. It preserves ordered binary contracts in the report.

The helper records explicit false claims for loaded helper, loaded Python, loaded compiler, complete compiler dependencies, and complete SDK contents.

The retained SDK scope is limited to the invocation path, resolved directory, `SDKSettings.json`, target, and command arguments.

The direct child executable remains the fixed `swiftc` path. Produced binaries are read and sealed, never launched.

Each compiler command gets a separate exclusive log. A timeout sends `SIGTERM`, escalates to `SIGKILL`, and reaps the compiler process group.

Successful binaries require a thin arm64 executable Mach-O, one `LC_UUID`, a bounded descriptor hash, and stable metadata.

Final binary and log observations must equal their first successful observations. Source, manifest, tool, SDK, helper-path, and Python-path observations repeat afterward.

The helper still discloses post-run-only log and binary caps. It also discloses unbounded module-cache and temporary-directory trees.

## Scope limits

The held-directory checks are endpoint observations. They do not attest every transient pathname state during `swiftc` execution.

The helper does not attest compiler-opened source descriptors, loaded interpreter bytes, loaded compiler images, compiler dependencies, or complete SDK contents.

A13 is intentionally incompatible with A02's filename caller-binding contract. A qualified successor must use the final A14 manifest.

## Required successor gate

1. Preserve A02 and this review unchanged.
2. Cross-join both PNG contract declarations.
3. Require the shared source and semantic PNG caller bindings.
4. Freeze and re-review the successor against A14.
5. Run no compiler until that review is green.

This review grants no typecheck, executable build, control, native framework, product, playback, hearing, or creative acceptance.

## Reviewed identity

| File | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `prepare_swift_build_a02.py` | 1,463 | 63,056 | `7726f1f4a0563009836d003443e0482348715829c02badca287056705930c95a` |

The preserved A01 review remains SHA-256 `bb33c15e52684a40aa03fdc071217c6a940310cbe64982e9cf4525de58e2ac53`.
