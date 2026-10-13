import { Effect, Schema } from 'effect'
import { execFile } from 'node:child_process'
import { createHash } from 'node:crypto'
import {
  mkdir,
  mkdtemp,
  open,
  readFile,
  rm,
  stat,
  writeFile,
} from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { promisify } from 'node:util'

import { features, tools } from '../editor/catalog'
import { jsonSchema } from '../editor/json-schema'
import { KitDescriptor, kitNames } from '../editor/kit-contract'
import { Preview, PreviewBundle, validatePreview } from '../editor/preview'
import {
  Asset,
  Edit,
  Project,
  applyEdits,
  decodeProject,
  validateProject,
} from '../editor/project'
import { OutputId, ReleaseBrief } from '../src/domain'
import { EditorRecipe, materializeEditorRecipe } from './editor-recipe'
import { editorFetch, editorOperationTimeout } from './editor-request'
import { CloudProductionPlan, GeneratedProductionPlan } from './plan'

const help = {
  service: 'release-kit-editor',
  commands: [
    'tools',
    'schema project',
    'schema edits',
    'schema production-plan',
    'schema generated-production-plan',
    'schema recipe',
    'materialize <recipe.json> <inputs.json> <destination.json>',
    'validate <project.json> [edit|render|kit]',
    'edit <project.json> <edits.json>',
    'progress',
    'health',
    'call <tool> <request.json>',
    'upload <asset.json> <media-file>',
    'download <job-id> <output-id> <destination>',
    'archive <job-id> <new-destination.zip>',
    'preview <request.json> <new-directory>',
  ],
  environment: {
    EDITOR_URL:
      'HTTPS editor service URL; localhost is supported for development',
    EDITOR_TOKEN: 'Tenant-scoped editor bearer token; never printed',
  },
  deployment:
    'Standalone local editor or Cloudflare Worker; use health to identify the runtime',
}
export const runEditorCli = async (
  args: ReadonlyArray<string>,
  env: NodeJS.ProcessEnv = process.env,
) => {
  const [command, first, second, third] = args
  const jsonFile = async (path: string | undefined) => {
    if (!path) throw new Error('A JSON input file is required.')
    const content = await readFile(path, 'utf8')
    if (Buffer.byteLength(content) > 4 * 1024 * 1024)
      throw new Error('JSON input exceeds 4 MiB.')
    return JSON.parse(content)
  }
  if (!command || command === 'help' || command === '--help') return help
  if (command === 'tools')
    return {
      source: 'local-client',
      tools: tools(),
      editSchema: jsonSchema(Schema.Array(Edit)),
      features,
      execution: 'Call health to inspect the deployed service and renderer.',
    }
  if (command === 'progress')
    return {
      source: 'code-ledger',
      features,
      cloudVerified: false,
      fullKitCompleted: false,
    }
  if (command === 'schema') {
    if (first === 'production-plan') return jsonSchema(CloudProductionPlan)
    if (first === 'generated-production-plan')
      return jsonSchema(GeneratedProductionPlan)
    if (first === 'recipe') return jsonSchema(EditorRecipe)
    if (first !== 'project' && first !== 'edits')
      throw new Error(
        'Schema must be project, edits, recipe, production-plan or generated-production-plan.',
      )
    return jsonSchema(first === 'project' ? Project : Schema.Array(Edit))
  }
  if (command === 'materialize') {
    if (!third) throw new Error('A new destination project file is required.')
    const recipe = Schema.decodeUnknownSync(EditorRecipe, {
      onExcessProperty: 'error',
    })(await jsonFile(first))
    const input = Schema.decodeUnknownSync(
      Schema.Struct({
        releaseId: Schema.String,
        brief: ReleaseBrief,
        canonicalSource: Schema.String,
        shots: Schema.Array(
          Schema.Struct({ id: Schema.String, path: Schema.String }),
        ),
      }),
      { onExcessProperty: 'error' },
    )(await jsonFile(second))
    if (new Set(input.shots.map(shot => shot.id)).size !== input.shots.length)
      throw new Error('Collected shot IDs must be unique.')
    const result = await materializeEditorRecipe(
      recipe,
      input,
      input.canonicalSource,
      new Map(input.shots.map(shot => [shot.id, shot.path])),
      new AbortController().signal,
    )
    const content = JSON.stringify(result.project, null, 2) + '\n'
    await writeFile(third, content, { flag: 'wx', mode: 0o600 })
    return {
      projectFile: third,
      sha256: createHash('sha256').update(content).digest('hex'),
      assets: result.project.assets,
      fullKitCompleted: false,
      creativelyAccepted: false,
    }
  }
  if (command === 'validate') {
    if (second && !['edit', 'render', 'kit'].includes(second))
      throw new Error('Validation mode must be edit, render or kit.')
    const project = decodeProject(await jsonFile(first))
    const mode =
      second === 'render' ? 'render' : second === 'kit' ? 'kit' : 'edit'
    const findings = validateProject(project, mode)
    return {
      valid: findings.length === 0,
      mode,
      findings,
      measured: false,
      motionReviewed: false,
      heard: false,
      creativelyAccepted: false,
    }
  }
  if (command === 'edit') {
    const project = decodeProject(await jsonFile(first))
    const edits = Schema.decodeUnknownSync(Schema.Array(Edit), {
      onExcessProperty: 'error',
    })(await jsonFile(second))
    const result = applyEdits(project, edits)
    const findings = validateProject(result)
    if (findings.length)
      throw new Error(JSON.stringify({ code: 'invalid_edit', findings }))
    return { project: result, committed: false }
  }
  if (
    !['call', 'health', 'upload', 'download', 'archive', 'preview'].includes(
      command,
    )
  )
    throw new Error('Unknown command. Run editor help.')
  if (args.length > 4 || (third && command !== 'download'))
    throw new Error('Unexpected command argument.')
  if (!env.EDITOR_URL)
    throw new Error('EDITOR_URL is required for service commands.')
  const base = new URL(env.EDITOR_URL)
  if (
    base.protocol !== 'https:' &&
    !(
      base.protocol === 'http:' &&
      ['localhost', '127.0.0.1'].includes(base.hostname)
    )
  )
    throw new Error('Use HTTPS or a localhost development service.')
  if (
    base.username ||
    base.password ||
    base.search ||
    base.hash ||
    base.pathname !== '/'
  )
    throw new Error('EDITOR_URL must be a clean service origin.')
  if (command === 'call' && !tools().some(tool => tool.name === first))
    throw new Error('Unknown editor tool. Run editor tools.')
  if (command !== 'health' && !env.EDITOR_TOKEN)
    throw new Error('EDITOR_TOKEN is required for service commands.')
  const requestJson = async (
    path: string,
    method: string,
    body?: string | Blob,
    headers: Record<string, string> = {},
  ) => {
    const response = await editorFetch(new URL(path, base), {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(env.EDITOR_TOKEN
          ? { Authorization: `Bearer ${env.EDITOR_TOKEN}` }
          : {}),
        ...headers,
      },
      ...(body ? { body } : {}),
      redirect: 'error',
      signal: AbortSignal.timeout(editorOperationTimeout(path, 30000)),
    })
    const result: unknown = await response.json()
    if (!response.ok)
      throw new Error(
        JSON.stringify({ status: response.status, response: result }),
      )
    return result
  }
  if (command === 'preview') {
    if (!second) throw new Error('Provide a request and new review directory.')
    const input = Schema.decodeUnknownSync(Preview, {
      onExcessProperty: 'error',
    })(await jsonFile(first))
    await mkdir(second, { mode: 0o700 })
    try {
      const located = Schema.decodeUnknownSync(
        Schema.Struct({
          artifact: Schema.Struct({
            id: OutputId,
            sha256: Schema.String,
            bytes: Schema.Int,
          }),
        }),
      )(
        await requestJson(
          '/v1/tools/artifact.locate',
          'POST',
          JSON.stringify({ jobId: input.jobId, outputId: input.outputId }),
        ),
      )
      const result = Schema.decodeUnknownSync(
        Schema.Struct({ bundle: PreviewBundle, reused: Schema.Boolean }),
      )(
        await requestJson(
          '/v1/tools/artifact.preview',
          'POST',
          JSON.stringify(input),
        ),
      )
      await validatePreview(input, result.bundle.source, result.bundle)
      if (
        result.bundle.source.id !== located.artifact.id ||
        result.bundle.source.sha256 !== located.artifact.sha256 ||
        result.bundle.source.bytes !== located.artifact.bytes
      )
        throw new Error('Review preview belongs to another immutable artifact.')
      for (const file of result.bundle.files) {
        const response = await editorFetch(
          new URL(
            `/v1/jobs/${input.jobId}/previews/${result.bundle.bundleId}/${file.name}`,
            base,
          ),
          {
            headers: { Authorization: `Bearer ${env.EDITOR_TOKEN}` },
            redirect: 'error',
            signal: AbortSignal.timeout(120000),
          },
        )
        if (
          !response.ok ||
          Number(response.headers.get('Content-Length')) !== file.bytes ||
          response.headers.get('X-Content-Sha256') !== file.sha256 ||
          response.headers.get('X-Source-Sha256') !==
            result.bundle.source.sha256
        )
          throw new Error(
            'Review download differs from its bound source and receipt.',
          )
        if (
          !response.body ||
          response.headers.get('Content-Type') !==
            (file.name.endsWith('.mp4') ? 'video/mp4' : 'image/jpeg')
        )
          throw new Error('Review stream has an unexpected media type.')
        const destination = await open(join(second, file.name), 'wx', 0o600)
        const reader = response.body.getReader()
        const checksum = createHash('sha256')
        let bytes = 0
        try {
          for (;;) {
            const part = await reader.read()
            if (part.done) break
            bytes += part.value.byteLength
            if (bytes > file.bytes)
              throw new Error('Review stream exceeds its declared size.')
            checksum.update(part.value)
            await destination.writeFile(part.value)
          }
          if (bytes !== file.bytes || checksum.digest('hex') !== file.sha256)
            throw new Error('Review download failed checksum verification.')
          await destination.sync()
        } finally {
          await reader.cancel().catch(() => {})
          await destination.close()
        }
      }
      await writeFile(
        join(second, 'receipt.json'),
        JSON.stringify(result.bundle, null, 2) + '\n',
        { flag: 'wx', mode: 0o600 },
      )
      return {
        directory: second,
        bundleId: result.bundle.bundleId,
        sourceSha256: result.bundle.source.sha256,
        filesVerified: result.bundle.files.length,
        reused: result.reused,
        semanticReviewed: false,
        motionReviewed: false,
        heard: false,
        creativelyAccepted: false,
      }
    } catch (error) {
      await rm(second, { recursive: true, force: true })
      throw error
    }
  }
  if (command === 'upload') {
    if (!second) throw new Error('A media file is required.')
    const asset = Schema.decodeUnknownSync(Asset, {
      onExcessProperty: 'error',
    })(await jsonFile(first))
    if (
      asset.bytes > 100 * 1024 * 1024 ||
      (await stat(second)).size !== asset.bytes
    )
      throw new Error('Media must match the registered size, at most 100 MiB.')
    const content = await readFile(second)
    if (
      content.byteLength !== asset.bytes ||
      createHash('sha256').update(content).digest('hex') !== asset.sha256
    )
      throw new Error('Media checksum differs from immutable asset metadata.')
    await requestJson('/v1/tools/media.register', 'POST', JSON.stringify(asset))
    const inspect = () =>
      requestJson(
        '/v1/tools/media.inspect',
        'POST',
        JSON.stringify({ assetId: asset.id }),
      )
    const current = Schema.decodeUnknownSync(
      Schema.Struct({ uploaded: Schema.Boolean }),
    )(await inspect())
    if (!current.uploaded)
      await requestJson(
        `/v1/media/${asset.id}`,
        'PUT',
        new Blob([new Uint8Array(content)]),
        {
          'Content-Type': 'application/octet-stream',
          'Content-Length': String(asset.bytes),
        },
      )
    return {
      ...Schema.decodeUnknownSync(
        Schema.Struct({
          metadata: Asset,
          uploaded: Schema.Literal(true),
          mediaProbeVerified: Schema.Literal(false),
        }),
      )(await inspect()),
      resumedExistingUpload: current.uploaded,
    }
  }
  if (command === 'archive') {
    if (!first || !/^[a-zA-Z0-9_-]{1,80}$/.test(first) || !second)
      throw new Error('Provide a render job ID and new archive destination.')
    const descriptor = Schema.decodeUnknownSync(KitDescriptor, {
      onExcessProperty: 'error',
    })(
      await requestJson(
        '/v1/tools/kit.locate',
        'POST',
        JSON.stringify({ jobId: first }),
      ),
    )
    if (
      descriptor.jobId !== first ||
      descriptor.downloadPath !== `/v1/jobs/${first}/archive` ||
      new Set(descriptor.entries.map(entry => entry.name)).size !== 8 ||
      !kitNames.every(name =>
        descriptor.entries.some(entry => entry.name === name),
      ) ||
      descriptor.entries.find(entry => entry.name === 'manifest.json')
        ?.sha256 !== descriptor.manifestSha256
    )
      throw new Error('Archive descriptor differs from the requested kit.')
    const destination = await open(second, 'wx', 0o600)
    const state: {
      reader: ReadableStreamDefaultReader<Uint8Array> | null
      temp: string | null
    } = { reader: null, temp: null }
    try {
      const response = await editorFetch(
        new URL(descriptor.downloadPath, base),
        {
          headers: { Authorization: `Bearer ${env.EDITOR_TOKEN}` },
          redirect: 'error',
          signal: AbortSignal.timeout(30 * 60 * 1000),
        },
      )
      if (
        !response.ok ||
        !response.body ||
        response.headers.get('Content-Type') !== 'application/zip' ||
        Number(response.headers.get('Content-Length')) !== descriptor.bytes ||
        response.headers.get('X-Kit-Manifest-Sha256') !==
          descriptor.manifestSha256
      )
        throw new Error('Archive stream differs from its descriptor.')
      const checksum = createHash('sha256')
      const count = { bytes: 0 }
      state.reader = response.body.getReader()
      for (;;) {
        const part = await state.reader.read()
        if (part.done) break
        count.bytes += part.value.byteLength
        if (count.bytes > descriptor.bytes)
          throw new Error('Archive exceeds its verified size.')
        checksum.update(part.value)
        await destination.writeFile(part.value)
      }
      if (count.bytes !== descriptor.bytes)
        throw new Error('Archive is incomplete.')
      await destination.sync()
      state.temp = await mkdtemp(join(tmpdir(), 'release-kit-verification-'))
      const metadata = join(state.temp, 'descriptor.json')
      await writeFile(metadata, JSON.stringify(descriptor), {
        flag: 'wx',
        mode: 0o600,
      })
      const result = await promisify(execFile)(
        'python3',
        [
          fileURLToPath(new URL('./verify-kit.py', import.meta.url)),
          second,
          metadata,
        ],
        { timeout: 300000, maxBuffer: 65536 },
      )
      const verified = Schema.decodeUnknownSync(
        Schema.Struct({
          archiveEntriesVerified: Schema.Literal(8),
          manifestSha256: Schema.String,
          motionReviewed: Schema.Literal(false),
          heard: Schema.Literal(false),
          creativelyAccepted: Schema.Literal(false),
        }),
      )(JSON.parse(result.stdout))
      if (verified.manifestSha256 !== descriptor.manifestSha256)
        throw new Error('Verifier returned a different manifest.')
      return {
        jobId: descriptor.jobId,
        releaseId: descriptor.releaseId,
        destination: second,
        bytes: count.bytes,
        sha256: checksum.digest('hex'),
        downloadedBytesVerified: true,
        ...verified,
      }
    } catch (error) {
      await destination.close()
      await rm(second, { force: true })
      throw error
    } finally {
      await state.reader?.cancel().catch(() => {})
      state.reader?.releaseLock()
      await destination.close()
      if (state.temp) await rm(state.temp, { recursive: true, force: true })
    }
  }
  if (command === 'download') {
    if (!first || !/^[a-zA-Z0-9_-]{1,80}$/.test(first) || !third)
      throw new Error('Provide a job ID, output ID and destination.')
    const outputId = Schema.decodeUnknownSync(OutputId)(second)
    const located = Schema.decodeUnknownSync(
      Schema.Struct({
        artifact: Schema.Struct({
          id: OutputId,
          sha256: Schema.String,
          bytes: Schema.Int.check(
            Schema.isBetween({ minimum: 1, maximum: 2147483648 }),
          ),
        }),
      }),
    )(
      await requestJson(
        '/v1/tools/artifact.locate',
        'POST',
        JSON.stringify({ jobId: first, outputId }),
      ),
    )
    if (located.artifact.id !== outputId)
      throw new Error('Artifact identity differs from the request.')
    const response = await editorFetch(
      new URL(`/v1/jobs/${first}/outputs/${outputId}`, base),
      {
        headers: { Authorization: `Bearer ${env.EDITOR_TOKEN}` },
        redirect: 'error',
        signal: AbortSignal.timeout(300000),
      },
    )
    if (
      !response.ok ||
      !response.body ||
      Number(response.headers.get('Content-Length')) !== located.artifact.bytes
    )
      throw new Error('Output stream differs from its receipt.')
    const destination = await open(third, 'wx')
    try {
      const reader = response.body.getReader()
      const checksum = createHash('sha256')
      const count = { bytes: 0 }
      for (;;) {
        const part = await reader.read()
        if (part.done) break
        count.bytes += part.value.byteLength
        if (count.bytes > located.artifact.bytes) {
          await reader.cancel()
          throw new Error('Output exceeds its registered size.')
        }
        checksum.update(part.value)
        await destination.writeFile(part.value)
      }
      if (
        count.bytes !== located.artifact.bytes ||
        checksum.digest('hex') !== located.artifact.sha256
      )
        throw new Error('Downloaded bytes differ from the artifact checksum.')
      return {
        ...located.artifact,
        destination: third,
        downloadedBytesVerified: true,
        motionReviewed: false,
        heard: false,
        creativelyAccepted: false,
      }
    } catch (error) {
      await destination.close()
      await rm(third, { force: true })
      throw error
    } finally {
      await destination.close()
    }
  }
  return requestJson(
    command === 'health' ? '/v1/health' : `/v1/tools/${first}`,
    command === 'health' ? 'GET' : 'POST',
    command === 'call' ? JSON.stringify(await jsonFile(second)) : undefined,
  )
}
if (import.meta.main) {
  await Effect.runPromise(
    Effect.tryPromise({
      try: () => runEditorCli(process.argv.slice(2)),
      catch: error =>
        new Error(error instanceof Error ? error.message : 'Editor CLI failed'),
    }).pipe(
      Effect.match({
        onFailure: error => {
          console.error(JSON.stringify({ ok: false, error: error.message }))
          process.exitCode = 1
        },
        onSuccess: result => {
          console.log(JSON.stringify(result, null, 2))
          if (
            typeof result === 'object' &&
            result !== null &&
            'valid' in result &&
            result.valid === false
          )
            process.exitCode = 2
        },
      }),
    ),
  )
}
