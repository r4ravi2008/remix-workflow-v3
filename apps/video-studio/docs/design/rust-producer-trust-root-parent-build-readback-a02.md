# Rust producer trust root A02 parent build readback

The fixed A02 library, harness, and no-argument fixture execution each returned 0. All 27 fixture cases passed once. The production pin remains absent.

I reopened all 125 inputs, totaling 75,172,991 bytes. Preflight, before, after, and current content hashes, byte counts, and nine-field file identities match exactly. The executed argv, cwd, and environment equal the frozen recipe. No Cargo resolution occurred.

The library emitted two dead-code warnings for the private Accepted value and unused extraction method. No compiler error occurred. Harness stderr, control stderr, and all stdout files are empty. All six log identities and hashes match the report. No command timed out, overflowed, or retained an open captured stream. All three command PIDs were absent at this readback. The owned temporary directory is empty.

The generated library is 3,982,136 bytes with SHA-256 ccca8ebab868af48c7370bb905ed7b28742f69ebcdcf8439459c93a919774539. The arm64 executable is 1,678,104 bytes with SHA-256 3cd845fc2a42cb3b80fac049555310e2822887e097a18356e1942685292f0834. Independent Mach-O readback found CPU type 16777228, file type 2, and UUID 2b8278adc06f3d168a38ab1d792885f5.

The 3,634-byte control report has SHA-256 99c509fbd4ad407f5a277e1f0319fd41ea22fa7897357bf40bb3f01f38455652. I read all 27 results. The repaired swapped-review and acceptance-cycle cases reached trust_entry_join and acceptance_reference_cycle, respectively. All intended rejection codes matched. The other five generated and log records matched their current content and identities.

The additive parent-actual-readback-a01.json preserves the current observations. This readback found no P1/P2 evidence defect. Separate-author actual-evidence review remains pending.

These are isolated fixture controls with an in-memory artifact reader. This run does not test filesystem race behavior, reconstruct real accepted producer subjects, install a production pin, or create attempt authorization. Native, media, GPU, Resolve, product, watched, heard, and creative acceptance remain unverified.
