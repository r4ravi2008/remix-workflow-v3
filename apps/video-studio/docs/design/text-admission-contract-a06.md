# Native text observer contract A06

## Status

A06 is a narrow successor to A04. It preserves A03, A04, and all frozen input files. It adds
descriptor-path truth, explicit producer execution scope, A04 naming, and one unexecuted pure
control runner. No native producer, build, GPU, Resolve, product, or helper execution belongs to
this revision.

New files:

- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/verify_input_authority_a04.py`;
- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/verify_orientation_a04.py`;
- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/control_runner_a01.py`.

Current hashes are:

- input helper: `c89ac8816709972d1491e22d08731a6c1f89d1b002bd62278e7d27f0a6e4446d`;
- orientation helper: `fe25a49e6a1fade97209253ad8ab2ac05a5466467c7969b3573b73206292c69b`;
- pure control runner: `c4588c78263c159c08631ee608b1720a3aa7fceef21ed7b7bf377908684e10d2`.

Actual-proof reports and orientation sidecars must use fresh A04 names. A04 rejects A01, A02, and
A03 report or sidecar names in actual-proof mode. A rejected protected path receives no failure
report. A fresh A04 failure path may receive a bounded report.

## Exact captured paths

`binding(path, data)` returns the path already resolved before the file descriptor opened. It does
not call `resolve()` after the descriptor closes. The read helper opens one descriptor, performs
the bounded read, checks pre-read and post-read `fstat`, and passes that same resolved path to
`binding`.

Orientation artifact containment uses the path in each returned measured binding. It checks that
captured path against the resolved sidecar `outputRoot`. It checks distinctness after capture.
The observer therefore reports the path it actually measured rather than a separately resolved
caller string.

## Producer execution scope

The orientation report explicitly contains:

```text
producerBinaryExecutionEstablishedHere: false
exclusiveRunEstablishedHere: false
sourceLifetimeEstablishedHere: false
sourceLifetimeScope: source/binary path identities and sidecar exclusive declaration only
```

The sidecar still binds the producer source or Rust source-bundle manifest, root build closure,
producer binary, and three distinct artifact files. Those hashes establish inputs and declared
paths. They do not prove that the binary executed, that the run created the exclusive directory,
or that the PNG came directly from the native source snapshot. A later root-owned run-closure
record must establish execution and exclusive creation.

The sidecar operation is `native_text_orientation_a04`. The source kind is `swift-source` or
`rust-source-bundle-manifest`. The Rust form binds the complete bundle manifest plus the root build
closure. It does not describe a single Rust entry file as the complete source.

## Pure control runner

`control_runner_a01.py` is a separate pure harness. It imports explicit A04 validation functions
and uses bounded copies in a newly created exclusive output directory. It never writes canonical
inputs. It records every original input path, byte count, and SHA-256 before and after controls.

The control schedule includes:

- positive 2,049×2,047 padded charge `4,225,008`;
- negative padded charges `4,194,303` and `4,225,007`;
- separate 13×17 exact-stride, visible-only, and one-byte-undercharge cases;
- raw font-source byte, table byte, OFL byte, text byte, range, and Q16-size mutations;
- explicit expected `ValidationFailure.code` values;
- a `python -O` subprocess control that must fail and write a bounded failure report;
- a synthetic PNG orientation check labeled `synthetic-neverNativeproof`.

The synthetic PNG control reports `sourceExecutionEstablishedHere: false`,
`binaryExecutionEstablishedHere: false`, and `nativeProducerRunEstablishedHere: false`. It makes
no producer, native, or source-lifetime claim.

Actual-proof mode accepts only the frozen A04 helper constants and fresh output paths. It cannot
replace baseline hashes, redirect canonical inputs, or select a pre-existing output directory.
Every control report is bounded and created with exclusive file creation. Unexpected passes,
wrong failure codes, optimizer-control passes, and before/after input hash changes fail the runner.

The runner remains design-time source. Root must read and freeze it before any control execution.
