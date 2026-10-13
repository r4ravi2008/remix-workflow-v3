# Comparator control A12: parent source review

Root read all 210 lines of the A11-to-A12 control patch against the previously reviewed A11 control.
Root read the complete A12 README, rationale, and manifest.
Root checked the current full-report fixtures, prefix schedules, and active-gate helpers.
No control, comparator import, compiler, native framework, decoder, GPU, or Resolve process ran.

| Artifact | SHA-256 |
| --- | --- |
| A11 comparator source | `e94b6ea3fb671ba66d413594060959bb5ec86f7e4fcffb8e774ababaeb438520` |
| A12 actual control source | `3df9b1dd2141c16532344f48f39ea9a561dc224a39f3a4ba864876088cc60db9` |
| A11-to-A12 parent-read patch | `7fd50abbec2b2f9cf68682085c68a8ede91893f35cc425dab93a1e0f01067c20` |
| A12 README | `627a6eb7673f84c4e34e07fefb5f7606c34c7c4ea7235c283fa5cac4d3f90c22` |
| A12 rationale | `be2dee460c149dcdf6134b7a7221803a9cf3c924a797e8984791fa574d063f4c` |
| A12 package manifest | `99094c8bb32fe61157fd021d9b6e2ee011241f484f337514dc98376102466431` |

The control source repairs the two A11 P1 findings at source-review level.
It distinguishes binding errors from aligned baseline or peak range errors.
It expects `toggle_count` for the omitted toggle and retains a separate wrong-order control.
The current allocation, failed prefixes, fractional prefixes, observation prefixes, and outer causal failure reach the complete report parser.
The repaired branches also reach the active producer gate.
Failed reports must not qualify, and observation-only declarations remain explicitly unqualified.

The loader record derives from the same retained payload passed to `exec`.
Its `path` and `sha256` fields are Strings.
Its output `bytes` field is a decimal String, although the internal captured byte count is an integer.
Any future wrapper must bind that exact source-defined output shape or review a separate source successor.
This record establishes captured-source provenance, not loaded-memory integrity or native execution.

## P2: inherited package authority is inconsistent

A12's manifest binds the changed A11 manifest with SHA-256 `fde359966503739aa5225cf911e3e75ff61e74b04396343612d5ff323ce064a8`.
That manifest records the corrected README hash with the earlier byte count.
The README actually has 6,802 bytes, while the manifest row declares 6,682.
The original and changed metadata have been preserved separately.

Keep A12 source unchanged while peer review completes.
Create a separate manifest and contract successor with direct measured rows for every required source, contract, and input authority.
The successor must also include the required-evidence control and complete A15 source join.
It must not use the inconsistent A11 or inherited A12 manifest as execution authority.

## Review boundary

The independent same-family source review remains pending.
Actual control outcomes remain unverified.
Root has not accepted a runnable comparator package.
No native, text, playback, hearing, story, or creative acceptance follows from this source review.
