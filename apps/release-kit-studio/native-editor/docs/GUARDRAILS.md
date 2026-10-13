# Native verifier guardrails

The Rust editor is the product.
The development verifier checks the product.
The verifier stays outside the runtime.
Release Kit remains an optional workflow outside the native editor contract.

## Ownership

| Component | Owns |
| --- | --- |
| `editor-core` | Typed editing semantics, revisions, intents, native pixels, and artifact integrity |
| `editor-cli` | JSON framing, schemas, discovery, deadlines, and exit codes |
| `editor-devcheck` | Development policy, bounded processes, independent observations, and reports |

Runtime crates do not import `editor-devcheck`.
The verifier observes the public CLI.
The verifier does not share the CLI edit implementation.

The Rust compiler checks types and privacy.
The verifier checks source rules and actual feature outcomes.
The two checks have separate responsibilities.

## Enforced rules

- Runtime crates cannot import the development verifier or an application adapter.
- `editor-core` cannot spawn processes or terminate its host.
- Source and dependency checks reject FFmpeg, libav, and historical renderer fallbacks.
- Recursive inventory includes nested and disabled source files.
- The capability ledger cannot promote a feature to trusted `verified`.
- A caller cannot author evidence that the verifier accepts as its own.
- Each process has a deadline, an output limit, and a preserved report.
- A missing tool produces an incomplete result.
- A failed result remains separate from an incomplete result.
- Document receipts and runtime reports use separate run directories.

Architecture mode checks repository structure.
Full mode adds current-build P0 execution.
Neither mode changes capability state.

## Evidence limits

The verifier covers the bounded P0 editor.
It does not prove movie codecs, audio, text, multilayer composition, GPU execution, hosted execution, playback, listening, or creative approval.
It does not sandbox arbitrary hostile Rust.
It does not authenticate a compromised compiler.
It does not sign a trusted promotion receipt.

Human reviewers decide whether acceptance expectations represent the requested feature.
Technical comparisons cannot grant that decision.

## Historical records

Use [HISTORY.md](HISTORY.md) for archived design comparisons, review records, and task records.
Use [VERIFICATION.md](VERIFICATION.md) for commands and saved runtime evidence.
Use [INTENT-VERIFICATION.md](INTENT-VERIFICATION.md) for expected and observed feature results.
