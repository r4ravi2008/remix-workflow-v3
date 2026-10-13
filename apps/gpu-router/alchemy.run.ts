import * as Alchemy from "alchemy";
import * as Cloudflare from "alchemy/Cloudflare";
import { localState } from "alchemy/State";
import { Effect } from "effect";

export default Alchemy.Stack(
  "GpuRouter",
  {
    providers: Cloudflare.providers(),
    state: localState(),
  },
  Effect.gen(function* () {
    const jobs = yield* Cloudflare.D1.Database("Jobs", {
      name: "gpu-router-preview",
      migrations: "./migrations",
    });
    const api = yield* Cloudflare.Worker("Api", {
      name: "gpu-router-preview",
      main: "src/worker.ts",
      env: { JOBS: jobs },
      crons: ["* * * * *"],
    });
    return { apiUrl: api.url };
  }),
);
