# A16/A08 recipe-eligibility ROOT and peer disposition

ROOT and peer reject compilation eligibility for the same three missing recipe evidence paths. ROOT classifies one P2 integrity group; peer classifies one P1 package-eligibility group. The severity difference does not change the required repair or rejected disposition.

ROOT fully read the A08 peer report, 8053 bytes, SHA-256 `f2c05171353cb79bd86fe8ab904e9ebc46305a4b55224e2d487c365254d61f0e`, and the separate A16 peer addendum, 2378 bytes, SHA-256 `80905766012112f91c33fc51340571568052f3a38bb855289ed6ddb4a05e6f5d`. Both current files match held descriptor reads. The A08 wrapper source remains byte/AST-equivalent to A07 after fixed labels and the current metadata-key map. Neither reviewer found an independent wrapper behavior defect.

Add these exact companion keys in the separate A17 recipe:

- `a15_controls_failure_log` points to A15 build-attempt-a01/2-stderr.log.
- `a15_compile_measurements` points to A15 build-attempt-a01/compile-measurements-a01.json.
- `a15_compile_terminal_closure` points to A15 build-attempt-a01/compile-terminal-closure-a01.json.

Each path must be absolute and match its already-bound byte/hash/current-identity row. Keep the existing SHA scalars. Reproduce every byte/digest scalar join, including missing-path rejection, before source acceptance. Preserve production logic, controls repairs, all schemas/schedules, exact four commands, environment, caps, and 65 dependency boundary. Do not weaken the validator.

The peer recommends rebinding the recipe receipt. Frozen A16 and A08 will instead remain preserved. A17 and its separately bound compiler wrapper will supply the correction. The prior source/hash measurements remain valid within their scope; they do not authorize compilation. No A16/A08 gate, decision, compiler, control, native producer, or product integration was executed.
