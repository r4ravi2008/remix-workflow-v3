# Observer runtime snapshot A06 source review

Status: source-only review. The A06 helper, attempt directory, and report have
not run. No import, compiler, native framework, media, GPU, Resolve, or control
process ran.

## Reviewed identities

| File | SHA-256 | Size |
| --- | --- | ---: |
| `freeze_observer_runtime_a06.py` | `474ea7b97da675b0499598b297d8860b413297dac7bf6bf57b7f4f236b217ed0` | 1002 lines, 39483 bytes |
| `observer-runtime-snapshot-contract-a06.md` | `c742514d5c25c0b923fee9a86e1d9f6d718af9043e1f819ff2fcdfd793641b45` | 310 lines, 11150 bytes |
| `observer-runtime-snapshot-rationale-a06.md` | `f81424d7989cff2c93072aa0e777f2cca56ff6fa075bbca954a4c1cf60a0a9b7` | 81 lines, 4569 bytes |
| A05 to A06 source patch | `49dfc40a4afbc73ad23155c25d005c52b6d82906e9efdfeb2b428a224e70da70` | 464 lines, 19460 bytes |
| A05 to A06 contract patch | `c38333fa874830ec20e25dbf575c25ab828dce4f917ce4378fc21278c2144572` | 129 lines, 7450 bytes |
| A05 to A06 rationale patch | `c33c7a41f66318a4429f96d5dd5f6822ab5d2419651e8862d2a557a54d09520f` | 81 lines, 5545 bytes |
| Preserved A05 review | `a8520f8bf027cc238ccfeb8e9be460d7792fd89ca96f9457e1305edd8d7e4e51` | 94 lines, 4900 bytes |

The A06 attempt and report paths are absent. This review binds source and
contract identities only. It does not bind an observed runtime snapshot.

## Finding

### P2-1: A failed confined parent check can leak one descriptor

In `measure_confined_regular`, lines 314-333, A06 opens each parent directory
with `os.open`. It calls `os.fstat` and the endpoint identity check before it
appends the descriptor to `parent_chain`. If either call or the `require` at
lines 325-329 fails, `child_fd` is absent from `parent_chain`.

The `finally` block at lines 390-394 closes `descriptor` and only the child
descriptors already appended to `parent_chain`. The just-opened `child_fd`
therefore remains open on that failure path. This is failure-only for the
standalone helper, and it does not make a successful snapshot incorrect, but it
violates local descriptor ownership and could matter if the function is reused
in a longer-lived process.

Before execution, close `child_fd` through a local ownership guard whenever the
open succeeds. Transfer ownership to `parent_chain` only after the identity
check passes, or append a tracked entry immediately and remove it only after a
successful transfer. Preserve the existing no-follow flags and endpoint
comparison.

No P1 finding remains from this review.

## A05 findings closed by A06

### Descriptor-confined RECORD parent traversal

The A05 lexical parent traversal is replaced by `measure_confined_regular`.
Each normalized RECORD path is opened from the held Python-root descriptor.
Every parent uses descriptor-relative `stat`, `O_NOFOLLOW`, and `O_DIRECTORY`.
The final file uses descriptor-relative `open` with `O_NOFOLLOW`. The helper
retains the parent chain through the read and checks each parent descriptor and
pathname after the read.

This closes the A05 path-redirection gap, including RECORD rows such as
`../../bin` whose normalized path remains below the fixed Python root. A
symlinked or replaced parent is rejected. The review does not claim that an
unexecuted helper has measured the current tree.

### One-entry output allowlist and held report descriptor

`require_exact_attempt_output` now enumerates the attempt through `attempt_fd`,
caps enumeration, requires exactly `runtime-snapshot-a06.json`, and checks its
identity. The source performs this check after report flush and again after
the final root checks.

`verify_held_report` keeps `output_fd` open, checks descriptor identity before
and after a bounded reread, recomputes byte count and SHA-256, and checks the
descriptor-relative pathname. The outer `finally` closes the report only after
these checks. A later consumer must still independently hash and bind the
report, as the contract states.

### Cumulative capture admission

The source now calls `BUDGET.capture(descriptor_before.st_size)` before retaining
captured chunks in both regular-file paths. The contract names the complete
capture set: the runtime manifest, historical A03 closure, both METADATA files,
and both RECORD files. The 8 MiB limit is cumulative across that set.

The contract also states the correct boundary: the admission covers logical
retained bytes, not Python allocator capacity, object overhead, RSS, or total
process memory. The embedded counters intentionally stop at report
construction; post-serialization allowlist and held-report checks enforce
caps without changing the report being verified.

## Verified compatibility and scope

- The report remains schema 3 and the source, contract, and rationale agree on
  the A06 attempt and report names.
- The current domain remains the regular files declared by both Pillow and
  NumPy RECORD metadata, including `.pyc` rows.
- Pillow and NumPy remain unimported, and the scope explicitly excludes loaded
  image identity, standard-library closure, dynamic-library closure, runner
  closure, comparator execution, and native text execution.
- Historical A03 bytes remain path-set authority only. A06 does not reuse them
  as current package-byte authority.
- The helper reports no readiness, binding, seal, or authorization artifact.
  A later operation must bind the helper, contract, report, and consumer
  sources separately.

## Review limit

This is a source and contract review. The P2 descriptor cleanup must be fixed
before helper invocation. No runtime snapshot, package-byte observation,
loaded-image observation, or execution qualification is established here.
