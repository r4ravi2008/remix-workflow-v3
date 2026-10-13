# Focused comparator runner no-child controls A01 — root source review

The frozen A01 controls are preserved and rejected before import or execution. Root read all 806 control source lines, the complete contract, all 728 fixture lines, and the complete manifest. All twenty manifest source/input rows match current bytes and SHA-256. The manifest digest also matches. Root did not recompute the undocumented manifest aggregate.

## Frozen identities

- Control source: 35,313 bytes; SHA-256 `d7ce0ad273fe251288dababe8b5af80ece26137b731403a1b97d4bb94df41458`.
- Contract: 5,683 bytes; SHA-256 `89721bb30970f7b72905eaa32105ce9dde717284c14fbc97943293792a0580b9`.
- Fixture: 19,284 bytes; SHA-256 `930ea0c99bef041cf0de380ce9d558da072f9bf6c0841cacb7b4ade8c91313c4`.
- Manifest: SHA-256 `d0f2d9ab968ea8d5f4834f1920a8498b7c213756f49936e4fbd2a049799002ce`.

## P2 — Popen failure expects cleanup of a selector that was never created

The `popen-failure-cleanup-no-child` case creates an external fake selector. Its backend exposes that selector through `selector_factory`. The injected Popen raises before runner source reaches `selector_factory`. Runner cleanup correctly retains selector=None. The control nevertheless requires the external selector to be closed. This assertion rejects valid Popen-failure behavior after the production Path guard is repaired. The successor must record selector-factory calls and require zero calls. It must also retain exact launchError, processStarted=False, no signals, no pipes, and no direct-child wait facts.

## Required successor validation

The A01 contract honestly states that its fake cases do not qualify the capture loop. Those cases cover only prelaunch cancellation, Popen failure, and an already-completed fake child with an empty selector. Pure transition rows do not exercise the actual loop or exceptional cleanup.

Before runner execution, the successor controls must exercise the reviewed repair through injected backend scenarios. Cover post-Popen setup failure, deadline, both stream overflows, direct-child exit with retained pipes, TERM/KILL/final-drain bounds, direct-child reap timeout, and the early-exit getpgid race. Require exact launch command and environment. Require separate process-group and direct-child fallback observations. Canonically publish the applicable successful and failed capture records through control, failure, and seal owners. No real subprocess is needed.

Cover ordinary `Path(...)` values through both held-directory opening and fake capture. Cover Boolean/integer substitutions inside runtime flags and authorization scope. The final successor binding must refer to the repaired frozen runner and its review. Preserve this package unchanged.

## Scope

The independent fixture contains the complete 59-row comparator order and twelve required-evidence rows. Root read those rows and the complete transition/allowlist fixtures. The review establishes source inspection only. No target module, control, helper, real child, comparator, native producer, media process, GPU process, or Resolve process ran. No authorization or native authority was created. Independent source review remains pending.
