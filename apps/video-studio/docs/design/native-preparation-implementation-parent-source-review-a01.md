# Native preparation implementation A01 — root source review

A01 is preserved and rejected before compilation or execution. Root read every new source file, all four observer fixtures, Cargo.toml, README, rationale, verification plan, and the complete manifest. All twenty-five package/external rows match current bytes and SHA-256. They total 522,683 bytes. The 4,978-byte manifest matches SHA-256 `98f6024587e7ae54d9f3b7887fe4c9567e55e2cbc90097157991e7dd5a03b3cc`.

Root also checked the actual saved Swift source-row and log key sets. Root read all nine actual toolchain argv arrays. The reused RoleIndex V2 validator retains its reviewed lowercase role grammar and absolute path scalar semantics.

## P1 — adapter helpers cannot compile as written

In `saved_report_adapters_v1.rs`, `expect_string` at line 544 and `expect_tool_file` at line 585 return a borrowed str. Both functions have two reference inputs and no explicit output lifetime. The return must be tied to the Object borrow. In `find_directory_role`, line 533 assigns a tuple to the local name `endpoint`. Line 536 then attempts to call that tuple as the endpoint function. Use explicit object-borrow lifetimes and a distinct local endpoint name. These are source findings; root did not invoke a compiler.

## P1 — valid source and log rows fail the shared regular-file key check

`expand_closure` validates six source-row fields, then passes the unchanged object to `regular` at line 245. `regular` requires the four-field FILE_KEYS shape. The real saved source row includes relativePath and role, so the adapter rejects every valid build closure. `expand_inputs` repeats this error for six-field LOG_KEYS at line 289. Validate each complete enclosing object once, then extract the four regular-file fields through a helper that preserves the outer shape check. Do not widen FILE_KEYS globally or accept unknown keys. Controls must expand both exact saved reports and reject a new outer field.

## P1 — emitted role names violate the reused RoleIndex grammar

Adapter role suffixes directly embed saved camelCase keys such as compilerExecutable, sourceRows, pythonInvocationText, allBinaries, and infoPlist. The reused validator accepts only `[a-z][a-z0-9_.:-]{0,127}`. Encoding therefore rejects otherwise valid expansions. Use a closed, documented source-key-to-role-token map with lowercase tokens. Apply the map consistently to every row and reference. Preserve the RoleIndex validator and the 153/339/89 expansion counts. Controls must check every emitted role and exact reference graph.

## P1 — option and command tokens are misclassified as absolute paths

`expand_tool_observations` encodes every argv token as PathBytes at line 353. The actual saved arrays include --version, which, cargo, -vV, --sdk, macosx, --show-sdk-path, and other ordinary tokens. The reused path scalar validator requires an absolute path, so the valid toolchain report cannot encode. Retain the executable invocation token as a path scalar. Encode ordinary flags and command values as UTF-8 scalars through a closed per-observation mapping. Preserve exact order and all twenty-four argv scalar rows. Do not weaken absolute path validation.

## P1 — three positive observer fixtures do not use the selected exception envelope

The classifier correctly requires state=failed and exit status 1 for every exception envelope. The exception fixture instead uses state=pixel_failed. Both publication-failure fixtures use state=publication_failed. All three become ContractViolation. `classify_bounded_fixtures` returns Ok even for those variants, so a test that checks only success of the Result would miss the mismatch. Correct the fixtures and assert their exact semantic branches. Keep an ordinary direct three-key stdout plus measured failed disk report for the distinct normal pixel-failure branch. Require joins for measured path, bytes, hash, state, status, and exception detail. Preserve the exact A07 envelope instead of relaxing the classifier.

## P2 — fresh toolchain observations omit the requested path and role join

The toolchain artifact, output-log, and framework loops compare returned observations only with saved content size and hash. The caller-owned FreshRegularFileObservation can return the same bytes under a different path or role. The adapter then retains that unrelated observation. Require the exact source-owned requested role and saved absolute path bytes before appending each observation. Also retain the RoleIndex identity-size and regular-file checks. Negative controls must use identical content under another path and a different valid role.

## Retained boundary

`Accepted<T>` remains uninhabited. `AcceptanceTrustRootV1::open_pinned` returns PinnedManifestAbsent. No trust pin or native authority was created. The saved-report adapters remain unqualified observation candidates. The selected design keeps Rust producer qualification independent of Swift, observer, and comparator evidence. Rust still needs its own stage-specific runner qualification.

Root did not import a target module, compile this package, run a source control, launch a native producer, call a native framework, mutate media, use the GPU, or operate Resolve. No listening, watching, or creative acceptance changed. Independent source review remains pending.

A source successor must preserve this package, repair the grouped findings, and add meaningful pure controls after source review. A01 must remain uncompiled and unexecuted.
