# Darwin launch grounding peer review A01

## Disposition

The saved evidence is internally consistent for a bounded Darwin OS feasibility probe.
It supports the suspended `posix_spawn` and `libproc` observation route for `/usr/bin/true`.
It does not qualify Runner A06, a Rust producer, a loaded runtime, or native output.

No P1 evidence failure was found. Two implementation follow-ups remain outside this
feasibility disposition: Rust `libc` 0.2.190 does not expose every required Darwin
constant or observation struct, and the probe's held-descriptor byte check is limited.

## Evidence identity

The independent readback is `darwin-launch-grounding-a01/readback.json`, 11,114 bytes,
SHA-256 `437b0b2ff6475b7dd4c655b970df0deaaa5fa0b3aa77233fd671008a15c0dc38`.
The current file rehash matched that identity.

The four saved receipts are:

| Receipt | Bytes | SHA-256 |
| --- | ---: | --- |
| `darwin-descriptor-exec-probe-a01.json` | 1,468 | `3d98793d18851258a3a67ca660a226ae3980be45b17c4533825ab85d70b2d5a2` |
| `darwin-suspended-vnode-probe-a01.json` | 6,290 | `758f0e5ffe80263d03cd3449e1c522645adc23ece3f0e817b6811356e218ba94` |
| `darwin-suspended-vnode-probe-a02.json` | 6,464 | `7acbd092a35fd28600e5c0f4e45ba6b7b4afaca2eb0f65ee44ff4e1debcd871e` |
| `darwin-suspended-vnode-probe-a03.json` | 6,801 | `3a2c60ead6c31d66bdb3f82861deffb22a1ef57d873e81b55ba3830e8c14c9f9` |

The four snapshotted Python sources also rehashed to their readback rows:

| Source | Bytes | SHA-256 |
| --- | ---: | --- |
| `native_runner_process_a05.py` | 5,459 | `81d55fe104b310c6d046b3e1f0fef914e3085f88073d07e7014cb302a8241ccf` |
| `darwin_suspended_vnode_probe_a01.py` | 8,753 | `bead9d22df45445d68772db8bf5b929d195798067e0ed80a8f6da440f015bce7` |
| `darwin_suspended_vnode_probe_a02.py` | 10,120 | `f5ac95f4213ef658e55803a2e7394169db7d74faf5c444c1c9faf13685e4ff8b` |
| `darwin_suspended_vnode_probe_a03.py` | 10,640 | `2fa1bf1bf662e3b98ae8a1c6c63c098db6568efce1bf1b35fdd71abfb8e6301f` |

The nine measured input rows also rehashed exactly. They include the four receipts and:

- `MacOSX26.1.sdk/usr/include/unistd.h`, 31,226 bytes,
  `bc3df41b77bd9cf7c1e46bb562280d3ae11068f2e22180e1eae2125c158182ff`.
- `MacOSX26.1.sdk/usr/include/sys/spawn.h`, 3,492 bytes,
  `8e73a88c3f63dae77ebf831737942e82ee7c78a7af1446fdbb1ee7ac6804a7e4`.
- `MacOSX26.1.sdk/usr/include/sys/proc_info.h`, 31,262 bytes,
  `e427fa96b348537b21552b9de71e01039410bcad2cedee5584c5e5fddafd70fc`.
- `MacOSX26.1.sdk/usr/include/libproc.h`, 7,575 bytes,
  `246d87709fc6b9157ce5cf3c475656ac48e0e1ae8bbdc46cf45acd34294448cd`.
- `libc-0.2.190/src/unix/bsd/apple/mod.rs`, 198,124 bytes,
  `bb4cf053d10bba3cae21616cdf8b80e53ec8b0bcd6f4a9ab257c2c4d2379b8da`.

The readback records all three PIDs as reaped and currently absent. A fresh read-only
`ps` query also returned no rows for PIDs 98190, 98266, and 98333.

## SDK and ABI trace

The Python `ctypes` declarations match the pinned SDK layouts.

- `spawn.h:51-64` defines the opaque spawn attribute and file-action pointers and the
  `posix_spawn` argument shape.
- `spawn.h:72-81` declares `posix_spawn_file_actions_addfchdir`,
  `posix_spawn_file_actions_adddup2`, and their return type.
- `sys/spawn.h:60-62` defines `POSIX_SPAWN_START_SUSPENDED = 0x0080`,
  `POSIX_SPAWN_SETSID = 0x0400`, and `POSIX_SPAWN_CLOEXEC_DEFAULT = 0x4000`.
- `libproc.h:96-103` declares `proc_pidinfo` and `proc_pidpath`.
- `sys/proc_info.h:166-190` defines `proc_regioninfo` in the field order used by
  `Region`.
- `sys/proc_info.h:285-345` defines `vinfo_stat`, `vnode_info_path`,
  `proc_regionwithpathinfo`, and `proc_vnodepathinfo` in the field order used by
  `VStat`, `VPath`, `RegionPath`, and `CwdPath`.
- `sys/proc_info.h:716-749` assigns flavor 8 to `PROC_PIDREGIONPATHINFO`, flavor 9 to
  `PROC_PIDVNODEPATHINFO`, and 4,096 bytes to `PROC_PIDPATHINFO_MAXSIZE`.
- `sys/fcntl.h:113-153` confirms the `O_NONBLOCK`, `O_NOFOLLOW`, `O_DIRECTORY`, and
  `O_CLOEXEC` values used by the helper and probes.

The probe's asserted `ctypes` sizes are 136 bytes for `VStat`, 1,176 for `VPath`,
1,272 for `RegionPath`, and 2,352 for `CwdPath`. Those sizes follow the SDK's
1,024-byte `MAXPATHLEN` and the pinned `vinfo_stat` and `proc_regioninfo` layouts.

The call declarations are also consistent with the live Rust `libc` source:
`posix_spawnattr_t` and `posix_spawn_file_actions_t` are opaque pointers at
`mod.rs:48-49`; spawn functions and `c_short` flags are at `mod.rs:5058-5093`;
`addfchdir` is at `mod.rs:5150-5163`; and `proc_pidinfo` plus `proc_pidpath` are at
`mod.rs:5484-5505`. The Rust source defines `WIFSTOPPED` at `mod.rs:4630-4632`.

The future Rust seam must account for these binding gaps. `libc` 0.2.190's Apple
module does not define `POSIX_SPAWN_SETSID`, `PROC_PIDREGIONPATHINFO`, or
`PROC_PIDPATHINFO`, and it does not provide `proc_regionwithpathinfo`. A production
binding must pin local constants and `#[repr(C)]` structs to the saved SDK rows or use
another pinned binding. This is an implementation prerequisite, not a failure of the
Python feasibility evidence.

The SDK marks `posix_spawn_file_actions_addfchdir` as available from macOS 26.0.
The probe is therefore grounded on the saved MacOSX26.1 SDK. A lower deployment target
needs an explicitly reviewed compatibility route.

## Exact launch and observation sequence

The probes open the target with `O_RDONLY | O_NOFOLLOW | O_NONBLOCK | O_CLOEXEC`.
They open the working directory with `O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC`.
They duplicate `/dev/null` onto descriptors 0, 1, and 2.

They initialize opaque spawn attributes and set the three flags above. They add the
held directory through `posix_spawn_file_actions_addfchdir`, then call direct
`posix_spawn` with the pathname `/usr/bin/true`.

They poll `waitpid` with `WNOHANG | WUNTRACED` and require `os.WIFSTOPPED` before
reading the child. The child process group equals its PID, which is consistent with
the `SETSID` flag.

They query `proc_pidinfo` flavor 8 from address zero and then from each prior region
end. Each returned structure must have the expected size and a nonzero region size.
The source bounds the loop at 256 rows and requires forward, non-overflowing addresses.

They query the loaded executable selector through `proc_pidpath` with a 4,096-byte
buffer. The header separately names flavor 11 `PROC_PIDPATHINFO`; the probe calls the
dedicated `proc_pidpath` function. The path selector must equal the target pathname.
The refined probe then selects the executable region by path, selected file offset,
executable protection, and all six vnode fields.

They query flavor 9 for the child current directory. The saved predicate compares its
device and inode with the held directory descriptor. The receipt also records the
loaded directory path and its remaining vnode fields.

Only after these checks does A03 send `SIGCONT`. It polls for exit, requires return code
zero, and records reaping. Assertion failure enters the kill-and-reap path without
resuming the child, as demonstrated by A02.

## Independent result checks

The descriptor route failed before spawn with `EACCES` 13 for `/dev/fd/3`. The SDK
does not declare `fexecve` in `unistd.h`, so the saved direct-path replacement is the
available route in this evidence scope.

A01 established the suspended launch path and descriptor cwd anchor. It resumed PID
98190 and reaped return code zero. It used the same 256-row region bound.

A02 is a negative result. It observed `WIFSTOPPED`, then found
`loadedMainImageExactMatchCount: 0` because its offset-zero predicate rejected the
universal binary's ARM64 mapping. It recorded `AssertionError()`, sent cleanup SIGKILL,
recorded return code -9, did not resume the child, and reaped it. A02 must not be
counted as a passing launch proof.

A03 is the only refined positive result. Independent parsing of the current
`/usr/bin/true` header found FAT magic `0xcafebabe`, two slices, and the ARM64 slice
at offset 49,152. The saved A03 rows contain 13 regions with strictly increasing,
non-overlapping addresses.

The unique selected region is:

```text
path=/usr/bin/true
address=4295720960
sizeOfRegion=16384
protection=5
offset=49152
device=16777230
inode=1152921500312555706
mode=33261
size=84128
modified_ns=1758783812000000000
changed_ns=1758783812000000000
```

There are two `/usr/bin/true` rows, but exactly one satisfies the selected offset,
executable protection, pathname, and six-field identity predicate.

The saved target before and after records have identical 84,128-byte content hash
`1315b337a4740ed84543bbfd684ad0d6779e35eec6d84808bb909574839a3de1` and identical
device, inode, mode, size, modification time, and change time. A current read-only
hash and stat of `/usr/bin/true` match those records. The held cwd anchor is device
16,777,230 and inode 24,431,453, with the recorded project path. A03 observed one
selected main-image match, one matching cwd anchor, resumed, exited zero, and reaped.

## Bounded findings

The A03 executable-content check is path based. `measure(target)` hashes a newly opened
pathname and `fstat`s the held executable descriptor, but it does not hash bytes through
the held descriptor itself. The saved result is valid for this harmless canary and the
documented no-concurrent-mutation scope. A future production proof must either hash
through the held descriptor or state that stronger concurrent mutation protection is
outside the contract.

The A03 cwd acceptance predicate compares only device and inode. The receipt records
the loaded cwd path, mode, size, and timestamps, but those fields are not part of the
pass predicate. Future code must preserve this distinction instead of claiming a full
six-field cwd equality check.

The 256-region bound is explicit and the current 13-row scan terminated before the
bound. The receipt records the cap and rows but does not persist a separate zero-return
termination flag. A production implementation should report clean termination or fail
when the bound is exhausted, rather than treating a truncated scan as complete.

The refined FAT offset is a measured `/usr/bin/true` system-canary value. The actual
producer was only read as a thin ARM64 Mach-O header. No producer execution or general
FAT support was established, and the production seam may require offset zero for that
thin binary.

The probes do not attest dyld dependencies, post-resume output opens, cancellation
cleanup, or general in-place host mutation. They provide no loaded-runtime, native
media, GPU, Resolve, product, watched, heard, or creative acceptance.

## Scoped conclusion

The saved receipts and SDK bindings support the stated Darwin API feasibility seam.
The readback, current file hashes, selected mapping, content identity, stop state,
reaping, and A02 negative disposition are consistent. Runner A06 remains source-only,
and all product and creative acceptance flags remain false.
