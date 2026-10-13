# Implement and accept a feature

Use this procedure for Rust editor features that target DaVinci Resolve behavior.
Release Kit is one optional workflow profile.

## Define the feature

1. Read `AGENTS.md`, `SPEC.md`, and the applicable entry in `FEATURES.md`.
2. Read the feature entry in `capabilities.json`.
3. Record the creator purpose in plain language.
4. Record one concrete scenario.
5. Record the preconditions for the scenario.
6. Record the agent action and the expected observable outcome.
7. Record the non-goals for this unit.
8. Record every acceptance case ID and each owned file.
9. State how the verifier observes each expected outcome.
10. Describe one failure that can still compile.
11. Separate technical acceptance from playback, listening, creative, and contract-adequacy review.

Use `intentId` for retry identity.
Use the feature purpose for the creator result.
Do not use one name for both concepts.

## Implement one bounded unit

1. Read the public command schema before you send a request.
2. Use the direct Rust CLI for the actual feature path.
3. Record the command, response, artifact, and observed values.
4. Compare each observation with its expected value.
5. Save raw stdout, stderr, failed reports, and changed artifacts.
6. Keep failed evidence beside successful evidence.

If an executable check is missing, mark verification incomplete.
Do not mark a compiled runtime unimplemented because the check is missing.
If acceptance fails, keep the failure evidence and do not promote the feature.
Do not infer a feature result from compilation, a document check, or a hash.

## Complete the handoff

1. Run the feature acceptance cases through the actual CLI.
2. Read the saved report and inspect the referenced artifacts.
3. Run the full development verifier before code handoff.
4. Update only the capability state that the evidence supports.
5. Append the decision and evidence path to `docs/decisions.tsv`.
6. Request an independent review of contract adequacy.

Build and run the verifier from the `native-editor` directory:

    cargo build --locked -p editor-devcheck --bin native-editor-check
    target/debug/native-editor-check full

The full verifier covers repository rules and current executable feature outcomes.
The Rust compiler catches type and privacy errors.
Neither check proves that the contract represents the requested creator result.

## Read older evidence

Use [VERIFICATION.md](VERIFICATION.md) for the current command and evidence rules.
Use [INTENT-VERIFICATION.md](INTENT-VERIFICATION.md) for purpose and contract review.
Use [HISTORY.md](HISTORY.md) for archived designs, task records, and old score tables.
