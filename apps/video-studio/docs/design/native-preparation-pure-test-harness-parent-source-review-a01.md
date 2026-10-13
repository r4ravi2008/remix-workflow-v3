# Native preparation pure-test harness A01 — parent source review

Root read the complete 5,097-byte test source, 4,081-byte contract, and package
manifest. Both source bindings match their current bytes and SHA-256 values.
Root found no P1 or P2 within the five-test harness scope. Compilation and the
independent source review remain pending.

The source SHA-256 is
`5bb6d8072b2fec03bcd059b201a555885dd43b3b02275f31ca1092b4e9a7b84d`.
The contract SHA-256 is
`fea5ee7f770d6cc5187abdc0804eac5b88dc0b3968c806d12983179ed0204760`.
The manifest SHA-256 is
`beca58998b0983e70246fa42a11786808ef0fc467e3d8c20ad5703046c565f3a`.

The harness links the frozen A03 crate as an explicit external rlib. It uses
A03's held fixed-report reader. It does not copy the adapter implementation.
Its five tests check expansion and encoded authority counts, coherent baseline
mutations, fresh role and path mismatches, observer branches and normal pixel
failure, the combined entry point, and exact unavailable-acceptance errors.

Root checked the referenced public APIs and the encoder's
`structural_accounting.row_count` field. The parent will supply an explicit
harness crate name, exact measured rlib, existing fixed dependency paths, and
`--test-threads=1`. No Cargo resolution is needed.

The parent must seal the source manifests, fixed saved reports, compiler, and
dependency archives before either direct build. Each build and the test binary
will have separate saved argv, environment, status, log, and output receipts.
The test schedule must contain and pass all five named tests.

No compiler, test, native producer, media process, GPU generation, Resolve,
hearing, viewing, or creative acceptance occurred during this source review.
