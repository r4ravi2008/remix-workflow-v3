# Swift control runner A02 independent source review

## Scope and status

This is a read-only review of the frozen A02 runner package. I read the complete runner, wire schema, source rationale, and source-only control. I did not import, execute, typecheck, compile, or run any helper, control, binary, native framework, GPU, or Resolve process.

The reviewed files are:

| File | Lines | Bytes | SHA-256 |
|---|---:|---:|---|
| `native-text-unit-a01/run_swift_controls_a02.py` | 2789 | 125311 | `6428e862a455910c4aa495c07336c6f9dfe3d63ab9f1e515f280b64c9a4a6ebb` |
| `native-text-unit-a01/swift-control-runner-wire-schema-a02.md` | 258 | 8965 | `b734b36a20be16a2d681fbd6fb0d20f15d704803cdddc92de85256ee1068da24` |
| `native-text-unit-a01/swift-control-runner-source-rationale-a02.md` | 126 | 4878 | `fc21de1558d4a0fa9970c311bd999ae89ef4b401ccebe6f6dc9c0a39c3beb742` |
| `native-text-unit-a01/swift-control-runner-source-controls-a02.py` | 438 | 18585 | `646698d86378bdfcaf2b79958b942cbf5da4fe03ac1bf57cbd4abd4d870d2153` |

The runner binds the reviewed A15 manifest (`0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e`), A04 build helper (`ba632ed73005d8c3f870d4b7886c3057ae80405071c4f2154469fe090c195886`), build report (`214864e3d4bc7af8e7698dc3c6ad78f409147a5fffaeabfc8c9898c356fcc3ea`), publication seal (`23cd14ae2a46f5990831cb34e7de9b2dfa959cd642d3aec81381d804c63a97ae`), and parent readback (`cfc3aa29d7825a1d4d843a297df55e95651dcc0eef76cbbf94f0528f62a2f63a`).

## Verdict

The package has one P1 liveness defect and two P2 qualification defects. It is not ready for control authorization until the P1 is repaired. The P2 items also require repair or an explicit reviewed qualification boundary.

The source has strong positive structure. It uses direct-child names, exact manifest selection, held descriptors, bounded reads, duplicate-key rejection, one-object JSON framing, strict control report assertions, sequential control launches, and explicit false native boundaries. Those checks do not remove the findings below.

## P1 — retained descendant pipes can hang the runner indefinitely

`run_captured_process` loops while either a pipe remains registered or the direct leader has not exited (lines 2255–2270). It sends `SIGKILL` only when `process.poll() is None` (line 2265). After `SIGTERM`, a leader can exit while a descendant keeps stdout or stderr open. In that state, `process.poll()` is no longer `None`, `killed` stays false, and the runner never sends `SIGKILL` or unregisters the pipes. The selector loop then runs forever with a zero wait interval after the grace deadline.

The process-group design makes this case possible. A descendant can ignore `SIGTERM` while retaining an inherited pipe. The runner must still escalate the group and close the capture path after a bounded drain period.

The later `process.wait()` call at line 2299 has no timeout. The OSError path at lines 2300–2304 also calls an unbounded `wait()` after one `SIGKILL`. A hung child or a surviving process group therefore blocks the whole four-control run and prevents final evidence publication.

Repair the state machine before authorization. Base escalation on elapsed termination time, independent of leader liveness. Always attempt group `SIGKILL` after the grace interval. Add a bounded pipe-drain deadline and a bounded direct-child reap deadline. Use a documented fallback when group signaling reports that the group is absent. Preserve partial stdout, stderr, termination records, and a specific reap-timeout failure. Any post-`Popen` exception must enter the same bounded terminate-and-reap cleanup path before it escapes.

## P2 — strict JSON types are inconsistent for build authority

The runner defines strict helpers (`require_bool`, `require_int`, and `require_number`) but bypasses them for several authority fields. Python equality accepts values with the wrong JSON type:

- `manifest.schema`, `producerReportSchema`, and `controlReportSchema` use raw `==` comparisons at lines 825 and 829–830.
- `sourceControlReportSchemas` uses dictionary equality at line 834. `true` compares equal to schema integer `1` for the failed-publication and terminal controls.
- `buildReport.schema` uses raw equality at line 1250. The exact `limits` dictionary uses raw equality at line 1255, so boolean or floating numeric substitutions can compare equal to integer limits.
- `expectedBuildCount` and `observedBuildCount` use raw equality at lines 1330–1331. Build step return codes and several numeric limits use raw equality at lines 1072 and 1074–1087.
- `buildSeal.schema`, `buildReadback.schema`, and `authorization.schema` use raw equality at lines 1416, 1497, and 1564.

The wire schema and rationale require strict field types, but the source control only mutates the PNG schema-map value to `true` (source-control lines 240–245). That mutation rejects because PNG schema is `3`; it does not test the schema-`1` map entries or the top-level documents. A future authorization could therefore pass a boolean or float where the contract requires an integer.

Repair by requiring exact integer types before equality, and by validating every numeric map member recursively. Add source-only negative cases for top-level schema fields, schema-map schema `1`, build limits, build counts, and step return code. Keep the existing strict control-report validators, which already call `require_int` for their numeric fields.

## P2 — source-only controls do not cover process and drift branches

The source control explicitly forbids the runner main path and replaces `subprocess.Popen` with a rejecting sentinel (source-control lines 2–6 and 395–405). Its cases exercise framing, manifest order and bindings, build/seal/readback joins, authorization, report assertions, tri-state fields, and selected negative mutations (lines 227–380).

It does not exercise `run_captured_process`, `run_one_control`, or `main`. No control covers timeout escalation, cancellation, stdout or stderr cap crossing, retained descendant pipes, post-launch exception cleanup, partial capture publication, root drift, build-root drift, binary descriptor drift, or pathname replacement. The positive source-only report therefore cannot qualify those runtime branches. Add a separate reviewed process-harness control, or state in the authorization that those branches remain source-reviewed only and require a later evidence unit before acceptance.

## Verified source properties

- `parse_json_bytes` rejects duplicate keys, non-finite values, trailing bytes, invalid UTF-8, and roots that are not objects (lines 292–319).
- Descriptor reads cap bytes, hash the complete input, detect growth, and compare metadata before and after the read (lines 345–375).
- The runner holds the attempt, build, package, selected-binary, and authority-file descriptors through control execution (lines 1942–1969 and 2031–2141).
- Each selected Mach-O is checked before and after its child. The check includes path and held-descriptor observations, arm64 type, load-command bounds, and one UUID (lines 554–624 and 2325–2375).
- Controls run in fixed order. Authority drift, timeout, cancellation, or output overflow stops later launches (lines 2419–2445).
- Control reports require exact keys, exact schemas, exact producer labels, exact case order, exact strings, exact hashes where defined, and strict numeric and boolean types (lines 1604–1851).
- Output publication uses exclusive descriptor-relative creation, fsync, bounded bytes, and a post-write descriptor readback (lines 516–551 and 2340–2355).
- The runner keeps native producer, duplicate PNG, loaded-image, GPU, Resolve, and creative-acceptance boundaries false. The package does not claim native text or media acceptance.

## Authority and scope limits retained by the contract

The package documents that path-bound execution does not prove the bytes mapped by the kernel. The source-only control imports the runner after a separate hash read, so it also relies on the frozen no-writer assumption during that import. The runner does not claim a loaded-image attestation, complete compiler dependency closure, complete SDK closure, native framework trace, playback, film quality, hearing, or creative approval.

No binary or native result is accepted by this review.
