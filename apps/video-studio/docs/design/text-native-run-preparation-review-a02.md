# Rust native-run preparation review A02

## Disposition

The corrected Rust A05 native-run preparation is source-ready for root gate authoring.
I found no P1 or P2 defect in the three frozen successor helpers.

This verdict does not authorize the native producer.
Root must still inspect the generated schema-2 gate before any A03 or A04 attempt.

The execution gate and both run directories were absent during this review.
I did not execute a helper, producer, observer, compiler, GPU process, or Resolve process.

## Reviewed correction set

The successor closes all six findings from `text-native-run-preparation-review-a01.md`.

### One gate read

`run_rust_native_probe_a03.py:1216-1252` performs one bounded gate read.
The runner derives the SHA-256 identity and authorization object from those exact bytes.

The runner also reads each bound JSON document once before parsing it.
Each read checks file type, size, SHA-256, and stable descriptor metadata.

### Exact gate authority

`prepare_rust_native_gate_a02.py` builds one role-sorted binding list.
The list has a 4,096-row cap and a domain-separated aggregate.

The gate builder closes these authorities:

- the 15-file A05 source bundle and 14-file pre-lock freeze;
- every source-freeze attachment and the generated `Cargo.lock`;
- dependency files, archives, manifests, features, and direct policies;
- the build gate, build attempt, build command, environment, log, and executable;
- the schema-2 build manifest and observed Mach-O UUID;
- input authority, raw bridge, 21 pure controls, fonts, cases, and license;
- observer source, runtime, helpers, Python executable, and installed package files;
- comparator, runner, sidecar, protocol, synthesis, and review documents;
- toolchain executables, launchers, SDK settings, framework records, and raw logs;
- the separate A05 PNG callback proof and its seven-record closure.

`run_rust_native_probe_a03.py:369-1097` independently reconstructs that role set.
The runner rejects every missing, extra, duplicated, conflicting, or renamed role.

`run_rust_native_probe_a03.py:1100-1213` validates the exact gate schema.
It joins all summary hashes back to their bound role rows.

The runner separately joins the source aggregate, lock, build gate, build manifest, and binary.
It also joins input, observer, comparator, and control evidence.

### PNG callback prerequisite

The gate keeps the PNG callback proof separate from the 21 pure controls.
It binds the helper, report, two step records, logs, test executable, and release-build record.

The exact selected callback test must pass alone.
The report must retain seven identical before-and-after closure records.

The gate recomputes the expected 1,921 identity-check count from current closures.
It also requires an empty identity-error list and exact build and test arguments.

This prerequisite establishes the tested callback boundary only.
It does not establish ImageIO behavior or native text output.

### Child environment

`run_rust_native_probe_a03.py:1302-1386` replaces the inherited environment.
The child receives only `LANG`, `LC_ALL`, `PATH`, and `TZ`.

The exact environment appears in the gate and terminal attempt report.
No caller `DYLD_*`, `LD_*`, framework, Python, or workspace variable reaches the child.

### Exclusive directory ownership

`run_rust_native_probe_a03.py:1580-1709` creates A03 or A04 relative to a retained unit descriptor.
The runner opens the new run directory without following links.

The runner requires `probe-output` and `cancel-marker` to be absent before launch.
It retains the run descriptor until the terminal report is saved.

After producer exit, the runner opens `probe-output` relative to the run descriptor.
It retains the output descriptor through inventory and closure checks.

The runner checks device, inode, and mode at each directory boundary.
It also checks content metadata during run-entry and output inventory scans.

### Active log and terminal bounds

`run_rust_native_probe_a03.py:1302-1386` drains one merged stdout and stderr pipe.
It persists at most 4 MiB in the exclusive log file.

The runner kills and reaps the direct child on timeout, overflow, or exceptional exit.
The read buffer can hold one bounded 64 KiB chunk beyond the persisted allowance.
No byte beyond the allowance is written to `producer.log`.

`run_rust_native_probe_a03.py:1447-1510` bounds output traversal.
The limits cover total bytes, files, directories, and all directory entries.

Traversal uses descriptor-relative, no-follow opens.
It rejects links, devices, sockets, and other non-regular entries.

`run_rust_native_probe_a03.py:1513-1561` counts terminal JSON before file creation.
It then streams the same object through a capped exclusive file.

A report encoding or write failure gets a separate 64 KiB causal record when possible.
A partial full report cannot qualify through the orientation sidecar.

### Post-run closure

The runner reopens every gate binding after the child closes.
It compares path, size, SHA-256, device, inode, mode, modification time, and change time.

The runner also rereads the execution gate.
The before and after gate identities must match exactly.

A zero producer return code does not accept native output.
It records only `native_producer_completed_external_qualification_pending`.

### Build-manifest sidecar authority

`seal_native_orientation_sidecar_a02.py:217-408` requires one clean closed A03 or A04 attempt.
The sidecar accepts a failed producer only when its nonzero return code is the recorded cause.

The sidecar joins the report's complete before-and-after list to the role-sorted gate.
It rereads the source-bundle manifest, schema-2 build manifest, and producer binary.

The build manifest must name the source aggregate and executable SHA-256.
Its Mach-O UUID must equal the gate's observed UUID.

The sidecar records the schema-2 build manifest as `rootBuildClosure`.
It records the execution gate separately as `producer.executionGate`.

The sidecar retains run and output descriptors while rereading all three orientation artifacts.
Each artifact must equal its exact closed-inventory path, size, SHA-256, and metadata.

The sidecar keeps orientation, native, product, watching, hearing, and creative acceptance external.

## Failure behavior

The source preserves these outcomes without upgrading them:

| Failure point | Saved result |
| --- | --- |
| Gate or binding admission | No run directory or producer launch |
| Exclusive run creation | No producer launch |
| Child launch | Causal attempt error when the run descriptor exists |
| Timeout or log overflow | Direct child killed and reaped; attempt fails |
| Nonzero producer exit | Failed attempt may retain exact output evidence |
| Missing or invalid output | Attempt error and failed terminal state |
| Binding or gate drift | `afterErrors` and failed terminal state |
| Full report failure | Exclusive causal fallback when writable |
| Failed or partial report | Sidecar rejects the attempt |

## Bounded residual assumptions

This is a static source review.
It does not establish Python API behavior on the execution host or successful native output.

The gate builder accepts caller-selected review paths under the design directory.
Root must supply the intended accepted reviews and inspect the completed gate.

The timeout controls the one exact direct producer process.
It does not provide process-group supervision for an unreviewed descendant process.

The directory evidence is path-scoped local workflow evidence.
It does not claim protection against a privileged concurrent filesystem adversary.

File `fsync` calls protect completed file writes within the documented scope.
The helpers make no parent-directory crash-durability claim.

The sidecar relies on the reviewed runner's closed attempt record.
It does not independently repeat the runner's entire role reconstruction.

The final gate, native framework calls, producer outputs, and observer reports remain unverified.
Product integration, playback, hearing, lyrics, and creative quality also remain unverified.

This review used the same model family.
It is an independent task read, rather than a blind or cross-family review.

## Exact reviewed identities

| File | SHA-256 |
| --- | --- |
| `prepare_rust_native_gate_a02.py` | `d95cfaa45ee59d36e7ab1b73e06cef1c2f1fdce70b90f5e3be3407360c2000b2` |
| `run_rust_native_probe_a03.py` | `1dcda8040b85c30786456a499c9ffba5a3de4720b47e8eb0fd53fe43fffe6f4d` |
| `seal_native_orientation_sidecar_a02.py` | `ad4a3a835d32195713599483bc3627d1f5d85cefa3e0787203ba5c854b00e22b` |
| `text-native-run-preparation-a02.md` | `cccd90432ba562e0e15a4cc816fd9d6fd7eb9507e77bc1f1fcaa3540ec9ca647` |

