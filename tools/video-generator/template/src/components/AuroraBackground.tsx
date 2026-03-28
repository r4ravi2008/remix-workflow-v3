import React, { useMemo } from 'react';
import { useCurrentFrame, interpolate } from 'remotion';
import { seededRandom } from '../utils/seededRandom';
import { splitFrequencyBands } from '../utils/audioUtils';
import type { DesignConfig } from '../utils/designLoader';

interface AuroraBackgroundProps {
  design: DesignConfig;
  frequencyData: number[];
  width?: number;
  height?: number;
}

export const AuroraBackground: React.FC<AuroraBackgroundProps> = ({
  design,
  frequencyData,
  width = 1920,
  height = 1080,
}) => {
  const frame = useCurrentFrame();
  const { bassAmplitude } = splitFrequencyBands(frequencyData);

  // Generate noise filter params from seed
  const noiseParams = useMemo(() => {
    const rng = seededRandom(design.seed);
    return {
      baseFrequencyX: 0.01 + rng() * 0.02,
      baseFrequencyY: 0.01 + rng() * 0.02,
      numOctaves: Math.floor(3 + rng() * 3),
      seed: Math.floor(rng() * 100),
    };
  }, [design.seed]);

  // Animate turbulence over time
  const turbulence = useMemo(() => {
    const baseFreq = noiseParams.baseFrequencyX;
    const animation = interpolate(
      frame % 300,
      [0, 150, 300],
      [0, 0.005, 0],
      { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
    );
    return `${baseFreq + animation} ${noiseParams.baseFrequencyY}`;
  }, [frame, noiseParams]);

  // Pulse opacity to bass
  const opacity = useMemo(() => {
    return 0.4 + bassAmplitude * 0.4;
  }, [bassAmplitude]);

  // Generate gradient stops
  const gradientStops = useMemo(() => {
    const stops = design.palette.backgroundStops;
    return stops.map((stop, i) => (
      <stop
        key={i}
        offset={stop.position}
        stopColor={stop.color}
      />
    ));
  }, [design.palette.backgroundStops]);

  return (
    <svg
      width={width}
      height={height}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        pointerEvents: 'none',
        mixBlendMode: 'screen',
        opacity,
      }}
    >
      <defs>
        <filter id="aurora-filter" x="0%" y="0%" width="100%" height="100%">
          <feTurbulence
            type="fractalNoise"
            baseFrequency={turbulence}
            numOctaves={noiseParams.numOctaves}
            seed={noiseParams.seed}
            result="noise"
          />
          <feDisplacementMap
            in="SourceGraphic"
            in2="noise"
            scale={30 + bassAmplitude * 50}
            xChannelSelector="R"
            yChannelSelector="G"
          />
        </filter>
        <linearGradient
          id="aurora-gradient"
          x1="0%"
          y1="0%"
          x2="100%"
          y2="100%"
        >
          {gradientStops}
        </linearGradient>
      </defs>
      
      <rect
        width={width}
        height={height}
        fill="url(#aurora-gradient)"
        filter="url(#aurora-filter)"
      />
    </svg>
  );
};
