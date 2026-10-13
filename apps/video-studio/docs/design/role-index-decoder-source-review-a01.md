# Independent RoleIndexV2 decoder A01 source review

## Disposition

The frozen decoder source, wire contract, and rationale have no P1 or P2 findings.
This is a source-only review. The decoder was not imported or executed.

The reviewed files are:

| File | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/independent-role-index-decoder-a01/decode_role_index_v2_a01.py` | 781 | 23381 | `57fca7995ee886561ad7152f549c92aafd6839c84beeec63a59487527e59581` |
| `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/independent-role-index-decoder-a01/wire-contract-a01.md` | 268 | 7192 | `679df5d0e6dcd3997c7b4a582ca8b6fa7a4ca9504baf217d8e5f98c182650b31` |
| `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/independent-role-index-decoder-a01/source-rationale-a01.md` | 111 | 4131 | `091c8528a88d6d1728aa04b16a6d695fb4cf31781de33eee09ae8b11ac2cbf28` |

The source was compared with the frozen A06 design
`260e83d2b5fb8474b3ef04801b5f28f764ee08e4e94ea648352679cedc2b6eb5` and A07 design
`d5fce8f6f0b4111de6ed4b3c28ba9701dcacf12af80474a55bf86b62b0fb3b46`.

## Checked contract

- The decoder reads the exact NUL-terminated magic, schema `2`, row count, raw-role
  ordering, seven observation tags, and declaration-order payloads.
- All nested tags are literal and closed. Zero and unknown observation, scalar,
  directory-authority, directory-identity, alias, and option tags fail.
- Fixed-width scalar values enforce lengths and big-endian signedness. UTF-8 rejects
  invalid bytes and NUL. Absolute and relative path rules match A06. Role, path,
  scalar, list, dependency, row, and aggregate limits are checked before each copy
  or loop.
- Stable identities use the six declared fields. Regular files and symlinks enforce
  their mode bits and size equalities. Directory variants enforce directory mode.
  Mach-O option payloads preserve the declared four integers and 16-byte UUID.
- `PathnameOnly` requires all four directory options absent. The held mode requires
  all four present. Optional values remain distinct from absent values.
- References are parsed independently of row order. The final map rejects missing
  roles, rejects symlink targets outside regular-file and directory-authority rows,
  and runs a bounded Kahn traversal over symlink, list, alias, and derived edges.
  Repeated list or dependency references remain separate edges. A derived vector
  accepts up to 4,096 entries, so it does not truncate the required over-64 case.
- The decoder rejects truncation and trailing bytes, requires strictly increasing
  raw role bytes, and returns no decoded model on failure. The 4 MiB input limit is
  enforced before parsing, and the complete input hash is computed only on success.

The decoder does not validate filesystem state, recompute adapter-specific aliases
or derived booleans, enforce adapter row cardinalities, or create trust authority.
Those are the correct later loader and adapter boundaries in A06/A07.

## Remaining qualification boundary

No canonical vector, cross-implementation comparison, negative matrix, compiler,
filesystem observation, native process, media process, GPU process, or Resolve process
was run. A later control must bind one complete vector, its byte count, and SHA-256,
exercise every nested tag and option, include empty and nonempty lists, include more
than 64 dependencies, and run the stated malformed-input matrix.

The 4 MiB check bounds encoded input only. It does not establish Python object,
allocator, or process-RSS bounds. The decoder therefore remains a structural parser,
not an accepted loader or trust root.
