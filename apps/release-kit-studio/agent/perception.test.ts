// @vitest-environment node
import { Effect } from 'effect'
import { createHash } from 'node:crypto'
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, describe, expect, it } from 'vitest'

import { defaultProfile } from '../src/domain'
import { GPU, GPUError, type GPUObservationResult } from './gpu'
import { type ObservationIntent, audioQuestions } from './observation'
import { observationWindows, stageObservations } from './perception'
import { fileReceipt } from './transfer'

const directories: Array<string> = []
afterEach(async () => {
  await Promise.all(
    directories
      .splice(0)
      .map(path => rm(path, { recursive: true, force: true })),
  )
})
const fixture = async (failSecond = false) => {
  const root = await mkdtemp(join(tmpdir(), 'release-kit-perception-'))
  directories.push(root)
  const job = {
    id: '8f55a7a3-e2df-4239-ab5f-603ad55d070b',
    releaseId: '92a6e687-e9ec-4325-a767-f44a56c73d84',
    brief: {
      title: 'పల్ పల్',
      lyrics: 'ప్రతి నిమిషం',
      language: 'Telugu',
      audioName: 'canonical.wav',
      audioSha256: '',
      audioBytes: 0,
      audioDuration: 60,
      profile: defaultProfile,
    },
  }
  const source = join(root, job.id, 'canonical-audio')
  await mkdir(join(root, job.id), { recursive: true })
  await writeFile(source, 'source-bound test bytes')
  const measured = await fileReceipt(source)
  job.brief.audioSha256 = measured.sha256
  job.brief.audioBytes = measured.bytes
  const calls: Array<ObservationIntent> = []
  const receipts: Array<string> = []
  const unavailable = Effect.fail(
    new GPUError('Unexpected generation operation'),
  )
  const provider: typeof GPU.Service = {
    probe: unavailable,
    submit: () => unavailable,
    ensure: () => unavailable,
    status: () => unavailable,
    reconcile: () => unavailable,
    collect: () => unavailable,
    observe: observation =>
      Effect.tryPromise({
        try: async () => {
          calls.push(observation.intent)
          receipts.push(observation.localReceipt)
          const samples = Math.round(
            (observation.intent.endSeconds - observation.intent.startSeconds) *
              16000,
          )
          const frames = Math.ceil(samples / 160)
          const failed = failSecond && calls.length === 2
          const raw = {
            schemaVersion: 2,
            status: failed ? 'failed' : 'observed',
            request: observation.intent,
            source: { sha256: measured.sha256, bytes: measured.bytes },
            reviewer: {
              ...(observation.intent.audioBackend === 'qwen2.5-omni'
                ? {
                    model: 'Qwen/Qwen2.5-Omni-7B',
                    revision: 'ae9e1690543ffd5c0221dc27f79834d0294cba00',
                    quantization: 'nf4-text-bf16-audio-vision-thinker-only',
                  }
                : {
                    model: 'Qwen/Qwen2-Audio-7B-Instruct',
                    revision: '0a095220c30b7b31434169c3086508ef3ea5bf0a',
                    quantization: 'nf4-text-bf16-audio',
                  }),
              runnerSha256: 'b'.repeat(64),
              promptSha256: createHash('sha256')
                .update(JSON.stringify(audioQuestions))
                .digest('hex'),
            },
            decodedAudio: {
              sampleRate: 16000,
              samples,
              sha256: 'c'.repeat(64),
            },
            modelAudioInput: {
              featureShape: [
                1,
                128,
                observation.intent.audioBackend === 'qwen2.5-omni'
                  ? 30000
                  : 3000,
              ],
              attendedFrames: frames,
              audioTokens:
                Math.floor((Math.floor((frames - 1) / 2) + 1 - 2) / 2) + 1,
              featureSha256: 'd'.repeat(64),
            },
            observations: audioQuestions.map(question => ({
              question,
              response: 'Singing over a synth pattern.',
              usable: true,
              issues: [],
              semanticVerified: false,
            })),
            observationContractPassed: true,
            modelLoad: {
              thinkerOnly: true,
              missingKeys: 0,
              mismatchedKeys: 0,
              discardedAudioGenerationKeys: 12,
            },
            audioPerceptionComplete: !failed,
            semanticFindingsVerified: false,
            fullSongHeard: false,
            pilotApproved: false,
            humanAccepted: false,
          }
          await writeFile(observation.localReceipt, JSON.stringify(raw), {
            flag: 'wx',
            mode: 0o600,
          })
          if (failed) throw new GPUError('Model qualification failed')
          const result: GPUObservationResult = {
            provider: 'tailscale-herdr',
            executionDevice: 'cuda',
            localReceipt: observation.localReceipt,
            ...(await fileReceipt(observation.localReceipt)),
            inferenceSubmitted: true,
            semanticVerified: false,
          }
          return result
        },
        catch: error =>
          new GPUError(
            error instanceof Error ? error.message : 'Test model failure',
          ),
      }),
  }
  const config = {
    baseUrl: 'http://localhost:1337',
    token: 'test',
    workstationConfig: '/unused',
    localState: root,
    planRegistry: root,
  }
  const workstation = {
    machine: 'unused',
    pane: 'unused',
    sshAlias: 'unused',
    expectedTailscaleHost: 'unused',
    remoteRoot: 'unused',
    localState: 'unused',
  }
  return { config, workstation, job, calls, receipts, source, provider }
}

describe('held-job observation preparation', () => {
  it('keeps explicitly selected Omni windows separate from default backend evidence', async () => {
    const test = await fixture()
    const signal = new AbortController().signal
    const first = await stageObservations(
      test.config,
      test.workstation,
      test.job,
      'backend-r01',
      signal,
      test.provider,
    )
    const selected = {
      ...test.config,
      audioObservations: {
        attempt: 'backend-r02',
        backend: 'qwen2.5-omni' as const,
      },
    }
    const second = await stageObservations(
      selected,
      test.workstation,
      test.job,
      'backend-r02',
      signal,
      test.provider,
    )
    expect(first.fullSongHeard).toBe(false)
    expect(second.fullSongHeard).toBe(false)
    expect(second.automaticDirectionQualified).toBe(false)
    expect(
      test.calls.slice(3).every(row => row.audioBackend === 'qwen2.5-omni'),
    ).toBe(true)
    expect(first.windows.map(row => row.id)).not.toEqual(
      second.windows.map(row => row.id),
    )
    await expect(
      stageObservations(
        test.config,
        test.workstation,
        test.job,
        'backend-r02',
        signal,
        test.provider,
      ),
    ).rejects.toThrow()
    expect(test.calls).toHaveLength(6)
  })
  it('covers the complete song and reuses exact receipts without approving direction', async () => {
    const test = await fixture()
    const prepare = () =>
      stageObservations(
        test.config,
        test.workstation,
        test.job,
        'test-r01',
        new AbortController().signal,
        test.provider,
      )
    const first = await prepare()
    const second = await prepare()
    expect(first).toEqual(second)
    expect(test.calls.map(row => [row.startSeconds, row.endSeconds])).toEqual([
      [0, 28],
      [26, 54],
      [52, 60],
    ])
    expect(first.modelAudioCoverageComplete).toBe(true)
    expect(first.automaticDirectionQualified).toBe(false)
    expect(first.fullSongHeard).toBe(false)
    expect(first.pilotApproved).toBe(false)
    const receipt = test.receipts[0]
    if (!receipt) throw new Error('Expected a test receipt')
    const tampered = JSON.parse(await readFile(receipt, 'utf8'))
    tampered.fullSongHeard = true
    await writeFile(receipt, JSON.stringify(tampered))
    await expect(prepare()).rejects.toThrow()
    expect(test.calls).toHaveLength(3)
  })

  it('preserves failed windows and stops repeat polls before another inference', async () => {
    const test = await fixture(true)
    const prepare = () =>
      stageObservations(
        test.config,
        test.workstation,
        test.job,
        'test-r01',
        new AbortController().signal,
        test.provider,
      )
    await expect(prepare()).rejects.toThrow('qualification failed')
    await expect(prepare()).rejects.toThrow('qualification failed')
    expect(test.calls).toHaveLength(2)
  })

  it('rejects changed canonical bytes and invalid coverage before inference', async () => {
    const test = await fixture()
    await writeFile(test.source, 'changed source')
    await expect(
      stageObservations(
        test.config,
        test.workstation,
        test.job,
        'test-r01',
        new AbortController().signal,
        test.provider,
      ),
    ).rejects.toThrow('frozen brief')
    expect(test.calls).toEqual([])
    for (const duration of [0, 901, Infinity])
      expect(() => observationWindows(duration)).toThrow()
    const windows = observationWindows(239.68)
    expect(windows).toHaveLength(10)
    expect(windows.at(-1)?.endSeconds).toBe(239.68)
  })
})
