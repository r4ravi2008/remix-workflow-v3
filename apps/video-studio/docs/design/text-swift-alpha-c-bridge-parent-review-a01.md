# Swift A08 alpha-context bridge parent review

Root rejected the A08 alpha-context binding before execution. A08 remains preserved, unbuilt, and unexecuted.

The A08 source used a bodyless Swift declaration with `_silgen_name` to call `CGBitmapContextCreate`. The [official Swift attribute reference](https://github.com/swiftlang/swift/blob/main/docs/ReferenceGuides/UnderscoredAttributes.md) specifies Swift calling conventions for this attribute. The declaration does not establish the required C ABI.

Root requested a separately preserved successor with a real imported C header. A09 now uses `alpha-context-shim.h`, SDK C types, explicit `NULL`, and `CF_RETURNS_RETAINED`. Root read the full header and A08-to-A09 source and contract changes. The A09 manifest binds that header.

This review closes only the source mechanism choice. Swift import behavior, ownership, linking, and native behavior remain unverified. Independent A09 review has also identified setter-import, failed-prefix evidence, and owner-formula defects. A09 is not released for native execution.
