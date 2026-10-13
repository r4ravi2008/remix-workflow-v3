# Text pure-control source review A02

## Verdict

This was a read-only source review. I did not execute a helper, control, build, or native API.

I found no P1 defect. `control_runner_a02.py` closes the six blockers from the A01 control review.
It is suitable for one isolated, non-native actual-proof run with the frozen A02 bindings below.

One P2 evidence-labeling defect remains in `verify_orientation_a05.py`. It blocks an A05 native
orientation report from serving as proof. It does not block the runner's synthetic orientation controls.

No reviewed source establishes producer execution, source lifetime, native text behavior, product behavior,
playback, listening, or creative acceptance.

## P2 — the orientation success scope still omits measured identities

The helper separately reads and reports the producer source or source-bundle manifest, root build closure,
producer binary, and three artifacts. The successful scope fields still say only:

```text
source/binary path identities and sidecar exclusive declaration only
```

This wording appears in `sourceLifetimeScope` and `producerEvidenceScope`. It does not name the measured
root-build-closure identity. It also leaves the three measured artifact identities implicit.

The frozen A03 review required the scope to name the source or bundle, root build closure, and producer
binary separately. A successor should use that explicit wording. It may also name the three distinct
artifact pathname identities.

This is an evidence-label defect. The helper correctly keeps these stronger claims false:

- producer binary execution;
- run exclusivity;
- native producer source lifetime.

The new `producerBinaryPathIdentityEstablishedHere` and `exclusiveRunDeclaredBySidecar` fields otherwise
match the implemented observations. Failure reports correctly leave both fields false.

## Closed A01 control findings

The A02 runner closes all six prior control findings.

1. It verifies the runtime binding and dependency closure before importing either A05 helper. The closure
   binds the runner, both helpers, and runtime-binding JSON by resolved path, byte count, and SHA-256.
2. The optimizer control requires exit code `1`, report state `failed`, and error `optimized_python`.
   The A05 input helper checks optimization before comparing the optimization-zero runtime binding.
3. The positive license control calls `verify_license`. The mutation uses the helper's bounded reader with
   the exact 4,377-byte length and frozen SHA-256.
4. The positive 13-by-17 synthetic raw plane fills all 51 padding bytes with `0xA5`.
5. Five synthetic mutations exercise raw-row reversal, padding, canonical bytes, PNG alpha, and PNG size.
6. Late failures retain completed controls, a bounded causal error, and available before/after input maps.

The runner snapshots the manifest, cases, repository record, OFL file, and both font files before controls.
It rehashes the same canonical paths afterward. Copy mutations use exclusive files under a fresh output
directory. A failure before the first snapshot truthfully leaves those maps unavailable.

The stride arithmetic is also correct. The 2,049-by-2,047 case accepts 4,225,008 bytes with stride 2,064.
Charges of 4,194,303 and 4,225,007 reject. The small 13-by-17 cases remain independent controls.

## Narrow execution admission

The frozen schema-one control closure binds the exact reviewed runner, helpers, and runtime-binding file.
It also references the full observer dependency closure. I rehashed all three closure files without running
their code. Actual-proof mode must receive the control closure, runtime binding, and a new output directory.

| Frozen binding | SHA-256 |
| --- | --- |
| `observer-runtime-binding-a02.json` | `7917d0890987f83568817a56bada908bfd6ca0eec0ae49ffb3fd28957dc067da` |
| `observer-runtime-closure-a02.json` | `fd363f9da43be57ffa0c2a15c540f1b7ca2821496e6a419bcee9f4f6b8bfe12f` |
| `control-source-closure-a02.json` | `2601b8c2bda792a4d834e622189db35a563840f131c8abf505973db3b50ce7f8` |

The runner directly measures the control closure's runner, helper, and runtime-binding entries before
imports. The full dependency closure remains documentary path identity. It is not loaded-module proof.

That run can establish the behavior of these pure helper controls in the bound Python environment. Its
synthetic PNG does not establish Core Graphics output, producer execution, or native orientation.

The A05 orientation helper needs the P2 scope correction and a separately frozen producer sidecar before
proof-bearing execution. The later producer closure must establish actual execution and exclusivity.

## Reviewed identities

| Item | SHA-256 |
| --- | --- |
| `verify_input_authority_a05.py` | `1e6486979e511cc44af89d0ca5381ecd9e5c7840c8183b34b8301ab197684b50` |
| `verify_orientation_a05.py` | `f36df59d6c588f183a8e11ccba2ec637cb217b892e3328f2c7a6a9ac939f910f` |
| `control_runner_a02.py` | `44922cc7241bfaa617d04217dcdcf356f7c37fc2180d5f45f2f00e22ec750734` |
| `text-admission-contract-a07.md` | `3c8c78be61aa2cae49ed3e7f6b154be2e2913560f816b76c56977a8f7cb2fb79` |

The preserved A04 helpers and A01 runner remain byte-distinct predecessors. No reviewed source or frozen
input was modified during this review.

This is a same-model-family review. No cross-family reviewer was available.
