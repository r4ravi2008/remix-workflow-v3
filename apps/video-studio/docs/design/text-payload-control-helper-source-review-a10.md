# Payload A10 pure-control helper source review

## Result

`run_payload_control_a10.py` is not ready for the selected pure-control run.

The helper has no P1 finding. One P2 evidence-binding finding remains.

This was a read-only, same-model-family source review of all 620 lines. I did not run the helper, Cargo, compiler, harness, test, measurement binary, or native framework.

## Reviewed identity

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `payload-build-prep-a10/run_payload_control_a10.py` | 31,090 | `f4db8bae0a2618e4fcbd95f49602174cab5f76ceccb7ffeede9d93fce668ddd8` |

The helper's compile-parent, compile-report, executable-identity, metadata-review, common-module, and contract hashes match the current files.

## P2 finding

### Parsed command evidence is not joined to the command observations

`run_split()` observes Cargo stdout after the child exits. `discover_harness()` reopens and parses that pathname at lines 231–282.

The helper records both observations. It never requires `harness.cargo_stdout == no_run.stdout`.

`run_logged()` similarly observes the selected-test log. `parse_test_summary()` reopens and parses that pathname at lines 285–302.

The helper records both observations. It never requires `test_summary.log == test_command.log`.

A pathname replacement between either pair can disconnect the parsed harness or pass result from the corresponding child output.

Retain and parse the bounded bytes from each command's descriptor observation. A smaller repair may require exact observation equality before using the parsed result.

## Correct source behavior

The helper binds the exact successful compile parent readback and its reviewed upstream identities.

The Cargo command uses a fresh control target with `--lib`, `--no-run`, and JSON messages. Harness discovery requires one library test executable below that target.

The direct harness command selects the full test name with `--exact`, one thread, and no capture. The parser requires one passing test and zero failures.

The helper compares the harness file observation and Mach-O identity before and after execution. It also rechecks source, dependencies, toolchain, producer binary, Cargo files, and upstream records.

The selected Rust test exercises bounded byte output and descriptor-attached partial evidence. It does not open media or call the Payload measurement path.

## Disposition and limits

Repair the P2 in a preserved successor before execution. The corrected helper may then qualify only the selected pure Rust output control.

`native_execution: false` is scoped to native media/framework work. The helper will launch Cargo, compiler processes, and one Mach-O test harness.

The command log caps remain post-run read caps. Active Cargo, compiler, and harness log growth remains outside the claim.

This source review does not establish a passing control, Payload measurement, native behavior, product integration, playback, hearing, or creative acceptance.
