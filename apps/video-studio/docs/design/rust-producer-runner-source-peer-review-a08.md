# Rust producer runner A08 source peer review

## Disposition

**Rejected before compilation.** One P1 and seven P2 findings remain.

The suspended-launch path can still release its last cleanup owner while the direct child is unreaped. The private controls also leave material race, ownership, and coverage gaps.

This review is source-only. I did not compile, import, test, bootstrap, launch, or execute any package code. I did not start a child, native framework, media tool, GPU, or Resolve.

## Frozen receipts

I read all 15 package files and the complete A07-to-A08 source changes. I rehashed every source and external row.

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| `source-manifest-a08.json` | 47,223 | `21775644ee59b2de369fe775d33d5c356c79cba337fd811b92b5a36191f46d78` |
| `src/lib.rs` | 142,440 | `d83befcb6ad9b033b8c04271e0e848c09a225e96b26b3705782b9f90ea012b79` |
| `src/a08_launch_controls.rs` | 17,293 | `ab4ecbaff496729ac582fb512f490141c95f5ce0c8f7f6038080038b64498fb1` |
| `src/a05_focused_controls.rs` | 55,983 | `5d632c1da53c67bd481c54af8914a3c18622479317c8c9f76734a19784a5bc5d` |
| `src/a05_control_extension.rs` | 70,098 | `9c3dce57fc8aa65e40dc2e3175df2f19036b1327fc2dab38306bf58ec01749fc` |
| `src/pure.rs` | 6,459 | `c2a6ab8948b2762034007cd50c5188c622b48a7ec9f5242e72ca13a7b06a8739` |
| `direct-build-recipe-a08.json` | 18,182 | `26c74a6a61b3ab74e93cbdec7cc20f52ef02e23407cfd7d4fd76b1242beb5` |
| `runner-contract-a08.md` | 7,604 | `c8cdd6da4e498a102cbefdab62c7b65d3eed6fcc7410786cfff187f00bd0c333` |
| `README.md` | 6,286 | `e18a9540a0e2c3bc6bbe951bc796da1da6ee032ff1f5dd4bdd1e6ff0a35e2cab` |

The 15 source rows total 351,644 bytes. Their framed aggregate is `219df7f0d56ff036e49625aa4007ee0b154da3e5f42d58f54be325e65d1db1fb`.

The 97 unique `(role, path)` external rows total 10,580,106 bytes. Their framed aggregate is `7382780d79fe9f6632a00ee4d9791fdd8f8b7b7fd8d77dcb70477ddc470f5dca`.

Every row matches its current file. I independently reproduced both documented aggregate encodings.

## P1 finding

### P1.1: Bounded cleanup can release an unreaped direct child

`darwin_kill_and_reap` returns after its one-second wait and 250-millisecond retry. It can return `(None, kill_sent, false)`. See `src/lib.rs:2299-2336`.

The foreign-process-group path stores that unresolved result and returns a closed failure. See `src/lib.rs:2653-2671` and `2759-2774`.

Other pre-resume failures discard the returned `reaped` fact. See `src/lib.rs:2853-2868`.

`DarwinSpawned::drop` closes only the executable and cwd descriptors. It retains no reaper or final child-absence check. See `src/lib.rs:2132-2144`.

The report then classifies the foreign-group path as `Launch`, even when cleanup is unresolved. The runner can return while it still owns a live, stopped, or zombie child.

Keep the direct-child ownership until terminal status is observed. Persist a distinct cleanup failure if the bounded reap cannot finish. Never publish the attempt as closed while that ownership remains unresolved.

## P2 findings

### P2.1: Post-review mutation controls race the production path

Production sets `A08_REVIEW_OBSERVED` after reading the review. It immediately continues to prelaunch rereads and spawn. See `src/lib.rs:1036-1039` and `2807-2851`.

The control polls every 10 milliseconds before replacing files. See `src/a08_launch_controls.rs:177-220`.

No production pause or acknowledgement barrier exists. The same-byte executable, different executable, cwd swap, and review-identity controls can mutate after the guarded boundary.

Add a feature-private pause after the retained review observation. Resume only after the control acknowledges its mutation or no-mutation choice.

### P2.2: Launch cases are outside the owned control attempt

`launch_variant_controls_a08` creates a timestamped directory under the shared unit root. It ignores the caller-owned `--control-attempt` directory. See `src/a08_launch_controls.rs:345-378`.

The code uses `create_dir_all`, not one exclusive directory creation. The top-level control inventory cannot bind or close these per-run directories.

Place every launch case under the exclusive control attempt. Record its exact inventory and cleanup disposition in the combined report.

### P2.3: Several launch rows can pass without launching a child

The default failure predicate accepts `!child_started || reaped`. See `src/a08_launch_controls.rs:297-303`.

That predicate covers same-byte executable replacement, different executable replacement, cwd swap, proc errors, region failures, and vnode mismatch. The report still declares `actualSuspendedSpawn:true` for the group.

Prelaunch rejection is useful evidence. It is not stopped-child evidence. Give each variant an explicit required start state and report the group claim from observed rows.

### P2.4: Fault injection overwrites kernel observations

The stop mismatch replaces an accepted kernel stop signal with `SIGTSTP`. See `src/lib.rs:2245-2255`.

The group mismatch replaces the observed process group with `pid + 1`. See `src/lib.rs:2644-2657`.

Those injected values become the saved process observation. The control then writes `injectedFault` from its requested variant, not from the saved process record. See `src/a08_launch_controls.rs:266-324`.

Preserve the kernel observation unchanged. Store injected comparator input in a separate field. Require the control to join the saved injected-fault field and observed cleanup facts.

### P2.5: The region deadline does not bound or close the final call

The region loop checks elapsed time only before `proc_pidinfo`. See `src/lib.rs:2397-2410`.

It performs no elapsed check after that call. It can accept a clean `EINVAL` end after the deadline. A blocked `proc_pidinfo` call also remains outside the loop's effective bound.

Recheck elapsed time before accepting either a region or clean end. Document that an individual system call has no user-space interruption bound.

### P2.6: Review and typed-field controls do not isolate their claimed joins

The review-identity case replaces root review, peer review, and sidecar files in one loop. See `src/a05_focused_controls.rs:183-205`.

The first failing reread masks the other two identity joins. The control cannot identify which retained reference rejected the replacement.

The typed authorization variants rewrite `authorization.json`. Saved-file verification rejects that artifact before `validate_typed_authorization`. See `src/a05_focused_controls.rs:83-180`.

Test root, peer, and sidecar identities separately. Add coherent private typed inputs that reach the typed validator while preserving the saved-file drift controls.

### P2.7: Three pure controls remain disconnected from production decisions

`descriptor_read_is_allowed`, `esrch_termination_facts`, and `pipe_drain_completion` are called only by private fixture controls. See `src/pure.rs:138-169` and `src/a05_focused_controls.rs:922-947`.

Production uses separate file-open, signal, and pipe-drain logic. Passing these fixture cases cannot qualify those production branches.

Move each decision behind the shared predicate, or exercise the production branch through a bounded private seam.

## Verified repairs and retained limits

The recipe now includes `src/lib.rs`, both dependency search paths, and all four fixed archives for every direct command.

The source separates rejected stops from terminal statuses. It recognizes the grounded `EINVAL` region end and checks monotonic region addresses.

The source retains executable and cwd descriptors through child closure. It rereads qualification authority while the child is stopped.

The process schema separates owned and foreign process groups. The 21 pure cases are executed instead of copied into report counts.

The package correctly reports source-only status. Native result, product integration, playback, hearing, and creative acceptance remain false.

A separate 441-row source readback was reported after the orchestration snapshot. This review did not execute that helper. Source measurement does not close the findings above.

A08 remains uncompiled and unexecuted. It proves no successful control run, native child lifecycle, producer output, cancellation behavior, product integration, playback, hearing, or creative acceptance.

This is a same-model-family, nonblind review. The parent disclosed some launch and control concerns while this review was underway. No cross-family reviewer was available.
