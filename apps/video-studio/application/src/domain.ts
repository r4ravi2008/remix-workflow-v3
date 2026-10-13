import { Effect } from "effect";

export type IdKind =
  | "TenantId"
  | "ActorId"
  | "ProjectId"
  | "NativeProjectId"
  | "RevisionId"
  | "AssetId"
  | "JobId"
  | "AttemptId"
  | "ReviewId"
  | "BudgetId"
  | "WorkerClaimId"
  | "IntentId"
  | "DeliveryId"
  | "NativeReceiptId"
  | "NativeSchemaVersion"
  | "NativeTimelineIdentity";

export type EntityId<K extends IdKind> = Readonly<{
  readonly kind: K;
  readonly value: string;
}>;

export type TenantId = EntityId<"TenantId">;
export type ActorId = EntityId<"ActorId">;
export type ProjectId = EntityId<"ProjectId">;
export type NativeProjectId = EntityId<"NativeProjectId">;
export type RevisionId = EntityId<"RevisionId">;
export type AssetId = EntityId<"AssetId">;
export type JobId = EntityId<"JobId">;
export type AttemptId = EntityId<"AttemptId">;
export type ReviewId = EntityId<"ReviewId">;
export type BudgetId = EntityId<"BudgetId">;
export type WorkerClaimId = EntityId<"WorkerClaimId">;
export type IntentId = EntityId<"IntentId">;
export type NativeReceiptId = EntityId<"NativeReceiptId">;
export type DeliveryId = EntityId<"DeliveryId">;

export type Sha256 = Readonly<{
  readonly kind: "Sha256";
  readonly value: string;
}>;

export type NativeSchemaVersion = Readonly<{
  readonly kind: "NativeSchemaVersion";
  readonly value: string;
}>;

export type NativeTimelineIdentity = Readonly<{
  readonly kind: "NativeTimelineIdentity";
  readonly value: string;
}>;

export type DomainError =
  | InvalidIdentifierError
  | InvalidHashError
  | InvalidNumberError
  | TenantAccessDeniedError
  | RecordNotFoundError
  | IdempotencyConflictError
  | StateConflictError
  | ReconciliationRequiredError
  | WorkerLeaseConflictError
  | BudgetExceededError
  | StorageError
  | ProviderUnconfiguredError
  | NativeProvisioningUnavailableError
  | NativeUnconfiguredError
  | NativeReceiptInvalidError;

export interface InvalidIdentifierError {
  readonly _tag: "InvalidIdentifier";
  readonly kind: IdKind;
  readonly value: string;
}

export interface InvalidHashError {
  readonly _tag: "InvalidHash";
  readonly value: string;
}

export interface InvalidNumberError {
  readonly _tag: "InvalidNumber";
  readonly field: string;
  readonly value: number;
}

export interface TenantAccessDeniedError {
  readonly _tag: "TenantAccessDenied";
  readonly projectId: string;
}

export interface RecordNotFoundError {
  readonly _tag: "RecordNotFound";
  readonly record: string;
  readonly id: string;
}

export interface IdempotencyConflictError {
  readonly _tag: "IdempotencyConflict";
  readonly intentId: string;
}

export interface StateConflictError {
  readonly _tag: "StateConflict";
  readonly record: string;
  readonly detail: string;
}

export interface ReconciliationRequiredError {
  readonly _tag: "ReconciliationRequired";
  readonly intentId: string;
}

export interface WorkerLeaseConflictError {
  readonly _tag: "WorkerLeaseConflict";
  readonly jobId: string;
  readonly owner: string;
}

export interface BudgetExceededError {
  readonly _tag: "BudgetExceeded";
  readonly projectId: string;
  readonly requested: number;
  readonly available: number;
}

export interface StorageError {
  readonly _tag: "StorageError";
  readonly operation: string;
  readonly detail: string;
}

export interface ProviderUnconfiguredError {
  readonly _tag: "ProviderUnconfigured";
  readonly provider: string;
}

export interface NativeProvisioningUnavailableError {
  readonly _tag: "NativeProvisioningUnavailable";
}

export interface NativeUnconfiguredError {
  readonly _tag: "NativeUnconfigured";
  readonly schemaVersion: string;
}

export interface NativeReceiptInvalidError {
  readonly _tag: "NativeReceiptInvalid";
  readonly detail: string;
}

export const MAX_SOURCE_BYTES = 1_099_511_627_776;
export const MAX_TEXT_LENGTH = 4096;
const identifierPattern = /^[a-z0-9][a-z0-9_-]{0,63}$/;
const hashPattern = /^[a-f0-9]{64}$/;

export const isIdentifierValue = (value: unknown): value is string =>
  typeof value === "string" && identifierPattern.test(value);

export const isSha256Value = (value: unknown): value is string =>
  typeof value === "string" && hashPattern.test(value);

export const makeId = <K extends IdKind>(
  kind: K,
  value: string,
): Effect.Effect<EntityId<K>, InvalidIdentifierError> =>
  isIdentifierValue(value)
    ? Effect.succeed({ kind, value })
    : Effect.fail({ _tag: "InvalidIdentifier", kind, value });

export const makeSha256 = (value: string): Effect.Effect<Sha256, InvalidHashError> =>
  isSha256Value(value)
    ? Effect.succeed({ kind: "Sha256", value })
    : Effect.fail({ _tag: "InvalidHash", value });

export const makeNativeSchemaVersion = (
  value: string,
): Effect.Effect<NativeSchemaVersion, InvalidIdentifierError> =>
  isIdentifierValue(value)
    ? Effect.succeed({ kind: "NativeSchemaVersion", value })
    : Effect.fail({ _tag: "InvalidIdentifier", kind: "NativeSchemaVersion", value });

export const makeNativeTimelineIdentity = (
  value: string,
): Effect.Effect<NativeTimelineIdentity, InvalidIdentifierError> =>
  isIdentifierValue(value)
    ? Effect.succeed({ kind: "NativeTimelineIdentity", value })
    : Effect.fail({ _tag: "InvalidIdentifier", kind: "NativeTimelineIdentity", value });

export const makePositiveNumber = (
  field: string,
  value: number,
): Effect.Effect<number, InvalidNumberError> =>
  Number.isFinite(value) && Number.isSafeInteger(value) && value > 0
    ? Effect.succeed(value)
    : Effect.fail({ _tag: "InvalidNumber", field, value });

export const makeNonNegativeNumber = (
  field: string,
  value: number,
): Effect.Effect<number, InvalidNumberError> =>
  Number.isFinite(value) && Number.isSafeInteger(value) && value >= 0
    ? Effect.succeed(value)
    : Effect.fail({ _tag: "InvalidNumber", field, value });

export interface TenantContext {
  readonly tenantId: TenantId;
  readonly actorId: ActorId;
}

/** The only input accepted by the trusted native-project provisioning seam. */
export interface NativeProvisioningRequest {
  readonly projectId: ProjectId;
  readonly source: SourceIdentity;
}

export interface NativeProjectProvisioner {
  readonly provision: (
    context: TenantContext,
    request: NativeProvisioningRequest,
  ) => Effect.Effect<
    NativeProjectBinding,
    NativeProvisioningUnavailableError | NativeReceiptInvalidError
  >;
}

export interface SourceIdentity {
  readonly sha256: Sha256;
  readonly bytes: number;
}

export interface NativeReceipt {
  readonly receiptId: NativeReceiptId;
  readonly schemaVersion: NativeSchemaVersion;
  readonly nativeProjectId: NativeProjectId;
  readonly projectId: ProjectId;
  readonly revision: number;
  readonly source: SourceIdentity;
  readonly timeline: NativeTimelineIdentity;
}

export interface NativeProjectBinding {
  readonly nativeProjectId: NativeProjectId;
  readonly schemaVersion: NativeSchemaVersion;
}

export interface AuthorizedProjectMapping {
  readonly tenantId: TenantId;
  readonly actorId: ActorId;
  readonly projectId: ProjectId;
  readonly native: NativeProjectBinding;
  readonly revision: number;
  readonly source: SourceIdentity;
}

export interface ProjectRecord {
  readonly tenantId: TenantId;
  readonly projectId: ProjectId;
  readonly native: NativeProjectBinding;
  readonly revision: number;
  readonly source: SourceIdentity;
  readonly createIntentId: IntentId;
  readonly createdAt: number;
}

export type AssetOrigin =
  | Readonly<{
      readonly _tag: "ClientImport";
      readonly declaredBy: ActorId;
    }>
  | Readonly<{
      readonly _tag: "NativeOutput";
      readonly receipt: NativeReceipt;
    }>;

export interface AssetRecord {
  readonly tenantId: TenantId;
  readonly assetId: AssetId;
  readonly projectId: ProjectId;
  readonly revision: number;
  readonly origin: AssetOrigin;
  readonly source: SourceIdentity;
  readonly createdAt: number;
}

export type JobState =
  | Readonly<{ readonly _tag: "Queued" }>
  | Readonly<{
      readonly _tag: "Submitting";
      readonly submissionIntentId: IntentId;
    }>
  | Readonly<{
      readonly _tag: "ReconciliationRequired";
      readonly submissionIntentId: IntentId;
      readonly reason: string;
    }>
  | Readonly<{
      readonly _tag: "Running";
      readonly providerReference: string;
    }>
  | Readonly<{
      readonly _tag: "Completed";
      readonly providerReference: string;
    }>
  | Readonly<{
      readonly _tag: "Failed";
      readonly reason: string;
    }>;

export interface JobRecord {
  readonly tenantId: TenantId;
  readonly jobId: JobId;
  readonly projectId: ProjectId;
  readonly revision: number;
  readonly intentId: IntentId;
  readonly requestFingerprint: Sha256;
  readonly state: JobState;
  readonly createdAt: number;
}

export type AttemptState =
  | Readonly<{ readonly _tag: "Prepared" }>
  | Readonly<{ readonly _tag: "Submitted"; readonly providerReference: string }>
  | Readonly<{ readonly _tag: "Unknown"; readonly reason: string }>
  | Readonly<{ readonly _tag: "Rejected"; readonly reason: string }>;

export interface AttemptRecord {
  readonly tenantId: TenantId;
  readonly attemptId: AttemptId;
  readonly jobId: JobId;
  readonly submissionIntentId: IntentId;
  readonly state: AttemptState;
  readonly createdAt: number;
}

export type ReviewDisposition = "Pending" | "Accepted" | "Rejected";

export interface ReviewRecord {
  readonly tenantId: TenantId;
  readonly reviewId: ReviewId;
  readonly projectId: ProjectId;
  readonly revision: number;
  readonly plan: Sha256;
  readonly output: Sha256;
  readonly renderer: Sha256;
  readonly disposition: ReviewDisposition;
  readonly createdAt: number;
}

export interface BudgetRecord {
  readonly tenantId: TenantId;
  readonly budgetId: BudgetId;
  readonly projectId: ProjectId;
  readonly limitUnits: number;
  readonly reservedUnits: number;
  readonly spentUnits: number;
  readonly updatedAt: number;
}

export type WorkerClaimState =
  | Readonly<{
      readonly _tag: "Active";
      readonly workerId: string;
      readonly fence: number;
      readonly leaseExpiresAt: number;
      readonly claimedAt: number;
    }>
  | Readonly<{
      readonly _tag: "Released";
      readonly workerId: string;
      readonly fence: number;
      readonly releasedAt: number;
    }>;

export interface WorkerClaimRecord {
  readonly tenantId: TenantId;
  readonly claimId: WorkerClaimId;
  readonly jobId: JobId;
  readonly state: WorkerClaimState;
}

export type SubmissionState =
  | Readonly<{ readonly _tag: "Prepared" }>
  | Readonly<{ readonly _tag: "Unknown"; readonly reason: string }>
  | Readonly<{ readonly _tag: "Confirmed"; readonly providerReference: string }>
  | Readonly<{ readonly _tag: "Rejected"; readonly reason: string }>;

export interface SubmissionIntentRecord {
  readonly tenantId: TenantId;
  readonly submissionIntentId: IntentId;
  readonly jobId: JobId;
  readonly attemptId: AttemptId;
  readonly provider: string;
  readonly requestFingerprint: Sha256;
  readonly state: SubmissionState;
  readonly createdAt: number;
  readonly updatedAt: number;
}

export type DeliveryState =
  | Readonly<{ readonly _tag: "Prepared" }>
  | Readonly<{ readonly _tag: "Published"; readonly providerReference: string }>
  | Readonly<{ readonly _tag: "Unknown"; readonly reason: string }>
  | Readonly<{ readonly _tag: "Failed"; readonly reason: string }>;

export interface DeliveryRecord {
  readonly tenantId: TenantId;
  readonly deliveryId: DeliveryId;
  readonly projectId: ProjectId;
  readonly revision: number;
  readonly assetId: AssetId;
  readonly state: DeliveryState;
  readonly createdAt: number;
  readonly updatedAt: number;
}

export interface TenantState {
  readonly tenantId: TenantId;
  readonly projects: ReadonlyArray<ProjectRecord>;
  readonly assets: ReadonlyArray<AssetRecord>;
  readonly jobs: ReadonlyArray<JobRecord>;
  readonly attempts: ReadonlyArray<AttemptRecord>;
  readonly reviews: ReadonlyArray<ReviewRecord>;
  readonly budgets: ReadonlyArray<BudgetRecord>;
  readonly workerClaims: ReadonlyArray<WorkerClaimRecord>;
  readonly submissionIntents: ReadonlyArray<SubmissionIntentRecord>;
  readonly deliveries: ReadonlyArray<DeliveryRecord>;
}

export interface CreateProjectRequest {
  readonly projectId: ProjectId;
  readonly source: SourceIdentity;
  readonly createIntentId: IntentId;
  readonly now: number;
}

/** Internal store representation after the trusted provisioner returns. */
export interface CreateProjectInput extends CreateProjectRequest {
  readonly native: NativeProjectBinding;
}

export interface CreateClientAssetInput {
  readonly assetId: AssetId;
  readonly projectId: ProjectId;
  readonly revision: number;
  readonly source: SourceIdentity;
  readonly declaredBy: ActorId;
  readonly now: number;
}

export interface CreateAssetInput {
  readonly assetId: AssetId;
  readonly projectId: ProjectId;
  readonly revision: number;
  readonly origin: AssetOrigin;
  readonly source: SourceIdentity;
  readonly now: number;
}

export interface CreateJobInput {
  readonly jobId: JobId;
  readonly projectId: ProjectId;
  readonly revision: number;
  readonly intentId: IntentId;
  readonly requestFingerprint: Sha256;
  readonly now: number;
}

export interface CreateReviewInput {
  readonly reviewId: ReviewId;
  readonly projectId: ProjectId;
  readonly revision: number;
  readonly plan: Sha256;
  readonly output: Sha256;
  readonly renderer: Sha256;
  readonly disposition: ReviewDisposition;
  readonly now: number;
}

export interface ReserveBudgetInput {
  readonly budgetId: BudgetId;
  readonly projectId: ProjectId;
  readonly limitUnits: number;
  readonly requestedUnits: number;
  readonly now: number;
}

export interface ClaimWorkerInput {
  readonly claimId: WorkerClaimId;
  readonly jobId: JobId;
  readonly workerId: string;
  readonly fence: number;
  readonly leaseExpiresAt: number;
  readonly now: number;
}

export interface ReleaseWorkerInput {
  readonly claimId: WorkerClaimId;
  readonly workerId: string;
  readonly fence: number;
  readonly releasedAt: number;
}

export interface CreateDeliveryInput {
  readonly deliveryId: DeliveryId;
  readonly projectId: ProjectId;
  readonly revision: number;
  readonly assetId: AssetId;
  readonly now: number;
}

export interface PrepareSubmissionInput {
  readonly submissionIntentId: IntentId;
  readonly attemptId: AttemptId;
  readonly jobId: JobId;
  readonly provider: string;
  readonly requestFingerprint: Sha256;
  readonly now: number;
}

export type PrepareSubmissionResult =
  | Readonly<{
      readonly _tag: "Created";
      readonly intent: SubmissionIntentRecord;
    }>
  | Readonly<{
      readonly _tag: "Existing";
      readonly intent: SubmissionIntentRecord;
    }>;

export type ProviderSubmissionResult =
  | Readonly<{ readonly _tag: "Confirmed"; readonly providerReference: string }>
  | Readonly<{ readonly _tag: "Rejected"; readonly reason: string }>
  | Readonly<{ readonly _tag: "Unknown"; readonly reason: string }>;

export type ProviderReconciliationResult =
  | Readonly<{ readonly _tag: "Confirmed"; readonly providerReference: string }>
  | Readonly<{ readonly _tag: "Rejected"; readonly reason: string }>
  | Readonly<{ readonly _tag: "StillUnknown"; readonly reason: string }>;

export interface ProviderBridge {
  readonly submit: (
    intent: SubmissionIntentRecord,
  ) => Effect.Effect<ProviderSubmissionResult, ProviderUnconfiguredError>;
  readonly reconcile: (
    intent: SubmissionIntentRecord,
  ) => Effect.Effect<ProviderReconciliationResult, ProviderUnconfiguredError>;
}

export interface NativeBridge {
  readonly verifyReceipt: (
    schemaVersion: NativeSchemaVersion,
    receipt: unknown,
  ) => Effect.Effect<NativeReceipt, NativeUnconfiguredError | NativeReceiptInvalidError>;
}

export const unconfiguredProvider: ProviderBridge = {
  submit: (intent) => Effect.fail({ _tag: "ProviderUnconfigured", provider: intent.provider }),
  reconcile: (intent) => Effect.fail({ _tag: "ProviderUnconfigured", provider: intent.provider }),
};

export const unconfiguredNative: NativeBridge = {
  verifyReceipt: (schemaVersion) =>
    Effect.fail({ _tag: "NativeUnconfigured", schemaVersion: schemaVersion.value }),
};

export const unconfiguredNativeProvisioner: NativeProjectProvisioner = {
  provision: () => Effect.fail({ _tag: "NativeProvisioningUnavailable" }),
};

export const fingerprintParts = (parts: ReadonlyArray<string | number>): string =>
  JSON.stringify(parts);

export const assertProjectRevision = (
  project: ProjectRecord,
  projectId: ProjectId,
  revision: number,
): Effect.Effect<void, TenantAccessDeniedError | StateConflictError> => {
  if (project.projectId.value !== projectId.value)
    return Effect.fail({ _tag: "TenantAccessDenied", projectId: projectId.value });
  if (project.revision !== revision)
    return Effect.fail({
      _tag: "StateConflict",
      record: "Project",
      detail: `Expected revision ${revision}, found ${project.revision}.`,
    });
  return Effect.succeed(undefined);
};
