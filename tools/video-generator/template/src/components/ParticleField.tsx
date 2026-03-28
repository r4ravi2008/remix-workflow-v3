import React, { useMemo } from 'react';
import { useCurrentFrame } from 'remotion';
import { generateParticlePositions, seededRandom } from '../utils/seededRandom';
import { splitFrequencyBands } from '../utils/audioUtils';
import type { DesignConfig } from '../utils/designLoader';

interface ParticleFieldProps {
  design: DesignConfig;
  frequencyData: number[];
  width?: number;
  height?: number;
}

export const ParticleField: React.FC<ParticleFieldProps> = ({
  design,
  frequencyData,
  width = 1920,
  height = 1080,
}) => {
  const frame = useCurrentFrame();
  const { bassAmplitude, highsAmplitude } = splitFrequencyBands(frequencyData);

  // Generate particle count based on seed and intensity
  const particleCount = useMemo(() => {
    const rng = seededRandom(design.seed);
    const baseCount = design.motif.intensity === 'high' ? 80 : design.motif.intensity === 'medium' ? 50 : 30;
    return Math.floor(baseCount + rng() * 30);
  }, [design.seed, design.motif.intensity]);

  // Generate particle positions and properties from seed
  const particles = useMemo(() => {
    const rng = seededRandom(design.seed);
    const positions = generateParticlePositions(design.seed, particleCount, width, height);
    
    return positions.map((pos, i) => ({
      ...pos,
      size: 2 + rng() * 6,
      speed: 0.2 + rng() * 0.5,
      opacity: 0.3 + rng() * 0.5,
    }));
  }, [design.seed, particleCount, width, height]);

  // Animate particles based on frame and audio
  const animatedParticles = useMemo(() => {
    return particles.map((particle, i) => {
      // Drift based on frame and speed
      const driftX = Math.cos(particle.angle) * particle.speed * (frame * 0.5);
      const driftY = Math.sin(particle.angle) * particle.speed * (frame * 0.5);
      
      // Wrap around screen
      let x = (particle.x + driftX) % width;
      let y = (particle.y + driftY) % height;
      if (x < 0) x += width;
      if (y < 0) y += height;

      // Pulse size and opacity to bass
      const pulse = 1 + bassAmplitude * 0.5;
      const size = particle.size * pulse;
      const opacity = particle.opacity * (0.5 + bassAmplitude * 0.5);

      // Add high-frequency jitter
      const jitter = highsAmplitude * 2;
      x += (Math.random() - 0.5) * jitter;
      y += (Math.random() - 0.5) * jitter;

      return { ...particle, x, y, size, opacity };
    });
  }, [particles, frame, bassAmplitude, highsAmplitude, width, height]);

  return (
    <svg
      width={width}
      height={height}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        pointerEvents: 'none',
      }}
    >
      {animatedParticles.map((particle, i) => (
        <circle
          key={i}
          cx={particle.x}
          cy={particle.y}
          r={particle.size}
          fill={design.palette.accentColor}
          opacity={particle.opacity}
        />
      ))}
    </svg>
  );
};
