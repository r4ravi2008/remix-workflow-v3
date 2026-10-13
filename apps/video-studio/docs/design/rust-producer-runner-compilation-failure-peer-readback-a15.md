# A15 compilation-failure peer readback

This is an independent readback of the saved A15/A07 fixed-compile attempt. I did not import candidate source, execute a built binary, run controls, or run a native producer. The result is a closed failed attempt. It is not a four-build, native, or product qualification.

## Bound evidence

The attempt directory is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a15-build-attempt-a01/`

| Record | Bytes | SHA-256 |
| --- | ---: | --- |
| `preflight.json` | 354131 | `131d10f715c3abcd7b7cb27006b406e880e55d8559a9004511ad89d2d4891233` |
| `compile-measurements-a01.json` | 716266 | `ad691555e69d9cf2bfcd5a1d4f0c9da56cdf54ef9d04c1b9c618e50e0918ebe7` |
| `compile-terminal-closure-a01.json` | 1248 | `795946bfbae78a3500ec2a627c8dee9af0aa14321bdf9ebe2a574a7520e735cd` |
| `compile-failure-root-readback-a01.json` | 354407 | `5c516da8ee82b4825af52f3be679fbcf58f24ae173cace44a9c08b2b82a49856` |
| root disposition | 2540 | `7e91e99730b2e01c84cdcfd71b34f40a4d3bfa1ff564729e770914229cc5c736` |

The root disposition is `apps/video-studio/docs/design/rust-producer-runner-compilation-failure-root-disposition-a15.md`.

The preflight declared four commands and four output paths. The saved attempt invoked only three commands. The controls CLI was not invoked.

## Input and source closure

I reopened all 594 current input paths as regular files. Their recorded bytes total 155207221. Every path was unique. Every current row matched its saved bytes, SHA-256, and all nine identity fields:

`device`, `inode`, `mode`, `links`, `uid`, `gid`, `bytes`, `mtimeNs`, and `ctimeNs`.

The saved `inputsBefore` and `inputsAfter` arrays are identical. The root readback `attemptInputs` array is also identical. The four predeclared commands are the production library, production CLI, controls library, and controls CLI. The current source closure includes 65 dependency rows. No native producer was allowed.

The A07 held-source readback is 23654 bytes with SHA-256 `f76b605af28da671c7029377f1a4ae49f2f402d36df82fad9be1e30ef213341c`. It records 65 selected dependencies, 4 source rows, 32 external rows, 65539 source bytes, and 19211739 external bytes. It records all four fixed archives, stable nine-field identities, no source import, and no compiler execution. Its source aggregate is `e174d6ecaf3c679aa82bd2323d520f38ad529f0631b5295bff737576ab565b4a`.

The A07 launch authentication record is 13310 bytes with SHA-256 `959968ca44ebc379377ee61e209f77799b1b64cd0ad31c6650d9c10c0934edd4`. It authenticates the fixed-four-compiles operation and exact held capsule. It is a prelaunch authentication record: it reports `callerLaunched=false` and `compilerExecutionObserved=false`. The later caller-closure record supplies the actual attempt result.

The external A07 caller closure is 2324 bytes with SHA-256 `ecbddea3dee9fd26669f988091652973a96b6c15b3a665d334d6e214919f6b86`. Its caller PID and process group are 42154. It records exit code 0, reaped, absent PID and group, and closed stdout and stderr. Its candidate result is false. Its external stdout is 1095 bytes with SHA-256 `0fca7d766fa6a20b2610c64d7b34ec12191a7358f29f8f5188ad612b1454d865`; external stderr is empty with SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

I rehashed all 18 current-reference rows in the A07 authentication record. Each path matched its recorded byte count and SHA-256. This validates evidence-file closure only. It does not attest loaded runtime code.

## Compiler result

The actual compiler phases were:

| Phase | PID / group | Return code | Closure |
| --- | --- | ---: | --- |
| production library | 42155 / 42155 | 0 | reaped, PID absent, group absent, streams and authorities closed |
| production CLI | 42164 / 42164 | 0 | reaped, PID absent, group absent, streams and authorities closed |
| controls library | 42183 / 42183 | 1 | reaped, PID absent, group absent, streams and authorities closed |

All three phases had no timeout, stream overflow, or termination signal. The caller descriptor closure has `cwd_fd` and `attempt_fd` both closed. The terminal receipt joins the complete measurements receipt, including all nine identity fields. The join matches the current file.

The six phase logs are current and match the root stream rows:

| Log | Bytes | SHA-256 |
| --- | ---: | --- |
| `0-stdout.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `0-stderr.log` | 25913 | `d6a7d3b9f6e9ef20cd9dc8e138b9066c9341854c2ef6dfdaefa9154da4f4dc66` |
| `1-stdout.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `1-stderr.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `2-stdout.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `2-stderr.log` | 13844 | `4796480e8524cbc9700996fabfd12f4bd88df9f55c387589fa17ed09f22363e9` |

The production-library stderr contains warnings only. The production CLI stderr and stdout are empty. The controls-library stderr contains nine compiler errors: two `E0277`, one `E0515`, one `E0521`, four `E0505`, and one `E0596`. The log ends with `error: aborting due to 9 previous errors; 9 warnings emitted`.

The two generated outputs are current and match their complete receipts:

| Output | Bytes | SHA-256 |
| --- | ---: | --- |
| `lib-rust-producer-runner-a15.rlib` | 20591120 | `f4efa74cea52175ad3d2b5c40f72b6fda997b92d4c891c5e1745e96e32c6c258` |
| unexecuted production CLI `rust-producer-runner-a15` | 3792152 | `e73a60688ef9dfee63a4a6cce69ac8b8cafc89c984ae196d6b3870cb81a4892d` |

The CLI is a thin arm64 Mach-O. I read its header bytes directly. The header has magic `0xfeedfacf`, CPU type `16777228`, file type `2`, and 19 load commands. Its `LC_UUID` is `40f6d3e612263d0eb68feae2180c7a58`. I did not execute it. The controls-library output and controls-CLI output are absent. No phase-3 logs exist.

The raw measurements leave `productionLibraryCompiled` and `productionCLICompiled` null. The root readback derives both as true from the two zero-return phases and matching output receipts. I retain that distinction. It does not change the failed four-build disposition.

## Disposition

The caller's exit code 0 only closes the caller process. It does not make the candidate pass. The controls library returned 1 with nine errors, and the controls CLI was never invoked. Therefore `candidateChecksPassed`, `candidateAccepted`, and `fourBuildCandidateAccepted` are false.

The saved terminal and root readbacks report `nativeProducerExecuted=false`, `nativeResultAccepted=false`, `productIntegrationAllowed=false`, `watched=false`, `heard=false`, and `creativeAccepted=false`. The A07 source readback and external receipts also report no native execution. These are evidence-scope flags, not product qualification.

This readback qualifies only a closed failed compilation attempt. A separate source repair and a fresh complete four-build attempt are required before any control, native, or product claim. I did not modify the source, frozen outputs, or prior evidence.
