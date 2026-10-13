# Rust producer runner A09 root process utility source peer review A03

## Disposition

**Rejected before caller preparation or execution.** No P1 finding remains. Two P2 truth defects remain in the returned closure record.

A03 closes the three A02 findings. It accepts Darwin stop signal zero, retains exceptional cleanup ownership, and performs final executable and cwd joins.

This review is source-only. I did not import or execute the utility. I did not compile, test, spawn, probe, or start any child, native, media, GPU, or Resolve process.

## Frozen receipt

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `native_runner_process_a09.py` | 45,327 | `7ae21330bdcd3fa7708c9c6c7a3180df7a9c18dd317bbb76185d23964b98dc18` |
| `source-rationale-a03.md` | 1,825 | `103fc1cff2914b23d4f3ae266317b27af9c91fd21e4061c0ebab56c330954fb5` |
| `preparation-receipt-a03.json` | 871 | `0e57dd8fcda94b6ca9669089a704068ee8b5c4a2730cfb2a6b14b62e024ba03a` |

I read all 934 source lines and the complete A02-to-A03 change. The three file identities match the frozen provisional receipt.

## P2 findings

### P2.1: Delivered-signal summaries can omit successful attempts after truncation

`record_signal` counts every attempt but retains only the first 32 records. See lines 688-692.

`termDelivered` and `killDelivered` search only that retained prefix. See lines 914-929.

Exceptional supervision can continue beyond 32 attempts. A later successful signal can therefore coexist with `killDelivered=false` or `termDelivered=false`.

The exact attempt count and truncation flag do not repair those two summary values. Consumers can read a false delivery summary.

Track each delivered-signal summary across every attempt. Keep the 32-record detail cap and exact total count unchanged.

### P2.2: `closureComplete` does not require successful local resource closure

`held` starts empty. A selector readback failure leaves it empty. See lines 674 and 861-865.

Selector close, stream close, and launch-authority descriptor close failures only append causal records. See lines 866-880.

The `closureComplete` predicate checks `not held`. It does not check successful selector readback or those close operations. See lines 904-905.

The utility can therefore report `closureComplete=true` when stream ownership was unknown or a retained descriptor failed to close.

Record explicit selector-readback, selector-close, stream-close, and authority-close results. Require those results for `closureComplete`.

Also capture an `attempt_fd` close failure as a bounded causal record. The current close at line 893 can escape the structured result.

## Closed A02 findings

The stopped-child gate now requires the grounded Darwin stop signal zero. A consumed terminal status remains separate from the stopped status.

The exceptional supervisor retains the stack, process object, streams, and authority descriptors. It does not return until terminal wait and group absence succeed.

The supervisor never signals a reaped direct child. It also stops signalling an observed-absent owned group.

The ordinary timeout, TERM, KILL, reap, and pipe-hold windows remain finite. Exceptional ownership supervision may remain active without a deadline.

The utility caps retained signal records at 32. It records the exact attempt count and whether record truncation occurred.

After reap, the utility rehashes the held executable and rejoins its full receipt. It also rejoins the held cwd and current pathname anchor.

`closureComplete` requires both final authority joins. The caller must provide the original executable receipt and cwd and attempt anchors.

The main-image check remains limited to the loaded executable mapping. Runtime dependencies and dyld remain unattested.

One synchronous `proc_pidinfo` call has no user-space interruption bound. The source states this limit accurately.

## Scope limit

This review covers only the immutable A03 utility, rationale, and receipt. It does not review or authorize a future caller or Runner A10.

A03 has no prepared caller and no execution evidence. It establishes no compilation, native output, product integration, playback, hearing, or creative acceptance.

This is a same-model-family, nonblind review. The A02 findings and requested A03 repair shape were known before completion.
