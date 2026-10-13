# Focused comparator runner A01 — root source review

A01 is preserved and rejected before import or execution. Root read the complete 2,962-line source and all four package documents. All four manifest rows and the separate manifest identity match current files. Independent source review remains a separate required result.

## Frozen source

- Source: 147,302 bytes; SHA-256 `f8dee802b2e673c8819ecccf3daef6d9eef0d0ea0522df8ff92154d971c4d3eb`.
- Contract: 8,138 bytes; SHA-256 `4c1c48a12500ec5ddc9705fd99b3dc688abbae3654d0a645def3d7c1549c79d5`.
- Output schema: 3,108 bytes; SHA-256 `86ced09a43efcd55283d1edbb51204c56e03fff97e0bc34268de9dd841638e52`.
- Rationale: 2,780 bytes; SHA-256 `10a66f8982bb593c5e218e676e044ffc921c34f55b4c746ab348a52f100ef0b4`.
- Manifest: 2,679 bytes; SHA-256 `e47bb19f385ab07bccc4795b2f8eb27fbf18ead3b565a6018593dce914708877`.

## Findings

### P1 — ordinary macOS paths fail the production type guards

`BoundDirectory.open` at line 2197 requires `type(path) is Path`. `UNIT` is created by `pathlib.Path`, which returns a concrete `PosixPath` on macOS. The exact-type guard therefore rejects the fixed unit directory before creating an attempt. `run_captured_child` at line 1951 repeats the same guard for its temporary directory. Both guards must accept the concrete filesystem Path type while preserving the absolute-path requirement. A no-child control must cover an ordinary `Path(...)` argument through the actual held-directory and fake-capture seams.

### P1 — capture timestamps cannot enter any canonical result

`_capture_event` at line 1833 publishes float monotonic seconds. The capture record also stores float start and finish times at lines 1994 and 2176. `_to_codec_json` at lines 1588–1596 rejects floats, consistent with the frozen output schema. The success report, failure report, and publication seal all include the capture record. Thus a completed child cannot publish a result; its failure fallback encounters the same serialization error. Preserve the no-float codec. Convert retained timestamps to a declared exact integer time unit. Use no-child fake capture controls to serialize successful, deadline, cancellation, and setup-failure records through each applicable publication owner.

### P2 — early direct-child exit loses the owned process-group target

After Popen succeeds, the runner creates a selector before calling `getpgid` at line 2045. `process_group` remains None until that call succeeds. A direct child can exit before `getpgid`, while a descendant retains the pipes. The lookup then fails. Exceptional cleanup attempts only direct-child fallback because no process group was retained. The descendant can survive cleanup. The fixed `start_new_session=True` launch establishes the expected group as the direct PID. Retain that positive PID as the owned group immediately after launch. Verify the live observed PGID equals that PID when available. Add a fake-backend control for the exited-parent lookup race and separate observations for group and direct-child cleanup.

### P2 — nested exact types are not enforced by typed_equal

`typed_equal` at lines 434–436 validates only the outer type before Python equality. Python considers True equal to 1 and False equal to 0 inside containers. For example, `validate_a09_structure` at line 1123 accepts integer safePath=1 and boolean isolated=True. The same shortcut applies to nested closure and authorization scope dictionaries. The fixed A09 raw hash prevents these mutations in normal bundle binding, but the public structural seam does not meet its strict nested-type contract. Compare nested dictionaries, lists, and tuples recursively with exact leaf types. Add field-specific no-child controls for boolean/integer substitutions in report flags and authorization scope.

## Retained scope

The review confirms source structure only. Root did not import the runner, codec, helper, or child. Root did not run any runner control, comparator child, native producer, GPU operation, Resolve operation, or media review. No execution authorization or accepted native authority was created. Rust producer qualification remains independent of comparator evidence and still requires its own stage-specific qualification.

A successor must preserve A01 and repair these findings together with the independent review. A01 source must not be edited after this review.
