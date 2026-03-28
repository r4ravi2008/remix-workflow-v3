/**
 * Audio utilities for the music video visualizer.
 *
 * The visualizer pipeline:
 *   raw FFT (64 bins, 0–1 linear amplitude)
 *     → log-frequency binning (equal width per octave)
 *     → dB conversion (compresses 50× dynamic range into ~24 dB)
 *     → A-weighting gain (+2 dB/octave, boosts mids/highs)
 *     → range normalisation ([-60 dB, 0 dB] → [0, 1])
 *     → mirror for symmetry
 *     → per-bar attack/release smoothing (in MusicVideo.tsx)
 *     → spatial smoothing
 *
 * This is the standard approach used in professional audio visualizers.
 * It works regardless of genre because dB scale + A-weighting naturally
 * balance bass-heavy and treble-heavy content.
 */

// ─── Main visualizer bar computation ─────────────────────────────────────────

/**
 * Convert raw FFT amplitudes into visualizer bar heights.
 *
 * @param frequencyData  64 linear-amplitude samples (0–1) from visualizeAudio
 * @param numHalfBars    number of bars for ONE side (caller mirrors for symmetry)
 * @returns              array of numHalfBars values in [0, 1]
 */
export function computeVisualizerBars(
  frequencyData: number[],
  numBars: number,
): number[] {
  const n = frequencyData.length; // 64
  if (n === 0) return Array(numBars).fill(0);

  // ── Step 1: Log-frequency binning ──
  const raw: number[] = [];
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
    raw.push(count > 0 ? sum / count : 0);
  }

  // ── Step 2: Convert to dB ──
  // Raise the floor to -40 dB (vs -60) so quiet/noise content is suppressed
  // and the bars only move meaningfully when there's real audio energy.
  const DB_FLOOR = -40;
  const dB = raw.map(amp => {
    const clamped = Math.max(amp, 0.001);
    return 20 * Math.log10(clamped);
  });

  // ── Step 3: A-weighting gain ──
  // Moderate boost (+10 dB max) to balance bass vs. treble without over-amplifying.
  const aWeighted = dB.map((val, i) => {
    const octaveBoost = (i / Math.max(numBars - 1, 1)) * 10; // 0 → +10 dB
    return val + octaveBoost;
  });

  // ── Step 4: Normalise dB range → [0, 1] ──
  const DB_CEIL = 10;
  const normalised = aWeighted.map(val =>
    Math.max(0, Math.min(1, (val - DB_FLOOR) / (DB_CEIL - DB_FLOOR)))
  );

  // ── Step 5: Spatial smoothing (5-tap) ──
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
