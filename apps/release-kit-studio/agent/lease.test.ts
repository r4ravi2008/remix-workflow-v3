// @vitest-environment node
import { Effect } from 'effect'
import { describe, expect, it } from 'vitest'

import { withLease } from './lease'

describe('continuous job ownership', () => {
  it('renews throughout a long operation and stops renewing when it finishes', async () => {
    const renewals: Array<number> = []
    const handle = { complete: () => {} }
    const completed = new Promise<string>(resolve => {
      handle.complete = () => resolve('finished')
    })
    const operation = Effect.tryPromise(() => completed)
    const renew = Effect.sync(() => {
      renewals.push(renewals.length + 1)
      if (renewals.length === 2) handle.complete()
    })
    expect(await Effect.runPromise(withLease(operation, renew, 5))).toBe(
      'finished',
    )
    await new Promise(resolve => setTimeout(resolve, 20))
    expect(renewals).toEqual([1, 2])
  })

  it('interrupts the active transfer and prevents publication when renewal is fenced out', async () => {
    const state: { signal: AbortSignal | null; published: boolean } = {
      signal: null,
      published: false,
    }
    const operation = Effect.tryPromise({
      try: signal => {
        state.signal = signal
        return new Promise<void>((_resolve, reject) =>
          signal.addEventListener('abort', () => reject(new Error('aborted')), {
            once: true,
          }),
        )
      },
      catch: error => error,
    }).pipe(
      Effect.flatMap(() =>
        Effect.sync(() => {
          state.published = true
        }),
      ),
    )
    await expect(
      Effect.runPromise(
        withLease(operation, Effect.fail(new Error('stale lease')), 5),
      ),
    ).rejects.toThrow('stale lease')
    expect(state.signal?.aborted).toBe(true)
    expect(state.published).toBe(false)
  })
})
