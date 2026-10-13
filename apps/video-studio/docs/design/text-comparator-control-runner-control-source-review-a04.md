# Comparator runner A03 additive controls A04 — peer source review

## Review result

I found no P1 or P2 in the requested A04 repair scope. The supplement is
source-frozen and unexecuted. One fixed combined A03+A04 control run remains
required before the source-control layer can qualify.

I read the complete A04 source, fixture, contract, and self-excluding manifest.
I compared their production-shape checks with the frozen A03 runner. I retained
the complete A03 peer review instead of repeating its already accepted scope.

This review is same-model and nonblind. I authored runner A03 and reviewed the
A03 controls. The judge authored this additive supplement.

## Frozen identities

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `control_comparator_runner_a04.py` | 25,301 | `c7fdc4b77e14a70ff9186a772fa1fae218dcc943f7fdf961d954f6f42714c246` |
| `control-contract-a04.md` | 5,166 | `ca4a3f92be177d7c7b615e29952f69c0cf2399a0b71f5911eaf406ccfca98218` |
| `control-fixture-a04.json` | 5,977 | `f8996031ba39acd04a6f74dde5534ac4ba3e0c87f40116e535d1b76bc927f75c` |
| `source-package-manifest-a04.json` | 10,311 | `a10ef50aa23624a5609268faa17116f167e626a6254b46fb45eeac99ec3fa755` |

All 30 manifest rows match current file sizes and SHA-256 values. Their total is
4,821,536 bytes. I independently recomputed the documented aggregate as
`114775e5684ab4a9c2bd613abcf79ee111a5ed06f6e2655ab945b383c7f41b2a`.

## A03 additive loading join

A04 reads the exact 79,578 A03 control-source bytes through a bounded no-follow
descriptor. It loads only those measured bytes and calls A03 `run_controls`.

A04 requires the A03 passed state and false child and subprocess facts. A03
`run_controls` itself requires every result row to be accepted. A04 also
requires the named two-domain seal-cap result before running its supplements.

A04 then uses the measured A03 helpers to reopen the runner, codec, runtime
helper, A09 report, overlay, and diagnostic. The combined report retains the
A03 result count and a digest of the complete A03 result object.

An A04-only result cannot replace A03 evidence. The contract, manifest, and
result state all preserve that additive qualification rule.

## Production-shaped report-owner repair

`production_shape_control` parses the measured runner source. It extracts the
literal success, failure, validation, scope, error, phase-summary, capture, and
capture-event keys. Those exact orders must match the frozen fixture.

The maximum capture starts from a record produced by the production capture
function. The control preserves all production record fields. It calls the
runner's `_capture_event` exactly 4,096 times.

The sequence reaches `COMPLETE` through `started`, 4,092 `stdout_bytes` events,
`direct_exit`, `pipes_closed`, and `reaped`. Each event retains the production
`event`, `before`, `after`, and integer timestamp fields. Event accounting must
match, and no admitted event may be dropped.

The stdout observation binds the exact compact 59-row actual-comparator child
value. Its byte count and hash must also satisfy the runner's production capture
acceptance predicate. Stderr remains exactly empty.

The success control constructs every production report field. It includes the
complete capture, validation, three phase summaries, child receipt, closure
aggregate, authorization receipt, and success scope. It encodes through the
actual codec's `CONTROL_RESULT` owner under the unchanged 1 MiB cap.

The failure control uses the same maximum capture. It includes three phase
summaries, five pre-failure entries, the exact failure scope, and a 512-byte
bounded error detail. It encodes through `FAILURE_RESULT` under 1 MiB.

This is the requested fixed-input boundary. It does not claim a theoretical
maximum across every permitted integer or error string. The production codec
still enforces each actual publication cap.

The A03 seal remains the seal authority. A04 requires that control's accepted
row. The seal uses the production builder, two complete measured runtime
domains, the capture summary, and the measured report reference under 4 MiB.
The full event array remains only in the control or failure report.

## Both fixed-command repair

A04 sends both `ControlMode` values through the production capture entry point.
Each injected Popen checks the exact Python path, `-I -B`, and child path.

Each case also checks the working directory, six-value environment, standard
streams, descriptor policy, and new-session flag. The Popen raises before any
process starts. The selector factory must have zero calls in both modes.

The result retains separate required-evidence and actual-comparator command
facts. No real child, selector, stream, signal, process group, or reap evidence
is inferred from these fake cases.

## Scope

No runner, A03 control, A04 control, codec, helper, child, compiler, native
process, media process, GPU process, or Resolve process was imported or run for
this review. No authorization, attempt directory, publication, loaded-image
attestation, provider origin, playback, watching, hearing, or creative
acceptance was established.
