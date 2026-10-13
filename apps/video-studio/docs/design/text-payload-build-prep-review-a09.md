# Payload A09 remaining-helper source review

## Disposition

Payload A09 is not ready for the selected control or measurement.
The actual release compile failed with three Rust errors.

The compile report is `compile_failed_preserved` with Cargo exit 101.
No executable identity, compile review, control directory, or measurement directory exists.

Two helper-level P2 provenance defects also remain.
They affect the future control and measurement stages after compilation is repaired.

I did not run a helper, parser, Cargo command, control, measurement binary, native framework, GPU process, or Resolve process.
This was a same-model-family source review.

## P1: the selected package does not compile

The actual A02 compile report has SHA-256 `4c37cb477d54eeb1599a80920e24bfa5f868f7976455ea32aea489b24227b009`.
Its retained Cargo log has SHA-256 `264f7598d362665d1735a7655218d2657918a06df98314365b735be1e330798f`.

The log records these three source errors:

- `E0432`: `BuildIdentity` is imported from `crate::model`, but the public type is re-exported from `crate`.
- `E0433`: `crate::layers` does not exist. The layers module is private under `crate::movie`.
- `E0599`: `uuid` is an `&str`, so `uuid.capacity()` does not exist.

The wrapper correctly preserved the failure and returned no successful binary identity.
The current source cannot reach the pure control or measurement stage.

Repair these errors in a fresh copied source package.
Preserve the A08 package and failed compile A02 unchanged.
Require a fresh compile directory and a separately reviewed successful result.

## P2: the control does not close its stage or harness identity

`run_payload_control_a09.py:273-274` sends Cargo test output into `compile-a02/target`.
The command therefore mutates the previously reviewed compile stage.
The contract describes `control-a02` as the fresh control stage.

Use a control-owned target directory, such as `control-a02/target`.
This keeps generated test artifacts inside the stage that owns them.

The helper observes and parses the selected harness before execution.
It writes that identity into `lib-test-harness-identity-a02.json`.

The final checks reread source, dependencies, preparation files, reviews, manifests, locks, and toolchain files.
They never reread the harness executable.

A successful report therefore lacks path, byte, hash, and Mach-O identity closure after the direct test.
Reobserve the harness after test completion and require exact equality.
Keep loaded-vnode identity outside the claim unless separately established.

## P2: the measurement wrapper does not close its interpreter identity

`run_payload_measurement_a09.py:237` observes `sys.executable` before launching the reviewed runner.
The command then uses that pathname at line 239.

The final checks cover the runner, payload binary, source, dependencies, toolchain, and review records.
They do not reread `sys.executable`.

Record explicit Python before and after observations.
Require equal path, bytes, SHA-256, and stable file metadata.
This remains path-bound evidence and does not claim loaded interpreter identity.

## Confirmed source properties

### Metadata and dependency joins

The helper constants match the actual reviewed metadata records.
The current hashes are:

- metadata report: `efe7bd49a1f37dc0d1c4f12f7144167eefaba86a0d25942d3aa519b4747eca62`;
- dependency report: `3a0afe3904f214e3ac8b47e7002b61e8083f15420f010138c387db8fe56078b2`;
- Cargo metadata: `e0fd646ddf6538ad2cd9ee5a9c561a28af0b2ac93d1be1c1c35ae03f763d045`;
- metadata review marker: `5537386b746bc5ece61a2c51f1d9710c509360a1b27a19519c83771116eba14c`;
- parent readback: `eba5134ebf6c48966874e1613d17b2c9c7995bfa515d2feab1fe5250306806ce`.

The parent readback records 58 package rows and five runner rows.
It records 63 registry packages and 4,065 dependency source files.
It keeps compilation and native execution false for the metadata stage.

The later helpers require the exact metadata report, dependency report, and review marker.
They do not fall back to A01 records.

### Compile wrapper

The compile command selects the exact package, binary, feature, target, lock, and offline mode.
It uses a fresh target directory and never starts the output binary.

The failed attempt proves the command reached the selected `video-studio` library.
It does not prove compile compatibility.

### Exact one-test control

The control command includes `--package video-studio`, `--lib`, and `--features payload-measurement`.
It also includes `--no-run` and Cargo JSON output.

Harness discovery requires exactly one `video-studio` library test artifact.
The direct filter is the complete test name.
Libtest receives `--exact --test-threads=1 --nocapture`.

The selected test exists under the feature-gated library module.
Its source checks capped partial output and retained-descriptor identity.
The log parser requires that one named test and a one-pass, zero-failure summary.

These checks make the test selection exact after compilation succeeds.
They do not close the two control provenance defects above.

### Bounded measurement wrapper

The measurement stage requires successful metadata, compile, control, and review records.
It rehashes the A08 runner and sealed payload binary before use.
It rereads both files after the child closes.

The wrapper creates a fresh output root.
The reviewed A08 runner owns the nested measurement output.
The runner limits accepted report and failure files to 32 MiB.

The outer wrapper also limits retained reports to 32 MiB.
Its command log has a 16 MiB post-run reader.
The contract accurately says the command log has no active growth cap.

The wrapper preserves the runner record without converting failure into success.
It excludes native behavior, RSS, loaded-vnode identity, media behavior, and product acceptance.

## Conditions for a successor

1. Compile a fresh repaired package with the same fixed authority model.
2. Preserve the current failed compile report and log.
3. Keep the pure test target inside its control-owned stage.
4. Close the harness path identity before and after the exact test.
5. Close the Python path identity before and after the measurement runner.
6. Review each successful stage before creating the next release marker.

No native, product, playback, hearing, or creative acceptance follows from these conditions.

## Exact reviewed source identities

| File | SHA-256 |
| --- | --- |
| `run_payload_compile_a09.py` | `d0f3c43313a9bfe20104c715288969dee260107d1466f89dcda33bdf6ec44c57` |
| `run_payload_control_a09.py` | `56d9ee751ab77c8558d87ce2f54d8f81f391e2a2ffc07fcf6a49f885675c30e4` |
| `run_payload_measurement_a09.py` | `7a512b900341ab51c65b2a4294e75458fd2ea50953b1b917d43181e014143388` |
| `payload_build_common_a09.py` | `f9b6ba6cd1c73f12d6e431669ce262f9d941e8ec8f20c8d251b4e02f49b08952` |
| `payload-build-contract-a09.md` | `d4602d1804b7ca7fdeb784f2cf47b171dbecd0fca2c80dec39ad1da884e4e7af` |
| `prepare_payload_metadata_a09.py` | `ef8d2a1e00adcde39fcc2cd2ebe458cc1412a4cb8cca0342e43d4aa39e929e8b` |
