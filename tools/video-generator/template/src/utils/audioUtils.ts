/**
 * Audio utilities for the music video visualizer.
 *
 * The visualizer pipeline:
 *   raw FFT (64 bins, 0–1 linear amplitude)
 *     → log-frequency binning (equal width per octave)
 *     → dB conversion
 *     → adaptive per-band normalization (running min/max envelope)
 *     → per-bar attack/release smoothing (in MusicVideo.tsx)
 *     → spatial smoothing
 *
 * Adaptive normalization means each frequency band auto-scales to its own
 * recent dynamic range, so mids/highs stay visible regardless of how much
 * quieter they are than bass, and bass gets full variance instead of sitting
 * at a fixed height.
 */

// ─── Band boundaries as fraction of numBars (0-1) ───────────────────────────

const BAND_BOUNDARIES = {
  bass: 0.17,
  lowMid: 0.42,
  highMid: 0.67,
};

function getBandIndex(barIndex: number, numBars: number): number {
  const frac = barIndex / numBars;
  if (frac < BAND_BOUNDARIES.bass) return 0;
  if (frac < BAND_BOUNDARIES.lowMid) return 1;
  if (frac < BAND_BOUNDARIES.highMid) return 2;
  return 3;
}

// ─── Adaptive envelope tracker ──────────────────────────────────────────────

// Per-band envelope: tracks running min/max dB over recent frames.
// Uses asymmetric smoothing — min/max expand quickly, contract slowly —
// so the normalization range adapts to the music without jittering.

export interface EnvelopeState {
  min: Float64Array; // per-bar running minimum dB
  max: Float64Array; // per-bar running maximum dB
  initialized: boolean;
}

export function createEnvelopeState(numBars: number): EnvelopeState {
  return {
    min: new Float64Array(numBars).fill(-40),
    max: new Float64Array(numBars).fill(-10),
    initialized: false,
  };
}

// How fast the envelope expands vs contracts, per band.
// Bass uses slower contraction for a more stable, grounded feel.
// Mids/highs contract faster so they stay responsive.
const BAND_ENVELOPE = [
  { expandAttack: 0.3, contractRelease: 0.992 }, // bass — slow contraction, stable base
  { expandAttack: 0.3, contractRelease: 0.985 }, // lowMid
  { expandAttack: 0.3, contractRelease: 0.982 }, // highMid
  { expandAttack: 0.3, contractRelease: 0.980 }, // highs — faster contraction, more responsive
];

// Minimum dB range per band so normalization doesn't blow up on near-silence
const MIN_RANGE_DB = [10, 8, 8, 6]; // bass needs wider minimum range

// ─── Main visualizer bar computation ─────────────────────────────────────────

/**
 * Convert raw FFT amplitudes into visualizer bar heights.
 * Uses adaptive per-band normalization — each bar tracks its own
 * recent dB range and normalizes against it.
 *
 * @param frequencyData  64 linear-amplitude samples (0–1) from visualizeAudio
 * @param numBars        number of bars for the visualizer
 * @param envelope       mutable envelope state (pass same object each frame)
 * @returns              array of numBars values in [0, 1]
 */
export function computeVisualizerBars(
  frequencyData: number[],
  numBars: number,
  envelope?: EnvelopeState,
): number[] {
  const n = frequencyData.length; // 64
  if (n === 0) return Array(numBars).fill(0);

  // ── Step 1: Log-frequency binning ──
  const rawAmps: number[] = [];
  for (let i = 0; i < numBars; i++) {
    const fracLo = i / numBars;
    const fracHi = (i + 1) / numBars;
    const binLo = Math.floor(Math.pow(n, fracLo));
    const binHi = Math.min(Math.ceil(Math.pow(n, fracHi)), n) - 1;

    let sum = 0;
    let count = 0;
    for (let b = Math.max(0, binLo); b <= binHi; b++) {
      sum += frequencyData[b] ?? 0;
      count++;
    }
    rawAmps.push(count > 0 ? sum / count : 0);
  }

  // ── Step 2: Convert to dB ──
  const dbValues: number[] = rawAmps.map(amp => {
    const clamped = Math.max(amp, 0.00001);
    return 20 * Math.log10(clamped);
  });

  // ── Step 3: Adaptive normalization ──
  const normalised: number[] = [];

  for (let i = 0; i < numBars; i++) {
    const dB = dbValues[i];
    const band = getBandIndex(i, numBars);

    if (envelope) {
      const { expandAttack, contractRelease } = BAND_ENVELOPE[band];
      const minRange = MIN_RANGE_DB[band];

      if (!envelope.initialized) {
        // Seed with current values
        envelope.min[i] = dB - minRange / 2;
        envelope.max[i] = dB + minRange / 2;
      } else {
        // Asymmetric envelope update:
        // If current dB is below tracked min → expand quickly (attack)
        // If current dB is above tracked min → contract slowly (release)
        if (dB < envelope.min[i]) {
          envelope.min[i] = envelope.min[i] * expandAttack + dB * (1 - expandAttack);
        } else {
          // Slowly pull min upward toward current
          envelope.min[i] = envelope.min[i] * contractRelease + dB * (1 - contractRelease);
        }

        // Same for max but inverted
        if (dB > envelope.max[i]) {
          envelope.max[i] = envelope.max[i] * expandAttack + dB * (1 - expandAttack);
        } else {
          envelope.max[i] = envelope.max[i] * contractRelease + dB * (1 - contractRelease);
        }
      }

      // Enforce minimum range
      const currentRange = envelope.max[i] - envelope.min[i];
      if (currentRange < minRange) {
        const mid = (envelope.max[i] + envelope.min[i]) / 2;
        envelope.min[i] = mid - minRange / 2;
        envelope.max[i] = mid + minRange / 2;
      }

      // Normalize against tracked range
      const range = envelope.max[i] - envelope.min[i];
      const norm = (dB - envelope.min[i]) / range;
      normalised.push(Math.max(0, Math.min(1, norm)));
    } else {
      // Fallback: simple fixed normalization (backwards compat)
      const norm = (dB + 40) / 40; // -40dB → 0, 0dB → 1
      normalised.push(Math.max(0, Math.min(1, norm)));
    }
  }

  if (envelope && !envelope.initialized) {
    envelope.initialized = true;
  }

  // ── Step 4: Spatial smoothing (5-tap) ──
  const smoothed: number[] = [];
  for (let i = 0; i < normalised.length; i++) {
    const b2 = normalised[i - 2] ?? normalised[i];
    const b1 = normalised[i - 1] ?? normalised[i];
    const b0 = normalised[i];
    const a1 = normalised[i + 1] ?? normalised[i];
    const a2 = normalised[i + 2] ?? normalised[i];
    smoothed.push(b2 * 0.06 + b1 * 0.24 + b0 * 0.40 + a1 * 0.24 + a2 * 0.06);
  }

  return smoothed;
}

// ─── Per-bar attack/release smoothing ────────────────────────────────────────

/**
 * Smooth an array of bar heights with asymmetric attack/release.
 *
 * - Attack (value rising):  fast coefficient → bars snap up to beats
 * - Release (value falling): slow coefficient → bars decay gracefully
 *
 * @param current   this frame's bar heights
 * @param previous  last frame's smoothed heights (null on first frame)
 * @param attack    rising coefficient (0 = instant, 1 = frozen). 0.25 = snappy.
 * @param release   falling coefficient.  0.96 = slow, elegant decay.
 */
export function attackReleaseSmooth(
  current: number[],
  previous: number[] | null,
  attack = 0.25,
  release = 0.96,
): number[] {
  if (!previous || previous.length !== current.length) return current;
  return current.map((val, i) => {
    const prev = previous[i] ?? 0;
    const coeff = val > prev ? attack : release;
    return prev * coeff + val * (1 - coeff);
  });
}

// ─── Band energies (used by motif components, background pulse) ──────────────

export interface BandEnergies {
  bass: number;
  lowMid: number;
  highMid: number;
  highs: number;
  overall: number;
}

export function extractBandEnergies(frequencyData: number[]): BandEnergies {
  const bass    = rms(frequencyData.slice(0, 4));
  const lowMid  = rms(frequencyData.slice(4, 16));
  const highMid = rms(frequencyData.slice(16, 32));
  const highs   = rms(frequencyData.slice(32, 64));
  const overall = rms(frequencyData);
  return { bass, lowMid, highMid, highs, overall };
}

function rms(arr: number[]): number {
  if (arr.length === 0) return 0;
  return Math.sqrt(arr.reduce((s, v) => s + v * v, 0) / arr.length);
}

// Legacy — kept for motif components
export function splitFrequencyBands(frequencyData: number[]) {
  const bass    = frequencyData.slice(0, 4);
  const lowMid  = frequencyData.slice(4, 16);
  const highMid = frequencyData.slice(16, 32);
  const highs   = frequencyData.slice(32, 64);
  const avg = (a: number[]) => a.length ? a.reduce((s, v) => s + v, 0) / a.length : 0;
  return {
    bass, lowMid, highMid, highs,
    bassAmplitude: avg(bass),
    lowMidAmplitude: avg(lowMid),
    highMidAmplitude: avg(highMid),
    highsAmplitude: avg(highs),
  };
}

export function detectBeat(bassAmplitude: number, threshold = 0.6): boolean {
  return bassAmplitude > threshold;
}

// Legacy stubs
export function smoothFrequencyData(c: number[], p: number[] | null, s = 0.8) {
  if (!p || p.length !== c.length) return c;
  return c.map((v, i) => v * (1 - s) + (p[i] ?? 0) * s);
}
export function getVisualizerBarHeights(freq: number[], n: number) {
  const half = computeVisualizerBars(freq, Math.ceil(n / 2));
  return [...[...half].reverse(), ...half].slice(0, n);
}
export function generateEnvelopeBars(bands: BandEnergies, n: number) {
  return Array(n).fill(0.5);
}
