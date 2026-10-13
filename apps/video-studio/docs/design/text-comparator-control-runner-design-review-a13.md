# Comparator control runner A13 independent review

## Disposition

The frozen A13 additive contract and canonical vectors are internally
consistent. The closure-order erratum closes the one P2 documentation defect
found during review. I found no remaining P1 or P2 in this bounded design and
data unit.

This disposition permits source authoring for the runner and shared digest
module. It does not authorize a child launch or accept a runner result. The
writer, validator, capture path, publication path, controls, and parent readback
remain unimplemented and unexecuted.

The review is same-model-family and not blind. It used shared task history.
The byte reconstruction was independent and did not import the A13 recipe or a
future target module.

## Reviewed identities

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| A13 additive contract | 10,963 | `f09b1ae8a8cc9dbbdf2166c386901e70a5d0d75166050cfb5602ebea61dd0603` |
| A13 closure-order erratum | 9,707 | `cc6271f8804d3596bf8c9e533a519bd3e6614885ec41b971ccc4aff670e71aaf` |
| A13 vector recipe | 15,468 | `ae51933516a2651005e379337c46232848683c6d2a3b06a2b1ac3249d8540dad` |
| A13 vector artifact | 11,427 | `4aaa1cd4d83bd0714f509fb48edb08da2ba52f7887527040a7ee829d6dee73e2` |
| A13 ordered closure | 34,195 | `7131ee06d72c255442ee30f6e00f6d9ea93c13f28bd929883af398256c3f25a9` |
| Parent independent vector manifest | 5,896 | `228cad7f0c0c216e567aca44e463dc340f449a74eaf8509c3945721e8823d0d1` |

I rehashed every A13 input above from its current bytes. I also reopened all
60 closure rows. Every row matched its saved SHA, byte count, and eight
filesystem identity fields.

The closure has 60 unique paths and 7,504,476 total bytes. I found no aliases,
missing rows, duplicate paths, or changed identities.

## Independent vector reconstruction

I reconstructed the complete A11 row, overlay, and domain grammar. I applied
only the A12 symlink correction. The reconstruction produced these exact
binary facets:

| Facet | Bytes | SHA-256 |
| --- | ---: | --- |
| rows-empty | 33 | `1b47012a24817833a73829cecb438cb29787c2452ba19c87ee4bdf9845b0c8b2` |
| rows-one | 189 | `7b27483354433c3d22bdaeb23a73481d50f15bc10a4537c4455295fcc1d4d70e` |
| overlay-one | 132 | `6a943b3833cde33e4954211700ac5927f85c3635504d81887c222f399e1d63cc` |
| domain-one | 1,310 | `109fa9ae6a211c734b19ad5c5ee40335fe58e72f929b3a5a40486696b094f527` |

Every byte matches the A13 artifact and the independently frozen parent
manifest. The 189-byte row result follows the complete A11 grammar. The old
188-byte A11 declaration is retained only as a discrepancy. It is not a target
expectation. The old A11 domain hash remains retired.

I also reconstructed both A13 canonical JSON vectors:

| Vector | Bytes | SHA-256 |
| --- | ---: | --- |
| basic | 34 | `75a5e1754766234964e2cc913129d7dbdc36e806b6e4346fc2412794490e74ca` |
| escapes-and-unicode | 79 | `e28bf60301be509c89f976fb14319791a4c32d436fe837b7b7befe9da8a23950` |

The parent manifest splits its additional JSON coverage into separate
55-byte escape and 37-byte UTF-8-key vectors. A13 instead uses one 79-byte
combined vector. The five vectors shared by both artifacts are byte-identical.
The A13 combined vector also reproduces independently from its published value.

The A13 rejection table covers duplicate keys, floats, non-finite values, NUL
strings, surrogate scalars, and invalid UTF-8. These are expectations for
future controls. No target writer or rejection control ran in this review.

## Wire and package authority

A13 binds the full A11 grammar by exact SHA. It gives one explicit override for
the A12 symlink fields. It does not allow A12 summary prose to redefine the
wire.

The package values are exact source values:

```text
DistributionKey = "pillow" | "numpy"
OverlayPackage = "pillow-12.3.0.dist-info" | "numpy-2.3.5.dist-info"
```

The row order is Pillow followed by NumPy. The overlay keeps its saved 45-row
order. Display labels remain outside the digest. This closes the earlier
package-key ambiguity without normalizing source evidence.

## Cap ownership

The A13 ledger assigns each finite limit to one owner:

1. authority scan;
2. report and overlay binding;
3. request and preflight;
4. child capture;
5. child result;
6. publication; and
7. parent readback.

Each owner has a named evidence set. The scan ledger includes file, package,
read, open, row, and path limits. Capture owns timing, stream prefixes, signals,
pipe residue, and cleanup. Publication owns file identities, partial prefixes,
the allowlist, and the aggregate total.

Phase counters remain outside the phase-independent digest. Each phase still
retains and validates its own counters. Parent readback compares each ledger
against the same cap without requiring equal totals. This is a complete
design-level ownership assignment. Implementation controls remain required.

## Closure-order erratum

The original A13 numbered blocks describe 58 rows. The saved closure contains
60 rows. The additive erratum now records the exact 60-row order.

The erratum correctly includes these formerly unclear positions:

- row 6: A03 scoped acceptance review;
- row 13: historical A09 parent preflight; and
- row 18: A03 reader tool result.

I compared every erratum path with the closure entry at the same index. All 60
paths match. Rows 20 through 35 preserve the A14 manifest order. Rows 36
through 57 preserve the A15 manifest order.

The erratum does not rewrite the original closure. It binds the original
contract and closure hashes. This preserves the frozen snapshot.

The current closure is a preimplementation expectation. It excludes the
future runner, shared module, this erratum, authorization, and runtime output.
Before authorization, a later source closure must add the reviewed runner,
shared-module rows, and this erratum. It must bind the current closure by its
original SHA. This rule avoids a self-hash cycle and prevents a silent source
upgrade.

## A03 evidence scope

The repaired A03 records establish a completed filesystem readback. The saved
execution contains 1,548 installed rows and 45 fixed divergences. It contains
995 strict declared matches and 508 independently observed undeclared rows.

The evidence remains unqualified. It keeps execution authorization,
comparator execution, native execution, loaded-image attestation, and creative
acceptance false. It does not establish package import, provider origin,
playback, watching, or hearing.

## Remaining gates

The next unit may author the runner and shared digest module against this
contract. Before any external authorization or child launch, it must:

1. reproduce every frozen vector byte, length, and SHA;
2. pass every rejection and single-field mutation control;
3. bind its exact source rows and the A13 erratum in a new source closure;
4. receive independent source review;
5. prove bounded capture, cancellation, failure, and publication controls; and
6. preserve parent readback as a separate final phase.

No runner, comparator control, compiler, child, native process, decoder, media
process, GPU process, or Resolve operation ran for this review. No playback,
listening, watching, or creative acceptance follows from this disposition.
