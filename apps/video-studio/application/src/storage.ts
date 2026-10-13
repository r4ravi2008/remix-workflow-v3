import { constants } from "node:fs";
import { mkdir, open, rename, unlink, writeFile } from "node:fs/promises";
import { isAbsolute, join, resolve } from "node:path";
import { randomUUID } from "node:crypto";
import { Context, Effect, Schema } from "effect";
import {
  type AssetRecord,
  type AttemptRecord,
  type BudgetRecord,
  type ClaimWorkerInput,
  type CreateAssetInput,
  type CreateProjectRequest,
  type CreateJobInput,
  type CreateReviewInput,
  type DomainError,
  type EntityId,
  type IntentId,
  type JobRecord,
  type NativeReceipt,
  type ProjectId,
  type ProjectRecord,
  type PrepareSubmissionInput,
  type PrepareSubmissionResult,
  type ProviderReconciliationResult,
  type ProviderSubmissionResult,
  type ReviewRecord,
  type SubmissionIntentRecord,
  type TenantContext,
  type TenantId,
  type TenantState,
  type WorkerClaimRecord,
  type WorkerClaimState,
  type AssetOrigin,
  type JobState,
  type AttemptState,
  type SubmissionState,
  type DeliveryRecord,
  type DeliveryState,
  type CreateDeliveryInput,
  type ReleaseWorkerInput,
  type NativeProjectBinding,
  type NativeProjectProvisioner,
  type SourceIdentity,
  type StorageError,
  makeId,
  makeNativeSchemaVersion,
  makeNativeTimelineIdentity,
  makePositiveNumber,
  makeSha256,
  isIdentifierValue,
  isSha256Value,
  MAX_SOURCE_BYTES,
  MAX_TEXT_LENGTH,
  unconfiguredNativeProvisioner,
} from "./domain";
import { TenantStateSchema, type TenantStateWire } from "./schema";
import { isVerifiedNativeReceipt } from "./native-authority";

export interface ApplicationStore {
  readonly readState: (context: TenantContext) => Effect.Effect<TenantState, DomainError>;
  readonly createProject: (
    context: TenantContext,
    input: CreateProjectRequest,
  ) => Effect.Effect<ProjectRecord, DomainError>;
  readonly getProject: (
    context: TenantContext,
    projectId: ProjectId,
  ) => Effect.Effect<ProjectRecord, DomainError>;
  readonly createAsset: (
    context: TenantContext,
    input: CreateAssetInput,
  ) => Effect.Effect<AssetRecord, DomainError>;
  readonly createNativeAsset: (
    context: TenantContext,
    input: CreateAssetInput,
  ) => Effect.Effect<AssetRecord, DomainError>;
  readonly createJob: (
    context: TenantContext,
    input: CreateJobInput,
  ) => Effect.Effect<JobRecord, DomainError>;
  readonly getJob: (
    context: TenantContext,
    jobId: EntityId<"JobId">,
  ) => Effect.Effect<JobRecord, DomainError>;
  readonly createReview: (
    context: TenantContext,
    input: CreateReviewInput,
  ) => Effect.Effect<ReviewRecord, DomainError>;
  readonly reserveBudget: (
    context: TenantContext,
    input: {
      readonly budgetId: EntityId<"BudgetId">;
      readonly projectId: ProjectId;
      readonly limitUnits: number;
      readonly requestedUnits: number;
      readonly now: number;
    },
  ) => Effect.Effect<BudgetRecord, DomainError>;
  readonly claimWorker: (
    context: TenantContext,
    input: ClaimWorkerInput,
  ) => Effect.Effect<WorkerClaimRecord, DomainError>;
  readonly releaseWorker: (
    context: TenantContext,
    input: ReleaseWorkerInput,
  ) => Effect.Effect<WorkerClaimRecord, DomainError>;
  readonly createDelivery: (
    context: TenantContext,
    input: CreateDeliveryInput,
  ) => Effect.Effect<DeliveryRecord, DomainError>;
  readonly getDelivery: (
    context: TenantContext,
    deliveryId: EntityId<"DeliveryId">,
  ) => Effect.Effect<DeliveryRecord, DomainError>;
  readonly prepareSubmission: (
    context: TenantContext,
    input: PrepareSubmissionInput,
  ) => Effect.Effect<PrepareSubmissionResult, DomainError>;
  readonly recordSubmission: (
    context: TenantContext,
    intentId: IntentId,
    result: ProviderSubmissionResult | ProviderReconciliationResult,
  ) => Effect.Effect<SubmissionIntentRecord, DomainError>;
  readonly getSubmissionIntent: (
    context: TenantContext,
    intentId: IntentId,
  ) => Effect.Effect<SubmissionIntentRecord, DomainError>;
}

export class ApplicationStoreService extends Context.Service<
  ApplicationStoreService,
  ApplicationStore
>()("video-studio/ApplicationStore") {}

type StoreFailure = DomainError;

export const MAX_STATE_BYTES = 1_048_576;
export const MAX_RECORDS = 1024;
export const MAX_TENANT_ID_BYTES = 64;

const storageFailure = (operation: string, detail: string): StorageError => ({
  _tag: "StorageError",
  operation,
  detail,
});

const isNotFound = (error: unknown): boolean =>
  typeof error === "object" && error !== null && "code" in error && error.code === "ENOENT";

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

const decodeState = (text: string): Effect.Effect<TenantStateWire, StoreFailure> =>
  Effect.try({
    try: () => {
      const parsed: unknown = JSON.parse(text);
      return parsed;
    },
    catch: () => storageFailure("decode", "The tenant state is not valid JSON."),
  }).pipe(
    Effect.flatMap((parsed) =>
      Schema.decodeUnknownEffect(TenantStateSchema, {
        onExcessProperty: "error",
      })(parsed).pipe(
        Effect.mapError(() => storageFailure("decode", "The tenant state shape is invalid.")),
      ),
    ),
  );

const sourceFromWire = (value: { readonly sha256: string; readonly bytes: number }) =>
  Effect.gen(function* () {
    const sha256 = yield* makeSha256(value.sha256);
    const bytes = yield* makePositiveNumber("source.bytes", value.bytes);
    if (bytes > MAX_SOURCE_BYTES)
      return yield* Effect.fail(storageFailure("decode", "Source bytes exceed the bound."));
    return { sha256, bytes } satisfies SourceIdentity;
  });

const idFromWire = <K extends Parameters<typeof makeId>[0]>(kind: K, value: string) =>
  makeId(kind, value);

const nativeBindingFromWire = (value: {
  readonly nativeProjectId: string;
  readonly nativeSchemaVersion: string;
}) =>
  Effect.gen(function* () {
    const nativeProjectId = yield* idFromWire("NativeProjectId", value.nativeProjectId);
    const schemaVersion = yield* makeNativeSchemaVersion(value.nativeSchemaVersion);
    return { nativeProjectId, schemaVersion } satisfies NativeProjectBinding;
  });

const receiptFromWire = (value: {
  readonly receiptId: string;
  readonly schemaVersion: string;
  readonly nativeProjectId: string;
  readonly projectId: string;
  readonly revision: number;
  readonly source: { readonly sha256: string; readonly bytes: number };
  readonly timeline: string;
}) =>
  Effect.gen(function* () {
    const receiptId = yield* idFromWire("NativeReceiptId", value.receiptId);
    const schemaVersion = yield* makeNativeSchemaVersion(value.schemaVersion);
    const nativeProjectId = yield* idFromWire("NativeProjectId", value.nativeProjectId);
    const projectId = yield* idFromWire("ProjectId", value.projectId);
    const source = yield* sourceFromWire(value.source);
    const timeline = yield* makeNativeTimelineIdentity(value.timeline);
    return {
      receiptId,
      schemaVersion,
      nativeProjectId,
      projectId,
      revision: value.revision,
      source,
      timeline,
    } satisfies NativeReceipt;
  });

const assetOriginFromWire = (value: {
  readonly _tag: "ClientImport" | "NativeOutput";
  readonly declaredBy?: string;
  readonly receipt?: {
    readonly receiptId: string;
    readonly schemaVersion: string;
    readonly nativeProjectId: string;
    readonly projectId: string;
    readonly revision: number;
    readonly source: { readonly sha256: string; readonly bytes: number };
    readonly timeline: string;
  };
}) =>
  value._tag === "ClientImport"
    ? Effect.gen(function* () {
        const declaredBy = yield* idFromWire("ActorId", value.declaredBy ?? "");
        return { _tag: "ClientImport", declaredBy } satisfies AssetOrigin;
      })
    : Effect.gen(function* () {
        if (value.receipt === undefined)
          return yield* Effect.fail(storageFailure("decode", "A native asset lacks its receipt."));
        const receipt = yield* receiptFromWire(value.receipt);
        return { _tag: "NativeOutput", receipt } satisfies AssetOrigin;
      });

const projectFromWire = (value: TenantStateWire["projects"][number]) =>
  Effect.gen(function* () {
    const tenantId = yield* idFromWire("TenantId", value.tenantId);
    const projectId = yield* idFromWire("ProjectId", value.projectId);
    const native = yield* nativeBindingFromWire({
      nativeProjectId: value.nativeProjectId,
      nativeSchemaVersion: value.nativeSchemaVersion,
    });
    const source = yield* sourceFromWire(value.source);
    const createIntentId = yield* idFromWire("IntentId", value.createIntentId);
    return {
      tenantId,
      projectId,
      native,
      revision: value.revision,
      source,
      createIntentId,
      createdAt: value.createdAt,
    } satisfies ProjectRecord;
  });

const assetFromWire = (value: TenantStateWire["assets"][number]) =>
  Effect.gen(function* () {
    const tenantId = yield* idFromWire("TenantId", value.tenantId);
    const assetId = yield* idFromWire("AssetId", value.assetId);
    const projectId = yield* idFromWire("ProjectId", value.projectId);
    const origin = yield* assetOriginFromWire(value.origin);
    const source = yield* sourceFromWire(value.source);
    return {
      tenantId,
      assetId,
      projectId,
      revision: value.revision,
      origin,
      source,
      createdAt: value.createdAt,
    } satisfies AssetRecord;
  });

const jobStateFromWire = (value: TenantStateWire["jobs"][number]["state"]) =>
  value._tag === "Queued"
    ? Effect.succeed({ _tag: "Queued" } satisfies JobState)
    : value._tag === "Submitting"
      ? idFromWire("IntentId", value.submissionIntentId).pipe(
          Effect.map(
            (submissionIntentId) =>
              ({
                _tag: "Submitting",
                submissionIntentId,
              }) satisfies JobState,
          ),
        )
      : value._tag === "ReconciliationRequired"
        ? idFromWire("IntentId", value.submissionIntentId).pipe(
            Effect.map(
              (submissionIntentId) =>
                ({
                  _tag: "ReconciliationRequired",
                  submissionIntentId,
                  reason: value.reason,
                }) satisfies JobState,
            ),
          )
        : value._tag === "Running"
          ? Effect.succeed({ _tag: "Running" as const, providerReference: value.providerReference })
          : value._tag === "Completed"
            ? Effect.succeed({
                _tag: "Completed" as const,
                providerReference: value.providerReference,
              })
            : Effect.succeed({ _tag: "Failed" as const, reason: value.reason });

const jobFromWire = (value: TenantStateWire["jobs"][number]) =>
  Effect.gen(function* () {
    const tenantId = yield* idFromWire("TenantId", value.tenantId);
    const jobId = yield* idFromWire("JobId", value.jobId);
    const projectId = yield* idFromWire("ProjectId", value.projectId);
    const intentId = yield* idFromWire("IntentId", value.intentId);
    const requestFingerprint = yield* makeSha256(value.requestFingerprint);
    const state = yield* jobStateFromWire(value.state);
    return {
      tenantId,
      jobId,
      projectId,
      revision: value.revision,
      intentId,
      requestFingerprint,
      state,
      createdAt: value.createdAt,
    } satisfies JobRecord;
  });

const attemptStateFromWire = (value: TenantStateWire["attempts"][number]["state"]) =>
  value._tag === "Prepared"
    ? Effect.succeed({ _tag: "Prepared" } satisfies AttemptState)
    : value._tag === "Submitted"
      ? Effect.succeed({ _tag: "Submitted" as const, providerReference: value.providerReference })
      : value._tag === "Unknown"
        ? Effect.succeed({ _tag: "Unknown" as const, reason: value.reason })
        : Effect.succeed({ _tag: "Rejected" as const, reason: value.reason });

const attemptFromWire = (value: TenantStateWire["attempts"][number]) =>
  Effect.gen(function* () {
    const tenantId = yield* idFromWire("TenantId", value.tenantId);
    const attemptId = yield* idFromWire("AttemptId", value.attemptId);
    const jobId = yield* idFromWire("JobId", value.jobId);
    const submissionIntentId = yield* idFromWire("IntentId", value.submissionIntentId);
    const state = yield* attemptStateFromWire(value.state);
    return {
      tenantId,
      attemptId,
      jobId,
      submissionIntentId,
      state,
      createdAt: value.createdAt,
    } satisfies AttemptRecord;
  });

const reviewFromWire = (value: TenantStateWire["reviews"][number]) =>
  Effect.gen(function* () {
    const tenantId = yield* idFromWire("TenantId", value.tenantId);
    const reviewId = yield* idFromWire("ReviewId", value.reviewId);
    const projectId = yield* idFromWire("ProjectId", value.projectId);
    const plan = yield* makeSha256(value.plan);
    const output = yield* makeSha256(value.output);
    const renderer = yield* makeSha256(value.renderer);
    return {
      tenantId,
      reviewId,
      projectId,
      revision: value.revision,
      plan,
      output,
      renderer,
      disposition: value.disposition,
      createdAt: value.createdAt,
    } satisfies ReviewRecord;
  });

const budgetFromWire = (value: TenantStateWire["budgets"][number]) =>
  Effect.gen(function* () {
    const tenantId = yield* idFromWire("TenantId", value.tenantId);
    const budgetId = yield* idFromWire("BudgetId", value.budgetId);
    const projectId = yield* idFromWire("ProjectId", value.projectId);
    return {
      tenantId,
      budgetId,
      projectId,
      limitUnits: value.limitUnits,
      reservedUnits: value.reservedUnits,
      spentUnits: value.spentUnits,
      updatedAt: value.updatedAt,
    } satisfies BudgetRecord;
  });

const workerClaimFromWire = (value: TenantStateWire["workerClaims"][number]) =>
  Effect.gen(function* () {
    const tenantId = yield* idFromWire("TenantId", value.tenantId);
    const claimId = yield* idFromWire("WorkerClaimId", value.claimId);
    const jobId = yield* idFromWire("JobId", value.jobId);
    const state: Effect.Effect<WorkerClaimState, DomainError> =
      value.state._tag === "Active"
        ? Effect.succeed({
            _tag: "Active",
            workerId: value.state.workerId,
            fence: value.state.fence,
            leaseExpiresAt: value.state.leaseExpiresAt,
            claimedAt: value.state.claimedAt,
          })
        : Effect.succeed({
            _tag: "Released",
            workerId: value.state.workerId,
            fence: value.state.fence,
            releasedAt: value.state.releasedAt,
          });
    return { tenantId, claimId, jobId, state: yield* state } satisfies WorkerClaimRecord;
  });

const submissionStateFromWire = (value: TenantStateWire["submissionIntents"][number]["state"]) =>
  value._tag === "Prepared"
    ? Effect.succeed({ _tag: "Prepared" } satisfies SubmissionState)
    : value._tag === "Unknown"
      ? Effect.succeed({ _tag: "Unknown" as const, reason: value.reason })
      : value._tag === "Confirmed"
        ? Effect.succeed({ _tag: "Confirmed" as const, providerReference: value.providerReference })
        : Effect.succeed({ _tag: "Rejected" as const, reason: value.reason });

const submissionFromWire = (value: TenantStateWire["submissionIntents"][number]) =>
  Effect.gen(function* () {
    const tenantId = yield* idFromWire("TenantId", value.tenantId);
    const submissionIntentId = yield* idFromWire("IntentId", value.submissionIntentId);
    const jobId = yield* idFromWire("JobId", value.jobId);
    const attemptId = yield* idFromWire("AttemptId", value.attemptId);
    const requestFingerprint = yield* makeSha256(value.requestFingerprint);
    const state = yield* submissionStateFromWire(value.state);
    return {
      tenantId,
      submissionIntentId,
      jobId,
      attemptId,
      provider: value.provider,
      requestFingerprint,
      state,
      createdAt: value.createdAt,
      updatedAt: value.updatedAt,
    } satisfies SubmissionIntentRecord;
  });

const deliveryStateFromWire = (value: TenantStateWire["deliveries"][number]["state"]) =>
  value._tag === "Prepared"
    ? Effect.succeed({ _tag: "Prepared" } satisfies DeliveryState)
    : value._tag === "Published"
      ? Effect.succeed({ _tag: "Published" as const, providerReference: value.providerReference })
      : value._tag === "Unknown"
        ? Effect.succeed({ _tag: "Unknown" as const, reason: value.reason })
        : Effect.succeed({ _tag: "Failed" as const, reason: value.reason });

const deliveryFromWire = (value: TenantStateWire["deliveries"][number]) =>
  Effect.gen(function* () {
    const tenantId = yield* idFromWire("TenantId", value.tenantId);
    const deliveryId = yield* idFromWire("DeliveryId", value.deliveryId);
    const projectId = yield* idFromWire("ProjectId", value.projectId);
    const assetId = yield* idFromWire("AssetId", value.assetId);
    const state = yield* deliveryStateFromWire(value.state);
    return {
      tenantId,
      deliveryId,
      projectId,
      revision: value.revision,
      assetId,
      state,
      createdAt: value.createdAt,
      updatedAt: value.updatedAt,
    } satisfies DeliveryRecord;
  });

const stateFromWire = (value: TenantStateWire): Effect.Effect<TenantState, DomainError> =>
  Effect.gen(function* () {
    const collections = [
      value.projects,
      value.assets,
      value.jobs,
      value.attempts,
      value.reviews,
      value.budgets,
      value.workerClaims,
      value.submissionIntents,
      value.deliveries,
    ];
    if (collections.some((collection) => collection.length > MAX_RECORDS))
      return yield* Effect.fail(
        storageFailure("decode", "A tenant collection exceeds its record limit."),
      );
    const tenantId = yield* idFromWire("TenantId", value.tenantId);
    const projects = yield* Effect.forEach(value.projects, projectFromWire);
    const assets = yield* Effect.forEach(value.assets, assetFromWire);
    const jobs = yield* Effect.forEach(value.jobs, jobFromWire);
    const attempts = yield* Effect.forEach(value.attempts, attemptFromWire);
    const reviews = yield* Effect.forEach(value.reviews, reviewFromWire);
    const budgets = yield* Effect.forEach(value.budgets, budgetFromWire);
    const workerClaims = yield* Effect.forEach(value.workerClaims, workerClaimFromWire);
    const submissionIntents = yield* Effect.forEach(value.submissionIntents, submissionFromWire);
    const deliveries = yield* Effect.forEach(value.deliveries, deliveryFromWire);
    const state = {
      tenantId,
      projects,
      assets,
      jobs,
      attempts,
      reviews,
      budgets,
      workerClaims,
      submissionIntents,
      deliveries,
    } satisfies TenantState;
    return yield* validateStateRelations(state);
  });

const validateStateRelations = (state: TenantState): Effect.Effect<TenantState, StorageError> => {
  const fail = (detail: string): Effect.Effect<TenantState, StorageError> =>
    Effect.fail(storageFailure("decode", detail));
  const tenant = state.tenantId.value;
  const collections: ReadonlyArray<readonly [string, ReadonlyArray<unknown>, string]> = [
    ["projects", state.projects, "projectId"],
    ["assets", state.assets, "assetId"],
    ["jobs", state.jobs, "jobId"],
    ["attempts", state.attempts, "attemptId"],
    ["reviews", state.reviews, "reviewId"],
    ["budgets", state.budgets, "budgetId"],
    ["workerClaims", state.workerClaims, "claimId"],
    ["submissionIntents", state.submissionIntents, "submissionIntentId"],
    ["deliveries", state.deliveries, "deliveryId"],
  ];
  for (const [name, records, key] of collections) {
    if (records.length > MAX_RECORDS) return fail(`${name} exceeds the record limit.`);
    const seen = new Set<string>();
    for (const record of records) {
      const candidate = record as {
        readonly tenantId?: { readonly value?: unknown };
        readonly [key: string]: unknown;
      };
      const recordTenant = candidate.tenantId?.value;
      const identifier = (candidate[key] as { readonly value?: unknown } | undefined)?.value;
      if (recordTenant !== tenant) return fail(`${name} contains a foreign tenant record.`);
      if (typeof identifier !== "string" || seen.has(identifier))
        return fail(`${name} contains a duplicate or invalid identifier.`);
      seen.add(identifier);
    }
  }
  const projectById = new Map(state.projects.map((project) => [project.projectId.value, project]));
  const jobById = new Map(state.jobs.map((job) => [job.jobId.value, job]));
  const intentById = new Map(
    state.submissionIntents.map((intent) => [intent.submissionIntentId.value, intent]),
  );
  const attemptById = new Map(state.attempts.map((attempt) => [attempt.attemptId.value, attempt]));
  const nativeProjectIds = new Set<string>();
  const createIntentIds = new Set<string>();
  for (const project of state.projects) {
    if (nativeProjectIds.has(project.native.nativeProjectId.value))
      return fail("projects contain a duplicate native project identifier.");
    if (createIntentIds.has(project.createIntentId.value))
      return fail("projects contain a duplicate creation intent.");
    nativeProjectIds.add(project.native.nativeProjectId.value);
    createIntentIds.add(project.createIntentId.value);
  }
  const assertProject = (projectId: string, revision: number, record: string): boolean => {
    const project = projectById.get(projectId);
    return project !== undefined && project.revision === revision && record === "Project";
  };
  for (const asset of state.assets) {
    const project = projectById.get(asset.projectId.value);
    if (project === undefined || project.revision !== asset.revision)
      return fail("asset project/revision relation is invalid.");
    if (asset.origin._tag === "NativeOutput") {
      const receipt = asset.origin.receipt;
      if (
        receipt.projectId.value !== asset.projectId.value ||
        receipt.nativeProjectId.value !== project.native.nativeProjectId.value ||
        receipt.schemaVersion.value !== project.native.schemaVersion.value ||
        receipt.revision !== asset.revision ||
        !sameSource(receipt.source, project.source) ||
        !sameSource(receipt.source, asset.source)
      )
        return fail("native receipt is not joined to its project, revision, or source.");
    }
  }
  for (const job of state.jobs) {
    if (!assertProject(job.projectId.value, job.revision, "Project"))
      return fail("job project/revision relation is invalid.");
    if (state.jobs.some((other) => other !== job && other.intentId.value === job.intentId.value))
      return fail("job intent identifiers must be unique.");
    if (job.state._tag === "Submitting" || job.state._tag === "ReconciliationRequired") {
      const intent = intentById.get(job.state.submissionIntentId.value);
      if (intent === undefined || intent.jobId.value !== job.jobId.value)
        return fail("job submission state is not joined to its intent.");
      if (
        (job.state._tag === "Submitting" && intent.state._tag !== "Prepared") ||
        (job.state._tag === "ReconciliationRequired" && intent.state._tag !== "Unknown")
      )
        return fail("job and submission intent states are not coherent.");
    }
    if (job.state._tag === "Running" || job.state._tag === "Completed") {
      const intent = [...intentById.values()].find(
        (candidate) =>
          candidate.jobId.value === job.jobId.value && candidate.state._tag === "Confirmed",
      );
      if (intent === undefined) return fail("running job lacks a confirmed submission intent.");
    }
    if (job.state._tag === "Failed") {
      const intent = [...intentById.values()].find(
        (candidate) =>
          candidate.jobId.value === job.jobId.value && candidate.state._tag === "Rejected",
      );
      if (intent === undefined) return fail("failed job lacks a rejected submission intent.");
    }
  }
  const attemptJobs = new Set<string>();
  for (const attempt of state.attempts) {
    if (attemptJobs.has(attempt.jobId.value))
      return fail("a job cannot have multiple submission attempts.");
    attemptJobs.add(attempt.jobId.value);
    const job = jobById.get(attempt.jobId.value);
    const intent = intentById.get(attempt.submissionIntentId.value);
    if (job === undefined || intent === undefined || intent.jobId.value !== job.jobId.value)
      return fail("attempt is not joined to its job and intent.");
    if (intent.attemptId.value !== attempt.attemptId.value)
      return fail("attempt and intent identifiers do not match.");
    if (
      (attempt.state._tag === "Prepared" && intent.state._tag !== "Prepared") ||
      (attempt.state._tag === "Unknown" && intent.state._tag !== "Unknown") ||
      (attempt.state._tag === "Submitted" && intent.state._tag !== "Confirmed") ||
      (attempt.state._tag === "Rejected" && intent.state._tag !== "Rejected")
    )
      return fail("attempt and submission intent states are not coherent.");
  }
  const submissionJobs = new Set<string>();
  for (const intent of state.submissionIntents) {
    if (submissionJobs.has(intent.jobId.value))
      return fail("a job cannot have multiple submission intents.");
    submissionJobs.add(intent.jobId.value);
    const job = jobById.get(intent.jobId.value);
    const attempt = attemptById.get(intent.attemptId.value);
    if (
      job === undefined ||
      attempt === undefined ||
      job.requestFingerprint.value !== intent.requestFingerprint.value
    )
      return fail("submission intent is not joined to its job and attempt.");
    if (
      attempt.jobId.value !== job.jobId.value ||
      attempt.submissionIntentId.value !== intent.submissionIntentId.value
    )
      return fail("submission intent attempt points to another job.");
    if (
      (intent.state._tag === "Prepared" && job.state._tag !== "Submitting") ||
      (intent.state._tag === "Unknown" && job.state._tag !== "ReconciliationRequired") ||
      (intent.state._tag === "Confirmed" &&
        job.state._tag !== "Running" &&
        job.state._tag !== "Completed") ||
      (intent.state._tag === "Rejected" && job.state._tag !== "Failed")
    )
      return fail("submission intent and job states are not coherent.");
  }
  for (const review of state.reviews) {
    if (!assertProject(review.projectId.value, review.revision, "Project"))
      return fail("review project/revision relation is invalid.");
  }
  for (const budget of state.budgets) {
    if (!projectById.has(budget.projectId.value))
      return fail("budget project relation is invalid.");
    if (budget.reservedUnits + budget.spentUnits > budget.limitUnits)
      return fail("budget totals exceed the limit.");
  }
  const fencesByJob = new Map<string, number>();
  const activeByJob = new Set<string>();
  for (const claim of state.workerClaims) {
    if (!jobById.has(claim.jobId.value)) return fail("worker claim points to a missing job.");
    if (!isIdentifierValue(claim.state.workerId)) return fail("worker claim owner is invalid.");
    const previousFence = fencesByJob.get(claim.jobId.value);
    if (previousFence !== undefined && claim.state.fence <= previousFence)
      return fail("worker claim fences must increase for each job.");
    fencesByJob.set(claim.jobId.value, claim.state.fence);
    if (claim.state._tag === "Active") {
      if (claim.state.leaseExpiresAt <= claim.state.claimedAt)
        return fail("active worker claims must have a forward lease.");
      if (activeByJob.has(claim.jobId.value))
        return fail("a job cannot have multiple active worker claims.");
      activeByJob.add(claim.jobId.value);
    } else if (claim.state.releasedAt < 0) {
      return fail("released worker claims must have a non-negative release time.");
    }
  }
  for (const delivery of state.deliveries) {
    const project = projectById.get(delivery.projectId.value);
    const asset = state.assets.find((item) => item.assetId.value === delivery.assetId.value);
    if (
      project === undefined ||
      asset === undefined ||
      project.revision !== delivery.revision ||
      asset.projectId.value !== project.projectId.value ||
      asset.revision !== delivery.revision
    )
      return fail("delivery is not joined to its project, revision, and asset.");
  }
  return Effect.succeed(state);
};

const sourceToWire = (source: SourceIdentity) => ({
  sha256: source.sha256.value,
  bytes: source.bytes,
});
const jobStateToWire = (state: JobState) =>
  state._tag === "Queued"
    ? { _tag: "Queued" as const }
    : state._tag === "Submitting"
      ? { _tag: "Submitting" as const, submissionIntentId: state.submissionIntentId.value }
      : state._tag === "ReconciliationRequired"
        ? {
            _tag: "ReconciliationRequired" as const,
            submissionIntentId: state.submissionIntentId.value,
            reason: state.reason,
          }
        : state._tag === "Running"
          ? { _tag: "Running" as const, providerReference: state.providerReference }
          : state._tag === "Completed"
            ? { _tag: "Completed" as const, providerReference: state.providerReference }
            : { _tag: "Failed" as const, reason: state.reason };
const attemptStateToWire = (state: AttemptState) =>
  state._tag === "Prepared"
    ? { _tag: "Prepared" as const }
    : state._tag === "Submitted"
      ? { _tag: "Submitted" as const, providerReference: state.providerReference }
      : state._tag === "Unknown"
        ? { _tag: "Unknown" as const, reason: state.reason }
        : { _tag: "Rejected" as const, reason: state.reason };
const submissionStateToWire = (state: SubmissionState) =>
  state._tag === "Prepared"
    ? { _tag: "Prepared" as const }
    : state._tag === "Unknown"
      ? { _tag: "Unknown" as const, reason: state.reason }
      : state._tag === "Confirmed"
        ? { _tag: "Confirmed" as const, providerReference: state.providerReference }
        : { _tag: "Rejected" as const, reason: state.reason };
const deliveryStateToWire = (state: DeliveryState) =>
  state._tag === "Prepared"
    ? { _tag: "Prepared" as const }
    : state._tag === "Published"
      ? { _tag: "Published" as const, providerReference: state.providerReference }
      : state._tag === "Unknown"
        ? { _tag: "Unknown" as const, reason: state.reason }
        : { _tag: "Failed" as const, reason: state.reason };
const workerClaimStateToWire = (state: WorkerClaimState) =>
  state._tag === "Active"
    ? {
        _tag: "Active" as const,
        workerId: state.workerId,
        fence: state.fence,
        leaseExpiresAt: state.leaseExpiresAt,
        claimedAt: state.claimedAt,
      }
    : {
        _tag: "Released" as const,
        workerId: state.workerId,
        fence: state.fence,
        releasedAt: state.releasedAt,
      };
const receiptToWire = (receipt: NativeReceipt) => ({
  receiptId: receipt.receiptId.value,
  schemaVersion: receipt.schemaVersion.value,
  nativeProjectId: receipt.nativeProjectId.value,
  projectId: receipt.projectId.value,
  revision: receipt.revision,
  source: sourceToWire(receipt.source),
  timeline: receipt.timeline.value,
});
const originToWire = (origin: AssetOrigin) =>
  origin._tag === "ClientImport"
    ? { _tag: "ClientImport" as const, declaredBy: origin.declaredBy.value }
    : { _tag: "NativeOutput" as const, receipt: receiptToWire(origin.receipt) };
const stateToWire = (value: TenantState): TenantStateWire => ({
  schema: 1,
  tenantId: value.tenantId.value,
  projects: value.projects.map((project) => ({
    tenantId: project.tenantId.value,
    projectId: project.projectId.value,
    nativeProjectId: project.native.nativeProjectId.value,
    nativeSchemaVersion: project.native.schemaVersion.value,
    revision: project.revision,
    source: sourceToWire(project.source),
    createIntentId: project.createIntentId.value,
    createdAt: project.createdAt,
  })),
  assets: value.assets.map((asset) => ({
    tenantId: asset.tenantId.value,
    assetId: asset.assetId.value,
    projectId: asset.projectId.value,
    revision: asset.revision,
    origin: originToWire(asset.origin),
    source: sourceToWire(asset.source),
    createdAt: asset.createdAt,
  })),
  jobs: value.jobs.map((job) => ({
    tenantId: job.tenantId.value,
    jobId: job.jobId.value,
    projectId: job.projectId.value,
    revision: job.revision,
    intentId: job.intentId.value,
    requestFingerprint: job.requestFingerprint.value,
    state: jobStateToWire(job.state),
    createdAt: job.createdAt,
  })),
  attempts: value.attempts.map((attempt) => ({
    tenantId: attempt.tenantId.value,
    attemptId: attempt.attemptId.value,
    jobId: attempt.jobId.value,
    submissionIntentId: attempt.submissionIntentId.value,
    state: attemptStateToWire(attempt.state),
    createdAt: attempt.createdAt,
  })),
  reviews: value.reviews.map((review) => ({
    tenantId: review.tenantId.value,
    reviewId: review.reviewId.value,
    projectId: review.projectId.value,
    revision: review.revision,
    plan: review.plan.value,
    output: review.output.value,
    renderer: review.renderer.value,
    disposition: review.disposition,
    createdAt: review.createdAt,
  })),
  budgets: value.budgets.map((budget) => ({
    tenantId: budget.tenantId.value,
    budgetId: budget.budgetId.value,
    projectId: budget.projectId.value,
    limitUnits: budget.limitUnits,
    reservedUnits: budget.reservedUnits,
    spentUnits: budget.spentUnits,
    updatedAt: budget.updatedAt,
  })),
  workerClaims: value.workerClaims.map((claim) => ({
    tenantId: claim.tenantId.value,
    claimId: claim.claimId.value,
    jobId: claim.jobId.value,
    state: workerClaimStateToWire(claim.state),
  })),
  submissionIntents: value.submissionIntents.map((intent) => ({
    tenantId: intent.tenantId.value,
    submissionIntentId: intent.submissionIntentId.value,
    jobId: intent.jobId.value,
    attemptId: intent.attemptId.value,
    provider: intent.provider,
    requestFingerprint: intent.requestFingerprint.value,
    state: submissionStateToWire(intent.state),
    createdAt: intent.createdAt,
    updatedAt: intent.updatedAt,
  })),
  deliveries: value.deliveries.map((delivery) => ({
    tenantId: delivery.tenantId.value,
    deliveryId: delivery.deliveryId.value,
    projectId: delivery.projectId.value,
    revision: delivery.revision,
    assetId: delivery.assetId.value,
    state: deliveryStateToWire(delivery.state),
    createdAt: delivery.createdAt,
    updatedAt: delivery.updatedAt,
  })),
});

const emptyState = (tenantId: TenantId): TenantState => ({
  tenantId,
  projects: [],
  assets: [],
  jobs: [],
  attempts: [],
  reviews: [],
  budgets: [],
  workerClaims: [],
  submissionIntents: [],
  deliveries: [],
});

const sameSource = (left: SourceIdentity, right: SourceIdentity): boolean =>
  left.bytes === right.bytes && left.sha256.value === right.sha256.value;

const sameReceipt = (left: NativeReceipt, right: NativeReceipt): boolean =>
  left.receiptId.value === right.receiptId.value &&
  left.schemaVersion.value === right.schemaVersion.value &&
  left.nativeProjectId.value === right.nativeProjectId.value &&
  left.projectId.value === right.projectId.value &&
  left.revision === right.revision &&
  sameSource(left.source, right.source) &&
  left.timeline.value === right.timeline.value;

const sameOrigin = (left: AssetOrigin, right: AssetOrigin): boolean =>
  left._tag === "ClientImport" && right._tag === "ClientImport"
    ? left.declaredBy.value === right.declaredBy.value
    : left._tag === "NativeOutput" && right._tag === "NativeOutput"
      ? sameReceipt(left.receipt, right.receipt)
      : false;

const recordNotFound = (record: string, id: string): StoreFailure => ({
  _tag: "RecordNotFound",
  record,
  id,
});

const requireRecord = <A>(
  record: string,
  id: string,
  value: A | undefined,
): Effect.Effect<A, StoreFailure> =>
  value === undefined ? Effect.fail(recordNotFound(record, id)) : Effect.succeed(value);

const stateForContext = (
  state: TenantState,
  context: TenantContext,
): Effect.Effect<TenantState, StoreFailure> =>
  state.tenantId.value === context.tenantId.value
    ? Effect.succeed(state)
    : Effect.fail({ _tag: "TenantAccessDenied", projectId: context.tenantId.value });

const validateContext = (context: TenantContext): Effect.Effect<TenantContext, StoreFailure> => {
  const raw = context as unknown as {
    readonly tenantId?: { readonly kind?: unknown; readonly value?: unknown };
    readonly actorId?: { readonly kind?: unknown; readonly value?: unknown };
  };
  if (
    raw === null ||
    typeof raw !== "object" ||
    raw.tenantId?.kind !== "TenantId" ||
    raw.actorId?.kind !== "ActorId" ||
    !isIdentifierValue(raw.tenantId.value) ||
    !isIdentifierValue(raw.actorId.value)
  )
    return Effect.fail(
      storageFailure("context", "The tenant context is not a validated identifier pair."),
    );
  return Effect.succeed(context);
};

const validateEntity = (id: unknown, expectedKind: string): Effect.Effect<void, StoreFailure> =>
  isRecord(id) && id.kind === expectedKind && isIdentifierValue(id.value)
    ? Effect.succeed(undefined)
    : Effect.fail(storageFailure("input", `The ${expectedKind} identifier is invalid.`));

const validateText = (field: string, value: string): Effect.Effect<void, StoreFailure> =>
  typeof value === "string" && value.length <= MAX_TEXT_LENGTH
    ? Effect.succeed(undefined)
    : Effect.fail(storageFailure("input", `${field} exceeds the text limit.`));

const validateNumber = (
  field: string,
  value: number,
  positive = false,
): Effect.Effect<void, StoreFailure> =>
  Number.isSafeInteger(value) && value >= (positive ? 1 : 0)
    ? Effect.succeed(undefined)
    : Effect.fail({ _tag: "InvalidNumber", field, value });

const validateSource = (
  source: SourceIdentity,
  field: string,
): Effect.Effect<void, StoreFailure> =>
  !isRecord(source) || !isRecord(source.sha256)
    ? Effect.fail(storageFailure("input", `${field} is not a source identity.`))
    : source.sha256.kind !== "Sha256"
      ? Effect.fail(storageFailure("input", `${field}.sha256 has the wrong runtime kind.`))
      : validateNumber(`${field}.bytes`, source.bytes, true).pipe(
          Effect.flatMap(() =>
            source.bytes <= MAX_SOURCE_BYTES && isSha256Value(source.sha256.value)
              ? Effect.succeed(undefined)
              : Effect.fail(
                  storageFailure("input", `${field} is outside its bounded source shape.`),
                ),
          ),
        );

const validateNativeReceipt = (
  receipt: unknown,
  field: string,
): Effect.Effect<void, StoreFailure> => {
  if (!isRecord(receipt))
    return Effect.fail(storageFailure("input", `${field} is not a native receipt.`));
  return Effect.all([
    validateEntity(receipt.receiptId, "NativeReceiptId"),
    validateEntity(receipt.schemaVersion, "NativeSchemaVersion"),
    validateEntity(receipt.nativeProjectId, "NativeProjectId"),
    validateEntity(receipt.projectId, "ProjectId"),
    validateNumber(`${field}.revision`, receipt.revision as number),
    validateSource(receipt.source as SourceIdentity, `${field}.source`),
    validateEntity(receipt.timeline, "NativeTimelineIdentity"),
  ]).pipe(Effect.asVoid);
};

const validateAssetOrigin = (origin: unknown, field: string): Effect.Effect<void, StoreFailure> => {
  if (!isRecord(origin) || typeof origin._tag !== "string")
    return Effect.fail(storageFailure("input", `${field} is not an asset origin.`));
  return origin._tag === "ClientImport"
    ? validateEntity(origin.declaredBy, "ActorId")
    : origin._tag === "NativeOutput"
      ? validateNativeReceipt(origin.receipt, `${field}.receipt`)
      : Effect.fail(storageFailure("input", `${field} has an unknown origin tag.`));
};

const validateSubmissionResult = (result: unknown): Effect.Effect<void, StoreFailure> => {
  if (!isRecord(result) || typeof result._tag !== "string")
    return Effect.fail(storageFailure("submission", "The provider result is invalid."));
  if (result._tag === "Confirmed")
    return typeof result.providerReference === "string"
      ? validateText("submission.providerReference", result.providerReference)
      : Effect.fail(storageFailure("submission", "The confirmed provider result is invalid."));
  if (result._tag === "Rejected" || result._tag === "Unknown" || result._tag === "StillUnknown")
    return typeof result.reason === "string"
      ? validateText("submission.reason", result.reason)
      : Effect.fail(storageFailure("submission", "The unresolved provider result is invalid."));
  return Effect.fail(storageFailure("submission", "The provider result tag is invalid."));
};

const isStoreFailure = (value: unknown): value is StoreFailure => {
  if (!isRecord(value) || typeof value._tag !== "string") return false;
  switch (value._tag) {
    case "StorageError":
    case "TenantAccessDenied":
    case "RecordNotFound":
    case "IdempotencyConflict":
    case "StateConflict":
    case "WorkerLeaseConflict":
    case "BudgetExceeded":
    case "ReconciliationRequired":
    case "InvalidIdentifier":
    case "InvalidHash":
    case "InvalidNumber":
    case "NativeProvisioningUnavailable":
    case "NativeUnconfigured":
    case "NativeReceiptInvalid":
      return true;
    default:
      return false;
  }
};

export interface FileStore {
  readonly service: ApplicationStore;
  readonly root: string;
  readonly close: () => Effect.Effect<void, StorageError>;
}

export const openFileStore = (
  root: string,
  provisioner: NativeProjectProvisioner = unconfiguredNativeProvisioner,
): Effect.Effect<FileStore, StorageError> => {
  if (!isAbsolute(root) || root.includes("\0") || resolve(root) !== root)
    return Effect.fail(storageFailure("open", "The local store root must be absolute."));

  const lockPath = join(root, ".application-store.lock");
  const ownershipPath = join(root, "native-project-ownership.json");
  const runStore = (lockHandle: import("node:fs/promises").FileHandle): FileStore => {
    let closed = false;
    let closing = false;
    let closePromise: Promise<void> | undefined;
    let tail: Promise<void> = Promise.resolve();

    const serial = <A>(operation: () => Promise<A>): Promise<A> => {
      if (closed || closing) return Promise.reject(new Error("The application store is closed."));
      const previous = tail;
      let release: (() => void) | undefined;
      tail = new Promise<void>((resolve) => {
        release = resolve;
      });
      return previous.then(operation).finally(() => release?.());
    };

    const tenantDirectory = (tenantId: TenantId): string => join(root, "tenants", tenantId.value);
    const statePath = (tenantId: TenantId): string => join(tenantDirectory(tenantId), "state.json");

    const readBoundedText = async (path: string): Promise<string> => {
      const flags = constants.O_RDONLY | constants.O_NONBLOCK | constants.O_NOFOLLOW;
      const handle = await open(path, flags);
      try {
        const before = await handle.stat();
        if (!before.isFile() || before.size > MAX_STATE_BYTES)
          throw new Error("The bounded state file is not a regular file or is too large.");
        const bytes = Buffer.allocUnsafe(before.size);
        let offset = 0;
        while (offset < bytes.byteLength) {
          const result = await handle.read(bytes, offset, bytes.byteLength - offset, offset);
          if (result.bytesRead === 0) throw new Error("The bounded state file ended early.");
          offset += result.bytesRead;
        }
        const after = await handle.stat();
        if (
          !after.isFile() ||
          after.size !== before.size ||
          after.dev !== before.dev ||
          after.ino !== before.ino
        )
          throw new Error("The bounded state file changed while it was being read.");
        return bytes.toString("utf8");
      } finally {
        await handle.close().catch(() => undefined);
      }
    };

    const readOwnership = async (): Promise<Record<string, string>> => {
      try {
        const text = await readBoundedText(ownershipPath);
        const parsed: unknown = JSON.parse(text);
        if (!isRecord(parsed) || parsed.schema !== 1 || !isRecord(parsed.owners))
          throw new Error("The native ownership registry shape is invalid.");
        const owners: Record<string, string> = {};
        for (const [nativeProjectId, tenantId] of Object.entries(parsed.owners)) {
          if (!isIdentifierValue(nativeProjectId) || !isIdentifierValue(tenantId))
            throw new Error("The native ownership registry contains invalid identifiers.");
          owners[nativeProjectId] = tenantId;
        }
        return owners;
      } catch (error) {
        if (isNotFound(error)) return {};
        throw error;
      }
    };

    const writeOwnership = async (owners: Record<string, string>): Promise<void> => {
      const temporary = `${ownershipPath}.${randomUUID()}.tmp`;
      try {
        const text = JSON.stringify({ schema: 1, owners });
        if (Buffer.byteLength(text, "utf8") > MAX_STATE_BYTES)
          throw new Error("The native ownership registry exceeds its bound.");
        await writeFile(temporary, text, { encoding: "utf8", flag: "wx" });
        await rename(temporary, ownershipPath);
      } finally {
        await unlink(temporary).catch(() => undefined);
      }
    };

    const validateProjectInput = (context: TenantContext, input: CreateProjectRequest) =>
      Effect.all([
        validateContext(context),
        validateEntity(input.projectId, "ProjectId"),
        validateEntity(input.createIntentId, "IntentId"),
        validateSource(input.source, "project.source"),
        validateNumber("project.now", input.now),
      ]).pipe(Effect.asVoid);

    const validateAssetInput = (context: TenantContext, input: CreateAssetInput) =>
      Effect.all([
        validateContext(context),
        validateEntity(input.assetId, "AssetId"),
        validateEntity(input.projectId, "ProjectId"),
        validateNumber("asset.revision", input.revision),
        validateNumber("asset.now", input.now),
        validateSource(input.source, "asset.source"),
        validateAssetOrigin(input.origin, "asset.origin"),
      ]).pipe(Effect.asVoid);

    const validateJobInput = (context: TenantContext, input: CreateJobInput) =>
      Effect.all([
        validateContext(context),
        validateEntity(input.jobId, "JobId"),
        validateEntity(input.projectId, "ProjectId"),
        validateEntity(input.intentId, "IntentId"),
        validateNumber("job.revision", input.revision),
        validateNumber("job.now", input.now),
        validateSource({ sha256: input.requestFingerprint, bytes: 1 }, "job.fingerprint"),
      ]).pipe(Effect.asVoid);

    const validateReviewInput = (context: TenantContext, input: CreateReviewInput) =>
      Effect.all([
        validateContext(context),
        validateEntity(input.reviewId, "ReviewId"),
        validateEntity(input.projectId, "ProjectId"),
        validateNumber("review.revision", input.revision),
        validateNumber("review.now", input.now),
        validateSource({ sha256: input.plan, bytes: 1 }, "review.plan"),
        validateSource({ sha256: input.output, bytes: 1 }, "review.output"),
        validateSource({ sha256: input.renderer, bytes: 1 }, "review.renderer"),
        input.disposition === "Pending" ||
        input.disposition === "Accepted" ||
        input.disposition === "Rejected"
          ? Effect.succeed(undefined)
          : Effect.fail(storageFailure("input", "The review disposition is invalid.")),
      ]).pipe(Effect.asVoid);

    const validateSubmissionInput = (context: TenantContext, input: PrepareSubmissionInput) =>
      Effect.all([
        validateContext(context),
        validateEntity(input.submissionIntentId, "IntentId"),
        validateEntity(input.attemptId, "AttemptId"),
        validateEntity(input.jobId, "JobId"),
        validateText("submission.provider", input.provider),
        validateNumber("submission.now", input.now),
        validateSource({ sha256: input.requestFingerprint, bytes: 1 }, "submission.fingerprint"),
      ]).pipe(
        Effect.flatMap(() =>
          isIdentifierValue(input.provider)
            ? Effect.succeed(undefined)
            : Effect.fail(storageFailure("input", "The provider identifier is invalid.")),
        ),
        Effect.asVoid,
      );

    const persistState = async (tenantId: TenantId, next: TenantState): Promise<void> => {
      const checked = await Effect.runPromise(validateStateRelations(next));
      const encoded = JSON.stringify(stateToWire(checked));
      if (Buffer.byteLength(encoded, "utf8") > MAX_STATE_BYTES)
        throw storageFailure("update", "The tenant state exceeds its byte bound.");
      const path = statePath(tenantId);
      const temporary = `${path}.${randomUUID()}.tmp`;
      try {
        await writeFile(temporary, encoded, { encoding: "utf8", flag: "wx" });
        await rename(temporary, path);
      } finally {
        await unlink(temporary).catch(() => undefined);
      }
    };

    const loadTenant = async (context: TenantContext): Promise<TenantState> => {
      await mkdir(tenantDirectory(context.tenantId), { recursive: true });
      try {
        const text = await readBoundedText(statePath(context.tenantId));
        const wire = await Effect.runPromise(decodeState(text));
        const state = await Effect.runPromise(stateFromWire(wire));
        const owners = await readOwnership();
        for (const project of state.projects) {
          if (owners[project.native.nativeProjectId.value] !== context.tenantId.value)
            throw new Error(
              "The native project ownership registry does not match the tenant state.",
            );
        }
        return await Effect.runPromise(stateForContext(state, context));
      } catch (error) {
        if (isNotFound(error)) return emptyState(context.tenantId);
        throw error;
      }
    };

    const validateTenantOwnership = async (state: TenantState): Promise<void> => {
      const owners = await readOwnership();
      for (const project of state.projects) {
        if (owners[project.native.nativeProjectId.value] !== state.tenantId.value)
          throw new Error("The native project ownership registry does not match the tenant state.");
      }
    };

    const createProject = (context: TenantContext, input: CreateProjectRequest) =>
      validateProjectInput(context, input).pipe(
        Effect.flatMap(() =>
          Effect.tryPromise({
            try: () =>
              serial(async () => {
                const state = await loadTenant(context);
                const owners = await readOwnership();
                const existingByIntent = state.projects.find(
                  (project) => project.createIntentId.value === input.createIntentId.value,
                );
                if (
                  existingByIntent !== undefined &&
                  existingByIntent.projectId.value !== input.projectId.value
                )
                  throw {
                    _tag: "IdempotencyConflict",
                    intentId: input.createIntentId.value,
                  } satisfies DomainError;
                const existing = state.projects.find(
                  (project) => project.projectId.value === input.projectId.value,
                );
                if (existing !== undefined) {
                  if (
                    existing.createIntentId.value !== input.createIntentId.value ||
                    !sameSource(existing.source, input.source)
                  )
                    throw {
                      _tag: "IdempotencyConflict",
                      intentId: input.createIntentId.value,
                    } satisfies DomainError;
                  return existing;
                }
                const native = await Effect.runPromise(
                  provisioner.provision(context, {
                    projectId: input.projectId,
                    source: input.source,
                  }),
                );
                await Effect.runPromise(
                  Effect.all([
                    validateEntity(native.nativeProjectId, "NativeProjectId"),
                    validateEntity(native.schemaVersion, "NativeSchemaVersion"),
                  ]),
                );
                const owner = owners[native.nativeProjectId.value];
                if (owner !== undefined && owner !== context.tenantId.value)
                  throw {
                    _tag: "TenantAccessDenied",
                    projectId: input.projectId.value,
                  } satisfies DomainError;
                const existingByNative = state.projects.find(
                  (project) =>
                    project.native.nativeProjectId.value === native.nativeProjectId.value &&
                    project.projectId.value !== input.projectId.value,
                );
                if (existingByNative !== undefined)
                  throw {
                    _tag: "StateConflict",
                    record: "Project",
                    detail: "The native project identifier is already mapped in this tenant.",
                  } satisfies DomainError;
                const record: ProjectRecord = {
                  tenantId: context.tenantId,
                  projectId: input.projectId,
                  native,
                  revision: 0,
                  source: input.source,
                  createIntentId: input.createIntentId,
                  createdAt: input.now,
                };
                const next = { ...state, projects: [...state.projects, record] };
                owners[native.nativeProjectId.value] = context.tenantId.value;
                await writeOwnership(owners);
                await persistState(context.tenantId, next);
                return record;
              }),
            catch: (error) =>
              isStoreFailure(error)
                ? error
                : storageFailure(
                    "createProject",
                    error instanceof Error ? error.message : "The project could not be created.",
                  ),
          }),
        ),
      );

    const read = (context: TenantContext): Effect.Effect<TenantState, StoreFailure> =>
      validateContext(context).pipe(
        Effect.flatMap(() =>
          Effect.tryPromise({
            try: () =>
              serial(async () => {
                await mkdir(tenantDirectory(context.tenantId), { recursive: true });
                try {
                  const text = await readBoundedText(statePath(context.tenantId));
                  const wire = await Effect.runPromise(decodeState(text));
                  const state = await Effect.runPromise(stateFromWire(wire));
                  await validateTenantOwnership(state);
                  return await Effect.runPromise(stateForContext(state, context));
                } catch (error) {
                  if (isNotFound(error)) return emptyState(context.tenantId);
                  throw error;
                }
              }),
            catch: (error) =>
              isStoreFailure(error)
                ? error
                : storageFailure(
                    "read",
                    error instanceof Error ? error.message : "The tenant state could not be read.",
                  ),
          }),
        ),
      );

    const update = (
      context: TenantContext,
      change: (state: TenantState) => Effect.Effect<TenantState, StoreFailure>,
    ): Effect.Effect<TenantState, StoreFailure> =>
      validateContext(context).pipe(
        Effect.flatMap(() =>
          Effect.tryPromise({
            try: () =>
              serial(async () => {
                await mkdir(tenantDirectory(context.tenantId), { recursive: true });
                let current: TenantState;
                try {
                  const text = await readBoundedText(statePath(context.tenantId));
                  const wire = await Effect.runPromise(decodeState(text));
                  current = await Effect.runPromise(stateFromWire(wire));
                  await validateTenantOwnership(current);
                } catch (error) {
                  if (!isNotFound(error)) throw error;
                  current = emptyState(context.tenantId);
                }
                const checked = await Effect.runPromise(stateForContext(current, context));
                const next = await Effect.runPromise(change(checked));
                await persistState(context.tenantId, next);
                return next;
              }),
            catch: (error) =>
              isStoreFailure(error)
                ? error
                : storageFailure(
                    "update",
                    error instanceof Error
                      ? error.message
                      : "The tenant state could not be updated.",
                  ),
          }),
        ),
      );

    const getProject = (context: TenantContext, projectId: ProjectId) =>
      validateEntity(projectId, "ProjectId").pipe(
        Effect.flatMap(() => read(context)),
        Effect.flatMap((state) => {
          const project = state.projects.find((item) => item.projectId.value === projectId.value);
          return project === undefined
            ? Effect.fail(recordNotFound("Project", projectId.value))
            : Effect.succeed(project);
        }),
      );

    const getJob = (context: TenantContext, jobId: EntityId<"JobId">) =>
      validateEntity(jobId, "JobId").pipe(
        Effect.flatMap(() => read(context)),
        Effect.flatMap((state) => {
          const job = state.jobs.find((item) => item.jobId.value === jobId.value);
          return job === undefined
            ? Effect.fail(recordNotFound("Job", jobId.value))
            : Effect.succeed(job);
        }),
      );

    const getSubmissionIntent = (context: TenantContext, intentId: IntentId) =>
      validateEntity(intentId, "IntentId").pipe(
        Effect.flatMap(() => read(context)),
        Effect.flatMap((state) => {
          const intent = state.submissionIntents.find(
            (item) => item.submissionIntentId.value === intentId.value,
          );
          return intent === undefined
            ? Effect.fail(recordNotFound("SubmissionIntent", intentId.value))
            : Effect.succeed(intent);
        }),
      );

    const insertAsset = (context: TenantContext, input: CreateAssetInput, allowNative: boolean) =>
      validateAssetInput(context, input).pipe(
        Effect.flatMap(() =>
          input.origin._tag === "NativeOutput" && !allowNative
            ? Effect.fail<StoreFailure>(
                storageFailure("asset", "Native output assets require the verified native path."),
              )
            : input.origin._tag === "NativeOutput" &&
                allowNative &&
                !isVerifiedNativeReceipt(input.origin.receipt)
              ? Effect.fail<StoreFailure>({
                  _tag: "NativeReceiptInvalid",
                  detail: "Native output insertion requires a receipt verified by NativeBridge.",
                })
              : allowNative && input.origin._tag !== "NativeOutput"
                ? Effect.fail<StoreFailure>(
                    storageFailure("asset", "The verified native path requires NativeOutput."),
                  )
                : update(context, (state) => {
                    const project = state.projects.find(
                      (item) => item.projectId.value === input.projectId.value,
                    );
                    if (project === undefined)
                      return Effect.fail(recordNotFound("Project", input.projectId.value));
                    if (project.revision !== input.revision)
                      return Effect.fail({
                        _tag: "StateConflict",
                        record: "Project",
                        detail: `Expected revision ${input.revision}, found ${project.revision}.`,
                      });
                    if (input.origin._tag === "NativeOutput") {
                      const receipt = input.origin.receipt;
                      if (
                        receipt.projectId.value !== project.projectId.value ||
                        receipt.nativeProjectId.value !== project.native.nativeProjectId.value ||
                        receipt.schemaVersion.value !== project.native.schemaVersion.value ||
                        receipt.revision !== project.revision ||
                        !sameSource(receipt.source, project.source) ||
                        !sameSource(receipt.source, input.source)
                      )
                        return Effect.fail<StoreFailure>({
                          _tag: "NativeReceiptInvalid",
                          detail: "The native receipt does not match the stored project mapping.",
                        });
                    }
                    const existing = state.assets.find(
                      (item) => item.assetId.value === input.assetId.value,
                    );
                    if (existing !== undefined)
                      return sameSource(existing.source, input.source) &&
                        existing.projectId.value === input.projectId.value &&
                        existing.revision === input.revision &&
                        sameOrigin(existing.origin, input.origin)
                        ? Effect.succeed(state)
                        : Effect.fail({
                            _tag: "StateConflict",
                            record: "Asset",
                            detail: "The asset identifier is already bound to different content.",
                          });
                    const record: AssetRecord = {
                      tenantId: context.tenantId,
                      assetId: input.assetId,
                      projectId: input.projectId,
                      revision: input.revision,
                      origin: input.origin,
                      source: input.source,
                      createdAt: input.now,
                    };
                    return Effect.succeed({ ...state, assets: [...state.assets, record] });
                  }).pipe(
                    Effect.flatMap((state) =>
                      requireRecord(
                        "Asset",
                        input.assetId.value,
                        state.assets.find((item) => item.assetId.value === input.assetId.value),
                      ),
                    ),
                  ),
        ),
      );

    const service: ApplicationStore = {
      readState: read,
      createProject,
      getProject,
      createAsset: (context, input) => insertAsset(context, input, false),
      createNativeAsset: (context, input) => insertAsset(context, input, true),
      createJob: (context, input) =>
        validateJobInput(context, input).pipe(
          Effect.flatMap(() =>
            update(context, (state) => {
              const project = state.projects.find(
                (item) => item.projectId.value === input.projectId.value,
              );
              if (project === undefined)
                return Effect.fail(recordNotFound("Project", input.projectId.value));
              if (project.revision !== input.revision)
                return Effect.fail({
                  _tag: "StateConflict",
                  record: "Project",
                  detail: `Expected revision ${input.revision}, found ${project.revision}.`,
                });
              const existingByIntent = state.jobs.find(
                (job) => job.intentId.value === input.intentId.value,
              );
              if (existingByIntent !== undefined)
                return existingByIntent.requestFingerprint.value ===
                  input.requestFingerprint.value &&
                  existingByIntent.jobId.value === input.jobId.value &&
                  existingByIntent.projectId.value === input.projectId.value &&
                  existingByIntent.revision === input.revision
                  ? Effect.succeed(state)
                  : Effect.fail({ _tag: "IdempotencyConflict", intentId: input.intentId.value });
              const existingById = state.jobs.find((job) => job.jobId.value === input.jobId.value);
              if (existingById !== undefined)
                return Effect.fail({
                  _tag: "StateConflict",
                  record: "Job",
                  detail: "The job identifier is already in use.",
                });
              const record: JobRecord = {
                tenantId: context.tenantId,
                jobId: input.jobId,
                projectId: input.projectId,
                revision: input.revision,
                intentId: input.intentId,
                requestFingerprint: input.requestFingerprint,
                state: { _tag: "Queued" },
                createdAt: input.now,
              };
              return Effect.succeed({ ...state, jobs: [...state.jobs, record] });
            }).pipe(
              Effect.flatMap((state) =>
                requireRecord(
                  "Job",
                  input.jobId.value,
                  state.jobs.find((item) => item.jobId.value === input.jobId.value),
                ),
              ),
            ),
          ),
        ),
      getJob,
      createReview: (context, input) =>
        validateReviewInput(context, input).pipe(
          Effect.flatMap(() =>
            update(context, (state) => {
              const project = state.projects.find(
                (item) => item.projectId.value === input.projectId.value,
              );
              if (project === undefined)
                return Effect.fail(recordNotFound("Project", input.projectId.value));
              if (project.revision !== input.revision)
                return Effect.fail({
                  _tag: "StateConflict",
                  record: "Project",
                  detail: `Expected revision ${input.revision}, found ${project.revision}.`,
                });
              const existing = state.reviews.find(
                (item) => item.reviewId.value === input.reviewId.value,
              );
              if (existing !== undefined) {
                return existing.projectId.value === input.projectId.value &&
                  existing.revision === input.revision &&
                  existing.plan.value === input.plan.value &&
                  existing.output.value === input.output.value &&
                  existing.renderer.value === input.renderer.value &&
                  existing.disposition === input.disposition
                  ? Effect.succeed(state)
                  : Effect.fail({
                      _tag: "StateConflict",
                      record: "Review",
                      detail: "The review identifier is already bound to different evidence.",
                    });
              }
              const record: ReviewRecord = {
                tenantId: context.tenantId,
                reviewId: input.reviewId,
                projectId: input.projectId,
                revision: input.revision,
                plan: input.plan,
                output: input.output,
                renderer: input.renderer,
                disposition: input.disposition,
                createdAt: input.now,
              };
              return Effect.succeed({ ...state, reviews: [...state.reviews, record] });
            }).pipe(
              Effect.flatMap((state) =>
                requireRecord(
                  "Review",
                  input.reviewId.value,
                  state.reviews.find((item) => item.reviewId.value === input.reviewId.value),
                ),
              ),
            ),
          ),
        ),
      createDelivery: (context, input) =>
        Effect.all([
          validateContext(context),
          validateEntity(input.deliveryId, "DeliveryId"),
          validateEntity(input.projectId, "ProjectId"),
          validateEntity(input.assetId, "AssetId"),
          validateNumber("delivery.revision", input.revision),
          validateNumber("delivery.now", input.now),
        ]).pipe(
          Effect.asVoid,
          Effect.flatMap(() =>
            update(context, (state) => {
              const project = state.projects.find(
                (item) => item.projectId.value === input.projectId.value,
              );
              const asset = state.assets.find((item) => item.assetId.value === input.assetId.value);
              if (project === undefined)
                return Effect.fail(recordNotFound("Project", input.projectId.value));
              if (asset === undefined)
                return Effect.fail(recordNotFound("Asset", input.assetId.value));
              if (
                project.revision !== input.revision ||
                asset.projectId.value !== input.projectId.value ||
                asset.revision !== input.revision
              )
                return Effect.fail({
                  _tag: "StateConflict",
                  record: "Delivery",
                  detail: "The delivery does not match the project, revision, and asset.",
                });
              const existing = state.deliveries.find(
                (item) => item.deliveryId.value === input.deliveryId.value,
              );
              if (existing !== undefined) {
                return existing.projectId.value === input.projectId.value &&
                  existing.revision === input.revision &&
                  existing.assetId.value === input.assetId.value
                  ? Effect.succeed(state)
                  : Effect.fail({
                      _tag: "StateConflict",
                      record: "Delivery",
                      detail: "The delivery identifier is already bound to another asset.",
                    });
              }
              const record: DeliveryRecord = {
                tenantId: context.tenantId,
                deliveryId: input.deliveryId,
                projectId: input.projectId,
                revision: input.revision,
                assetId: input.assetId,
                state: { _tag: "Prepared" },
                createdAt: input.now,
                updatedAt: input.now,
              };
              return Effect.succeed({ ...state, deliveries: [...state.deliveries, record] });
            }).pipe(
              Effect.flatMap((state) =>
                requireRecord(
                  "Delivery",
                  input.deliveryId.value,
                  state.deliveries.find((item) => item.deliveryId.value === input.deliveryId.value),
                ),
              ),
            ),
          ),
        ),
      getDelivery: (context, deliveryId) =>
        validateContext(context).pipe(
          Effect.flatMap(() => validateEntity(deliveryId, "DeliveryId")),
          Effect.flatMap(() =>
            read(context).pipe(
              Effect.flatMap((state) =>
                requireRecord(
                  "Delivery",
                  deliveryId.value,
                  state.deliveries.find((item) => item.deliveryId.value === deliveryId.value),
                ),
              ),
            ),
          ),
        ),
      reserveBudget: (context, input) =>
        Effect.all([
          validateContext(context),
          validateEntity(input.budgetId, "BudgetId"),
          validateEntity(input.projectId, "ProjectId"),
          validateNumber("budget.limitUnits", input.limitUnits, true),
          validateNumber("budget.requestedUnits", input.requestedUnits, true),
          validateNumber("budget.now", input.now),
        ]).pipe(
          Effect.asVoid,
          Effect.flatMap(() =>
            update(context, (state) => {
              const project = state.projects.find(
                (item) => item.projectId.value === input.projectId.value,
              );
              if (project === undefined)
                return Effect.fail(recordNotFound("Project", input.projectId.value));
              if (
                input.limitUnits <= 0 ||
                input.requestedUnits <= 0 ||
                input.requestedUnits > input.limitUnits
              )
                return Effect.fail({
                  _tag: "BudgetExceeded",
                  projectId: input.projectId.value,
                  requested: input.requestedUnits,
                  available: input.limitUnits,
                });
              const existing = state.budgets.find(
                (item) => item.budgetId.value === input.budgetId.value,
              );
              if (existing !== undefined) {
                return existing.projectId.value === input.projectId.value &&
                  existing.reservedUnits === input.requestedUnits &&
                  existing.limitUnits === input.limitUnits
                  ? Effect.succeed(state)
                  : Effect.fail({
                      _tag: "StateConflict",
                      record: "Budget",
                      detail: "The budget identifier is already bound to a different reservation.",
                    });
              }
              const record: BudgetRecord = {
                tenantId: context.tenantId,
                budgetId: input.budgetId,
                projectId: input.projectId,
                limitUnits: input.limitUnits,
                reservedUnits: input.requestedUnits,
                spentUnits: 0,
                updatedAt: input.now,
              };
              return Effect.succeed({ ...state, budgets: [...state.budgets, record] });
            }).pipe(
              Effect.flatMap((state) =>
                requireRecord(
                  "Budget",
                  input.budgetId.value,
                  state.budgets.find((item) => item.budgetId.value === input.budgetId.value),
                ),
              ),
            ),
          ),
        ),
      claimWorker: (context, input) =>
        Effect.all([
          validateContext(context),
          validateEntity(input.claimId, "WorkerClaimId"),
          validateEntity(input.jobId, "JobId"),
          validateText("worker.workerId", input.workerId),
          validateNumber("worker.fence", input.fence),
          validateNumber("worker.leaseExpiresAt", input.leaseExpiresAt),
          validateNumber("worker.now", input.now),
        ]).pipe(
          Effect.asVoid,
          Effect.flatMap(() =>
            update(context, (state) => {
              if (!state.jobs.some((job) => job.jobId.value === input.jobId.value))
                return Effect.fail(recordNotFound("Job", input.jobId.value));
              if (!isIdentifierValue(input.workerId))
                return Effect.fail(storageFailure("input", "The worker identifier is invalid."));
              if (input.leaseExpiresAt <= input.now)
                return Effect.fail({
                  _tag: "WorkerLeaseConflict",
                  jobId: input.jobId.value,
                  owner: input.workerId,
                });
              const existing = state.workerClaims.find(
                (item) => item.claimId.value === input.claimId.value,
              );
              if (existing !== undefined) {
                return existing.jobId.value === input.jobId.value &&
                  existing.state._tag === "Active" &&
                  existing.state.workerId === input.workerId &&
                  existing.state.fence === input.fence &&
                  existing.state.leaseExpiresAt === input.leaseExpiresAt &&
                  existing.state.claimedAt === input.now
                  ? Effect.succeed(state)
                  : Effect.fail({
                      _tag: "StateConflict",
                      record: "WorkerClaim",
                      detail: "The claim identifier is already in use.",
                    });
              }
              const conflicting = state.workerClaims.find(
                (claim) =>
                  claim.jobId.value === input.jobId.value &&
                  claim.state._tag === "Active" &&
                  (claim.state.workerId !== input.workerId || claim.state.fence !== input.fence),
              );
              if (conflicting !== undefined && conflicting.state._tag === "Active")
                return Effect.fail({
                  _tag: "WorkerLeaseConflict",
                  jobId: input.jobId.value,
                  owner: conflicting.state.workerId,
                });
              const highestFence = state.workerClaims
                .filter((claim) => claim.jobId.value === input.jobId.value)
                .reduce((maximum, claim) => {
                  const fence = claim.state.fence;
                  return Math.max(maximum, fence);
                }, -1);
              if (input.fence <= highestFence)
                return Effect.fail({
                  _tag: "WorkerLeaseConflict",
                  jobId: input.jobId.value,
                  owner: "fence-regression",
                });
              const record: WorkerClaimRecord = {
                tenantId: context.tenantId,
                claimId: input.claimId,
                jobId: input.jobId,
                state: {
                  _tag: "Active",
                  workerId: input.workerId,
                  fence: input.fence,
                  leaseExpiresAt: input.leaseExpiresAt,
                  claimedAt: input.now,
                },
              };
              return Effect.succeed({ ...state, workerClaims: [...state.workerClaims, record] });
            }).pipe(
              Effect.flatMap((state) =>
                requireRecord(
                  "WorkerClaim",
                  input.claimId.value,
                  state.workerClaims.find((item) => item.claimId.value === input.claimId.value),
                ),
              ),
            ),
          ),
        ),
      releaseWorker: (context, input) =>
        Effect.all([
          validateContext(context),
          validateEntity(input.claimId, "WorkerClaimId"),
          validateText("worker.workerId", input.workerId),
          validateNumber("worker.fence", input.fence),
          validateNumber("worker.releasedAt", input.releasedAt),
        ]).pipe(
          Effect.asVoid,
          Effect.flatMap(() =>
            update(context, (state) => {
              const index = state.workerClaims.findIndex(
                (item) => item.claimId.value === input.claimId.value,
              );
              const existing = index >= 0 ? state.workerClaims[index] : undefined;
              if (existing === undefined)
                return Effect.fail(recordNotFound("WorkerClaim", input.claimId.value));
              if (existing.state._tag === "Released")
                return existing.state.workerId === input.workerId &&
                  existing.state.fence === input.fence &&
                  existing.state.releasedAt === input.releasedAt
                  ? Effect.succeed(state)
                  : Effect.fail({
                      _tag: "WorkerLeaseConflict",
                      jobId: existing.jobId.value,
                      owner: existing.state.workerId,
                    });
              if (
                existing.state.workerId !== input.workerId ||
                existing.state.fence !== input.fence ||
                input.releasedAt < existing.state.claimedAt
              )
                return Effect.fail({
                  _tag: "WorkerLeaseConflict",
                  jobId: existing.jobId.value,
                  owner: existing.state.workerId,
                });
              const replacement: WorkerClaimRecord = {
                ...existing,
                state: {
                  _tag: "Released",
                  workerId: input.workerId,
                  fence: input.fence,
                  releasedAt: input.releasedAt,
                },
              };
              return Effect.succeed({
                ...state,
                workerClaims: state.workerClaims.map((item, itemIndex) =>
                  itemIndex === index ? replacement : item,
                ),
              });
            }).pipe(
              Effect.flatMap((state) =>
                requireRecord(
                  "WorkerClaim",
                  input.claimId.value,
                  state.workerClaims.find((item) => item.claimId.value === input.claimId.value),
                ),
              ),
            ),
          ),
        ),
      prepareSubmission: (context, input) =>
        validateSubmissionInput(context, input).pipe(
          Effect.flatMap(() =>
            (() => {
              let created = false;
              return update(context, (state) => {
                const job = state.jobs.find((item) => item.jobId.value === input.jobId.value);
                if (job === undefined) return Effect.fail(recordNotFound("Job", input.jobId.value));
                if (job.requestFingerprint.value !== input.requestFingerprint.value)
                  return Effect.fail({
                    _tag: "IdempotencyConflict",
                    intentId: input.submissionIntentId.value,
                  });
                const existing = state.submissionIntents.find(
                  (item) => item.submissionIntentId.value === input.submissionIntentId.value,
                );
                if (existing !== undefined) {
                  return existing.jobId.value === input.jobId.value &&
                    existing.requestFingerprint.value === input.requestFingerprint.value &&
                    existing.provider === input.provider &&
                    existing.attemptId.value === input.attemptId.value
                    ? Effect.succeed(state)
                    : Effect.fail({
                        _tag: "IdempotencyConflict",
                        intentId: input.submissionIntentId.value,
                      });
                }
                if (job.state._tag === "ReconciliationRequired")
                  return Effect.fail({
                    _tag: "ReconciliationRequired",
                    intentId: job.state.submissionIntentId.value,
                  });
                if (job.state._tag !== "Queued")
                  return Effect.fail({
                    _tag: "StateConflict",
                    record: "Job",
                    detail: `Job is already ${job.state._tag}.`,
                  });
                if (state.attempts.some((item) => item.attemptId.value === input.attemptId.value))
                  return Effect.fail({
                    _tag: "IdempotencyConflict",
                    intentId: input.submissionIntentId.value,
                  });
                const attempt: AttemptRecord = {
                  tenantId: context.tenantId,
                  attemptId: input.attemptId,
                  jobId: input.jobId,
                  submissionIntentId: input.submissionIntentId,
                  state: { _tag: "Prepared" },
                  createdAt: input.now,
                };
                const intent: SubmissionIntentRecord = {
                  tenantId: context.tenantId,
                  submissionIntentId: input.submissionIntentId,
                  jobId: input.jobId,
                  attemptId: input.attemptId,
                  provider: input.provider,
                  requestFingerprint: input.requestFingerprint,
                  state: { _tag: "Prepared" },
                  createdAt: input.now,
                  updatedAt: input.now,
                };
                created = true;
                const nextJob: JobRecord = {
                  ...job,
                  state: { _tag: "Submitting", submissionIntentId: input.submissionIntentId },
                };
                return Effect.succeed({
                  ...state,
                  jobs: state.jobs.map((item) =>
                    item.jobId.value === job.jobId.value ? nextJob : item,
                  ),
                  attempts: [...state.attempts, attempt],
                  submissionIntents: [...state.submissionIntents, intent],
                });
              }).pipe(
                Effect.flatMap((state) => {
                  const intent = state.submissionIntents.find(
                    (item) => item.submissionIntentId.value === input.submissionIntentId.value,
                  );
                  return intent === undefined
                    ? Effect.fail(
                        recordNotFound("SubmissionIntent", input.submissionIntentId.value),
                      )
                    : Effect.succeed(
                        created
                          ? { _tag: "Created" as const, intent }
                          : { _tag: "Existing" as const, intent },
                      );
                }),
              );
            })(),
          ),
        ),
      getSubmissionIntent,
      recordSubmission: (context, intentId, result) =>
        Effect.all([validateEntity(intentId, "IntentId"), validateSubmissionResult(result)]).pipe(
          Effect.asVoid,
          Effect.flatMap(() =>
            update(context, (state) => {
              const intentIndex = state.submissionIntents.findIndex(
                (item) => item.submissionIntentId.value === intentId.value,
              );
              const intent = intentIndex >= 0 ? state.submissionIntents[intentIndex] : undefined;
              if (intent === undefined)
                return Effect.fail(recordNotFound("SubmissionIntent", intentId.value));
              const attemptIndex = state.attempts.findIndex(
                (item) => item.attemptId.value === intent.attemptId.value,
              );
              const attempt = attemptIndex >= 0 ? state.attempts[attemptIndex] : undefined;
              const jobIndex = state.jobs.findIndex(
                (item) => item.jobId.value === intent.jobId.value,
              );
              const job = jobIndex >= 0 ? state.jobs[jobIndex] : undefined;
              if (
                attempt === undefined ||
                job === undefined ||
                attempt.jobId.value !== job.jobId.value ||
                attempt.submissionIntentId.value !== intent.submissionIntentId.value
              )
                return Effect.fail(
                  storageFailure(
                    "recordSubmission",
                    "The job, attempt, and intent join is invalid.",
                  ),
                );
              if (intent.state._tag !== "Prepared" && intent.state._tag !== "Unknown") {
                const matches =
                  (intent.state._tag === "Confirmed" &&
                    result._tag === "Confirmed" &&
                    intent.state.providerReference === result.providerReference) ||
                  (intent.state._tag === "Rejected" &&
                    result._tag === "Rejected" &&
                    intent.state.reason === result.reason);
                return matches
                  ? Effect.succeed(state)
                  : Effect.fail({
                      _tag: "IdempotencyConflict",
                      intentId: intent.submissionIntentId.value,
                    });
              }
              const now = Date.now();
              const nextState: SubmissionState =
                result._tag === "Confirmed"
                  ? { _tag: "Confirmed", providerReference: result.providerReference }
                  : result._tag === "Rejected"
                    ? { _tag: "Rejected", reason: result.reason }
                    : { _tag: "Unknown", reason: result.reason };
              const nextIntent: SubmissionIntentRecord = {
                ...intent,
                state: nextState,
                updatedAt: now,
              };
              const nextAttempt: AttemptRecord = {
                ...attempt,
                state:
                  result._tag === "Confirmed"
                    ? { _tag: "Submitted", providerReference: result.providerReference }
                    : result._tag === "Rejected"
                      ? { _tag: "Rejected", reason: result.reason }
                      : { _tag: "Unknown", reason: result.reason },
              };
              const nextJob: JobRecord = {
                ...job,
                state:
                  result._tag === "Confirmed"
                    ? { _tag: "Running", providerReference: result.providerReference }
                    : result._tag === "Rejected"
                      ? { _tag: "Failed", reason: result.reason }
                      : {
                          _tag: "ReconciliationRequired",
                          submissionIntentId: intent.submissionIntentId,
                          reason: result.reason,
                        },
              };
              return Effect.succeed({
                ...state,
                submissionIntents: state.submissionIntents.map((item, index) =>
                  index === intentIndex ? nextIntent : item,
                ),
                attempts: state.attempts.map((item, index) =>
                  index === attemptIndex ? nextAttempt : item,
                ),
                jobs: state.jobs.map((item, index) => (index === jobIndex ? nextJob : item)),
              });
            }).pipe(
              Effect.flatMap((state) =>
                requireRecord(
                  "SubmissionIntent",
                  intentId.value,
                  state.submissionIntents.find(
                    (item) => item.submissionIntentId.value === intentId.value,
                  ),
                ),
              ),
            ),
          ),
        ),
    };
    const close = (): Effect.Effect<void, StorageError> =>
      Effect.tryPromise({
        try: async () => {
          if (closePromise !== undefined) return closePromise;
          closing = true;
          closePromise = tail.then(async () => {
            await lockHandle.close();
            closed = true;
            await unlink(lockPath).catch(() => undefined);
          });
          return closePromise;
        },
        catch: (error) =>
          storageFailure(
            "close",
            error instanceof Error ? error.message : "The local store could not be closed.",
          ),
      });
    return { root, service, close };
  };

  return Effect.tryPromise({
    try: async () => {
      await mkdir(root, { recursive: true });
      try {
        const lockHandle = await open(lockPath, "wx");
        return runStore(lockHandle);
      } catch (error) {
        if (isRecord(error) && error.code === "EEXIST")
          throw storageFailure("open", "A store is already open for this root.");
        throw error;
      }
    },
    catch: (error) =>
      isStoreFailure(error) && error._tag === "StorageError"
        ? error
        : storageFailure(
            "open",
            error instanceof Error ? error.message : "The local store could not be opened.",
          ),
  });
};
