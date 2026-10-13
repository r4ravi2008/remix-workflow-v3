# RoleIndexV2 decoder control A03 actual-evidence scope review

## Disposition

This is a read-only review of the saved A03 direct-control evidence. I did not
rerun or import the control or decoder. I did not run a helper, compiler,
vector, native, media, GPU, Resolve, or playback process.

The saved evidence supports pure decoder-control and saved-report evidence.
I found no new P1 or P2. The evidence does not claim operating-system launch
identity, process-group cleanup, child reaping, loaded-image closure, atomic
launch, native production, or media acceptance. The saved scope statements
correctly leave those claims false.

This review is same-family and nonblind. It checks saved JSON identities and
relations without treating the direct tool record as a loaded-process proof.

## Reviewed evidence identities

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `independent-role-index-decoder-a03/root-launch-receipt-a03.json` | 78050 | `e0f05f874b3b2055f74a379cc217041644edd6c132c64f0804843dadefdd3542` |
| `independent-role-index-decoder-a03/root-tool-result-a03.json` | 349 | `c0daf673f34f801f2649fcef902d4d846fcbfa27ae0837822280192ed55203bd` |
| `independent-role-index-decoder-a03/root-postcheck-a03.json` | 78938 | `5063fddccebcc2bbc7898f4e65a9e530fd840a8887141b5c00a4a41ec881fa64` |
| `independent-role-index-decoder-a03/control-attempt-a03/control-report-a03.json` | 26118 | `08f8371580ff20652ee273c720f54cb98c8d5ded02f2f44c92a628564df81dde` |
| `apps/video-studio/docs/design/role-index-decoder-control-parent-readback-a03.md` | 2115 | `ca801f13ef03e6851691dc49165faa0dd115927d98672f559f76317200d4f473` |

The source-reviewed A03 control remains bound in the report as 92,907 bytes
with SHA-256
`0281d006ed97da61738ff41e3355e450c1ffabcdfd12fef3f1687637e79665b1`.

## Direct-control evidence

The pre-run receipt records one fixed interpreter invocation, `-I -B`, the
A03 control path, the A03 working directory, and an environment with exactly
six keys: `HOME`, `LANG`, `LC_ALL`, `PATH`, `TMPDIR`, and `TZ`. It records the
fresh temporary-directory identity and the A03 attempt directory as absent.
The receipt state is
`root_external_receipt_before_one_direct_role_index_control_a03`.

The saved tool result reports exit code `0` and empty output. Its scope states
that it is completion-tool-return evidence only. It sets
`loadedImageAttestation`, `processReapingAttested`, and native authority to
false. The receipt's `atomicLaunchAttested` and `processReapingAttested` flags
are also false. These boundaries are consistent with the requested direct
tool evidence.

The saved control report has schema 2 and the historical A02 success state
`independent_role_index_decoder_controls_a02_passed_no_authority`. Its
publication path is the fresh A03 path:
`independent-role-index-decoder-a03/control-attempt-a03/control-report-a03.json`.
The report's scope retains same-process control, external-launcher-required,
no child process, no process isolation, no encoder execution, and no authority
flags.

The report contains 74 result objects. Read-only comparison with the frozen
A02 schedule found equal ordinal, identifier, and expectation sequences. All
74 statuses are `passed`. The 59 rejection rows retain their scheduled error
codes. The result partition is 14 `pass`, 59 `reject`, and one `different`.
The vector identity is 4,158 bytes, SHA-256
`105602cc365676ecad1b75dd43a9a1f7b9c23b4557ba91135a9108138b5155ae`, with
79 rows.

The report records independent expected and actual model records at 19,503
bytes. Both records have SHA-256
`006e1659fe06fdda987c9cc3d3e8d8b7c4f19008d5c611987a367f182f039648`.
The source-reviewed control performed the complete model comparison; the
report records the resulting digests rather than publishing a second model
file.

## Post-run file and report checks

The postcheck state is
`role_index_control_a03_root_current_file_and_result_postcheck_passed`.
It reports 180 matched outer source rows and 183 unique regular files totaling
22,830,018 bytes. It binds the 26,118-byte report and 349-byte tool result to
their exact paths and hashes. It records the same result partition and model
digest as the report.

The A03 attempt directory contains exactly one file: the primary report. No
publication-failure file or other control output exists. The temporary
directory remains empty. The postcheck includes the A03 receipt and tool result
among the current evidence, while the postcheck itself is not incorrectly
treated as a preexisting source row.

The ten report input observations match the corresponding pre-run source rows
by path, byte count, and SHA-256. The pre-run receipt contains 180 unique
source paths. The postcheck reports all 180 source rows matched. This provides
the intended saved-file join for the pure control inputs.

## Scope and findings

The evidence supports the following bounded statement: one saved direct-tool
completion produced a canonical A03 control report whose 74 results, scheduled
rejection codes, vector identity, model digests, publication path, and input
observations match the reviewed source and schedule, with an independent
read-only postcheck.

The evidence does not attest that the planned argv reached a particular
operating-system process image. It does not attest Python loaded modules,
process-group cleanup, child reaping, descriptor-atomic launch, or durable
filesystem transactions. The saved receipt, tool result, report, and postcheck
explicitly deny those claims. Requiring a new external wrapper solely to make
unsupported claims would exceed this bounded evidence scope.

The report's A02 state names are intentional historical wire compatibility.
The A03 report path, control-source identity, and A03 attempt directory provide
the current output binding. The prior failed A02 report and unrelated A03
launcher attempts remain preserved and are not reused as current control output.

No P1 or P2 remains in this saved-evidence scope. Native producer execution,
native text production, media output, playback, watching, hearing, creative
approval, and gate authority remain unqualified.
