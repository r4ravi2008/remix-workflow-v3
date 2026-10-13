# Runner A17 ROOT orchestration A09 source peer review

Review state: complete source-only review of the frozen A09 preparation package. The package has one bounded documentation identity defect. Its measured source, external closure, dependency selection, and A08-to-A09 code normalization otherwise pass.

## Reviewed package

Package path:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a17-root-orchestration-preparation-a09`

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `native_runner_fixed_compile_a17.py` | 44,844 | `4f93d86dd5f5a7fa354fab53296e0556394df95f314815da66263f83295cfa1a` |
| `root_inline_launch_capsule_a09.py` | 11,393 | `59cb08d584ae309af0bb005eea06e3820b38aee3f23e634db584c10a295fdc25` |
| `root-inline-launch-recipe-a09.json` | 2,122 | `3c4e5e5af30cb7448ced2c6e4921df03bd3f03f28c7d97f0c1c90e53f46c6c7c` |
| `orchestration-rationale-a09.md` | 6,785 | `28911432dc30d2d7ca05f3e7541beba30c53387bc764dbc2aad128f36a4727bf` |
| `preparation-receipt-a09.json` | 32,349 | `4b4e823afdcf88cf4d34cee64cd34618e9e867be21712a82505e2abce7584998` |

The receipt records `frozen_source_only_root_and_peer_review_pending`. It records no source import, source execution, authorization, capsule execution, compiler execution, control execution, native producer, native result, or product integration.

## Source and external closure

I used standalone JSON parsing, regular-file reads, SHA-256, `ast.parse`, `ast.dump`, and the receipt's framed aggregate encodings. I did not import or execute the caller, capsule, compiler, controls, process utility, or native code.

All four package files match the receipt's source rows. Recomputing the source aggregate produced 4 rows, 65,144 bytes, and SHA `ff7219e07bc7c689d11a5c376b9bae897d06db7d9f2fe3136b0974dec28ae97a`.

All 40 external `(role, path)` rows exist and match their declared bytes and SHA-256 values. The role/path pairs are unique. Recomputing the external aggregate produced 40 rows, 20,221,050 bytes, and SHA `2cfaf0ce85a7bbd912707c4619247a7745fb985ecd3246fff5607cdb91ea7fab`.

The external bindings include the current A17 manifest and recipe, the 655-row source readback, the helper and authentication receipt, the A17 root and peer reviews, the current-readback addendum, the source acceptance disposition, the A04 utility and reviews, the 65-row preflight, and the A16 predecessor evidence. Each current binding matched the saved receipt.

The current subject bindings are:

- A17 manifest: 122,137 bytes, SHA `4a018cbf2547b58c86993e59829a6b87fe7e40604681190bed006669e8dbd48b`.
- A17 recipe: 47,943 bytes, SHA `6fa505ab5f491e09044f78c814c86a92bb5531716dd2321bde504c4a1f130e50`.
- Current source readback: 764,624 bytes, SHA `70d509163202c8bf01ca60deeb824f92b2fc0f3b87c800a1f0ee3734e1861e82`.
- Current-readback peer addendum: 4,753 bytes, SHA `2ccba55deada1ef92a61ea8c2289499775b272079d6d587ce4c0e9ea0d86aa16`.
- Source acceptance disposition: 2,156 bytes, SHA `274b397ac61b63e1efb0dc5713afa0443b57fb35e4faac06222896f5b0991f9c`.

## A08-to-A09 normalization

The caller normalization has 17 declared fixed-label mappings. Applying those mappings to the A08 caller reproduced the A09 caller byte-for-byte. The normalized AST also matched. Its normalized AST digest is `e53379780837bd97275ea378b1e469b7ff9e4cdeaf05974101aee7a3849d0b3e`.

The capsule normalization has 6 declared fixed-label mappings. Applying those mappings to the A08 capsule reproduced the A09 capsule byte-for-byte. The normalized AST also matched. Its normalized AST digest is `c7395d984c908177905c8cbc1760999adc8419b7017ab8f094de1fa9a69b6574`.

The caller's three 64-character SHA literals and the capsule's two 64-character SHA literals have unchanged multisets after normalization. The recipe diff contains only the A09 operation name, capsule path and digest, and caller path and digest. The environment, fixed operation, and other recipe limits remain unchanged.

The subject key is correctly advanced to `a17_external_evidence_rows=204`. The unused inherited `a16_external_evidence_rows=198` value remains recorded as metadata. The historical A15 external count was 159.

## Dependency closure

The bound dependency preflight is 87,471 bytes with SHA `2b89ccd5dc5472867c17f27ac1474726ba8230f9faa6b3a1ab405eec7eaf64f5`. It contains 138 input rows. Selecting rows whose direct parent is one of the two declared A09 dependency roots yields exactly 65 rows.

I reopened all 65 selected files. Their current bytes, SHA-256 values, and preflight identity records matched. The selected files have no duplicate paths and no shared device/inode pairs. Their suffixes are limited to `.rlib`, `.rmeta`, and `.dylib`. The four fixed archive rows for `libc`, `serde`, `serde_json`, and `sha2` are included. The selected closure totals 74,337,756 bytes.

## Finding: stale capsule documentation label

`root_inline_launch_capsule_a09.py:1` still begins with:

```python
"""Authenticate and enter one fixed Runner A15 orchestration caller.
```

The A09 capsule constants, recipe operation, paths, and failure states identify Runner A17. The receipt's six capsule mappings do not include `Runner A15` to `Runner A17`, so the stale docstring remains in the normalized source.

This is a P2 source identity documentation defect. It is inert at runtime, but it weakens the claimed complete A08-to-A09 capsule identity advance. A successor should either update the docstring to Runner A17 and refresh its capsule binding or explicitly document why the historical wording is retained. The A15 host diagnostic path is a separate intentional historical binding and is not this finding.

## Disposition and limits

The A09 package preserves the A08 dependency selection, four-build schedule, environment, caps, source closure checks, current A17 row key, bounded failure handling, and publication ordering. The source and external receipts are current and internally consistent.

The package remains source-only. This review establishes no compiler result, process lifecycle result, native framework result, media result, product qualification, loaded-runtime claim, WATCHED state, HEARD state, or creative acceptance. No package helper, compiler, control, process utility, or native process was executed.
