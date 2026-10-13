# Text observer source review A03

## Disposition

This is a source-only review. I found no P1 defect.

The A03 helpers close the three earlier P2 findings. Two narrow P2 evidence-labeling defects remain before proof-bearing execution. Preserve A01, A02, and A03. Correct both defects in a new successor.

After those corrections, the input-authority helper is suitable for the scheduled isolated non-native observer controls. The orientation helper still needs an actual frozen producer sidecar. A separate producer closure must establish which binary executed and whether the producer run was exclusive.

This review does not accept native text feasibility, product integration, rendered output, or creative quality.

## Remaining findings

### P2 — A read can be reported under a second pathname resolution

Both helpers resolve the pathname before opening one file descriptor. They read through that descriptor and compare its complete `fstat` identity before and after the read.

However, `read_bounded` returns `binding(path, data)`. The `binding` function calls `path.resolve()` again after the descriptor closes. A pathname substitution during that interval can relabel the captured bytes with a later resolution.

The orientation helper also checks each artifact path against `outputRoot` before reading. It does not require the later measured binding path to equal that prevalidated resolved path.

The successor must capture one resolved pathname before opening the descriptor. It must return that exact captured string without resolving it again. Each orientation artifact binding must equal its prevalidated path and remain under the captured output root.

This correction binds the report label to the observed descriptor read. It does not establish exclusive pathname ownership or source lifetime.

### P2 — Orientation provenance does not separate declarations from established facts

The orientation helper verifies the producer binary's current pathname bytes. It also requires the sidecar field `run.exclusive` to be true.

The report then emits `producer.binary` and `run.exclusive: true`. Its scope text does not state that actual binary execution and run exclusivity remain unproved here. The `sourceLifetimeScope` text also omits the producer-binary pathname identity that the helper does establish.

The successor must report these boundaries explicitly:

- `producerBinaryPathIdentityEstablishedHere: true`
- `producerBinaryExecutionEstablishedHere: false`
- `exclusiveRunDeclaredBySidecar: true`
- `exclusiveRunEstablishedHere: false`
- `sourceLifetimeEstablishedHere: false`

The scope must name source or bundle pathname identity, root-build-closure pathname identity, and producer-binary pathname identity. It may also name the three distinct, sidecar-declared artifact paths.

The later producer freeze and run closure must establish actual execution and exclusivity.

## Closed earlier P2 findings

The A03 source closes the three original review findings.

1. Proof-bearing checks use `require` and bounded `ValidationFailure` records. Python optimization cannot remove these checks.
2. Input authority now reads the actual `OFL.txt`. It requires 4,377 bytes, SHA-256 `0dab92d0544f7b233403f14b84a663bdbfa746982eda629e7f4f9ffe1b036feb`, repository `notofonts/noto-fonts`, and commit `ffebf8c1ee449e544955a7e813c54f9b73848eac`.
3. Actual proof mode requires a frozen runtime binding. The helpers bind runtime versions, executable pathname bytes, producer source, root build closure, producer binary, and named artifacts. They keep native, lifetime, product, watching, hearing, and creative claims false.

The bounded reader uses one open descriptor for each file. It checks regular-file type, size limit, complete measured read, and stable device, inode, mode, size, modification time, and change time. The first remaining P2 concerns only the later pathname label.

The input helper also recomputes the declared font-table observations and deterministic face fingerprint. This is container evidence. It does not claim an observed native font face.

The orientation helper independently compares the 272-byte raw plane, 221-byte canonical plane, and PNG alpha plane. Its checks cover row reversal, all 51 padding bytes, rectangle orientation, PNG decoding, and alpha equality.

The small admission controls are correct. A 13×17 mask with stride 16 accepts an exact 272-byte charge. Charges of 221 and 271 bytes reject.

## Runtime and execution boundary

The frozen observer runtime records CPython 3.12.14 with optimization disabled. It records Pillow 12.3.0 and NumPy 2.3.5. The evidence scope is pre-execution pathname identity, not loaded-vnode or process-memory identity.

The runtime closure records `nativeTextExecution: false` and `observerProofExecuted: false`. I did not run either helper, build native code, or invoke a native API.

The 2049×2047 padded positive case belongs to future pure admission testing. Its exact stride charge is 4,225,008 bytes. Only an undercharged permit is a negative case. Its absence from these observer helpers is not a defect or an implementation claim.

## Reviewed identities

| Item | SHA-256 |
| --- | --- |
| `verify_input_authority_a03.py` | `299beff4972d7d96d9392a3913887b2fc44fb3c9d094b36f598f66955bb21ac1` |
| `verify_orientation_a03.py` | `4e4a2b70609cf3f68c7e56fda4d5caae107e647f69d15db9c1c07a6caf4ccc99` |
| `text-admission-contract-a04.md` | `622c6407e8e62793aabbde85369b92d2245ad8f43efb9b2d0703c4cb2908602c` |
| `text-admission-contract-a05.md` | `901c9bd06e4d10d9019bf2f7e8b3785f479b144f998b2dc635a330e8a17f0d7a` |
| `observer-runtime-binding-a01.json` | `7917d0890987f83568817a56bada908bfd6ca0eec0ae49ffb3fd28957dc067da` |
| `observer-runtime-closure-a01.json` | `f5290f7d01db519e1a8fe1a809f92c879cc88560f877fccee7150b6b1902d7ca` |
| `freeze_observer_runtime_a01.py` | `822a523f1ffa51b82d4d86142a4860382ed99db1cb59acb2ec5184c5f3992565` |

## Verdict

There is no P1. The original three P2 findings are closed.

The two remaining P2 corrections are required before proof-bearing execution. After correction and the predeclared control schedule, the isolated raw observer and pure controls may proceed against the frozen runtime. Native text integration and output acceptance remain pending.

This is a same-model-family review. No cross-family review was available.
