# Native RoleIndexV2 A03 build evidence scope review

## Disposition

This is a read-only review of the completed A03 direct compiler evidence. The
evidence supports one successful compiler invocation and its recorded file
observations. It does not establish loaded-image, native, media, GPU, or
acceptance authority. I found no new P1 or P2 evidence finding.

I did not run or import the launcher, compiler, built binary, Rust controls,
vector encoder, decoder control, helper, native framework, or media process.

## Reviewed evidence identities

| Evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| `build-attempt-a03/build-report-a03.json` | 20,253 | `7841a47f632c645e7419becf20c7a5707a6be09426c4e8576602e1a0c3384c11` |
| `build-attempt-a03/build/native-role-index-v2-a02` | 577,496 | `f7c915c29410942e4983c9a320ea4129223051e175ecae41019ca4872c313314` |
| `build-root-launch-receipt-a03.json` | 19,789 | `7836549d76ea370261d546377202e9ba146d3081f34b038c0668c3de1efeabf5` |
| `build-root-postcheck-a03.json` | 24,423 | `efc83c3703c8a8c95d35e65fee56e414af0b4c9fe91b43d0fe6d8e18d4ea8401` |
| `build-root-tool-result-a03.json` | 325 | `95f027e9fcfc66611ca6dbc7c0f869fa05b445699510282a0ea2a417b770cccc` |
| `native-role-index-v2-build-parent-readback-a03.md` | 2,320 | `d9bac0f53b1ae65cd08e20eb0c75c8f7d553dd2a1e89b27fc06f58361c002539` |
| `build-parent-readback-a03.json` | 755 | `862f86df1dd3a6ffcc60fc92f64fac680762b44ec96a14f069ebd9862952ba34` |

The launcher source-review marker bound by the pre-launch receipt is
`source-review-a03.json`, SHA-256
`d80472cfd563c950d74adfa3666202d841ea33e14dad138d5fa08fbde97953da`.

## Pre-launch authority boundary

The external receipt state is
`root_external_receipt_before_one_role_index_launcher_a03_build`. It records
the fixed Python path with `-I -B`, the A03 launcher path, the `build` mode,
and the repository working directory.

The receipt records the fresh build attempt as absent before launch. It binds
40 source, review, interpreter, toolchain, and SDK rows. It also records 24
encoder file-backed bindings and the compiler-only scope. The receipt states
that encoder commands, vector execution, decoder controls, loaded-image
attestation, native authority, and gate authority are false.

The parent review records that this receipt was fsynced before launch. The
review also records the fixed ten-key compiler environment and exact compiler
arguments. The launcher report independently retains the same command receipt.

## Compiler result and file evidence

The launcher report state is
`role_index_v2_launcher_a03_direct_build_complete_encoder_commands_unexecuted`.
The direct child returned zero and was reaped. The process record reports no
timeout, output overflow, retained pipes, capture error, or termination.
Both separately published compiler logs contain zero bytes.

The produced file is a thin arm64 Mach-O executable. Its tuple is:

- 577,496 bytes;
- SHA-256 `f7c915c29410942e4983c9a320ea4129223051e175ecae41019ca4872c313314`;
- UUID `e47ea81d6a5e34d5a6a71ea351faedb8`.

The report marks `machoParsedFromObservedBytes=true` and gives equal
`rawBytesSha256` and `sha256` values. The parent review states that root parsed
the UUID from the same retained bytes used for hashing.

## Independent root postcheck and readback

The root postcheck state is
`root_role_index_a03_compiler_postcheck_passed_encoder_commands_unexecuted`.
It reports 50 unique regular files and 19,634,381 regular bytes read. It
reports 24 encoder bindings and the same Mach-O UUID from hashed bytes.

The postcheck rebinds the report, outer receipt, tool result, source rows,
toolchain, compiler environment, binary, and published logs. The parent review
records comparison of all nine regular-file identity fields before and after.

The parent readback state is
`role_index_v2_build_a03_parent_readback_passed`. Its report descriptor matches
the build report exactly. Its scope has `evidenceReviewed=true`, while
`executionAuthorization`, `loadedImageAttestation`, `nativeAuthority`, and
`gateAuthority` are false.

## Scope and remaining limits

This evidence establishes recorded compiler completion against the observed
source, compiler, interpreter, SDK, and encoder closure. It does not attest
which executable image the kernel loaded, descriptor-atomic launch, linker
descendant reaping, child RSS, filesystem-cache behavior, or process-wide
memory use.

It does not establish that the binary runs its encoder commands. Rust controls,
vector encoding, and decoder controls remain unexecuted. Native text rendering,
media behavior, GPU behavior, Resolve behavior, watching, hearing, and creative
acceptance remain outside this evidence.

The parent readback is sufficient for the reviewed next-stage boundary. Any
vector or decoder stage still requires its own fresh execution evidence and
parent readback.
