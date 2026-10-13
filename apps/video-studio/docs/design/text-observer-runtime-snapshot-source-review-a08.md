# Observer runtime snapshot A08 source review

Status: source-only independent review. The A08 helper, attempt, and report
have not run. No import, compiler, native framework, media, GPU, Resolve, or
control process ran.

## Reviewed identities

| File | SHA-256 | Size |
| --- | --- | ---: |
| `freeze_observer_runtime_a08.py` | `a8b7a2466ad4d46ecbd69e2ad6827142716d00b615fc867bddadfcee671f0d2f` | 1006 lines, 39611 bytes |
| `observer-runtime-snapshot-contract-a08.md` | `b26b2fdb88ef648fcf4ae1fcc7927dab8b887b9e28bb7ab7d9a60ee628b08a55` | 312 lines, 11384 bytes |
| `observer-runtime-snapshot-rationale-a08.md` | `49c3eb26a4dc5266a3150a5da0341b9182d4f441e987c93f78ce71227ea9e1e9` | 86 lines, 4906 bytes |
| A07 to A08 source patch | `d020471a461953be5d5f41ad674140f80bcf21dbd8a921e3003a0272e60d4baf` | 44 lines, 2263 bytes |
| A07 to A08 contract patch | `031c04ffdbdd26da6cabb892e626b2764642de99a582f7f5f5a7cec717049129` | 69 lines, 4340 bytes |
| A07 to A08 rationale patch | `db4166583d5fd185d5b4e5be24a4c94a0c086fc2ee4fb9beae59764abf60c79c` | 59 lines, 4015 bytes |
| Preserved A07 review | `88457e71de10a532a13956f84ce0bac7b6aa6bfaf488b2ca9908055088660747` | 58 lines, 2961 bytes |

## Result

No P1 or P2 finding remains. A08 is a narrow, source-consistent successor to
A07.

## Verified delta

The source changes only the helper namespace and the strict Pillow metadata
name. It now binds:

- `freeze_observer_runtime_a08.py`;
- `observer-runtime-snapshot-attempt-a08/`;
- `runtime-snapshot-a08.json`; and
- package metadata `Name: pillow`, with no case folding or normalization.

The contract and rationale state the same lowercase metadata requirement. The
source checks `headers.get("Name") == spec["metadataName"]` before accepting
the package metadata. NumPy remains bound to lowercase `numpy`.

The fresh-attempt rule remains exclusive. An existing A08 attempt rejects
before report creation. The report keeps schema 3, the one-entry allowlist,
held-descriptor reread, parent confinement guard, cumulative capture bound,
and all A07 logical caps.

## Preserved boundaries

- Descriptor-relative RECORD traversal still uses no-follow directory opens.
- The just-opened parent descriptor remains guarded through endpoint checks.
- Every installed file retains before, during, and after identity checks.
- The report excludes loaded-image identity, standard-library closure,
  dynamic-library closure, runner/comparator execution, native text execution,
  and authorization.
- The report remains unqualified until a later operation binds its actual
  bytes and independently rereads the filesystem domain.

## Review limit

The A08 report is absent, so this review establishes source and contract
consistency only. It does not establish the current Pillow header, package
bytes, runtime report, loaded images, or execution qualification. A later
runner must bind the successful A08 report and its exact source variant.
