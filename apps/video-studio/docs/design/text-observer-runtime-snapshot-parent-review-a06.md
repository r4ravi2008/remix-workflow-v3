# Observer runtime snapshot A06 parent review

Status: complete source-only change and contract review.
The parent read all 464 source-patch lines and the complete contract and rationale.
The parent read the entire independent peer review.

| Artifact | SHA-256 |
| --- | --- |
| A06 helper | `474ea7b97da675b0499598b297d8860b413297dac7bf6bf57b7f4f236b217ed0` |
| A06 contract | `c742514d5c25c0b923fee9a86e1d9f6d718af9043e1f819ff2fcdfd793641b45` |
| A06 rationale | `f81424d7989cff2c93072aa0e777f2cca56ff6fa075bbca954a4c1cf60a0a9b7` |
| A06 peer review | `45f70c77ea54296247052f6782ce3c591c6a221eeda6b7d868cbc66935ce9b9f` |

A06 closes the three A05 P2 findings.
The parent confirms one new failure-only descriptor-ownership P2.
A parent descriptor opened before `fstat` or endpoint validation is not yet
owned by `parent_chain`. That local failure can bypass the cleanup list.
The repair must close that descriptor until ownership transfers to the chain.

The counter contract correctly distinguishes prepublication observations from
the later bounded output enumeration and held-report reread.
The confined traversal, capture pre-admission, and exact output allowlist remain required.

Preserve A06 and both reviews. Review the narrow A07 local-guard repair before invocation.
No snapshot helper, import, native, GPU, or Resolve process ran.
