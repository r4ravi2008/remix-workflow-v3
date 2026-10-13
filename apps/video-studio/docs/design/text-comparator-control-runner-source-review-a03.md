# Comparator control runner A03 — independent source review

## Scope and disposition

I read the complete A02-to-A03 runner delta, the A03 contract, wire schema,
rationale, manifest, and the currently staged no-child control files.

I used read-only file reads and hash checks. I did not import, compile, typecheck,
execute, launch a child, run a control, or invoke native, media, GPU, or Resolve code.

The five A03 runner rows match their declared bytes and SHA-256 values.
The selected A03 repairs are present. They introduce no new P1 or P2 in the
runner source. The runner remains source-only and unqualified.

## Frozen package identities

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `run_comparator_controls_a03.py` | 174446 | `f5a2b4c74d8a6658c3c1e299f41fbb44d59a78d7648dfeb686a183258819f95a` |
| `runner-contract-a03.md` | 11073 | `9e418a76c8ff10b5b652e59f7f07e5d6f005072fee23d87da4efbd0eecaac35b` |
| `output-schema-a03.md` | 4557 | `5c303d76d53c0bb6ee40835e5c9a3f93b53857d538b61e2ae6f546af2cb5fa45` |
| `source-rationale-a03.md` | 4054 | `4cb1c722835e18d233dcbf73e65c169c413426b01d0653200edd4446afdb1eb3` |
| `source-package-manifest-a03.json` | 4114 | `3168af7ddd7e43b36dc8962b0caa1583dbc2f8f8fd099e2eb12e38233f3f9054` |

The preserved A02 lower-bound record is `root-publication-cap-lower-bound-a02.json`.
Its SHA-256 is `536eca6006eed87acb15a9f807910f7e90f27c2aef56f324db38199c731fb1a8`.

## Confirmed A03 repairs

1. `PhaseObservation.publication` keeps full measured runtime domains. The
   A03 seal removes the full capture event array and uses `capture_summary`.
   The seal also carries the measured report entry as `captureReportReference`.
   `build_seal_value` requires that reference to equal the matching pre-seal entry.

2. `validate_source_closure` reads every additive role and retains its full
   descriptor receipt. It joins path, byte count, hash, nine identity fields,
   and four successful pathname or descriptor checks.

3. `validate_source_identity_joins` compares the closure, authorization, and
   later reads for the runner, codec, and source-package manifest. The comparison
   is recursive and type-sensitive.

4. Successful and failed paths validate the expected pre-seal inventory. Both
   paths validate the final inventory after writing the seal. A post-seal error
   becomes `post_seal_terminal_failure` and cannot enter failure publication.

5. Attempt setup tracks the raw child-directory descriptor before ownership
   transfer. Setup failure closes the raw or transferred descriptor and records
   whether the exclusive directory was observed empty. It preserves the directory.

6. Publisher and unit-directory cleanup run independently. A close error creates
   terminal failure without rewriting already published evidence.

7. The fixed child map, `-I -B` command, six-value environment, direct-child
   process-group capture, pipe limits, seven-name allowlist, and bounded waits
   remain unchanged. No generic caller-supplied launcher was introduced.

## Remaining evidence boundary

The seal still serializes complete `prelaunch` and `post_child` domains through
`PhaseObservation.publication`, including both 1,548-row arrays. The A02 source-only
projection measured 4,503,788 bytes for two row arrays plus 4,096 valid event objects.
Removing the event projection leaves 4,098,284 bytes before other seal fields.
The remaining 96,020 bytes must cover capture summary, entries, facets, receipts,
and seal metadata. Therefore the unchanged 4 MiB seal cap needs the planned maximum
capture control before the format can be accepted. `canonical_publication` rejects
an over-cap seal, so this open capacity item cannot create a false sealed result.

The runner does not attest loaded Python images, descendant reaping, native output,
media output, provider origin, watching, hearing, or creative acceptance. The
fixed external launch command and later independent parent readback remain required.

## Pending external control package

The manifest explicitly lists the A03 control source, contract, fixture, manifest,
reviews, source closure, and authorization as external rows pending. The current
staged control directory contains only these two unbound files:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `source-controls-a03/control_comparator_runner_a03.py` | 61395 | `00f29149ca7145b0d32772c91036e9ed6a34edb95922176b71969dae10e792e1` |
| `source-controls-a03/control-fixture-a03.json` | 23844 | `755db7475bc22b42564e43541c0cfbbcc497bddf234711b701e4c8e43178cab0` |

Those files are not part of the five-row A03 package manifest. The control source
still contains placeholder fixture byte and hash constants, and the fixture state
retains an A02 label. The A03 control contract and control manifest are absent.
This is an explicit pre-execution blocker for the independent control authority,
not a qualification claim about the runner repairs.

## Final disposition

The A03 runner source is internally consistent for the reviewed repair boundary.
The seal-cap maximum representation, external source closure and authorization,
independent controls, and parent readback remain open. No runtime, native, media,
GPU, Resolve, watched, heard, or creative result was established.
