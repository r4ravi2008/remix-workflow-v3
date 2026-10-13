# Runner A15 orchestration A05: ROOT host-entry correction

ROOT rejects A05 before compiler execution for one P2 host-entry finding.
The earlier source-only ROOT review remains preserved. This later observed
host fact supersedes its suitability for an actual launch on this Mac.
Peer review remains pending. No gate, current decision, or build attempt exists.

## Observed blocker

The frozen capsule requires `/usr/bin/python3`, a matching `sys.executable`,
`sys.orig_argv`, and exactly six environment variables. The Apple entry is a
shim on this host. A read-only standard-library diagnostic observed actual
`sys.executable` `/Library/Developer/CommandLineTools/usr/bin/python3`,
Python 3.9.6, and no `sys.orig_argv`. The shim also adds CPATH, LIBRARY_PATH,
MANPATH, SDKROOT, and `__CF_USER_TEXT_ENCODING` to the prescribed environment.
A direct CLT argument probe raised AttributeError for `sys.orig_argv`.
Neither entry can satisfy the frozen capsule. This is P2 because the reviewed
compile operation cannot enter its caller on the actual target machine.

## Bounded replacement evidence

ROOT used the dependency tool to locate the bundled Python runtime. Its
canonical executable is
`/Users/aira/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3.12`.
ROOT held and measured 18,058,560 bytes, SHA
`4158f03e1bae2b759f25a1ba1fbdab8bfb7161eba4caf22e28f0915986625bbc`,
with all nine identity fields stable. The descriptor closed before launch.
A standard-library-only diagnostic observed Python 3.12.14, exact original
argv, exact executable path, isolated/nonoptimized/no-bytecode mode, and an
exact seven-variable environment. The seventh explicitly supplied variable
was `__CF_USER_TEXT_ENCODING=0x1F5:0x0:0x0`. CoreFoundation adds that variable
even when the shim is bypassed. An earlier Homebrew entry rewrote both the
original argv and executable path, so it was not selected.

The diagnostic PID and private process group 35156 were reaped and absent.
Saved proof `rust-producer-runner-a15-canonical-python-host-entry-diagnostic-a01.json`
is 4,265 bytes, SHA
`ed830612259dadca1fd930ef3ad60ad6987321aa7b0d5af24e040ae54e343e67`.
The proof also discloses the earlier failed CLT inspection.
This diagnostic does not attest loaded runtime identity.

## Narrow successor

Preserve A05 bytes. A separate A06 should bind the exact canonical interpreter,
its byte receipt, the verified seven-variable environment, exact argv, and
this correction. Native A15 source, four compiler commands, process ownership,
private schedules, output schemas, and native false flags remain unchanged.
Re-review only this launcher repair and its resulting receipts.

No candidate capsule, compiler caller, shared utility, retained supervisor,
compiler, control, producer, or native operation ran. Only read-only Python
host diagnostics ran. WATCHED, HEARD, creative and product acceptance remain
unverified.
