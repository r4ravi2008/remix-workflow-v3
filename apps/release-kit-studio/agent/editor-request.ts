import { Schema } from 'effect'

import type { WorkerConfig } from './config'
import { type OwnedJob, workerHeaders } from './connection'

const pause = (milliseconds: number, signal: AbortSignal) =>
  new Promise<void>((resolve, reject) => {
    const abort = () => {
      clearTimeout(timer)
      reject(signal.reason)
    }
    const timer = setTimeout(() => {
      signal.removeEventListener('abort', abort)
      resolve()
    }, milliseconds)
    signal.addEventListener('abort', abort, { once: true })
    if (signal.aborted) abort()
  })
const Busy = Schema.Struct({ code: Schema.Literal('render_capacity_busy') })
export const editorFetch = (input: RequestInfo | URL, init: RequestInit) => {
  const request: RequestInit & { timeout: false } = {
    ...init,
    timeout: false,
  }
  return fetch(input, request)
}
export const editorOperationTimeout = (path: string, fallback: number) =>
  /(?:^|\/)tools\/(?:artifact\.(?:verify|preview)|render\.(?:status|reconcile))$/u.test(
    path,
  )
    ? 600000
    : fallback
export const editorRequest = async (
  config: WorkerConfig,
  job: OwnedJob,
  root: string,
  path: string,
  value: unknown,
  signal: AbortSignal,
) => {
  for (;;) {
    signal.throwIfAborted()
    const response = await editorFetch(new URL(`${root}/${path}`, config.baseUrl), {
      method: 'POST',
      headers: {
        ...workerHeaders(config, job),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(value),
      redirect: 'error',
      signal: AbortSignal.any([
        signal,
        AbortSignal.timeout(editorOperationTimeout(path, 120000)),
      ]),
    })
    const result: unknown = await response.json()
    if (response.ok) return result
    if (
      ['tools/artifact.verify', 'tools/artifact.preview'].includes(path) &&
      response.status === 503 &&
      Schema.is(Busy)(result)
    ) {
      const seconds = Number(response.headers.get('Retry-After') ?? 5)
      await pause(
        (Number.isFinite(seconds) ? Math.max(1, Math.min(30, seconds)) : 5) *
          1000,
        signal,
      )
      continue
    }
    throw new Error(
      `Cloudflare editor request failed (${response.status}): ${JSON.stringify(result)}`,
    )
  }
}
