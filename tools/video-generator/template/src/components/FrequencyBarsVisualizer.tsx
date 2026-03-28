import React, { useMemo } from 'react';
import type { DesignConfig } from '../utils/designLoader';

interface FrequencyBarsVisualizerProps {
  design: DesignConfig;
  barHeights: number[];   // pre-computed, pre-smoothed, already mirrored (0–1 each)
  width?: number;
  height?: number;
}

export const FrequencyBarsVisualizer: React.FC<FrequencyBarsVisualizerProps> = ({
  design,
  barHeights,
  width = 1400,
  height = 160,
}) => {
  const numBars = barHeights.length;

  // Mirrored colour gradient: accent → highlight → accent
  const colours = useMemo(
    () => buildMirroredGradient(
      design.palette.accentColor,
      design.palette.highlightColor,
      numBars,
    ),
    [design.palette.accentColor, design.palette.highlightColor, numBars],
  );

  const gap = 4;
  const barWidth = Math.max(4, (width - gap * (numBars - 1)) / numBars);

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      style={{ display: 'block', overflow: 'visible' }}
    >
      <defs>
        {/* Soft glow filter */}
        <filter id="viz-glow" x="-80%" y="-80%" width="260%" height="260%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur" />
          <feColorMatrix
            in="blur" type="matrix"
            values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0.55 0"
            result="dim"
          />
          <feMerge>
            <feMergeNode in="dim" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>

        {/* Per-bar vertical gradient: bright centre, fades at tips */}
        {colours.map((color, i) => (
          // y1=0 is top of bar, y2=1 is bottom — bright tip, fades to base
          <linearGradient key={i} id={`vg-${i}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor={color} stopOpacity="1" />
            <stop offset="60%"  stopColor={color} stopOpacity="0.7" />
            <stop offset="100%" stopColor={color} stopOpacity="0.2" />
          </linearGradient>
        ))}
      </defs>

      {barHeights.map((h, i) => {
        // Bars grow upward from a fixed base at the bottom.
        // Minimum is 6px (visible sliver) not barWidth (would force circles).
        const barH = Math.max(6, h * (height * 0.92));
        const x = i * (barWidth + gap);
        const y = height - barH; // anchored at bottom
        // Round top corners only; keep base square so bars look grounded
        const r = Math.min(barWidth / 2, barH / 2, 8);

        return (
          <rect
            key={i}
            x={x}
            y={y}
            width={barWidth}
            height={barH}
            rx={r}
            ry={r}
            fill={`url(#vg-${i})`}
            filter="url(#viz-glow)"
          />
        );
      })}
    </svg>
  );
};

// ── Colour helpers ───────────────────────────────────────────────────────────

function buildMirroredGradient(accent: string, highlight: string, total: number): string[] {
  const half = Math.ceil(total / 2);
  const left = interpolateColors(accent, highlight, half);
  const right = [...left].reverse();
  return [...left, ...right].slice(0, total);
}

function interpolateColors(c1Hex: string, c2Hex: string, steps: number): string[] {
  const c1 = hexToRgb(c1Hex);
  const c2 = hexToRgb(c2Hex);
  if (!c1 || !c2) return Array(steps).fill(c1Hex);
  return Array.from({ length: steps }, (_, i) => {
    const t = steps > 1 ? i / (steps - 1) : 0;
    return `rgb(${lerp(c1.r, c2.r, t)},${lerp(c1.g, c2.g, t)},${lerp(c1.b, c2.b, t)})`;
  });
}

function lerp(a: number, b: number, t: number) { return Math.round(a + (b - a) * t); }

function hexToRgb(hex: string) {
  const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return m ? { r: parseInt(m[1], 16), g: parseInt(m[2], 16), b: parseInt(m[3], 16) } : null;
}
