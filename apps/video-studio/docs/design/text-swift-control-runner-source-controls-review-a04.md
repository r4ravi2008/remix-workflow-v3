# Swift control runner source controls A04: independent review

## Scope and frozen identities

This is a read-only source review of the A03-to-A04 source-control change. I read the
complete A04 control module and rationale, the complete production Runner A03 path used by
the controls, and the preserved A03 result. I did not import or execute a control, runner,
compiler, helper, binary, or native framework.

| Artifact | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `swift-control-runner-source-controls-a04.py` | 959 | 40,593 | `9f6c3391c6bb2717a92049749959c77525627308bd80a9343bedd161d4f02028` |
| `swift-control-runner-source-controls-rationale-a04.md` | 52 | 2,131 | `7c3b898522627472361e6657e28ee9c5360430c216c8f848226fff503c8ebce3` |
| preserved source controls A03 | 926 | 39,183 | `518799ff5379700c01d6b0bd643f1559f7c40d119b29f63206f5f2ec01b38a08` |
| production Runner A03 | 3,015 | 135,472 | `d0d89138412caa6760a72ceb41bea24d61ca2b5a74eb9dc00e83b8eadc3e990c` |
| preserved A03 result | 290 | 6,360 | `3e9226bad76e75de439770dfb989272d2095c0b92ea4450dabc2bc6070c22f85` |

The preserved A03 result records 53 of 54 cases passing. The only failed case was
`held-binary-path-replacement-detected`, with the old assertion that the complete retained
descriptor remained equal after `rename`.

## Verdict

No P1 or P2 finding remains in the frozen A04 source-control delta. The change is a bounded,
source-only repair of the failed disposable Mach-O replacement assertion. It does not weaken
the production runner's metadata-drift check.

## Diff review

The functional change is confined to `binary_drift_control`.

The control now checks the retained descriptor against `binary.before` for path, byte count,
SHA-256, Mach-O UUID, CPU type, file type, load-command count, and load-command bytes. It also
checks retained device, inode, mode, and size. These fields cover the requested content and
stable identity facts.

The control compares `descriptorMatchedBefore` with the complete dictionary equality result.
It does not require complete equality to remain true after `rename`. This is correct because
the production identity includes `st_ctime_ns`, and the measured filesystem can change ctime
when the held file is renamed. The A04 rationale states this boundary precisely.

The reopened pathname is required to have a different device/inode pair, SHA-256, and Mach-O
UUID. The control also requires `pathnameMatchedBefore` to equal the complete replacement
comparison and to be false. It therefore detects both pathname replacement and any accidental
reuse of the retained descriptor's bytes or identity.

The source-control scratch prefix and report producer change from A03 to A04. The module keeps
the rejecting `Popen` sentinel, fake capture backend, authority validation, and bounded report
publication unchanged. The production runner remains bound to the A03 source hash above.

## Production boundary and remaining limits

Runner A03 still computes full `stable_identity` equality, including mtime and ctime, after
descriptor reads. A04 changes only the disposable control's expected result. It does not alter
production acceptance, path authority, binary hashing, UUID parsing, or drift rejection.

The A04 control has not run in this review. The preserved A03 result is historical evidence
for the unchanged cases, not an A04 pass. A future source-control run must bind the exact A04
module and the production Runner A03 hash, then retain its own report.

This review does not establish real child-process pipes, signal delivery, filesystem race
behavior beyond the injected source control, loaded Python or compiler image identity, native
text feasibility, native media output, GPU behavior, Resolve state, playback, hearing, or
creative acceptance.
