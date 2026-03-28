import React, { useMemo } from 'react';
import { useCurrentFrame, interpolate } from 'remotion';
import { generatePolygons, seededRandom } from '../utils/seededRandom';
import { splitFrequencyBands } from '../utils/audioUtils';
import type { DesignConfig } from '../utils/designLoader';

interface GeometricBurstProps {
  design: DesignConfig;
  frequencyData: number[];
  width?: number;
  height?: number;
}

export const GeometricBurst: React.FC<GeometricBurstProps> = ({
  design,
  frequencyData,
  width = 1920,
  height = 1080,
}) => {
  const frame = useCurrentFrame();
  const { bassAmplitude, highMidAmplitude } = splitFrequencyBands(frequencyData);

  // Generate polygons from seed
  const polygons = useMemo(() => {
    const count = design.motif.intensity === 'high' ? 7 : design.motif.intensity === 'medium' ? 5 : 3;
    return generatePolygons(design.seed, count, count);
  }, [design.seed, design.motif.intensity]);

  // Calculate rotation based on audio and frame
  const rotation = useMemo(() => {
    return frame * (0.2 + highMidAmplitude * 2);
  }, [frame, highMidAmplitude]);

  // Scale based on bass
  const scale = useMemo(() => {
    return 1 + bassAmplitude * 0.3;
  }, [bassAmplitude]);

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
      {polygons.map((polygon, i) => {
        const points = generatePolygonPoints(
          centerX,
          centerY,
          polygon.sides,
          polygon.radius * scale * (1 + i * 0.3),
          polygon.rotation + rotation * (i % 2 === 0 ? 1 : -1)
        );

        return (
          <polygon
            key={i}
            points={points}
            fill="none"
            stroke={design.palette.accentColor}
            strokeWidth={2 + bassAmplitude * 3}
            opacity={0.6 - i * 0.1}
          />
        );
      })}
      
      {/* Central pulse ring */}
      <circle
        cx={centerX}
        cy={centerY}
        r={50 + bassAmplitude * 100}
        fill="none"
        stroke={design.palette.highlightColor}
        strokeWidth={3}
        opacity={0.5 + bassAmplitude * 0.5}
      />
    </svg>
  );
};

/**
 * Generate points for a regular polygon
 */
function generatePolygonPoints(
  cx: number,
  cy: number,
  sides: number,
  radius: number,
  rotation: number
): string {
  const points: string[] = [];
  for (let i = 0; i < sides; i++) {
    const angle = (i / sides) * Math.PI * 2 + rotation;
    const x = cx + Math.cos(angle) * radius;
    const y = cy + Math.sin(angle) * radius;
    points.push(`${x},${y}`);
  }
  return points.join(' ');
}
