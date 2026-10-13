# Rust producer subject adapter A08 parent source review

A08 remains uncompiled and unexecuted. One P1 type error blocks the fixed control harness. Preserve A08 and repair this exact error in an additive successor.

At src/fixture_controls.rs:177-184, document_root declares Result<&mut StrictJson>. Its unchanged map expression returns &mut value.json. A08 changes that field to Option<StrictJson>, so the function now produces Result<&mut Option<StrictJson>>. This cannot satisfy its declared return type. The mutation accessor must first obtain the existing document, then use json.as_mut() with the same subject_document_not_json failure for helpers. It must preserve fixture_mutation_document for a missing document. No placeholder or unchecked unwrap is appropriate.

The intended payload repair is otherwise correctly bounded. Exactly buildManifestHelper and inputRawBridgeHelper use measure_regular and retained measured bytes. The other eighteen fixed documents still require the strict JSON parser. SubjectDocuments::json rejects helper access. Toolchain MeasuredReport obtains its JSON through that accessor. Existing helper rows and cross-file size/hash joins remain unchanged. The 28-case controls, 2,068-role schedule, resource counts, and fixed direct build recipe remain unchanged after successor-label normalization.

I compared every package file against A07 after exact version substitution. All 14 source rows (252,080 bytes), 48 external rows (1,435,416 bytes), and twenty fixed authority descriptors match individually. Both aggregates reproduce exactly: c22732aa25a26f43625f8631140adb3f9861200c85a74e5cc212163b6959e0e0 and 5b6c1ec749fe75db56efaef77ed88a594a62698348a9441f8b433195deed371a.

The exact observed manifest is 42,187 bytes with SHA-256 4088075b25f74e74350cd575075ce561b82cbffa3a762a4048b15cebd05d2ec0. The author handoff quoted a different manifest hash. This review uses observed bytes; that handoff discrepancy is bookkeeping and is not an additional source defect.

The separate source peer independently reported the same P1 and continues its bounded review. No Rust source was imported, compiled, or executed. Native execution, production pin, real acceptance, attempt authorization, product integration, WATCHED, HEARD, and creative acceptance remain unverified.
