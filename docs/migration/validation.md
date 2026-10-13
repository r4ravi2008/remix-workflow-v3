# Source publication validation, 2026-10-13

Checks ran against an isolated copy of the reviewed Mac source. Local dependency
directories were copied for verification and excluded from Git. The original
checkout, index, branch, worker and production files remained unchanged.

The source snapshot commit is
`e20479e18e619f3a1763bdd36ab7d7be7f84b0bd`, based on
`15c28719209195edd2a7364ad25506ae83339534`. Its exact paths and SHA-256 hashes are
in [source-manifest.json](source-manifest.json). Setup and cutover requirements
are in [workstation-runbook.md](workstation-runbook.md).

## Measured checks

| Check | Result |
| --- | --- |
| Workspace resolver, video initializer, visual-sequence Node tests | 41 passed |
| Remotion template TypeScript | Passed |
| Video-director helpers | 9 passed |
| Music-video-director helpers, with Pillow | 28 passed |
| GPU-footage helpers | 16 passed |
| Portable Hunyuan graph builder | 4 passed |
| ACE-Step request/configuration tests | 22 passed |
| Acapella extractor preparation tests | 7 passed |
| GPU router typecheck, lint, tests and worker bundle | Passed, 23 tests |
| Release Kit typecheck, lint, tests and build | Passed, 133 TypeScript tests and 49 Python tests |
| Release Kit actual Bun loopback request checks | Passed, 3 request/deadline/cancellation checks |
| Native editor Rust default tests | 56 passed across acceptance/devcheck suites |
| Native editor Rust test-hook tests | 59 passed |
| Native editor warnings-denied clippy | Passed |
| Native editor architecture verifier | Passed |
| Native editor full verifier | Passed, 8 CORE families and 16 A/B cases |
| Video Studio Rust tests on macOS | 139 passed, 2 intentionally ignored child helpers |
| Video Studio Effect application prototype typecheck/tests | Passed, 8 tests |
| Existing acapella, ACE-Step and Instagram uv locks | Passed offline lock checks, 106/180/78 resolved packages |
| Portability audit | No high-confidence credential-pattern matches or missing lock/fixture errors |

The native editor full report hash is
`115beffcc37771bfa8879ec70310562dbb31f68156fa86d9cee24660c7a803af`.
The architecture report hash is
`de6072e5eaf82d78c7073e86c5c25a2c7779a5d19dcd45bf8f68ba4b2ffa2a37`.
Fresh report bytes and process logs are retained in the isolated checkout's
ignored `.runs/verification/` tree and the migration session's evidence folder.
They are local verification evidence, not published private runtime receipts.

The Mac toolchain was Node 24.9.0, Bun 1.3.7, Python 3.14.3 for standard-library
checks, Python 3.12.8 for existing ML/Pillow/pytest environments, uv 0.9.0, and
Rust/Cargo 1.94.0. Remotion resolved to 4.0.441. These are the measured versions,
not a claim that every workflow requires each exact toolchain version.

## Portability repairs

- Copied the exact latest independent alpha manifest and five PNG test inputs
  into the Rust fixture tree. Tests now resolve that directory locally. Manifest
  and image hashes remain unchanged; historical manifest paths are documentary.
- Marked native-editor `.runs/` references as Mac-local historical evidence.
  The document verifier can now check a clean source checkout without archived
  generated runs. Immutable archive manifests and payload bytes were preserved.
- Included the two npm lockfiles. The template lock's root requirements were
  matched to the pinned package manifest without changing its resolved packages.
- Added explicit ignore rules for secrets, provider/runtime receipts, private
  dialogue, production artifacts and account screenshots.
- Added the rerunnable, read-only `scripts/audit_workflow_portability.py`.

The auditor's generic credential-literal locations were reviewed. They contain
synthetic test credentials, schema/help strings, descriptive notes and an npm
`js-tokens` dependency range. A real token in a local provider receipt caused
that entire receipt to be excluded. No credential values appear in the audit
reports or publication manifest. The focused scanner is not a complete security
assessment.

## Remaining limits

The song-specific `test_motion_v5.py` requires an external production
`edit-contract.json` and source assets. Its setup failed because those private
inputs are absent from the source snapshot. Its five production-specific cases
were not exercised. The independent four graph-builder tests pass. Historical
song scripts retain Mac/iCloud, Resolve, GPU and provider paths; inspect and adapt
them before target execution.

The first sandboxed Release Kit test run could not bind loopback sockets. The
first sandboxed Video Studio tests could not start AVFoundation readers. Both
complete suites passed when rerun with local socket/native-framework access.
The first music helper run lacked Pillow; the complete suite passed in the
existing Python environment. Native document checks initially referenced ignored
reports; the final architecture and full verifiers pass after the documented
portability repair.

`git diff --check` reports pre-existing whitespace in imported archival/design
documents and a few configuration/scripts. These bytes were retained rather
than rewriting historical evidence. They do not change the measured runtime
results above.

No Linux/NixOS install, CUDA generation, complete song remix/render, provider
call, browser integration, Resolve/FL Studio session, service migration, hosted
deployment, playback/listening or creative acceptance was performed. Video
Studio's AVFoundation renderer is macOS-specific. The separate native editor is
a bounded P0 foundation with 73 planned capability families. Passing these tests
does not establish a general workstation renderer or Resolve feature parity.

The original Mac checkout intentionally still reports its original 20 tracked
modifications and untracked files. Their reviewed source copies are published;
the Mac remains on its original base commit to preserve the active worker and
other tasks. Unpublished production artifacts, media, private receipts, caches,
credentials and transcripts stay on the Mac. Do not pull through that dirty
checkout or start duplicate queue consumers during workstation setup.
