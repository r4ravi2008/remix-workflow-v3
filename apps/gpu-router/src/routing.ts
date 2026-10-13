import { Effect } from "effect";
import { type JobRequest, type Offer, type Quote, fault } from "./domain";
import { Providers } from "./providers";

export const rank = (
  request: JobRequest,
  offers: ReadonlyArray<Offer>,
  now: number,
): ReadonlyArray<Quote> => {
  const budgetMicros = Math.floor(request.limits.maxCostUsd * 1_000_000);
  return offers
    .filter(
      (offer) =>
        offer.expiresAt > now &&
        offer.workloads.includes(request.workload.kind) &&
        offer.gpuCount === request.gpu.count &&
        offer.vramGbPerGpu >= request.gpu.minVramGb &&
        (request.routing.regions.length === 0 || request.routing.regions.includes(offer.region)) &&
        (request.routing.providers.length === 0 ||
          request.routing.providers.includes(offer.providerId)) &&
        (request.routing.allowInterruptible || !offer.interruptible) &&
        [offer.microsPerSecond, offer.fixedCostMicros, offer.startupSeconds].every(
          (n) => Number.isSafeInteger(n) && n >= 0,
        ),
    )
    .map((offer) => ({
      ...offer,
      estimatedMaxCostMicros:
        offer.fixedCostMicros +
        offer.microsPerSecond * (request.limits.maxRuntimeSeconds + offer.startupSeconds),
    }))
    .filter(
      (quote) =>
        Number.isSafeInteger(quote.estimatedMaxCostMicros) &&
        quote.estimatedMaxCostMicros <= budgetMicros,
    )
    .sort(
      (a, b) =>
        (request.routing.strategy === "fastest_start"
          ? a.startupSeconds - b.startupSeconds
          : a.estimatedMaxCostMicros - b.estimatedMaxCostMicros) ||
        a.estimatedMaxCostMicros - b.estimatedMaxCostMicros ||
        a.id.localeCompare(b.id),
    );
};

export const quotes = (request: JobRequest, excluded: ReadonlyArray<string> = []) =>
  Effect.gen(function* () {
    const providers = yield* Providers;
    const eligible = providers.filter(
      (provider) =>
        !excluded.includes(provider.id) &&
        (request.routing.providers.length === 0 || request.routing.providers.includes(provider.id)),
    );
    const inventories = yield* Effect.forEach(
      eligible,
      (provider) =>
        provider.offers(request).pipe(
          Effect.map((offers) =>
            offers.filter(
              (offer) => offer.providerId === provider.id && offer.mode === provider.mode,
            ),
          ),
          Effect.catch(() => Effect.succeed([])),
        ),
      { concurrency: 4 },
    );
    const ranked = rank(request, inventories.flat(), Date.now());
    if (ranked.length === 0)
      return yield* Effect.fail(
        fault(
          503,
          "no_capacity",
          "No eligible provider meets this workload, region, and estimated cost limit.",
        ),
      );
    return ranked;
  });
