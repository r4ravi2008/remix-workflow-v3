import { defineConfig } from "vitest/config";
import { fileURLToPath } from "node:url";

const applicationRoot = fileURLToPath(new URL(".", import.meta.url));

export default defineConfig({
  root: applicationRoot,
  test: {
    include: ["test/**/*.test.ts"],
    environment: "node",
    pool: "forks",
    fileParallelism: false,
  },
});
