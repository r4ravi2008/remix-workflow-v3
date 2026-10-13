import { Schema } from 'effect'
import { readFile, writeFile } from 'node:fs/promises'

import { editorRequest } from './editor-request'

const [inputPath, outputPath] = process.argv.slice(2)
if (!inputPath || !outputPath)
  throw new Error('Pass the private local canary input and result paths.')
const input = Schema.decodeUnknownSync(
  Schema.Struct({ token: Schema.String, jobId: Schema.String }),
)(JSON.parse(await readFile(inputPath, 'utf8')))
const config = {
  baseUrl: 'http://localhost:1339',
  token: input.token,
  workstationConfig: '',
  localState: '',
  planRegistry: '',
}
const actualFetch = globalThis.fetch
const statuses: Array<number> = []
globalThis.fetch = async (...args) => {
  const response = await actualFetch(...args)
  statuses.push(response.status)
  return response
}
const result = await editorRequest(
  config,
  { id: 'local-capacity-canary', lease: 'diagnostic-only' },
  '/v1',
  'tools/artifact.verify',
  { jobId: input.jobId, outputId: 'film' },
  AbortSignal.timeout(600000),
)
await writeFile(outputPath, JSON.stringify({ statuses, result }), {
  flag: 'wx',
  mode: 0o600,
})
console.log(JSON.stringify({ statuses, verificationCompleted: true }))
