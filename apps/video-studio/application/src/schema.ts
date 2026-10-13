import { Schema } from "effect";

const Identifier = Schema.String.check(Schema.isPattern(/^[a-z0-9][a-z0-9_-]{0,63}$/));
const Hash = Schema.String.check(Schema.isPattern(/^[a-f0-9]{64}$/));
const PositiveInt = Schema.Int.check(Schema.isBetween({ minimum: 1, maximum: 2 ** 53 - 1 }));
const NonNegativeInt = Schema.Int.check(Schema.isBetween({ minimum: 0, maximum: 2 ** 53 - 1 }));
const Text = Schema.String.check(Schema.isBetweenLength(0, 4096));
const WorkerId = Schema.String.check(Schema.isPattern(/^[a-z0-9][a-z0-9_-]{0,63}$/));

const SourceIdentity = Schema.Struct({
  sha256: Hash,
  bytes: PositiveInt,
});

const NativeReceipt = Schema.Struct({
  receiptId: Identifier,
  schemaVersion: Identifier,
  nativeProjectId: Identifier,
  projectId: Identifier,
  revision: NonNegativeInt,
  source: SourceIdentity,
  timeline: Identifier,
});

const NativeOutputOrigin = Schema.Struct({
  _tag: Schema.Literal("NativeOutput"),
  receipt: NativeReceipt,
});

const ClientImportOrigin = Schema.Struct({
  _tag: Schema.Literal("ClientImport"),
  declaredBy: Identifier,
});

const JobState = Schema.Union([
  Schema.Struct({ _tag: Schema.Literal("Queued") }),
  Schema.Struct({
    _tag: Schema.Literal("Submitting"),
    submissionIntentId: Identifier,
  }),
  Schema.Struct({
    _tag: Schema.Literal("ReconciliationRequired"),
    submissionIntentId: Identifier,
    reason: Text,
  }),
  Schema.Struct({
    _tag: Schema.Literal("Running"),
    providerReference: Text,
  }),
  Schema.Struct({
    _tag: Schema.Literal("Completed"),
    providerReference: Text,
  }),
  Schema.Struct({
    _tag: Schema.Literal("Failed"),
    reason: Text,
  }),
]);

const AttemptState = Schema.Union([
  Schema.Struct({ _tag: Schema.Literal("Prepared") }),
  Schema.Struct({
    _tag: Schema.Literal("Submitted"),
    providerReference: Text,
  }),
  Schema.Struct({ _tag: Schema.Literal("Unknown"), reason: Text }),
  Schema.Struct({ _tag: Schema.Literal("Rejected"), reason: Text }),
]);

const SubmissionState = Schema.Union([
  Schema.Struct({ _tag: Schema.Literal("Prepared") }),
  Schema.Struct({ _tag: Schema.Literal("Unknown"), reason: Text }),
  Schema.Struct({
    _tag: Schema.Literal("Confirmed"),
    providerReference: Text,
  }),
  Schema.Struct({ _tag: Schema.Literal("Rejected"), reason: Text }),
]);

const WorkerClaimState = Schema.Union([
  Schema.Struct({
    _tag: Schema.Literal("Active"),
    workerId: WorkerId,
    fence: NonNegativeInt,
    leaseExpiresAt: NonNegativeInt,
    claimedAt: NonNegativeInt,
  }),
  Schema.Struct({
    _tag: Schema.Literal("Released"),
    workerId: WorkerId,
    fence: NonNegativeInt,
    releasedAt: NonNegativeInt,
  }),
]);

const Project = Schema.Struct({
  tenantId: Identifier,
  projectId: Identifier,
  nativeProjectId: Identifier,
  nativeSchemaVersion: Identifier,
  revision: NonNegativeInt,
  source: SourceIdentity,
  createIntentId: Identifier,
  createdAt: NonNegativeInt,
});

const Asset = Schema.Struct({
  tenantId: Identifier,
  assetId: Identifier,
  projectId: Identifier,
  revision: NonNegativeInt,
  origin: Schema.Union([ClientImportOrigin, NativeOutputOrigin]),
  source: SourceIdentity,
  createdAt: NonNegativeInt,
});

const Job = Schema.Struct({
  tenantId: Identifier,
  jobId: Identifier,
  projectId: Identifier,
  revision: NonNegativeInt,
  intentId: Identifier,
  requestFingerprint: Hash,
  state: JobState,
  createdAt: NonNegativeInt,
});

const Attempt = Schema.Struct({
  tenantId: Identifier,
  attemptId: Identifier,
  jobId: Identifier,
  submissionIntentId: Identifier,
  state: AttemptState,
  createdAt: NonNegativeInt,
});

const Review = Schema.Struct({
  tenantId: Identifier,
  reviewId: Identifier,
  projectId: Identifier,
  revision: NonNegativeInt,
  plan: Hash,
  output: Hash,
  renderer: Hash,
  disposition: Schema.Literals(["Pending", "Accepted", "Rejected"]),
  createdAt: NonNegativeInt,
});

const Budget = Schema.Struct({
  tenantId: Identifier,
  budgetId: Identifier,
  projectId: Identifier,
  limitUnits: PositiveInt,
  reservedUnits: NonNegativeInt,
  spentUnits: NonNegativeInt,
  updatedAt: NonNegativeInt,
});

const WorkerClaim = Schema.Struct({
  tenantId: Identifier,
  claimId: Identifier,
  jobId: Identifier,
  state: WorkerClaimState,
});

const SubmissionIntent = Schema.Struct({
  tenantId: Identifier,
  submissionIntentId: Identifier,
  jobId: Identifier,
  attemptId: Identifier,
  provider: Identifier,
  requestFingerprint: Hash,
  state: SubmissionState,
  createdAt: NonNegativeInt,
  updatedAt: NonNegativeInt,
});

const DeliveryState = Schema.Union([
  Schema.Struct({ _tag: Schema.Literal("Prepared") }),
  Schema.Struct({ _tag: Schema.Literal("Published"), providerReference: Text }),
  Schema.Struct({ _tag: Schema.Literal("Unknown"), reason: Text }),
  Schema.Struct({ _tag: Schema.Literal("Failed"), reason: Text }),
]);

const Delivery = Schema.Struct({
  tenantId: Identifier,
  deliveryId: Identifier,
  projectId: Identifier,
  revision: NonNegativeInt,
  assetId: Identifier,
  state: DeliveryState,
  createdAt: NonNegativeInt,
  updatedAt: NonNegativeInt,
});

export const TenantStateSchema = Schema.Struct({
  schema: Schema.Literal(1),
  tenantId: Identifier,
  projects: Schema.Array(Project),
  assets: Schema.Array(Asset),
  jobs: Schema.Array(Job),
  attempts: Schema.Array(Attempt),
  reviews: Schema.Array(Review),
  budgets: Schema.Array(Budget),
  workerClaims: Schema.Array(WorkerClaim),
  submissionIntents: Schema.Array(SubmissionIntent),
  deliveries: Schema.Array(Delivery),
});

export type TenantStateWire = typeof TenantStateSchema.Type;
export type ProjectWire = TenantStateWire["projects"][number];
export type AssetWire = TenantStateWire["assets"][number];
export type JobWire = TenantStateWire["jobs"][number];
export type AttemptWire = TenantStateWire["attempts"][number];
export type ReviewWire = TenantStateWire["reviews"][number];
export type BudgetWire = TenantStateWire["budgets"][number];
export type WorkerClaimWire = TenantStateWire["workerClaims"][number];
export type SubmissionIntentWire = TenantStateWire["submissionIntents"][number];
export type DeliveryWire = TenantStateWire["deliveries"][number];
