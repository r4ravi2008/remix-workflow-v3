# Swift pure-control runner A02: parent source findings

The parent read all 2,789 runner lines, the complete wire schema, rationale, and 438-line source-control schedule. This was source review only. The parent did not import or execute this runner or its controls. The six Swift binaries remain unexecuted.

Reviewed identities:

| Artifact | SHA-256 |
| --- | --- |
| Runner A02 | `6428e862a455910c4aa495c07336c6f9dfe3d63ab9f1e515f280b64c9a4a6ebb` |
| Wire schema A02 | `b734b36a20be16a2d681fbd6fb0d20f15d704803cdddc92de85256ee1068da24` |
| Rationale A02 | `fc21de1558d4a0fa9970c311bd999ae89ef4b401ccebe6f6dc9c0a39c3beb742` |
| Source controls A02 | `646698d86378bdfcaf2b79958b942cbf5da4fe03ac1bf57cbd4abd4d870d2153` |

## P1: capture can outlive the declared timeout

`run_captured_process` loops while either capture pipe remains registered or the direct child remains running. It sends SIGTERM at the deadline, but it sends SIGKILL only while `process.poll()` is `None`. It closes retained pipes only after the `killed` flag becomes true.

An exited direct child can leave a descendant holding a capture pipe. The loop then keeps a nonempty selector map. The timeout cannot set `killed`, because the direct child has exited. The runner can therefore wait indefinitely after its declared 15-second timeout and two-second termination grace. A TERM exit during cancellation or output overflow has the same failure shape.

Escalate the owned process group on a bounded schedule regardless of the direct child's state while capture remains open. End capture on a fixed deadline, close all pipes, and reap the direct child. Record only the observations actually established. A process-group signal and direct-child reap do not prove that every descendant has been reaped.

## P1: post-launch exceptions can leave the child running

The exception handler in `run_captured_process` handles only `OSError`. `require` can raise `ContractError` after `Popen`, and selector operations can raise other exceptions. The `finally` block closes pipes but does not terminate or reap the launched child. The caller catches the exception and proceeds toward a failure report while the child can remain alive.

Make launched-child cleanup unconditional on every exit path. Preserve the original failure, use bounded termination and capture teardown, and record direct-child reap separately. Do not turn this into an unsupported descendant-reap claim.

## P2: authority inputs accept boolean or floating-point integer substitutes

Manifest, build report, seal, parent readback, and authorization validators use equality against schema `1`. Python accepts `True == 1` and `1.0 == 1`. The source-control schema dictionary also accepts `True` for an expected schema `1`, and a compiler step's return code accepts `False == 0`.

The dynamic control-report validators already use strict integer and Boolean checks. Apply the same typed contract to authority schemas, numeric policies, compiler return codes, and nested numeric observations before equality comparisons. The current accepted evidence bytes remain valid; this finding concerns malformed-input rejection.

## Source-control execution gate remains unmet

The current source-control schedule covers JSON, report assertions, and several authority joins. It does not exercise capture timeout, retained pipes after leader exit, output overflow, cancellation, termination escalation, exception cleanup, root replacement, or binary replacement.

Add controls that exercise the actual runner functions with fake process, clock, selector, and signal backends. No child process should launch. Add actual temporary-file identity controls for held roots and binaries. Mutate schema `1` to both `True` and `1.0`, and mutate return code `0` to `False` and `0.0`.

The source-control loader currently verifies source bytes and then reopens the pathname through an import loader. Execute the verified bytes instead. Install the rejecting process-launch sentinel before executing module definitions. Read only bounded regular files and bind the exact runner filename. State the limits of loaded-image attestation plainly.

## Disposition

Preserve A02. Prepare a new source-only revision and updated wire schema, rationale, and controls. Independent source review and meaningful source-control execution must pass before four Swift control binaries run. Native rendering, ImageIO, CoreText, GPU, Resolve, listening, and creative acceptance remain unverified.
