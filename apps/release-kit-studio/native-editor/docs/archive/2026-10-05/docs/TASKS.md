# Native editor work record

The current scope includes the authorized Rust foundation and the 81-family specification expansion.
Effect and optional UI adapters remain separate future applications.
The earlier spec-only run is historical. Its baseline and audit do not describe the current runtime.

## Rust foundation

- [x] Read the Principles section of poteto-mode in full.
- [x] Trace the affected boundary through `how`.
- [x] Compare ownership designs through `architect` and `arena`.
- [x] Record necessary first steps, independent tasks, shared state, and the smallest safe task division.
- [x] Assign one code owner to the coupled Rust domain, protocol, storage, and CLI.
- [x] Implement CORE-01 through CORE-08 as a bounded Rust library and direct CLI.
- [x] Review the actual source independently and repair the concrete findings.
- [x] Save the final current-build acceptance evidence and independent PNG inspection.
- [x] Complete the measured progress record and handoff.

Each acceptance run uses isolated state.
SQLite transactions serialize real project writes.
The library cannot terminate its host.
The CLI owns process framing, result selection, and exits.
Native P0 execution does not need Effect, Node, Bun, a browser, a Cloudflare account, Resolve, or an external GPU.

## Parallel feature-detail specification

- [x] Read the Principles section of poteto-mode in full.
- [x] Phase A: Frame. Cover exactly the current 81 IDs with creator scenarios and explicit boundaries.
- [x] Phase B: Design the workflow. Freeze the assignment, common headings, and completion predicate.
- [x] Frame. Require complete coverage, concrete scenarios, bounded pieces, proof cases, and links that resolve.
- [x] Fan out. Seven writers own seven separate domain files. Only the parent writes the index and ledger.
- [x] Aggregate. Examine actual artifacts and integrate contract paths, case IDs, and navigation that starts with scenarios.
- [x] Phase C: Run the loop. Independently review all domains and correct ambiguous boundaries.
- [x] Phase D: Keep the audit trail. Save final decisions and measurements.
- [x] Phase E: Verify and hand back. Refresh structural receipts and open the guide.

The parent froze all 81 assignments and the seven-section contract before the writers started.
Each domain document has a separate owner.
The runtime code has a different owner.
Only the parent edits the shared ledger, index, coverage manifest, and progress records.
The seven domains keep related knowledge together without concurrent writes to shared files.

This expansion specifies future behavior.
It does not implement all 81 families or map every Resolve control.
The independent review and corrections are saved in [FEATURE-REVIEW.md](FEATURE-REVIEW.md).

## Earlier specification run

The spec-first run completed framing, design comparison, synthesis, document checks, and independent specification review.
[baseline.json](baseline.json), [AUDIT.md](AUDIT.md), and [decisions.tsv](decisions.tsv) preserve that earlier scope.
The user later authorized Rust implementation.
The user also separated the Effect wrapper from the editor.

## Workflow adaptations

The installed Poteto workflows mention Cursor roles and unavailable model families.
This run uses Codex collaboration agents and records the actual GPT model used for each independent review.
The review does not establish cross-family model independence.
The cursor-team-kit control-cli and deslop skills are absent.
Actual local CLI checks provide the integration proof.

Commits, PR publication, deployment, GPU work, and production media are outside this bounded local task.
The repository contains unrelated uncommitted work.
This handoff does not need branch publication or a rebase.
