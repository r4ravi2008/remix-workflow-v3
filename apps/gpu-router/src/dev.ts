import { Database } from "bun:sqlite";
import { mkdir } from "node:fs/promises";
import { Effect, Layer } from "effect";
import { api } from "./api";
import { sha256 } from "./domain";
import { tick } from "./engine";
import { Providers } from "./providers";
import { simulationMigration, simulationProvider } from "./simulation";
import { sqliteSql } from "./sqlite";
import { JobStore, sqlStore } from "./store";

await mkdir(".state", { recursive: true });
const db = new Database(".state/router.sqlite", { create: true });
db.exec("PRAGMA journal_mode=WAL;");
db.exec(await Bun.file(new URL("../migrations/0001_jobs.sql", import.meta.url)).text());
db.exec(simulationMigration);
const token = process.env.GPU_ROUTER_DEV_TOKEN ?? "gpu-router-local-demo";
db.query("INSERT OR IGNORE INTO api_keys(token_hash,tenant_id) VALUES(?,?)").run(
  await sha256(token),
  "local-demo",
);
const sql = sqliteSql(db);
const services = Layer.merge(
  Layer.succeed(JobStore, sqlStore(sql)),
  Layer.succeed(Providers, [
    simulationProvider(sql, "simulated-a", 200, 5),
    simulationProvider(sql, "simulated-b", 400, 1),
  ]),
);
const server = Bun.serve({
  hostname: "127.0.0.1",
  port: Number(process.env.GPU_ROUTER_PORT ?? 1341),
  maxRequestBodySize: 1_048_576,
  fetch: (request) => Effect.runPromise(api(request).pipe(Effect.provide(services))),
});
let processing = false;
const timer = setInterval(() => {
  if (processing) return;
  processing = true;
  void Effect.runPromise(
    tick().pipe(
      Effect.provide(services),
      Effect.catch((error) => Effect.logError({ code: error.code })),
    ),
  ).finally(() => {
    processing = false;
  });
}, 500);
console.log(`GPU router local simulation: ${server.url}`);
console.log("Simulated prices and outputs only. No GPU or provider account is connected.");
const stop = () => {
  clearInterval(timer);
  server.stop(true);
  db.close();
  process.exit(0);
};
process.on("SIGINT", stop);
process.on("SIGTERM", stop);
