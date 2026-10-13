# Payload A06 parent source review

A06 remains rejected before build. The parent read the complete A05-to-A06 module and runner changes and all three contract deltas. Invalid UTF-8 and final sync error fields are repaired. Partial hashing now uses bounded read_at on the owned file descriptor.

All four output creators still open files with write(true) only. A read_at call through that descriptor must fail with EBADF on Unix. The new evidence path therefore cannot compute the intended partial hash. All four creators also call open(output), consuming the PathBuf, before stream_json borrows &output. This is a source-level Rust move error. The package has not been compiled.

A separately preserved A07 must open the exclusive file for reading and writing and pass &output to open. A small pure IO control should use the actual shared creator and stream_json. It should force a bounded partial-output failure and require exact byte/hash evidence. It should also verify that descriptor-based hashing stays attached to the written file after pathname replacement.

No payload compiler, measurement executable, project, media, native framework, GPU, or Resolve operation ran. A01 through A06 remain preserved. The parent review covers changed source against the prior fully read A03/A04/A05 baseline. Product payload admission remains pending actual capacity measurements and checked aggregate derivation.
