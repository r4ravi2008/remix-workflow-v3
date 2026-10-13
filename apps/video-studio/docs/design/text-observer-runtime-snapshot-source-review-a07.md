# Observer runtime snapshot A07 source review

Status: source-only independent review. The A07 helper, attempt, and report
have not run. No import, compiler, native framework, media, GPU, Resolve, or
control process ran.

## Reviewed identities

| File | SHA-256 | Size |
| --- | --- | ---: |
| `freeze_observer_runtime_a07.py` | `eb0cbd3d68de9ff1d41c12170ab127cc5613cc084c73b8d0ee2de54ae65f5b65` | 1006 lines, 39611 bytes |
| `observer-runtime-snapshot-contract-a07.md` | `4b17e50681c612045b3695fbf5019b76ffb5a59e2ceb42d4697cda44eb34f9bb` | 312 lines, 11384 bytes |
| `observer-runtime-snapshot-rationale-a07.md` | `bb8e65cd64abfa6ed56ce9b525e1364b1f6d8e174f4ef307e7a0492fa18156bd` | 83 lines, 4762 bytes |
| A06 to A07 source patch | `eb996a20801f80c3e55d54be31e446e2af531fb46534b514940f052cc6f3f32b` | 464 lines, 19460 bytes |
| A06 to A07 contract patch | `6883646496f9f56cf58fc37d388ed7e07ceb2cfdf81c086e250916a7d180c358` | 129 lines, 7450 bytes |
| A06 to A07 rationale patch | `856219ae6eafba2bfb3537e738701ff3e0b653b6b463911d1eaa2d1fb6bf16b8` | 81 lines, 5545 bytes |

## Result

No P1 or P2 finding remains. A07 closes the A06 failure-only descriptor leak
without changing the A06 input domain, logical caps, or schema.

## Verified repair

`measure_confined_regular` now keeps a just-opened parent descriptor under a
local `try` block. `os.fstat` and endpoint identity validation run before
ownership transfer. Any `BaseException` closes `child_fd` and re-raises. A
successful check appends the descriptor to `parent_chain`, which retains the
existing reverse-order cleanup.

The guard covers both descriptor observation failure and endpoint mismatch. It
does not weaken `O_NOFOLLOW|O_DIRECTORY`, descriptor-relative traversal, or
the parent identity checks after the file read.

## Verified unchanged boundaries

- The helper and attempt names are consistently A07 in source, contract, and
  rationale. No A06 output path remains in the A07 package.
- The report remains schema 3 with the same top-level fields and current
  runtime/package domain.
- The cumulative 8 MiB capture admission remains pre-read and covers the
  runtime manifest, historical closure, both METADATA files, and both RECORD
  files.
- Descriptor-confined RECORD traversal, final-file identity checks, one-entry
  attempt allowlist, held report reread, and post-flush root checks remain in
  place.
- The report still excludes loaded-image identity, standard-library closure,
  dynamic-library closure, runner/comparator execution, native text execution,
  and authorization.
- The contract still states that logical caps do not establish Python
  allocator, RSS, operating-system memory, or total process bounds.

## Review limit

This review establishes source and contract consistency only. It does not
establish current Python, Pillow, NumPy, or runtime report bytes. A later
caller must bind the exact A07 helper, report, package rows, and parent
readback independently.
