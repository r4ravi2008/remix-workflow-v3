import { DurableObject } from 'cloudflare:workers'

import { type EditorEnv, editorStore } from './api'
import { RenderCoordinator } from './render-coordinator'

export class RenderObject extends DurableObject<EditorEnv> {
  coordinator = new RenderCoordinator(this.ctx, this.env, editorStore(this.env))
  fetch(request: Request) {
    return this.coordinator.fetch(request)
  }
  alarm() {
    return this.coordinator.alarm()
  }
}
