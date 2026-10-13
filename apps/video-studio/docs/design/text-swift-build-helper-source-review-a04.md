# Generic Swift build helper source review A04

## Result

`prepare_swift_build_a04.py` closes both A02 findings and the remaining A03 join gap.

I found no P1 or P2 in the reviewed helper source.

The helper is source-ready for the separately reviewed bounded invocation against Swift A15.

This was a source-only, same-model-family review. I did not invoke Python, the helper, `swiftc`, any control, or any produced executable.

## Closed manifest joins

The A02→A03 changes enforce the required whole contract:

- `sharedSourceSha256` is required;
- its value must name a manifest row;
- that row must appear in both producer and PNG-control compile units;
- `sourceControls` must equal the canonical four-control order;
- the duplicate PNG compile-unit lists must be identical;
- the duplicate PNG schemas must be identical;
- exactly four `*ControlSource` keys are allowed;
- each semantic control key must name its canonical source file.

The A03→A04 repair also requires `compileUnits.control[0]` to equal `png-consumer-control.swift`.

That direct equality joins the PNG primary with `pngConsumerControlSource`. A failed-publication primary can no longer occupy the PNG slot.

## Swift A15 compatibility

The frozen A15 manifest satisfies every reviewed condition:

- package `feasibility-swift-a15` matches the selected source directory;
- `sourceSha256` names the first producer unit, `probe.swift`;
- `sharedSourceSha256` names `png-consumer-shared.swift` in both required unit lists;
- the PNG primary and `pngConsumerControlSource` both name `png-consumer-control.swift`;
- both PNG unit lists equal `[png-consumer-control.swift, png-consumer-shared.swift]`;
- both PNG schema declarations equal 3;
- all four source controls and semantic caller keys use the canonical order and filenames;
- every compile unit names a manifest source row.

The A15 manifest producer remains `independent-swift-coretext-a14`. That value matches the unchanged producer report literal.

## Preserved helper boundaries

A04 changes no compiler command, path ownership, timeout, sealing, or publication behavior from A02.

The caller must provide the package, manifest filename, manifest SHA-256, and fresh attempt path. The helper has no package fallback.

The helper launches only the fixed `swiftc` path. It never launches a produced binary.

The held attempt-directory descriptor still protects descriptor-relative logs, binaries, reports, and the publication seal.

Source rows, manifest bytes, helper identity, Python path, compiler path, SDK records, and output identities receive before-and-after checks.

Compiler logs and binaries retain their documented post-run caps. Module-cache and temporary-directory growth remain disclosed limits.

The operation label now identifies `manifest_authorized_swift_build_preparation_a04`.

## Remaining gates

1. Preserve A04 and this review unchanged.
2. Invoke A04 only through the separately reviewed bounded typecheck or build runner.
3. Verify the saved report, publication seal, source closure, compiler results, and binary contracts after execution.
4. Run all four A15 controls before any native producer execution.

This review does not establish compiler success, executable identity, control success, or native feasibility.

It establishes no product integration, playback, hearing, creative acceptance, or full-film result.

## Reviewed identities

| File | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `prepare_swift_build_a04.py` | 1,501 | 64,953 | `ba632ed73005d8c3f870d4b7886c3057ae80405071c4f2154469fe090c195886` |
| `prepare_swift_build_a03.py` | 1,499 | 64,809 | `3a46a18a4039e1e0a61e0b03bc49de110179827385995c83250b0dea96630276` |
| `prepare_swift_build_a02.py` | 1,463 | 63,056 | `7726f1f4a0563009836d003443e0482348715829c02badca287056705930c95a` |
| `feasibility-swift-a15/source-manifest-a15.json` | 250 | 11,656 | `0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e` |

The preserved A02 review remains SHA-256 `e3cc82952b09228090cf4659fb623f8b2cc772eac960a6231182621bd341d47f`.
