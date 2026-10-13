# Swift pure-control runner A03: independent source review

## Scope and frozen identities

This is a read-only source review. I read the complete A03 runner, wire schema, rationale,
source-control module, A02 source review, A02 parent findings, A15 manifest, and the bound
build evidence. I did not import, execute, typecheck, compile, or run a helper, control,
binary, native framework, GPU, or Resolve process.

| Artifact | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `run_swift_controls_a03.py` | 3,015 | 135,472 | `d0d89138412caa6760a72ceb41bea24d61ca2b5a74eb9dc00e83b8eadc3e990c` |
| `swift-control-runner-wire-schema-a03.md` | 294 | 10,943 | `8882a32a98742b8275c84bcbeab37de40ca5268467e603d2c2a7f00d7d59b791` |
| `swift-control-runner-source-rationale-a03.md` | 148 | 6,212 | `43cd99304f3b1c3ccab984c80bd83fb231679e1620777b9dbefa5319b02d3560` |
| `swift-control-runner-source-controls-a03.py` | 926 | 39,183 | `518799ff5379700c01d6b0bd643f1559f7c40d119b29f63206f5f2ec01b38a08` |

The runner binds these accepted inputs:

```text
A15 manifest       0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e
A04 build helper   ba632ed73005d8c3f870d4b7886c3057ae80405071c4f2154469fe090c195886
A02 build report   214864e3d4bc7af8e7698dc3c6ad78f409147a5fffaeabfc8c9898c356fcc3ea
A02 build seal     23cd14ae2a46f5990831cb34e7de9b2dfa959cd642d3aec81381d804c63a97ae
A02 readback       cfc3aa29d7825a1d4d843a297df55e95651dcc0eef76cbbf94f0528f62a2f63a
```

The A02 predecessors remain preserved. Their relevant hashes are:

```text
run_swift_controls_a02.py                    6428e862a455910c4aa495c07336c6f9dfe3d63ab9f1e515f280b64c9a4a6ebb
swift-control-runner-wire-schema-a02.md     b734b36a20be16a2d681fbd6fb0d20f15d704803cdddc92de85256ee1068da24
swift-control-runner-source-rationale-a02.md fc21de1558d4a0fa9970c311bd999ae89ef4b401ccebe6f6dc9c0a39c3beb742
swift-control-runner-source-controls-a02.py 646698d86378bdfcaf2b79958b942cbf5da4fe03ac1bf57cbd4abd4d870d2153
```

## Verdict

No P1 or P2 finding remains in the frozen A03 source package.

A03 repairs the two A02 cleanup findings, the strict numeric-authority finding, and the
source-control coverage finding. The package is source-ready for the separately authorized
source-control gate. It does not authorize native output or loaded-image acceptance.

## Capture liveness and bounded reaping

The capture loop now ends only when both registered capture streams are closed and the direct
child has exited. A leader that exits while a descendant retains a pipe cannot keep the loop
alive indefinitely. Timeout, cancellation, and output overflow establish a termination time,
send `SIGTERM`, send `SIGKILL` after the fixed grace interval regardless of leader state, close
the streams at the fixed drain deadline, and perform one direct-child wait with a one-second
timeout.

The direct-child wait does not claim descendant reaping. A reap timeout is retained as the
specific `direct-child-reap-timeout` condition and prevents a later control from starting.
The success predicate requires a true integer return code, a completed direct-child reap, no
reap timeout, no cleanup errors, and no timeout, cancellation, or output-limit condition.

The source controls exercise this state machine through `run_captured_process` with injected
clock, selector, pipe, read, signal, and process implementations. The retained-pipe leader-exit
case reaches the bounded close deadline. Separate cases cover timeout, cancellation, both output
caps, direct-child reap timeout, and a selector exception. These controls do not launch a child
process, which is intentional and stated in the report boundary.

## Post-launch cleanup

Every exception after `Popen` enters `captureError` and the same cleanup path. Cleanup records
the first capture exception, attempts process-group termination, closes registered and process
pipe handles, records cleanup errors, attempts `SIGKILL` after the bounded grace interval, and
performs the bounded direct-child wait. Selector close and final-clock failures are also retained
as bounded cleanup errors.

The source control's selector-failure case reaches this path and requires both termination
signals, closed selector state, and a successful direct-child reap. A control failure therefore
cannot silently leave the runner's child cleanup unrecorded. The runner preserves partial stdout
and stderr bytes before report publication failure or process failure classification.

## Process-group fallback and claims

`signal_owned_process` records process-group delivery separately from direct-child fallback.
It attempts the owned process group first. If group delivery fails, it checks direct-child
liveness and records a direct-child signal attempt only when the child is still running.
Process-group errors, direct-child errors, and absent-process races remain separate fields.

The source control injects an absent process group and verifies the direct-child fallback record.
Both the runner and schema keep `descendantsReapedAttested` false. The package does not convert a
successful `killpg`, fallback signal, or direct-child wait into a descendant-reaping claim.

## Strict numeric authority typing

A03 applies exact integer checks to manifest schemas, source-control schema-map entries, build
limits, build counts, compiler return codes, seal and readback schemas, authorization schemas,
Mach-O fields, identity fields, and nested binary contracts. `require_typed_equal` recursively
checks types before values for derived manifest contracts and nested arrays and maps. Boolean and
floating-point substitutions cannot pass Python equality against integer authority values.

The source controls exercise both `true` and `1.0` mutations for top-level schemas, schema-map
entries, build limits, build counts, compiler return codes, nested manifest contracts, nested
binary contracts, seal schemas, readback schemas, and authorization schemas. Dynamic control
reports retain their existing strict integer and Boolean validators.

Timestamps remain explicitly finite JSON numbers. That is the only intentional numeric union in
the wire contract, and it is checked by `require_number` rather than raw equality.

## Authority and drift coverage

The runner holds the attempt, build, binary, package, authority-file, runner, helper, and
manifest descriptors through execution. It verifies the current closure, all six binary records,
all seven build logs, selected held-binary descriptors, and descriptor-versus-path observations
before and after the controls. A changed root, source, authority file, log, binary, or build
closure produces a preserved identity-drift result and stops later controls.

The source controls replace a held directory and a held Mach-O pathname in disposable scratch
state. The old descriptors remain observable, while replacement path observations fail. The
control loader reads the exact bounded runner bytes, compiles those bytes directly, and installs
the rejecting `subprocess.Popen` sentinel before executing module definitions. It does not reopen
the runner through an import loader.

## Boundaries that remain honest

The source controls execute the actual capture function, but they do not run `main`, launch a
compiled control, or exercise real pipe and signal delivery. The A03 package therefore preserves
the following false or unestablished boundaries:

- no loaded Python, compiler, SDK, or produced-binary image attestation;
- no descendant-reaping attestation;
- no bound Python JSON parser or encoder heap peak;
- no native framework, ImageIO, CoreText, CoreGraphics, GPU, or Resolve observation;
- no native text, media, playback, hearing, film-quality, or creative-acceptance claim.

Those are qualification limits, not defects in the A03 source-only runner contract.
