# Rust producer qualification A06 build evidence peer review

This is a finite saved-evidence review of the A06 Rust qualification attempt. It is a same-model-family, nonblind review. I inspected and rehashed the saved package, attempt, published outputs, and frozen decoder. I did not replay A10 or trust-root controls, rerun the A06 harness, rebuild sources, launch a native child, or perform a product, media, WATCHED, HEARD, or creative action.

## Source and recipe bindings

The source package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-qualification-a06`

Its source manifest is `84860` bytes with SHA-256 `9b8df81fbb563ae175b570e633cbecf32bb6859b1bbf6e225d68a5326bbe542c`. The manifest declares eight package rows totaling `135498` bytes. I rehashed all eight rows and recomputed the documented source aggregate:

`e2361b82cdbe272bfe2732804262d294113804e86d7de0b25290d083c96eae8b`

The package rows and aggregate matched. The manifest binds 165 external rows totaling `30797997` bytes. I rehashed every external path and recomputed the role-plus-path aggregate:

`38741d8382ee101ac986ec9be19c3ef3f0ba5f2c9ecdd78d64d4814597a38fe8`

The external rows and aggregate matched. The direct build recipe is `8296` bytes with SHA-256 `897e51a4894a7d85417ab9ad18f20d4cf3adbc4723fd61a1cc31ffd2a0a18ee0`.

The recipe binds the stable AArch64 macOS compiler, four fixed dependency archives, two dependency roots, and the declared output paths. The saved preflight adds three ordered vectors: library compile, diagnostic compile, and one no-argument diagnostic invocation. It also binds ten environment variables, a 60-second command limit, and stream guards. The package state remains source-only. The later attempt is the separate actual-evidence record.

## Saved attempt and command results

The attempt directory is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-qualification-a06-attempt-a01`

- `preflight.json`: `163116` bytes, SHA-256 `476830bef458defd9fd2458a734ce8e5eb875a0210cd8c4da2a742e9e33ead57`
- `report.json`: `329061` bytes, SHA-256 `c55721ce890a9003ef16a34c06ea74b9bbc90f519aa57df92b46f3cb78dd972d`
- `0-stderr.log`: `25051` bytes, SHA-256 `db8b38c085e32a36455156479bfa803f367a9b77479b749a05e3785189018de1`
- `0-stdout.log`: `0` bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `1-stderr.log`: `0` bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `1-stdout.log`: `0` bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `2-stderr.log`: `0` bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `2-stdout.log`: `188` bytes, SHA-256 `19674c1f9f0b9363c83e8d6ce956941d5585d052d450a9b3704f6a41cfaeff83`

The outer report state is `fixed_direct_diagnostic_complete`. It records `sourceControlOnly=true`, `compiled=true`, `executed=true`, and `controlsPassed=true`. It has `268` input rows totaling `99972321` bytes. The preflight rows equal `inputsBefore`, and before and after rows are equal.

All three report command vectors equal the corresponding preflight vectors. Each command returned `0`, reaped successfully, timed out false, overflow false, sent no termination signal, and left no unclosed stream. PIDs `91814`, `91818`, and `91836` are absent in the current process table. All six log files match their saved byte counts, hashes, and identities.

The diagnostic stdout is the saved 188-byte line:

`qualification_diagnostic_passed source_rows=2068 class_rows=2068,18,25,8 runner_files=35 runner_cases=10 controls=7 reader_controls=4 revalidation_negatives=3 trust=pinned_manifest_absent`

The `pinned_manifest_absent` text is a passed missing-trust-pin control result. It is not an active trust pin.

## Input, output, and absence readback

I reopened every current input path from `inputsAfter`. All 268 rows matched the saved byte count, SHA-256, and all nine identity fields. No current input row differed. The report sets `inputsMatched=true`.

The report lists nine generated outputs. I reopened and rehashed every output:

| Output | Bytes | SHA-256 |
| --- | ---: | --- |
| `librust_producer_qualification_a06.rlib` | 11184096 | `34700bea7302c36ec3568beb53f0d371b338c73ef84adb867c167604ae2d9448` |
| `rust-producer-qualification-a06-diagnostic` | 3029560 | `87779853c9b0898bd6361c52a54bf1c94438e8ee4800eb78f365442a36bdb92e` |
| `source-candidate.role-index` | 536911 | `a73f5a67503a524034b48da198f69e27898dac2b8cbb77e8c6814c5694ed1a5b` |
| `source.role-index` | 536911 | `a73f5a67503a524034b48da198f69e27898dac2b8cbb77e8c6814c5694ed1a5b` |
| `build.role-index` | 5408 | `9068e916a9748038093fe7a904a55d26c233fb2eb7dcbb98c4ceb8cd911c767c` |
| `input.role-index` | 7429 | `2fff4571b0905130d4ecbe8db68d4b1428b26c677786882606a6718b8d000e1e` |
| `png-control.role-index` | 2570 | `c2b65f10c11e7169c53209caa505b88c5686db7dc448bce67ba507529e8c2d46` |
| `runner.role-index` | 15579 | `2c0a3b98623c9af3cf1d7a060efc53d3ea0793252b4d98ef90b0488925153fc2` |
| `report.json` | 2967 | `d0645cf3a038abc1ae48808a900156aa258b1bc9c3de89d9e0e59fb36f4ec370` |

The diagnostic Mach-O readback is arm64, executable type 2, with 19 load commands and UUID `2fb259f5829f387ea4259f862d405f81`.

The report has no temporary entries. Its reader-control and future-evidence roots are absent. The seven declared canonical output paths are all present under the saved output root, and no additional output was used for this review.

## Saved control report

The published control report is `rust-producer-qualification-a06-diagnostic-output-a01/report.json`, with `2967` bytes and SHA-256 `d0645cf3a038abc1ae48808a900156aa258b1bc9c3de89d9e0e59fb36f4ec370`.

It records:

- `sourceRows=2068`, `sourceBytes=536911`, and candidate SHA-256 `a73f5a67503a524034b48da198f69e27898dac2b8cbb77e8c6814c5694ed1a5b`.
- Six class receipts, with two 2068-row reconstructions equal byte-for-byte.
- Seven negative controls, all passed with matching expected and observed codes.
- Four reader controls, all passed with matching expected and observed codes.
- Three revalidation negatives.
- Runner receipt: 63 rows, 15,579 bytes, SHA-256 `2c0a3b98623c9af3cf1d7a060efc53d3ea0793252b4d98ef90b0488925153fc2`.

The seven negative controls are missing future evidence, noncanonical reader path, malformed acceptance record, missing trust pin, fresh subject-reference drift, fresh final-reference drift, and fresh final-byte drift. The four reader controls cover FIFO rejection, symlink path rejection, growth detection, and replacement detection.

The source candidate and source RoleIndex files are exact byte copies. The class report records `source-candidate`, `source`, `build`, `input`, `png-control`, and `runner` receipts. No accepted value or production output is created by this report.

## Independent frozen decoder

I used the frozen standalone decoder at:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/independent-role-index-decoder-a01/decode_role_index_v2_a01.py`

It is `23381` bytes with SHA-256 `57fca7995ee886561ad7152f549c92aafd6839c84beeec63a59487527e59581b`. I decoded all six published `*.role-index` files. Every file passed the decoder's closed RoleIndexV2 grammar, role ordering, bounds, references, and cycle checks.

The decoded file shapes are:

| File | Rows | Decoded shape |
| --- | ---: | --- |
| `source-candidate.role-index` | 2068 | 1991 regular, 16 ordered lists, 61 scalars |
| `source.role-index` | 2068 | 1991 regular, 16 ordered lists, 61 scalars |
| `build.role-index` | 18 | 17 regular, 1 ordered list |
| `input.role-index` | 25 | 25 regular |
| `png-control.role-index` | 8 | 8 regular |
| `runner.role-index` | 63 | 35 regular, 15 scalars, 12 derived booleans, 1 ordered list |

For every decoded regular-file row, I reopened its encoded absolute path and compared content size, SHA-256, device, inode, mode, file size, modification time, and change time. All regular rows matched current files. This includes 1991 rows in each source candidate, 17 build rows, 25 input rows, 8 PNG rows, and 35 runner rows.

The runner semantic map decodes a ten-case ordered list, `result_count=10`, `passed_count=10`, `file_count=35`, `control invocation returncode=0`, and true build and control semantic joins. All ten `rust.runner.control.case:*` booleans are true. Its stored build phase returncodes are `0`, `0`, and `78`; these are facts in the referenced runner RoleIndex and are separate from the A06 qualification command returncodes, which are all zero.

The decoder is same-family diagnostic code. Disk hashes and identity fields do not attest to a loaded runtime image or native library closure.

## Scope disposition

The outer report keeps these fields false: `nativeProducerExecuted`, `acceptedValueConstructible`, `executionAuthorized`, `trustPinPresent`, `productIntegrationAllowed`, `watched`, `heard`, and `creativeAccepted`. The canonical report scope is diagnostic-only and keeps `acceptedValueConstructible`, `executionAuthorized`, `nativeExecutionEstablished`, and `productIntegrationAllowed` false.

This evidence establishes a completed bounded Rust compile, diagnostic invocation, control report, and independent RoleIndex readback. It does not establish an active trust pin, native producer qualification, real product execution, media output acceptance, or human WATCHED, HEARD, or creative approval.

