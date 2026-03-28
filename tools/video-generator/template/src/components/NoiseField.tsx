import React, { useMemo } from 'react';
import { useCurrentFrame } from 'remotion';
import { seededRandom } from '../utils/seededRandom';
import { splitFrequencyBands } from '../utils/audioUtils';
import type { DesignConfig } from '../utils/designLoader';

interface NoiseFieldProps {
  design: DesignConfig;
  frequencyData: number[];
  width?: number;
  height?: number;
}

export const NoiseField: React.FC<NoiseFieldProps> = ({
  design,
  frequencyData,
  width = 1920,
  height = 1080,
}) => {
  const frame = useCurrentFrame();
  const { bassAmplitude } = splitFrequencyBands(frequencyData);

  // Generate noise texture offset from seed and frame
  const noiseOffset = useMemo(() => {
    const rng = seededRandom(design.seed);
    const speed = 0.5 + rng() * 0.5;
    const x = (frame * speed) % 100;
    const y = (frame * speed * 0.7) % 100;
    return { x, y };
  }, [frame, design.seed]);

  // Opacity based on intensity and bass
  const opacity = useMemo(() => {
    const baseOpacity = design.motif.intensity === 'high' ? 0.15 : 
                       design.motif.intensity === 'medium' ? 0.1 : 0.05;
    return baseOpacity + bassAmplitude * 0.1;
  }, [design.motif.intensity, bassAmplitude]);

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width,
        height,
        pointerEvents: 'none',
        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        backgroundPosition: `${noiseOffset.x}% ${noiseOffset.y}%`,
        backgroundSize: '200px 200px',
        opacity,
        mixBlendMode: 'overlay',
      }}
    />
  );
};
