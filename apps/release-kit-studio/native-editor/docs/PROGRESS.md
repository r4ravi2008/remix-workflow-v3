# Native editor progress

The standalone Rust editor is the active product.
It targets DaVinci Resolve feature behavior through a direct agent CLI.
Release Kit is one optional workflow profile.

## Current facts

| Item | Current state | Evidence |
| --- | --- | --- |
| Capability families | 8 implemented, 73 planned | [`capabilities.json`](../capabilities.json) |
| Trusted promotion | 0 features promoted to `verified` | [`capabilities.json`](../capabilities.json) |
| Implemented tools | `engine.capabilities`, `project.create`, `project.inspect`, `project.commit`, `frame.render`, `artifact.verify` | [`CLI-EXAMPLES.md`](CLI-EXAMPLES.md) |
| Render scope | One non-overlapping solid RGBA track with CPU PNG output | [`CLI-EXAMPLES.md`](CLI-EXAMPLES.md) |
| Unimplemented scope | Movie, audio, text, multilayer, GPU, and hosted execution | [`FEATURES.md`](FEATURES.md) |

The capability ledger keeps `planned`, `implemented`, and `verified` separate.
The six tools do not establish Resolve parity or Release Kit output completion.

## Last passing runtime snapshot

The last successful full runtime snapshot is report.json in `../.runs/verification/1791190183401588000-54565/report.json`.
It passed 22 of 22 required checks.
Its intent report records 16 CORE A/B pass observations across eight implemented families.
It records 73 planned families as unobserved.
It did not promote a capability.

That receipt describes its original source snapshot.
The cleanup result is recorded in the cleanup summary in `../.runs/product-contract-1791264756707/SUMMARY.md`.
That summary records any later current full receipt.
This page does not claim a post-cleanup full pass.

## Failed and negative evidence

Keep these receipts as evidence of failure modes:

- Slow-reader full-run failure in `../.runs/verification/1791185642606452000-304/report.json`
- CORE-07-B full-run failure in `../.runs/verification/1791185835787000000-4022/report.json`
- Wrong-pixels negative report in `../.runs/intent-negative-1791180824088958000/native-editor/.runs/verification/1791181963547193000-69082/report.json`

The wrong-pixels run compiled successfully.
It failed only the intent comparisons for CORE-04-A and CORE-05-A.
Each case reported 4,096 wrong pixels.
The old verbose measurements and moved task records are indexed in [HISTORY.md](HISTORY.md).

## Evidence boundaries

The Rust compiler proves Rust type and privacy rules.
The document checks prove link and contract structure.
The development verifier proves its recorded source rules and P0 observations.
Artifact checks read actual bytes.
Playback, listening, and creative review remain separate.

No historical Python or FFmpeg receipt promotes a Rust capability.
Read [VERIFICATION.md](VERIFICATION.md) before a native code handoff.
