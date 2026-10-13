# A17 retained A04 actual failure disposition

The A17 retained A04 attempt ran and failed. The caller and control driver have closed.
The accepted four-build compilation result remains valid within its compilation scope.
This failed control result does not permit bootstrap, native production, or product integration.

## ROOT readback

ROOT saved `rust-producer-runner-a17-retained-a04-failure-root-readback-a01.json` under the native text unit.
The proof contains 702,970 bytes and has SHA-256 `bf6babf40e7ff00222b4453c0d33d7ca46cd26a9f886f481fb4a5e19660f49ae`.

The independent reader opened regular files with `O_NOFOLLOW`, `O_NONBLOCK`, and bounded reads.
It compared nine identity fields before reading, after reading, and against the current pathname.
It matched ten pinned input records and twelve saved closure references.
It did not import or execute the frozen caller, Supervisor, control binary, or native producer.

The control tree contains 560 regular files and 60,627,297 regular-file bytes.
It contains 280 directories including its root, or 279 directories excluding its root.
One FIFO remains preserved and unopened.
The JSON scan found 315 valid files and four exact intentional malformed sentinels.
The independent scan did not find a malformed generated report.

The saved execution observation proves `controlsExecuted=true` and a valid returned Supervisor phase.
The caller PID and process group were 63918; the driver PID and process group were 63920.
Both processes returned exit code 1.
Saved observations establish reap, outer process absence, stream EOF, and descriptor closure.
ROOT independently confirmed both outer PIDs and process groups were absent.
The Supervisor did not establish nested control closure acceptance.
This disposition preserves `nestedClosureAccepted=false`.

## Two distinct failure scopes

The caller failed with `unparsed_actual_report_json` while reading private control outputs.
The malformed-fixture contract declares three lifecycle sentinels.
It omits the focused `authorization_path_collision` sentinel.
That fixture contains exactly `authorization-collision-sentinel\n`, or 33 bytes.
Its current SHA-256 is `a3b8e30e1f8de716401feff51dc0589442e7f4012d17905883bd24eb1a776916`.
ROOT also hashed the source literal and obtained the same digest.
The original peer report contains an incorrect digest suffix for this fourth sentinel.
The peer report remains preserved; an additive correction was requested.

The control driver separately returned failure before the caller parsed its reports.
The observed outcomes are:

| Control group | Passed | Total |
| --- | ---: | ---: |
| Copied pure cases | 21 | 21 |
| Lifecycle cases | 9 | 10 |
| Focused cases | 4 | 15 |
| Suspended launch variants | 6 | 11 |

The lifecycle FIFO case reports `stage_or_report_failed` after 997 milliseconds.
Several focused cases stopped at authorization identity, review validity, or review drift checks.
The postflight drift case did not reach its intended mutation.
Three identity-review mutations observed the expected terminal code but still failed their complete predicates.
The path-anchor case observed `run_root_parent_drift` rather than its intended `authorization_path_drift`.

Four failed launch cases stopped before a child started.
The `different_executable` case started, stopped, resumed, reaped, and observed its user-code marker.
That case reports `completed`, although its expected code is `loaded_executable_vnode_ambiguous`.
These observations require source-grounded diagnosis of fixture delivery and production publication.
They do not by themselves prove that the intended executable replacement occurred.

Adding the omitted parser sentinel cannot qualify these separate runtime failures.
Every other malformed JSON payload must remain rejected.
Any successor must preserve this attempt and repair the actual failed predicates.
The expected cases and negative outcomes must remain explicit.

## Current scope

The source-time reviews and compilation receipts remain preserved with their original scope.
The A04 control gate has been consumed by this single failed invocation.
No rerun is authorized by that consumed gate.
A fresh repaired package requires separate source review and a new execution decision.

`candidateAccepted`, `nativeProducerExecuted`, `nativeResultAccepted`, and `productIntegrationAllowed` remain false.
Watching, hearing, and creative acceptance remain false.
The general editor, tenant application, and complete 273-second Panja film remain unfinished.
