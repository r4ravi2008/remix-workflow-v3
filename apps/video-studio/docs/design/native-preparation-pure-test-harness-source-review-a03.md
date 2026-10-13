# Native preparation pure-test harness A03 source review

## Result

The A03 direct harness is source-ready for the planned fixed-archive build.
I found no P1 or P2 source defect in the requested scope.

The source removes only the five A02 `#[test]` attributes. It adds one
explicit `main` that runs the same five bodies in order. The planned
`-C panic=abort` command matches the fixed dependency archives that rejected
the earlier libtest harness.

This was a same-model, nonblind peer review. I knew the preserved A02 build
failure and the requested repair. I did not compile, link, import, or execute
the harness, library, tests, helper, native code, or media code.

## Reviewed package

The frozen package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/pure-test-harness-a03`

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `pure-test-harness-a03.rs` | 5,745 | `9f4388e0451c934a55390d2d1af3d72a5ebb616ebda0152a5a094636d19f8ae8` |
| `pure-test-harness-contract-a03.md` | 3,475 | `50c132ddd96f309dd8b5d724fc2cca58b0f15eb49e8f720f6e47a6cc7e1de0b4` |
| `source-manifest-a03.json` | 2,399 | `97f88f2bb390b37d1c336d4d56e84b99c8b5d91f3ce8e04e7bf4206bc395b80a` |

The manifest's two file rows match the source and contract bytes above.

## Predecessor and library bindings

The A02 predecessor source is 5,097 bytes with SHA-256
`87e461193a3799562bc2f235fcfdfba155abfdbc92de5e0e4d044f3466c02b3d`.
The complete A02-to-A03 source diff contains only these changes:

- remove five `#[test]` attributes;
- add the explicit ordered `main` function;
- print one passed line after each successful body;
- print `passed total=5` after all bodies return.

The five function bodies, imports, fixed unit path, and external crate alias
remain unchanged.

The A04 source manifest matches SHA-256
`25e65b31679d6bb05d02249bed14595971367449f0b7a795480803abb41b9b5d`.
The preserved A04 rlib is 4,262,496 bytes with SHA-256
`42723d0bc95379d69986bf621accbf62c27d51fff6ca69e4610be8c94b6605bb`.
Its preserved build report is 8,435 bytes with SHA-256
`c53bc7e4c5038772391940a1150d3332c06c935f8ae003585a7b69bb55274ba6`.

The A04 library exports every module and item referenced by the unchanged
A02 bodies. The prior A02 build reached the panic-strategy compatibility
check against these archives. It did not report an unresolved harness import
or type error.

## Panic strategy repair

The preserved A02 stderr is 1,743 bytes with SHA-256
`03f50aad8412373dbcc39dcf24ec61314f09595f469ff3b370a04902dd51a71a`.
It reports 14 dependencies built with panic strategy `abort` while the
libtest harness used `unwind`.

The A03 contract removes `--test` and passes `-C panic=abort` to a normal
binary build. Assertions and `expect` failures therefore terminate before
the corresponding passed line. A successful run must return zero and contain
the six fixed output lines in the declared order.

## Control coverage retained

The direct entry point retains all five A02 control bodies:

1. It checks saved expansion counts 153, 339, and 89.
2. It checks encoded row counts 154, 341, and 90.
3. It checks baseline, closure, log, binary, role, and path mutations.
4. It checks all observer branches, including normal pixel failure.
5. It checks combined summaries and unavailable pinned acceptance.

The first four controls read the same fixed reports through the A04
held-root reader. The fifth control requires both acceptance entry points to
remain unavailable without a pinned trust root.

## Evidence boundary

The A03 harness remains source-only. The successful A04 rlib does not prove
that this new binary compiles or runs. A later operation must preserve the
exact build command, input identities, binary identity, stdout, stderr, exit
status, and six-line output check.

This review establishes no accepted authority, loaded-code identity, native
execution, media execution, GPU execution, watched review, heard review, or
creative acceptance.
