import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { Effect } from "effect";
import { afterEach, describe, expect, it } from "vitest";
import {
  makeId,
  makeNativeSchemaVersion,
  makeSha256,
  makeStudioApplication,
  openFileStore,
  type NativeBridge,
  type NativeProjectProvisioner,
  type ProviderBridge,
  type TenantContext,
} from "../src/index";

const roots: string[] = [];
const openedStores: Array<{ readonly close: () => Effect.Effect<void, unknown> }> = [];
const run = <A, E>(effect: Effect.Effect<A, E>) => Effect.runPromise(effect);

const makeContext = async (tenant: string, actor: string): Promise<TenantContext> => ({
  tenantId: await run(makeId("TenantId", tenant)),
  actorId: await run(makeId("ActorId", actor)),
});

const id = async <K extends Parameters<typeof makeId>[0]>(kind: K, value: string) =>
  run(makeId(kind, value));

const hash = async (value: string) => run(makeSha256(value.repeat(64 / value.length)));

const makeProvisioner = (
  overrides: Readonly<Record<string, string>> = {},
): NativeProjectProvisioner => ({
  provision: (context, request) => {
    const key = `${context.tenantId.value}/${request.projectId.value}`;
    const value = overrides[key] ?? `native-${context.tenantId.value}-${request.projectId.value}`;
    return Effect.succeed({
      nativeProjectId: { kind: "NativeProjectId" as const, value },
      schemaVersion: { kind: "NativeSchemaVersion" as const, value: "cli-v1" },
    });
  },
});

const setup = async (
  provider?: ProviderBridge,
  native?: NativeBridge,
  provisioner: NativeProjectProvisioner = makeProvisioner(),
) => {
  const root = await mkdtemp(join(tmpdir(), "video-studio-application-a02-"));
  roots.push(root);
  const opened = await run(openFileStore(root, provisioner));
  openedStores.push(opened);
  return {
    root,
    opened,
    store: opened.service,
    app: makeStudioApplication(opened.service, provider, native),
  };
};

afterEach(async () => {
  while (openedStores.length > 0) {
    const opened = openedStores.pop();
    if (opened !== undefined) await run(opened.close());
  }
  while (roots.length > 0) {
    const root = roots.pop();
    if (root !== undefined) await rm(root, { recursive: true, force: true });
  }
});

describe("tenant-scoped application store", () => {
  it("persists every collection and keeps records inside one tenant", async () => {
    const { root, app, opened } = await setup();
    const context = await makeContext("tenant-a", "actor-a");
    const other = await makeContext("tenant-b", "actor-b");
    const source = { sha256: await hash("a"), bytes: 120 };
    const project = await run(
      app.createProject(context, {
        projectId: await id("ProjectId", "project-a"),
        source,
        createIntentId: await id("IntentId", "create-a"),
        now: 100,
      }),
    );
    const asset = await run(
      app.createAsset(context, {
        assetId: await id("AssetId", "asset-a"),
        projectId: project.projectId,
        revision: project.revision,
        source,
        declaredBy: context.actorId,
        now: 101,
      }),
    );
    await run(
      app.createReview(context, {
        reviewId: await id("ReviewId", "review-a"),
        projectId: project.projectId,
        revision: project.revision,
        plan: source.sha256,
        output: source.sha256,
        renderer: source.sha256,
        disposition: "Pending",
        now: 102,
      }),
    );
    const budget = await run(
      app.reserveBudget(context, {
        budgetId: await id("BudgetId", "budget-a"),
        projectId: project.projectId,
        limitUnits: 10,
        requestedUnits: 4,
        now: 103,
      }),
    );
    const job = await run(
      app.createJob(context, {
        jobId: await id("JobId", "job-a"),
        projectId: project.projectId,
        revision: project.revision,
        intentId: await id("IntentId", "job-intent-a"),
        requestFingerprint: source.sha256,
        now: 104,
      }),
    );
    const claim = await run(
      app.claimWorker(context, {
        claimId: await id("WorkerClaimId", "claim-a"),
        jobId: job.jobId,
        workerId: "worker-a",
        fence: 1,
        leaseExpiresAt: 500,
        now: 105,
      }),
    );
    await expect(
      run(
        app.releaseWorker(context, {
          claimId: claim.claimId,
          workerId: "worker-b",
          fence: 1,
          releasedAt: 106,
        }),
      ),
    ).rejects.toMatchObject({ _tag: "WorkerLeaseConflict" });
    await run(
      app.releaseWorker(context, {
        claimId: claim.claimId,
        workerId: "worker-a",
        fence: 1,
        releasedAt: 106,
      }),
    );
    await expect(
      run(
        app.releaseWorker(context, {
          claimId: claim.claimId,
          workerId: "worker-a",
          fence: 1,
          releasedAt: 107,
        }),
      ),
    ).rejects.toMatchObject({ _tag: "WorkerLeaseConflict" });
    await expect(
      run(
        app.claimWorker(context, {
          claimId: await id("WorkerClaimId", "claim-c"),
          jobId: job.jobId,
          workerId: "worker-c",
          fence: 1,
          leaseExpiresAt: 700,
          now: 107,
        }),
      ),
    ).rejects.toMatchObject({ _tag: "WorkerLeaseConflict" });
    await run(
      app.claimWorker(context, {
        claimId: await id("WorkerClaimId", "claim-b"),
        jobId: job.jobId,
        workerId: "worker-b",
        fence: 2,
        leaseExpiresAt: 600,
        now: 107,
      }),
    );
    const delivery = await run(
      app.createDelivery(context, {
        deliveryId: await id("DeliveryId", "delivery-a"),
        projectId: project.projectId,
        revision: project.revision,
        assetId: asset.assetId,
        now: 108,
      }),
    );
    expect(delivery.state._tag).toBe("Prepared");
    expect(budget.reservedUnits).toBe(4);
    expect(claim.state._tag).toBe("Active");
    await expect(run(app.authorizeProject(other, project.projectId))).rejects.toMatchObject({
      _tag: "RecordNotFound",
    });

    await run(opened.close());
    const reopened = await run(openFileStore(root));
    openedStores.push(reopened);
    const state = await run(reopened.service.readState(context));
    expect(state.projects).toHaveLength(1);
    expect(state.assets).toHaveLength(1);
    expect(state.jobs).toHaveLength(1);
    expect(state.attempts).toHaveLength(0);
    expect(state.reviews).toHaveLength(1);
    expect(state.budgets).toHaveLength(1);
    expect(state.workerClaims).toHaveLength(2);
    expect(state.deliveries).toHaveLength(1);
    expect(state.tenantId.value).toBe("tenant-a");
    await expect(run(reopened.service.readState(other))).resolves.toMatchObject({
      projects: [],
      assets: [],
      jobs: [],
      deliveries: [],
    });
    await expect(run(opened.service.readState(context))).rejects.toMatchObject({
      _tag: "StorageError",
      operation: "read",
    });
  });

  it("requires the trusted provisioning seam and publishes ownership before state", async () => {
    const root = await mkdtemp(join(tmpdir(), "video-studio-application-unconfigured-"));
    roots.push(root);
    const opened = await run(openFileStore(root));
    openedStores.push(opened);
    const app = makeStudioApplication(opened.service);
    const context = await makeContext("tenant-a", "actor-a");
    const source = { sha256: await hash("f"), bytes: 4 };
    await expect(
      run(
        app.createProject(context, {
          projectId: await id("ProjectId", "project-a"),
          source,
          createIntentId: await id("IntentId", "create-a"),
          now: 1,
        }),
      ),
    ).rejects.toMatchObject({ _tag: "NativeProvisioningUnavailable" });
  });

  it("binds semantic idempotence to all identifiers and fields", async () => {
    const { app } = await setup();
    const context = await makeContext("tenant-a", "actor-a");
    const source = { sha256: await hash("b"), bytes: 80 };
    const input = {
      projectId: await id("ProjectId", "project-a"),
      source,
      createIntentId: await id("IntentId", "create-a"),
      now: 200,
    };
    const first = await run(app.createProject(context, input));
    expect(await run(app.createProject(context, input))).toEqual(first);
    await expect(
      run(
        app.createProject(context, {
          ...input,
          projectId: await id("ProjectId", "project-b"),
        }),
      ),
    ).rejects.toMatchObject({ _tag: "IdempotencyConflict" });
    await expect(
      run(app.createProject(context, { ...input, source: { ...source, bytes: 81 } })),
    ).rejects.toMatchObject({ _tag: "IdempotencyConflict" });
  });

  it("persists before the provider callback and reconciles without blind retry", async () => {
    let submissions = 0;
    let reconciliations = 0;
    let observeDuringSubmit: (() => Promise<void>) | undefined;
    const provider: ProviderBridge = {
      submit: () =>
        Effect.tryPromise({
          try: async () => {
            submissions += 1;
            await observeDuringSubmit?.();
            return { _tag: "Unknown" as const, reason: "The provider response was lost." };
          },
          catch: () => ({ _tag: "ProviderUnconfigured" as const, provider: "test" }),
        }),
      reconcile: () =>
        Effect.sync(() => {
          reconciliations += 1;
          return { _tag: "Confirmed" as const, providerReference: "provider-job-a" };
        }),
    };
    const { app, store, root, opened } = await setup(provider);
    const context = await makeContext("tenant-a", "actor-a");
    const source = { sha256: await hash("c"), bytes: 12 };
    const project = await run(
      app.createProject(context, {
        projectId: await id("ProjectId", "project-a"),
        source,
        createIntentId: await id("IntentId", "create-a"),
        now: 300,
      }),
    );
    const job = await run(
      app.createJob(context, {
        jobId: await id("JobId", "job-a"),
        projectId: project.projectId,
        revision: project.revision,
        intentId: await id("IntentId", "job-intent-a"),
        requestFingerprint: source.sha256,
        now: 301,
      }),
    );
    observeDuringSubmit = async () => {
      const state = await run(store.readState(context));
      expect(state.jobs[0]?.state._tag).toBe("Submitting");
      expect(state.attempts).toHaveLength(1);
      expect(state.submissionIntents).toHaveLength(1);
    };
    const submission = {
      submissionIntentId: await id("IntentId", "submit-a"),
      attemptId: await id("AttemptId", "attempt-a"),
      jobId: job.jobId,
      provider: "unconfigured-test-provider",
      requestFingerprint: source.sha256,
      now: 302,
    };
    const unknown = await run(app.submitJob(context, submission));
    expect(unknown.state._tag).toBe("Unknown");
    expect(submissions).toBe(1);
    await expect(run(app.submitJob(context, submission))).rejects.toMatchObject({
      _tag: "ReconciliationRequired",
    });
    const reconciled = await run(app.reconcileJob(context, submission.submissionIntentId));
    expect(reconciled.state).toEqual({
      _tag: "Confirmed",
      providerReference: "provider-job-a",
    });
    expect(reconciliations).toBe(1);
    await expect(
      run(
        store.recordSubmission(context, submission.submissionIntentId, {
          _tag: "Confirmed",
          providerReference: "a-different-reference",
        }),
      ),
    ).rejects.toMatchObject({ _tag: "IdempotencyConflict" });
    await run(store.readState(context));
    await run(opened.close());
    const reopened = await run(openFileStore(root));
    openedStores.push(reopened);
    const reopenedState = await run(reopened.service.readState(context));
    expect(reopenedState.attempts).toHaveLength(1);
    expect(reopenedState.submissionIntents).toHaveLength(1);
    expect(reopenedState.jobs[0]?.state).toEqual({
      _tag: "Running",
      providerReference: "provider-job-a",
    });
  });

  it("binds native receipts to the authoritative mapping and source", async () => {
    const context = await makeContext("tenant-native", "actor-native");
    const schemaVersion = await run(makeNativeSchemaVersion("cli-v1"));
    const source = { sha256: await hash("e"), bytes: 20 };
    const receiptId = await id("NativeReceiptId", "native-receipt");
    const nativeProjectId = await id("NativeProjectId", "native-owner");
    const projectId = await id("ProjectId", "native-project");
    const timeline = await id("NativeTimelineIdentity", "timeline-a");
    const native: NativeBridge = {
      verifyReceipt: () =>
        Effect.succeed({
          receiptId,
          schemaVersion,
          nativeProjectId,
          projectId,
          revision: 0,
          source,
          timeline,
        }),
    };
    const { app, store } = await setup(
      undefined,
      native,
      makeProvisioner({ "tenant-native/native-project": "native-owner" }),
    );
    const project = await run(
      app.createProject(context, {
        projectId,
        source,
        createIntentId: await id("IntentId", "native-create"),
        now: 400,
      }),
    );
    await expect(
      run(
        app.registerNativeAsset(context, {
          assetId: await id("AssetId", "native-asset-bad"),
          projectId: project.projectId,
          revision: 0,
          source: { ...source, bytes: 21 },
          now: 401,
          nativeReceipt: {},
        }),
      ),
    ).rejects.toMatchObject({ _tag: "NativeReceiptInvalid" });
    const nativeAsset = await run(
      app.registerNativeAsset(context, {
        assetId: await id("AssetId", "native-asset-ok"),
        projectId: project.projectId,
        revision: 0,
        source,
        now: 402,
        nativeReceipt: { encoded: "fixture" },
      }),
    );
    expect(nativeAsset.origin._tag).toBe("NativeOutput");
    await expect(
      run(
        store.createAsset(context, {
          assetId: await id("AssetId", "native-asset-bypass"),
          projectId: project.projectId,
          revision: 0,
          origin:
            nativeAsset.origin._tag === "NativeOutput"
              ? { _tag: "NativeOutput", receipt: { ...nativeAsset.origin.receipt } }
              : nativeAsset.origin,
          source,
          now: 403,
        }),
      ),
    ).rejects.toMatchObject({ _tag: "StorageError" });
    await expect(
      run(
        store.createNativeAsset(context, {
          assetId: await id("AssetId", "native-asset-unverified"),
          projectId: project.projectId,
          revision: 0,
          origin:
            nativeAsset.origin._tag === "NativeOutput"
              ? { _tag: "NativeOutput", receipt: { ...nativeAsset.origin.receipt } }
              : nativeAsset.origin,
          source,
          now: 404,
        }),
      ),
    ).rejects.toMatchObject({ _tag: "NativeReceiptInvalid" });
  });

  it("rejects malformed, foreign, scalar, and non-finite boundaries", async () => {
    const { root, store } = await setup();
    const context = await makeContext("tenant-a", "actor-a");
    const tenantDir = join(root, "tenants", "tenant-a");
    const statePath = join(tenantDir, "state.json");
    await mkdir(tenantDir, { recursive: true });
    await writeFile(statePath, '{"schema":1,"projects":"bad"}');
    await expect(run(store.readState(context))).rejects.toMatchObject({ _tag: "StorageError" });
    await writeFile(
      statePath,
      JSON.stringify({
        schema: 1,
        tenantId: "tenant-b",
        projects: [],
        assets: [],
        jobs: [],
        attempts: [],
        reviews: [],
        budgets: [],
        workerClaims: [],
        submissionIntents: [],
        deliveries: [],
      }),
    );
    await expect(run(store.readState(context))).rejects.toMatchObject({
      _tag: "TenantAccessDenied",
    });
    await expect(
      run(
        store.reserveBudget(context, {
          budgetId: await id("BudgetId", "budget-a"),
          projectId: await id("ProjectId", "project-a"),
          limitUnits: Number.NaN,
          requestedUnits: 1,
          now: 1,
        }),
      ),
    ).rejects.toMatchObject({ _tag: "InvalidNumber" });
    await expect(run(makeId("TenantId", "../escape"))).rejects.toMatchObject({
      _tag: "InvalidIdentifier",
    });
    await expect(
      run(
        store.readState({
          tenantId: { kind: "TenantId", value: "../escape" },
          actorId: context.actorId,
        } as TenantContext),
      ),
    ).rejects.toMatchObject({ _tag: "StorageError", operation: "context" });
    await expect(
      run(
        store.claimWorker(context, {
          claimId: await id("WorkerClaimId", "claim-invalid"),
          jobId: await id("JobId", "job-invalid"),
          workerId: "worker-invalid",
          fence: Number.POSITIVE_INFINITY,
          leaseExpiresAt: 1,
          now: 0,
        }),
      ),
    ).rejects.toMatchObject({ _tag: "InvalidNumber" });
  });

  it("rejects a full collection before publishing an over-cap state", async () => {
    const { app } = await setup();
    const context = await makeContext("tenant-cap", "actor-cap");
    const source = { sha256: await hash("a"), bytes: 8 };
    const project = await run(
      app.createProject(context, {
        projectId: await id("ProjectId", "project-cap"),
        source,
        createIntentId: await id("IntentId", "create-cap"),
        now: 1,
      }),
    );
    for (let index = 0; index < 1024; index += 1)
      await run(
        app.createAsset(context, {
          assetId: await id("AssetId", `asset-${index}`),
          projectId: project.projectId,
          revision: project.revision,
          source,
          declaredBy: context.actorId,
          now: index + 2,
        }),
      );
    await expect(
      run(
        app.createAsset(context, {
          assetId: await id("AssetId", "asset-over-cap"),
          projectId: project.projectId,
          revision: project.revision,
          source,
          declaredBy: context.actorId,
          now: 2_000,
        }),
      ),
    ).rejects.toMatchObject({ _tag: "StorageError" });
  }, 30_000);

  it("enforces one store per root and permits same identifiers across tenants", async () => {
    const root = await mkdtemp(join(tmpdir(), "video-studio-application-lock-"));
    roots.push(root);
    const first = await run(
      openFileStore(
        root,
        makeProvisioner({
          "tenant-a/same-project": "native-a",
          "tenant-b/same-project": "native-b",
          "tenant-b/other-project": "native-a",
        }),
      ),
    );
    openedStores.push(first);
    await expect(run(openFileStore(root))).rejects.toMatchObject({
      _tag: "StorageError",
      operation: "open",
    });
    const app = makeStudioApplication(first.service);
    const tenantA = await makeContext("tenant-a", "actor-a");
    const tenantB = await makeContext("tenant-b", "actor-b");
    const source = { sha256: await hash("d"), bytes: 2 };
    const common = {
      projectId: await id("ProjectId", "same-project"),
      source,
      createIntentId: await id("IntentId", "same-intent"),
      now: 1,
    };
    await run(
      app.createProject(tenantA, {
        ...common,
      }),
    );
    await run(
      app.createProject(tenantB, {
        ...common,
      }),
    );
    await expect(
      run(
        app.createProject(tenantB, {
          ...common,
          projectId: await id("ProjectId", "other-project"),
          createIntentId: await id("IntentId", "other-intent"),
        }),
      ),
    ).rejects.toMatchObject({ _tag: "TenantAccessDenied" });
    await run(first.close());
    const reopened = await run(openFileStore(root));
    openedStores.push(reopened);
    expect((await run(reopened.service.readState(tenantA))).projects).toHaveLength(1);
    expect((await run(reopened.service.readState(tenantB))).projects).toHaveLength(1);
  });
});
