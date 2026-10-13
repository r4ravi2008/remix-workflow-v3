# Native preparation A05 saved pure-control evidence review

## Disposition

The saved A08 evidence consistently supports five A05 pure saved-report
controls. I found no P1 or P2 in this evidence scope.

The evidence records two direct Rust builds and one direct harness invocation.
It does not qualify a loaded process image, native producer, media output,
GPU operation, Resolve operation, watched review, heard review, or creative
acceptance.

This is a same-family, nonblind review of saved evidence. I did not rerun,
compile, link, import, or execute the library, harness, controls, helper,
native code, or media code. I did not publish a new inventory.

## Saved evidence identities

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `native-preparation-pure-attempt-a08/preflight.json` | 87,471 | `2b89dcc5dc5472867c17f27ac1474726ba8230f9faa6b3a1ab405eec7eaf64f5` |
| `native-preparation-pure-attempt-a08/report.json` | 11,190 | `f68eafc1531f2c36467833b093e21db2cb26d50fc33c3aeae3dedb7f9b16a98d` |
| `apps/video-studio/docs/design/native-preparation-implementation-parent-control-readback-a08.md` | 1,509 | `d1df3f997476fe51c842cf2792830d488ab8d7691e6369567320b4a5efc865b8` |

The preflight contains 138 unique input rows totaling 80,154,926 bytes. A
read-only current check found all 138 hashes and all nine identity fields
unchanged. The saved report independently records before-and-after equality
for the same inputs.

## Fixed commands

The preflight and report contain the same three ordered argv arrays.

The first command builds `native_preparation_implementation_a05` as an rlib.
It uses direct `rustc`, edition 2021, the `aarch64-apple-darwin` target, fixed
dependency archives, and `-C panic=abort`.

The second command builds `native_preparation_pure_controls_a04` as a normal
binary. It links the generated A05 rlib. It uses the same fixed archive roots,
`-C panic=abort`, and `-C lto=thin`. It does not use libtest.

The third command invokes only the generated direct harness binary. No Cargo
resolver command appears. The report sets `cargoResolverUsed` to false.

All three commands returned zero. No command timed out or received a signal.
All three stderr files are empty. Both build stdout files are empty. Each log
remains within the 4 MiB cap.

## Generated outputs

| Output | Bytes | SHA-256 |
| --- | ---: | --- |
| `libnative_preparation_implementation_a05.rlib` | 3,907,864 | `dedadef25dbbd481ada781c9a625582da45131b592f207b348e74f7d8acb4833` |
| `native-preparation-pure-controls-a04` | 1,516,424 | `517ae793d43d49f1b53d57be0c67736d6eb7c492d34252ed8e5d2a6da5430451` |

The two standalone output receipts equal the corresponding report objects.
A read-only current check found both output hashes and all nine identity
fields unchanged. The report also records stable output identities after the
harness invocation.

## Five control results

The harness stdout is 293 bytes with SHA-256
`54588e638d085b2bc9d4df1663a37da97e19b92270a368abab7f535853d9b4f2`.
It exactly equals these six ordered lines:

```text
passed saved_expansions_and_authority_counts_are_exact
passed baseline_mutations_and_fresh_identity_controls_reject
passed observer_branches_include_normal_pixel_failure
passed combined_source_control_entrypoint_keeps_both_summaries
passed pinned_acceptance_remains_unavailable
passed total=5
```

The source-reviewed bodies check expansion counts 153, 339, and 89. They
check encoded totals 154, 341, and 90. They retain baseline, closure, log,
binary, role, path, and observer-branch controls.

The fifth control confirms that the pinned acceptance root remains absent.
It also confirms that qualification returns `NoPinnedTrustRoot`. The run did
not create accepted authority.

## Evidence boundary

The saved result supports one bounded statement: the exact direct builds and
one direct harness invocation completed, and the five pure saved-report
control bodies returned successfully with their fixed output lines.

The report does not attest which process image the operating system loaded.
It sets loaded-code qualification false. It also keeps accepted authority,
native producer execution, media execution, GPU execution, Resolve execution,
watching, hearing, and creative acceptance false. The Rust producer runner
remains a separate source and qualification task.
