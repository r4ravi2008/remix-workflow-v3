import { Effect, Layer } from "effect";
import { api } from "./api";
import { d1Sql } from "./d1";
import { tick } from "./engine";
import { Providers } from "./providers";
import { JobStore, sqlStore } from "./store";

interface Env {
  readonly JOBS: D1Database;
}
const services = (env: Env) =>
  Layer.merge(Layer.succeed(JobStore, sqlStore(d1Sql(env.JOBS))), Layer.succeed(Providers, []));
export default {
  fetch: (request: Request, env: Env) =>
    Effect.runPromise(api(request).pipe(Effect.provide(services(env)))),
  scheduled: (_event: ScheduledController, env: Env, context: ExecutionContext) => {
    context.waitUntil(Effect.runPromise(tick().pipe(Effect.provide(services(env)))));
  },
};
