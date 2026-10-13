# Comparator A08 draft parent source findings

A08 draft remains preserved and unexecuted. Root read all 737 comparator delta lines, all 293 actual-control delta lines, the unchanged required-evidence control identity, every changed contract paragraph and the complete README. Root also inspected the active report adapter, event replay, error vocabulary, producer repeat aggregation and raster summary fields.

Comparator SHA-256: `494245cf947e3493f319df0c50b13c324962df779f30a4d02583b39f2f047415`.
Actual-control SHA-256: `d0d7b4eccd0a0495eaaeba0aee05c3fee38e7fb16891148f4fe8ff4d26814443`.

## P1: new allocation fields never reach a compatible full validator or replay

The report path projects through `_adapt_swift_for_a01` without projecting allocation. The preserved validator at line 724 still requires exactly fourteen allocation keys. A13 and its successors emit five additional reservation fields.

`validate_swift_allocation_log` at line 2411 still starts outstanding and peak at eventScratchBytes alone. The producer starts at 1,081,600 bytes. The later reconciliation wrapper checks baseline copies but cannot repair an event stream already rejected at its first transition.

Validate the complete new allocation contract, project only an independently checked historical view where needed, and seed actual stream replay from the checked initialReplayBaselineBytes. Require peak and final charge to cover the baseline. Add a bounded real event stream control through the complete report/replay path.

## P1: failed-case grammar invents producer fields

`_a08_validate_failed_case_state` requires code producer_contract_not_met and gatePassed=false inside producer ErrorRecord. The producer ErrorRecord has code, detail, evidence, partialFace and geometryFailure. It has no gatePassed field and preserves actual operation error codes.

The new error validator rejects geometryFailure. It also rejects the invented gatePassed used by the draft's own failed fixtures. Those fixtures call the narrow case-obligation helper and bypass the complete parser.

Preserve source-defined producer errors and causal records. Put comparator qualification status and producer_contract_not_met in comparator output. A structurally valid failed producer must keep qualification false without being rewritten into an impossible input grammar. Controls at repeats zero, one and two must pass through the complete structural path.

## P1: the draft control schedule cannot load or validate its declared positives

The actual-control source still pins comparator hash `237aaab95996a9f71ed9f8b1b5f177413f22fee9452d4071dc46623887ee694f`, rather than its final `494245cf...`. Its loader therefore rejects before calling any comparator function.

The positive stability fixture includes a different repeat index in each compared signature. The positive reservation fixture reports a 25,600-byte peak with a 1,081,600-byte baseline. The proposed scratch mutation recomputes a consistent baseline; it cannot trigger its expected baseline-arithmetic error. The source-join control also expects an obsolete source-controls error from a four-control A13 map.

Static literal comparison found one A13 row checksum transcription defect: protocol-bound-correction-a12.md differs from the manifest. Generate final bindings from the exact accepted manifest and verify every literal before freezing.

Repair the fixtures around truthful producer records and actual stream observations. Rehash the final comparator in every loader. Keep both full and required-evidence schedules.

## P2: Rust shaping, dispositions and controls are still not derived across repeats

The new Rust stability branch compares main, guard, clip and reference summaries only. It leaves shaping/disposition booleans authoritative and omits Rust toggle summaries. A mutation copied across both fresh-process reports can still change one repeat's shaping or control while keeping those flags true.

Derive the complete supported Rust shape, disposition and control relationships across repeats. Preserve the separate fresh-process and cross-producer comparisons. Add same-mutation controls for each retained relationship.

## P2: the Swift aggregate flag uses a different rule from the producer

The draft forces the derived flag false for any failed case. The producer aggregates only results with a main mask. A failure at repeat zero has no main mask and can leave allSupportedRepeatsEqual=true, while unexpectedFailures independently closes qualification.

Match the source-defined aggregation and derive actual stability for its comparable cases. Keep incomplete or failed-case qualification separate from this flag. Do not normalize or reject honest failure evidence because of a different aggregate definition.

The temporary serialization owner classification now matches the producer labels. The exact error byte caps and range checks are useful repairs. They are not executed results.

The final Swift source binding remains pending. No draft control, comparator main, native producer, image decoder, GPU or Resolve operation ran. No product or audiovisual acceptance is established.
