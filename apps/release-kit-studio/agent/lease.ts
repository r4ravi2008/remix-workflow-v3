import { Effect } from 'effect'

export const withLease = <A, E, R, E2, R2>(
  operation: Effect.Effect<A, E, R>,
  renew: Effect.Effect<void, E2, R2>,
  intervalMilliseconds = 45000,
) =>
  Effect.raceFirst(
    operation,
    Effect.sleep(intervalMilliseconds).pipe(
      Effect.flatMap(() => renew.pipe(Effect.timeout('20 seconds'))),
      Effect.forever,
    ),
  )
