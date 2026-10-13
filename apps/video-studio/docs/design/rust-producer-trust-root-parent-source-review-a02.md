# Rust producer trust root A02 parent source review

A02 passes the finite parent source review with no P1 or P2 finding. Separate source review and one fixed build/control attempt remain pending. The production pin and embedded production manifest remain absent.

Root read every A01-to-A02 source, harness, contract, fixture-recipe, output-schema, and rationale delta, plus the complete fixed build recipe and aggregate metadata. The 1080-line production trust implementation, library module imports, and every synthetic fixture are byte-identical to A01.

All thirty-six package rows match 132549 bytes. All twenty external rows match 263714 bytes. Root reproduces the explicit source aggregate fe7a9b7fadad0bc9296d62573e807419c6ef4a74b2b8f9844f636c1b20652234. Manifest: 15734 bytes / f6f18d6d79c5d579aab937572bc60435faaf5b8a6769b5ef5217f03d59b602b9.

## A01 findings closed at source level

The swapped-review and acceptance-cycle cases now derive their top acceptance reference from the exact altered record bytes before moving those bytes into the fixture map. reconstructed_source_with_acceptance changes only the top source reference. Nested subjects, nested record/review references, logical rows, and expected validator codes remain unchanged. The helper is private inside the feature-gated control module.

The manifest now specifies a bare ASCII domain, exactly one NUL terminator, ascending raw UTF-8 path order, u32be path length, path bytes, u64be file bytes, raw SHA-256, and no count/total prefix, separator, or trailer. That declared recipe reproduces its digest without an inferred escape interpretation.

The fixed direct recipe binds the observed compiler, libc/serde/serde_json/sha2 archives, both existing dependency roots, edition 2021, panic-abort, thin-LTO harness, thirty-three exact source/fixture inputs, separate fresh build/control roots, and zero harness arguments. Root reopened those declared inputs and archives; every identity binding matches. Both attempt roots are absent before any execution.

A01 remains preserved. No compilation, import, target execution, real acceptance record, active pin, authorization, native producer, product integration, media, GPU, Resolve, watch, listen, or creative acceptance occurred during this source review. A later real qualification still requires fixed reconstructors, reviewed real data, and bootstrap source/binary review.
