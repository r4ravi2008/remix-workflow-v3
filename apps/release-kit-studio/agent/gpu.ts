import { Context, Effect, Schema } from 'effect'
import { execFile } from 'node:child_process'
import {
  chmod,
  link,
  mkdir,
  readFile,
  rename,
  unlink,
  writeFile,
} from 'node:fs/promises'
import { dirname, join } from 'node:path'

import {
  type GPUObservation,
  ObservationManifest,
  observationKey,
  validateObservationIntent,
  validateObservationReceipt,
} from './observation'
import { fileReceipt } from './transfer'
import {
  readTransport,
  releaseTransport,
  reserveTransport,
  transportPath,
} from './transport'

export const WorkstationConfig = Schema.Struct({
  machine: Schema.String,
  pane: Schema.String,
  sshAlias: Schema.String,
  expectedTailscaleHost: Schema.String,
  remoteRoot: Schema.String,
  localState: Schema.String,
})
export type WorkstationConfig = typeof WorkstationConfig.Type
export const GPUProbe = Schema.Struct({
  managed: Schema.Boolean,
  hostname: Schema.String,
  gpu: Schema.String,
  queueIdle: Schema.Boolean,
  lease: Schema.Unknown,
  modelsReady: Schema.Boolean,
})
export type GPUProbe = typeof GPUProbe.Type
export interface GPUAttempt {
  id: string
  ledger: string
  workflow: string
  inputs: string
  bindings: string
  inputRoot: string
  outputRoot: string
  archive: string
  outputNode: string
}
export class GPUError extends Error {}
export interface GPUObservationResult {
  provider: 'tailscale-herdr'
  executionDevice: 'cpu' | 'cuda'
  localReceipt: string
  sha256: string
  bytes: number
  inferenceSubmitted: boolean
  semanticVerified: false
}
export class GPU extends Context.Service<
  GPU,
  {
    probe: Effect.Effect<GPUProbe, GPUError>
    submit: (attempt: GPUAttempt) => Effect.Effect<unknown, GPUError>
    ensure: (attempt: GPUAttempt) => Effect.Effect<unknown, GPUError>
    status: (attempt: GPUAttempt) => Effect.Effect<unknown, GPUError>
    reconcile: (attempt: GPUAttempt) => Effect.Effect<unknown, GPUError>
    observe: (
      observation: GPUObservation,
    ) => Effect.Effect<GPUObservationResult, GPUError>
    collect: (
      attempt: GPUAttempt,
      localOutput: string,
    ) => Effect.Effect<unknown, GPUError>
  }
>()('release-kit/GPU') {}
const Reply = Schema.Struct({
  ok: Schema.Boolean,
  result: Schema.Unknown,
  error: Schema.NullOr(Schema.String),
})
const Collection = Schema.Struct({
  archive: Schema.String,
  sha256: Schema.String,
  bytes: Schema.Number,
  full_video_decode: Schema.Boolean,
})
const shellQuote = (value: string) => `'${value.replaceAll("'", "'\\''")}'`
export const command = (
  binary: string,
  args: Array<string>,
  timeout = 300000,
  signal: AbortSignal = new AbortController().signal,
) =>
  new Promise<string>((resolve, reject) => {
    execFile(
      binary,
      args,
      { timeout, maxBuffer: 2 * 1024 * 1024, signal },
      (error, stdout, stderr) => {
        if (error)
          reject(new GPUError(`${binary} failed: ${stderr.slice(0, 500)}`))
        else resolve(stdout)
      },
    )
  })
export const tailscaleGPU = (config: WorkstationConfig): typeof GPU.Service => {
  const verifyRoute = async (signal: AbortSignal) => {
    const ssh = await command('ssh', ['-G', config.sshAlias], 300000, signal)
    const host = ssh
      .split('\n')
      .find(line => line.startsWith('hostname '))
      ?.slice(9)
    if (host !== config.expectedTailscaleHost || !host.endsWith('.ts.net'))
      throw new GPUError(
        'SSH alias does not resolve to the configured Tailscale workstation.',
      )
  }
  const invoke = async (
    action: string,
    attempt: GPUAttempt | null,
    signal: AbortSignal,
    observation?: GPUObservation,
  ) => {
    const id = crypto.randomUUID()
    const localRequest = join(config.localState, `${id}.request.json`)
    const localResponse = join(config.localState, `${id}.response.json`)
    const remoteRequest = `${config.remoteRoot}/requests/${id}.request.json`
    const remoteResponse = `${config.remoteRoot}/requests/${id}.response.json`
    const transport = await reserveTransport(
      transportPath(config.expectedTailscaleHost, config.pane),
      {
        id,
        action,
        attemptId: observation?.intent.id ?? attempt?.id ?? null,
        request: localRequest,
        response: localResponse,
        remoteResponse,
      },
    )
    try {
      await verifyRoute(signal)
      const info = JSON.parse(
        await command(
          'herdr',
          [
            '--machine',
            config.machine,
            'pane',
            'process-info',
            '--pane',
            config.pane,
          ],
          300000,
          signal,
        ),
      )
      const processes = Schema.decodeUnknownSync(
        Schema.Struct({
          result: Schema.Struct({
            process_info: Schema.Struct({
              foreground_processes: Schema.Array(
                Schema.Struct({ name: Schema.String }),
              ),
            }),
          }),
        }),
      )(info)
      if (
        !processes.result.process_info.foreground_processes.every(process =>
          ['zsh', 'bash', 'fish'].includes(process.name),
        )
      )
        throw new GPUError(
          'The configured production pane is occupied; preserve its process.',
        )
      const stagedSource = `${config.remoteRoot}/requests/${id}.audio`
      if (observation) {
        await command(
          'scp',
          [observation.localSource, `${config.sshAlias}:${stagedSource}`],
          300000,
          signal,
        )
        const measured = await fileReceipt(observation.localSource, signal)
        if (
          measured.sha256 !== observation.intent.sourceSha256 ||
          measured.bytes !== observation.intent.sourceBytes
        )
          throw new GPUError(
            'Canonical audio changed during workstation staging.',
          )
      }
      await writeFile(
        localRequest,
        JSON.stringify({
          action,
          attempt,
          response: remoteResponse,
          ...(observation
            ? { observation: { intent: observation.intent, stagedSource } }
            : {}),
        }),
        { mode: 0o600, flag: 'wx' },
      )
      await command(
        'scp',
        [localRequest, `${config.sshAlias}:${remoteRequest}`],
        300000,
        signal,
      )
      signal.throwIfAborted()
      await transport.dispatched()
      await command(
        'herdr',
        [
          '--machine',
          config.machine,
          'pane',
          'run',
          config.pane,
          `python3 ${shellQuote(`${config.remoteRoot}/remote_gpu.py`)} ${shellQuote(remoteRequest)} > ${shellQuote(`${remoteRequest}.log`)} 2>&1`,
        ],
        300000,
        signal,
      )
      const response = await Effect.runPromise(
        Effect.gen(function* () {
          const poll: Effect.Effect<string, GPUError> = Effect.suspend(() =>
            Effect.tryPromise({
              try: async () => {
                await command(
                  'scp',
                  [`${config.sshAlias}:${remoteResponse}`, localResponse],
                  300000,
                  signal,
                )
                return readFile(localResponse, 'utf8')
              },
              catch: error =>
                new GPUError(
                  error instanceof Error
                    ? error.message
                    : 'Response not available',
                ),
            }).pipe(
              Effect.catch(() =>
                Effect.sleep('1 second').pipe(Effect.flatMap(() => poll)),
              ),
            ),
          )
          return yield* poll.pipe(
            Effect.timeout('6 minutes'),
            Effect.mapError(
              () =>
                new GPUError(
                  'Provider response is uncertain. Inspect the saved request and remote attempt before retrying.',
                ),
            ),
          )
        }),
        { signal },
      )
      const reply = Schema.decodeUnknownSync(Reply)(JSON.parse(response))
      transport.terminal()
      if (!reply.ok)
        throw new GPUError(
          reply.error ??
            'Workstation operation failed; inspect its preserved ledger.',
        )
      return reply.result
    } finally {
      await transport.close()
    }
  }
  const effect = <A>(operation: (signal: AbortSignal) => Promise<A>) =>
    Effect.tryPromise({
      try: operation,
      catch: error =>
        new GPUError(
          error instanceof Error ? error.message : 'GPU operation failed',
        ),
    })
  return {
    probe: effect(async signal =>
      Schema.decodeUnknownSync(GPUProbe)(await invoke('probe', null, signal)),
    ),
    submit: attempt => effect(signal => invoke('submit', attempt, signal)),
    ensure: attempt => effect(signal => invoke('ensure', attempt, signal)),
    status: attempt => effect(signal => invoke('status', attempt, signal)),
    reconcile: attempt =>
      effect(signal => invoke('reconcile', attempt, signal)),
    observe: observation =>
      effect(async signal => {
        validateObservationIntent(observation.intent)
        const source = await fileReceipt(observation.localSource, signal)
        if (
          source.sha256 !== observation.intent.sourceSha256 ||
          source.bytes !== observation.intent.sourceBytes
        )
          throw new GPUError(
            'Observation source differs from the frozen master.',
          )
        const manifest = Schema.decodeUnknownSync(ObservationManifest)(
          await invoke('observe', null, signal, observation),
        )
        if (
          observationKey(manifest.intent) !==
            observationKey(observation.intent) ||
          manifest.receipt.path !==
            `${config.remoteRoot}/director/operations/${observation.intent.id}/receipt.json` ||
          !/^[a-f0-9]{64}$/u.test(manifest.receipt.sha256) ||
          !Number.isSafeInteger(manifest.receipt.bytes) ||
          manifest.receipt.bytes <= 0 ||
          manifest.receipt.bytes > 2 * 1024 * 1024
        )
          throw new GPUError(
            'Model evidence differs from its exact provider operation.',
          )
        await mkdir(dirname(observation.localReceipt), {
          recursive: true,
          mode: 0o700,
        })
        const temporary = `${observation.localReceipt}.incoming-${crypto.randomUUID()}`
        try {
          await command(
            'scp',
            [`${config.sshAlias}:${manifest.receipt.path}`, temporary],
            300000,
            signal,
          )
          const measured = await fileReceipt(temporary, signal)
          if (
            measured.sha256 !== manifest.receipt.sha256 ||
            measured.bytes !== manifest.receipt.bytes
          )
            throw new GPUError(
              'Transferred model evidence differs from its provider checksum.',
            )
          await chmod(temporary, 0o600)
          signal.throwIfAborted()
          await link(temporary, observation.localReceipt).catch(async error => {
            if (error.code !== 'EEXIST') throw error
            const existing = await fileReceipt(observation.localReceipt, signal)
            if (
              existing.sha256 !== measured.sha256 ||
              existing.bytes !== measured.bytes
            )
              throw new GPUError(
                'Preserved observation evidence changed; do not overwrite it.',
              )
          })
          validateObservationReceipt(
            observation.intent,
            JSON.parse(await readFile(observation.localReceipt, 'utf8')),
          )
          return {
            provider: 'tailscale-herdr',
            executionDevice:
              observation.intent.kind === 'lyric-alignment'
                ? (observation.intent.alignmentDevice ?? 'cuda')
                : 'cuda',
            localReceipt: observation.localReceipt,
            ...measured,
            inferenceSubmitted: manifest.inferenceSubmitted,
            semanticVerified: false,
          }
        } finally {
          await unlink(temporary).catch(error => {
            if (error.code !== 'ENOENT') throw error
          })
        }
      }),
    collect: (attempt, localOutput) =>
      effect(async signal => {
        const result = await invoke('collect', attempt, signal)
        const collection = Schema.decodeUnknownSync(Collection)(result)
        if (!collection.full_video_decode)
          throw new GPUError('The original has not passed a full decode.')
        const temporary = `${localOutput}.incoming-${crypto.randomUUID()}`
        try {
          await command(
            'scp',
            [`${config.sshAlias}:${collection.archive}`, temporary],
            300000,
            signal,
          )
          const file = await fileReceipt(temporary, signal)
          if (
            file.sha256 !== collection.sha256 ||
            file.bytes !== collection.bytes
          )
            throw new GPUError(
              'Transferred original differs from the workstation receipt.',
            )
          signal.throwIfAborted()
          await rename(temporary, localOutput)
          return {
            provider: 'tailscale-herdr',
            collection: result,
            localOutput,
            sha256: file.sha256,
            bytes: file.bytes,
          }
        } finally {
          await unlink(temporary).catch(error => {
            if (error.code !== 'ENOENT') throw error
          })
        }
      }),
  }
}

export const reconcileTransport = async (config: WorkstationConfig) => {
  const path = transportPath(config.expectedTailscaleHost, config.pane)
  const saved = await readTransport(path)
  const prefix = `${config.remoteRoot}/requests/`
  if (saved.remoteResponse !== `${prefix}${saved.id}.response.json`)
    throw new GPUError(
      'The saved response is outside the configured provider root.',
    )
  const ssh = await command('ssh', ['-G', config.sshAlias])
  const hostname = ssh
    .split('\n')
    .find(line => line.startsWith('hostname '))
    ?.slice(9)
  if (
    hostname !== config.expectedTailscaleHost ||
    !hostname.endsWith('.ts.net')
  )
    throw new GPUError(
      'The saved request route does not match the configured Tailscale host.',
    )
  const response = join(
    config.localState,
    `${saved.id}.reconciled.response.json`,
  )
  await command('scp', [`${config.sshAlias}:${saved.remoteResponse}`, response])
  const reply = Schema.decodeUnknownSync(Reply)(
    JSON.parse(await readFile(response, 'utf8')),
  )
  await releaseTransport(path, saved.id)
  return {
    state: 'terminal-response-reconciled',
    requestId: saved.id,
    action: saved.action,
    attemptId: saved.attemptId,
    remoteSucceeded: reply.ok,
    inferenceSubmitted: false,
  }
}
