import { Context, Effect, Layer } from "effect";
import {
  type AssetRecord,
  type CreateAssetInput,
  type CreateClientAssetInput,
  type CreateProjectRequest,
  type CreateJobInput,
  type CreateReviewInput,
  type DomainError,
  type JobRecord,
  type NativeBridge,
  type NativeReceipt,
  type NativeSchemaVersion,
  type ProviderBridge,
  type ProjectId,
  type ProjectRecord,
  type ReviewRecord,
  type SubmissionIntentRecord,
  type TenantContext,
  type AuthorizedProjectMapping,
  type PrepareSubmissionInput,
  type IntentId,
  type AssetOrigin,
  type WorkerClaimRecord,
  type ClaimWorkerInput,
  type BudgetRecord,
  type DeliveryRecord,
  type CreateDeliveryInput,
  type ReleaseWorkerInput,
} from "./domain";
import { type ApplicationStore } from "./storage";
import { unconfiguredNative, unconfiguredProvider } from "./domain";
import { markVerifiedNativeReceipt } from "./native-authority";

export interface StudioApplication {
  readonly authorizeProject: (
    context: TenantContext,
    projectId: ProjectId,
  ) => Effect.Effect<AuthorizedProjectMapping, DomainError>;
  readonly createProject: (
    context: TenantContext,
    input: CreateProjectRequest,
  ) => Effect.Effect<ProjectRecord, DomainError>;
  readonly createAsset: (
    context: TenantContext,
    input: CreateClientAssetInput,
  ) => Effect.Effect<AssetRecord, DomainError>;
  readonly createJob: (
    context: TenantContext,
    input: CreateJobInput,
  ) => Effect.Effect<JobRecord, DomainError>;
  readonly createReview: (
    context: TenantContext,
    input: CreateReviewInput,
  ) => Effect.Effect<ReviewRecord, DomainError>;
  readonly reserveBudget: (
    context: TenantContext,
    input: Parameters<ApplicationStore["reserveBudget"]>[1],
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
    deliveryId: CreateDeliveryInput["deliveryId"],
  ) => Effect.Effect<DeliveryRecord, DomainError>;
  readonly submitJob: (
    context: TenantContext,
    input: PrepareSubmissionInput,
  ) => Effect.Effect<SubmissionIntentRecord, DomainError>;
  readonly reconcileJob: (
    context: TenantContext,
    intentId: IntentId,
  ) => Effect.Effect<SubmissionIntentRecord, DomainError>;
  readonly registerNativeAsset: (
    context: TenantContext,
    input: Omit<CreateAssetInput, "origin" | "schemaVersion"> & {
      readonly nativeReceipt: unknown;
    },
  ) => Effect.Effect<AssetRecord, DomainError>;
  readonly nativeReceipt: (
    schemaVersion: NativeSchemaVersion,
    receipt: unknown,
  ) => Effect.Effect<NativeReceipt, DomainError>;
}

export class StudioApplicationService extends Context.Service<
  StudioApplicationService,
  StudioApplication
>()("video-studio/StudioApplication") {}

export class ProviderBridgeService extends Context.Service<ProviderBridgeService, ProviderBridge>()(
  "video-studio/ProviderBridge",
) {}

export class NativeBridgeService extends Context.Service<NativeBridgeService, NativeBridge>()(
  "video-studio/NativeBridge",
) {}

const mappingFor = (
  context: TenantContext,
  project: ProjectRecord,
): Effect.Effect<AuthorizedProjectMapping, DomainError> =>
  project.tenantId.value === context.tenantId.value
    ? Effect.succeed({
        tenantId: context.tenantId,
        actorId: context.actorId,
        projectId: project.projectId,
        native: project.native,
        revision: project.revision,
        source: project.source,
      })
    : Effect.fail({ _tag: "TenantAccessDenied", projectId: project.projectId.value });

const assertNow = (now: number): Effect.Effect<number, DomainError> =>
  Number.isSafeInteger(now) && now >= 0
    ? Effect.succeed(now)
    : Effect.fail({ _tag: "InvalidNumber", field: "now", value: now });

const assertNonNegative = (field: string, value: number): Effect.Effect<number, DomainError> =>
  Number.isSafeInteger(value) && value >= 0
    ? Effect.succeed(value)
    : Effect.fail({ _tag: "InvalidNumber", field, value });

const sameSource = (left: unknown, right: unknown): boolean => {
  if (typeof left !== "object" || left === null || typeof right !== "object" || right === null)
    return false;
  const leftSource = left as {
    readonly sha256?: { readonly value?: unknown };
    readonly bytes?: unknown;
  };
  const rightSource = right as {
    readonly sha256?: { readonly value?: unknown };
    readonly bytes?: unknown;
  };
  return (
    typeof leftSource.bytes === "number" &&
    typeof rightSource.bytes === "number" &&
    leftSource.bytes === rightSource.bytes &&
    leftSource.sha256?.value === rightSource.sha256?.value
  );
};

export const makeStudioApplication = (
  store: ApplicationStore,
  provider: ProviderBridge = unconfiguredProvider,
  native: NativeBridge = unconfiguredNative,
): StudioApplication => {
  const authorizeProject = (context: TenantContext, projectId: ProjectId) =>
    store
      .getProject(context, projectId)
      .pipe(Effect.flatMap((project) => mappingFor(context, project)));

  const createProject = (context: TenantContext, input: CreateProjectRequest) =>
    assertNow(input.now).pipe(Effect.flatMap(() => store.createProject(context, input)));

  const createAsset = (context: TenantContext, input: CreateClientAssetInput) =>
    authorizeProject(context, input.projectId).pipe(
      Effect.flatMap((mapping) =>
        mapping.revision === input.revision &&
        input.declaredBy?.kind === "ActorId" &&
        input.declaredBy.value === context.actorId.value
          ? store.createAsset(context, {
              ...input,
              origin: { _tag: "ClientImport", declaredBy: input.declaredBy },
            })
          : Effect.fail<DomainError>({
              _tag: "StateConflict",
              record: "Project",
              detail:
                "The asset revision or declaring actor does not match the authorized project.",
            }),
      ),
    );

  const createJob = (context: TenantContext, input: CreateJobInput) =>
    authorizeProject(context, input.projectId).pipe(
      Effect.flatMap((mapping) =>
        mapping.revision === input.revision
          ? store.createJob(context, input)
          : Effect.fail<DomainError>({
              _tag: "StateConflict",
              record: "Project",
              detail: "The job revision does not match the authorized project revision.",
            }),
      ),
    );

  const createReview = (context: TenantContext, input: CreateReviewInput) =>
    authorizeProject(context, input.projectId).pipe(
      Effect.flatMap((mapping) =>
        mapping.revision === input.revision
          ? store.createReview(context, input)
          : Effect.fail<DomainError>({
              _tag: "StateConflict",
              record: "Project",
              detail: "The review revision does not match the authorized project revision.",
            }),
      ),
    );

  const submitJob = (context: TenantContext, input: PrepareSubmissionInput) =>
    Effect.gen(function* () {
      const preparation = yield* store.prepareSubmission(context, input);
      if (preparation._tag === "Existing") {
        if (preparation.intent.state._tag === "Unknown")
          return yield* Effect.fail<DomainError>({
            _tag: "ReconciliationRequired",
            intentId: preparation.intent.submissionIntentId.value,
          });
        return preparation.intent;
      }
      const result = yield* provider.submit(preparation.intent);
      return yield* store.recordSubmission(context, preparation.intent.submissionIntentId, result);
    });

  const reconcileJob = (context: TenantContext, intentId: IntentId) =>
    Effect.gen(function* () {
      const intent = yield* store.getSubmissionIntent(context, intentId);
      if (intent.state._tag !== "Prepared" && intent.state._tag !== "Unknown")
        return yield* Effect.fail<DomainError>({
          _tag: "StateConflict",
          record: "SubmissionIntent",
          detail: "Only an unconfirmed submission can be reconciled.",
        });
      const result = yield* provider.reconcile(intent);
      return yield* store.recordSubmission(context, intent.submissionIntentId, result);
    });

  const nativeReceipt = (schemaVersion: NativeSchemaVersion, receipt: unknown) =>
    native.verifyReceipt(schemaVersion, receipt);

  const registerNativeAsset = (
    context: TenantContext,
    input: Omit<CreateAssetInput, "origin" | "schemaVersion"> & {
      readonly nativeReceipt: unknown;
    },
  ) =>
    Effect.gen(function* () {
      const mapping = yield* authorizeProject(context, input.projectId);
      if (mapping.revision !== input.revision)
        return yield* Effect.fail<DomainError>({
          _tag: "StateConflict",
          record: "Project",
          detail: "The native asset revision does not match the authorized project.",
        });
      const receipt = yield* native.verifyReceipt(
        mapping.native.schemaVersion,
        input.nativeReceipt,
      );
      if (receipt.schemaVersion.value !== mapping.native.schemaVersion.value)
        return yield* Effect.fail<DomainError>({
          _tag: "NativeReceiptInvalid",
          detail:
            "The native receipt schema version does not match the authorized project mapping.",
        });
      if (
        receipt.nativeProjectId.value !== mapping.native.nativeProjectId.value ||
        receipt.projectId.value !== mapping.projectId.value ||
        receipt.revision !== mapping.revision ||
        !sameSource(receipt.source, mapping.source) ||
        !sameSource(receipt.source, input.source)
      )
        return yield* Effect.fail<DomainError>({
          _tag: "NativeReceiptInvalid",
          detail: "The native receipt is not bound to the authorized project revision and source.",
        });
      const origin: AssetOrigin = {
        _tag: "NativeOutput",
        receipt: markVerifiedNativeReceipt(receipt),
      };
      return yield* store.createNativeAsset(context, { ...input, origin });
    });

  return {
    authorizeProject,
    createProject,
    createAsset,
    createJob,
    createReview,
    reserveBudget: (context, input) =>
      Effect.all([
        assertNow(input.now),
        assertNonNegative("budget.limitUnits", input.limitUnits),
        assertNonNegative("budget.requestedUnits", input.requestedUnits),
      ]).pipe(Effect.flatMap(() => store.reserveBudget(context, input))),
    claimWorker: (context, input) =>
      Effect.all([
        assertNow(input.now),
        assertNonNegative("worker.fence", input.fence),
        assertNonNegative("worker.leaseExpiresAt", input.leaseExpiresAt),
      ]).pipe(Effect.flatMap(() => store.claimWorker(context, input))),
    releaseWorker: (context, input) =>
      Effect.all([
        assertNonNegative("worker.fence", input.fence),
        assertNow(input.releasedAt),
      ]).pipe(Effect.flatMap(() => store.releaseWorker(context, input))),
    createDelivery: (context, input) =>
      assertNow(input.now).pipe(Effect.flatMap(() => store.createDelivery(context, input))),
    getDelivery: (context, deliveryId) => store.getDelivery(context, deliveryId),
    submitJob,
    reconcileJob,
    registerNativeAsset,
    nativeReceipt,
  };
};

export const studioApplicationLayer = (
  store: ApplicationStore,
  provider: ProviderBridge = unconfiguredProvider,
  native: NativeBridge = unconfiguredNative,
): Layer.Layer<StudioApplicationService | ProviderBridgeService | NativeBridgeService> =>
  Layer.mergeAll(
    Layer.succeed(StudioApplicationService, makeStudioApplication(store, provider, native)),
    Layer.succeed(ProviderBridgeService, provider),
    Layer.succeed(NativeBridgeService, native),
  );
