# Technical documentation procedure

Use the installed [Simplified Technical English skill](https://github.com/0xpili/simplified-technical-english) for technical documents in this application.
Find the skill through the active skill catalog.
The shared dotfiles configuration supplies the skill. The application does not need its own copy.

The installed skill uses ASD-STE100 Issue 7 as its source.
The skill checker cannot establish full compliance with the official specification.
The writer must also examine word choices, technical terms, and requirement content.
The supplied word list gives parts of speech and approved forms. It does not give approved definitions.

## Document scope

The scope includes product requirements, architecture, feature contracts, scenarios, plans, tasks, procedures, and technical review reports.
It also includes the authored briefs and reviews under `.impeccable`.
Keep generated evidence under `.runs` and `.state` intact.
Keep dependency documents under `node_modules`, `.local`, `target`, and `dist` intact.
Do not rewrite earlier rows in the append-only [decision log](decisions.tsv).

Code, commands, identifiers, paths, quoted errors, official names, and quoted source text are outside the skill's prose rules.
Marketing copy and creative text are also outside these rules.
Preserve native lyrics and original quotations.
Do not mark ordinary technical prose as code or a quotation to bypass a check.

## Before the revision

1. Read the installed `SKILL.md`.
2. Read `references/writing-rules.md` in the skill directory.
3. Read `references/substitutions.md` in the skill directory.
4. Read `examples/before-after.md` in the skill directory.
5. Compare word choices with `references/word-list.md`.
6. Save the initial documents and their hashes.
7. Identify each document's procedures and descriptions.
8. Identify the protected requirements and literals.

## Protected application contracts

Preserve requirement strength, feature ownership, preconditions, actions, expected results, and non-goals.
Preserve all commands, code blocks, inline literals, link targets, IDs, numeric criteria, and review states.
Keep `planned`, `implemented`, and `verified` distinct.
Measured evidence does not establish playback, listening, or human creative approval.

The feature parser needs the current feature titles and seven section labels.
Keep the acceptance cases in their Verification sections.
Keep the CORE cases in their current order.
The specification checker also needs three exact Rust ownership phrases.
Do not change these parser requirements during a prose revision.

The [intent contract sidecar](features/intent-contracts.json) binds the raw bytes of [core.md](features/core.md).
After a CORE prose revision, review the feature intent before you update `coreDocumentSha256`.
Update only that digest for a prose revision.
Keep all fixture values, expectations, case IDs, and review requirements intact.
A digest match does not establish human contract adequacy.

## Revise the prose

1. Name the actor and exact target.
2. Use one stable name for each item.
3. Write one primary thought in each sentence.
4. Use at most 20 words in each procedural sentence.
5. Use at most 25 words in each descriptive sentence.
6. Put one procedure action in each numbered step.
7. Put a condition before its applicable action.
8. Use the imperative for procedure steps.
9. Use at most six sentences in each paragraph.
10. Divide paragraphs by topic.
11. Examine tables and headings manually.
12. Keep recommendations distinct from mandatory requirements.

## Run the checks

Set `STE_SKILL_DIR` to the installed skill directory from the active catalog.
Run the upstream checker with vocabulary checks enabled.
Use `mixed` mode for documents that contain procedures and descriptions.
Use `procedural` mode for a procedure that needs the 20-word limit.

```sh
python3 "$STE_SKILL_DIR/scripts/ste_check.py" --mode mixed docs/ARCHITECTURE.md docs/SPEC.md
python3 "$STE_SKILL_DIR/scripts/ste_check.py" --mode procedural <procedure-file>
```

1. Correct every checker error.
2. Run the checker again.
3. Examine each vocabulary warning.
4. Confirm technical names and their definitions.
5. Examine parts of speech against the word list.
6. Compare protected content with the initial documents.
7. Save the check output and manual review findings.

The checker skips code, headings, tables, and quotations.
The checker cannot establish correct approved definitions or preserved feature intent.
Zero checker errors are one part of the acceptance result.
Necessary technical terms can still produce warnings.
Do not disable vocabulary checks to remove those warnings.

Run the current document checks with new output paths.
The `--output` option preserves earlier receipts.

```sh
node docs/features/check.mjs --output .runs/<new-run>/feature-coverage.json
node docs/check-spec.mjs --output .runs/<new-run>/specification.json
target/debug/native-editor-check architecture
```

Finalize all source documents before you start the native verifier.
If a CORE revision changes the bound document digest, run the full verifier after the update.
Keep the earlier reports as evidence for their original snapshots.
Save new reports for the current document snapshot.

## Review technical names

The upstream checker flags technical names that end in an unapproved suffix.
Names such as encoding, compositing, and timing can be correct nouns in this application.
Keep the precise name when the sentence uses the correct concept.
Correct actual verb-form defects. Keep ordinary prose outside code and quotations.

The [project check](../../docs/check-writing.py) retains the raw upstream diagnostics and vocabulary results.
The [technical-use records](../../docs/ste-technical-uses.json) contain the reviewed contexts.
Each record binds a file, an exact normalized sentence, a word, and its occurrence count.
Each record also defines the concept and explains the particular use.
The records do not approve a word globally.

Run the project check from the native editor directory:

```sh
python3 ../docs/check-writing.py --skill-dir "$STE_SKILL_DIR" --approvals ../docs/ste-technical-uses.json --output .runs/<new-run>/writing-check.json
```

1. Correct every upstream error and sentence-length defect.
2. Examine every unresolved technical-name diagnostic in its sentence.
3. Compare the technical name with the actual feature or source contract.
4. If the use is valid, save its exact contextual record.
5. Ask an independent reviewer to examine the changed prose and records.
6. Run the project check again.

The project check rejects stale records, duplicate records, wrong counts, invalid schemas, and unresolved diagnostics.
A record cannot override an upstream error or a sentence-length diagnostic.
The check preserves vocabulary results for manual examination.
An exact record does not prove that a word has its approved meaning.
Zero unresolved diagnostics does not certify full official STE compliance.

## Record the result

Record edited documents, checker results, manual findings, protected-content comparisons, and independent review findings.
State which runtime or creative reviews remain incomplete.
Append the result to the decision log.
Do not replace historical evidence with a new document hash.

The initial STE migration saved its baseline and audit procedure under `.runs/ste-docs-1791184225862792000`.
That run contains `manifest.json`, `assignments.json`, `contract-trace.md`, and `corpus_audit.py`.
Run these commands from the `native-editor` directory.

```sh
python3 .runs/ste-docs-1791184225862792000/corpus_audit.py audit
python3 .runs/ste-docs-1791184225862792000/corpus_audit.py lint
```

The saved audit compares the current documents with that migration's fixed baseline.
Do not replace the baseline after the migration.
