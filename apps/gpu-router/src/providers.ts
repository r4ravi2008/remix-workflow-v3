import { Context, Effect } from "effect";
import type { Artifact, Attempt, JobRequest, Offer, RouterError } from "./domain";

export type Submission =
  | { readonly _tag: "Accepted"; readonly reference: string }
  | { readonly _tag: "Rejected"; readonly reason: string }
  | { readonly _tag: "Unknown"; readonly reason: string };
export type Reconciliation =
  | { readonly _tag: "Found"; readonly reference: string }
  | { readonly _tag: "Absent" }
  | { readonly _tag: "Unknown" };
export type Progress =
  | { readonly _tag: "Running" }
  | { readonly _tag: "Succeeded"; readonly artifacts: ReadonlyArray<Artifact> }
  | { readonly _tag: "Failed"; readonly reason: string };

export interface Provider {
  readonly id: string;
  readonly mode: "simulation" | "live";
  readonly offers: (request: JobRequest) => Effect.Effect<ReadonlyArray<Offer>, RouterError>;
  readonly submit: (
    request: JobRequest,
    attempt: Attempt,
  ) => Effect.Effect<Submission, RouterError>;
  readonly reconcile: (attempt: Attempt) => Effect.Effect<Reconciliation, RouterError>;
  readonly poll: (reference: string) => Effect.Effect<Progress, RouterError>;
  readonly release: (reference: string) => Effect.Effect<boolean, RouterError>;
}
export class Providers extends Context.Service<Providers, ReadonlyArray<Provider>>()(
  "gpu-router/Providers",
) {}
