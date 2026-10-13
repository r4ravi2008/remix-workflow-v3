# Rust producer pinned qualification A01 parent source review

Root rejects frozen A01 before compilation: zero P1 findings and one P2 finding remain. The Rust pin and diagnostic changes have no additional identified defect within this source scope.

Root independently measured all eight source files and all 207 external bindings. Both declared aggregates match. Source has 177,441 bytes and SHA-256 `9da21e8b8ed15985808611d5d053f0149a78959fb7b113b22740dffe38e05bc9`. External bindings total 33,335,081 bytes and SHA-256 `8eccf632114b209be23890338d5d7bf29b30bad4fcf7044c661708443d8d5036`. The final manifest is 90,182 bytes with SHA-256 `2cb9d7e25718a458ccf4788962190d66aca7c78a70602f24888bed1f8bf5c460`.

## P2: the direct recipe retains draft closure receipts

The frozen recipe's `sourceClosure.externalBindingCount` is 205. Its `externalAggregateSha256` is `4ce92a37a831a478725a420e4aa2ce1b570eedd4a4f1eb073c8368518ccbff85`. The final manifest instead binds 207 rows with aggregate `8eccf632114b209be23890338d5d7bf29b30bad4fcf7044c661708443d8d5036`. The final data peer review and root disposition account for the two additions. The recipe labels those stale values as the current frozen source closure.

The recipe is 14,013 bytes with SHA-256 `42435c8486367d2171737b3acbc8019b249526db07400cde3a7b0419dc34a607`. Preserve it and the frozen A01 package. A narrow successor must name and bind its actual closure accurately before compilation.

## Complete source delta read

Root fully read the final README, contract, rationale, direct recipe, lib and no-argument harness. Root read the complete qualification diff against A06 and trust-root diff against A02. The qualification additions bind four expected vectors, load the opaque qualification, use fresh private full revalidation, compare all four references and both final byte buffers, and exclusively save two vectors and a diagnostic report. The trust-root change only replaces the absent pin with schema 1, 2,664 bytes, SHA-256 `ddd6614afb7879905e3941e18269979728e57d92ffb43df84c49beb41c2f7707`, and embedded exact manifest bytes. The lib changes the local trust import and exports the diagnostic seam. The harness retains the actionable error.

The existing private constructor and private qualification fields remain. Callers cannot select paths, hashes, commands, dispositions or accepted authority. Diagnostic publication reports a privately constructed opaque qualification separately from caller construction, execution authorization and native execution. The fixed recipe retains the measured compiler, four archives, ten-variable environment and owned TMPDIR. The prescribed order requires source reviews, two compiles, external bootstrap source/binary/pin reviews and one positive invocation. Historical A06 absent-pin controls are outside that invocation.

Separate source peer review is pending when this parent review is saved. No compilation, diagnostic invocation, native child, product integration, WATCHED, HEARD or creative acceptance occurred. This is a same-model-family, nonblind source review. Disk measurements do not attest loaded runtime images.
