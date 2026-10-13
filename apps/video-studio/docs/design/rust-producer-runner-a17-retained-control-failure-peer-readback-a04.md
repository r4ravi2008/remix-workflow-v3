# A17 retained-control A04 failed-attempt peer readback

This report reviews the saved A17 retained-control A04 attempt only. It does not rerun the caller, controls, compiler, child processes, native producer, media work, or product integration.

## Disposition

The attempt is a closed failed attempt. The outer caller exited with code 1 after the stage `reading_private_control_outputs`. The saved failure code is `unparsed_actual_report_json`.

The immediate root cause is a caller allowlist defect. One malformed JSON file is an intentional focused control sentinel, but A04 does not declare that path in `malformed_fixture_contract`.

This is a P1 for the retained-control attempt. It prevents the caller from reaching its normal report joins. It does not indicate an invalid generated producer report.

## Frozen source and saved failure identities

The reviewed A04 caller is:

- `rust-producer-runner-a17-retained-control-preparation-a04/native_runner_retained_controls_a17.py`
- 87,927 bytes
- SHA-256 `198f5e7a6a9213800da70a05aeb9b35c71ebabb4624d7a1224aa7bb9e6da661f`

The A04 source manifest is 45,050 bytes with SHA-256 `e3401393028553f925b6ab4ac7c40ecc2a5bfa4bc43b1bf1776a6bf31daafbaf`.

The saved external authentication record is 16,237 bytes with SHA-256 `c9adf4986145f53193bde65fe35b434a1b87f06cdcd15630ba2cb108dcdbbb84`.

The saved caller closure record is 2,400 bytes with SHA-256 `36815771c209db3a744ade5a94d3ad47ba67f057956ef656c41b7ba6a1dc8fae`.

The saved caller stderr is 613 bytes with SHA-256 `dccf73a97d724febe96c33aba9d83337e9a5d6dc116448aef3ff4d0b37d8ea23`.

The stderr line records `unparsed_actual_report_json`, stage `reading_private_control_outputs`, and the terminal-closure receipt. The saved stdout is empty.

## Root cause

A04 defines three deliberate malformed entries at caller lines 298–310:

1. `terminal_collision_fallback/report.json`, 29 bytes, SHA-256 `a6f38dbfe66a446687ce5a95fbe7202d1f808824b26791267b00ab25517dfc4b`.
2. `double_terminal_collision_preserved/report.json`, the same 29-byte sentinel and hash.
3. `double_terminal_collision_preserved/report-failure.json`, 31 bytes, SHA-256 `a8ebc6f871fd25b405c0ce1c5a5b9184abc9f75646c990b59ef81329efda4aa2`.

The A04 parser records those three paths in `deliberate_malformed`. It then parses every `.json` payload and rejects any parse failure outside that set at lines 1237–1244.

The focused control `authorization_path_collision` creates a fourth deliberate malformed fixture. Its source creates `output-parent/collision-run/authorization.json` before the exclusive authorization write. The source expects `authorization_write_failed` and verifies unchanged sentinel bytes and identity. The pure fixture declares this mutation and expected error at `pure-fixtures-a17.json` lines 361–365.

The saved fourth sentinel is:

- `control-attempt-a17/focused/cases/authorization_path_collision/output-parent/collision-run/authorization.json`
- 33 bytes
- contents `authorization-collision-sentinel\n`
- SHA-256 `a3b8e30e1f8de7169c53209caa505b88c5686db7dc448bce67ba507529e8c2d46`

Its bytes are intentionally non-JSON. The focused implementation creates and preserves that sentinel in `a17_focused_controls.rs` lines 682–746. The focused report marks `authorization_path_collision` passed with `authorization_write_failed`, unchanged bytes, and unchanged identity.

A04 does not include this path in `malformed_fixture_contract`. The parse loop therefore appends it to `parse_failures` and raises `unparsed_actual_report_json`. The parser never reaches the combined-report validation that follows.

This is a scope omission in the caller’s explicit malformed-fixture contract. It is not evidence that a generated `report.json` or `report-failure.json` was malformed. The four current parse failures are all deliberate sentinel fixtures; the other 315 JSON files under the control tree parse successfully.

## Reopened attempt and partial inventory

The attempt directory currently contains 581 files, 281 directories, and 116,773,594 file bytes. The control-attempt subtree contains 560 files, 279 directories, and 60,627,297 file bytes.

The independent current JSON scan found 319 JSON files under the control-attempt subtree:

- 315 parsed successfully.
- 4 were the deliberate sentinels listed above.
- 0 additional JSON parse failures were found.

The saved caller failure measurement is 11,172 bytes with SHA-256 `576679c6c2033c823473dd69c2cc7720328e5aac81f31822800bf5354691a2a6`. Its saved `partialOuterInventory` and `partialControlInventory` both state `available=false` with `bounded_inventory_unavailable`. The current independent re-open supplied the counts above without changing the saved attempt.

The saved measurements and current files agree for the retained preflight, root gate, utility, failure observation, executable, stream logs, terminal failure measurement, external authentication, and external stdout/stderr receipts. Each checked receipt matched its saved byte count, SHA-256, and nine current identity fields.

Key reopened records are:

- `controls-preflight-a01.json`: 411,022 bytes, SHA-256 `391ef6cb03140a85cbe6bd12dca29eb1559406aeb76370ff0053cf52ac257f35`.
- `controls-caller-failure-measurements-a01.json`: 11,172 bytes, SHA-256 `576679c6c2033c823473dd69c2cc7720328e5aac81f31822800bf5354691a2a6`.
- `controls-terminal-closure-a01.json`: 1,289 bytes, SHA-256 `270d423847b9fd5a4ced72e1a59fc1b3aef04485170578f014131d9c56965285`.
- `retained-controls-a01-failure-observation-a02.json`: 684 bytes, SHA-256 `32786dda21f9196a7baeffa45e791a83bccd0c5705c65508a649ab0a91bd4690`.
- `control-report-a17.json`: 171,054 bytes, SHA-256 `1dd440119fa52a83e99ec2cb974847aa0c1533d5f9ca4104954883c3e253149e`.
- `a04-lifecycle/control-report-a03.json`: 6,501 bytes, SHA-256 `9fa57c4b8cf65fefc0ac84a79e8e3bc4133785312e1d942cc94885c966973508`.
- `focused/focused-control-report-a17.json`: 170,593 bytes, SHA-256 `49785811e6707c03c8fafc723385eb9703a83ebae338209b6ec1ef89e6e3b53b`.

## Process and descriptor facts

The outer caller closure records PID and process group 63918. It records exit code 1, reaped true, process absent, process group absent, both streams closed, and both streams within caps.

The returned retained phase records nested driver PID and process group 63920. It records return code 1, raw wait status 256, valid returned phase, resume observed, outer PID and group absent, outer EOF, outer stream descriptors closed, launch authorities closed, and outer closure complete.

The retained phase records `nestedReportsInspected=false`, `nestedProcessAbsenceInspected=false`, `nestedClosureAccepted=false`, and `externalNestedClosureReadbackRequired=true`. The failure observation records `retained_driver_nonzero_exit`, `driverResumed=true`, and `cooperativeCancellationUnavailable=true`.

The terminal closure records `allCallerDescriptorsClosed=true`, `externalReadbackRequired=true`, and `candidateAccepted=false`. Native producer execution, native result acceptance, product integration, watching, hearing, and creative acceptance remain false.

## Other saved control results

The caller stopped before combined structural checks. The saved control reports still provide separate diagnostic facts:

- The A04 lifecycle report has 10 rows and 9 passed rows. `fifo_authority_rejected_nonblocking` is false.
- The focused report has 15 rows and 4 passed rows.
- The combined report state is `source_controls_failed_no_native_acceptance`.
- The retained control stdout is exactly `{"schema":1,"state":"failed","passed":9,"total":10}\n`.

These additional control failures are separate from the immediate parse failure. This report does not reinterpret them as accepted evidence.

## Limits and disposition

The saved attempt proves a closed failed caller run and preserves its evidence. It does not qualify the retained control, the native producer, media output, or product integration.

The required repair is narrow: bind the focused `authorization_path_collision` sentinel to the explicit malformed-fixture contract, with its exact anchored path, bytes, and SHA-256. Keep the strict rejection for every other malformed JSON payload. Preserve the current failure artifacts before any successor attempt.
