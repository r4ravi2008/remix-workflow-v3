import { Schema } from 'effect'
import { readFile } from 'node:fs/promises'

import { AudioBackend } from './observation'

export const WorkerConfig = Schema.Struct({
  baseUrl: Schema.String,
  token: Schema.String,
  workstationConfig: Schema.String,
  localState: Schema.String,
  planRegistry: Schema.String,
  audioObservations: Schema.optional(
    Schema.Struct({
      attempt: Schema.String,
      backend: Schema.optional(AudioBackend),
    }),
  ),
})
export type WorkerConfig = typeof WorkerConfig.Type
export const loadWorkerConfig = async (path: string): Promise<WorkerConfig> => {
  const config = await readFile(path, 'utf8').then(value => {
    try {
      return Schema.decodeUnknownSync(WorkerConfig)(JSON.parse(value))
    } catch {
      throw new Error(
        'Worker configuration is incomplete or invalid; credentials have been withheld.',
      )
    }
  })
  const url = new URL(config.baseUrl)
  if (
    url.protocol !== 'https:' &&
    !['localhost', '127.0.0.1'].includes(url.hostname)
  )
    throw new Error('Worker dispatch requires HTTPS outside localhost.')
  return config
}
