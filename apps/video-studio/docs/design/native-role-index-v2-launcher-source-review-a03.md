# Native RoleIndexV2 launcher A03 independent source review

## Disposition

This is a read-only review of the frozen A03 source package. The two A02
findings are closed. The five accepted A02 repair groups remain present. I
found no new P1 or P2 source finding.

No launcher, helper, compiler, Rust binary, vector, decoder, control, native,
media, GPU, or Resolve process ran during this review. No A03 attempt or
source-review marker was created.

This review is same-family and nonblind. I authored the independent decoder
control package. That package remains a separate expected-model authority,
but this review is not independent-source-origin evidence.

## Reviewed identities

| File | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `native-role-index-v2-launcher-a03/run_role_index_v2_pipeline_a03.py` | 1958 | 84799 | `06f19d0da7142e077e52651f5f19bbecac9918755fe62d5b676002aa1873c256` |
| `native-role-index-v2-launcher-a03/launcher-contract-a03.md` | 368 | 13711 | `a495dd841aa2e562e394dddfea126b7e5377caca641fe3acae82c3ffea18a994` |
| `native-role-index-v2-launcher-a03/source-delta-a02-to-a03.patch` | 370 | 16805 | `92dc3fe4e2785ab5144867773a9407819ad8f281042fd5a8668553ce3b887857` |
| `native-role-index-v2-launcher-a03/source-package-manifest-a03.json` | 1 | 771 | `ebd0b49119a66120856ce35b262f0a31ebd1a2ae43bc1a89242cec584bb389ba` |
| `native-role-index-v2-launcher-a03/source-rationale-a03.md` | 139 | 6692 | `f405030466eb8de92f8f24798cf4cf3fe60a1fc1b6a2fe1070241f448965eebb` |

The preserved A02 independent review is
`apps/video-studio/docs/design/native-role-index-v2-launcher-source-review-a02.md`,
SHA-256 `49120a6b1d3c4923ec30975e93329bdcbbd997ed2c63d10647ba565a12222385`.
The A03 rationale binds that review and the parent findings.

## A02 cleanup repair

The capture loop records the first cleanup trigger and sends group TERM in
`request_group_cleanup`. Once the TERM deadline expires, `run_bounded` leaves
the loop and its `finally` calls `finish_group_cleanup` with the live selector
and retained stdout and stderr buffers.

`finish_group_cleanup` waits until the recorded TERM deadline, attempts group
KILL in a `finally` block, records the result and elapsed time, then drains
the retained selector for at most `FINAL_DRAIN`. It records drain completion,
remaining pipes, overflow, and drain failure. If the selector is unavailable,
the record carries `unavailableReason` instead of claiming a drain.

The order is therefore TERM, TERM-grace expiry, KILL, and bounded post-KILL
drain. The direct-child wait remains separate from the unattested descendant
state. A dead leader with retained pipes still enters the retained-pipe
branch, and `signal_process_group` attempts `killpg` without requiring
`process.poll()` to report a running leader.

The A02 loop previously waited through the final-drain interval before the
cleanup function sent KILL. A03 changes the loop deadline to TERM grace and
moves the post-KILL drain into the cleanup function. This closes that finding
without adding an unbounded wait or a descendant-reaping claim.

## A02 attempt-ownership repair

`new_progress` starts with `attemptOwnedByInvocation` set to `False`.
`prepare_attempt` uses exclusive `mkdir(path, 0700)` and sets this flag only
after `mkdir` succeeds. A collision writes only the sibling
`<mode>-prepare-failure-a03.json` record. The prepare exception handler in
`main` writes `failure-a03.json` inside the attempt only when the ownership
flag is true.

Thus a failed exclusive creation cannot write into a pre-existing attempt.
If post-creation metadata validation fails, the invocation owns the directory
and may publish its in-attempt failure record. The distinction is explicit in
the progress object and survives failure-model serialization.

## Preserved accepted repair groups

1. `validate_decoder_control_report` requires the closed schema-2 report,
   canonical bytes, ten input observations, aliases, publication facts,
   vector identity, actual and expected model identities, complete scope, and
   all 74 scheduled rows. `validate_decoder_results` checks order, ordinal,
   identifier, category, expectation, status, rejection code and evidence,
   and mapping hashes.
2. Each process record is appended to caller-owned progress before `Popen`.
   Artifact and log publication records enter progress before writes and
   retain failure and partial-path observations. Failure records retain the
   progress object and current causal stage.
3. Post-launch `BaseException` handling requests group cleanup even after the
   direct leader exits. The selector-aware cleanup path records TERM, KILL,
   post-KILL drain, and direct-child reaping separately.
4. `observe_macho` hashes and parses the Mach-O UUID from the same retained
   bytes returned by `read_regular`, whose descriptor and pathname identities
   are checked before the observation returns.
5. Vector mode creates exclusive `rust-controls-tmp` and `rust-fixture-tmp`
   directories and builds a separate exact environment and receipt for each
   command. Controls must pass before fixture encoding starts.

The A03-only source changes are otherwise package/version bindings, state and
filename updates, cleanup evidence, and attempt ownership. The fixed build,
vector, and decoder-control modes remain ordered and separate.

## Limits

The source still does not attest loaded executable images, atomic launch,
descendant reaping, child RSS, filesystem-cache behavior, native frameworks,
media, GPU, Resolve, or creative acceptance. Failure publication is not an
atomic transaction. A post-KILL drain is attempted only while the selector and
buffers remain available, and the unavailable case is recorded explicitly.

The green disposition is source-level only. A future build, child process,
filesystem, decoder, or vector run requires its own reviewed authorization and
readback.
