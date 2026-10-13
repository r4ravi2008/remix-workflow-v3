# Rust producer subject adapter A09 parent source review

A09 repairs the A08 mutation-accessor type mismatch. I found no P1/P2 in this bounded source review. The package remains uncompiled and unexecuted.

I read the complete A08 peer rejection and compared every A09 source file after exact successor-label normalization. The only executable semantic delta is fixture_controls::document_root. It preserves fixture_mutation_document for an absent document. It then calls json.as_mut(), returning subject_document_not_json for a present non-JSON helper. The returned reference now has the declared &mut StrictJson type. No unwrap or placeholder is used.

I audited all direct optional-JSON accesses. The immutable getter and mutable mutation getter both check the optional payload. The toolchain MeasuredReport obtains its required JSON through the immutable getter. Exactly two fixed Python helper descriptors retain bounded regular byte measurements. All eighteen JSON descriptors still pass the strict parser. Helper regular-file rows, hashes, identities, and later joins remain preserved.

All 14 source rows (252,609 bytes), 51 external rows (1,485,642 bytes), twenty fixed authority descriptors, compiler/archive/preflight bindings, and both aggregates reproduce exactly. Source aggregate: adebe1a9a4a426340112c5f86541d7c076a7a72f4233ce878cdf7234b44cc4cd. External aggregate: 4d931409faa3881b462c9dd4ae4118fc24e23bdafbb9d41a4b3dfd24d561a141. The observed manifest is 43,023 bytes with SHA-256 4a6f37c4e0c6690ef074ca78716a0feafe9f65f5847924975182bfd6aaf1f7c7.

The frozen direct recipe matches A08 after successor substitution. It retains repository cwd, edition 2024, panic=abort, harness thin LTO, both dependency roots, and all four existing archives. The 28-case schedule, 2,068 roles, resource counts, and two full reconstruction equality checks remain unchanged. A09 attempt, canonical publication paths, and fixture roots are absent.

A08 and both source rejection reviews remain immutable external lineage. A07 successful compilation and failed control evidence remain preserved. I read the complete separate-author A09 source peer review and its bookkeeping correction. It found no P1/P2. The review is same-family and nonblind.

No source was imported or executed. Source review does not establish controls, native execution, production trust, attempt authorization, product integration, WATCHED, HEARD, or creative acceptance.
