# Swift A07 compiler-only check A01

Root ran three bounded commands through the observed swiftc path. Apple Swift 6.2.1 reported target arm64-apple-macosx26.0 with macOS SDK 26.1.

The producer and shared callback typecheck failed with language and Swift-imported SDK API errors. Root read the full retained diagnostics. Shared callback plus pure control typecheck passed with an empty log. Neither producer nor control executable was built or started.

All eleven source, helper, manifest, compiler-path, and SDK-settings identities matched before and after. The record is compiler-only and path-bound. It does not attest loaded compiler internals or native framework behavior.

The existing A07 source and independent review remain preserved. A source successor must repair the actual compiler errors and remaining P2 ownership/partial-file evidence findings. No native, product, hearing, watching, or creative acceptance follows.
