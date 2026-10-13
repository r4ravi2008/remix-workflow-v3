# Swift compiler-only wrapper A04 source review

## Result

`run_swift_typechecks_a04.py` remains a compiler-only wrapper. It invokes
`swiftc --version` and `swiftc -typecheck`. It does not build or launch a
producer, run a native control, call ImageIO or CoreText, or establish native
text output.

A04 preserves the A03 descriptor, preflight, closure, and failure-publication
model. It adds a manifest-authorized source-control map. Each pure source
control gets an exact ordered Swift command. The optional
`--source-controls-only` mode removes the producer and PNG-control commands
while retaining the compiler-version check and every mapped source control.

## Reviewed identity

| file | bytes | SHA-256 |
| --- | ---: | --- |
| `run_swift_typechecks_a04.py` | 11,174 | `19a816ee48d028a8a951834561e5149aa7f7abff0020770160fbfb67476ac8f5` |

This review read the complete 201-line source. It did not run the wrapper,
invoke Swift, typecheck Swift, call a native framework, or inspect native
output.

## Confirmed source-control binding

Lines 124–138 require a nonempty unique `sourceControls` list and an exact
`sourceControlCompileUnits` key set. Each mapping value must be an ordered,
unique Swift list beginning with its primary source. Every listed unit must be
a manifest file row. The manifest hash and the before/after closure therefore
bind the source-control inputs to the same frozen package as the primary
producer and control.

Lines 144–155 preserve the primary command order and append one command for
each source control in manifest list order. The default runs version, producer,
PNG control, and all source controls. `--source-controls-only` runs version
and all source controls, with no producer or PNG-control command. Lines
170–172 record separate source-control and producer/PNG results, while the
overall state requires every executed step to return zero.

The current A10 manifest has `sourceControls` but no
`sourceControlCompileUnits` field. A04 must therefore remain deferred until
the A11 manifest supplies that exact mapping. This is an explicit input
contract, not evidence that A10 passed A04.

## Preserved safeguards

The A03 safeguards remain intact. `observe()` uses one bounded descriptor with
regular-file, growth, and descriptor-metadata checks. The retained manifest
bytes are parsed and then joined to the initial closure row. The closure covers
the wrapper, Python executable, manifest, compiler, SDK settings, and every
manifest file row.

The wrapper refuses an existing attempt directory. It writes and `fsync`s an
exclusive preflight record before source validation or compiler launch. It
retains source, compiler, timeout, launch, and identity-drift failures after
that record. Final report creation is exclusive, flushed, and synchronized.
Publication failure emits a bounded partial-report identity and the preflight
path. CLI validation, the existing-attempt check, and attempt-directory
creation remain outside the stated preservation boundary.

## Scope limits

The wrapper records `producerStarted`, `controlStarted`,
`nativeFrameworkCalledByProducer`, and `loadedCompilerAttested` as false. Its
file closure and command records do not prove the loaded compiler identity,
Swift type semantics, source-control runtime behavior, shaping, raster output,
or creative acceptance. Log size remains a postprocess read cap, not a child
disk-write cap.

## Disposition

Accept A04 as a source-reviewed compiler preparation successor, conditional on
the exact A11 manifest carrying `sourceControlCompileUnits` and its bound file
rows. Bind any run to this wrapper hash, the A11 manifest hash, ordered primary
and source-control commands, compiler and SDK identities, and a fresh attempt.
No compiler or native execution was performed here.

