import { Schema } from 'effect'

import { canonicalJson } from '../src/canonical'
import { type EditorRuntime, fixedStream } from './api'
import { NativeArtifact } from './artifact'
import { type CapacityGrant, EditorCapacity } from './capacity'
import { Render } from './catalog'
import {
  Preview,
  PreviewBundle,
  previewIdentity,
  previewPrefix,
  previewSamples,
  previewSource,
  readPreview,
  validatePreview,
} from './preview'
import { type Composition } from './project'
import { EditorError, EditorStore, JobRow, digest } from './store'

const NativeReceipt = Schema.Struct({
  outputs: Schema.Array(NativeArtifact),
  sources: Schema.Unknown,
  engine: Schema.Unknown,
  projectSha256: Schema.String,
  measured: Schema.Literal(true),
  motionReviewed: Schema.Literal(false),
  heard: Schema.Literal(false),
  creativelyAccepted: Schema.Literal(false),
})
const NativeStatus = Schema.Struct({
  state: Schema.String,
  progress: Schema.Unknown,
  receipt: Schema.NullOr(NativeReceipt),
  error: Schema.NullOr(Schema.String),
})
const Command = Schema.Struct({
  jobId: Schema.String,
  tenant: Schema.String,
  outputId: Schema.optional(Schema.String),
  preview: Schema.optional(Preview),
})
export interface CoordinatorTransaction {
  get<T>(key: string): Promise<T | undefined>
  put(key: string, value: unknown): Promise<unknown>
}
export interface CoordinatorContext {
  storage: CoordinatorTransaction & {
    delete(key: string): Promise<unknown>
    setAlarm(time: number): Promise<unknown>
    deleteAlarm(): Promise<unknown>
    transaction<T>(
      action: (storage: CoordinatorTransaction) => Promise<T>,
    ): Promise<T>
  }
  container?: {
    readonly running: boolean
    start(options: { enableInternet: boolean }): unknown
    destroy(): Promise<unknown>
    setInactivityTimeout(milliseconds: number): Promise<unknown>
    getTcpPort(port: number): {
      fetch(url: string, init: RequestInit): Promise<Response>
    }
  }
  waitUntil(action: Promise<unknown>): void
}

export class RenderCoordinator {
  constructor(
    readonly ctx: CoordinatorContext,
    readonly env: EditorRuntime,
    readonly store: EditorStore,
  ) {}
  operation = Promise.resolve()
  capacity() {
    return new EditorCapacity(this.store.db)
  }
  async terminate(job: JobRow, purpose: 'render' | 'verify' = 'render') {
    const grant = await this.capacity().holder()
    if (
      grant &&
      (grant.job_id !== job.id ||
        grant.tenant_id !== job.tenant_id ||
        grant.purpose !== purpose)
    )
      return
    try {
      await this.ctx.container?.destroy()
      if (this.ctx.container?.running)
        throw new EditorError(
          409,
          'termination_uncertain',
          'Owned render runtime is still running; capacity remains reserved.',
        )
      if (grant) await this.capacity().release(grant)
    } catch (error) {
      await this.ctx.storage.setAlarm(Date.now() + 15000)
      throw error
    }
  }
  async exclusive<T>(action: () => Promise<T>): Promise<T> {
    const previous = this.operation
    const completion = { release: () => {} }
    this.operation = new Promise<void>(resolve => {
      completion.release = resolve
    })
    await previous
    try {
      return await action()
    } finally {
      completion.release()
    }
  }
  async native(path: string, init: RequestInit = {}) {
    const container = this.ctx.container
    if (!container)
      throw new EditorError(
        503,
        'container_unavailable',
        'Cloudflare Container is not bound.',
      )
    await container.setInactivityTimeout(600000)
    if (!container.running)
      throw new EditorError(
        409,
        'container_not_running',
        'Container is not running; reconcile before replaying.',
      )
    return container.getTcpPort(8080).fetch(`http://container${path}`, init)
  }
  async boot() {
    const container = this.ctx.container
    if (!container)
      throw new EditorError(
        503,
        'container_unavailable',
        'Cloudflare Container is not configured.',
      )
    await container.setInactivityTimeout(600000)
    if (!container.running) container.start({ enableInternet: false })
    for (const _attempt of Array.from({ length: 80 }, (_, index) => index)) {
      try {
        if ((await this.native('/health')).ok) return
      } catch {}
      await new Promise(resolve => setTimeout(resolve, 250))
    }
    throw new EditorError(
      503,
      'container_not_ready',
      'Cloudflare Container did not become ready within 20 seconds.',
    )
  }
  async update(
    job: JobRow,
    state: string,
    progress: unknown,
    receipt: unknown = null,
    error: string | null = null,
  ) {
    await this.store.db.run(
      "UPDATE editor_jobs SET state=?,progress_json=?,receipt_json=COALESCE(?,receipt_json),error=?,updated_at=? WHERE id=? AND tenant_id=? AND fingerprint=? AND state NOT IN ('ready','failed','cancelled') AND (? IN ('cancelled','cancel-requested') OR state!='cancel-requested')",
      [
        state,
        JSON.stringify(progress),
        receipt === null ? null : JSON.stringify(receipt),
        error,
        Math.floor(Date.now() / 1000),
        job.id,
        job.tenant_id,
        job.fingerprint,
        state,
      ],
    )
  }
  async sendFile(job: JobRow, path: string, key: string) {
    const object = await this.env.MEDIA.get(key, {})
    if (!object)
      throw new EditorError(
        404,
        'source_missing',
        'Private source object is missing.',
      )
    const fixed = fixedStream(this.env, object.size)
    const transfer = object.body.pipeTo(fixed.writable)
    const uploaded = await this.native(path, {
      method: 'PUT',
      headers: { 'Content-Length': String(object.size) },
      body: fixed.readable,
    })
    await transfer
    if (!uploaded.ok)
      throw new EditorError(
        422,
        'native_upload_failed',
        'Native engine rejected the immutable media transfer: ' +
          (await uploaded.text()).slice(0, 500),
      )
  }
  async attach(input: JobRow): Promise<void> {
    const job = await this.store.job(input.tenant_id, input.id)
    if (job.state !== 'queued') return this.reconcile(job)
    await this.ctx.storage.put('active', {
      jobId: job.id,
      tenant: job.tenant_id,
    })
    await this.ctx.storage.setAlarm(Date.now() + 5000)
    const grant = await this.capacity().claim(job, 'render')
    if (!grant) {
      await this.update(job, 'queued', {
        phase: 'waiting-for-render-capacity',
        completedOutputs: 0,
      })
      return
    }
    const claimed = await this.ctx.storage.transaction(async transaction => {
      const previous = await transaction.get<{ jobId: string }>('attachment')
      if (previous?.jobId === job.id) return false
      await transaction.put('attachment', {
        jobId: job.id,
        fingerprint: job.fingerprint,
      })
      return true
    })
    if (!claimed) return
    await this.ctx.storage.put('active', {
      jobId: job.id,
      tenant: job.tenant_id,
    })
    await this.ctx.storage.setAlarm(Date.now() + 60000)
    await this.update(job, 'staging', { phase: 'staging', completedOutputs: 0 })
    try {
      const staged = await this.store.job(job.tenant_id, job.id)
      if (staged.state === 'cancel-requested') {
        await this.update(staged, 'cancelled', {
          phase: 'cancelled-before-attachment',
        })
        await this.terminate(staged)
        await this.ctx.storage.deleteAlarm()
        return
      }
      if (staged.state !== 'staging') return
      await this.boot()
      const beforeCreate = await this.store.job(job.tenant_id, job.id)
      if (['cancel-requested', 'cancelled'].includes(beforeCreate.state)) {
        await this.update(beforeCreate, 'cancelled', {
          phase: 'cancelled-before-native-create',
        })
        await this.terminate(beforeCreate)
        await this.ctx.storage.deleteAlarm()
        return
      }
      const snapshot = await this.store.inspect(
        job.tenant_id,
        job.project_id,
        job.revision,
      )
      const request = Schema.decodeUnknownSync(Render)(
        JSON.parse(job.request_json),
      )
      const project =
        request.mode === 'kit'
          ? snapshot.project
          : {
              ...snapshot.project,
              compositions: snapshot.project.compositions.filter(
                comp => comp.id === request.outputId,
              ),
            }
      const create = await this.native('/jobs', {
        method: 'POST',
        body: JSON.stringify({ jobId: job.id, project }),
      })
      if (!create.ok)
        throw new EditorError(
          409,
          'native_intent_conflict',
          'Native job attachment needs reconciliation.',
        )
      for (const asset of project.assets) {
        const stored = await this.store.asset(job.tenant_id, asset.id)
        if (!stored?.uploaded)
          throw new EditorError(
            422,
            'source_missing',
            'A tenant-owned source is not uploaded.',
          )
        await this.sendFile(
          job,
          `/jobs/${job.id}/assets/${asset.id}`,
          stored.object_key,
        )
      }
      const started = await this.native(`/jobs/${job.id}/run`, {
        method: 'POST',
      })
      if (!started.ok)
        throw new EditorError(
          409,
          'native_start_uncertain',
          'Native start could not be confirmed.',
        )
      await this.update(job, 'running', {
        phase: 'rendering',
        completedOutputs: 0,
        totalOutputs: project.compositions.length,
      })
      await this.ctx.storage.setAlarm(Date.now() + 15000)
    } catch (error) {
      await this.update(
        job,
        'uncertain',
        { phase: 'needs-reconciliation' },
        null,
        error instanceof Error
          ? error.message
          : 'Native attachment outcome is uncertain.',
      )
    }
  }
  async verify(job: JobRow, outputId: string, composition: Composition) {
    if (job.state === 'ready') {
      await this.boot()
      const status = await this.native(`/jobs/${job.id}`)
      if (status.status === 404) {
        const snapshot = await this.store.inspect(
          job.tenant_id,
          job.project_id,
          job.revision,
        )
        const request = Schema.decodeUnknownSync(Render)(
          JSON.parse(job.request_json),
        )
        const project =
          request.mode === 'kit'
            ? snapshot.project
            : {
                ...snapshot.project,
                compositions: snapshot.project.compositions.filter(
                  comp => comp.id === request.outputId,
                ),
              }
        const created = await this.native('/jobs', {
          method: 'POST',
          body: JSON.stringify({
            jobId: job.id,
            project,
            verificationOnly: true,
          }),
        })
        if (!created.ok)
          throw new EditorError(
            409,
            'verification_runtime',
            'Could not restore an independent verifier.',
          )
        for (const asset of project.assets) {
          const stored = await this.store.asset(job.tenant_id, asset.id)
          if (!stored?.uploaded)
            throw new EditorError(
              404,
              'verification_source',
              'Canonical verification input is missing.',
            )
          await this.sendFile(
            job,
            `/jobs/${job.id}/assets/${asset.id}`,
            stored.object_key,
          )
        }
      } else if (!status.ok)
        throw new EditorError(
          409,
          'verification_runtime',
          'Native verification runtime could not be reconciled.',
        )
    }
    await this.sendFile(
      job,
      `/jobs/${job.id}/verification/${outputId}`,
      `editor/${job.tenant_id}/jobs/${job.id}/${outputId}`,
    )
    const checked = await this.native(`/jobs/${job.id}/verify`, {
      method: 'POST',
      body: JSON.stringify({ outputId }),
    })
    if (!checked.ok)
      throw new EditorError(
        422,
        'verification_failed',
        'Independent stored-byte verification failed.',
      )
    const result = Schema.decodeUnknownSync(NativeArtifact)(
      await checked.json(),
    )
    if (
      result.id !== outputId ||
      result.width !== composition.width ||
      result.height !== composition.height ||
      result.frames !== composition.frames ||
      result.frameDiagnostics?.sampledFrames !== composition.frames
    )
      throw new EditorError(
        422,
        'verification_binding',
        'Stored-byte measurements differ from the project composition.',
      )
    return result
  }
  async withVerification<T>(
    job: JobRow,
    action: () => Promise<T>,
    cached?: () => Promise<T | undefined>,
  ) {
    return this.exclusive(async () => {
      const reused = await cached?.()
      if (reused !== undefined) return reused
      const active = await this.store.db.first(
        "SELECT id FROM editor_jobs WHERE tenant_id=? AND release_id=? AND state IN ('queued','staging','running','verifying','cancel-requested','uncertain') LIMIT 1",
        [job.tenant_id, job.release_id],
      )
      if (active)
        throw new EditorError(
          409,
          'renderer_busy',
          'Reconcile active work before artifact verification or review previews.',
        )
      const grant = await this.capacity().claim(job, 'verify')
      if (!grant)
        throw new EditorError(
          503,
          'render_capacity_busy',
          'Native render capacity is occupied; retry this artifact operation later.',
        )
      await this.ctx.storage.put('verification', grant)
      await this.ctx.storage.setAlarm(Date.now() + 60000)
      try {
        return await action()
      } finally {
        await this.terminate(job, 'verify')
        await this.ctx.storage.delete('verification')
        await this.ctx.storage.deleteAlarm()
      }
    })
  }
  async preview(job: JobRow, input: Preview) {
    if (input.jobId !== job.id)
      throw new EditorError(
        422,
        'preview_binding',
        'Preview names a different render job.',
      )
    const source = previewSource(job, input.outputId)
    const sampleFrames = previewSamples(input, source)
    const bundleId = await previewIdentity(input, source)
    const prefix = previewPrefix(job.tenant_id, job.id, bundleId)
    const readCached = async () => {
      const cached = await readPreview(
        this.env.MEDIA,
        job.tenant_id,
        job,
        bundleId,
      )
      if (!cached) return undefined
      await validatePreview(input, source, cached)
      for (const file of cached.files)
        if (
          (await this.env.MEDIA.head(prefix + file.name))?.size !== file.bytes
        )
          throw new EditorError(
            422,
            'preview_integrity',
            'Cached review media is missing or changed.',
          )
      return { bundle: cached, reused: true }
    }
    return this.withVerification(
      job,
      async () => {
        const snapshot = await this.store.inspect(
          job.tenant_id,
          job.project_id,
          job.revision,
        )
        const comp = snapshot.project.compositions.find(
          item => item.id === input.outputId,
        )
        if (!comp)
          throw new EditorError(
            404,
            'artifact_not_found',
            'Composition is missing.',
          )
        const parent = await this.verify(job, input.outputId, comp)
        if (parent.sha256 !== source.sha256 || parent.bytes !== source.bytes)
          throw new EditorError(
            422,
            'preview_source',
            'Stored source differs from the completed immutable artifact.',
          )
        const generated = await this.native(`/jobs/${job.id}/preview`, {
          method: 'POST',
          body: JSON.stringify({
            ...input,
            sampleFrames,
            bundleId,
            sourceSha256: source.sha256,
          }),
        })
        if (!generated.ok)
          throw new EditorError(
            422,
            'preview_failed',
            'Native review preview failed verification.',
          )
        const result = Schema.decodeUnknownSync(
          Schema.Struct({ files: PreviewBundle.fields.files }),
        )(await generated.json())
        const bundle = Schema.decodeUnknownSync(PreviewBundle)({
          schemaVersion: 1,
          method: 'native-review-preview/v2',
          ...input,
          sampleFrames,
          bundleId,
          source,
          files: result.files,
          measured: true,
          semanticReviewed: false,
          motionReviewed: false,
          heard: false,
          creativelyAccepted: false,
        })
        await validatePreview(input, source, bundle)
        for (const file of bundle.files) {
          const raw = await this.native(
            `/jobs/${job.id}/previews/${bundleId}/${file.name}`,
          )
          if (
            !raw.ok ||
            !raw.body ||
            Number(raw.headers.get('Content-Length')) !== file.bytes
          )
            throw new EditorError(
              422,
              'preview_transfer',
              'Native review stream differs from its receipt.',
            )
          const fixed = fixedStream(this.env, file.bytes)
          await Promise.all([
            this.env.MEDIA.put(prefix + file.name, fixed.readable, {
              sha256: file.sha256,
              httpMetadata: {
                contentType: file.name.endsWith('.mp4')
                  ? 'video/mp4'
                  : 'image/jpeg',
              },
              customMetadata: {
                tenant: job.tenant_id,
                jobId: job.id,
                sourceSha256: source.sha256,
                bundleId,
              },
            }),
            raw.body.pipeTo(fixed.writable),
          ])
          const stored = await this.env.MEDIA.get(prefix + file.name, {})
          if (
            !stored ||
            stored.size !== file.bytes ||
            (await digest(await new Response(stored.body).arrayBuffer())) !==
              file.sha256
          )
            throw new EditorError(
              422,
              'preview_integrity',
              'Stored review media differs from verified native bytes.',
            )
        }
        const content = canonicalJson(bundle)
        const fixedReceipt = fixedStream(
          this.env,
          new TextEncoder().encode(content).byteLength,
        )
        await Promise.all([
          this.env.MEDIA.put(prefix + 'receipt.json', fixedReceipt.readable, {
            sha256: await digest(content),
            httpMetadata: { contentType: 'application/json' },
            customMetadata: {
              tenant: job.tenant_id,
              jobId: job.id,
              sourceSha256: source.sha256,
              bundleId,
            },
          }),
          new Blob([content]).stream().pipeTo(fixedReceipt.writable),
        ])
        const stored = await readPreview(
          this.env.MEDIA,
          job.tenant_id,
          job,
          bundleId,
        )
        if (!stored || canonicalJson(stored) !== content)
          throw new EditorError(
            422,
            'preview_integrity',
            'Stored review receipt differs from the verified bundle.',
          )
        return { bundle: stored, reused: false }
      },
      readCached,
    )
  }
  async reconcile(input: JobRow): Promise<void> {
    const job = await this.store.job(input.tenant_id, input.id)
    if (job.state === 'queued') {
      const attachment = await this.ctx.storage.get<{ jobId: string }>(
        'attachment',
      )
      if (attachment?.jobId !== job.id) return this.attach(job)
    }
    if (['ready', 'failed', 'cancelled'].includes(job.state)) {
      const grant = await this.capacity().holder()
      if (grant?.job_id === job.id && grant.purpose === 'render') {
        await this.terminate(job)
        await this.ctx.storage.deleteAlarm()
      }
      return
    }
    const grant = await this.capacity().holder()
    if (
      !grant ||
      grant.job_id !== job.id ||
      grant.tenant_id !== job.tenant_id ||
      grant.fingerprint !== job.fingerprint ||
      grant.purpose !== 'render'
    )
      throw new EditorError(
        409,
        'capacity_reconciliation',
        'This render has no confirmed account capacity grant; reconcile or cancel its owned runtime.',
      )
    try {
      const inspected = await this.native(`/jobs/${job.id}`)
      if (!inspected.ok)
        throw new EditorError(
          409,
          'native_outcome_missing',
          'Native attempt is missing. Automatic replay is disabled.',
        )
      const status = Schema.decodeUnknownSync(NativeStatus)(
        await inspected.json(),
      )
      if (status.state === 'ready' && status.receipt) {
        if (job.state === 'cancel-requested') {
          await this.update(job, 'cancelled', {
            phase: 'cancelled-after-native-completion',
          })
          await this.terminate(job)
          await this.ctx.storage.deleteAlarm()
          return
        }
        const snapshot = await this.store.inspect(
          job.tenant_id,
          job.project_id,
          job.revision,
        )
        const request = Schema.decodeUnknownSync(Render)(
          JSON.parse(job.request_json),
        )
        const project =
          request.mode === 'kit'
            ? snapshot.project
            : {
                ...snapshot.project,
                compositions: snapshot.project.compositions.filter(
                  comp => comp.id === request.outputId,
                ),
              }
        if (
          status.receipt.projectSha256 !==
          (await digest(canonicalJson(project)))
        )
          throw new EditorError(
            422,
            'recipe_binding',
            'Native receipt belongs to a different immutable project recipe.',
          )
        if (
          status.receipt.outputs.length !== project.compositions.length ||
          new Set(status.receipt.outputs.map(output => output.id)).size !==
            project.compositions.length
        )
          throw new EditorError(
            422,
            'output_contract',
            'Native outputs do not match the requested composition set.',
          )
        await this.update(job, 'verifying', {
          phase: 'stored-byte-verification',
          completedOutputs: 0,
          totalOutputs: project.compositions.length,
        })
        for (const output of status.receipt.outputs) {
          const comp = project.compositions.find(
            candidate => candidate.id === output.id,
          )
          if (!comp)
            throw new EditorError(
              422,
              'output_contract',
              'Unexpected output identity.',
            )
          const raw = await this.native(`/jobs/${job.id}/outputs/${output.id}`)
          if (
            !raw.ok ||
            !raw.body ||
            Number(raw.headers.get('Content-Length')) !== output.bytes
          )
            throw new EditorError(
              422,
              'output_transfer',
              'Native output stream differs from its receipt.',
            )
          const key = `editor/${job.tenant_id}/jobs/${job.id}/${output.id}`
          const fixed = fixedStream(this.env, output.bytes)
          await Promise.all([
            this.env.MEDIA.put(key, fixed.readable, {
              sha256: output.sha256,
              httpMetadata: {
                contentType: ['thumbnail', 'artwork'].includes(output.id)
                  ? 'image/jpeg'
                  : 'video/mp4',
              },
              customMetadata: {
                tenant: job.tenant_id,
                jobId: job.id,
                fingerprint: job.fingerprint,
              },
            }),
            raw.body.pipeTo(fixed.writable),
          ])
          if ((await this.env.MEDIA.head(key))?.size !== output.bytes)
            throw new EditorError(
              422,
              'stored_size',
              'Stored output byte count differs from the native receipt.',
            )
          const verified = await this.verify(job, output.id, comp)
          if (
            verified.sha256 !== output.sha256 ||
            verified.bytes !== output.bytes
          )
            throw new EditorError(
              422,
              'stored_hash',
              'Read-back output differs from the encoded bytes.',
            )
        }
        const receipt = {
          ...status.receipt,
          storedByteReadback: true,
          intentFingerprint: job.fingerprint,
          mode: request.mode,
        }
        const document = canonicalJson(receipt)
        const receiptSha256 = await digest(document)
        const receiptBytes = new TextEncoder().encode(document).byteLength
        const receiptKey = `editor/${job.tenant_id}/jobs/${job.id}/receipt.json`
        const fixedReceipt = fixedStream(this.env, receiptBytes)
        await Promise.all([
          this.env.MEDIA.put(receiptKey, fixedReceipt.readable, {
            sha256: receiptSha256,
            httpMetadata: { contentType: 'application/json' },
            customMetadata: {
              tenant: job.tenant_id,
              jobId: job.id,
              fingerprint: job.fingerprint,
            },
          }),
          new Blob([document]).stream().pipeTo(fixedReceipt.writable),
        ])
        const storedReceipt = await this.env.MEDIA.get(receiptKey, {})
        if (
          !storedReceipt ||
          storedReceipt.size !== receiptBytes ||
          (await digest(await new Response(storedReceipt.body).text())) !==
            receiptSha256
        )
          throw new EditorError(
            422,
            'receipt_integrity',
            'Immutable stored receipt failed readback.',
          )
        await this.update(
          job,
          'ready',
          {
            phase: 'verified',
            completedOutputs: project.compositions.length,
            totalOutputs: project.compositions.length,
          },
          { ...receipt, receiptStored: true, receiptSha256 },
        )
        const final = await this.store.job(job.tenant_id, job.id)
        if (final.state === 'cancel-requested')
          await this.update(final, 'cancelled', {
            phase: 'cancelled-during-verification',
          })
        await this.terminate(job)
        await this.ctx.storage.deleteAlarm()
      } else if (status.state === 'failed' || status.state === 'cancelled') {
        const current = await this.store.job(job.tenant_id, job.id)
        await this.update(
          job,
          current.state === 'cancel-requested' ? 'cancelled' : status.state,
          status.progress,
          null,
          status.error,
        )
        const final = await this.store.job(job.tenant_id, job.id)
        if (final.state === 'cancel-requested')
          await this.update(final, 'cancelled', {
            phase: 'cancelled-after-native-exit',
          })
        await this.terminate(job)
        await this.ctx.storage.deleteAlarm()
      } else {
        if (Math.floor(Date.now() / 1000) - grant.started_at > 1800) {
          await this.native(`/jobs/${job.id}/cancel`, { method: 'POST' })
          await this.update(job, 'cancel-requested', {
            phase: 'deadline-cancellation',
          })
        } else
          await this.update(
            job,
            job.state === 'cancel-requested'
              ? 'cancel-requested'
              : status.state === 'staging'
                ? 'staging'
                : 'running',
            status.progress,
          )
        await this.ctx.storage.setAlarm(Date.now() + 15000)
      }
    } catch (error) {
      if (
        ['queued', 'staging'].includes(job.state) &&
        Math.floor(Date.now() / 1000) - grant.started_at < 60
      ) {
        await this.ctx.storage.setAlarm(Date.now() + 5000)
        return
      }
      await this.update(
        job,
        'uncertain',
        { phase: 'needs-reconciliation' },
        null,
        error instanceof Error
          ? error.message
          : 'Render outcome could not be established.',
      )
      const latest = await this.store.job(job.tenant_id, job.id)
      if (['ready', 'failed', 'cancelled'].includes(latest.state))
        await this.ctx.storage.setAlarm(Date.now() + 15000)
      else await this.ctx.storage.deleteAlarm()
    }
  }
  async fetch(request: Request): Promise<Response> {
    try {
      const command = Schema.decodeUnknownSync(Command)(await request.json())
      const job = await this.store.job(command.tenant, command.jobId)
      const owner = await this.ctx.storage.get<{
        tenant: string
        release: string
      }>('owner')
      if (
        owner &&
        (owner.tenant !== job.tenant_id || owner.release !== job.release_id)
      )
        throw new EditorError(
          403,
          'render_owner',
          'Renderer is owned by another release.',
        )
      await this.ctx.storage.put('owner', {
        tenant: job.tenant_id,
        release: job.release_id,
      })
      const path = new URL(request.url).pathname
      if (path === '/preview' && command.preview)
        return Response.json(await this.preview(job, command.preview))
      if (path === '/start') {
        this.ctx.waitUntil(this.exclusive(() => this.attach(job)))
        return Response.json({ attached: true }, { status: 202 })
      }
      if (path === '/reconcile') {
        await this.exclusive(() => this.reconcile(job))
        return Response.json({ reconciled: true })
      }
      if (path === '/cancel') {
        return await this.exclusive(async () => {
          const current = await this.store.job(job.tenant_id, job.id)
          if (['ready', 'failed', 'cancelled'].includes(current.state))
            return Response.json({
              cancelRequested: false,
              state: current.state,
            })
          const grant = await this.capacity().holder()
          if (current.state === 'queued' && grant?.job_id !== current.id) {
            await this.update(current, 'cancelled', {
              phase: 'cancelled-before-capacity',
            })
            await this.ctx.storage.deleteAlarm()
            return Response.json({ cancelRequested: true })
          }
          await this.update(current, 'cancel-requested', {
            phase: 'cancellation-requested',
          })
          if (!this.ctx.container)
            throw new EditorError(
              409,
              'cancel_uncertain',
              'Owned container lifecycle is unavailable; reconcile before retrying.',
            )
          await this.ctx.container.destroy()
          if (this.ctx.container.running)
            throw new EditorError(
              409,
              'cancel_uncertain',
              'Owned render runtime is still running.',
            )
          if (
            grant?.job_id === current.id &&
            grant.tenant_id === current.tenant_id &&
            grant.purpose === 'render'
          )
            await this.capacity().release(grant)
          await this.update(current, 'cancelled', {
            phase: 'owned-runtime-terminated',
          })
          await this.ctx.storage.deleteAlarm()
          return Response.json({ cancelRequested: true })
        })
      }
      if (path === '/verify' && command.outputId) {
        const snapshot = await this.store.inspect(
          job.tenant_id,
          job.project_id,
          job.revision,
        )
        const comp = snapshot.project.compositions.find(
          candidate => candidate.id === command.outputId,
        )
        if (!comp || job.state !== 'ready')
          throw new EditorError(
            409,
            'output_not_ready',
            'A completed output is required.',
          )
        const outputId = command.outputId
        return await this.withVerification(job, async () =>
          Response.json(await this.verify(job, outputId, comp)),
        )
      }
      throw new EditorError(
        404,
        'render_route',
        'Unknown render coordination route.',
      )
    } catch (error) {
      return Response.json(
        {
          code: error instanceof EditorError ? error.code : 'render_internal',
          error:
            error instanceof Error
              ? error.message
              : 'Render coordination failed.',
        },
        {
          status: error instanceof EditorError ? error.status : 500,
          headers:
            error instanceof EditorError &&
            error.code === 'render_capacity_busy'
              ? { 'Retry-After': '5' }
              : {},
        },
      )
    }
  }
  async alarm() {
    const verification =
      await this.ctx.storage.get<CapacityGrant>('verification')
    if (verification) {
      await this.exclusive(async () => {
        const current =
          await this.ctx.storage.get<CapacityGrant>('verification')
        if (current?.token !== verification.token) return
        const job = await this.store.job(
          verification.tenant_id,
          verification.job_id,
        )
        await this.terminate(job, 'verify')
        await this.ctx.storage.delete('verification')
        const active = await this.ctx.storage.get<{ jobId: string }>('active')
        if (!active || active.jobId === job.id)
          await this.ctx.storage.deleteAlarm()
      })
      return
    }
    const active = await this.ctx.storage.get<{
      jobId: string
      tenant: string
    }>('active')
    if (active)
      await this.exclusive(async () =>
        this.reconcile(
          Schema.decodeUnknownSync(JobRow)(
            await this.store.db.first(
              'SELECT * FROM editor_jobs WHERE id=? AND tenant_id=?',
              [active.jobId, active.tenant],
            ),
          ),
        ),
      )
  }
}
