# Rust producer subject adapter A10 evidence peer review

This is a finite saved-evidence review of the A10 Rust source-control attempt. It is a same-model-family, nonblind review. I inspected and rehashed the saved files. I did not import the target package, rebuild it, rerun controls, launch a child, or perform a native, media, product, WATCHED, HEARD, or creative action.

## Bound artifacts

The frozen source package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-subject-adapter-a10/source-manifest-a10.json`

- Bytes: `49981`
- SHA-256: `f9542ea9eda14c8892dc2cb246ee448fd176a60083fb83d9f5d8b3b1dbaa06fe`
- Package rows: `14`
- Package bytes: `255410`
- Source aggregate: `9c7baa1763de48c3317436411c78ad0671b4e1561be1060844fa5a822e5b74b0`

I rehashed all 14 package rows. Every declared byte count and SHA-256 matched. I recomputed the source aggregate from the documented domain, NUL terminator, big-endian row count, total bytes, sorted UTF-8 paths, row lengths, file sizes, and raw SHA-256 bytes.

The manifest binds 65 external rows totaling `13360550` bytes. Every external path, byte count, and SHA-256 matched. The independently recomputed external aggregate is `4653961bd303da6e6df22d6945a3fb455bf146625ba1137084e7668ca640c900`, matching the manifest.

The manifest remains a source-package identity with state `source_only_uncompiled_unexecuted`. The later attempt is the separate saved execution record. I do not treat the package state as a claim that the later attempt did not run.

## Saved attempt and command results

The attempt directory is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-subject-adapter-a10-attempt-a01`

- `preflight.json`: `109114` bytes, SHA-256 `c11f4ab1a82e6b0dc123c2ce9520482c09eea596b1b530be7ac3a32197cc0c08`
- `report.json`: `326218` bytes, SHA-256 `20192057764e854cbc3ba60e1961f1d7a7f2bd57d158b86372597201b4aba82e`
- `parent-actual-readback-a01.json`: `114635` bytes, SHA-256 `821fada91bc1a20a424d5b7e2137f853bde85cc8f8d8fa48bb82750b8ac1ca7c`
- `independent-decoder-readback-a01.json`: `1688187` bytes, SHA-256 `2f43f8a4fcc15e1297c15f543a47327cded8091a410e296a9dc1e911e8d86b38`

The saved report states `source-controls-passed`, `compiled=true`, `executed=true`, and `controlsPassed=true`. Its three commands are the fixed library compile, harness compile, and no-argument control invocation. Each returned `0`, reaped successfully, timed out false, overflow false, and had no unclosed streams. The saved parent readback records PIDs `85717`, `85718`, and `85736` as reaped and absent.

The preflight command list and report command list are identical. The parent readback records the reviewed fixed command, working directory, and ten-variable environment. The report binds the fixed compiler and existing dependency archives. It does not invoke Cargo resolution or a native producer.

The library stderr is `1288` bytes with SHA-256 `c6456916e6aea518a871f9b65bfbffff0c89b9247840f6ec6e1c42e5782a97f4`. It contains three ordinary warnings: one unused import, one unused variable, and one unused function. Harness and control stderr are empty. The warnings do not change the saved return-code or control result, but they remain part of the evidence.

The report has `177` input rows totaling `89487716` bytes. I compared preflight rows with report `inputsBefore`, report before and after rows, and the parent current rows. I rehashed every current input file and checked all nine recorded identity fields. All 177 rows matched. The report `inputsMatched` field is true.

The four generated outputs and six capture logs were reopened and rehashed. Every current byte count, SHA-256, and recorded identity matched. The four outputs are the library, harness, candidate vector, and canonical control report. The two disposable fixture roots are absent, and the parent readback records an empty temporary-entry list.

The generated library is `8836848` bytes with SHA-256 `4d41bfea7382f2c7ab2d96e599b23bba6db67d5b28d0575ceb3d7eeb05bc4865`. The harness is `2591000` bytes with SHA-256 `9962138f80bfce588eeb45eaafd6d86d27a6eeb799daccee93027cac97b4f9df`. The harness Mach-O readback is arm64 executable type 2 with UUID `8522a879a18f3ae090f71f95288c579f`.

## Canonical control report

The saved canonical report is `/private/tmp/native-text-feasibility-rust-subject-adapter-a10-diagnostic-report.json` and the attempt keeps an exact mirror at `canonical-control-report-a10.json`.

- Bytes: `4859`
- SHA-256: `536a7ab8e2468455bab2eed339626c7a98a93ffd927aab8a6c63411a9cf9487f`
- State: `source_controls_passed_no_native_acceptance`
- Reconstruction count: `2`
- Reconstruction byte equality: `true`
- Control cases: `28`

The control report contains 12 fixture controls, 3 scalar controls, 2 FIFO controls, 4 vector-reader controls, 5 schedule controls, one PNG control, and one compilation-boundary control. Every recorded result has `passed=true`, and each observed error code matches its expected code.

The candidate output is `/private/tmp/native-text-feasibility-rust-subject-adapter-a10-diagnostic-output.bin` and the attempt mirror is `candidate-role-index-a10.bin`. Both are `536911` bytes with SHA-256 `a73f5a67503a524034b48da198f69e27898dac2b8cbb77e8c6814c5694ed1a5b`.

The canonical control report records candidate `rowCount=2068`; it does not expose a sequence digest. The frozen manifest's `completeDiagnosticSchedule` and independent decoder readback provide row count `2068` and sequence digest `a5ff306ed57b7e4ef44818674efeb03a7950f855d1d30a5e05be1e46f4c05bcf`. The source-owned schedule declares the same 38 source, 1889 dependency, 19 build, 90 toolchain/report, 25 input, and 7 PNG rows.

The report's measured and streamed file counts are separate accounting partitions. The candidate reports 1950 measured unique files and 18 streamed toolchain files. I do not add those partitions as if they were disjoint. The independent decoder separately reports the reopened union and its own identity checks below.

## Independent decoder readback

The saved decoder readback uses the frozen decoder source at:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/independent-role-index-decoder-a01/decode_role_index_v2_a01.py`

It binds `23381` bytes and SHA-256 `57fca7995ee886561ad7152f549c92aafd6839c84beeec63a59487527e59581b`. Its static runtime closure is also rechecked before and after. The readback reports `runtimeMatches=true`, `loadedImageAttestation=false`, and `nativeLibraryClosureAttestation=false`.

The decoder reopened the actual candidate, not only its saved mirror. It found:

- `1991` regular-file rows
- `1967` unique files
- `424092189` unique bytes
- `allRegularFilesMatch=true`
- `reconstructionBytesEqualSavedClaim=true`

The actual candidate and both permanent mirrors match their saved byte counts and hashes. The independent readback decodes the same `2068` role/tag rows and the same ordered sequence digest. This is a separate file decoder, but it remains same-family diagnostic code. It does not attest to a loaded native image or native library closure.

The A10 source manifest also binds the A03 decoder control package as external source evidence. The actual decoder readback records the A01 decoder source above. These are separate provenance roles. I do not collapse them into a claim that the A03 control source executed during this attempt.

## Scalar correction

The preserved `4158`-byte scalar fixture has SHA-256 `105602cc365676ecad1b75dd43a9a1f7b9c23b4557ba91135a9108138b5155ae` and contains only the `+42` and `-42` fixture rows. The canonical report wire bytes contain `+42`, `-42`, and zero with hex `0000000000000000`.

The independent readback records the corrected scope. It decodes zero from the actual saved canonical report wire bytes. It does not claim that zero was present in the two-row fixture. The earlier zero-row requirement was corrected in the saved readback without rerunning controls or inventing a vector.

## Scope and disposition

The outer actual report and independent decoder keep these eight fields false: `nativeProducerExecuted`, `acceptedValueConstructible`, `executionAuthorized`, `trustPinPresent`, `productIntegrationAllowed`, `watched`, `heard`, and `creativeAccepted`. The canonical report exposes false for `nativeProducerExecuted`, `acceptedValueConstructible`, `executionAuthorized`, `permissionCreated`, `productIntegrationAllowed`, and `compilerExecuted`, with `sourceOnly=true`. The parent readback independently asserts the outer eight through its `allScopeGatesFalse` list. Missing fields in the canonical report are not treated as false.

I found no byte, identity, command, control-result, decoder-row, or saved-mirror mismatch within this diagnostic scope. This evidence establishes a successful bounded Rust source-control and vector-readback attempt. It does not establish an active trust pin, a real native text qualification, a production run, product integration, media output, or human WATCHED, HEARD, or creative approval.

