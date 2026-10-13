import { Effect, Schema } from "effect";
import { JobRequest, JobSchema, sha256 } from "./domain";

const base = process.env.GPU_ROUTER_URL ?? "http://127.0.0.1:1341";
const token = process.env.GPU_ROUTER_DEV_TOKEN ?? "gpu-router-local-demo";
const saved = Bun.file(".state/http-smoke.json");
const previous = process.argv.includes("--replay")
  ? Schema.decodeUnknownSync(
      Schema.Struct({
        intent: Schema.String,
        jobId: Schema.String,
      }),
    )(await saved.json())
  : null;
const intent = previous?.intent ?? `smoke-${crypto.randomUUID()}`;
const request = Schema.decodeUnknownSync(JobRequest)(
  await Bun.file(new URL("../examples/container-job.json", import.meta.url)).json(),
);
const call = async (path: string, method = "GET", body?: JobRequest) => {
  const response = await fetch(`${base}${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      "Idempotency-Key": intent,
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  if (!response.ok) throw new Error(`${method} ${path} failed with ${response.status}`);
  return response.json();
};
const health = Schema.decodeUnknownSync(
  Schema.Struct({
    service: Schema.Literal("gpu-router"),
    simulation: Schema.Literal(true),
    gpuExecution: Schema.Literal(false),
  }),
)(await call("/health"));
let job = Schema.decodeUnknownSync(JobSchema)(await call("/v1/jobs", "POST", request));
if (previous !== null && previous.jobId !== job.id)
  throw new Error("Restart replay created a different job.");
const duplicate = Schema.decodeUnknownSync(JobSchema)(await call("/v1/jobs", "POST", request));
if (duplicate.id !== job.id) throw new Error("Duplicate submission created a different job.");
for (let tries = 0; tries < 30 && job.state._tag !== "Finished"; tries++) {
  await Effect.runPromise(Effect.sleep("500 millis"));
  job = Schema.decodeUnknownSync(JobSchema)(await call(`/v1/jobs/${job.id}`));
}
if (job.state._tag !== "Finished" || job.state.result._tag !== "Succeeded")
  throw new Error("Simulation did not finish successfully.");
const artifact = job.state.result.artifacts[0];
const receipt = job.attempts[0];
if (artifact === undefined || receipt?._tag !== "Accepted" || receipt.releasedAt === null)
  throw new Error("Artifact or cleanup receipt missing.");
const encoded = artifact.uri.split(",")[1];
if (encoded === undefined) throw new Error("Simulation artifact is invalid.");
const content = atob(encoded);
if (!content.includes("No container, workflow, or GPU was executed."))
  throw new Error("Simulation disclosure is missing.");
if (
  (await sha256(content)) !== artifact.sha256 ||
  new TextEncoder().encode(content).length !== artifact.bytes
)
  throw new Error("Artifact digest or byte count does not match.");
const proof = {
  checkedAt: new Date().toISOString(),
  scope: "local HTTP simulation",
  health,
  intent,
  jobId: job.id,
  duplicateReusedJob: true,
  replayAfterRestart: previous !== null,
  provider: receipt.attempt.quote.providerId,
  cleanupConfirmedAt: receipt.releasedAt,
  artifactSha256: artifact.sha256,
  artifactBytes: artifact.bytes,
  realGpuExecution: false,
  cloudDeployment: false,
};
await Bun.write(saved, `${JSON.stringify(proof, null, 2)}\n`);
console.log(JSON.stringify(proof, null, 2));
