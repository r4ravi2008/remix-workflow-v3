// @vitest-environment node
import { afterEach, describe, expect, it, vi } from 'vitest'

import { editorRequest } from './editor-request'

const config = {
  baseUrl: 'https://studio.test',
  token: 'private-test',
  workstationConfig: '/unused',
  localState: '/unused',
  planRegistry: '/unused',
}
const job = { id: 'owned-job', lease: 'lease-test' }
afterEach(() => {
  vi.unstubAllGlobals()
  vi.useRealTimers()
})
describe('editor capacity backoff', () => {
  it.each(['tools/artifact.verify', 'tools/artifact.preview'])(
    'retries only the same explicit busy %s and keeps its lease',
    async path => {
      vi.useFakeTimers()
      const fetch = vi
        .fn()
        .mockResolvedValueOnce(
          Response.json(
            { code: 'render_capacity_busy' },
            { status: 503, headers: { 'Retry-After': '2' } },
          ),
        )
        .mockResolvedValueOnce(Response.json({ sha256: 'a'.repeat(64) }))
      vi.stubGlobal('fetch', fetch)
      const input = { jobId: 'editor-job', outputId: 'film' }
      const result = editorRequest(
        config,
        job,
        '/assigned-editor',
        path,
        input,
        new AbortController().signal,
      )
      await vi.advanceTimersByTimeAsync(2000)
      expect(await result).toEqual({ sha256: 'a'.repeat(64) })
      expect(fetch).toHaveBeenCalledTimes(2)
      expect(fetch.mock.calls[0]?.[0]).toEqual(fetch.mock.calls[1]?.[0])
      expect(fetch.mock.calls[0]?.[1].body).toEqual(
        fetch.mock.calls[1]?.[1].body,
      )
      expect(fetch.mock.calls[0]?.[1].headers).toEqual(
        fetch.mock.calls[1]?.[1].headers,
      )
      expect(fetch.mock.calls[0]?.[1].headers['X-Job-Lease']).toBe(job.lease)
    },
  )
  it('does not repeat render starts or unknown failed verification outcomes', async () => {
    const fetch = vi
      .fn()
      .mockImplementation(async () =>
        Response.json({ code: 'render_capacity_busy' }, { status: 503 }),
      )
    vi.stubGlobal('fetch', fetch)
    await expect(
      editorRequest(
        config,
        job,
        '/assigned-editor',
        'tools/render.start',
        {},
        new AbortController().signal,
      ),
    ).rejects.toThrow('503')
    expect(fetch).toHaveBeenCalledTimes(1)
    fetch.mockImplementation(async () =>
      Response.json({ code: 'verification_unknown' }, { status: 503 }),
    )
    await expect(
      editorRequest(
        config,
        job,
        '/assigned-editor',
        'tools/artifact.verify',
        {},
        new AbortController().signal,
      ),
    ).rejects.toThrow('503')
    expect(fetch).toHaveBeenCalledTimes(2)
  })
  it('stops a queued verification when the owning operation loses its lease', async () => {
    vi.useFakeTimers()
    const fetch = vi
      .fn()
      .mockImplementation(async () =>
        Response.json({ code: 'render_capacity_busy' }, { status: 503 }),
      )
    vi.stubGlobal('fetch', fetch)
    const controller = new AbortController()
    const result = editorRequest(
      config,
      job,
      '/assigned-editor',
      'tools/artifact.verify',
      {},
      controller.signal,
    )
    const rejected = expect(result).rejects.toThrow('lease lost')
    await vi.advanceTimersByTimeAsync(0)
    controller.abort(new Error('lease lost'))
    await rejected
    await vi.advanceTimersByTimeAsync(30000)
    expect(fetch).toHaveBeenCalledTimes(1)
  })
})
