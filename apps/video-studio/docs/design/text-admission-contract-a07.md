# Native text observer contract A07

## Scope

A07 is a narrow successor to A06. It preserves A01 through A06, all frozen inputs, and every
unexecuted report. It adds the A05 helper names, truthful successful path fields, and the A02 pure
control runner. No helper, control, build, native, GPU, Resolve, product, or provider execution was
performed.

New source files:

- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/verify_input_authority_a05.py`;
- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/verify_orientation_a05.py`;
- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/control_runner_a02.py`.

Current source hashes are:

- input helper: `1e6486979e511cc44af89d0ca5381ecd9e5c7840c8183b34b8301ab197684b50`;
- orientation helper: `f36df59d6c588f183a8e11ccba2ec637cb217b892e3328f2c7a6a9ac939f910f`;
- control runner: `44922cc7241bfaa617d04217dcdcf356f7c37fc2180d5f45f2f00e22ec750734`.

Actual proof requires A05 report and sidecar names. The orientation operation is
`native_text_orientation_a05`. A01 through A04 paths are rejected for actual proof and never
receive failure reports.

## A05 orientation success scope

After the sidecar source, root build closure, binary, and three artifact bindings pass, a successful
orientation report records:

```text
producerBinaryPathIdentityEstablishedHere: true
exclusiveRunDeclaredBySidecar: true
producerBinaryExecutionEstablishedHere: false
exclusiveRunEstablishedHere: false
sourceLifetimeEstablishedHere: false
```

The two `true` fields mean that the observer measured the declared binary path and read the
sidecar's `exclusive: true` declaration. They do not establish binary execution, directory
exclusivity, or native source lifetime. Failure reports use `false` for both successful-path
fields.

## Pre-import identity closure

Actual-proof control execution requires two schema-one JSON inputs before importing either A05
helper or starting the optimizer subprocess.

The runtime binding uses the existing A05 schema and includes Python implementation, version,
optimization flag, executable path/bytes/SHA-256, Pillow version, and NumPy version. The control
runner reads the executable and package distribution versions before helper imports.

The closure binding has this shape:

```json
{
  "schema": 1,
  "runner": {"path": "<control_runner_a02.py>", "bytes": 0, "sha256": "<64 hex>"},
  "helpers": {
    "input": {"path": "<verify_input_authority_a05.py>", "bytes": 0, "sha256": "<64 hex>"},
    "orientation": {"path": "<verify_orientation_a05.py>", "bytes": 0, "sha256": "<64 hex>"}
  },
  "runtimeBinding": {"path": "<runtime-binding.json>", "bytes": 0, "sha256": "<64 hex>"}
}
```

The runner opens and hashes the runner, both helpers, and the runtime binding before importing the
helpers. Actual-proof mode requires both binding paths. Normal mode can remain unbound and reports
`actualProofMode: false`.

## A02 control guarantees

The A02 runner uses fresh exclusive output directories and bounded reports. It records canonical
input path, byte count, and SHA-256 maps before and after controls, including failure paths. It
preserves completed controls and the causal error when a later baseline, helper, or dependency
step fails.

The positive synthetic orientation buffer fills all 51 stride-padding bytes with `0xA5`. Synthetic
negative controls cover one visible raw row, one padding byte, one canonical byte, one PNG alpha
byte, and PNG dimensions. These results are labeled `synthetic-neverNativeproof`.

The optimizer control requires exit code `1`, a bounded report with state `failed`, and error code
`optimized_python`. It records the report binding and truncated subprocess output.

The positive license control calls the A05 helper's real `verify_license` path. The mutated license
control calls the A05 helper's real bounded reader with frozen count `4,377` and SHA-256
`0dab92d0544f7b233403f14b84a663bdbfa746982eda629e7f4f9ffe1b036feb`. It does not duplicate the
license predicate in the harness.

Input mutations remain copies: raw source-font byte, table byte, text byte, line range, and Q16
size. Actual-proof mode cannot replace frozen constants or redirect canonical input paths.

The padded-mask controls remain positive at `2,049×2,047`, stride `2,064`, charge `4,225,008`.
Charges `4,194,303` and `4,225,007` remain negative. The 13×17 stride controls remain separate.

No control result establishes native execution, source lifetime, product behavior, playback,
listening, or creative acceptance.
