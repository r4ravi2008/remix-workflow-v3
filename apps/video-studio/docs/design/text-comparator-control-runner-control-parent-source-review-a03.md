# Comparator runner A03 no-child controls — parent source review

## Result

A03 is preserved and unexecuted. Root found no P1 and two P2 coverage gaps.
The independent source review confirms both gaps. A small A04 supplement will
close them while preserving the frozen runner and A03 control package.

Root read all 1,810 control-source lines, the complete contract and manifest,
and the complete fixture delta from the previously read A01 fixture. All 45
manifest rows match current bytes and SHA-256 values. The total is 5,198,613
bytes. The independently reconstructed aggregate is
`7c2a5244067dfc7d581a535c4bc186b3c6be5e9d1ef47e161c5f99fa92e540d5`.

## Frozen files

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `control_comparator_runner_a03.py` | 79,578 | `116e8099cdda156fecb9bc4aa6092ef9b852e4fc56e4704d9624608ac1fc53c7` |
| `control-contract-a03.md` | 7,224 | `973d9176a0de30a83c71aed4a9e513ca5ef99128d5926b4518bb6a9e9079f83b` |
| `control-fixture-a03.json` | 24,239 | `80c0bb6cfad1291e713c57ed733e68d0a933755d45ba0a668650bb73f5a6aa2e` |
| `source-package-manifest-a03.json` | 14,704 | `120d3e0c7683cc468e1b599c6d18e0eb224173f6b10e02c4cfd9d58a052a2748` |

## P2 findings

The maximum-capture fixture uses `state`, `event`, and timestamp fields. The
production capture events use `event`, `before`, `after`, and timestamp fields.
The fixture also encodes a minimal three-field envelope. It does not establish
that the full production control and failure reports fit their 1 MiB owners.
This is a coverage gap, not evidence that either production report exceeds its
cap. The production seal seam retains two complete measured domains and a
bounded capture summary. Its 4 MiB codec result remains pending execution.

The fake Popen gate selects only the required-evidence child. The actual-
comparator command is declared in the fixture but never reaches that gate.
The successor must exercise both fixed commands and their exact launch options.

## Peer readback and repair scope

Root read the complete 6,313-byte independent report at
`text-comparator-control-runner-control-source-review-a03.md`. Its SHA-256 is
`b5f6a5d3b1e6b209496a66d931de5608d5417d0549c4d38060196b1044dd942a`.
The reviewer is the runner author. The review is separate-author, same-family,
and nonblind. Its two P2 findings match this parent disposition.

A04 may measure and run the reviewed A03 suite, then add complete production-
shaped report cap cases and both fixed-command fake cases. A03 remains historical
source provenance in the frozen runner closure. Qualification will name the
combined A03+A04 evidence explicitly. No runner revision is needed solely to
rename external supplemental controls. Root must review A04 before execution.

No target source was imported or executed. No real child, compiler, native
producer, media process, GPU generation, Resolve operation, playback, hearing,
viewing, or creative acceptance occurred.
