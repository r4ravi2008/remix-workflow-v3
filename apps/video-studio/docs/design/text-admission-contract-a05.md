# Native text admission contract A05

## Scope

A05 is a targeted successor to A03. It preserves A02, A04, and all A01 inputs and reports.
It records the file-read, runtime-identity, proof-mode, producer-source, and padded-mask repairs
that must be reviewed before any helper execution. It does not run a helper, build a producer, or
make a native, product, playback, or creative claim.

The new helper paths are:

- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/verify_input_authority_a03.py`;
- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/verify_orientation_a03.py`.

Current A03 source hashes are:

- input helper: `299beff4972d7d96d9392a3913887b2fc44fb3c9d094b36f598f66955bb21ac1`;
- orientation helper: `4e4a2b70609cf3f68c7e56fda4d5caae107e647f69d15db9c1c07a6caf4ccc99`.

The A02 helpers remain frozen predecessors. A03 reports must use fresh A03 names. An actual-proof
failure targeting an A01 or A02 report path is printed without writing that protected path.

## Race-stable bounded reads

Every bounded input read opens one file descriptor and uses that descriptor for all observations.
The helper performs these steps in order:

1. Open the resolved path for binary reading.
2. Call `fstat` and require a regular file.
3. Reject a size above the limit.
4. Read at most the measured size plus one byte.
5. Call `fstat` again on the same descriptor.
6. Require stable device, inode, mode, size, modification time, and change time.
7. Require that the read length equals the first measured size.
8. Apply the expected byte count and SHA-256 checks.

The helper never calls `Path.read_bytes()` after path metadata inspection. A growth, shrink, or
metadata change is a bounded failure. The Python executable is read through this same path.

## Runtime identity

Actual-proof mode requires a schema-one runtime binding with this shape:

```json
{
  "schema": 1,
  "python": {
    "implementation": "CPython",
    "version": "<platform.python_version>",
    "optimize": 0,
    "executable": {
      "path": "<resolved executable>",
      "bytes": 0,
      "sha256": "<64 hex>"
    }
  },
  "dependencies": {
    "pillow": "<PIL.__version>",
    "numpy": "<numpy.__version>"
  }
}
```

The input helper checks schema, Python implementation, version, optimization flag, executable
path, executable byte count, and executable SHA-256. The orientation helper checks those fields
and the Pillow and NumPy versions. Every report contains `actualProofMode: true` or `false`.
Normal mode remains pre-execution evidence and cannot receive proof credit. The executable binding
is path and byte identity observed before verification. It is not proof that a later process loaded
the same vnode or that a native child inherited the executable.

## Producer source and run binding

The orientation sidecar uses `operation: native_text_orientation_a03` and requires:

```json
{
  "producer": {
    "source": {
      "kind": "swift-source",
      "path": "<Swift source or Rust source-bundle manifest>",
      "bytes": 0,
      "sha256": "<64 hex>",
      "rootBuildClosure": {
        "path": "<root build-closure manifest>",
        "bytes": 0,
        "sha256": "<64 hex>"
      }
    },
    "binary": {"path": "<producer binary>", "bytes": 0, "sha256": "<64 hex>"}
  },
  "run": {
    "id": "<fresh id>",
    "exclusive": true,
    "outputRoot": "<fresh directory>",
    "artifacts": {
      "rawAlpha": {"path": "<raw>", "bytes": 272, "sha256": "<64 hex>"},
      "canonicalAlpha": {"path": "<canonical>", "bytes": 221, "sha256": "<64 hex>"},
      "nativeImagePng": {"path": "<PNG>", "bytes": 0, "sha256": "<64 hex>"}
    }
  }
}
```

`kind` must be `swift-source` or `rust-source-bundle-manifest`. The Rust form binds the complete
source-bundle manifest as one measured input. The root build-closure binding identifies the build
inputs that the root freeze selected. The observer does not claim that one Rust entry file contains
all source, and it does not establish source lifetime.

The observer verifies the source or bundle-manifest bytes, root build-closure bytes, binary bytes,
and all three artifact paths, sizes, and hashes. The three artifacts must be distinct and under the
exclusive output root. Reports retain:

```text
sourceLifetimeEstablishedHere: false
sourceLifetimeScope: source-or-bundle-identity, root-build-closure identity, and exclusive artifact binding only
```

## Padded-mask control override

A05 overrides the A03 control wording for the maximum padded mask. The valid exact maximum is a
positive case:

```text
width=2,049
height=2,047
stride=2,064
charged_bytes=4,225,008
```

The exact charge is `2,064 × 2,047 = 4,225,008` bytes. The paired negative controls use the same
dimensions and stride:

```text
charged_bytes=4,194,303  # visible pixels only; reject before allocation
charged_bytes=4,225,007  # one byte below exact stride charge; reject before allocation
```

The tiny 13×17 orientation sample remains a separate control. Its positive exact-stride charge is
272 bytes. Its 221-byte visible-only and 271-byte one-byte-undercharge cases remain negative.

## Report and failure boundary

A03 reports are bounded to 1 MiB and use exclusive creation. Every report includes the helper
source binding, runtime evidence scope, actual-proof mode, input bindings, and declared mutation
schedule. Failed actual-proof invocations never create an A01 or A02-named report. They either
write a fresh A03 failure report or return a failure record with `written: false` for a protected
path.

The A03 changes close file-read and provenance gaps. They do not establish CoreText feasibility,
Rust representation bounds, native source lifetime, native memory peaks, product rendering,
playback, listening, or creative acceptance.
