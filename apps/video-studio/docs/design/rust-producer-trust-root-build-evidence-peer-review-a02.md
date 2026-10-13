# Rust producer trust-root A02 build evidence peer review

## Scope and method

This review covers the saved A02 trust-root build and fixture-control attempt.
It does not import the package, recompile it, rerun controls, or start native,
media, GPU, Resolve, or product work.

The reviewed roots are:

- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-trust-root-a02`
- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-trust-root-build-attempt-a02`
- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-trust-root-control-attempt-a02`

I reopened the saved regular files and used `lstat` for recorded paths. I
checked recorded content hashes, byte counts, and the nine identity fields in
each input and output row: `bytes`, `mtimeNs`, `ctimeNs`, `device`, `inode`,
`mode`, `links`, `uid`, and `gid`.

## Source package binding

The A02 source package manifest is 15,734 bytes with SHA-256
`f6f18d6d79c5d579aab937572bc60435faaf5b8a6769b5ef5217f03d59b602b9`.
All 36 manifest rows match their current package files. The declared source
aggregate recomputes to
`fe7a9b7fadad0bc9296d62573e807419c6ef4a74b2b8f9844f636c1b20652234` using
the published ASCII domain, one NUL terminator, ascending raw UTF-8 path
ordering, and the published framed row encoding without count or byte-total
prefixes.

The package remains source-only as a package artifact. The separate attempt
records its later direct build and fixture-control execution.

## Frozen recipe and command result

`preflight.json` is 80,001 bytes with SHA-256
`be5ceaa347692a0b2682f359aecf37653a28d4da8886c471e24dfbd99b164951`.
It records 125 input rows totaling 75,172,991 bytes, a 60-second limit, a
4 MiB captured-stream limit, `sourceControlOnly=true`,
`productionPinPresent=false`, and `nativeProducerAllowed=false`.

The three preflight command vectors, working directory, and environment equal
the frozen `direct-build-recipe-a02.json`. The three saved report command
vectors also equal the frozen recipe. The recipe uses the observed arm64
Rust compiler, fixed dependency roots, and the direct `libc`, `serde`,
`serde_json`, and `sha2` archives.

`report.json` is 161,536 bytes with SHA-256
`01bcbd029beefac35de491f35d9dfaff3c5497cf3a1c1bc5d5d05f2aace0d30e`.
It truthfully records:

- state `source_controls_passed_pending_independent_readback`;
- `compiled=true`, `executed=true`, and `controlsPassed=true`;
- library, harness, and controls return code `0`;
- all three processes reaped;
- no timeout, captured-stream overflow, or unclosed stream;
- three generated outputs;
- an empty temporary-entry list;
- false production-pin, accepted-production-value, authorization, native,
  product, watched, heard, and creative fields.

The saved attempt directory contains the expected logs, reports, library,
and control executable. Its owned `tmp` directory is empty.

## Generated outputs and process readback

The generated library is 3,982,136 bytes with SHA-256
`ccca8ebab868af48c7370bb905ed7b28742f69ebcdcf8439459c93a919774539`.

The arm64 control executable is 1,678,104 bytes with SHA-256
`3cd845fc2a42cb3b80fac049555310e2822887e097a18356e1942685292f0834`.
The saved Mach-O observation records CPU type `16777228`, file type `2`, and
UUID `2b8278adc06f3d168a38ab1d792885f5`.

The three command PIDs were absent at the saved parent readback. The parent
readback is 86,828 bytes with SHA-256
`64e9139580d1d3d9531d564ead9fe8295259c893e36b53ac20510b9b89705caa`.
It preserves the three output rows, six log rows, process absence rows, and
the report and preflight identities.

The library emitted two dead-code warnings for the private `Accepted` value
and its unused extraction method. Harness and control stderr were empty. All
six saved stream rows matched their current identities and hashes.

## 125-input readback

The preflight input rows equal `report.inputsBefore` exactly. The report
contains 125 rows in both `inputsBefore` and `inputsAfter`, with exact array
equality and total bytes `75,172,991`.

Every before and after row points to a current regular file. All 250 rows
matched current nine-field identities, byte counts, and SHA-256 values. The
parent readback also reports exact input equality. No input changed during
the build or control run.

All three generated output rows matched their current regular-file identities,
byte counts, and SHA-256 values. The six compiler and control log rows also
matched their current identities and hashes.

## Fixture-control result

`source-control-report-a02.json` is 3,634 bytes with SHA-256
`99c509fbd4ad407f5a277e1f0319fd41ea22fa7897357bf40bb3f01f38455652`.
It records schema 1, state `source_controls_passed_no_production_pin`, and
27 passed results out of 27.

The swapped-review mutation returned `trust_entry_join`. The acceptance-cycle
mutation returned `acceptance_reference_cycle`. All remaining expected
rejection and boundary codes also matched their recorded results.

The fixture controls use an in-memory artifact reader and synthetic records.
They verify parser, join, private-construction, and rejection behavior only.
They do not qualify real source, build, input, PNG-control, runner, or accepted
production subjects.

## Disposition and limits

The saved trust-root build and fixture-control evidence is internally
consistent and truthfully bounded. The production pin remains absent. The run
created no execution authorization and did not construct a production trust
value.

This evidence does not qualify a real Rust producer or runner, native
framework, media output, observer, comparator, Swift path, GPU, Resolve path,
product integration, watched result, heard result, or creative acceptance.
This review did not rerun or import any target code.
