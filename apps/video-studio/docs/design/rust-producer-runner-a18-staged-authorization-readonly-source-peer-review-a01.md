# A18 staged-authorization reader source peer review

This is a source-only review. I did not import, execute, compile, or launch the A18 reader, bootstrap, staged binary, controls, or native provider.

## Reviewed identities

- A18 reader: `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a18-staged-authorization-readonly-root-a01.py`
  - 19,313 bytes
  - SHA-256 `3b9fbdd57b81ce6cb9c35e902a9c2d9792ddf5691db6b1d0456bbc66f30f458c`
- A17 predecessor:
  - 19,313 bytes
  - SHA-256 `e5304c1a5637c625f4580763df00f398bede920f198c3e84f3afed2a50d65ba1`
- A18 parent review:
  - 1,418 bytes
  - SHA-256 `8044b4918f7d6eac536bb1aa42a2f4e068254d5e229f5c85dd807de3d45108ce`

## Fixed-label comparison

The A18 source differs from A17 in exactly eight package labels:

1. The package root changes from `rust-producer-runner-a17` to `rust-producer-runner-a18`.
2. The first-attempt output root changes to A18.
3. The bootstrap root changes to A18.
4. The source manifest path changes to A18.
5. The staged binary path changes to A18.
6. The bootstrap state changes to the A18 label.
7. The manifest path inside the expected bootstrap object changes to A18.
8. The binary path inside the expected bootstrap object changes to A18.

I reversed those replacements in a separate text comparison. The result is byte-identical to the A17 reader. Both sources parse successfully with Python's AST parser. Their function and class inventories are identical. The seven complete SHA-256 literals are identical and remain protected.

## Preserved behavior

The reader retains the accepted bounded behavior:

- It reads regular files with `O_NOFOLLOW|O_NONBLOCK` and held-descriptor identity checks.
- It caps input JSON at 16 MiB and file reads at 512 MiB.
- It rejects duplicate JSON keys and nonfinite JSON values.
- It requires the exact three-argument digest shape.
- It checks the staged authorization path, output-parent and run-directory anchors.
- It requires exactly 17 authorization fields through the expected authorization object.
- It checks the exact command, environment, process policy, output policy, cancellation policy, and qualification references.
- It checks the held manifest, bootstrap, staged binary, production binary, and helper identities.
- It requires the staged run to contain only `authorization.json` and no review sidecar, report, probe output, or cancel marker.
- It writes only the new A18 readback path through an exclusive descriptor after all checks.
- It retains false native, product, loaded-runtime, watched, heard, and creative flags.

The source imports only Python standard-library modules. It has no project import, subprocess API, process-launch call, compiler call, provider call, or native/media operation.

## Disposition

I found no new P1 or P2 issue in this fixed-label A18 adaptation. The A18 source package, bootstrap, binary, and staged authorization remain pending separate review and execution gates. This review provides source evidence only.
