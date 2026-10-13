import { Effect, Schema } from 'effect'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { join } from 'node:path'

import { GPU, type GPUAttempt, WorkstationConfig, tailscaleGPU } from './gpu'

const configPath = process.argv[2]
if (!configPath)
  throw new Error('Pass the trusted workstation configuration path.')
const config = Schema.decodeUnknownSync(WorkstationConfig)(
  JSON.parse(await readFile(configPath, 'utf8')),
)
await mkdir(config.localState, { recursive: true, mode: 0o700 })
const run =
  '/home/r4ravi2008/projects/remix-workflow-v3/runs/pal-pal-release-kit-01a0ff81-r01'
const comfy =
  '/home/r4ravi2008/projects/remix-workflow-v3/tools/ltx-video-generator/comfyui'
const attempt: GPUAttempt = {
  id: 'P01-a02',
  ledger: `${run}/jobs`,
  workflow: `${run}/P01-a02-workflow.json`,
  inputs: `${run}/P01-a02-inputs.json`,
  bindings: `${run}/P01-a02-bindings.json`,
  inputRoot: `${comfy}/input`,
  outputRoot: `${comfy}/output`,
  archive: `${run}/originals`,
  outputNode: '28',
}
const receipt = await Effect.runPromise(
  Effect.gen(function* () {
    const gpu = yield* GPU
    const status = yield* gpu.status(attempt)
    const original = yield* gpu.collect(
      attempt,
      join(config.localState, 'P01-a02.mp4'),
    )
    return {
      status,
      original,
      bulkGenerationAccepted: false,
      newInferenceSubmitted: false,
    }
  }).pipe(Effect.provideService(GPU, tailscaleGPU(config))),
)
await writeFile(
  'docs/gpu-provider-receipt.json',
  JSON.stringify(receipt, null, 2) + '\n',
)
console.log(JSON.stringify(receipt))
