import { Schema } from 'effect'

import type { WorkerConfig } from './config'

export interface OwnedJob {
  id: string
  lease: string
}
export class DispatchError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message)
  }
}
export const workerHeaders = (
  config: WorkerConfig,
  job?: OwnedJob,
): Record<string, string> => ({
  Authorization: `Bearer ${config.token}`,
  ...(job ? { 'X-Job-Lease': job.lease, 'X-Job-Id': job.id } : {}),
})
export const workerRequest = async (
  config: WorkerConfig,
  method: 'GET' | 'POST',
  path: string,
  body?: unknown,
  job?: OwnedJob,
  signal: AbortSignal = new AbortController().signal,
) => {
  const response = await fetch(new URL(path, config.baseUrl), {
    method,
    headers: {
      ...workerHeaders(config, job),
      'Content-Type': 'application/json',
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    signal: AbortSignal.any([signal, AbortSignal.timeout(20000)]),
  })
  const result: unknown = await response.json()
  if (!response.ok)
    throw new DispatchError(
      response.status,
      Schema.decodeUnknownSync(Schema.Struct({ error: Schema.String }))(result)
        .error,
    )
  return result
}
