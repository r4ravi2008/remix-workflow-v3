# Rust producer runner A03 source peer review

## Disposition

The scoped source review is complete. I found no new P1 or P2 production-runner
finding. A03 closes the six actionable A02 finding groups within static source
scope. Compilation, process execution, and native evidence remain unverified.

This is a same-family, nonblind review. I read the complete A02-to-A03 source
delta, the affected lifecycle and inventory paths, `src/pure.rs`, `src/main.rs`,
the README, contract, output schema, fixtures, Cargo metadata, and manifest.

## Manifest and source identity

The frozen package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a03`

The manifest is `source-manifest-a03.json`, SHA-256
`f6bac0ffc32d4cff36331d65f82ba6948b7c9df8dd80e8dfe1516c6b614a2719`.
Its documented aggregate recomputes to
`61921924a64ecb75436a6e2dd54ba97dcf81ccbf8a31e08a261fcc071ec1b73d`.
All eight rows match their current bytes, totaling 91,971 bytes.

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| `Cargo.toml` | 490 | `5e811262d8189de224d6068fed03407ef5055a9450573918a5fafc588bf79e41` |
| `README.md` | 1,574 | `9692cac9ffeb6b027a53f61f8576f878d9ee5e4c2bb93e528fe5239c75a9a72a` |
| `output-schema-a03.md` | 3,079 | `6b58afb586c7bbbb0ebadc1cb941450f216ba3443e537b53c2dabfee2aae5767` |
| `pure-fixtures-a03.json` | 6,548 | `31c732c04960a02d4194167b18907a9a8e36f06dc907a19d9d41e31968770a9f` |
| `runner-contract-a03.md` | 10,975 | `933b7e8da4ccd83ff1f313ad583ad0db5172c87f027d03202a9d4c184e7b96b1` |
| `src/lib.rs` | 65,240 | `48c1f14ed5e61f5f5e46430b51ae26789adef4c761367adc8b06702b1712ba2f` |
| `src/main.rs` | 96 | `edc6278622d43e9e7a598222033accf8172f2b2ef4d09f02930c23b84a2aa3d7` |
| `src/pure.rs` | 3,969 | `b76f4edd50ca097e7aadb458c2325b02b874f9fdb1162a3f887c1c1f08c4ed1e` |

## Repair verification

1. **Compile and `Result`/`Option` conversions.** Exit status extraction uses
   inherent `code()` and Unix `signal()` methods at `src/lib.rs:1090-1091` and
   `:1403-1404`. The preflight directory result is converted with
   `.as_ref().ok().map(Vec::is_empty)` at `:459-460`. Descriptor-relative stat
   results are converted before `is_none_or` at `:910` and `:929`. These paths
   no longer apply `Option` methods to `Result` values.

2. **Bounded regular-file opens.** `open_path_readonly` uses `O_NONBLOCK`,
   `O_CLOEXEC`, and `O_NOFOLLOW` at `src/lib.rs:1625-1629`.
   `open_regular_path_readonly` rejects non-regular descriptors before reads at
   `:1632-1641`. `open_file_at` applies the same nonblocking type check at
   `:1656-1669`. A FIFO replacement therefore does not block in the bounded
   authority or output read path.

3. **Capture-log descriptor ownership.** The runner creates `producer.log` as
   `O_RDWR|O_CREAT|O_EXCL` and retains the `File` at `src/lib.rs:518-520`.
   The child loop writes through that same reference. Closure observes the
   held descriptor at `:556-564`; `observe_held_file` compares its complete
   descriptor identity with the descriptor-relative pathname at `:779-793`.
   The final report cannot silently hash a replacement opened by name.

4. **Regular-file identity joins.** `same_stable_identity` compares device,
   inode, mode, size, modification time, and change time at
   `src/lib.rs:1579-1594`. Authority reads use it after bounded reads at
   `:761-769`. Output files use it after descriptor reads and final
   descriptor-relative stats at `:927-930`. Directory anchors intentionally
   remain device/inode checks at `:600-608` and `:907-911`, because ordinary
   runner writes change directory metadata.

5. **TERM delivery facts.** `TerminationFacts` separates request, attempt, and
   delivery at `src/lib.rs:229-234`. `attempt_term` preserves `ESRCH` as an
   attempted but undelivered signal at `:1485-1492`. Cancellation, timeout, and
   overflow call it at `:1224-1248` and `:1329-1344`. The loop does not retry an
   attempted TERM. The report copies all three facts at `:1405-1416`.

6. **Bounded in-group cleanup.** Direct-child reap uses the one-second bounded
   helper at `src/lib.rs:1036-1056`. After a direct-child status or bounded reap,
   the one-second pipe-drain deadline is recorded at `:1287` and `:1381-1383`.
   An open pipe at the deadline sends group `SIGKILL`, records actual delivery,
   closes the logical drain state, and forces `ReapFailure` at `:1388-1401`.
   The child result carries the causal error at `:1418-1419`, so an unclosed
   pipe cannot produce the pending completion. Cleanup paths retain bounded
   group/direct KILL results through `cleanup_child` at `:1064-1072`.

The terminal schema and contract match these source paths. The private
qualification loader still returns `MissingAcceptance`, so the public CLI
launches no child and creates no accepted result. The 21 JSON fixture cases are
declarations for the separately owned controls; they are not runtime evidence.

## Limits

This review does not establish compilation, formatting, subprocess cleanup in
execution, signal delivery on macOS, codec or media behavior, native output,
audio, GPU, Resolve, product integration, WATCHED, HEARD, or creative
acceptance. The bounded reaper may remain detached after its observation
deadline, and the contract makes no claim to reap descendants that escape the
recorded process group.

