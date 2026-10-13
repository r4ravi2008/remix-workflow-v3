import { Effect } from "effect";
import { fault } from "./domain";
import type { Sql } from "./store";

export const d1Sql = (db: D1Database): Sql => ({
  first: (query, values) =>
    Effect.tryPromise({
      try: () =>
        db
          .prepare(query)
          .bind(...values)
          .first(),
      catch: () => fault(500, "storage_error", "The database read failed."),
    }),
  all: (query, values) =>
    Effect.tryPromise({
      try: async () =>
        (
          await db
            .prepare(query)
            .bind(...values)
            .all()
        ).results,
      catch: () => fault(500, "storage_error", "The database read failed."),
    }),
  run: (query, values) =>
    Effect.tryPromise({
      try: async () =>
        (
          await db
            .prepare(query)
            .bind(...values)
            .run()
        ).meta.changes,
      catch: () => fault(500, "storage_error", "The database write failed."),
    }),
});
