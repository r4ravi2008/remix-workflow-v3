# Rust producer trust root A01 parent source review

A01 is source-rejected with one P1 control blocker and one P2 aggregate-recipe ambiguity. It remains uncompiled and unexecuted. No active production pin exists.

Root read all 1080 trust implementation lines, all 869 source-control lines, library imports, direct harness, complete fixed build recipe, contracts, fixture recipe, output schema, source-static check, and the complete peer report. Root checked the five synthetic acceptance records and ten review artifact references against the fixture plan. Synthetic data creates no production acceptance.

All thirty-six package rows match 129322 bytes. All seventeen external rows match 240985 bytes. The manifest is 13070 bytes with SHA-256 2e31a83c6ecf07b8d99270e4db298892669983504a3289a3438a26459240d8a2.

## Confirmed findings

1. P1: Swapped-review and acceptance-cycle controls replace acceptance bytes and update the manifest, but reconstructed_source retains the original fixture-plan top acceptance reference. The memory backend compares changed bytes against that stale hash and returns artifact_reference_join. Both controls therefore stop before their intended trust_entry_join and acceptance_reference_cycle checks. Rebind only the private reconstructed top reference to exact changed bytes for each mutation.
2. P2: Aggregate metadata decodes to a suffix of two backslashes and zero, bytes 92/92/48. Hashing that literal domain does not reproduce the declared digest. The digest does reproduce with bare ASCII rust-producer-trust-root-source-package-v1, one NUL byte, and sorted UTF-8 path rows encoded u32be(path bytes)+path+u64be(file bytes)+raw SHA-256, with no count/total prefix or trailer. Declare that complete recipe explicitly in the successor.

Root independently confirmed both peer findings. The verified package aggregate under the reconstructed recipe is 416f741add9eeef84e92767dbcfdda2143162b697f19e18ced915d90b03ddea1. No individual source or external binding differs.

The implementation retains exactly two public subject keys and five evidence classes. The manifest and acceptance parsers have closed field sets and duplicate-key rejection. Source qualification joins all nine nested record/review rows. Accepted fields, constructor, and value extraction remain private or crate-private. The production pin is None and embedded manifest bytes are empty. open_pinned fails before parsing.

The fixture backend exists only under source-controls. The filesystem reader's bounded descriptor and pathname checks were source-reviewed, not executed. Full fixed real-subject reconstruction, five real acceptance records, bootstrap source/binary review, production pin data, and attempt-specific authorization remain unimplemented or absent.

A minimal additive A02 must repair the two fixture references and aggregate metadata, retaining production trust semantics and absent pin. No native, product, media, GPU, Resolve, watch, listen, or creative acceptance follows from this review.
