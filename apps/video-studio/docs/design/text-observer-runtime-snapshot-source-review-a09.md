# Observer runtime snapshot A09 source review

Status: source-only independent review. The A09 helper, attempt, and report have
not run. No package import, comparator, control, compiler, native, media, GPU, or
Resolve process ran.

## Reviewed identities

| Artifact | SHA-256 | Size |
| --- | --- | ---: |
| `freeze_observer_runtime_a09.py` | `c2ac751a7acdc9327112fad719dab751ba844162b346ff78e296e3eba3783dc4` | 1,408 lines, 55,732 bytes |
| `observer-runtime-snapshot-contract-a09.md` | `bb03fddb685b5a935a2a5f789ed12bcfb42c9252e8395b85e9c6054418e1341a` | 385 lines, 14,189 bytes |
| `observer-runtime-snapshot-rationale-a09.md` | `01683726ff727636ac6ef28d1cf894036045cd5dcac8bc911949ea0eae815603` | 112 lines, 6,202 bytes |
| A08 to A09 source patch | `16b2125f50d7c01625efb6a15c3eddad2ddabb51063258b7e457ef2d8df7f007` | 536 lines, 22,544 bytes |
| A08 to A09 contract patch | `8c8a9fe54ea43420545ea22749870f759d44b260e18337a5b1c8710076c8ba62` | 198 lines, 9,064 bytes |
| A08 to A09 rationale patch | `12aac33ae2f7b16a945b0df8213e7a79d30a51cee80223cbb285c50c910996ab` | 93 lines, 5,589 bytes |
| `runtime-record-declaration-diagnostic-a01.json` | `094c49dc02a1933782dba58fb75eb838587b9a6e7ab357a7c45cf0c61e7405d2` | 1,379,634 bytes |
| `observer-runtime-record-divergence-overlay-a09.json` | `975e9dbb05e45718c363ebac762c868cd3c85bc952757c4d3aff017dce11b22a` | 25,945 bytes |
| A03 historical closure | `8ca43d6b5f7340de7fcdbc22642239719f32e0201a957849d4a1d26474540c6e` | source-bound by A09 |

I also read the preserved A08 source review (`918eff1a18d487b20384f8c30aada3bbee32e5785a56808da84a964aa0ccb846`), its parent review (`4bdb621ac71cf7d64a36724592fbd13cdc161b173a0517825b8c574a397d01ec`), and the stored A07/A08 preflight and execution records.

## Result

No P1 or P2 finding remains in the A09 source and contract. A09 is a source-consistent successor to the failed A08 attempt.

The A08 to A09 change adds a fixed, hash-bound RECORD diagnostic and a 45-row overlay. It also changes the helper, attempt, report, and report schema names to A09. The stored patches show no unrelated source change.

## RECORD classification and projection

The current diagnostic input has 1,548 rows and 45,567,887 measured bytes. Read-only inspection confirms 45 rows with both declaration comparisons false, 995 rows with both comparisons true, and 508 rows with both declaration fields absent.

The 1,503 non-overlay rows therefore mean 995 strict declared matches plus 508 independently observed undeclared rows. A09 does not call all 1,503 rows strict matches. Undeclared rows retain `null` declaration values, `null` comparison flags, and the `independently_observed_undeclared` disposition.

The current `RECORD` domain includes every regular file named by the current Pillow and NumPy records, including `.pyc` files. Only the historical A03 path set excludes `.pyc`; A09 does not exclude them from the current scan.

`parse_record_divergence_authority` requires the diagnostic's exact key set, schema, unqualified flags, row count, byte total, unique package/path keys, and exact mismatch projection. It validates each row's declaration pair, current hash, current byte count, identity, and comparison flags at lines 522–704.

The overlay must bind the diagnostic path, byte count, and SHA-256. Its 45 rows must equal the diagnostic mismatch projection. Each installed overlay row must match the fixed path, declaration values, and current measured values. Every overlay row must still differ in both hash and byte count at lines 706–751 and 869–896.

Non-overlay declared rows require both hash and byte comparisons to be true. Partial declaration pairs, mixed mismatch flags, repaired overlay bytes, new mismatches, and unused overlay rows fail. This is an explicit overlay comparison, not a generic mismatch bypass.

## Bounded reads and ownership

`measure_regular` bounds every read to 65,536-byte chunks, reserves captured bytes from the descriptor size before retaining chunks, checks descriptor identity before and after reading, checks the pathname after reading, and records a final pathname check at lines 236–299.

`measure_confined_regular` walks every parent with descriptor-relative `openat`, `O_NOFOLLOW`, and `O_DIRECTORY`. It checks each child endpoint before transferring ownership to the retained chain. A failed endpoint check closes that child immediately. The final file remains open through hashing, parent descriptors are checked after reading, and cleanup closes the file and parent chain in reverse order at lines 302–467.

Runtime roots remain held through the scan. `finish_held_directory` checks descriptor and pathname endpoint identity. `finish_tracked_paths` performs a final no-follow pathname check. The main `finally` block closes every retained descriptor, including the report descriptor.

The report uses `O_RDWR|O_CREAT|O_EXCL|O_NOFOLLOW`. Streaming JSON writes enforce the 32 MiB report cap. The helper fsyncs the report, requires the attempt directory to contain exactly one report, fsyncs the attempt and unit directories, then rereads the report through the still-open descriptor. The final read checks bytes, SHA-256, size, descriptor identity, and descriptor-relative pathname at lines 992–1038 and 1342–1404.

These checks preserve failed attempts. They do not overwrite an existing attempt or qualify a partial report.

## Schema and qualification boundary

The report is schema 4 with state `current_runtime_filesystem_snapshot_complete_unqualified`. The record comparison has separate totals for 1,503 non-overlay rows, 995 strict matches, 508 undeclared observations, and 45 fixed measured divergences.

The diagnostic, overlay, and report scope keep execution authorization, package imports, loaded-image attestation, provider origin, divergence cause, wheel or RECORD trust, standard-library closure, native dependency closure, runner closure, observer execution, comparator execution, and native text execution false.

The source enforces isolated CPython 3.12.14, `-I -B`, exact executable bytes, runtime manifest identity, module absence before and after, and exact fixed paths. The logical caps bound reads, rows, paths, captures, output entries, and report bytes. The contract correctly excludes Python allocator overhead, RSS, operating-system memory, loaded images, and process-wide native closure.

## Preserved predecessor records and freshness

The A07 execution record (`86b919f2f290085f277d64a77cf312cb90b58efb604c5e09999c2558715d33d7`) records a pre-publication metadata-name failure. The A08 execution record (`880a3b0f8bc9708432810e412b1944120e68f3f05fdcffcf2ba8d5be20686a61`) records a pre-publication `RECORD` hash mismatch for `PIL/.dylibs/libXau.6.dylib`. Both records report no report, no comparator execution, no native execution, and no loaded-image attestation.

The A07 and A08 preflight records are preserved with hashes `810cb8ae0766203a641b1b68847441f71c6562ad6698cae83f34f8cd270ae8bd` and `327dbdd6d6209df0bc8c0eb603f47c8631108910e2af05674b18ff8e4258cc48`. The A09 attempt directory is absent at this review. The A07 and A08 failed attempt directories remain separate and empty.

## Review limit

This review establishes source and contract consistency only. It does not establish current runtime execution, a successful A09 report, package import behavior in a live process, loaded images, provider origin, wheel validity, divergence cause, observer or comparator qualification, native text execution, playback, hearing, or creative acceptance.
