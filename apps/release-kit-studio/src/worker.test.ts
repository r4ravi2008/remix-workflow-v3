// @vitest-environment node
import { describe, expect, it } from 'vitest'

import worker from './worker'

describe('preview worker', () => {
  const env = {
    ASSETS: {
      fetch: async () =>
        new Response('<html>studio</html>', {
          headers: { 'Content-Type': 'text/html' },
        }),
    },
  }
  it('reports the actual preview capabilities and prevents unconnected API jobs', async () => {
    const health = await worker.fetch(
      new Request('https://studio.test/api/health'),
      env,
    )
    expect(await health.json()).toMatchObject({
      cloudProduction: false,
      tenantAuthentication: false,
      cloudUploads: false,
    })
    const render = await worker.fetch(
      new Request('https://studio.test/api/releases', { method: 'POST' }),
      env,
    )
    expect(render.status).toBe(503)
  })
  it('serves the SPA with protection against framing and external connections', async () => {
    const response = await worker.fetch(
      new Request('https://studio.test/releases/one'),
      env,
    )
    expect(response.status).toBe(200)
    expect(response.headers.get('Content-Security-Policy')).toContain(
      "frame-ancestors 'none'",
    )
    expect(response.headers.get('Content-Security-Policy')).toContain(
      "connect-src 'self'",
    )
  })
  it('forwards editor tools through the separate Worker service binding', async () => {
    const received: Array<Request> = []
    const response = await worker.fetch(
      new Request('https://studio.test/api/editor/tools/project.inspect', {
        method: 'POST',
        headers: {
          Cookie: 'studio_session=private-session',
          Origin: 'https://studio.test',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ projectId: 'one', revision: null }),
      }),
      {
        ...env,
        EDITOR: {
          fetch: async request => {
            received.push(request)
            return Response.json({ projectId: 'one' })
          },
        },
      },
    )
    expect(response.status).toBe(200)
    expect(received[0]?.url).toBe(
      'https://studio.test/v1/tools/project.inspect',
    )
    expect(received[0]?.headers.get('Cookie')).toBe(
      'studio_session=private-session',
    )
    expect(received[0]?.headers.get('Origin')).toBe('https://studio.test')
  })
})
