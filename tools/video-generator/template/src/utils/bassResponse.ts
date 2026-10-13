import type {DesignConfig} from './designLoader';
import {splitFrequencyBands} from './audioUtils';

const clamp01 = (value: number) => Math.max(0, Math.min(1, value));

// Quintic ease-in/ease-out. The first derivative reaches zero at both ends,
// preventing the visual snap that a hard threshold or linear clamp creates.
const smootherstep = (edge0: number, edge1: number, value: number) => {
  const amount = clamp01((value - edge0) / Math.max(0.0001, edge1 - edge0));
  return amount * amount * amount * (amount * (amount * 6 - 15) + 10);
};

export type BassResponse = {
  amplitude: number;
  level: number;
  kick: number;
};

export const getBassResponse = (
  design: DesignConfig,
  frequencyData: number[],
): BassResponse => {
  const amplitude = clamp01(splitFrequencyBands(frequencyData).bassAmplitude);
  const floor = design.motif.bassResponse?.floor ?? 0.025;
  const kickStart = design.motif.bassResponse?.kick ?? 0.055;
  const peak = design.motif.bassResponse?.peak ?? 0.13;

  return {
    amplitude,
    level: smootherstep(floor, peak, amplitude),
    kick: smootherstep(kickStart, peak, amplitude),
  };
};
