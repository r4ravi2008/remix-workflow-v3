import { Effect, Schema } from "effect";
import {
  Artifact,
  type Attempt,
  type AttemptRecord,
  type Job,
  type JobRequest,
  type State,
  canonicalJson,
  fault,
  sha256,
} from "./domain";
import { type Provider, Providers } from "./providers";
import { quotes } from "./routing";
import { JobStore, change } from "./store";

export const createJob = (tenant: string, intent: string, request: JobRequest) =>
  Effect.gen(function* () {
    const store = yield* JobStore;
    const fingerprint = yield* Effect.promise(() => sha256(canonicalJson(request)));
    const previous = yield* store.findIntent(tenant, intent);
    if (previous !== null) {
      if (previous.fingerprint !== fingerprint)
        return yield* Effect.fail(
          fault(
            409,
            "idempotency_conflict",
            "This idempotency key was used with a different job request.",
          ),
        );
      return previous;
    }
    yield* quotes(request);
    const now = Date.now();
    return yield* store.create({
      id: crypto.randomUUID(),
      tenantId: tenant,
      intentId: intent,
      fingerprint,
      request,
      state: { _tag: "Queued" },
      rejectedProviders: [],
      attempts: [],
      cancelRequested: false,
      version: 0,
      createdAt: now,
      updatedAt: now,
    });
  });
export const cancelJob = (tenant: string, id: string) =>
  change(tenant, id, (job) => {
    if (job.state._tag === "Finished" || job.cancelRequested) return job;
    return {
      ...job,
      cancelRequested: true,
      state:
        job.state._tag === "Queued"
          ? { _tag: "Finished", result: { _tag: "Cancelled" } }
          : job.state,
    };
  });
const providerFor = (attempt: Attempt) =>
  Effect.gen(function* () {
    const providers = yield* Providers;
    return providers.find(
      (provider) =>
        provider.id === attempt.quote.providerId && provider.mode === attempt.quote.mode,
    );
  });
const sameAttempt = (state: State, token: string) =>
  state._tag !== "Queued" && state._tag !== "Finished" && state.attempt.token === token;
const receipt = (job: Job, record: AttemptRecord) =>
  job.attempts.map((previous) =>
    previous.attempt.token === record.attempt.token ? record : previous,
  );
const commit = (job: Job, attempt: Attempt, update: (current: Job) => Job) =>
  change(job.tenantId, job.id, (current) =>
    sameAttempt(current.state, attempt.token) ? update(current) : current,
  );
const submit = (job: Job, attempt: Attempt, provider: Provider) =>
  Effect.gen(function* () {
    const result = yield* provider.submit(job.request, attempt).pipe(
      Effect.timeout("10 seconds"),
      Effect.catch(() =>
        Effect.succeed({
          _tag: "Unknown" as const,
          reason: "Submission response was lost. Reconciliation is required.",
        }),
      ),
    );
    return yield* commit(job, attempt, (current) => {
      if (current.state._tag !== "Dispatching" && current.state._tag !== "Uncertain")
        return current;
      if (result._tag === "Accepted" && result.reference.length > 0)
        return {
          ...current,
          attempts: receipt(current, {
            _tag: "Accepted",
            attempt,
            reference: result.reference,
            releasedAt: null,
          }),
          state: { _tag: "Running", attempt, reference: result.reference },
        };
      if (result._tag === "Rejected")
        return {
          ...current,
          rejectedProviders: [...current.rejectedProviders, provider.id],
          attempts: receipt(current, { _tag: "Rejected", attempt, reason: result.reason }),
          state: current.cancelRequested
            ? { _tag: "Finished", result: { _tag: "Cancelled" } }
            : { _tag: "Queued" },
        };
      return {
        ...current,
        state: {
          _tag: "Uncertain",
          attempt,
          reason:
            result._tag === "Unknown" ? result.reason : "Provider returned an invalid reference.",
        },
      };
    });
  });

export const advanceJob = (
  tenant: string,
  id: string,
): Effect.Effect<Job, import("./domain").RouterError, JobStore | Providers> =>
  Effect.gen(function* () {
    const store = yield* JobStore;
    const job = yield* store.get(tenant, id);
    const state = job.state;
    if (state._tag === "Finished") return job;
    if (state._tag === "Queued") {
      if (Date.now() >= job.createdAt + job.request.limits.maxQueueSeconds * 1000)
        return yield* change(tenant, id, (current) =>
          current.state._tag === "Queued"
            ? {
                ...current,
                state: {
                  _tag: "Finished",
                  result: { _tag: "Failed", reason: "Queue deadline exceeded." },
                },
              }
            : current,
        );
      const available = yield* quotes(job.request, job.rejectedProviders).pipe(
        Effect.catch(() => Effect.succeed([])),
      );
      const quote = available[0];
      if (quote === undefined) return job;
      const attempt: Attempt = { token: crypto.randomUUID(), quote, startedAt: Date.now() };
      const claimed = {
        ...job,
        attempts: [...job.attempts, { _tag: "Pending" as const, attempt }],
        version: job.version + 1,
        updatedAt: Date.now(),
        state: { _tag: "Dispatching" as const, attempt, leaseUntil: Date.now() + 30000 },
      };
      if (!(yield* store.save(claimed, job.version))) return yield* store.get(tenant, id);
      const provider = yield* providerFor(attempt);
      if (provider === undefined) return claimed;
      return yield* submit(claimed, attempt, provider);
    }
    const provider = yield* providerFor(state.attempt);
    if (provider === undefined) return job;
    if (state._tag === "Dispatching" || state._tag === "Uncertain") {
      if (state._tag === "Dispatching" && state.leaseUntil > Date.now()) return job;
      const result = yield* provider.reconcile(state.attempt).pipe(
        Effect.timeout("10 seconds"),
        Effect.catch(() => Effect.succeed({ _tag: "Unknown" as const })),
      );
      return yield* commit(job, state.attempt, (current) => {
        if (current.state._tag !== "Dispatching" && current.state._tag !== "Uncertain")
          return current;
        if (result._tag === "Found" && result.reference.length > 0)
          return {
            ...current,
            attempts: receipt(current, {
              _tag: "Accepted",
              attempt: state.attempt,
              reference: result.reference,
              releasedAt: null,
            }),
            state: { _tag: "Running", attempt: state.attempt, reference: result.reference },
          };
        if (result._tag === "Absent")
          return {
            ...current,
            attempts: receipt(current, { _tag: "Absent", attempt: state.attempt }),
            state: current.cancelRequested
              ? { _tag: "Finished", result: { _tag: "Cancelled" } }
              : { _tag: "Queued" },
          };
        return {
          ...current,
          state: {
            _tag: "Uncertain",
            attempt: state.attempt,
            reason: "Provider has not established whether the submission created a resource.",
          },
        };
      });
    }
    if (state._tag === "CleanupPending") {
      const released = yield* provider.release(state.reference).pipe(
        Effect.timeout("10 seconds"),
        Effect.catch(() => Effect.succeed(false)),
      );
      if (!released) return job;
      return yield* commit(job, state.attempt, (current) =>
        current.state._tag === "CleanupPending"
          ? {
              ...current,
              attempts: receipt(current, {
                _tag: "Accepted",
                attempt: state.attempt,
                reference: state.reference,
                releasedAt: Date.now(),
              }),
              state: { _tag: "Finished", result: current.state.result },
            }
          : current,
      );
    }
    const elapsed = Date.now() - state.attempt.startedAt;
    if (
      job.cancelRequested ||
      elapsed > (job.request.limits.maxRuntimeSeconds + state.attempt.quote.startupSeconds) * 1000
    ) {
      return yield* commit(job, state.attempt, (current) =>
        current.state._tag === "Running"
          ? {
              ...current,
              state: {
                _tag: "CleanupPending",
                attempt: state.attempt,
                reference: state.reference,
                result: current.cancelRequested
                  ? { _tag: "Cancelled" }
                  : { _tag: "Failed", reason: "Runtime deadline exceeded." },
              },
            }
          : current,
      );
    }
    const progress = yield* provider.poll(state.reference).pipe(
      Effect.timeout("10 seconds"),
      Effect.catch(() => Effect.succeed({ _tag: "Running" as const })),
    );
    if (progress._tag === "Running") return job;
    const result =
      progress._tag === "Failed"
        ? progress
        : yield* Effect.try({
            try: () => ({
              _tag: "Succeeded" as const,
              artifacts: Schema.decodeUnknownSync(
                Schema.Array(Artifact).check(Schema.isMinLength(1)),
              )(progress.artifacts),
            }),
            catch: () =>
              fault(502, "invalid_receipt", "Provider returned an invalid artifact receipt."),
          }).pipe(
            Effect.catch((error) =>
              Effect.succeed({ _tag: "Failed" as const, reason: error.message }),
            ),
          );
    return yield* commit(job, state.attempt, (current) =>
      current.state._tag === "Running"
        ? {
            ...current,
            state: {
              _tag: "CleanupPending",
              attempt: state.attempt,
              reference: state.reference,
              result: current.cancelRequested ? { _tag: "Cancelled" } : result,
            },
          }
        : current,
    );
  });

export const tick = () =>
  Effect.gen(function* () {
    const store = yield* JobStore;
    const jobs = yield* store.active();
    yield* Effect.forEach(
      jobs,
      (job) =>
        advanceJob(job.tenantId, job.id).pipe(
          Effect.catch((error) => Effect.logError({ jobId: job.id, code: error.code })),
        ),
      { concurrency: 4, discard: true },
    );
  });
