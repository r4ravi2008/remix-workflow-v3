# Rust native-run preparation review A03

## Disposition

The successor closes the A02 `steps` alias defect.
The builder, runner, and sidecar remain fail closed for their stated source-only scope.

One P2 comparator-closure defect remains.
Do not author `rust-native-execution-gate-a03.json` until that defect has a preserved successor repair.

The A02 and A03 gates were absent during this review.
The A03 and A04 run directories were also absent.

I did not execute a helper, control, producer, observer, compiler, GPU process, or Resolve process.

## P2: the gate omits the actual-comparator control proof

The selected package is reconstructed as four fixed roles.
Those roles cover the comparator, schema, rationale, and `required-evidence-control-aNN.py`.

The current comparator contract describes that required-evidence control as a synthetic obligation model.
It separately names `actual-comparator-control-a02.py` as the control that imports the real comparator.

The A02 comparator review rejected replica-only controls.
It required a bounded control against the actual comparator validators.

`prepare_rust_native_gate_a03.py:96-122` cannot bind that actual-control source.
It also cannot bind an accepted control result, runtime closure, or source closure.

`run_rust_native_probe_a04.py:129-155` reconstructs the same incomplete four-role set.
Its exact-role check therefore treats the omitted proof as outside the gate.

This defect does not accept native output.
The gate and attempt keep all result-acceptance fields false.

The defect weakens the stated comparator prerequisite and later reproducibility.
A reviewed comparator source can drift from the actual-validator control evidence without invalidating this gate.

Use an exact comparator package manifest, or add explicit roles for these records:

- the actual-validator control source;
- its accepted result;
- its runtime and source closures;
- the comparator review that names those exact identities.

The runner must reconstruct those roles independently.
The gate joins must bind their hashes before any native child starts.

The selected comparator must also support the accepted Swift schema-5 producer and `successfulRaster` records.
The in-progress A03 comparator package was not stable during this review.
It is not part of this review's accepted identity set.

## Confirmed A03 corrections

### Release and PNG-control steps

The builder keeps `release_build_steps` and `png_control_steps` separate.
The runner independently uses the same two names.

Later release command and environment checks use `release_build_steps`.
The fatal A02 variable overwrite is closed.

### Comparator package reconstruction

The package path must be absolute and resolve under the bounded unit.
Its basename must match `text-report-comparator-aNN`.

The builder derives each fixed role from the same version suffix.
The runner reconstructs those paths from `gate.comparatorPackage`.

The runner checks four separate hash joins.
It also rejects missing, extra, conflicting, or renamed gate roles.

These checks correctly bind the four declared files.
They do not close the P2 actual-control omission.

### Gate and build authority

The inherited schema-2 checks remain intact.
They join the source freeze, source bundle, lock, dependency closure, build gate, build manifest, and executable.

The runner re-parses every bound JSON record from one descriptor read.
It reopens every binding after the child closes.

The before and after records include hashes and stable file metadata.
Any recorded drift makes the attempt fail.

### Log and output bounds

The child receives only the four declared environment variables.
The direct child's merged output is drained through a 64 KiB read buffer.

Only 4 MiB can reach the exclusive log.
Overflow, timeout, and exceptional terminal paths kill and reap the direct child.

Output traversal uses descriptor-relative, no-follow opens.
It bounds bytes, files, directories, and total entries.

The traversal rejects links and other non-regular entries.
Directory and file identities remain checked during each bounded read.

### Terminal failure behavior

The runner counts terminal JSON before creating the report.
It streams the report through an exclusive descriptor under a 16 MiB cap.

A report encoding or write failure attempts a separate 64 KiB causal file.
A partial full report cannot qualify through the sidecar.

Gate admission fails before run-directory creation.
Run creation fails before the native child starts.

A clean zero exit records only external qualification pending.
A nonzero exit remains a preserved failure.

### Orientation sidecar

The A03 sidecar differs from A02 only by the gate path.
It requires a clean, closed A03 or A04 attempt.

It joins the complete binding list, schema-2 build manifest, executable, and execution gate.
It rereads the three orientation artifacts through retained directory descriptors.

A failed producer is eligible only with a causal nonzero return code.
Timeout and log-overflow attempts remain ineligible.

The sidecar keeps native, product, watching, hearing, and creative acceptance false.

## Bounded residual assumptions

This is a static source review.
It does not establish Python API behavior or successful native output.

Root must supply the intended accepted reviews.
The helpers validate their locations and identities, not the reviews' prose verdicts.

The timeout supervises one exact direct child.
It does not supervise an unreviewed descendant process group.

The directory evidence is path-scoped workflow evidence.
It is not privileged-filesystem attestation.

File `fsync` covers the completed file writes.
The helpers make no parent-directory crash-durability claim.

The final gate, native framework calls, producer outputs, comparator result, and observer result remain unverified.
Product integration, playback, hearing, lyrics, and creative quality also remain unverified.

This review used the same model family.
It was an independent task read, rather than a blind or cross-family review.

## Exact reviewed identities

| File | SHA-256 |
| --- | --- |
| `prepare_rust_native_gate_a03.py` | `ed4d9270c76a1e1dec09b13045880fd35c1490a7414858c5d9e5446a62fd86d2` |
| `run_rust_native_probe_a04.py` | `dd25907f30c95ef2936550dbe1cce4f2f0e53fe799e4d5b7baccdab640171e82` |
| `seal_native_orientation_sidecar_a03.py` | `89588898bec61d2f8a5b57011fab84bb045847b8e96c0ac673993aa284dcdb2e` |
| `text-native-run-preparation-a03.md` | `d2e38ec37da2c654185f7fa1d151b599c7310fe28ef63a4f8fd643a9acb172be` |
