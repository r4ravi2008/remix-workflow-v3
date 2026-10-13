# Rust producer runner A09 root process utility source peer review A04

## Disposition

**No P1 or P2 finding remains in the bounded A04 utility source.**

A04 closes both A03 findings. It preserves the retained process owner, stop-zero admission, terminal-status separation, and final authority joins.

This result permits a separate caller-source review. It does not authorize utility execution or any caller execution.

## Frozen receipt

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `native_runner_process_a09.py` | 46,572 | `b903a9aff1cc2d8dae73b16800f177322b000b2983e5a45206a639326727d47d` |
| `source-rationale-a04.md` | 910 | `9c9dfceecc27187ab254dcfd812e2432d57790e912249d50ee2f9c40bc79d48f` |
| `preparation-receipt-a04.json` | 870 | `d50e7c4229599c98273aabcd52dae19d2ca6d2563824ec91918cf6d4369641a3` |

I read all 959 source lines and the complete A03-to-A04 change. The change contains 32 added lines and seven removed lines.

The three file identities match the frozen provisional receipt.

## Closed A03 findings

`record_signal` now updates `term_delivered` and `kill_delivered` for every signal attempt. See lines 695-704.

The retained 32-record event prefix remains bounded. The exact attempt count and truncation flag remain separate.

The final delivery summaries no longer depend on that retained prefix. See lines 939-954.

Selector readback, selector close, both stream closes, launch-authority close, and attempt descriptor close now have explicit results. See lines 873-916.

A stream close must also set the stream's `closed` property. Launch-authority closure must empty the retained descriptor list.

An attempt descriptor close error now enters the bounded causal record. It no longer escapes the structured result.

`closureComplete` requires every new result. See lines 927-930.

## Preserved ownership and evidence boundaries

The exceptional supervisor retains process, stream, executable, cwd, and attempt ownership until terminal wait and owned-group absence succeed.

Ordinary timeout, TERM, KILL, reap, and pipe-hold windows remain finite. Exceptional in-process supervision can remain active beyond those windows.

The stopped-child gate still requires the grounded Darwin stop signal zero. Stopped status and consumed terminal status remain separate.

The utility rejoins the complete held executable receipt after reap. It also rejoins the held cwd and current pathname anchor.

The caller must provide the original executable receipt and cwd and attempt anchors.

The loaded-image check covers the main executable mapping. Runtime dependencies and dyld remain unattested.

One synchronous `proc_pidinfo` call has no user-space interruption bound. The source states this limit accurately.

## Scope limit

This review covers only the immutable A04 utility, rationale, and receipt.

The provisional A10 compile caller remains unreviewed and unexecuted. It must bind the accepted successor before its own freeze and review.

No module, caller, compiler, test, child, probe, native producer, media, GPU, or Resolve process ran during this review.

This review establishes no native output, product integration, playback, hearing, or creative acceptance.

This is a same-model-family, nonblind review. The A03 findings and requested A04 repair shape were known before completion.
