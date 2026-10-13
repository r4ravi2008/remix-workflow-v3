# Comparator A09: parent source findings

The parent read all 2,258 lines of the A08-to-A09 source diff. The previously reviewed A08 baseline remains preserved. The parent also read the complete 524-line actual control, required-control changes, README, schema, rationale, and package manifest. All six package rows match the frozen manifest. No comparator or control was imported or executed.

| Artifact | SHA-256 |
| --- | --- |
| Comparator A09 | `bdbc009fffdec1dbcc574817559fd252e1166f8f25459f8fa010d857a46025d5` |
| Actual control A09 | `2c699793683cdf8cd32509ca17a2b9e4235f27fbb49c876c5d0e086b4c66622e` |
| Required control A09 | `cede76e770b2ab9fb44223add214b301e79ad21e32b04d642fd75e5558fcb54c` |
| Package manifest A09 | `d8dcdee1afea94f85fdd78601ba85d6224c6a3c836f8e4a22f079123c3542cd8` |

## P1: the active Swift gate calls an undefined function

`_require_swift_case` at line 4351 calls `_a09_validate_swift_state`. The only defined state validator is `_a06_validate_swift_state`. The A09 name has no definition or assignment anywhere in the frozen source.

Both `swift_case_gate_passed` and the active producer gate reach this call. `NameError` is not converted into a typed contract failure by either path. The deferred actual control also reaches it after its structural fixture. Bind the intended validator explicitly and exercise the actual gate.

## P1: the historical policy projection rejects honest A15 storage limits

The historical policy validator still requires `writtenFiles == 256 * 1024 * 1024` at lines 792–796. The projection preserves the current value. Frozen A15 `probe.swift` sets `maxWrittenFiles = maxPersistedOutputBytes`, which is 512 MiB. Every honest A15 report therefore fails the historical policy check.

Validate all current A15 caps before projection. Keep the historical structural view deliberate, with an explicit adapter for changed policy values or a current policy validator. Do not change the producer's accepted 512-MiB storage policy to satisfy a historical check.

The actual control fixtures also use incorrect positive caps: `logicalPayload` and allocation `capBytes` are 512 MiB, while A15 `maxProbePayload` is 16 MiB. Several fixture optional fields contain JSON null. The historical case validator validates a present field as an object; A15's synthesized optional encoding omits absent fields. Repair fixtures to reproduce the actual emitted shape and caps. The three complete parser positives must pass without replacing critical validators.

## P1: Swift mandatory case obligations were removed

The active `_require_swift_case` now invokes the historical structural validator and checks only the disposition of a declared rejection. It no longer enforces the actual closure's required case-level main/guard records, coverage requirement, declared rejection error codes, required case-level clipping/reference records, or the exact repeat-zero native glyph image obligation. The first-repeat binding compares case-level records only when those records exist.

The A06 extras still validate successful-raster roles and the fractional toggle schedule. The raster scanner still checks per-repeat digest and relation evidence. This finding concerns the missing source-bound case-level obligations and qualification gate.

The state validator also lost the complete case-role and failed-prefix residue checks. A failed repeat-zero case can retain case-level successful evidence, and a failed prefix can retain incomplete or contradictory success records. Failed cases must remain honest producer failures with the native gate closed. Their preservation must not weaken accepted-case obligations.

Restore current source-bound obligations for accepted, expected-rejection, observation-only, failed-prefix, and outer-failure cases. Keep real producer ErrorRecord fields. Add negative actual-function cases for the omitted obligations and positive faithful failed prefixes at repeats 0, 1, and 2.

## P1: Rust control stability compares repetition-specific paths

`_a09_rust_control_signatures` canonicalizes each entire `ControlDrawObservation`. Its nested mask contains `canonical.path` and `native_raw.path`, which vary with the repetition directory. Honest equal control pixels therefore produce unequal signatures.

Frozen Rust A05 `probe.rs::stability` requires exactly three completed repetitions and compares each control's `mask.canonical.decoded_sha256`. Derive that producer aggregate from independently opened control masks. Preserve location fields as provenance. Validate setter and predicate obligations separately. Add an actual-function positive with equal decoded masks and different repetition paths, plus a changed-pixel/false-declaration negative.

## P2: reservation observations need complete consistency checks

The current allocation binding table omits `reservationTableObservedPeakSlots`, although both policy and allocation emit the same final observation. The current shape validator also does not require peak or final outstanding to retain the permanent 1,081,600-byte baseline. Event replay can release baseline bytes under an arbitrary label and report a lower final outstanding value.

Bind the two observed slot peaks, enforce their range, and preserve the permanent baseline through every transition and final reconciliation. Keep cumulative owner charges separate from retained owner totals. Add direct mutations for both inconsistencies.

## Disposition

Preserve A09 and its partial snapshot. Prepare a new source-only comparator and meaningful actual controls. Source review and the corrected pure controls must pass before comparator or native acceptance execution. Rust and Swift produced binaries, native text, product integration, decoder orientation, film playback, hearing, and creative acceptance remain unverified.
