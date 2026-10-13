import { afterEach, describe, expect, test } from "bun:test";
import { Database } from "bun:sqlite";
import { Effect, Layer } from "effect";
import { api } from "../src/api";
import { type JobRequest, type Offer, fault, sha256 } from "../src/domain";
import { advanceJob, cancelJob, createJob } from "../src/engine";
import { type Provider, Providers } from "../src/providers";
import { rank } from "../src/routing";
import { simulationMigration, simulationProvider } from "../src/simulation";
import { sqliteSql } from "../src/sqlite";
import { JobStore, change, sqlStore } from "../src/store";

const migration = await Bun.file(new URL("../migrations/0001_jobs.sql", import.meta.url)).text();
const databases: Array<Database> = [];
afterEach(() => {
  for (const db of databases.splice(0)) db.close();
});
const request: JobRequest = {
  workload: {
    kind: "container",
    image: `example/runner@sha256:${"a".repeat(64)}`,
    command: ["python", "run.py"],
    input: { prompt: "hello" },
  },
  gpu: { count: 1, minVramGb: 24 },
  limits: { maxQueueSeconds: 300, maxRuntimeSeconds: 600, maxCostUsd: 2 },
  routing: { strategy: "lowest_cost", regions: ["us"], providers: [], allowInterruptible: false },
};
const harness = async (
  custom?: (base: ReadonlyArray<Provider>) => ReadonlyArray<Provider>,
  customStore?: (store: typeof JobStore.Service) => typeof JobStore.Service,
) => {
  const db = new Database(":memory:");
  databases.push(db);
  db.exec(migration);
  db.exec(simulationMigration);
  db.query("INSERT INTO api_keys(token_hash,tenant_id) VALUES(?,?)").run(
    await sha256("alice-key"),
    "alice",
  );
  db.query("INSERT INTO api_keys(token_hash,tenant_id) VALUES(?,?)").run(
    await sha256("bob-key"),
    "bob",
  );
  const sql = sqliteSql(db);
  const store = sqlStore(sql);
  const a = simulationProvider(sql, "simulated-a", 200, 5);
  const b = simulationProvider(sql, "simulated-b", 400, 1);
  const providers = custom?.([a, b]) ?? [a, b];
  const services = Layer.merge(
    Layer.succeed(JobStore, customStore?.(store) ?? store),
    Layer.succeed(Providers, providers),
  );
  const run = <A, E>(effect: Effect.Effect<A, E, JobStore | Providers>) =>
    Effect.runPromise(effect.pipe(Effect.provide(services)));
  const http = (
    path: string,
    method = "GET",
    body?: JobRequest,
    key = "alice-key",
    intent = "one",
  ) =>
    run(
      api(
        new Request(`http://localhost${path}`, {
          method,
          headers: {
            Authorization: `Bearer ${key}`,
            "Content-Type": "application/json",
            "Idempotency-Key": intent,
          },
          ...(body === undefined ? {} : { body: JSON.stringify(body) }),
        }),
      ),
    );
  return { db, sql, store, run, http };
};
const offer: Offer = {
  id: "one",
  providerId: "simulated-a",
  mode: "simulation",
  workloads: ["container"],
  gpuCount: 1,
  vramGbPerGpu: 24,
  region: "us",
  interruptible: false,
  microsPerSecond: 200,
  fixedCostMicros: 1000,
  startupSeconds: 5,
  expiresAt: Date.now() + 60000,
};

describe("routing constraints", () => {
  test("includes startup and fixed costs in the estimate", () => {
    expect(rank(request, [offer], Date.now())[0]?.estimatedMaxCostMicros).toBe(122000);
    expect(
      rank({ ...request, limits: { ...request.limits, maxCostUsd: 0.1 } }, [offer], Date.now()),
    ).toHaveLength(0);
  });
  test("requires memory per GPU and the requested GPU count", () => {
    expect(rank(request, [{ ...offer, gpuCount: 2, vramGbPerGpu: 12 }], Date.now())).toHaveLength(
      0,
    );
    expect(rank(request, [{ ...offer, gpuCount: 2 }], Date.now())).toHaveLength(0);
  });
  test("filters expired offers, unsupported workloads, regions, and interruptible hardware", () => {
    expect(
      rank(
        request,
        [
          { ...offer, expiresAt: Date.now() - 1 },
          { ...offer, workloads: ["comfyui"] },
          { ...offer, region: "eu" },
          { ...offer, interruptible: true },
        ],
        Date.now(),
      ),
    ).toHaveLength(0);
  });
  test("uses the caller provider allowlist before scoring", () => {
    expect(
      rank(
        { ...request, routing: { ...request.routing, providers: ["other"] } },
        [offer],
        Date.now(),
      ),
    ).toHaveLength(0);
  });
  test("supports fastest startup without discarding the cost cap", () => {
    const fast = { ...offer, id: "fast", startupSeconds: 1, microsPerSecond: 400 };
    expect(
      rank(
        { ...request, routing: { ...request.routing, strategy: "fastest_start" } },
        [offer, fast],
        Date.now(),
      )[0]?.id,
    ).toBe("fast");
    expect(rank(request, [offer, fast], Date.now())[0]?.id).toBe("one");
  });
});

describe("API and durable job creation", () => {
  test("reports simulation honestly and requires authentication", async () => {
    const h = await harness();
    const health = await h.http("/health");
    expect(await health.json()).toMatchObject({
      simulation: true,
      gpuExecution: false,
      ready: true,
    });
    expect((await h.http("/v1/jobs", "POST", request, "unknown")).status).toBe(401);
  });
  test("an unconnected registry refuses jobs instead of reporting simulated capacity", async () => {
    const h = await harness(() => []);
    expect(await (await h.http("/health")).json()).toMatchObject({
      simulation: false,
      gpuExecution: false,
      ready: false,
    });
    expect((await h.http("/v1/jobs", "POST", request)).status).toBe(503);
  });
  test("rejects oversized streamed bodies without trusting Content-Length", async () => {
    const h = await harness();
    const response = await h.run(
      api(
        new Request("http://localhost/v1/jobs", {
          method: "POST",
          headers: {
            Authorization: "Bearer alice-key",
            "Content-Type": "application/json",
            "Idempotency-Key": "large",
          },
          body: JSON.stringify({
            ...request,
            workload: { ...request.workload, input: "x".repeat(1_048_576) },
          }),
        }),
      ),
    );
    expect(response.status).toBe(400);
    expect(h.db.query("SELECT count(*) AS n FROM jobs").get()).toEqual({ n: 0 });
  });
  test("rejects mutable container tags and missing idempotency keys", async () => {
    const h = await harness();
    expect(
      (
        await h.http("/v1/jobs", "POST", {
          ...request,
          workload: {
            ...request.workload,
            kind: "container",
            image: "runner:latest",
            command: [],
            input: null,
          },
        })
      ).status,
    ).toBe(400);
    expect((await h.http("/v1/jobs", "POST", request, "alice-key", "")).status).toBe(400);
  });
  test("concurrent identical submissions create one job and one resource", async () => {
    const h = await harness();
    const jobs = await Promise.all(
      Array.from({ length: 8 }, () => h.run(createJob("alice", "same-intent", request))),
    );
    expect(new Set(jobs.map((job) => job.id)).size).toBe(1);
    const first = jobs[0]!;
    await Promise.all(Array.from({ length: 8 }, () => h.run(advanceJob("alice", first.id))));
    expect(h.db.query("SELECT count(*) AS n FROM simulation_resources").get()).toEqual({ n: 1 });
  });
  test("returns conflicts for reuse with different input", async () => {
    const h = await harness();
    await h.http("/v1/jobs", "POST", request);
    expect(
      (await h.http("/v1/jobs", "POST", { ...request, gpu: { count: 1, minVramGb: 16 } })).status,
    ).toBe(409);
  });
  test("tenant keys cannot read or cancel another tenant job", async () => {
    const h = await harness();
    const job = await h.run(createJob("alice", "one", request));
    expect((await h.http(`/v1/jobs/${job.id}`, "GET", undefined, "bob-key")).status).toBe(404);
    expect((await h.http(`/v1/jobs/${job.id}/cancel`, "POST", undefined, "bob-key")).status).toBe(
      404,
    );
    expect((await h.run(h.store.get("alice", job.id))).cancelRequested).toBe(false);
  });
  test("persists intent across repository instances and ignores JSON object key order", async () => {
    const h = await harness();
    const job = await h.run(createJob("alice", "one", request));
    const other = sqlStore(sqliteSql(h.db));
    const saved = await Effect.runPromise(other.findIntent("alice", "one"));
    expect(saved?.id).toBe(job.id);
    const reordered: JobRequest = {
      routing: request.routing,
      limits: request.limits,
      gpu: request.gpu,
      workload: request.workload,
    };
    expect((await h.run(createJob("alice", "one", reordered))).id).toBe(job.id);
  });
});

describe("resource lifecycle", () => {
  test("finishes only after artifact receipts and cleanup confirmation", async () => {
    const h = await harness();
    const job = await h.run(createJob("alice", "one", request));
    expect((await h.run(advanceJob("alice", job.id))).state._tag).toBe("Running");
    expect((await h.run(advanceJob("alice", job.id))).state._tag).toBe("CleanupPending");
    const finished = await h.run(advanceJob("alice", job.id));
    expect(finished.state._tag).toBe("Finished");
    if (finished.state._tag !== "Finished" || finished.state.result._tag !== "Succeeded")
      throw new Error("expected simulation output");
    const artifact = finished.state.result.artifacts[0]!;
    const text = atob(artifact.uri.split(",")[1]!);
    expect(text).toContain("No container, workflow, or GPU was executed.");
    expect(await sha256(text)).toBe(artifact.sha256);
    expect(new TextEncoder().encode(text).length).toBe(artifact.bytes);
    expect(h.db.query("SELECT released FROM simulation_resources").get()).toEqual({ released: 1 });
    expect(finished.attempts[0]?._tag).toBe("Accepted");
    const record = finished.attempts[0];
    if (record?._tag !== "Accepted") throw new Error("expected acceptance receipt");
    expect(record.releasedAt).not.toBeNull();
    expect(record.attempt.quote.providerId).toBe("simulated-a");
  });
  test("does not finish while cleanup fails", async () => {
    const h = await harness((base) =>
      base.map((provider) => ({ ...provider, release: () => Effect.succeed(false) })),
    );
    const job = await h.run(createJob("alice", "one", request));
    for (let i = 0; i < 4; i++) await h.run(advanceJob("alice", job.id));
    expect((await h.run(h.store.get("alice", job.id))).state._tag).toBe("CleanupPending");
  });
  test("a lost response blocks fallback and reconciles the original token", async () => {
    let submissions = 0;
    let found = false;
    const h = await harness((base) =>
      base.map((provider) => ({
        ...provider,
        submit: (req, attempt) =>
          provider.submit(req, attempt).pipe(
            Effect.tap(() =>
              Effect.sync(() => {
                submissions++;
              }),
            ),
            Effect.map(() => ({ _tag: "Unknown" as const, reason: "response lost" })),
          ),
        reconcile: (attempt) =>
          found ? provider.reconcile(attempt) : Effect.succeed({ _tag: "Unknown" as const }),
      })),
    );
    const job = await h.run(createJob("alice", "one", request));
    expect((await h.run(advanceJob("alice", job.id))).state._tag).toBe("Uncertain");
    for (let i = 0; i < 4; i++) await h.run(advanceJob("alice", job.id));
    expect(submissions).toBe(1);
    expect(h.db.query("SELECT count(*) AS n FROM simulation_resources").get()).toEqual({ n: 1 });
    found = true;
    expect((await h.run(advanceJob("alice", job.id))).state._tag).toBe("Running");
    expect(submissions).toBe(1);
  });
  test("fails over only after an explicit rejection with no created resource", async () => {
    const h = await harness((base) =>
      base.map((provider) =>
        provider.id === "simulated-a"
          ? {
              ...provider,
              submit: () => Effect.succeed({ _tag: "Rejected" as const, reason: "no capacity" }),
            }
          : provider,
      ),
    );
    const job = await h.run(createJob("alice", "one", request));
    expect((await h.run(advanceJob("alice", job.id))).state._tag).toBe("Queued");
    const running = await h.run(advanceJob("alice", job.id));
    expect(running.state._tag).toBe("Running");
    if (running.state._tag !== "Running") throw new Error("expected running");
    expect(running.state.attempt.quote.providerId).toBe("simulated-b");
    expect(h.db.query("SELECT count(*) AS n FROM simulation_resources").get()).toEqual({ n: 1 });
  });
  test("a typed submission failure is uncertain, never evidence of no resource", async () => {
    const h = await harness((base) =>
      base.map((provider) => ({
        ...provider,
        submit: () => Effect.fail(fault(502, "network", "connection lost")),
      })),
    );
    const job = await h.run(createJob("alice", "one", request));
    expect((await h.run(advanceJob("alice", job.id))).state._tag).toBe("Uncertain");
  });
  test("queued cancellation allocates no resource", async () => {
    const h = await harness();
    const job = await h.run(createJob("alice", "one", request));
    expect((await h.run(cancelJob("alice", job.id))).state).toEqual({
      _tag: "Finished",
      result: { _tag: "Cancelled" },
    });
    await h.run(advanceJob("alice", job.id));
    expect(h.db.query("SELECT count(*) AS n FROM simulation_resources").get()).toEqual({ n: 0 });
  });
  test("cancellation during submission preserves the returned resource for cleanup", async () => {
    let resume = () => {};
    let started = () => {};
    const gate = new Promise<void>((resolve) => {
      resume = resolve;
    });
    const entered = new Promise<void>((resolve) => {
      started = resolve;
    });
    const h = await harness((base) =>
      base.map((provider) => ({
        ...provider,
        submit: (req, attempt) =>
          provider.submit(req, attempt).pipe(
            Effect.flatMap((result) =>
              Effect.promise(async () => {
                started();
                await gate;
                return result;
              }),
            ),
          ),
      })),
    );
    const job = await h.run(createJob("alice", "one", request));
    const dispatch = h.run(advanceJob("alice", job.id));
    await entered;
    expect((await h.run(cancelJob("alice", job.id))).state._tag).toBe("Dispatching");
    expect((await h.run(advanceJob("alice", job.id))).state._tag).toBe("Dispatching");
    resume();
    expect((await dispatch).cancelRequested).toBe(true);
    expect((await h.run(advanceJob("alice", job.id))).state._tag).toBe("CleanupPending");
    expect((await h.run(advanceJob("alice", job.id))).state).toEqual({
      _tag: "Finished",
      result: { _tag: "Cancelled" },
    });
  });
  test("cancellation of an uncertain submission waits for authoritative reconciliation", async () => {
    const h = await harness((base) =>
      base.map((provider) => ({
        ...provider,
        submit: () => Effect.succeed({ _tag: "Unknown" as const, reason: "lost" }),
        reconcile: () => Effect.succeed({ _tag: "Unknown" as const }),
      })),
    );
    const job = await h.run(createJob("alice", "one", request));
    await h.run(advanceJob("alice", job.id));
    await h.run(cancelJob("alice", job.id));
    expect((await h.run(advanceJob("alice", job.id))).state._tag).toBe("Uncertain");
  });
  test("recovers acceptance after a database write failed without resubmitting", async () => {
    let failOnce = true;
    const h = await harness(undefined, (store) => ({
      ...store,
      save: (job, version) => {
        if (job.state._tag === "Running" && failOnce) {
          failOnce = false;
          return Effect.fail(fault(500, "storage_error", "simulated write loss"));
        }
        return store.save(job, version);
      },
    }));
    const job = await h.run(createJob("alice", "one", request));
    await expect(h.run(advanceJob("alice", job.id))).rejects.toThrow();
    await h.run(
      change("alice", job.id, (current) =>
        current.state._tag === "Dispatching"
          ? {
              ...current,
              state: { ...current.state, leaseUntil: Date.now() - 1 },
            }
          : current,
      ),
    );
    expect((await h.run(advanceJob("alice", job.id))).state._tag).toBe("Running");
    expect(h.db.query("SELECT count(*) AS n FROM simulation_resources").get()).toEqual({ n: 1 });
  });
  test("queue deadlines end jobs without creating resources", async () => {
    const h = await harness();
    const job = await h.run(createJob("alice", "one", request));
    await h.run(
      change("alice", job.id, (current) => ({ ...current, createdAt: Date.now() - 301000 })),
    );
    const expired = await h.run(advanceJob("alice", job.id));
    expect(expired.state).toEqual({
      _tag: "Finished",
      result: { _tag: "Failed", reason: "Queue deadline exceeded." },
    });
    expect(h.db.query("SELECT count(*) AS n FROM simulation_resources").get()).toEqual({ n: 0 });
  });
});
