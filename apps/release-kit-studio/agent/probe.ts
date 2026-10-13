import { Effect, Schema } from 'effect'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { join } from 'node:path'

import { GPU, WorkstationConfig, tailscaleGPU } from './gpu'

const path = process.argv[2]
if (!path) throw new Error('Pass the trusted workstation configuration path.')
const config = Schema.decodeUnknownSync(WorkstationConfig)(
  JSON.parse(await readFile(path, 'utf8')),
)
await mkdir(config.localState, { recursive: true, mode: 0o700 })
const result = await Effect.runPromise(
  Effect.gen(function* () {
    const gpu = yield* GPU
    return yield* gpu.probe
  }).pipe(Effect.provideService(GPU, tailscaleGPU(config))),
)
await writeFile(
  join(config.localState, 'gpu-probe.json'),
  JSON.stringify(result, null, 2),
  { mode: 0o600 },
)
console.log(JSON.stringify({ provider: 'tailscale-herdr', ...result }))
