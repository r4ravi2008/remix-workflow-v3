import React, { useMemo, useRef, useEffect } from 'react';
import { useCurrentFrame, interpolate } from 'remotion';
import { seededRandom } from '../utils/seededRandom';
import { splitFrequencyBands, detectBeat } from '../utils/audioUtils';
import type { DesignConfig } from '../utils/designLoader';

interface WaveformRingsProps {
  design: DesignConfig;
  frequencyData: number[];
  width?: number;
  height?: number;
}

interface Ring {
  id: number;
  radius: number;
  opacity: number;
  birthFrame: number;
}

export const WaveformRings: React.FC<WaveformRingsProps> = ({
  design,
  frequencyData,
  width = 1920,
  height = 1080,
}) => {
  const frame = useCurrentFrame();
  const { bassAmplitude } = splitFrequencyBands(frequencyData);
  const prevBeatRef = useRef(false);
  const ringsRef = useRef<Ring[]>([]);
  const ringIdRef = useRef(0);

  // Detect beat and spawn rings
  useEffect(() => {
    const isBeat = detectBeat(bassAmplitude, 0.5);
    const wasBeat = prevBeatRef.current;
    
    // Spawn new ring on beat onset
    if (isBeat && !wasBeat) {
      ringsRef.current.push({
        id: ringIdRef.current++,
        radius: 50,
        opacity: 1,
        birthFrame: frame,
      });
    }
    
    prevBeatRef.current = isBeat;
  }, [frame, bassAmplitude]);

  // Update existing rings
  const rings = useMemo(() => {
    // Filter out old rings
    ringsRef.current = ringsRef.current.filter(
      ring => frame - ring.birthFrame < 120 // Keep for 4 seconds at 30fps
    );

    // Update ring properties
    return ringsRef.current.map(ring => {
      const age = frame - ring.birthFrame;
      const maxRadius = Math.max(width, height) * 0.8;
      
      return {
        ...ring,
        radius: interpolate(age, [0, 120], [50, maxRadius], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        }),
        opacity: interpolate(age, [0, 60, 120], [1, 0.5, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        }),
      };
    });
  }, [frame, width, height]);

  const centerX = width / 2;
  const centerY = height / 2;

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
      {rings.map((ring) => (
        <circle
          key={ring.id}
          cx={centerX}
          cy={centerY}
          r={ring.radius}
          fill="none"
          stroke={design.palette.accentColor}
          strokeWidth={2 + bassAmplitude * 2}
          opacity={ring.opacity}
        />
      ))}
      
      {/* Central glow that pulses with bass */}
      <circle
        cx={centerX}
        cy={centerY}
        r={30 + bassAmplitude * 40}
        fill={design.palette.glowColor}
        opacity={0.3 + bassAmplitude * 0.4}
      />
    </svg>
  );
};
