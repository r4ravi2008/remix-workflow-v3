import { type ProductionEnv, productionApi } from './server/api'

interface WorkerEnv extends Partial<ProductionEnv> {
  ASSETS: { fetch: (request: Request) => Promise<Response> }
}

const capabilities = {
  service: 'release-kit-studio',
  stage: 'frontend-preview',
  version: '0.1.0',
  productionConnected: false,
  cloudProduction: false,
  tenantAuthentication: false,
  cloudUploads: false,
}

export default {
  async fetch(request: Request, env: WorkerEnv): Promise<Response> {
    const path = new URL(request.url).pathname
    const productionEditor =
      /^\/api\/worker\/jobs\/([a-zA-Z0-9-]+)\/editor\/(.+)$/.exec(path)
    if (productionEditor?.[1] && productionEditor[2]) {
      if (!env.EDITOR)
        return Response.json(
          { error: 'Cloudflare editor is not connected.' },
          { status: 503 },
        )
      const url = new URL(request.url)
      url.pathname = `/v1/production/jobs/${productionEditor[1]}/${productionEditor[2]}`
      return env.EDITOR.fetch(new Request(url, request))
    }
    if (path.startsWith('/api/editor/')) {
      if (!env.EDITOR)
        return Response.json(
          { error: 'Cloudflare editor is not connected.' },
          { status: 503 },
        )
      const url = new URL(request.url)
      url.pathname = path.replace('/api/editor/', '/v1/')
      return env.EDITOR.fetch(new Request(url, request))
    }
    if (
      path.startsWith('/api/') &&
      env.STUDIO_DB &&
      env.MEDIA &&
      env.STUDIO_OPERATOR_TOKEN
    ) {
      return productionApi(request, {
        STUDIO_DB: env.STUDIO_DB,
        MEDIA: env.MEDIA,
        STUDIO_OPERATOR_TOKEN: env.STUDIO_OPERATOR_TOKEN,
        ...(env.EDITOR ? { EDITOR: env.EDITOR } : {}),
      })
    }
    if (path === '/api/health' && request.method === 'GET') {
      return Response.json(capabilities, {
        headers: { 'Cache-Control': 'no-store' },
      })
    }
    if (path.startsWith('/api/')) {
      return Response.json(
        { error: 'Production is not connected to this preview.' },
        { status: 503 },
      )
    }
    const response = await env.ASSETS.fetch(request)
    const headers = new Headers(response.headers)
    headers.set('X-Content-Type-Options', 'nosniff')
    headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
    headers.set(
      'Permissions-Policy',
      'camera=(), microphone=(), geolocation=()',
    )
    headers.set(
      'Content-Security-Policy',
      "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; media-src 'self' blob:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
    )
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers,
    })
  },
}
