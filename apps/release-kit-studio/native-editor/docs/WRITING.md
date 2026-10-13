# Technical documentation procedure

Apply the installed Simplified Technical English skill to technical documents.
Find the skill through the active skill catalog.
The shared configuration supplies the skill.
This application does not keep a second copy.

The project checker pins the upstream checker and word list by SHA-256.
The pinned checker hash is `71850aa6f0aebaf980b176c59a18d13c713640ecd30d773e2fd04cf09a2244a2`.
The pinned word-list hash is `28bc1c52d2d1a1b1f564ed9e8e36f22a39ec0fb128ed973f7ba3212849a53afd`.
The checker uses vocabulary checks.
The checker does not certify full official ASD-STE100 compliance.

## Maintained corpus

The checker scans Markdown under `apps/release-kit-studio`.
The checker excludes only `apps/release-kit-studio/docs/archive` and `apps/release-kit-studio/native-editor/docs/archive` as immutable history.
The checker does not use a global word suppression.
Generated evidence under `.runs` and `.state` remains outside the corpus.
Dependency directories remain outside the corpus.

Code, commands, identifiers, paths, quoted errors, official names, and quoted source text keep their exact form.
Market copy, creative text, native lyrics, and original quotations keep their original voice.
Do not mark ordinary technical prose as code or a quotation.

## Protect the contracts

Preserve requirement strength, ownership, preconditions, actions, expected results, and non-goals.
Preserve commands, code blocks, inline literals, link targets, IDs, numeric criteria, and review states.
Keep `planned`, `implemented`, and `verified` distinct.
Keep technical evidence separate from playback, listening, and human creative approval.

The feature parser needs current feature titles and seven section labels.
Keep acceptance cases in their Verification sections.
Keep CORE cases in their current order.
Keep the parser-required Rust ownership phrases unchanged.

The [intent sidecar](features/intent-contracts.json) binds the raw bytes of [core.md](features/core.md).
After a CORE prose revision, review the feature intent before you update `coreDocumentSha256`.
Update only that digest for a CORE prose revision.
Keep all fixture values, expectations, case IDs, and review requirements intact.
A digest match does not establish human contract adequacy.

## Review and check the prose

1. Name the actor and exact target.
2. Use one stable name for each item.
3. Write one primary thought in each sentence.
4. Keep procedural sentences at 20 words or fewer.
5. Keep descriptive sentences at 25 words or fewer.
6. Put one action in each numbered step.
7. Put a condition before its action.
8. Use the imperative for procedure steps.
9. Keep each paragraph at six sentences or fewer.
10. Separate procedures from descriptions.
11. Keep mandatory requirements separate from recommendations.

Export `STE_SKILL_DIR` with the installed skill directory from the active catalog.
Use `mixed` mode for documents with procedures and descriptions.
Use `procedural` mode for a procedure that needs the 20-word limit.

```sh
python3 "$STE_SKILL_DIR/scripts/ste_check.py" --mode mixed native-editor/docs/WORKFLOW.md
python3 "$STE_SKILL_DIR/scripts/ste_check.py" --mode procedural native-editor/docs/WORKFLOW.md
```

Correct every checker error.
Run the checker again.
Review every vocabulary result in its sentence.
Confirm each technical name against the feature or source contract.
Keep a necessary technical noun when it names the correct concept.

The upstream checker skips code, headings, tables, and quotations.
The checker cannot establish approved word use or preserved feature intent.
Zero checker errors form one part of acceptance.
Necessary technical terms can still produce warnings.

## Check the maintained corpus

Run the project checker from the application root:

```sh
python3 -B docs/check-writing.py --skill-dir "$STE_SKILL_DIR" --approvals docs/ste-technical-uses.json --output native-editor/.runs/<run>/writing-check.json
```

The approval registry uses schema version 1.
Each record names a file, a normalized sentence, a word, and an occurrence count.
Each record also names a kind, a concept definition, and a reason.
The registry pins the upstream checker hash.
The registry approves one technical context.
It does not approve a word globally.

The project checker rejects stale records, duplicate records, wrong counts, invalid schemas, upstream errors, and unresolved warnings.
An approval record cannot override an upstream error or a sentence-length error.
The checker keeps raw vocabulary output for manual review.
Zero unresolved diagnostics do not certify full official STE compliance.

The independent reviewer must read each changed technical context.
The reviewer must compare the exact sentence with the feature contract or source.
The reviewer must inspect the registry record and its occurrence count.
Do not add a registry record to hide an ordinary prose error.

Run the regression command from the application root:

```sh
python3 -B docs/test_check_writing.py
```

The command checks the pinned checker, the registry, the archive boundary, and the maintained corpus.

## Finish the record

Run document checks after the prose is stable.
Use a new output path for each receipt.
Keep earlier receipts for their original snapshots.

```sh
node native-editor/docs/features/check.mjs --output native-editor/.runs/<run>/feature-coverage.json
node native-editor/docs/check-spec.mjs --output native-editor/.runs/<run>/specification.json
```

Run the native verifier after all source documents reach the final version.
Run a full verifier when a CORE digest changes.
Do not replace a historical receipt with a new document hash.

Record edited documents, check results, manual findings, protected-content comparisons, and independent review findings.
Record runtime or creative reviews that remain incomplete.
Use [HISTORY.md](HISTORY.md) for the earlier migration record and archived checker examples.
