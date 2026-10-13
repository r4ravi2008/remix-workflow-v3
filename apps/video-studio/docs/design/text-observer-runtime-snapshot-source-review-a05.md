# Observer runtime snapshot A05 source review

Status: source-only review. The helper and its output attempt remain
unexecuted. No import, compiler, native framework, media, GPU, Resolve, or
control process ran.

## Reviewed identities

| File | SHA-256 |
| --- | --- |
| `freeze_observer_runtime_a05.py` | `c3e520304944171dd40a76a5240ce5ccffafa662264267b3a3036e3bf14b745d` |
| `observer-runtime-snapshot-contract-a05.md` | `e812fbda0bc93098c173d63fc9bba3e577aa980844039ccb608bb65840406187` |
| `observer-runtime-snapshot-rationale-a05.md` | `c74cc237c931862ec05aaf6ddf1b9a21fc9de23e2d8c7e5c77991be79891cc10` |
| historical A03 closure | `8ca43d6b5f7340de7fcdbc22642239719f32e0201a957849d4a1d26474540c6e` |

The source has 772 lines and 31,088 bytes. The contract and rationale are
source-bound, unexecuted documents.

## Findings

### P2-1: RECORD parent components are not descriptor-confined

`open_held_directory` holds the unit, runtime, Python, and site-packages
descriptors. `record_path_to_absolute` then converts every RECORD row to an
absolute path using lexical normalization. `measure_regular` protects only
the final component with `O_NOFOLLOW` and compares its final pathname identity.

The intermediate components named by a RECORD row are still resolved through
the pathname. A replaced directory or a symlinked parent can therefore route a
declared file outside the held site-packages tree while its lexical
`runtimeRelativePath` remains under the Python root. The final pathname checks
do not detect a parent component that is replaced and restored between checks.

Before execution, either traverse every component with `openat` relative to the
held site-packages descriptor and `O_NOFOLLOW|O_DIRECTORY`, or validate the
complete parent descriptor chain before and after every file observation. Keep
the current final-file hash, size, and identity checks. This is a source
containment gap, not a claim that the current provider tree is malicious.

### P2-2: The successful attempt has no output allowlist or final report handle

The contract says that a fresh attempt contains exactly
`runtime-snapshot-a05.json`. The source creates that file exclusively, but it
never enumerates the attempt directory through `attempt_fd`. A same-user
writer could add another entry without changing the report or the recorded
input checks.

The source closes `output_fd` at line 745, checks the pathname once, and then
performs final directory checks. A replacement or write after that pathname
check can remain undetected until a later consumer read. Before execution,
enumerate the bounded attempt directory and require exactly the report name.
Retain or reopen the report through `attempt_fd` for the final identity and
bounded-byte check immediately before success. A later binding operation must
still hash and bind the report bytes.

### P2-3: The capture-bound wording omits some captured inputs

The source enforces one global `MAX_CAPTURED_INPUT_BYTES` value of 8 MiB. The
captured inputs include the runtime manifest, historical closure, both
distribution METADATA files, and both RECORD files. The contract describes the
8 MiB bound as applying to “metadata and historical JSON” and does not name
the runtime manifest or RECORD captures.

This does not permit an over-bound successful run because `Budget.capture`
rejects the cumulative total. Before execution, state that the 8 MiB cap
covers every `capture=True` observation, or add separate named reservations
for the manifest, metadata, RECORD, and historical captures.

## Verified source properties

The A05 source correctly preserves these boundaries:

- Runtime, Python, and site roots are opened with no-follow directory flags.
- Each regular file is hashed through one descriptor and checked before, after,
  and during the read.
- RECORD hashes and byte counts are compared with current observations.
- The current domain includes all declared regular files, including `.pyc`.
- Historical A03 hashes are used only for the path-set comparison.
- Pillow and NumPy remain absent from `sys.modules` before and after scanning.
- Report fragments are encoded and admitted before each bounded write.
- The fresh attempt and report use exclusive creation, and the attempt root
  receives an initial and final endpoint check.
- The report explicitly declines loaded-image, standard-library, native-load,
  process-memory, observer, comparator, and execution conclusions.

These checks support a useful source design. They do not close the two
descriptor/path containment and output-publication gaps above.

## Review limit

No runtime snapshot was produced. This review does not establish the current
Python, Pillow, or NumPy bytes, loaded-image identity, comparator behavior, or
any native text result. A later execution must bind the exact helper, contract,
runtime snapshot, output allowlist, and parent readback separately.
