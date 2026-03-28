import React from 'react';
import { useCurrentFrame, interpolate } from 'remotion';
import type { DesignConfig } from '../utils/designLoader';
import type { LyricsData, LyricLine, Section } from '../MusicVideo';
import {
  ParticleField,
  AuroraBackground,
  WaveformRings,
  NoiseField,
  FrequencyBarsVisualizer,
} from '../components';

// GeometricBurst is intentionally excluded — its large hexagonal/polygon overlays
// obscure the lyrics. Any design.json that requests it falls back to particles.
// Section badge is intentionally removed — stage directions (e.g. "VOCAL EFFECT: REVERB")
// from the lyrics file contaminate it and it adds visual noise.

interface CenterStageLayoutProps {
  design: DesignConfig;
  frequencyData: number[];
  bandEnergies?: any;
  barHeights: number[];
  lyricsData: LyricsData | null;
  currentLyric: LyricLine | null;
  nextLyric: LyricLine | null;
  currentSection: Section | null;
  currentTime: number;
  overallProgress: number;
  songTitle: string;
  genre: string;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Scrolling lyrics constants
// ---------------------------------------------------------------------------
const LINE_HEIGHT = 140;      // px — slot height for every lyric line
const CONTAINER_HEIGHT = 560; // px — visible window; ~4 lines visible at once
const CENTER_PADDING = CONTAINER_HEIGHT / 2 - LINE_HEIGHT / 2; // centers first line

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const CenterStageLayout: React.FC<CenterStageLayoutProps> = ({
  design,
  frequencyData,
  barHeights,
  lyricsData,
  currentLyric,
  nextLyric,
  currentSection,
  currentTime,
  overallProgress,
  songTitle,
  genre,
}) => {
  const frame = useCurrentFrame();

  // ── Active lyric styles (for the highlighted line) ─────────────────────
  const getActiveTextStyle = (): React.CSSProperties => {
    const base: React.CSSProperties = {
      color: design.palette.highlightColor,
      fontSize: design.typography.mainLyricSize,
      fontWeight: design.typography.mainLyricWeight,
      fontStyle: design.typography.mainLyricItalic ? 'italic' : 'normal',
      letterSpacing: design.typography.letterSpacing,
      margin: 0,
      lineHeight: 1.3,
    };

    switch (design.typography.textEffect) {
      case 'glow':
        return { ...base, textShadow: `0 4px 30px ${design.palette.glowColor}` };
      case 'shadow':
        return { ...base, textShadow: '4px 4px 10px rgba(0,0,0,0.5)' };
      case 'outline':
        return {
          ...base,
          WebkitTextStroke: `2px ${design.palette.accentColor}`,
          color: 'transparent',
        };
      default:
        return base;
    }
  };

  // ── Background motif renderers (GeometricBurst replaced by particles) ──
  const renderMotif = (motifName: string) => {
    const props = { design, frequencyData, width: 1920, height: 1080 };
    switch (motifName) {
      case 'aurora':
        return <AuroraBackground {...props} />;
      case 'waveform-rings':
        return <WaveformRings {...props} />;
      case 'noise-field':
        return <NoiseField {...props} />;
      case 'particles':
      case 'geometric-burst': // intentional fallback — no hexagons
      default:
        return <ParticleField {...props} />;
    }
  };

  // ── Scrolling lyrics ────────────────────────────────────────────────────
  const lyrics = lyricsData?.lyrics ?? [];

  // Find the index of the most recently started lyric line.
  // Lines persist after their end_time — we never clear them.
  let activeIndex = -1;
  for (let i = 0; i < lyrics.length; i++) {
    if (lyrics[i].start_time <= currentTime) activeIndex = i;
    else break;
  }

  // Compute smooth scroll offset: interpolate the per-lyric target positions
  // over the audio timestamps so the container glides continuously.
  let scrollY = 0;
  if (lyrics.length >= 2) {
    const times = lyrics.map(l => l.start_time);
    const targets = lyrics.map((_, i) => i * LINE_HEIGHT);
    scrollY = interpolate(currentTime, times, targets, {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
  }

  // Section badge removed — not rendered

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '60px 80px',
        boxSizing: 'border-box',
        position: 'relative',
        zIndex: 1,
      }}
    >
      {/* ── Background motifs (behind everything) ── */}
      <div style={{ position: 'absolute', inset: 0, zIndex: -1 }}>
        {renderMotif(design.motif.primary)}
        {design.motif.secondary && renderMotif(design.motif.secondary)}
      </div>

      {/* Section badge removed */}

      {/* ── Scrolling lyrics window ── */}
      <div
        style={{
          flex: 1,
          width: '100%',
          maxWidth: 1400,
          height: CONTAINER_HEIGHT,
          overflow: 'hidden',
          position: 'relative',
          // Fade edges so lines gracefully appear/disappear at top and bottom
          maskImage:
            'linear-gradient(to bottom, transparent 0%, black 18%, black 82%, transparent 100%)',
          WebkitMaskImage:
            'linear-gradient(to bottom, transparent 0%, black 18%, black 82%, transparent 100%)',
        }}
      >
        <div
          style={{
            transform: `translateY(-${scrollY}px)`,
            paddingTop: CENTER_PADDING,
            paddingBottom: CENTER_PADDING,
          }}
        >
          {lyrics.length === 0 ? (
            <div
              style={{
                height: LINE_HEIGHT,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <span style={{ color: design.palette.primaryColor, fontSize: 60 }}>♪</span>
            </div>
          ) : (
            lyrics.map((line, i) => {
              const isActive = i === activeIndex;
              const distance = i - activeIndex; // negative = past, positive = future
              const absDistance = Math.abs(distance);

              // Opacity curve: active → 1.0, ±1 → 0.5, ±2 → 0.3, further → 0.15
              const opacity = isActive
                ? 1
                : absDistance === 1
                ? 0.5
                : absDistance === 2
                ? 0.3
                : 0.15;

              // Font size: active uses design value, others scale down
              const fontSize = isActive
                ? design.typography.mainLyricSize
                : Math.max(32, Math.round(design.typography.mainLyricSize * 0.58));

              const activeStyle = getActiveTextStyle();

              const lineStyle: React.CSSProperties = isActive
                ? { ...activeStyle, fontSize }
                : {
                    color: design.palette.secondaryColor,
                    fontSize,
                    fontWeight: 400,
                    margin: 0,
                    lineHeight: 1.3,
                    letterSpacing: design.typography.letterSpacing,
                  };

              return (
                <div
                  key={i}
                  style={{
                    minHeight: LINE_HEIGHT,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    textAlign: 'center',
                    opacity,
                    padding: '0 80px',
                  }}
                >
                  <p style={{ ...lineStyle, margin: 0 }}>{line.text}</p>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* ── Bottom: visualizer + progress + title ── */}
      <div
        style={{
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 24,
        }}
      >
        {/* Frequency bars */}
        {design.layout.visualizerPosition === 'bottom' && (
          <FrequencyBarsVisualizer
            design={design}
            barHeights={barHeights}
            width={1400}
            height={240}
          />
        )}

        {/* Progress bar */}
        {design.layout.showProgressBar && (
          <div
            style={{
              width: '60%',
              maxWidth: 600,
              height: 6,
              background: `${design.palette.primaryColor}15`,
              borderRadius: 3,
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                width: `${overallProgress * 100}%`,
                height: '100%',
                background: `linear-gradient(to right, ${design.palette.accentColor}, ${design.palette.highlightColor})`,
                borderRadius: 3,
              }}
            />
          </div>
        )}

        {/* Song info */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginTop: 4 }}>
          <span style={{ color: design.palette.primaryColor, fontSize: 20, fontWeight: 600 }}>
            {songTitle}
          </span>
          <span
            style={{
              color: design.palette.accentColor,
              fontSize: 16,
              fontWeight: 500,
              padding: '6px 16px',
              background: `${design.palette.accentColor}15`,
              borderRadius: 100,
            }}
          >
            {genre}
          </span>
        </div>
      </div>
    </div>
  );
};
