# Independent RoleIndex decoder control A02: actual failure readback

A03 launcher decoder-control ran once. The external tool returned exit 1. The direct control child returned exit 1 and was reaped. Its stdout and stderr logs are empty. The launcher preserved its failure report and the child's exclusive failure report. The success launch report and publication-failure file are absent.

The child stopped at read_bound_inputs with logical_fixture_canonical. It completed zero scheduled results. It had not decoded the fixture. Both frozen input raw hashes match. The logical fixture and encoder source manifest are formatted JSON; compact sorted serialization differs from both raw inputs. Control A02 requires that compact format even though these source authorities were frozen in formatted JSON.

The parent independently checked 169 prelaunch source rows, the saved command/environment joins, input observations, reports, and available logs. The postcheck records every current file observation and both raw-format measurements. The launcher attempted SIGTERM and SIGKILL after the nonzero exit. Both process-group sends reported ProcessLookupError because the group was gone. Post-kill drain explicitly records capture-selector-unavailable. This evidence does not establish descendant reaping or loaded-code identity.

The failed A02 control and A03 launcher attempts remain preserved. A narrow A03 control successor will accept the existing hash-bound JSON formatting. The repair must retain strict parsing, duplicate-key rejection, every field comparison, all 74 scheduled results, vector-manifest canonical bytes, raw hashes, and exclusive fresh publication. No Rust build, Rust controls, or fixture encoding needs to repeat.

No independent decoder result, native producer output, media output, creative acceptance, or gate authority is accepted by this failure readback.
