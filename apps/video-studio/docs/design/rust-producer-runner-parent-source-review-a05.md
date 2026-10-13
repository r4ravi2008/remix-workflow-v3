# Runner A05 parent source review

Disposition: rejected for compilation and control execution. No A05 compiler, control, bootstrap, authorization, or native invocation is authorized by this source review.

The frozen manifest SHA-256 is `e0f4b89579ee5675611b02eeddaae9059d7b325c2d81e128cbd465c71a5f7253`. Its 13 source files total 250,148 bytes, aggregate `0307a9d6dc9996ebd728b850f0f3c7f6e14441ffe0ccd49c7ec62499756c4e94`. Its 64 external rows total 9,917,501 bytes, aggregate `b6e6a5ae0d487b54a0bf3cc60731f30d69b6c9ef5a81885f8f41676a31301d80`.

The saved parent readback is `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a05-parent-source-readback-a01.json`, 427,576 bytes, SHA-256 `9a5ad34f690f475bbf6a8b71078030ae0cf0bd65be56bed76db46125b855778d`. It measures 357 inputs totaling 126,455,355 bytes before and after. All content and nine-field file identities match. Its explicit import traversal covers 25 references and 22 Rust source files. It imports no project module and executes no compiler or native binary.

Two initial readback attempts stopped before publication. The root helper incorrectly required unique external roles instead of unique `(role, path)` pairs. Its second attempt rejected macOS's `/tmp` symlink when measuring the orchestration utility. The corrected helper uses the manifest's framed role/path uniqueness and canonical `/private/tmp` utility path. Neither failure changed frozen source or created a proof file.

## Findings

1. **P1 — incomplete CLI dependency resolution.** Both CLI commands in `direct-build-recipe-a05.json` omit the two fixed external dependency search directories. They only expose the local runner rlib. The library's transitive crates remain outside the CLI search path. Preserve the four measured archives and add the two existing dependency paths to both CLI commands.

2. **P1 — controls contain an invalid struct field.** `src/a05_control_extension.rs:1233` supplies `authorization` to `QualificationData`. The production struct has no such field. Keep that artifact in the private authority vector and remove the invalid initializer.

3. **P1 — controls borrow a moved layout.** `src/a05_control_extension.rs:1176` moves `layout` into the first tuple element before cloning it for the stage. Construct the stage before returning the tuple.

4. **P1 — negative controls inspect the wrong result.** Authorization-file mutations fail the retained-file check with `authorization_drift`. Six focused controls expect the later `authorization_invalid` check. Sidecar rejection and preflight FIFO rejection save terminal evidence, then return `AuthorizationNotReviewed`; controls inspect only the coarse error or require a closed result. Inspect the saved terminal and child-start fields on each applicable error. Require the exact expected rejection and no child. Do not bypass retained authorization validation.

5. **P1 — unavailable-loader dispatch is inconsistent.** The lifecycle subprocess supplies production CLI arguments to the controls binary. `dispatch_a05_with_focused` returns 64 for those arguments. Its expected 78 response also uses the superseded acceptance-unavailable JSON. Route the fixed CLI arguments to the production CLI only while bootstrap is absent, and match the current qualification-unavailable response.

6. **P2 — pure control execution is not evidenced.** Reports declare 21 copied pure cases. Neither lifecycle nor focused dispatch executes that schedule. Run the existing finite fixture schedule and record observed counts and failures. A copied count alone cannot establish 21 passing cases.

7. **P2 — postflight negative can pass on any error.** `focused_postflight_drift_a05` accepts its error branch based only on whether it attempted a mutation. Require the saved exact authority-drift rejection, actual child-start evidence, and successful process closure.

8. **P2 — collision control bypasses production authorization.** `focused_collision_case_a05` tests the private fixture writer twice. Exercise `write_attempt_authorization` against an existing sentinel through an owned private control directory. Verify refusal and unchanged sentinel identity/content.

The independent judge is also reviewing cross-read review-reference identity retention and the fixed four-entry run directory bound. Those issues remain pending at this parent review's publication.

## Scope

The root inspected the production qualification/authorization lifecycle and adapted controls. The separate peer provides a fresh same-family, non-blind source review. This parent review is not a successful compilation, a runtime control result, or a loaded-runtime attestation.

A02's previously reviewed real opaque qualification remains unchanged. The A05 private control loader also constructs that real opaque value. It then uses owned fake producer paths to test lifecycle behavior. The production binary excludes the controls entrypoint through its feature gate.

Preserve this A05 source and evidence. Prepare a narrow successor. After both source reviews pass, compile its fixed commands and run the finite controls once. Review the compiled production bootstrap separately before any primary invocation. Review the saved attempt authorization before acknowledging it.

Native result acceptance, product integration, WATCHED, HEARD, and creative acceptance remain false. The music-film proof and full correction loop remain unfinished.
