import { Context, Effect, Schema } from "effect";
import { type Job, JobSchema, type RouterError, canonicalJson, fault } from "./domain";

type Values = ReadonlyArray<string | number>;
export interface Sql {
  readonly first: (query: string, values: Values) => Effect.Effect<unknown, RouterError>;
  readonly all: (
    query: string,
    values: Values,
  ) => Effect.Effect<ReadonlyArray<unknown>, RouterError>;
  readonly run: (query: string, values: Values) => Effect.Effect<number, RouterError>;
}
export class JobStore extends Context.Service<
  JobStore,
  {
    readonly principal: (hash: string) => Effect.Effect<string | null, RouterError>;
    readonly findIntent: (tenant: string, intent: string) => Effect.Effect<Job | null, RouterError>;
    readonly create: (job: Job) => Effect.Effect<Job, RouterError>;
    readonly get: (tenant: string, id: string) => Effect.Effect<Job, RouterError>;
    readonly active: () => Effect.Effect<ReadonlyArray<Job>, RouterError>;
    readonly save: (job: Job, expectedVersion: number) => Effect.Effect<boolean, RouterError>;
  }
>()("gpu-router/JobStore") {}

const DocumentRow = Schema.Struct({ document_json: Schema.String });
const decodeRow = (value: unknown) =>
  Effect.try({
    try: () =>
      value === null
        ? null
        : Schema.decodeUnknownSync(JobSchema)(
            JSON.parse(Schema.decodeUnknownSync(DocumentRow)(value).document_json),
          ),
    catch: () => fault(500, "invalid_job_record", "The saved job record could not be decoded."),
  });
export const sqlStore = (sql: Sql): typeof JobStore.Service => {
  const findIntent = (tenant: string, intent: string) =>
    sql
      .first("SELECT document_json FROM jobs WHERE tenant_id=? AND intent_id=?", [tenant, intent])
      .pipe(Effect.flatMap(decodeRow));
  return {
    principal: (hash) =>
      sql.first("SELECT tenant_id FROM api_keys WHERE token_hash=? AND enabled=1", [hash]).pipe(
        Effect.flatMap((row) =>
          Effect.try({
            try: () =>
              row === null
                ? null
                : Schema.decodeUnknownSync(Schema.Struct({ tenant_id: Schema.String }))(row)
                    .tenant_id,
            catch: () =>
              fault(500, "invalid_key_record", "The API key record could not be decoded."),
          }),
        ),
      ),
    findIntent,
    create: (job) =>
      Effect.gen(function* () {
        yield* sql.run(
          "INSERT OR IGNORE INTO jobs(id,tenant_id,intent_id,fingerprint,version,active,document_json) VALUES(?,?,?,?,?,1,?)",
          [job.id, job.tenantId, job.intentId, job.fingerprint, job.version, canonicalJson(job)],
        );
        const saved = yield* findIntent(job.tenantId, job.intentId);
        if (saved === null)
          return yield* Effect.fail(fault(500, "job_write_failed", "The job was not saved."));
        if (saved.fingerprint !== job.fingerprint)
          return yield* Effect.fail(
            fault(
              409,
              "idempotency_conflict",
              "This idempotency key was used with a different job request.",
            ),
          );
        return saved;
      }),
    get: (tenant, id) =>
      Effect.gen(function* () {
        const job = yield* sql
          .first("SELECT document_json FROM jobs WHERE tenant_id=? AND id=?", [tenant, id])
          .pipe(Effect.flatMap(decodeRow));
        if (job === null) return yield* Effect.fail(fault(404, "job_not_found", "Job not found."));
        return job;
      }),
    active: () =>
      sql
        .all("SELECT document_json FROM jobs WHERE active=1 ORDER BY id LIMIT 100", [])
        .pipe(
          Effect.flatMap((rows) =>
            Effect.forEach(rows, (row) =>
              decodeRow(row).pipe(
                Effect.flatMap((job) =>
                  job === null
                    ? Effect.fail(fault(500, "invalid_job_record", "An active job is missing."))
                    : Effect.succeed(job),
                ),
              ),
            ),
          ),
        ),
    save: (job, expected) =>
      sql
        .run(
          "UPDATE jobs SET version=?,active=?,document_json=? WHERE tenant_id=? AND id=? AND version=?",
          [
            job.version,
            job.state._tag === "Finished" ? 0 : 1,
            canonicalJson(job),
            job.tenantId,
            job.id,
            expected,
          ],
        )
        .pipe(Effect.map((changes) => changes === 1)),
  };
};

export const change = (tenant: string, id: string, update: (job: Job) => Job) =>
  Effect.gen(function* () {
    const store = yield* JobStore;
    for (let retry = 0; retry < 32; retry++) {
      const current = yield* store.get(tenant, id);
      const changed = update(current);
      if (changed === current) return current;
      const next = { ...changed, version: current.version + 1, updatedAt: Date.now() };
      if (yield* store.save(next, current.version)) return next;
    }
    return yield* Effect.fail(
      fault(409, "job_busy", "The job changed concurrently. Retry this read or cancellation."),
    );
  });
