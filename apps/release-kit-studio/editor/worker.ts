import { type EditorEnv, editorApi } from './api'
import { productionEditorApi } from './production-access'

export { RenderObject } from './render-object'

export default {
  fetch(request: Request, env: EditorEnv) {
    if (new URL(request.url).pathname.startsWith('/v1/production/'))
      return productionEditorApi(request, env)
    return editorApi(request, env)
  },
}
