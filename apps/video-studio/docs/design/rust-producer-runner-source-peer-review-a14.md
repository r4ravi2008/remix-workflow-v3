# Rust producer runner A14 source peer review

## Disposition

**Rejected before compilation.** The two A13 signal groups close in source.
One P2 direct-recipe integrity group remains.

A14 routes every production direct signal through one authority-aware seam.
An actual direct `ESRCH` now revokes local and retained direct-PID authority.
The source also preserves actual KILL observations across suppressed signals.
TERM evidence remains separate from KILL evidence.

The direct build recipe contains two incorrect SHA-256 literals. Its fixed
preflight therefore cannot validate the measured compiler and one A12 receipt.
Preserve A14 and repair only those literals in a separate successor.

This review is source-only, same-model-family, and nonblind. I read the A13
ROOT review, peer review, and rejection disposition. I read the complete
A13-to-A14 source and descriptive delta. I also checked ROOT's canonical A14
readback and externally authenticated helper-launch receipt.

I did not import, compile, test, bootstrap, authorize, stage, or execute this
package. I did not start a child, native framework, media tool, GPU, or Resolve.

## P2 finding

### P2.1: Two direct-recipe SHA-256 pins do not match their fixed files

`direct-build-recipe-a14.json:11` declares the compiler SHA-256 as:

```text
4f26ad57dcb9b12f9791317a1487e3e8d6ad803d4bd20fcdc65142a91e903d45
```

The fixed 414,280-byte `rustc` file measures as:

```text
4f26ad57dcb9b12f9791317a1387e3e8d6ad803d4bd20fcdc65142a91e903d45
```

`direct-build-recipe-a14.json:290` declares the 1,418-byte A12 authenticated
helper receipt SHA-256 as:

```text
dd641ad8b84462f9cc734dd8b5a149ec070121f2db3e596fb5885537c361db5e
```

The fixed receipt measures as:

```text
dd641ad8b84462f9cc734dd8b5a139ec070121f2db3e596fb5885537c361db5e
```

Both A13 recipe literals were correct. The A14 values changed the embedded
`13` sequence to `14`, although the fixed files did not change.

I checked all 21 SHA-256 scalar joins in the A14 recipe. The other 19 joins
match their current fixed files. The recipe paths, byte counts, and package
manifest external rows retain the correct fixed subjects.

This is a recipe-integrity failure. It does not reopen the A14 signal repair.
It blocks the declared direct build from becoming qualified evidence.

## A13 signal-group closure

### Direct-signal authority

`darwin_signal_owned_direct` checks authority before each direct syscall.
It returns `allowed_after=false` after an actual `ESRCH`.

The exceptional supervisor updates both its local policy and the retained
owner at `src/lib.rs:2540-2555`. No later interval can signal that direct PID.

Finite direct and retry KILL use the same seam at
`src/lib.rs:3012-3017` and `3039-3050`. Wait errors still revoke direct
authority before any further retry.

Pre-resume SIGCONT uses `darwin_signal_resume` at `src/lib.rs:3971-3980`.
Its attempted, delivered, and errno facts are captured before cleanup.
An `ESRCH` leaves `child.direct_signal_allowed=false` for finite and exceptional
cleanup.

The production library has no raw direct KILL or SIGCONT call outside
`darwin_signal_direct`. The remaining raw `kill` calls are the private group
probe and private group/direct primitives.

### Actual signal evidence

`record_group_kill`, `record_direct_kill`, and `record_retry_kill` ignore
unattempted observations. A post-latch default cannot erase an actual errno,
ESRCH bit, delivery result, or retry fact.

`record_cleanup` and `record_supervision` update last-attempt fields only when
the corresponding attempt count is nonzero. Supervision delivery facts use
monotonic OR operations.

`attempt_term` stores TERM errno and ESRCH only in termination and private TERM
fields. Resumed KILL and pipe-drain KILL alone update public KILL fields.

### Cumulative KILL delivery

`DarwinKillReapOutcome` retains cumulative group, direct, and retry delivery
bits. Finite delivery initializes those bits at `src/lib.rs:3067-3074`.

Exceptional delivery is merged before any last-observation replacement at
`src/lib.rs:3159-3179`. A later actual non-delivery can update the last errno.
It cannot change an earlier delivered KILL into `kill_sent=false`.

Early failure paths return `outcome.kill_sent()`. The resumed path ORs cleanup
delivery into `kill_delivered`. Terminal-group supervision also contributes its
cumulative delivery fields to the final process observation.

## Preserved ownership and schema checks

The A13 closed ownership rules remain present:

1. Failed resumed waits finish retained supervision before outcome selection.
2. Historical reap failure remains separate from final closure.
3. Group absence remains monotonic through finite cleanup, supervision, and
   `Drop`.
4. A consumed terminal status disables direct signalling.
5. Region causes and initiating failure causes remain separate.

The public `ProcessObservation` field schedule is unchanged. SIGCONT errno and
TERM errno are private causal facts. The control schedule remains ten lifecycle
cases, fifteen focused cases, twenty-one pure cases, eleven launch variants,
and five review-reference variants.

No A14 compile or control result exists. These are source observations only.

## Frozen source receipt

I rehashed every source row and every external `(role,path)` row. I reproduced
both framed aggregates from their declared domains and encodings. Every row
byte count and SHA-256 matches. Source paths and external role-path pairs are
unique.

ROOT's canonical readback contains 556 stable inputs totaling 135,075,228
bytes. It records all nine identity fields before and after. ROOT's external
launch receipt records that the measured helper descriptor closed.

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| `source-manifest-a14.json` | 80,636 | `358fd33e4e48f82e42a8efa08ec303e729cb3094c4d9f17bebf191ea13c3e138` |
| 15 source rows | 454,745 | `a246d35097580e25ad9f2a1504505128e250dfafb1e2f59e1c779ce6b3962e73` |
| 130 external `(role,path)` rows | 12,276,933 | `18aa89ec0190bd8c7e49374bfb28c8cfc00799fd779cdee1b409e07f68b4cd42` |
| `src/lib.rs` | 200,612 | `1451e727e7cd4c8a60264d7d63b119414aec91b21fcbbc3be7642b8033ba37c9` |
| `src/pure.rs` | 7,187 | `cc79345d6a994eeb860814aa84ca220f6a6f471ad6f9c28b864ee44742f47f7a` |
| `src/a14_focused_controls.rs` | 67,411 | `7164c3817cb71899fc30195b4432134b8cead5c0757890dad40bcd2f27e5e544` |
| `src/a14_launch_controls.rs` | 21,491 | `4b8f945a36fbf8ef2a5a13b4733bdc93e1fd99cd8e64b6485e701b57fcb01b98` |
| `direct-build-recipe-a14.json` | 28,159 | `92f5033324ac3439d3b1ffccc02b319a034d8682315e5040a54a52f861ae23d1` |
| canonical ROOT readback | 651,864 | `5d4b2ccc7851c2d731fb16abc648ca3a6a8d03c7971e51bddff5c7e75ad45244` |
| external helper-launch receipt | 1,448 | `b54e3699ddebfc01696197dfcfc3565c08f7c0b0a0f2b292cdff606afb996956` |

The package remains uncompiled, unstaged, and unexecuted. This review proves no
bootstrap, authorization, child lifecycle, producer output, native behavior,
media output, playback, hearing, or creative acceptance.
