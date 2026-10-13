# Comparator control source peer review A06

## Scope and identities

This is a read-only, same-family review of the frozen A06 source package. I
read the complete source, contract, fixture, manifest, and adjacent erratum.

| artifact | bytes | SHA-256 |
| --- | ---: | --- |
| `control_comparator_runner_a06.py` | 15,009 | `a884be3aa1f00e0d641267112919f900cdff05c5e9f131827d51fbc0fc65032b` |
| `control-contract-a06.md` | 3,807 | `e382addc06f33b10d88baa703356f1b7ff06ded927e4e0347ab4243f0a96b991` |
| `control-fixture-a06.json` | 3,369 | `1ddb1f87b1c3fdc6a4588fe30f8f1e77b76dbc5a6ffd2d62118ae04f6747bd46` |
| `source-package-manifest-a06.json` | 7,051 | `25bc370b77e82c6d361f8c44c37482716d5f15148c4dda4c5ba2600426589d17` |
| `source-package-manifest-a06-erratum-a01.md` | 1,790 | `e4b3327b59a09472c069975a59ae5287af07d2cd543e595e9a624066dc106848` |

The frozen manifest declares 18 rows, 401,073 bytes, and aggregate SHA-256
`68ab4a59344c2521fdb613e00220dd5e90d22619dbdb2d7fb01c22e4deaa914e`. All 18
declared file and input rows matched their current byte counts and hashes.

The erratum correctly separates the historical A05 design review from failed
attempt authority. It binds the actual parent readback at
`apps/video-studio/docs/design/text-comparator-control-runner-control-parent-readback-a05.md`,
1,338 bytes, SHA-256
`9e3dab768515c0146a2185c4862e335db675e8ea73997b29a798608a9f04a204`.

## Repair trace

The fixture's repair set contains exactly these two names:

- `required-evidence-extra`;
- `actual-comparator-extra`.

`install_allowlist_expectation_repair` intercepts only the A03
`allowlist_controls` expectation callback. For each matching name it requires
the historical expected code `typed_equality_value`, records the case, and
passes `typed_equality_length` to the unchanged `Results.runner_rejection`.
It requires exactly two corrected callbacks and the exact fixture case set.
No production runner validator is modified.

The unchanged A03 allowlist function still supplies the reordered and duplicate
cases. `validate_repaired_result` requires both reordered rows to retain
`typed_equality_value`, both duplicate rows to retain `allowlist_duplicate`,
and both repaired rows to be accepted with `typed_equality_length`. The A03
inventory controls still exercise the pre-seal final-use length branch through
the original suite.

`run_complete_a05_with_expectation_repair` loads the measured A05 source,
then the measured A04 supplement, then exactly one measured A03 predecessor.
The A04 loader binds the fixed A03 source and installs the repair before the
A03 suite starts. The A06 load counters require one A04 and one repaired A03
load. A05 then runs its complete A03 and A04 suites and its overlay controls.

The result checks retain the A03 state, the A04 state, the A03 canonical digest,
the complete A05 report, and the accepted two-domain seal row with integer byte
count and string SHA-256. The returned A06 object retains the full A05 report,
its canonical receipt, and `twoFullDomainsSealResult`.

## Boundary checks

The fixture and every predecessor source are read with bounded, no-follow file
descriptors. The failed report and stderr are retained and checked for the
observed `typed_equality_length` code and `required-evidence-extra` case.
The combined report has a 4 MiB logical cap. The source records all real-child,
subprocess, authorization, publication, native, media, GPU, Resolve, playback,
watch, hearing, and creative flags as false.

The A06 source imports no runner or child during authoring. Its later planned
invocation is fixed, argument-free, and isolated. The controls call fake
capture backends inherited from A03 and A04, so they do not establish real
process or native evidence.

## Findings

No P1 or P2 finding remains in the frozen A06 source for the requested scope.
The two expected-code changes are closed over the fixture's exact two names.
Predecessor suites, validators, complete result reports, and the seal facts are
retained through explicit source paths and report joins.

The frozen manifest's historical parent-review row remains incorrect by design
of the preserved manifest. The adjacent erratum supplies the required external
closure rule and the actual parent readback. Future authorization must bind the
erratum and readback separately; this does not require changing the frozen A06
source or manifest.

## Review limits

This review establishes source and byte-identity consistency only. No Python
module was imported. No control, runner, helper, child, compiler, native,
media, GPU, or Resolve process ran. No source execution or no-child result is
accepted by this review.
