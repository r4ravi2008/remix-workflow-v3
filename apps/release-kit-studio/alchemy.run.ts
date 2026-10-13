import * as Alchemy from 'alchemy'
import * as Cloudflare from 'alchemy/Cloudflare'
import { localState } from 'alchemy/State'
import { Config, Effect } from 'effect'

import type { RenderObject } from './editor/render-object'

export default Alchemy.Stack(
  'ReleaseKitStudio',
  { providers: Cloudflare.providers(), state: localState() },
  Effect.gen(function* () {
    const database = yield* Cloudflare.D1.Database('StudioDatabase', {
      name: 'release-kit-studio-preview',
      primaryLocationHint: 'wnam',
      migrations: './migrations',
    })
    const media = yield* Cloudflare.R2.Bucket('StudioMedia', {
      name: 'release-kit-studio-preview-media',
      publicAccess: false,
      forceDestroy: false,
    })
    const editor = yield* Cloudflare.Worker('Editor', {
      name: 'release-kit-editor-preview',
      main: 'editor/worker.ts',
      dev: { port: 1339, strictPort: true },
      env: {
        STUDIO_DB: database,
        MEDIA: media,
        STUDIO_OPERATOR_TOKEN: Config.Redacted('STUDIO_OPERATOR_TOKEN'),
        RENDERER: Cloudflare.Container<RenderObject>('EditorRenderer', {
          context: './editor/engine',
          className: 'RenderObject',
          instanceType: 'standard-3',
          maxInstances: 1,
          instances: 0,
        }),
      },
    })
    const studio = yield* Cloudflare.Website.Foldkit('Studio', {
      name: 'release-kit-studio-preview',
      main: 'src/worker.ts',
      dev: { port: 1337, strictPort: true },
      env: {
        STUDIO_DB: database,
        MEDIA: media,
        STUDIO_OPERATOR_TOKEN: Config.Redacted('STUDIO_OPERATOR_TOKEN'),
        EDITOR: editor,
      },
      assets: {
        notFoundHandling: 'single-page-application',
        runWorkerFirst: true,
      },
      memo: {
        include: [
          'src/**',
          'public/**',
          'index.html',
          'vite.config.ts',
          'package.json',
          'bun.lock',
        ],
      },
    })
    return { url: studio.url, editorUrl: editor.url }
  }),
)
