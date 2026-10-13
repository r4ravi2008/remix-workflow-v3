# Rust producer runner A17 current readback peer review

Review state: complete read-only current-file readback. This report is separate from the frozen A17 source review. It does not rerun the A17 helper or import any target code.

## Bound evidence

The proof input is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a17-parent-source-readback-a01.json`

It has 764,624 bytes and SHA `70d509163202c8bf01ca60deeb824f92b2fc0f3b87c800a1f0ee3734e1861e82`. The proof declares 655 input rows, 164,928,922 input bytes, 27 explicit compile imports, and 23 imported Rust source files.

The authenticated helper receipt is:

`rust-producer-runner-a17-readonly-helper-external-authenticated-launch-a01.json`

It has 1,448 bytes and SHA `eaaddde7528a6ac564c9bc3761934f6f432a7be77c2842a3fe971c4081055872`.

## Independent path and identity readback

I parsed `inputsAfter` from the proof and reopened every one of its 655 unique paths. Each path was required to be a regular file. I read each file in bounded 1 MiB chunks, recomputed its byte count and SHA-256, then compared the current `path`, `bytes`, and `sha256` to the proof.

I also compared all nine identity fields for every row:

`device`, `inode`, `mode`, `links`, `uid`, `gid`, `bytes`, `mtimeNs`, and `ctimeNs`.

The current rows matched `inputsAfter` exactly. `inputsBefore == inputsAfter` also holds byte-for-byte in the saved proof. The proof's `inputsMatched` is `true`, and its declared total equals the current 164,928,922 bytes.

The current manifest file was reopened and matched the proof's complete path, byte count, SHA-256, and nine-field identity record:

`source-manifest-a17.json` — 122,137 bytes, SHA `4a018cbf2547b58c86993e59829a6b87fe7e40604681190bed006669e8dbd48b`.

The proof source and external aggregates match the current manifest. The current external aggregate remains 204 rows and 41,322,619 bytes with SHA `41d3e55c523574ef54f37eb3e145cf9daa3635ddc7e9f3dcdb7f5781049e112a`.

## Helper receipt and logs

The authenticated receipt has exactly these 18 top-level fields:

`schema`, `state`, `helper`, `manifestSha256`, `isolated`, `optimize`, `dontWriteBytecode`, `executedFromExactHeldMeasuredBytes`, `projectCodeImported`, `processUtilityImported`, `compilerExecuted`, `controlsExecuted`, `nativeProducerExecuted`, `nativeResultAccepted`, `productIntegrationAllowed`, `watched`, `heard`, and `creativeAccepted`.

The nested helper record has the expected path, bytes, SHA-256, `identityBefore`, `identityAfter`, and `descriptorClosed` fields. Its helper path, 14,766 bytes, SHA `71c613758f2ab9937992d45422c41a83e317edc795f25cbc912ea729f2bd9bdd`, and both nine-field identities match the current helper file. `descriptorClosed` is `true`. The receipt manifest SHA matches the current manifest SHA.

The receipt records `isolated=true`, `optimize=0`, `dontWriteBytecode=true`, and `executedFromExactHeldMeasuredBytes=true`. Its project-import, process-utility, compiler, control, native-producer, native-result, product-integration, watched, heard, and creative fields are all explicit `false` values.

The saved helper stdout is 858 bytes with SHA `1cbf09900ecf0549e04484cd109f97f9b37d87c20d35f7f5c389f5580d8bf873`. Its JSON result binds the same proof path, proof size, proof SHA, 655 rows, 164,928,922 bytes, both aggregates, 27 explicit imports, and 23 Rust files. The saved stderr is empty: 0 bytes with SHA `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## Current recipe closure

I replayed the current A08 suffix-field algorithm against the saved 655-row proof map. All 116 `_sha256` and `_bytes` fields passed. The `a11_incomplete_handoff_root_disposition_sha256` alias also passed through `a11_incomplete_handoff_disposition`. Missing scalar or path joins: zero.

The current recipe's `a17_external_evidence_rows` is 204. It equals both the current manifest external row count and the recipe current aggregate row count. The inherited `a15_external_evidence_rows=159` and `a16_external_evidence_rows=198` values remain metadata and are not used for the A17 current count.

## Disposition and limits

The saved 655-row proof is current-file complete for path, bytes, SHA-256, and all nine identity fields. The before/after proof rows, manifest binding, helper receipt, helper identities, logs, imports, Rust-file count, aggregates, and all 116 current closure joins are consistent.

This readback proves source-file identity closure only. It does not prove compilation, controls, process lifecycle, native framework behavior, media output, product qualification, or acceptance. No helper, compiler, control binary, producer, native process, or media operation was executed for this report.
