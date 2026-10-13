import { Effect, Schema } from "effect";
import { JobRequest, type RouterError, fault, sha256 } from "./domain";
import { cancelJob, createJob } from "./engine";
import { Providers } from "./providers";
import { quotes } from "./routing";
import { JobStore } from "./store";

export const api = (request: Request) =>
  Effect.gen(function* () {
    const url = new URL(request.url);
    if (url.pathname === "/health" && request.method === "GET") {
      const providers = yield* Providers;
      return Response.json({
        service: "gpu-router",
        version: "0.1.0",
        simulation: providers.some((provider) => provider.mode === "simulation"),
        gpuExecution: providers.some((provider) => provider.mode === "live"),
        ready: providers.length > 0,
      });
    }
    const token = request.headers.get("Authorization")?.match(/^Bearer (\S+)$/)?.[1];
    if (token === undefined || token.length > 1024)
      return yield* Effect.fail(fault(401, "unauthorized", "A valid API key is required."));
    const store = yield* JobStore;
    const hash = yield* Effect.promise(() => sha256(token));
    const tenant = yield* store.principal(hash);
    if (tenant === null)
      return yield* Effect.fail(fault(401, "unauthorized", "A valid API key is required."));
    if (
      request.method === "POST" &&
      (url.pathname === "/v1/quotes" || url.pathname === "/v1/jobs")
    ) {
      const decoded = yield* Effect.tryPromise({
        try: async () => {
          if (!request.headers.get("Content-Type")?.startsWith("application/json"))
            throw new Error("JSON required");
          if (Number(request.headers.get("Content-Length")) > 1_048_576)
            throw new Error("Too large");
          const reader = request.body?.getReader();
          if (reader === undefined) throw new Error("JSON required");
          const decoder = new TextDecoder();
          let bytes = 0;
          let text = "";
          try {
            while (true) {
              const chunk = await reader.read();
              if (chunk.done) break;
              bytes += chunk.value.byteLength;
              if (bytes > 1_048_576) {
                await reader.cancel();
                throw new Error("Too large");
              }
              text += decoder.decode(chunk.value, { stream: true });
            }
            text += decoder.decode();
          } finally {
            reader.releaseLock();
          }
          return Schema.decodeUnknownSync(JobRequest)(JSON.parse(text));
        },
        catch: () =>
          fault(
            400,
            "invalid_request",
            "Submit a valid JSON job request of at most 1 MiB. Container images require a SHA-256 digest.",
          ),
      });
      if (url.pathname === "/v1/quotes")
        return Response.json({
          quotes: yield* quotes(decoded),
          costLimit: "estimate",
          currency: "USD",
          monetaryUnit: "microdollar",
        });
      const intent = request.headers.get("Idempotency-Key");
      if (intent === null || !/^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$/.test(intent))
        return yield* Effect.fail(
          fault(
            400,
            "idempotency_key_required",
            "Idempotency-Key must contain 1–128 letters, digits, dots, underscores, or hyphens.",
          ),
        );
      return Response.json(yield* createJob(tenant, intent, decoded), { status: 202 });
    }
    const match = url.pathname.match(/^\/v1\/jobs\/([a-f0-9-]{36})(\/cancel)?$/);
    const id = match?.[1];
    if (id !== undefined && request.method === "GET" && match?.[2] === undefined)
      return Response.json(yield* store.get(tenant, id));
    if (id !== undefined && request.method === "POST" && match?.[2] === "/cancel")
      return Response.json(yield* cancelJob(tenant, id), { status: 202 });
    return yield* Effect.fail(fault(404, "route_not_found", "Route not found."));
  }).pipe(
    Effect.catch((error: RouterError) =>
      Effect.succeed(
        Response.json(
          { error: { code: error.code, message: error.message } },
          { status: error.status },
        ),
      ),
    ),
    Effect.map((response) => {
      response.headers.set("Cache-Control", "no-store");
      response.headers.set("X-Content-Type-Options", "nosniff");
      return response;
    }),
  );
