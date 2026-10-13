# Rust producer runner A15 source peer review

## Disposition

**Source-ready for separate compilation.** I found zero P1 and zero P2
findings. I found one P3 documentation-accuracy issue.

A15 corrects the two invalid A14 direct-recipe digests. Every current recipe
path, byte count, and digest join now matches its fixed file. The A15 package
also binds all six A14 predecessor receipts with their measured identities.

The Rust lifecycle, schema, and control schedules remain unchanged from A14.
The A14 signal-authority and cumulative-evidence repairs therefore remain in
the candidate source.

This review is source-only, same-model-family, and nonblind. I read the A14
ROOT review, peer review, and rejection disposition. I read the complete
A14-to-A15 source and descriptive delta. I checked ROOT's canonical A15
readback and authenticated helper-launch receipt.

I read the final ROOT A15 parent review before freezing this report. Its P3
rationale matches my independent source and authority assessment.

I did not import, compile, test, bootstrap, authorize, stage, or execute this
package. I did not start a child, native framework, media tool, GPU, or Resolve.

## P3 finding

### P3.1: One contract paragraph identifies A13 as the direct predecessor

`runner-contract-a15.md:181-183` calls A13 the direct predecessor evidence.
A14 is the direct A15 code predecessor. There is no intended provenance meaning
under which A13 is the direct predecessor.

`README.md:40-47` and `source-rationale-a15.md:133-151` describe retained A13
and earlier evidence. Those passages omit the direct A14 predecessor chain.
This omission makes the descriptive provenance incomplete.

The authority data remains correct. `source-manifest-a15.json` and
`direct-build-recipe-a15.json` bind these six A14 records:

1. A14 source manifest.
2. A14 ROOT source review.
3. A14 ROOT source readback.
4. A14 authenticated helper-launch receipt.
5. A14 peer source review.
6. A14 source rejection disposition.

No source selection, build preflight, or execution gate reads the stale prose.
The prose therefore does not alter the source or build authority decision.
This is a P3 documentation issue, not a P2 source or recipe defect.

Correct the predecessor wording before product completion. The correction does
not need to block the separate A15 compile stage.

## A14 repair verification

The fixed compiler digest is:

```text
4f26ad57dcb9b12f9791317a1387e3e8d6ad803d4bd20fcdc65142a91e903d45
```

The fixed A12 authenticated helper-receipt digest is:

```text
dd641ad8b84462f9cc734dd8b5a139ec070121f2db3e596fb5885537c361db5e
```

Both values match their current files. They replace the two corrupted A14
literals identified by the ROOT and peer reviews.

I checked every file-backed recipe join. All fixed paths, declared byte counts,
and SHA-256 values match current bytes. The A14 manifest, reviews, readback,
authenticated receipt, and rejection disposition also match their A15 recipe
and manifest records.

## Preserved lifecycle and control shape

`src/lib.rs` changes only A14-to-A15 package labels, paths, bootstrap state,
and private control-source names. No process, ownership, wait, signal, cleanup,
or report transition changes.

`src/pure.rs` is byte-identical to A14. Its SHA-256 remains
`cc79345d6a994eeb860814aa84ca220f6a6f471ad6f9c28b864ee44742f47f7a`.

The A14 ownership rules remain present:

1. Every actual direct `ESRCH` revokes direct-PID authority.
2. Actual TERM and KILL facts remain separate.
3. Earlier KILL delivery survives later non-delivery observations.
4. Terminal status consumption prevents later direct signalling.
5. Group absence remains monotonic through cleanup and `Drop`.
6. Historical reap failure remains distinct from final closure.

The public schema is unchanged. The private schedules remain ten lifecycle
cases, fifteen focused cases, twenty-one pure cases, eleven launch variants,
and five review-reference variants.

These are source observations. No A15 compiler or control result exists in the
reviewed evidence.

## Frozen source receipt

I rehashed all 15 source rows and all 136 external `(role,path)` rows. Every
row byte count and SHA-256 matches. I reproduced both framed aggregates from
their declared domains and encodings. Source paths and external role-path pairs
are unique.

ROOT's canonical readback contains 578 stable inputs totaling 136,300,674
bytes. It records all nine identity fields before and after. ROOT's external
launch receipt records that the helper descriptor closed.

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| `source-manifest-a15.json` | 86,784 | `a051180d94632deb8b581b8fb97a783fbf10aa8fc0af5f1686b8648aa2dd2fdf` |
| 15 source rows | 456,893 | `f1b8f356e761a96229ac8edf4a42fc897b9fecf024de0b43d34c53d0fe85d144` |
| 136 external `(role,path)` rows | 13,024,572 | `4cbaf906deef0af94b89e0e5aad5b759e4547fdbe78b7981baba37737243692b` |
| `src/lib.rs` | 200,612 | `3f9bfcf9bb07c2128f775fb16d2d0698f2f5c5cff83dfc90064166a6ed26a91b` |
| `src/pure.rs` | 7,187 | `cc79345d6a994eeb860814aa84ca220f6a6f471ad6f9c28b864ee44742f47f7a` |
| `src/a15_focused_controls.rs` | 67,411 | `093b67c0a2cc4d4cc046c2e639107396b0859f1018a443b11a818fcd6d3900a0` |
| `src/a15_launch_controls.rs` | 21,491 | `817aa868dac1b07bd6121172c9238ce0d92823c50652c6346d0e235bab0c1e5a` |
| `direct-build-recipe-a15.json` | 30,307 | `160f745b11dc01a554f00c558c858532a7c4a1a5e9529adfa70036455534798b` |
| `pure-fixtures-a15.json` | 15,816 | `a3dc7ffa70813915e629ee70dc53d663f62648509781dcd318a48f15d9e5d548` |
| canonical ROOT readback | 676,824 | `a92c7c3d0cf41f16ceb4860e6a0902f005f3fc14f54cb59e3e13bcaecd4cc2a5` |
| authenticated helper-launch receipt | 1,448 | `f36868756f183ff7c21e7a7b4e93c51107e4ebbc707f4a5cd564da8923802600` |

The package remains uncompiled, unstaged, and unexecuted. This review proves no
bootstrap, authorization, child lifecycle, producer output, native behavior,
media output, playback, hearing, or creative acceptance.
