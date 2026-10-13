# Independent Swift control runner design A02 review

## Status

This is a source-only review of the preserved runner design. It does not
implement or execute the runner, a control, `swiftc`, the producer, or a native
framework.

The reviewed design is:

- `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/docs/design/text-swift-control-runner-design-a02.md`
- 547 lines, 24,867 bytes
- SHA-256 `5934d558839fb2304b17b17bfd15672ea7c1417fd7bea8f3a5d69d4c084c7476`

The reviewed grounding files are the A04 build helper, its source review, the
current A15 source manifest, the A15 source review, and the A15 producer and
control sources. I compared the design's operation names, map, report
schemas, literals, hashes, and stated evidence boundaries with those files.

## Verdict

I found no P1 or P2 in the A02 design. The design is source-ready for a
separate runner implementation review.

The native control gate remains absent. The design correctly limits the result
to four pure source-control observations.

## Closed A04 operation and A15 source join

The design binds `prepare_swift_build_a04.py` SHA-256
`ba632ed73005d8c3f870d4b7886c3057ae80405071c4f2154469fe090c195886` and the
operation `manifest_authorized_swift_build_preparation_a04`. The helper source
uses that operation at line 1023 and launches only its fixed `swiftc` path.
It compiles the producer, duplicate PNG control, and four source controls at
lines 1195-1247. It records the exact binary contract map at lines 1251-1275.

The helper's success state requires all six builds, matching contracts,
successful Mach-O observations, matching logs, and stable attempt-root
observations at lines 1310-1320. Its before and after closure includes the
helper, Python invocation, compiler, SDK settings, manifest, source directory,
and all manifest rows at lines 1335-1368. Report and publication-seal creation
remain descriptor-relative and exclusive at lines 1382-1435.

The A15 manifest is the exact source package named by the design:

| Item | Value |
| --- | --- |
| manifest | `feasibility-swift-a15/source-manifest-a15.json` |
| manifest SHA-256 | `0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e` |
| producer | `independent-swift-coretext-a14` |
| producer report schema | `5` |
| PNG/source-control schema | `3` |
| source-control order | PNG, failed-publication, persisted-budget, terminal-publication |

The four source-control rows and report schemas are exactly:

| Primary source | Schema | Compile units |
| --- | ---: | --- |
| `png-consumer-control.swift` | 3 | `png-consumer-control.swift`, `png-consumer-shared.swift` |
| `failed-publication-control.swift` | 1 | `failed-publication-control.swift` |
| `persisted-output-budget-control.swift` | 2 | `persisted-output-budget-control.swift`, `persisted-output-budget-shared.swift` |
| `terminal-publication-control.swift` | 1 | `terminal-publication-control.swift`, `persisted-output-budget-shared.swift` |

The current source hashes match the design's frozen values:

| Source | SHA-256 |
| --- | --- |
| `probe.swift` | `83e9693be8d53a4bf2a2135f9b6bd643b7be3329129bddf13288ab85ea9f8a01` |
| `png-consumer-control.swift` | `0be8296ca50746f1a4828453568c9bed2646010e46e42e322ac9aa355b408727` |
| `png-consumer-shared.swift` | `22c66166890efc6dfd2e2076d1117139e1b7481f71a4e63df676ab9b2e185866` |
| `failed-publication-control.swift` | `753cd0d4b9f57b5157bc5af299a3839b47d6858bf70a1c643a0de6787d649284` |
| `persisted-output-budget-control.swift` | `a1586e82c51d3aca668eef39437e2132d3c46868346dc153cb87b20d81d6e80c` |
| `persisted-output-budget-shared.swift` | `8c678f77f0aabf2b7072be39d72c9fd9bae7926461c98d211e103bc305428838` |
| `terminal-publication-control.swift` | `5562f922005da7b7811c566b2f93e09f9e24422971cae32587bb9c5bc628e9d2` |

The four A14 producer strings in the design match the current source literals.
The design also preserves the A15 `sourceSha256` and `sharedSourceSha256`
filename bindings and the explicit `pngConsumerControlSource` binding.

## Process, capture, and reaping

The design specifies one child at a time, a fresh process group, `/dev/null`
standard input, concurrent nonblocking stdout and stderr drains, a 15-second
wall limit, a two-second termination grace period, and group reaping. It
rejects output before bytes beyond the retained cap enter the capture buffer.
It preserves bounded stdout and stderr observations after normal exit,
overflow, timeout, cancellation, and process failure.

The design keeps the capture boundary honest. The stdout cap bounds parser
input, but it does not claim a JSON parser heap bound. The report cap bounds
encoded publication bytes, but it does not claim encoder-heap or process-RSS
control. The material risks section repeats these limits. This closes the A01
parser-memory overclaim without introducing a new unproved bound.

The A04 build helper has a separate, explicitly disclosed limit. Its compiler
logs use a four-megabyte post-run read cap, while compiler output may exceed
that cap before rejection. The A02 design relies only on an accepted A04 report
whose log observations passed; it does not call this a live compiler-output
bound.

## Descriptor, path, parent-report, and seal authority

The authority chain is complete at the design level. It requires the explicit
manifest hash before parsing, exact manifest source rows, the A04 operation and
source hash, the accepted A04 state, the publication seal, an independent
parent readback, and an authorization hash over that readback.

The runner derives all four executable paths from the accepted map. No public
function accepts an arbitrary executable path. The runner holds the build root,
the binaries directory, and each selected binary without following symlinks.
It rechecks held-root authority, binary descriptor identity, and binary
pathname identity before and after each child.

The runner's own attempt directory is mode `0700`. Preflight, captured output,
the final report, and the report seal use descriptor-relative exclusive
creation. The final report cannot qualify without a stable publication seal.

The sketch names `ParentBuildEvidence`, `FileObservation`, and related value
types without expanding every nested wire key. Before implementation, the
runner source must give the parent readback, report, seal, and authorization
objects strict duplicate-key, unknown-field, type, and complete-field
validation. This is an implementation gate, not a remaining design finding;
the design already requires those joins and rejects missing or mismatched
fields before a child starts.

## Complete control assertions

The design's strict parser rejects duplicate keys, trailing bytes, missing
fields, extra fields, and type substitutions. It parses a report after child
reaping even when the exit code is nonzero. This allows a valid failed report
to remain evidence while keeping exit status, stderr, and every assertion in
the qualification predicate.

The PNG section covers all five A15 cases, every case field, the exact digest
and expected digest, release and seal observations, callback counts, and the
top-level `allPassed` value. The three other sections cover their complete
ordered case sets, exact schemas, exact producer strings, exact expected and
observed strings, native/file-I/O false fields, entry arrays, and top-level
`allPassed` values.

The corrected tri-state boundary fields remain observations. Missing,
malformed, or incomplete reports leave `controlReportsImageIOUsedFalse` and
`nonPngControlReportsNativeCallsFalse` as unknown. Qualification requires the
corresponding exact typed reports to establish true. A valid report that
exposes the opposite value is retained as a false observation and fails the
control assertion.

The source controls contain no ImageIO, CoreText, or CoreGraphics call. The
design does not turn their source-only callback, evidence-shape, budget, or
terminal-state checks into native publication claims.

## Loaded-image and native boundaries

The design explicitly records `loadedControlImageAttested=false`. It hashes
and rechecks the selected binary path and descriptor, but it does not claim
that the kernel mapped those exact bytes. The design also records
`nativeFrameworkCallTraceAttested=false`, leaves the dynamic-library graph
outside the evidence, and keeps producer and duplicate PNG binaries unstarted.

These are truthful limits. They require a later loaded-image measurement if
the project needs execution identity or native framework-call evidence.

## Remaining verification gates

The following work remains outside this review:

1. Build A15 through the independently reviewed A04 helper.
2. Read back the report, seal, source closure, logs, and six binary records.
3. Review and bind the eventual runner source hash and exact parent-readback
   schema.
4. Run exactly the four source controls and inspect every persisted observation.
5. Keep native producer execution, native PNG publication, CoreText pixels,
   playback, hearing, and creative acceptance as separate gates.

No build, typecheck, control, helper, executable, native framework, GPU,
Resolve, or acceptance operation ran during this review.
