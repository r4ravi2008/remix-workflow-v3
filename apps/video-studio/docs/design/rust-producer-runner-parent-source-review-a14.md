# Rust producer runner A14 parent source review

ROOT rejects the frozen A14 package before compilation: zero P1 and one P2 finding.
The P2 concerns two incorrect recipe receipt pins.
The two A13 process and signal evidence groups are repaired in source.
Runtime behavior remains untested.

## Measured subject

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| A14 source manifest | 80,636 | `358fd33e4e48f82e42a8efa08ec303e729cb3094c4d9f17bebf191ea13c3e138` |
| Actual ROOT source proof | 651,864 | `5d4b2ccc7851c2d731fb16abc648ca3a6a8d03c7971e51bddff5c7e75ad45244` |
| Actual external helper authentication | 1,448 | `b54e3699ddebfc01696197dfcfc3565c08f7c0b0a0f2b292cdff606afb996956` |
| A14 read-only helper | 14,766 | `100a1015dbed786addb65ff0b4581199a1ed51435d0abe2a4899940ab01872f1` |

ROOT executed only the read-only helper once from externally authenticated held source bytes.
ROOT separately authenticated the fixed manifest through a held descriptor before helper execution.
The helper descriptor closed before external authentication publication.
The external receipt uses the explicit A14 schema and records that successful closure.

The proof matches 556 files and 135,075,228 bytes.
All nine before/after identity fields remain stable.
The source aggregate has 15 rows and 454,745 bytes: `a246d35097580e25ad9f2a1504505128e250dfafb1e2f59e1c779ce6b3962e73`.
The external aggregate has 130 rows and 12,276,933 bytes: `18aa89ec0190bd8c7e49374bfb28c8cfc00799fd779cdee1b409e07f68b4cd42`.
The measured closure contains 27 literal import edges and 23 Rust source files.

ROOT read the complete A13-to-A14 library delta: 22,020 bytes and 402 lines.
ROOT read the complete remaining source and descriptive delta: 48,177 bytes and 813 lines.
ROOT previously read the predecessor source chain and reread the changed production signal and cleanup paths.
After review, ROOT independently reopened all 556 measured files through bounded, nonblocking, no-follow held descriptors.
Every byte pin and all nine identity fields still matched the actual proof.
The proof itself remained unchanged.

## P2: renaming changed two recipe digests

`direct-build-recipe-a14.json` contains two altered 64-character receipt values.
The A13-to-A14 replacement changed an embedded `a13` substring inside each digest.
These digests identify preserved bytes and must not change during package renaming.

The actual 414,280-byte rustc file hashes to `4f26ad57dcb9b12f9791317a1387e3e8d6ad803d4bd20fcdc65142a91e903d45`.
`toolchain.rustc_sha256` instead records `4f26ad57dcb9b12f9791317a1487e3e8d6ad803d4bd20fcdc65142a91e903d45`.

The actual 1,418-byte A12 helper authentication receipt hashes to `dd641ad8b84462f9cc734dd8b5a139ec070121f2db3e596fb5885537c361db5e`.
`source_closure.a12_authenticated_source_helper_receipt_sha256` instead records `dd641ad8b84462f9cc734dd8b5a149ec070121f2db3e596fb5885537c361db5e`.
The A14 manifest's A12 external row correctly records the actual digest.

ROOT checked nineteen current recipe path/digest joins.
Only these two joins failed.
The fixed compile preflight cannot pass the incorrect rustc receipt.
The preserved receipt declaration also disagrees with its manifest row.
Repair both scalars in a separate successor and protect complete digest tokens during any label adaptation.
Do not edit the frozen A14 package or its actual proof.

## Closed process and signal groups in source

Every production direct signal uses `darwin_signal_owned_direct`.
An actual direct `ESRCH` immediately revokes authority before later cleanup attempts.
Exceptional KILL, finite KILL retries, and SIGCONT share this behavior.
The SIGCONT observation captures errno before cleanup syscalls.
No raw production direct signal bypass remains.

Group, direct, and retry fact writers ignore unattempted observations.
Suppressed signals cannot erase earlier actual errno, retry, delivery, or supervision facts.
TERM observations remain separate from public KILL fields.
Cumulative cleanup delivery bits preserve an earlier delivered KILL after a later actual non-delivery.
Latest actual errno remains separate from that cumulative result.

The A13 terminal ownership, monotonic group absence, region cause, initiating failure, and metadata repairs remain present.
The authorization operation, implementation, public schema, error codes, and private schedules remain unchanged.
The schedules retain ten lifecycle cases, fifteen focused cases, twenty-one pure cases, eleven launch cases, and five review variants.

## Limits

Peer source review remains pending at this ROOT disposition.
ROOT imported no process utility, supervisor, capsule, runner, or project module.
No Rust compiler, lifecycle control, bootstrap, authorization, producer, native framework, media, GPU, or Resolve operation ran.
Native, product, watched, heard, and creative acceptance remain false.
