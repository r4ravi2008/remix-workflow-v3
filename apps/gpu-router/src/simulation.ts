import { Effect, Schema } from "effect";
import { fault, sha256 } from "./domain";
import type { Provider } from "./providers";
import type { Sql } from "./store";

export const simulationMigration = `CREATE TABLE IF NOT EXISTS simulation_resources (
  token TEXT PRIMARY KEY, provider_id TEXT NOT NULL, reference TEXT NOT NULL UNIQUE,
  released INTEGER NOT NULL DEFAULT 0
);`;
const Resource = Schema.Struct({ reference: Schema.String, released: Schema.Number });
const decodeResource = (value: unknown) =>
  Effect.try({
    try: () => (value === null ? null : Schema.decodeUnknownSync(Resource)(value)),
    catch: () => fault(500, "simulation_record_invalid", "Simulation record could not be decoded."),
  });
export const simulationProvider = (
  sql: Sql,
  id: string,
  microsPerSecond: number,
  startupSeconds: number,
): Provider => ({
  id,
  mode: "simulation",
  offers: (request) =>
    Effect.succeed([
      {
        id: `${id}-24gb`,
        providerId: id,
        mode: "simulation",
        workloads: ["container", "comfyui"],
        gpuCount: request.gpu.count,
        vramGbPerGpu: 24,
        region: "us",
        interruptible: false,
        microsPerSecond: microsPerSecond * request.gpu.count,
        fixedCostMicros: 1000,
        startupSeconds,
        expiresAt: Date.now() + 60000,
      },
    ]),
  submit: (_request, attempt) =>
    Effect.gen(function* () {
      const reference = `simulation-${attempt.token}`;
      yield* sql.run(
        "INSERT OR IGNORE INTO simulation_resources(token,provider_id,reference) VALUES(?,?,?)",
        [attempt.token, id, reference],
      );
      return { _tag: "Accepted" as const, reference };
    }),
  reconcile: (attempt) =>
    Effect.gen(function* () {
      const row = yield* sql
        .first(
          "SELECT reference,released FROM simulation_resources WHERE token=? AND provider_id=?",
          [attempt.token, id],
        )
        .pipe(Effect.flatMap(decodeResource));
      return row === null
        ? { _tag: "Absent" as const }
        : { _tag: "Found" as const, reference: row.reference };
    }),
  poll: (reference) =>
    Effect.gen(function* () {
      const row = yield* sql
        .first(
          "SELECT reference,released FROM simulation_resources WHERE reference=? AND provider_id=?",
          [reference, id],
        )
        .pipe(Effect.flatMap(decodeResource));
      if (row === null || row.released === 1)
        return {
          _tag: "Failed" as const,
          reason: "The simulated resource is missing or released.",
        };
      const content = "GPU router simulation. No container, workflow, or GPU was executed.\n";
      const digest = yield* Effect.promise(() => sha256(content));
      return {
        _tag: "Succeeded" as const,
        artifacts: [
          {
            uri: `data:text/plain;base64,${btoa(content)}`,
            sha256: digest,
            bytes: new TextEncoder().encode(content).length,
          },
        ],
      };
    }),
  release: (reference) =>
    Effect.gen(function* () {
      yield* sql.run(
        "UPDATE simulation_resources SET released=1 WHERE reference=? AND provider_id=?",
        [reference, id],
      );
      const row = yield* sql
        .first(
          "SELECT reference,released FROM simulation_resources WHERE reference=? AND provider_id=?",
          [reference, id],
        )
        .pipe(Effect.flatMap(decodeResource));
      return row === null || row.released === 1;
    }),
});
