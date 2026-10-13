# Native preparation implementation A02 — parent source review

A02 remains source-only and unexecuted. Root rejects it before compilation.
A01 and A02 remain preserved. The trust pin and Accepted authority remain absent.

## Reviewed material

Root read the complete A01-to-A02 delta for Cargo.toml, lib.rs,
artifact_observation.rs, saved_report_adapters_v1.rs, observer_stdout.rs, and
acceptance_v2.rs. Root read the new pure_controls.rs, four current fixtures,
README, rationale, verification plan, pure-control contract, and manifest.
Unchanged error.rs, strict_json.rs, and the three reused RoleIndex sources had
prior complete source review. Their current manifest identities match.

The 27 manifest rows match 542,058 current bytes. The self-excluding manifest
is 6,525 bytes, SHA-256
`9f90b6cde5083264ad23a28433f10b242ff653e45a6a76863394f57a104d5639`.
The adapter source is 40,509 bytes, SHA-256
`dc56a40da76a0ac9b7537b7c5a22a43365830f5e5ef28f7066263fb4c522f73e`.

Root also read the relevant saved build and pure-report fields as ordinary JSON.
Root inspected the original pure runner's derivations at lines 430–436 and
2032–2052. No target source was imported or executed.

## P1 — the closed role map omits schema

RustToolchainReportAdapterV1 loops over schema at line 190. It calls role_token
for that scalar at line 197. The closed match at lines 660–718 has no schema
entry. A valid report therefore fails with role_token, unmapped closed
field=schema, before the required 89-row expansion.

Add the exact lowercase schema token in a preserved successor. Exercise all
three actual saved-report expansions through the reused encoder after source
review, rather than assuming map completeness from its spelling policy.

## P2 — several match booleans still use different derivations

The original pure runner compares descriptor and pathname observations against
its retained before observation. It compares the build closure against its
prepared expected closure, all six binaries against their initial observations,
and seven logs against their initial observations.

A02 instead assigns both pair flags from descriptor == pathname. It derives
buildClosureMatched from closure_dependencies.len() == 76. It appends true for
each structurally valid log. It derives allBinariesMatched from four selected
rows aligned with positions two through five of the six-row list.

These predicates do not reproduce the saved fields' meanings. Two current
observations can equal each other while both differ from the original baseline.
A valid 76-row closure or correctly located log can also differ from its
baseline. Dependencies omit the observations needed for those comparisons.

A06 lines 247–248 require the loader to recompute each derived boolean and
reject copied mismatches. Merely changing a report flag fails A02, but changing
its structural inputs coherently can leave an incorrectly derived true flag.
The author's stated structural-only buildClosureMatched limitation is honest,
but it leaves this selected requirement incomplete.

The narrow repair must supply and join the exact measured baselines used by
these fixed report families. Preserve RoleIndex format and row cardinalities.
If a required original baseline cannot be recovered, return an explicit
unavailable error for that semantic derivation. Do not manufacture a match from
cardinality or endpoint membership. This is a saved-adapter requirement;
Rust native producer qualification remains independent of Swift evidence.

## Repairs confirmed within source scope

Explicit borrowed lifetimes and the renamed directory endpoint close the
previous compile findings. Source and log rows now use their exact six-key
parsers. The pure files object uses its seven closed names. Emitted role tokens
otherwise follow the strict lowercase grammar. Executable argv tokens remain
absolute paths, while fixed arguments use UTF-8. Final 89-row cardinality and
the closed token map reject truncated or extended vectors in the current shape.

Fresh callback results now join source-owned role, path, bytes, and hash. The
reused encoder validates regular-file identities. A held saved-root descriptor
is rechecked around each fixed report read. The reader still uses joined paths
and no-follow final opens; it does not claim openat or complete ancestor pinning.

The three failure fixtures now use failed state. The fixture helper explicitly
checks all four variants. Normal failed pixels no longer need exception fields.
The complete-check marker and exception measurements remain caller-supplied
candidate data, with no Accepted construction route.

Accepted<T> has private fields and an Infallible member. open_pinned remains
unavailable. No source pin, loader qualification, native runner, or acceptance
record was created. Dependency resolution and compilation remain unperformed.

## Disposition

Root found one P1 and one grouped P2. Independent A02 peer review is pending.
No package, compiler, control, native producer, observer, comparator, media,
GPU, or Resolve execution occurred. No listening, normal-speed watching, or
creative acceptance was established.
