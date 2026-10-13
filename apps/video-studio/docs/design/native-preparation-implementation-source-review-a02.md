# Native preparation implementation A02 — independent source review

This review is source-only. I read the complete A01-to-A02 source delta,
the A02 contracts and fixtures, the reused RoleIndex V2 sources, and all
manifest-bound files. I did not import, compile, execute, run controls, launch
a native process, inspect media, or change frozen package files.

## Bound inputs

The reviewed package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/native-preparation-implementation-a02`

Its self-excluding source manifest is 6,525 bytes with SHA-256
`9f90b6cde5083264ad23a28433f10b242ff653e45a6a76863394f57a104d5639`.
All 27 manifest rows match their current file bytes and SHA-256 values. The
rows total 542,058 bytes. The adapter source is 40,509 bytes with SHA-256
`dc56a40da76a0ac9b7537b7c5a22a43365830f5e5ef28f7066263fb4c522f73e`.
The new pure-controls source is 3,374 bytes with SHA-256
`9a539f9656265ce5a65fc7dca48b12e7036d7b7486dac209b28c2951807e1e7a`.

The manifest-bound RoleIndex model, validator, encoder, complete vector,
saved reports, decoder reports, and postcheck also match. The reused validator
keeps the required role grammar `[a-z][a-z0-9_.:-]{0,127}` at
`native-role-index-v2-a02/src/validate.rs:101-115`.

## P1 — the Rust toolchain adapter has no `schema` role token

`src/saved_report_adapters_v1.rs:190-198` includes `schema` in the eleven
top-level scalar loop. The loop calls `role_token("schema")`. The closed map at
`src/saved_report_adapters_v1.rs:660-714` has no `schema` arm. A valid fixed
toolchain report therefore returns `role_token: unmapped closed field=schema`
before `expand_tool_observations`, `expand_frameworks`, or the expected 89-row
count can complete.

The A06 contract defines those 89 rows as 11 top-level scalars, seven files,
nine observation lists, 24 argument scalars, nine return codes, nine output
files, one framework list, and 18 framework rows. The missing token blocks the
entire valid report path. A successor must add one lowercase `schema` token
and exercise all three adapters through the unchanged RoleIndex encoder.

## P2 — pure-input match booleans still use structural substitutes

The A02 adapter claims complete recomputation, but
`src/saved_report_adapters_v1.rs:314-333` does not reproduce the fixed report
semantics. `expand_paired_file` and `expand_paired_macho` at lines 345-376 set
both `descriptorMatchedBefore` and `pathnameMatchedBefore` from
`descriptor == pathname`. The source runner records each comparison against
the held `before` observation. Two current observations can equal each other
while both differ from that baseline.

The same function derives `buildClosureMatched` from `len() == 76`, sets each
log fact to `true` after endpoint parsing, and derives `allBinariesMatched`
from selected positions two through five. The source runner compares the
closure with its prepared expected closure, all six binaries with the initial
binary observations, and all seven logs with the initial log observations.
Those semantics are visible in
`run_swift_controls_a03.py:2032-2052`. The A02 dependencies therefore omit
the observations required to reproduce the saved booleans.

The repair must bind the exact measured original baselines used by these
reports, or return an explicit unavailable result when a baseline is absent.
Changing only a reported boolean is already rejected. Coherently changing the
structural observations can still produce an incorrectly derived match.
Rust producer qualification remains separate from Swift and comparator
qualification.

## P2 — held-root rechecks do not pin intermediate report directories

`src/artifact_observation.rs:45-113` holds and rechecks the unit-root
descriptor and pathname. `read_bound_report` then joins a fixed relative path,
and `read_report_file` opens that path with final-component `O_NOFOLLOW`.
Neither function holds or rechecks the intermediate directory descriptor, such
as `swift-build-attempt-a02` or `toolchain-observation-a01`.

Replacing an intermediate directory while the unit root remains unchanged can
redirect the joined pathname to another regular report. Final-file identity
checks cannot establish that the report came from the original intermediate
directory. The A01 peer requirement for unit-root and intermediate-directory
ownership therefore remains open. A later reader must use descriptor-relative
component traversal or hold and recheck every fixed intermediate directory.

## Repairs confirmed

- Explicit borrowed lifetimes and the renamed endpoint local close the A01
  source findings at `saved_report_adapters_v1.rs:648-658` and `717-760`.
- Source and log objects retain exact six-key shapes, and the pure files object
  retains its seven exact names.
- Lowercase role tokens are used consistently except for the missing `schema`
  entry identified above.
- Toolchain executable tokens use `PathBytes`; fixed arguments use UTF-8.
  Final row cardinality rejects a truncated vector, while an extra token fails
  the closed token map.
- Fresh observations now require the requested role, absolute path bytes,
  size, and hash before appending rows.
- The four fixtures use failed state and the pure control asserts normal,
  exception, safe-publication, and unsafe-publication branches.
- Normal pixel failure accepts complete measured checks without exception
  fields. Exception joins compare separately measured code and detail.
- `Accepted<T>` has private fields and an `Infallible` member. `open_pinned`
  still returns `PinnedManifestAbsent`; no acceptance value can be created.

## Disposition

A02 remains source-rejected because of the missing `schema` role token and the
two evidence-boundary gaps above. The package remains uncompiled and
unexecuted. No native, Swift, comparator, media, GPU, Resolve, watching,
listening, or creative acceptance claim is made.
