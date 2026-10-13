# Independent arena verdict

This document records a read-only design review. I read the brief and both candidates in full.
I made no repository change and ran no Cargo command. This GPT-only cross-judge uses the arena's stated model availability.

| Criterion (0–5) | A: integrated CLI | B: separate verifier |
| --- | ---: | ---: |
| Preserve runtime/library boundaries | 3 | 5 |
| Enforce current guard gaps with meaningful negative cases | 5 | 4 |
| Current-build evidence and default/hook isolation | 4 | 4 |
| Bounded processes and honest incomplete outcomes | 5 | 4 |
| Minimal maintainer burden | 2 | 4 |
| Extensible shared Rust API with optional future Lua | 4 | 5 |
| **Total** | **23** | **26** |

I recommend B as the base. A third, binary-only development crate adds a small ownership cost. It keeps Cargo, Node, process control, fixture workspaces, and report publication outside both runtime crates. `editor-core` remains the typed semantic API. The editor CLI remains the direct runtime interface. A future Lua adapter can call the same Rust API without access to the verifier or changes to expression semantics.

B's fixed `architecture` and `full` modes support a rerunnable claim. It also uses exclusive run directories, separate default and hook Cargo targets, and observed binary hashes. Its negative fixtures cover the current nested-source, side-module, build-script, dependency-alias, promotion, receipt, and process gaps. The full plan preserves actual P0 acceptance and adds independent PNG and artifact readback. An architecture pass remains a structure claim. A full pass remains a current-build P0 claim, with creative review still open.

Two additions from A improve B. The whole-run deadline bounds the complete full plan, repeated tool startup, and audit work.
The negative fixtures examine policy gaps and accepted Rust code.

1. Add a fixed whole-run deadline to B's per-command process limits.
2. When the deadline expires, terminate the active process group.
3. Record remaining required checks as `incomplete`.
4. If possible, publish a failed or incomplete report.
5. Add A's `cfg`-disabled process call to B's negative fixtures.
6. Add A's optional or target-specific forbidden dependency fixture.
7. Add A's external module path fixture.
8. Add A's legal current-source control fixture.
9. Do tests to confirm that these cases find concrete policy gaps without rejection of accepted Rust code.

1. Keep B's verifier interface at two modes.
2. Do not add caller-selected checks, expected outcomes, report paths, or feature-promotion controls.
3. Give the two document checkers explicit exclusive output paths.
4. Do not copy a full historical workspace into each run.
5. Do not claim that the Rust source scanner is a sandbox.
   This restriction covers arbitrary Rust, proc macros, and third-party build scripts.
6. Keep the current P0 behavior tests intact.
7. Move repository-wide source enforcement into the verifier.

The present fixed receipts collide. Thus, the two document checkers need exclusive output paths.

Before implementation, resolve these details inside B's fixed plan:

1. Record `NATIVE_EDITOR_EVIDENCE_DIR` for default and hook suites in the exact commands.
2. Before you accept hook evidence, build a fresh hook executable.
3. Calculate the hook executable's hash.
4. Where feasible, run Cargo with `--locked --offline`.
5. Classify unavailable cached dependencies as incomplete.
6. Do not change the lockfile.
7. Do not fetch new code silently.

The shown command list leaves the evidence binding implicit. Hook tests alone do not identify an output binary.
These are acceptance details, not reasons to choose A.

A has the stronger explicit whole-run budget and broader fixture set. Its feature-gated CLI still adds a process-capable development interface to the runtime crate. The three-target snapshot workflow, copies of historical links, and extra `--root`/`--out` coordination add maintenance cost. Its own assurance language correctly avoids arbitrary-Rust guarantees, but the proposed macro restrictions need frequent policy updates. B keeps the ownership line clearer with less routine coordination.
