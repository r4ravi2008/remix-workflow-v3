# A17 retained-control A04 mutation-delivery correction

This is a second additive correction. It preserves both earlier reports:

- Original failed-attempt peer report: `apps/video-studio/docs/design/rust-producer-runner-a17-retained-control-failure-peer-readback-a04.md`, 8,240 bytes, SHA-256 `bcd5b5149a8b090983d73e3927de9024449e691893650f13f6b9bba93134b1a6`.
- First correction: `apps/video-studio/docs/design/rust-producer-runner-a17-retained-control-failure-peer-readback-a04-correction-a01.md`, 4,105 bytes, SHA-256 `b7479ef934bec0af0d91c1cb3accc6c0b50b6b54bd19786944df9fe51b66cd27`.

The independent root readback remains `rust-producer-runner-a17-retained-a04-failure-root-readback-a01.json`, 702,970 bytes, SHA-256 `bf6babf40e7ff00222b4453c0d33d7ca46cd26a9f886f481fb4a5e19660f49ae`.

## Source and mutation timing

The reviewed private control source is:

`rust-producer-runner-a17/src/a17_launch_controls.rs`

- Bytes: `21,491`
- SHA-256: `52bafc6f3617bd73e422922f4bc5fa1d41aa0ed5c26ab5efa69591638059393d`

For `DifferentExecutable`, `a09_gate_for_action` selects `A09_GATE_STOPPED`. The action then renames the private executable and replacement at the `ReplaceDifferent` branch. The replacement is prepared from `/usr/bin/true` before the run.

The corresponding stage source is:

`rust-producer-runner-a17/src/lib.rs`

- Bytes: `200,612`
- SHA-256: `62974194b1544d14660ee84d102191ae7e963c15b3040a83c090dbadc05e34c8`

`darwin_spawn_suspended` waits at `A09_GATE_PRESPAWN` before it constructs the spawn call. The stage later waits at `A09_GATE_STOPPED` after the child has stopped. Therefore, this control's replacement action is scheduled after the executable path has already been passed to `posix_spawn`.

## Saved mutation evidence

The case is:

`.../rust-producer-runner-a17-build-attempt-a01/control-attempt-a17/focused/launch/different_executable`

The prepared replacement exists at `different-executable-replacement`:

- Bytes: `84,128`
- SHA-256: `1315b337a4740ed84543bbfd684ad0d6779e35eec6d84808bb909574839a3de1`

The saved source observation records the same replacement identity. The private executable used for the staged run remains present:

- `private-control-executable`
- Bytes: `5,017,344`
- SHA-256: `008fa6936c107095d0d1b3d05d7f5cdda79490860598f571ec0021ac415e03d7`

The saved case directory has no `different-executable-replacement-observation.json` and no `different-executable-original`. The post-review rename is therefore not evidenced in the preserved files.

The saved report records `started=true`, `stopped=true`, `resumed=true`, `sigcont_delivered=true`, `main_image_observed=true`, `reaped=true`, and `return_code=0`. Those fields describe process lifecycle. They do not prove that the replacement image was loaded.

## Corrected disposition

The `different_executable` row remains a failed control:

- `passed=false`
- `observedCode=completed`
- `allowedCodes=["loaded_executable_vnode_ambiguous"]`
- `childStarted=true`
- `resumed=true`
- `reaped=true`

The correct finding is that the intended replacement mutation was not delivered at the launch point. The saved process facts cannot be described as the replacement executable resuming and completing. The sentence with that meaning in correction A01 is superseded by this addendum.

The case still cannot qualify the driver. The parser failure and the launch-control mutation-delivery failure remain separate evidence issues. Native execution, native acceptance, product integration, watched, heard, and creative acceptance remain false.

## Scope

This correction is read-only. It changes no source, media, reports, metadata, state, controls, or product files. It does not rerun the driver or infer image identity beyond the saved source and filesystem evidence.
