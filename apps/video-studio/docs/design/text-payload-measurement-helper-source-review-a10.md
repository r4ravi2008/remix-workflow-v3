# Payload A10 measurement-helper source review

## Result

No P1 or P2 source finding remains within the isolated logical-measurement scope.

The exact A10 helper is source-ready for one fresh measurement run. Actual execution remains unverified.

This was a read-only, same-model-family review. I did not execute or typecheck the helper, runner, producer, control harness, or native framework.

## Reviewed identity

| File | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `payload-build-prep-a10/run_payload_measurement_a10.py` | 991 | 49,057 | `2fdc6aeec3d2eea7f2d73f812224d09695f8a92700cdbd0b322da2c6503d1231` |

The `measurement-a03` directory was absent during this review.

## Authority and pre/post closure

The helper requires the exact sixteen-field `control-review-a03.json` object. The object permits measurement and keeps native execution false.

I rehashed the referenced A03 evidence. The helper constants match the saved metadata, compile, selected-control, harness, log, and parent-readback files.

The accepted producer is SHA-256 `e7fb89cc6fa88676d304cae99516178a18c82164b63c3453b2f2a3f0480ca5fd`. Its Mach-O UUID is `6b8150394e46312494a6444036da4c8a`.

The selected control harness is SHA-256 `df1a3a06efd446871c4450801153944391377201aac93ca5e6de12111a393fb6`. Its Mach-O UUID is `9925076e75bf3ce39ba68e320b9ef5a6`.

Before launch, the helper reconstructs these authorities:

- 58 copied package files and six A09 runner files;
- eleven frozen fixture authorities;
- the preserved predecessor compile-failure lineage;
- 63 dependency packages and 4,065 dependency files;
- the successful A03 compile, executable identity, and build log;
- the exact one-test A03 control, harness identity, and direct test log;
- eleven helper, contract, review, and parent-readback preparation files;
- Cargo inputs, toolchain, producer, harness, and resolved Python executable.

The terminal `finally` path rechecks each mutable input class after every success or failure. Any mismatch changes the state to `measurement_identity_drift_failed_preserved`.

## Launch, output, and failure behavior

The helper creates `measurement-a03` exclusively and refuses reuse. It invokes only the reviewed A09 runner through the observed `sys.executable` path.

The outer runner has a 420-second timeout. The inner A09 producer has its own 300-second timeout and discards producer stdout and stderr.

The helper requires exactly one nested terminal record. Success requires `report.json`; a retained `failure.json`, timeout, launch error, nonzero exit, or malformed record remains failure.

The wrapper verifies the measurement report by bounded readback. It requires six plans, five snapshots, 28 allocation rows, seven precreation rows, and the exact nested output path.

The final wrapper report uses exclusive creation and a 32 MiB cap. The command log has a 16 MiB post-run read cap.

The shared contract correctly discloses that the log has no active growth cap while a child runs. This does not become a general bounded-log guarantee. The selected runner sends the measurement producer output to `/dev/null` and emits only its own bounded terminal status.

On a validation error, the helper retains the causal error and performs the same postchecks. Filesystem failure can still prevent writing the final wrapper report; the source does not claim crash-safe persistence.

## Interpreter identity

The helper records the resolved `sys.executable` path, bytes, SHA-256, and descriptor metadata before launch. It repeats the same observation after the child closes and requires exact equality.

This is path-bound interpreter evidence. It does not establish the loaded interpreter vnode, standard-library closure, or the exact executable image selected across the pathname-to-exec interval. The helper makes none of those claims.

## Measurement scope

The accepted result covers copied Rust type layouts, owned `String` and `Vec` capacities, actual fixture lengths, checked logical precreation charges, and current-thread standard-library BTree allocation requests.

The runner validates positive counts, maximum request bounds, start/end state, and all 28 plus seven expected rows. The exact reviewed A09 runner supplies those semantic checks; the wrapper binds its source and accepted report.

The result does not measure allocator bookkeeping, physical memory, native memory, process RSS, or universal product admission. It also does not establish native text behavior, playback, hearing, creative quality, or film completion.

## Disposition

Root may execute only this exact helper against the currently absent `measurement-a03` stage. A successful run would qualify the bounded logical-measurement observation only.

Any source or authority change requires a fresh marker and another review. Native and product acceptance remain false.
