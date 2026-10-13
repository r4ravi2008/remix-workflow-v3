# Native RoleIndexV2 launcher A01 independent source review

## Disposition

This is a read-only review of the frozen three-mode launcher. I found five P2
findings. The source needs a successor before the build, vector, or decoder
control attempts run.

No launcher, helper, compiler, Rust binary, vector, decoder, control, native,
media, GPU, or Resolve process ran during this review. No attempt, build
readback, vector readback, runtime-closure marker, or source-review marker was
created.

This review is same-family and nonblind. I authored the independent decoder
control package. The package remains a separate source and expected-model
authority, but it is not independent-source-origin evidence.

## Reviewed identities

| File | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `native-role-index-v2-launcher-a01/run_role_index_v2_pipeline_a01.py` | 1383 | 61039 | `f238c02a6e8efc6543b575d578a1d22c8a83d3352dd26f76c4438aec4ad6614d` |
| `native-role-index-v2-launcher-a01/launcher-contract-a01.md` | 321 | 10751 | `bcc8f52f30ddb1bf8f83342f524134539783d133235487824ab367eaf8bcacac` |
| `native-role-index-v2-launcher-a01/source-package-manifest-a01.json` | 1 | 640 | `cc2c0e159149970c05954e74770a3c5bb7f0b85600bb0f2871ff31abeec76353` |
| `native-role-index-v2-launcher-a01/source-rationale-a01.md` | 102 | 4608 | `d9c5c6e844b8b9eef7629fb6c1fe2fda36fa8d2478f79686b6da3aeb05609b83` |

The parent source review is
`apps/video-studio/docs/design/role-index-launcher-parent-review-a01.md`,
SHA-256 `902e85a96b5627bc4d06d820a1b74732dd4a9c8f1e53f48ced09538fbc8dd982`.
The fixed decoder contract is 6,727 bytes, SHA-256
`3c18bc4766fb82791f11dfdf59da24949c92c34f266d3c2c4107193bfcc8f7d3`.
The fixed 74-result schedule is 10,186 bytes, SHA-256
`dab5e7edb0c8fd3373a83b0287834212aa94baebf132367a8266a56b21eb255a`.

## Checks that passed

The source preserves the intended build, vector, and decoder-control order.
Each mode creates a private attempt directory and binds the fixed source,
reviews, interpreter, toolchain, and future readback inputs before launch.

The descriptor helpers use no-follow opens, bounded reads, stable descriptor
identity checks, pathname checks, and create-new publication. The build path
reobserves its compiler and SDK inputs. The vector path checks the binary
between the two commands and after fixture encoding. The decoder path reopens
the vector, control package, runtime closure, interpreter, and report inputs.

The process record separates launch, direct-child reaping, retained-pipe,
timeout, termination, and capture fields. The contract correctly limits only
retained logs and explicitly denies RSS, filesystem-cache, descendant-reaping,
loaded-image, atomic-launch, native, media, gate, and acceptance authority.

## Findings

### P2: decoder success validation accepts a reduced report projection

`validate_decoder_control_report` at source lines 1231–1242 checks only the
schema value, passing state, result count, result-schedule digest, three scope
flags plus `externalIsolatedLauncherRequired`, and vector row count plus hash.
It does not require the exact success-report keys or validate their types.

It does not compare any result identifier, ordinal, category, expectation,
status, rejection code, or result-specific evidence against the frozen
74-result schedule. It also omits the decoder, fixture, input, publication,
actual-model, and expected-model identities from the check. A count-preserving
table with duplicated or altered results could therefore pass the launcher.

The control contract closes identifiers, categories, expectations, rejection
codes, and ordinals. The control source publishes those fields and separate
actual and expected model identities. The launcher should require the exact
top-level and nested keys, strict scalar types, every scheduled row in order,
all expected error/status fields, model/input identities, and the complete
false-authority scope. It should retain the current no-authority semantics.

### P2: abnormal process evidence is lost before failure publication

`run_bounded` builds a detailed process record at lines 644–668. The caller
passes that record to `process_success` at the build, vector, and decoder
stages. When `process_success` raises, `run_bounded` has already returned, but
`main` passes only the exception, mode, constant `dispatch` stage, and attempt
path to `failure_model`.

When log publication raises in the `finally` block at lines 785–787,
`run_bounded` does not return its record at all. The failure model then retains
only best-effort `lstat` observations for selected output paths. It loses the
launch, capture, timeout, termination, retained-pipe, direct-reap, and partial
log facts. An unexpected exception also records `dispatch` instead of the
current handler stage because the handler-local `stage` is not returned to
`main`.

The contract requires causal stage and partial-output identities and keeps
storage failure non-transactional. A source successor should retain each
completed process record and current stage in caller-owned progress before
success validation and log publication. The failure writer should include that
bounded record and the observed partial logs when available. It must still
allow publication failure without claiming durable failure evidence.

### P2: exceptional cleanup can skip the process group

The capture exception path at lines 746–752 sends TERM and KILL only when
`process.poll() is None`. If the direct leader has exited while a descendant
still holds a pipe, the exception path skips process-group cleanup. A
`BaseException` does not enter this `except Exception` block at all. The
`finally` path closes selector streams and waits for the direct child, but a
dead leader gives it no opportunity to signal the still-existing group.

The process contract requires bounded TERM then KILL handling for capture
failure and retained pipes. The successor should attempt process-group cleanup
for every post-launch abnormal exit, including a leader that already exited,
then perform bounded direct-child waiting. It must keep descendant reaping
unattested and separate from direct-child reaping.

### P2: Mach-O hash and UUID observations are not joined

`observe_macho` first calls `observe_regular` at lines 580–584. It then calls
`macho_uuid`, which opens the pathname again and parses the UUID at lines
546–578. The second descriptor proves its own stability, but the source never
joins its identity to the first descriptor or to the retained hashed bytes.

A replacement between those opens can produce one returned artifact containing
the first file's bytes, size, and SHA-256 with the second file's UUID. This
violates the binary tuple used by build readback and later vector checks. Parse
the Mach-O header and UUID from the retained bytes used for hashing, or compare
the complete descriptor identities from both observations before returning.
This repair must not add loaded-image or atomic-launch claims.

### P2: the two vector commands reuse one temporary directory

`vector_mode` creates `attempt/tmp` once at lines 1071–1072 and constructs one
environment at line 1110. It passes that same environment and `TMPDIR` to both
the Rust controls command and the fixture command at lines 1119–1141. Their
command receipts also record the same directory.

The contract explicitly requires each command to receive a fresh `TMPDIR`.
Reuse can leave one command's temporary files visible to the next command and
does not match the recorded command contract. Allocate two exclusive private
directories, construct one environment per command, and record each exact
value before its process starts. This does not require a new process model.

## Review limits

The findings are static observations from the frozen source and contract.
They do not establish that any failure path will occur in a future run. No
compiler compatibility, child behavior, vector bytes, decoder equality,
filesystem durability, loaded image, native framework, or product behavior
was tested. A later source successor needs a fresh review before any launcher
attempt is authorized.
