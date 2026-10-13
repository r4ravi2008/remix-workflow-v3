import { Schema } from "effect";

const identifier = Schema.String.check(Schema.isPattern(/^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$/));
const positiveInt = (max: number) =>
  Schema.Int.check(Schema.isBetween({ minimum: 1, maximum: max }));
const digest = Schema.String.check(Schema.isPattern(/^[a-f0-9]{64}$/));
const https = Schema.String.check(Schema.isPattern(/^https:\/\/[^\s]+$/));

export const Workload = Schema.Union([
  Schema.Struct({
    kind: Schema.Literal("container"),
    image: Schema.String.check(Schema.isPattern(/^[^\s]+@sha256:[a-f0-9]{64}$/)),
    command: Schema.Array(Schema.String).check(Schema.isMaxLength(64)),
    input: Schema.Unknown,
  }),
  Schema.Struct({
    kind: Schema.Literal("comfyui"),
    bundleUrl: https,
    bundleSha256: digest,
    input: Schema.Unknown,
  }),
]);
export const JobRequest = Schema.Struct({
  workload: Workload,
  gpu: Schema.Struct({ count: positiveInt(8), minVramGb: positiveInt(192) }),
  limits: Schema.Struct({
    maxQueueSeconds: positiveInt(86400),
    maxRuntimeSeconds: positiveInt(86400),
    maxCostUsd: Schema.Finite.check(Schema.isBetween({ minimum: 0.01, maximum: 10000 })),
  }),
  routing: Schema.Struct({
    strategy: Schema.Literals(["lowest_cost", "fastest_start"]),
    regions: Schema.Array(identifier).check(Schema.isMaxLength(32)),
    providers: Schema.Array(identifier).check(Schema.isMaxLength(32)),
    allowInterruptible: Schema.Boolean,
  }),
});
export type JobRequest = typeof JobRequest.Type;

export interface Offer {
  readonly id: string;
  readonly providerId: string;
  readonly mode: "simulation" | "live";
  readonly workloads: ReadonlyArray<JobRequest["workload"]["kind"]>;
  readonly gpuCount: number;
  readonly vramGbPerGpu: number;
  readonly region: string;
  readonly interruptible: boolean;
  readonly microsPerSecond: number;
  readonly fixedCostMicros: number;
  readonly startupSeconds: number;
  readonly expiresAt: number;
}
export interface Quote extends Offer {
  readonly estimatedMaxCostMicros: number;
}
export interface Attempt {
  readonly token: string;
  readonly quote: Quote;
  readonly startedAt: number;
}
export const Artifact = Schema.Struct({
  uri: Schema.String,
  sha256: digest,
  bytes: Schema.Int.check(Schema.isGreaterThan(0)),
});
export type Artifact = typeof Artifact.Type;
export type Result =
  | { readonly _tag: "Succeeded"; readonly artifacts: ReadonlyArray<Artifact> }
  | { readonly _tag: "Failed"; readonly reason: string }
  | { readonly _tag: "Cancelled" };
export type State =
  | { readonly _tag: "Queued" }
  | { readonly _tag: "Dispatching"; readonly attempt: Attempt; readonly leaseUntil: number }
  | { readonly _tag: "Uncertain"; readonly attempt: Attempt; readonly reason: string }
  | { readonly _tag: "Running"; readonly attempt: Attempt; readonly reference: string }
  | {
      readonly _tag: "CleanupPending";
      readonly attempt: Attempt;
      readonly reference: string;
      readonly result: Result;
    }
  | { readonly _tag: "Finished"; readonly result: Result };
export type AttemptRecord =
  | { readonly _tag: "Pending"; readonly attempt: Attempt }
  | { readonly _tag: "Rejected"; readonly attempt: Attempt; readonly reason: string }
  | { readonly _tag: "Absent"; readonly attempt: Attempt }
  | {
      readonly _tag: "Accepted";
      readonly attempt: Attempt;
      readonly reference: string;
      readonly releasedAt: number | null;
    };
export interface Job {
  readonly id: string;
  readonly tenantId: string;
  readonly intentId: string;
  readonly fingerprint: string;
  readonly request: JobRequest;
  readonly state: State;
  readonly rejectedProviders: ReadonlyArray<string>;
  readonly attempts: ReadonlyArray<AttemptRecord>;
  readonly cancelRequested: boolean;
  readonly version: number;
  readonly createdAt: number;
  readonly updatedAt: number;
}
const QuoteSchema = Schema.Struct({
  id: Schema.String,
  providerId: Schema.String,
  mode: Schema.Literals(["simulation", "live"]),
  workloads: Schema.Array(Schema.Literals(["container", "comfyui"])),
  gpuCount: Schema.Number,
  vramGbPerGpu: Schema.Number,
  region: Schema.String,
  interruptible: Schema.Boolean,
  microsPerSecond: Schema.Number,
  fixedCostMicros: Schema.Number,
  startupSeconds: Schema.Number,
  expiresAt: Schema.Number,
  estimatedMaxCostMicros: Schema.Number,
});
const AttemptSchema = Schema.Struct({
  token: Schema.String,
  quote: QuoteSchema,
  startedAt: Schema.Number,
});
const AttemptRecordSchema = Schema.Union([
  Schema.Struct({ _tag: Schema.Literal("Pending"), attempt: AttemptSchema }),
  Schema.Struct({
    _tag: Schema.Literal("Rejected"),
    attempt: AttemptSchema,
    reason: Schema.String,
  }),
  Schema.Struct({ _tag: Schema.Literal("Absent"), attempt: AttemptSchema }),
  Schema.Struct({
    _tag: Schema.Literal("Accepted"),
    attempt: AttemptSchema,
    reference: Schema.String,
    releasedAt: Schema.NullOr(Schema.Number),
  }),
]);
const ResultSchema = Schema.Union([
  Schema.Struct({
    _tag: Schema.Literal("Succeeded"),
    artifacts: Schema.Array(Artifact).check(Schema.isMinLength(1)),
  }),
  Schema.Struct({ _tag: Schema.Literal("Failed"), reason: Schema.String }),
  Schema.Struct({ _tag: Schema.Literal("Cancelled") }),
]);
const StateSchema = Schema.Union([
  Schema.Struct({ _tag: Schema.Literal("Queued") }),
  Schema.Struct({
    _tag: Schema.Literal("Dispatching"),
    attempt: AttemptSchema,
    leaseUntil: Schema.Number,
  }),
  Schema.Struct({
    _tag: Schema.Literal("Uncertain"),
    attempt: AttemptSchema,
    reason: Schema.String,
  }),
  Schema.Struct({
    _tag: Schema.Literal("Running"),
    attempt: AttemptSchema,
    reference: Schema.String,
  }),
  Schema.Struct({
    _tag: Schema.Literal("CleanupPending"),
    attempt: AttemptSchema,
    reference: Schema.String,
    result: ResultSchema,
  }),
  Schema.Struct({ _tag: Schema.Literal("Finished"), result: ResultSchema }),
]);
export const JobSchema = Schema.Struct({
  id: Schema.String,
  tenantId: Schema.String,
  intentId: Schema.String,
  fingerprint: Schema.String,
  request: JobRequest,
  state: StateSchema,
  rejectedProviders: Schema.Array(Schema.String),
  attempts: Schema.Array(AttemptRecordSchema),
  cancelRequested: Schema.Boolean,
  version: Schema.Int,
  createdAt: Schema.Number,
  updatedAt: Schema.Number,
});
export class RouterError extends Schema.TaggedError<RouterError>()("RouterError", {
  status: Schema.Number,
  code: Schema.String,
  message: Schema.String,
}) {}
export const fault = (status: number, code: string, message: string) =>
  new RouterError({ status, code, message });

export const canonicalJson = (value: unknown): string => {
  if (value === null || typeof value !== "object") return JSON.stringify(value) ?? "null";
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  return `{${Object.entries(value)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, item]) => `${JSON.stringify(key)}:${canonicalJson(item)}`)
    .join(",")}}`;
};
export const sha256 = async (value: string) =>
  Array.from(
    new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value))),
    (byte) => byte.toString(16).padStart(2, "0"),
  ).join("");
