# Comparator A10: parent source findings

The parent read the complete 602-line A09-to-A10 comparator patch against the previously reviewed baseline. The parent read all 503 actual-control lines, all contracts, the package manifest, the required-control delta, and the complete independent A10 review. No A10 comparator or control was imported or executed.

| Artifact | SHA-256 |
| --- | --- |
| Comparator A10 | `f3d34fc015891cce0a0bfed5945de59f56410730e74d0db61ab7c4004acd32ab` |
| Actual controls A10 | `1cce87390afa509fac3310bf008fb351a637b4c12a2fa9a37249ffc567b9ccb6` |
| Required controls A10 | `0144720e2afca407bd8b4e1dad32452348daa02659ceba5883473a5f727d28c7` |
| Package manifest A10 | `347d5047d91aa34041bc112d234071466583c15aaf9267ae42c459c4c4df7666` |
| Independent source review A10 | `c3766d3c6d2969ed70c37010391c565c68fe64e483b897e83fae9cb3091188f7` |

A10 repairs the undefined active-validator call and several current schema bindings. It preserves the 16 MiB logical policy, 512 MiB persisted policy, 1,081,600-byte reservation baseline, exact optional omission, and complete 21-row source authority. Four P1 findings remain before control execution.

1. The historical projection sets policy written-file capacity to 256 MiB, but retains current allocation bytes. Its old allocation check rejects the mandatory A15 mask subset of 314,231,808 bytes. Preserve authoritative current allocation validation separately from the historical structural view.
2. The evidence reader also retains a 256 MiB per-run stored limit. The required mask subset exceeds that limit before observation-only files. Derive explicit producer-specific budgets from the frozen domains. Test exact capacity and one byte over.
3. The state grammar rejects truthful partial producer failures. `probe.swift` assigns causal case shape, main, guard, comparison, and controls before appending a successful repeat. Failed repeat zero can retain those fields. Fractional prefixes can retain only completed and partial terminal controls. Observation-only processing maps any caught `ProbeFailure` to its rejected observation disposition. Preserve these records without qualifying unexpected failure. Synthetic records must follow the actual producer sequence.
4. The actual-control positive policy omits `reservationTableObservedPeakSlots`. Its first allocation check raises `KeyError`. Its range mutation also fails the binding check before its expected range error. Correct the fixture and error attribution. Add complete-parser and active-gate controls for zero coverage, above-256-MiB current allocation, source-faithful partial failures, observation-only non-font errors, and the full evidence budget.

Preserve A10 and prepare A11. No native producer, decoder, compiler, GPU, or Resolve action is authorized by this comparator review. Passing the separate four Swift pure controls does not qualify A10 or native text rendering. The independent reviewer used the same model family and inherited context.
