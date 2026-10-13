# Native RoleIndexV2 launcher A02 independent source review

## Disposition

This is a read-only review of the frozen A02 launcher package. The five A01
findings are closed. I found two new P2 findings in cleanup timing and
attempt-failure publication. A source successor is required before execution.

No launcher, helper, compiler, Rust binary, vector, decoder, control, native,
media, GPU, or Resolve process ran during this review. No A02 source-review
marker or attempt directory exists.

This review is same-family and nonblind. I authored the independent decoder
control package. Its expected model remains separate from the launcher, but
this review is not independent-source-origin evidence.

## Reviewed identities

| File | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `native-role-index-v2-launcher-a02/run_role_index_v2_pipeline_a02.py` | 1900 | 82212 | `22fce34292ea05d457c1d0698ac67d5db102d4d56ca4df0698a71dcd3511517f` |
| `native-role-index-v2-launcher-a02/launcher-contract-a02.md` | 358 | 12891 | `ea1a219ee5cb51de51ae3db6db02fd786709be79b4f576f960968599c07f8f50` |
| `native-role-index-v2-launcher-a02/source-delta-a01-to-a02.patch` | 1150 | 53422 | `7c67833c9b8461321da7a787d375539226856ac6702c0bbc25a2bd16f9987b59` |
| `native-role-index-v2-launcher-a02/source-package-manifest-a02.json` | 1 | 771 | `c62e7bd6e2f207db85488091bbb9e7af83b633c21c969f039f223cc173535d65` |
| `native-role-index-v2-launcher-a02/source-rationale-a02.md` | 134 | 6289 | `d8626c132532f302039bdc87932f1efdd088064e85af901bcd5024dfb00c3b73` |

The preserved A01 independent review is
`apps/video-studio/docs/design/native-role-index-v2-launcher-source-review-a01.md`,
SHA-256 `3f86dc584937b7c4af6c138bfcb16905594c8addfe39fa3ca2f4677de62f8dcf`.
The A01 parent review bound by the A02 rationale is
`apps/video-studio/docs/design/role-index-launcher-parent-review-a01.md`,
SHA-256 `902e85a96b5627bc4d06d820a1b74732dd4a9c8f1e53f48ced09538fbc8dd982`.

## A01 findings closed

`validate_decoder_control_report` now requires the exact success-report key
set, canonical bytes, strict integer fields, full eleven-field scope, ten
current input observations, aliases, publication facts, vector identity, and
separate actual and expected model identities. It validates every result
against the reopened canonical schedule. Result identifiers, order, category,
expectation, status, rejection code, offsets, mutation hashes, and mapping
model hashes are checked.

Each process record enters `progress["processes"]` before `Popen`. Artifact and
log publication records update that same caller-owned structure before and
after writes. Failure publication carries stage history, process records,
cleanup observations, partial publication state, and partial output facts.
Unexpected failures use the current progress stage.

The capture handler catches `BaseException`, requests group cleanup even after
the direct leader exits, and keeps direct-child reaping separate from the
unattested descendant state. Mach-O UUID parsing consumes the same retained
bytes that `read_regular` hashed. Vector controls and fixture encoding receive
distinct exclusive `TMPDIR` directories and separate command receipts.

## Findings

### P2: the final-drain interval occurs before KILL

The main capture loop breaks at lines 923–924 when
`termination_at + TERM_GRACE + FINAL_DRAIN` is reached. It no longer sends
KILL in that loop. `finish_group_cleanup` then runs at lines 948–950 and sends
KILL after its deadline has already elapsed. The selector closes immediately
after that cleanup at lines 951–975.

The declared `FINAL_DRAIN` interval therefore occurs after TERM and before
KILL. There is no post-KILL drain. A child or descendant can write between
KILL and selector closure, and those bytes are not retained. The source still
attempts bounded TERM and KILL, but its rationale promises fixed TERM, KILL,
and pipe-drain deadlines, and the source-control expectation requires both
signals for a dead leader with retained pipes.

Keep the process record and caller-owned cleanup model. Send KILL after the
TERM grace interval, then retain a bounded post-KILL drain before closing the
selector and waiting for the direct child. Record each signal result and keep
descendant reaping unattested.

### P2: prepare failure can mutate an existing attempt

`prepare_attempt` catches `os.mkdir` failure at lines 1015–1034 and rethrows
after trying the sibling preparation-failure record. In `main`, the
`BaseException` handler at lines 1862–1875 then calls `lstat(attempt)` and
writes `failure-a02.json` whenever that path is an existing directory.

When an old attempt directory exists, the expected `FileExistsError` leaves
that directory untouched only until the second handler. The second handler
writes a new failure file inside the pre-existing attempt. This violates the
exclusive-attempt boundary and can mutate preserved evidence. The current
first-run absence check reduces exposure, but it does not make the failure
path safe or satisfy the contract for an attempt-creation failure.

Track whether this invocation created the directory. Write an in-attempt
failure only when ownership was established by this invocation. For an
existing directory, retain only the sibling preparation-failure record and
report the collision without writing inside the existing attempt.

## Review limits

The A01 closure statements are static source observations. They do not prove
that the future child, process group, filesystem, or vector behaves as shown.
The two P2 findings are source-level regressions. No compiler compatibility,
process capture, vector bytes, decoder equality, filesystem durability,
loaded image, native framework, or product behavior was tested.
