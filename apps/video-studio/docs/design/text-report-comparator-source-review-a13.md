# Comparator A13 source review

Status: independent source-only review. A13 is unbuilt, unexecuted, and
unqualified. No comparator import, control, compiler, native framework, media,
GPU, Resolve, or helper process ran.

## Reviewed identities

| File | SHA-256 |
| --- | --- |
| `actual-comparator-control-a13.py` | `4ac29f6f708938059f19f00f574a6212828c22873daa80e1d3d915c3ed4c8100` |
| `package-manifest-a13.json` | `239e9f7be13cd63a4058b9b64f245185939840362650d9e1e212281424b2a01e` |
| `output-schema-a13.md` | `e89cab9bb5f9b9f3621c19cb5298545bb144d4e2f6b1cd3025f39300f847aad0` |
| `source-rationale-a13.md` | `b909ac477e4f120b55b3413333665499992d5767d2f5e1a3ca0af83f12249a1d` |
| `README-a13.md` | `d1ed03d2fa0b4fe81fcf7886e36c5d3f48c63128848fbeb72f314acf0e5c5bc6` |
| A11 comparator | `e94b6ea3fb671ba66d413594060959bb5ec86f7e4fcffb8e774ababaeb438520` |
| A12 source review bound by A13 | `b9d8d4bd5fdd04acf63680c1097d000213ded2eaf586b2c44a86dc03fa2df243` |

## Findings

### P1-1: The source emits 59 results, but every frozen contract says 58

Static source accounting gives this ordered result count:

```text
loader                         1
source join                    1
allocation_controls           13
current allocation replay      1
parser_and_gate_controls      40
Rust stability controls        3
                               59
```

The extra row is
`a11-complete-parser-outer-failure-no-repeats`, emitted at the source path
that constructs `outer` before the causal outer-failure rows. The frozen
`output-schema-a13.md` table ends at item 58 and omits this row. The manifest
also declares `controlResultCount: 58`.

A strict runner cannot accept the child output as written. It must either
retain the row and update the schema, manifest, and any result-order binding,
or remove the source emission through a reviewed successor. Do not infer the
count from a successful process return code.

### P2-1: The post-correction review authority is outside the A13 manifest

A13 binds the preserved A12 review at
`b9d8d4bd5fdd04acf63680c1097d000213ded2eaf586b2c44a86dc03fa2df243`. The
additive gate-semantics correction is a separate review:
`apps/video-studio/docs/design/text-report-comparator-source-review-a12-correction-a01.md`,
SHA `ffd7af4283612a561ce87ad5a0f9609842274bee9c76bb2fb0ce8e861dad8bf1`.

The A13 source rationale already states the corrected rule: an
`observation_only_rejected` case may have a true structural case gate while
remaining `qualified: false`. A final runner authorization that relies on the
new review must bind this additive correction separately or issue a manifest
successor. The existing A13 row does not cover it.

## Verified A13 repairs

The control now captures the comparator loader from the exact bytes passed to
`exec`, requires integer loader bytes, and emits schema 2. The current
314,231,808-byte fixture calls the actual validation and allocation replay
functions, while its diagnostic labels the event sequence synthetic contract
evidence. Failed, fractional, and outer cases call
`swift_case_gate_passed` and require false. Observation prefixes call the same
function but require the explicit `qualified: false` boundary and record both
structural and native-qualification facts. This is the correct active-gate
split.

The package manifest excludes the invalid current A11 and A12 manifests and
binds the A15 21-row source manifest, the six comparator inputs, and the A13
source contract files. Those rows still require the future runner's descriptor
preflight and parent readback.

## Review limit

This review does not establish comparator execution, allocation replay against
a native event log, CoreText behavior, PNG orientation, native shaping,
loaded-image identity, media support, GPU use, Resolve behavior, playback,
listening, or creative acceptance.
