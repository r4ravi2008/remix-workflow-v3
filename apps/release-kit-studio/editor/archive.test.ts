// @vitest-environment node
import { Schema } from 'effect'
import { afterEach, describe, expect, it } from 'vitest'

import { canonicalJson } from '../src/canonical'
import { makeEditorApi } from './api'
import { prepareKit } from './archive'
import { FrameDiagnostics } from './artifact'
import { kitFixture, nodeArchiveHash } from './kit-testing'
import { digest } from './store'
import { streamZip } from './zip'

const fixtures: Array<Awaited<ReturnType<typeof kitFixture>>> = []
const fixture = async () => {
  const test = await kitFixture()
  fixtures.push(test)
  const api = makeEditorApi(
    { MEDIA: test.media, STUDIO_OPERATOR_TOKEN: 'operator'.repeat(8) },
    test.store,
  )
  const request = (
    path: string,
    method = 'GET',
    token = 'private-one',
    body?: unknown,
  ) =>
    api(
      new Request(`https://editor.test${path}`, {
        method,
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        ...(body ? { body: JSON.stringify(body) } : {}),
      }),
    )
  return { ...test, request }
}
afterEach(() => fixtures.splice(0).forEach(test => test.database.close()))
describe('tenant-scoped kit archives', () => {
  it('exports source-bound diagnostics and rejects metadata that hides a finding', async () => {
    const test = await fixture()
    const frameDiagnostics = {
      schemaVersion: 1,
      method: 'all-frame-reduced-rgb-luma/v1',
      width: 32,
      height: 18,
      timebaseFps: 24,
      sampledFrames: 48,
      completeFrameCoverage: true,
      motionExpected: true,
      thresholds: {
        blackMeanLuma: 3,
        blackPeakLuma: 6,
        flatLumaSpread: 2,
        staticMeanAbsoluteDelta: 0.2,
        staticMinimumFrames: 12,
        abruptMeanAbsoluteDelta: 60,
      },
      counts: {
        nearBlackFrames: 48,
        flatFrames: 48,
        nearStaticFrames: 48,
        nearBlackRanges: 1,
        flatRanges: 1,
        nearStaticRanges: 1,
        abruptChanges: 0,
        unplannedFindingRanges: 3,
      },
      omittedFindings: {
        nearBlackRanges: 0,
        flatRanges: 0,
        nearStaticRanges: 0,
        abruptChanges: 0,
      },
      nearBlackRanges: [
        {
          startFrame: 0,
          endFrame: 48,
          expected: false,
          context: 'no-declared-exemption',
          maximumMeanLuma: 0,
          maximumPeakLuma: 0,
        },
      ],
      flatRanges: [
        {
          startFrame: 0,
          endFrame: 48,
          expected: false,
          context: 'no-declared-exemption',
          maximumLumaSpread: 0,
        },
      ],
      nearStaticRanges: [
        {
          startFrame: 0,
          endFrame: 48,
          expected: false,
          context: 'no-declared-exemption',
          maximumMeanAbsoluteDelta: 0,
        },
      ],
      abruptChanges: [],
      joinMeasurements: [],
      reviewSuggested: true,
      semanticReviewed: false,
    }
    const outputs = test.receipt.outputs.map(output =>
      output.id === 'film' ? { ...output, frameDiagnostics } : output,
    )
    const stored = canonicalJson({
      projectSha256: test.receipt.projectSha256,
      outputs,
    })
    test.objects.set(test.prefix + 'receipt.json', stored)
    const receipt = {
      ...test.receipt,
      outputs,
      receiptSha256: await digest(stored),
    }
    const job = { ...test.job, receipt_json: JSON.stringify(receipt) }
    const kit = await prepareKit(test.store, test.media, 'one', job)
    const entry = kit.entries.find(item => item.name === 'manifest.json')!
    const manifest = Schema.decodeUnknownSync(
      Schema.Struct({
        files: Schema.Array(
          Schema.Struct({
            id: Schema.String,
            frameDiagnostics: Schema.optional(FrameDiagnostics),
          }),
        ),
        motionReviewed: Schema.Literal(false),
        heard: Schema.Literal(false),
        creativelyAccepted: Schema.Literal(false),
      }),
    )(await new Response(await entry.open()).json())
    expect(
      manifest.files.find(item => item.id === 'film')?.frameDiagnostics,
    ).toEqual(frameDiagnostics)
    expect(manifest).toMatchObject({
      motionReviewed: false,
      heard: false,
      creativelyAccepted: false,
    })
    const changed = {
      ...receipt,
      outputs: outputs.map(output =>
        output.id === 'film'
          ? {
              ...output,
              frameDiagnostics: { ...frameDiagnostics, reviewSuggested: false },
            }
          : output,
      ),
    }
    await expect(
      prepareKit(test.store, test.media, 'one', {
        ...job,
        receipt_json: JSON.stringify(changed),
      }),
    ).rejects.toMatchObject({ code: 'receipt_binding' })
  })
  it('locates and streams eight immutable entries without scheduling a render or claiming review', async () => {
    const test = await fixture()
    const kit = await prepareKit(test.store, test.media, 'one', test.job)
    expect(kit.descriptor.entries).toHaveLength(8)
    const first = await new Response(
      streamZip(kit.entries, nodeArchiveHash),
    ).arrayBuffer()
    const secondKit = await prepareKit(test.store, test.media, 'one', test.job)
    expect(
      await new Response(
        streamZip(secondKit.entries, nodeArchiveHash),
      ).arrayBuffer(),
    ).toEqual(first)
    expect(first.byteLength).toBe(kit.descriptor.bytes)
    const manifestEntry = kit.entries.find(
      item => item.name === 'manifest.json',
    )!
    expect(await new Response(await manifestEntry.open()).json()).toMatchObject(
      {
        jobId: test.job.id,
        releaseId: 'release-one',
        motionReviewed: false,
        heard: false,
        creativelyAccepted: false,
      },
    )
    const head = await test.request(`/v1/jobs/${test.job.id}/archive`, 'HEAD')
    expect(head.status).toBe(200)
    expect(head.body).toBeNull()
    expect(head.headers.get('Content-Length')).toBe(
      String(kit.descriptor.bytes),
    )
    const located = await test.request(
      '/v1/tools/kit.locate',
      'POST',
      'private-one',
      { jobId: test.job.id },
    )
    expect(await located.json()).toEqual(kit.descriptor)
    expect(await test.store.job('one', test.job.id)).toEqual(test.job)
  })
  it('rejects foreign tenants and wrong release bindings before accessing private media', async () => {
    const test = await fixture()
    for (const [path, token] of [
      [`/v1/jobs/${test.job.id}/archive`, 'private-two'],
      [`/v1/jobs/${test.job.id}/archive?releaseId=release-two`, 'private-one'],
    ]) {
      expect((await test.request(path!, 'GET', token)).status).toBe(404)
      expect(test.reads).toEqual([])
    }
  })
  it('rejects incomplete kits, changed stored receipts and missing objects', async () => {
    const test = await fixture()
    await expect(
      prepareKit(test.store, test.media, 'one', {
        ...test.job,
        state: 'rendering',
      }),
    ).rejects.toMatchObject({ code: 'kit_not_ready' })
    await expect(
      prepareKit(test.store, test.media, 'one', {
        ...test.job,
        receipt_json: JSON.stringify({
          ...test.receipt,
          outputs: test.receipt.outputs.slice(0, 5),
        }),
      }),
    ).rejects.toMatchObject({ code: 'kit_binding' })
    test.objects.set(test.prefix + 'receipt.json', 'changed')
    await expect(
      prepareKit(test.store, test.media, 'one', test.job),
    ).rejects.toMatchObject({ code: 'receipt_integrity' })
    test.objects.set(
      test.prefix + 'receipt.json',
      canonicalJson({
        projectSha256: test.receipt.projectSha256,
        outputs: test.receipt.outputs,
      }),
    )
    test.objects.delete(test.prefix + 'film')
    await expect(
      prepareKit(test.store, test.media, 'one', test.job),
    ).rejects.toMatchObject({ code: 'stored_output_missing' })
  })
  it('detects source changes between preflight and delivery', async () => {
    const test = await fixture()
    const kit = await prepareKit(test.store, test.media, 'one', test.job)
    test.objects.set(test.prefix + 'film', 'x'.repeat('synthetic-film'.length))
    await expect(
      new Response(streamZip(kit.entries, nodeArchiveHash)).arrayBuffer(),
    ).rejects.toThrow('changed during archive delivery')
  })
  it('rejects metadata drift from the stored receipt and the exact frozen brief', async () => {
    const test = await fixture()
    const changed = {
      ...test.receipt,
      outputs: test.receipt.outputs.map(item => ({
        ...item,
        sha256: 'f'.repeat(64),
      })),
    }
    await expect(
      prepareKit(test.store, test.media, 'one', {
        ...test.job,
        receipt_json: JSON.stringify(changed),
      }),
    ).rejects.toMatchObject({ code: 'receipt_binding' })
    await test.sql.run('UPDATE releases SET brief_json=? WHERE id=?', [
      JSON.stringify({
        title: 'Changed',
        lyrics: test.project.lyrics,
        language: 'Telugu',
        audioName: 'song.wav',
        audioSha256: 'a'.repeat(64),
        audioDuration: 2,
        audioBytes: 100,
        profile: (await import('../src/domain')).defaultProfile,
      }),
      'release-one',
    ])
    await expect(
      prepareKit(test.store, test.media, 'one', test.job),
    ).rejects.toMatchObject({ code: 'source_binding' })
  })
})
