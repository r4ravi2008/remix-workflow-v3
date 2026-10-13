# Rust producer subject adapter A04 parent source review

A04 is source-rejected before compilation. Three P1 blockers and one P2 recipe defect require a minimal additive A05.

Root read the complete harness, changed measurement reader, vector controls, library imports, diagnostic controls, contracts, manifest recipe, and complete peer review. The candidate adapter and historical fixture controls are byte-identical to A03. The saved-report adapter changes only its package comment.

All 14 source rows match 248,549 bytes. All 24 external rows match 388,559 bytes. Both aggregate recipes reproduce: source c2b86f690fead6584c986483046a9630cceb42e8f3382990ce3012530820151f and external 9d908febd83ee276d71ab02edfad698706c90fb9da467d3931e19cd541e57e39. All 20 fixed authority documents match. Root separately reopened the compiler, observed preflight, dependency closure, libc and sha2 archives. Both dependency directories exist.

## Findings

1. P1: The final literal JSON brace in the canonical report write! string is unescaped. Rust format syntax requires two braces for the literal closure. This is a source diagnosis, not a compiler result.
2. P1: Real growth and replacement controls still expect vector_reader_growth and vector_reader_replacement. The shared MeasurementSession validator supplies subject_file_changed for both identity changes. The manifest repeats the obsolete expectations. Keep distinct case IDs and align the expected codes.
3. P1: require_candidate confuses role-family totals with fixture resource counts. CandidateSummary loads sourceFiles=15, dependencyFiles=1847, dependencyArchives=35, toolchainRows=89, inputControlIds=21, and pngIdentityChecks=1921. The harness instead checks 38/1889/25/7 for four fields. Require the fixed resource counts and retain the independent 2068-row schedule.
4. P2: The declared compiler cwd is the package directory, while source, dependency, and archive arguments are repository-relative. Resolve the recipe from the repository root or use absolute paths throughout.

Root independently confirmed every peer finding from source and fixed fixture values. Peer review: rust-producer-subject-adapter-source-peer-review-a04.md, 8357 bytes, SHA-256 1afc497e2e98d4edecea95c74a9230e621272e974cd67d50b4c2fcf41396e729. The review is separate-author, same-model-family, and nonblind.

A04 repairs the missing static lifetime, aggregate recipe, canonical temporary paths, argument admission, full result gating, fresh reconstruction equality, and structured report design. Its crate-private disposable-file mutation hook now reaches the real reader and shared post-read validator. None of those source changes establishes an executed control result.

No source compilation, harness execution, Accepted value, active pin, trust data, native producer, media, GPU, Resolve, watch, listen, or creative acceptance occurred. A04 is preserved. Root requested only the four concrete repairs and successor bindings in A05.
