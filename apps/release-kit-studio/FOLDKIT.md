# Foldkit conventions

Foldkit owns this file.
`create-foldkit-app` writes it, and package upgrades replace it.
Project-specific instructions belong in `AGENTS.md`.

This file applies to the optional TypeScript application under `src/`, `agent/`, and `editor/`.
It does not apply to the standalone Rust editor under `native-editor/`.
Use [native `AGENTS.md`](native-editor/AGENTS.md) for native editor work.

The application pins Foldkit `0.165.0`, Effect `4.0.0`, and Alchemy `2.0.0-beta.80`.
Read `package.json` and `bun.lock` before you rely on a package API.

## Check the references before you change code

Use the installed package and its source as the API authority.
Written guidance can become stale.

If `./repos/foldkit` exists, read it directly:

- `repos/foldkit/examples/` contains runnable examples.
- `repos/foldkit/packages/foldkit/src/` contains framework source.
- `repos/foldkit/packages/typing-game/client/src/` and `repos/foldkit/packages/website/src/` contain production applications.

Treat `repos/foldkit/` as read-only reference.
Import from the `foldkit` npm package.

If the subtree is absent, check the applicable `AGENTS.md`.
If that file sets `subtree_prompted: false`, offer to vendor the repository at the installed package version:

```sh
git subtree add --prefix=repos/foldkit https://github.com/foldkit/foldkit.git "foldkit@$(node -p "require('./node_modules/foldkit/package.json').version")" --squash
```

For a canary package, use the full source commit named by its version.
Do not use `main` as the reference for a released package.

After a package upgrade, update the subtree first.
Then pull the release tag that matches the installed package and replace this complete file with the installed template:

```sh
git subtree pull --prefix=repos/foldkit https://github.com/foldkit/foldkit.git "foldkit@$(node -p "require('./node_modules/foldkit/package.json').version")" --squash
```

Use `repos/foldkit/packages/create-foldkit-app/templates/base/FOLDKIT.md` as the template.
Do not merge old rules into the new template.

## Keep the Foldkit model typed

Foldkit is coupled to Effect.
Model fields use Effect `Schema` types.
Use full names such as `Message` and `withReturnType`.
Declare all variants together with `defineMessageUnion()`, `defineTaggedUnion()`, or `defineRouteUnion()`.
Keep constructors on their union, such as `Message.ClickedIncrement()`.
Use `taggedStruct()` only for recursive unions that cannot be declared together.

Messages describe facts.
Commands describe effects.
Do not use `NoOp`.
Name each command result after its command.

Use discriminated unions for state.
Use `Option` for absent model values.
Use `modifyFields()` for immutable model updates.
Do not spread a model or call `Object.assign`.

## Match messages exhaustively

Declare the message union and its type alias together:

```ts
const Message = defineMessageUnion({
  ClickedDecrement: {},
  ClickedIncrement: {},
  ClickedReset: {},
})
type Message = typeof Message.Type
```

Use the union namespace to construct and match messages:

```ts
const update = (model: Model, message: Message) =>
  Message.match<Update.Return<Model, Message>>(message, {
    ClickedDecrement: () => ({
      model: modifyFields(model, { count: count => count - 1 }),
    }),
    ClickedIncrement: () => ({
      model: modifyFields(model, { count: count => count + 1 }),
    }),
    ClickedReset: () => ({
      model: modifyFields(model, { count: () => 0 }),
    }),
  })
```

Use `Message.match` for every message variant.
Use Effect `Match` for partial matches, fallbacks, and other tagged unions.
Do not use `switch` for message cases.

If the OutMessage is known when you construct a result, include it in `{ model, commands, outMessage }`.
Use `Update.withOutMessage` to attach an OutMessage to a current result:

```ts
const editorSave = Update.combine(model, [writeDraft, clearErrors])
return pipe(editorSave, Update.withOutMessage(outMessage))
Update.withOutMessage({ model, commands }, outMessage)
```

## Keep the runtime boot in `entry.ts`

Keep pure definitions in `src/main.ts` and runtime boot in `src/entry.ts`.
The definitions include `Model`, `Message`, `init`, `update`, `view`, and Commands.
The boot calls `Runtime.makeApplication` and `Runtime.run`.
`index.html` references `src/entry.ts`.
Do not call `Runtime.run` from `src/main.ts`.

The current application follows this boundary.
`src/main.ts` owns the model, messages, commands, update function, and init function.
`src/view.ts` owns the typed HTML view.
`src/entry.ts` starts the runtime.

Split a module only when it has a distinct reason to change and a clear name.
Extract `Message` when a Command module needs its constructors.
Keep a Command beside the update function that returns it unless its resource has a separate owner.

## Define Commands as named values

Define each Command with `Command.define(name, { args, messages, execute })`.
Omit `args` when the Command takes no arguments.
Assign each definition to a PascalCase constant.
Use the command name for its effect.

Catch command errors and return a failure message.
Use Effect modules for time, randomness, UUIDs, and delays.
Use the `Dom` module for focus, scroll, modal, and scroll-lock operations.
Do not call `document.querySelector`, `setTimeout`, `Date.now()`, or `Math.random()` directly.

## Forward child results only when required

Pass child Commands through the parent with the full result:

```ts
const commands = Command.mapMessages(
  [Feed.RefreshSummary(), Feed.RefreshTimeline()],
  toGotFeedMessage,
)
```

Add `toParentOutMessage` only when a child OutMessage must reach the current Submodel parent.
For partial pass-through, match every child variant.
Return `undefined` for variants that stop at the current Submodel.
Omit `toParentOutMessage` when every variant stops locally.
Never write `toParentOutMessage: () => undefined`.

When several child results can produce one parent OutMessage, add `resolveOutMessage`.
The callback runs after local folds complete and receives the named OutMessages and final Model.
Combine the information when both results matter.

Use `Update.foldChildInit` for one child init.
Use `Update.foldChildInits` for several child inits.
Use `Update.foldChild` for a child update with input.
Use `Update.foldChildStep` for a child helper that receives only its model.
Use `Update.combine` for two or more sequential Steps.

## Keep view and test boundaries clear

Every view receives `h`, the typed HTML builder, as its last parameter.
Use the builder methods, such as `h.div` and `h.OnClick`.

Use `h.empty` for an empty branch.
Use a stable model ID for a mapped key.
Do not key a branch or use an array index as a key.

Use `story` for pure update tests and `scene` for rendered view tests:

```ts
import { Command, given, message, model, story } from 'foldkit/story'
```

Keep `story.test.ts` beside the update code.
Keep `scene.test.ts` beside the view or at the root for cross-page flows.
Use accessible locators for scene tests.

The project includes `@foldkit/devtools-mcp`.
Use its model and message history when the dev server runs and the browser shows the app.
