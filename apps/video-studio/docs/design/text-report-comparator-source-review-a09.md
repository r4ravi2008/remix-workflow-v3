# Comparator A09 independent source review

## Status

Comparator A09 is not ready for control execution or native qualification.

This review found four P1 blockers and one P2 contract gap.
The package remains source-only, unexecuted, and unqualified.

This review used the preserved A08 findings as its fixed comparison point.
It also checked the frozen Rust A05 and Swift A15 producer contracts.

The reviewers use the same model family.
This review is not blind or cross-family evidence.

## Frozen identities

| Artifact | SHA-256 |
| --- | --- |
| `compare_text_reports_a09.py` | `bdbc009fffdec1dbcc574817559fd252e1166f8f25459f8fa010d857a46025d5` |
| `actual-comparator-control-a09.py` | `2c699793683cdf8cd32509ca17a2b9e4235f27fbb49c876c5d0e086b4c66622e` |
| `required-evidence-control-a09.py` | `cede76e770b2ab9fb44223add214b301e79ad21e32b04d642fd75e5558fcb54c` |
| `output-schema-a09.md` | `efd08c6b50de5428c9d7bb1456953a5dc2dd0e246fa0b006ca0d926b287bb49f` |
| `source-rationale-a09.md` | `74d7d6249cd1fdbaf3d0685320f3f21cf8a9dede2dafaabc2441c3d7c0294576` |
| `package-manifest-a09.json` | `d8dcdee1afea94f85fdd78601ba85d6224c6a3c836f8e4a22f079123c3542cd8` |
| Swift A15 `probe.swift` | `83e9693be8d53a4bf2a2135f9b6bd643b7be3329129bddf13288ab85ea9f8a01` |
| Swift A15 source manifest | `0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e` |

The A09 package manifest matches the reviewed package bytes.

## P1: the active Swift gate calls an undefined function

`_require_swift_case` calls `_a09_validate_swift_state` at line 4351.
No function or assignment defines that name.

The intended existing function appears to be `_a06_validate_swift_state`.
That function is defined at line 3807.

Both active gate paths reach the undefined call:

- `swift_case_gate_passed`
- `producer_internal_passed`

`swift_case_gate_passed` catches only `ContractError`.
The main entry point also does not catch `NameError`.

An otherwise complete comparison can therefore terminate without a structured failure result.
The actual-function control also reaches this call after its structural fixture.

Define one current state validator and call it by its exact name.
Add a positive call through both active gate paths.

## P1: the historical projection rejects an honest Swift A15 report

Swift A15 sets `writtenFiles` to 512 MiB.
Its source derives that value from `maxPersistedOutputBytes`.

The historical policy validator requires exactly 256 MiB at lines 778–796.
`_project_swift_historical` preserves the current `writtenFiles` value.

Every honest Swift A15 report therefore fails at line 3967.
The failure occurs before allocation replay or producer qualification.

The current A15 validator must check every A15 cap before projection.
The historical adapter must then use a deliberate historical structural view.
The producer's accepted 512 MiB persisted-output policy must remain unchanged.

The actual-function control does not provide a faithful positive report either.
Its fixtures use a 512 MiB `logicalPayload` and allocation cap.
Swift A15 uses a 16 MiB logical payload cap.

Several fixture optionals are present as JSON `null`.
Swift synthesized encoding omits absent optional fields.
The historical validator treats every present optional as an object.

Repair all three failure-position fixtures with actual A15 values and omission rules.
Require each positive fixture to pass the complete report parser.

## P1: the Swift gate omits mandatory producer obligations

Renaming the undefined state validator is insufficient.

`_a06_validate_swift_state` correctly checks these facts:

- disposition domains;
- ordered repeat prefixes;
- terminal failure placement;
- expected rejection residue;
- three successful repeats for accepted cases.

`_validate_a06_swift_extras` also checks successful-raster roles and the fractional toggle schedule.
The raster scanner later checks digest and relation evidence.

The active `_require_swift_case` still omits these source-bound obligations:

- allowed error codes for rejection and observation-only rejection;
- positive and exactly-zero coverage requirements;
- required case-level main and guard records;
- required case-level clip and reference records for `te-basic`;
- equality between required case-level records and repeat-zero records;
- the exact repeat-zero native glyph image for `ascii-digits-positive`;
- rejection of native glyph images for every other case;
- complete case-level evidence after a successful failed-case prefix.

The current repeat binding compares a case-level mask only when that mask exists.
It does not require the case-level record to exist.

Missing case-level masks can survive the current scan.
The scanner uses each repeat's retained `successfulRaster` records.

A missing Swift native glyph image can also survive cross comparison.
Native image identities are compared only between same-producer fresh runs.

The result can therefore overstate `producer_internal_gates_passed`.
Some omissions can also reach `source_validated_native_execution_pending`.

Restore one complete source-bound Swift obligation function.
Call it after structural parsing and before producer qualification.

Add actual-function controls for these states:

1. one accepted shape with all required records;
2. one accepted exactly-zero case;
3. one allowed expected rejection;
4. one allowed observation-only rejection;
5. faithful failures at repeat zero, one, and two;
6. missing case-level main or guard;
7. missing `te-basic` clip or reference;
8. wrong rejection error code;
9. missing or misplaced native glyph image;
10. missing fractional control evidence.

The current actual control has no valid accepted or expected-rejection full report.
Its narrow failure helpers do not close these obligations.

## P1: Rust control stability compares repetition-specific paths

`_a09_rust_control_signatures` serializes the complete control record.
That record includes its nested mask paths.

Rust A05 saves controls below a repetition-specific directory:

`cases/<case>/repeat-<n>/control-<schedule>`

Rust A05 derives `control_masks_identical` from canonical decoded SHA-256 values.
It does not compare evidence paths.

Equal control pixels from three honest repetitions therefore produce different A09 signatures.
The comparator then rejects the truthful declared stability value.

Derive control-mask equality from the independently opened canonical summaries.
Keep paths as per-run provenance.
Check setter traces and reported predicates as separate obligations.

Add two actual-function controls:

- equal decoded masks with different repetition paths;
- changed decoded pixels with a falsely true stability declaration.

The current actual control contains no Rust repeat-stability fixture.

## P2: reservation-table observations and permanent baseline are not fully bound

The allocation object and policy both report `reservationTableObservedPeakSlots`.
The binding table at lines 2408–2412 omits that pair.

The comparator checks only that the allocation value does not exceed the slot count.
The policy value can therefore disagree with the allocation value.

The event replay starts from the correct 1,081,600-byte baseline.
It does not keep that baseline permanent.

An arbitrary `release` event can reduce outstanding bytes below the baseline.
The final and peak summaries can then report that lower value consistently.

Bind both observed peak-slot fields exactly.
Require every replay transition to retain at least the permanent baseline.
Require peak and final outstanding values to retain the same baseline.

Add direct mutations for both conditions.

## A08 finding disposition

A09 makes useful progress on the preserved A08 findings.

- The 19-field allocation shape and initial replay baseline are now explicit.
- Producer `ErrorRecord` fields remain producer-owned.
- Rust shape and disposition equality are now derived.
- Swift repeat aggregation follows the producer's main-bearing rule.
- The A15 source manifest join is explicit and bounded.

The Rust control comparison is still incompatible with producer semantics.
The actual-function schedule also cannot pass its declared positive paths.

## Verdict and limits

Preserve A09 as a rejected, unexecuted source package.
Prepare a successor before any comparator or native gate uses it.

No Python source was imported or executed during this review.
No control, compiler, producer, native framework, PNG decoder, GPU, or Resolve operation ran.

This review does not establish native text feasibility, product integration, orientation, playback, hearing, or creative acceptance.
