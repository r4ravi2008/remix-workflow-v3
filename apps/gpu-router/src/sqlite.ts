import { Database } from "bun:sqlite";
import { Effect } from "effect";
import { fault } from "./domain";
import type { Sql } from "./store";

export const sqliteSql = (db: Database): Sql => ({
  first: (query, values) =>
    Effect.try({
      try: () => db.query(query).get(...values),
      catch: () => fault(500, "storage_error", "The database read failed."),
    }),
  all: (query, values) =>
    Effect.try({
      try: () => db.query(query).all(...values),
      catch: () => fault(500, "storage_error", "The database read failed."),
    }),
  run: (query, values) =>
    Effect.try({
      try: () => db.query(query).run(...values).changes,
      catch: () => fault(500, "storage_error", "The database write failed."),
    }),
});
