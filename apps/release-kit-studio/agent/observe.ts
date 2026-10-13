import { Effect, Schema } from 'effect'
import { mkdir, readFile } from 'node:fs/promises'

import { jsonSchema } from '../editor/json-schema'
import { GPU, WorkstationConfig, tailscaleGPU } from './gpu'
import { ObservationIntent } from './observation'

const Observation = Schema.Struct({
  intent: ObservationIntent,
  localSource: Schema.String,
  localReceipt: Schema.String,
})
const [configPath, inputPath] = process.argv.slice(2)
if (configPath === 'schema') {
  console.log(JSON.stringify(jsonSchema(Observation), null, 2))
} else {
  if (!configPath || !inputPath)
    throw new Error(
      'Pass the trusted workstation configuration and observation JSON paths, or use schema.',
    )
  const config = Schema.decodeUnknownSync(WorkstationConfig, {
    onExcessProperty: 'error',
  })(JSON.parse(await readFile(configPath, 'utf8')))
  const content = await readFile(inputPath, 'utf8')
  if (Buffer.byteLength(content) > 65536)
    throw new Error('Observation input exceeds 64 KiB.')
  const observation = Schema.decodeUnknownSync(Observation, {
    onExcessProperty: 'error',
  })(JSON.parse(content))
  await mkdir(config.localState, { recursive: true, mode: 0o700 })
  const result = await Effect.runPromise(
    Effect.gen(function* () {
      const gpu = yield* GPU
      return yield* gpu.observe(observation)
    }).pipe(Effect.provideService(GPU, tailscaleGPU(config))),
  )
  console.log(
    JSON.stringify({
      ...result,
      fullSongHeard: false,
      pilotApproved: false,
      humanAccepted: false,
    }),
  )
}
