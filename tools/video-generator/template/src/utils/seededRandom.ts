/**
 * Seeded random number generator
 * Generates deterministic pseudo-random sequences based on a seed
 */
export function seededRandom(seed: number): () => number {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) & 0xffffffff;
    return (s >>> 0) / 0xffffffff;
  };
}

/**
 * Generate an array of random values from a seed
 */
export function generateRandomValues(seed: number, count: number): number[] {
  const rng = seededRandom(seed);
  return Array.from({ length: count }, () => rng());
}

/**
 * Generate random positions for particles
 */
export function generateParticlePositions(
  seed: number,
  count: number,
  width: number,
  height: number
): Array<{ x: number; y: number; angle: number }> {
  const rng = seededRandom(seed);
  return Array.from({ length: count }, () => ({
    x: rng() * width,
    y: rng() * height,
    angle: rng() * Math.PI * 2,
  }));
}

/**
 * Generate random polygon configurations
 */
export function generatePolygons(
  seed: number,
  minCount: number,
  maxCount: number
): Array<{ sides: number; radius: number; rotation: number }> {
  const rng = seededRandom(seed);
  const count = Math.floor(rng() * (maxCount - minCount + 1)) + minCount;
  
  return Array.from({ length: count }, () => ({
    sides: [3, 4, 6, 8][Math.floor(rng() * 4)],
    radius: 50 + rng() * 200,
    rotation: rng() * Math.PI * 2,
  }));
}
