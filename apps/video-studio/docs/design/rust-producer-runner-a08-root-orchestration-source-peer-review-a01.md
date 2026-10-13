# Rust producer runner A08 root orchestration source peer review A01

## Disposition

**Rejected for execution.** Three P1 findings and four P2 findings remain in the frozen orchestration snapshot.

The staged-authorization content checks are suitably narrow. They cannot authorize execution or publish a review sidecar.

This review is source-only. I did not import or execute the wrappers or their shared helper. I did not compile, run controls, create a bootstrap, publish a sidecar, launch a child, or use native, media, GPU, or Resolve tools.

## Frozen receipts

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `preparation-receipt-a01.json` | 2,866 | `3f02fcaaa2d1d46f900645c338a84f21a35556466fb6b154d3d354d4ccbfc6b9` |
| `native_runner_a08_source_readback.py` | 6,564 | `833842d2815adc1989fd4196c4ada2200bc33ef95fa953058d0d28a869a5e743` |
| `native_runner_fixed_compile_a08.py` | 8,531 | `d503ec07d751955d92f9a7a38748983e623a087826bf7db6311fe22b92e06d9a` |
| `native_runner_fixed_controls_a08.py` | 7,974 | `b6e7b04a297c41fb9263cfcb84be756a3db97e2d2d83ab1d55e460866923a7c6` |
| `native_runner_a08_staged_authorization_readback.py` | 8,223 | `a2413227c979064fe13820dfd79b46925525819a6279ef9a8a30a67978b4164e` |
| `/private/tmp/native_runner_process_a05.py` | 5,459 | `81d55fe104b310c6d046b3e1f0fef914e3085f88073d07e7014cb302a8241ccf` |

The preparation receipt matches all four frozen wrapper files. It does not bind the shared helper.

## P1 findings

### P1.1: Every wrapper executes the shared helper before authenticating it

Each wrapper reads and executes `/tmp/native_runner_process_a05.py` immediately. The path resolves to the reviewed `/private/tmp` file on this host.

The source wrapper measures the helper only after `exec`. The other wrappers do not compare it with a fixed expected receipt before `exec`.

An altered helper can therefore run before any closure check. A later mismatch cannot undo that execution.

Open the helper once with no-follow flags. Measure the held bytes against the fixed 5,459-byte receipt before compiling those same bytes.

### P1.2: `run_phase` is not exception-safe around an owned child

The shared helper starts the process before selector setup. Selector creation, nonblocking setup, registration, reads, and final `wait(timeout=3)` are outside a cleanup guard.

Any exception can bypass group termination, pipe closure, reaping, and result publication. A final wait timeout also escapes without a causal record.

The compile and controls wrappers call this function without a terminal cleanup wrapper. Their promised single finite attempt can therefore strand a process or lose failure evidence.

Make child cleanup unconditional after `Popen`. Save a bounded causal result for spawn, setup, stream, TERM, KILL, drain, and reap failures.

### P1.3: The controls wrapper accepts only a self-declared state string

`native_runner_fixed_controls_a08.py:137-140` marks the candidate successful when the process closes and `combined.state` has one expected string.

It does not validate exact case IDs, order, group counts, per-case results, pass counts, false scope flags, or launch observations.

The recipe's `case_counts` are copied into preflight data but never joined to the actual report.

An incomplete control binary can therefore qualify itself by emitting the expected state.

Validate the complete fixed control schema and every scheduled group before setting `candidateControlsPassed=true`.

## P2 findings

### P2.1: The four compile commands are not validated as exact commands

The compile wrapper checks command names, rustc path, one source suffix, dependency search paths, and output presence.

It does not validate every argument, each `--extern` mapping, crate type, output argument, compiler flag, or exact environment value.

It also takes stream and output limits from the candidate recipe without enforcing finite fixed maxima.

Root and peer review hashes reduce this risk. The orchestration still claims a fixed-four-command gate and should enforce the complete reviewed vectors.

### P2.2: Process-group evidence is inferred instead of observed

`run_phase` records `processGroupId=process.pid` because `start_new_session=True`. It never reads the live group with `os.getpgid`.

The compile wrapper checks only compiler PIDs after completion. It does not check the four process groups for surviving descendants.

Measure the group while the child is live. Check both PID and group absence after every phase.

### P2.3: Several closure reads reopen pathnames after measurement

The wrappers measure files, then reopen them through `Path.read_bytes`, `read_text`, or `read_bytes` again for parsing.

Examples include manifest parsing, recipe parsing, Rust import scanning, and Mach-O parsing. Before-and-after measurements do not exclude a transient substitution restored before the final check.

Parse the same bounded bytes read from the measured descriptor. Keep the identity stable through parsing.

### P2.4: The control-output inventory is not anchored to a held directory

The controls wrapper traverses `control_root` with `exists`, `iterdir`, `lstat`, and later pathname reopens.

It bounds entries and total regular-file bytes. It does not retain the root descriptor or check root identity before and after traversal.

Hold the control directory descriptor. Use descriptor-relative traversal or verify the held root and every reopened entry before accepting the inventory.

## Checks that are correctly bounded

The source wrapper limits current source rows to 64 and external rows to 128. It reconstructs both framed aggregates and rejects unbound literal Rust imports.

The compile wrapper permits one absent attempt root and stops after the first failed command. It defers bootstrap creation.

The controls wrapper permits one absent control root. It bounds inventory entries to 8,192 and regular-file bytes to 512 MiB.

The staged-authorization helper requires one canonical `0700` run directory. It requires the review sidecar, output, marker, and reports to remain absent.

The staged helper validates all 17 authorization fields. It joins four qualification references, aggregate, producer bytes, command, environment, policies, paths, and false scope flags.

The staged helper creates no authorization, review sidecar, approval, bootstrap, or execution permission. Its saved result remains content review with peer and sidecar pending.

## Scope limit

This review covers the immutable preparation snapshot and the referenced shared helper. It does not review or accept the separate A08 runner candidate.

No wrapper has executed. No compiler, controls, bootstrap, authorization, sidecar, producer, or native result has been observed through this snapshot.

This is a same-model-family, nonblind review. No cross-family reviewer was available.
