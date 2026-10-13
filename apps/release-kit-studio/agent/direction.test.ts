// @vitest-environment node
import { Schema } from 'effect'
import {
  mkdir,
  mkdtemp,
  readFile,
  readdir,
  rm,
  stat,
  writeFile,
} from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { afterEach, describe, expect, it } from 'vitest'

import { defaultProfile, outputs } from '../src/domain'
import { DirectionPacket, stageDirection } from './direction'
import { command } from './gpu'
import { briefFingerprint } from './plan'
import { fileReceipt } from './transfer'

const directories: Array<string> = []
afterEach(async () => {
  await Promise.all(
    directories
      .splice(0)
      .map(path => rm(path, { recursive: true, force: true })),
  )
})
const fixture = async (format: 'wav' | 'mp3' = 'wav', silent = false) => {
  const directory = await mkdtemp(join(tmpdir(), 'release-kit-direction-'))
  directories.push(directory)
  const root = join(directory, 'job-one')
  await mkdir(root)
  const source = join(root, 'canonical-audio')
  await command('ffmpeg', [
    '-v',
    'error',
    '-f',
    'lavfi',
    '-i',
    silent
      ? 'anullsrc=r=48000:cl=stereo'
      : 'aevalsrc=0.2*sin(2*PI*100*t)|-0.2*sin(2*PI*100*t):s=48000',
    '-t',
    '2',
    '-f',
    format,
    source,
  ])
  const receipt = await fileReceipt(source)
  return {
    config: {
      baseUrl: 'http://localhost:1337',
      token: 'test-only',
      workstationConfig: '',
      localState: directory,
      planRegistry: join(directory, 'plans'),
    },
    job: {
      id: 'job-one',
      releaseId: 'release-one',
      brief: {
        title: 'పల్ పల్',
        lyrics: '[పల్లవి]\nప్రతి నిమిషం\n',
        language: 'Telugu',
        audioName: `song.${format}`,
        audioSha256: receipt.sha256,
        audioBytes: receipt.bytes,
        audioDuration: 2,
        profile: defaultProfile,
      },
    },
    source,
    signal: new AbortController().signal,
  }
}

describe('automatic direction preparation', () => {
  it('keeps the frozen brief and exact lyrics, measures opposed stereo channels, and never approves production', async () => {
    const test = await fixture()
    const result = await stageDirection(test.config, test.job, test.signal)
    const packet = Schema.decodeUnknownSync(DirectionPacket)(
      JSON.parse(await readFile(result.packetPath, 'utf8')),
    )
    const analysis = JSON.parse(
      await readFile(
        join(dirname(result.packetPath), 'audio-analysis.json'),
        'utf8',
      ),
    )
    expect(packet.brief).toEqual(test.job.brief)
    expect(packet.lyricLines.join('\n')).toBe(test.job.brief.lyrics)
    expect(packet.briefSha256).toBe(briefFingerprint(test.job.brief))
    expect(packet.deliverables.map(value => value.id)).toEqual(
      outputs.map(value => value.id),
    )
    expect(Object.values(packet.review).every(value => value === false)).toBe(
      true,
    )
    expect(
      analysis.rms.reduce((sum: number, value: number) => sum + value ** 2, 0) /
        analysis.rms.length,
    ).toBeCloseTo(0.02, 5)
    expect(analysis.frameCount).toBe(48)
    expect((await stat(result.packetPath)).mode & 0o777).toBe(0o600)
    const before = await stat(result.packetPath)
    expect(await stageDirection(test.config, test.job, test.signal)).toEqual(
      result,
    )
    expect((await stat(result.packetPath)).mtimeMs).toBe(before.mtimeMs)
    expect(
      (await readdir(dirname(dirname(result.packetPath)))).filter(name =>
        name.startsWith('.direction-incoming-'),
      ),
    ).toEqual([])
    await expect(stat(test.config.planRegistry)).rejects.toThrow('ENOENT')
  })

  it('analyzes uploaded MP3 bytes directly while preserving the source hash', async () => {
    const test = await fixture('mp3')
    const before = await fileReceipt(test.source)
    const result = await stageDirection(test.config, test.job, test.signal)
    expect(result.frameCount).toBe(48)
    expect(await fileReceipt(test.source)).toEqual(before)
  })

  it('keeps silence free of invented beats and rejects a changed source', async () => {
    const test = await fixture('wav', true)
    const result = await stageDirection(test.config, test.job, test.signal)
    const analysis = JSON.parse(
      await readFile(
        join(dirname(result.packetPath), 'audio-analysis.json'),
        'utf8',
      ),
    )
    expect(analysis.proposedBeatGrid).toBeNull()
    expect(analysis.rms.every((value: number) => value === 0)).toBe(true)
    await writeFile(test.source, 'changed')
    await expect(
      stageDirection(test.config, test.job, test.signal),
    ).rejects.toThrow('immutable release brief')
  })

  it('rejects a corrupt prepared analysis instead of silently replacing its evidence', async () => {
    const test = await fixture()
    const result = await stageDirection(test.config, test.job, test.signal)
    await writeFile(
      join(dirname(result.packetPath), 'audio-analysis.json'),
      '{}',
    )
    await expect(
      stageDirection(test.config, test.job, test.signal),
    ).rejects.toThrow('verified analysis')
  })

  it('rejects an uploaded media manifest and leaves no prepared packet', async () => {
    const test = await fixture()
    await writeFile(
      test.source,
      'ffconcat version 1.0\nfile /private/other-audio.wav\n',
    )
    const receipt = await fileReceipt(test.source)
    const job = {
      ...test.job,
      brief: {
        ...test.job.brief,
        audioSha256: receipt.sha256,
        audioBytes: receipt.bytes,
      },
    }
    await expect(stageDirection(test.config, job, test.signal)).rejects.toThrow(
      'python3 failed',
    )
    expect(await readdir(dirname(test.source))).toEqual(['canonical-audio'])
  })
})
