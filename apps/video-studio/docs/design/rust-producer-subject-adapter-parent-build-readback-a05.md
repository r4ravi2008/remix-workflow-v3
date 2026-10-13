# Rust producer subject adapter A05 failed build readback

One fixed library compilation failed with return code 1. Harness compilation and the twenty-eight controls did not run. The failed source package and attempt are preserved.

Root read the complete stderr log. E0432/E0433 identify missing direct serde and serde_json dependencies. E0220/E0223 associated-type diagnostics cascade from those unresolved imports. The log has eighteen error diagnostics and one unused-import warning. The warning requires no repair.

The direct recipe reused existing archives and used the declared repository cwd and fixed ten-field environment. It omitted serde/serde_json extern arguments needed by inherited strict_json.rs and fixture_controls.rs. Root and peer source reviews missed this recipe dependency gap.

Root independently reopened all 131 current input files, totaling 76512015 bytes. Full hashes and all nine identity fields match preflight, before, and after rows. Both saved streams match. The compiler returned 1, was reaped, and its PID is absent. No timeout, output overflow, open capture stream, generated library, harness binary, candidate vector, or control report occurred.

Root saved the full readback in rust-producer-subject-adapter-a05-attempt-a01/parent-failed-build-readback-a01.json. Actual-evidence peer review is pending. Minimal additive A06 will bind and add only the missing existing archives, audit inherited extern imports, and advance successor labels. No new dependency resolution is required.

No native producer, Accepted value, active pin, execution authorization, product integration, media, GPU, Resolve, watched, heard, or creative acceptance exists.
