import React from 'react';
import { useCurrentFrame, interpolate } from 'remotion';
import type { DesignConfig } from '../utils/designLoader';
import type { LyricsData, LyricLine, Section } from '../MusicVideo';
import {
  ParticleField,
  GeometricBurst,
  AuroraBackground,
  WaveformRings,
  NoiseField,
} from '../components';

interface MinimalLayoutProps {
  design: DesignConfig;
  frequencyData: number[];
  bandEnergies?: any;
  barHeights?: number[];
  lyricsData: LyricsData | null;
  currentLyric: LyricLine | null;
  nextLyric: LyricLine | null;
  currentSection: Section | null;
  currentTime: number;
  overallProgress: number;
  songTitle: string;
  genre: string;
}

export const MinimalLayout: React.FC<MinimalLayoutProps> = ({
  design,
  frequencyData,
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

  // Lyric entrance animation - word by word if selected
  const lyricProgress = currentLyric
    ? Math.min((currentTime - currentLyric.start_time) / (currentLyric.end_time - currentLyric.start_time), 1)
    : 0;

  const fadeIn = interpolate(lyricProgress, [0, 0.2], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Text effect styles
  const getTextStyles = () => {
    const baseStyles: React.CSSProperties = {
      color: design.palette.highlightColor,
      fontSize: design.typography.mainLyricSize * 1.4,
      fontWeight: design.typography.mainLyricWeight,
      fontStyle: design.typography.mainLyricItalic ? 'italic' : 'normal',
      letterSpacing: design.typography.letterSpacing,
      margin: 0,
      lineHeight: 1.4,
      textAlign: 'center',
    };

    switch (design.typography.textEffect) {
      case 'glow':
        return {
          ...baseStyles,
          textShadow: `0 4px 40px ${design.palette.glowColor}`,
        };
      case 'shadow':
        return {
          ...baseStyles,
          textShadow: `2px 2px 8px rgba(0,0,0,0.3)`,
        };
      case 'outline':
        return {
          ...baseStyles,
          WebkitTextStroke: `2px ${design.palette.accentColor}`,
          color: 'transparent',
        };
      default:
        return baseStyles;
    }
  };

  // Render subtle background motif
  const renderMotif = () => {
    const props = {
      design: { ...design, motif: { ...design.motif, intensity: 'low' as const } },
      frequencyData,
      width: 1920,
      height: 1080,
    };

    switch (design.motif.primary) {
      case 'particles':
        return <ParticleField {...props} />;
      case 'waveform-rings':
        return <WaveformRings {...props} />;
      case 'noise-field':
        return <NoiseField {...props} />;
      default:
        return <NoiseField {...props} />;
    }
  };

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '80px 120px',
        boxSizing: 'border-box',
        position: 'relative',
      }}
    >
      {/* Very subtle background */}
      <div style={{ position: 'absolute', inset: 0, zIndex: -1, opacity: 0.5 }}>
        {renderMotif()}
      </div>

      {/* Section badge - minimal */}
      {design.layout.showSectionBadge && currentSection && (
        <div
          style={{
            position: 'absolute',
            top: 60,
            padding: '8px 20px',
            background: 'transparent',
            border: `1px solid ${design.palette.accentColor}40`,
            borderRadius: 4,
          }}
        >
          <span
            style={{
              color: design.palette.accentColor,
              fontSize: 14,
              fontWeight: 500,
              textTransform: 'uppercase',
              letterSpacing: '0.2em',
            }}
          >
            {currentSection.name}
          </span>
        </div>
      )}

      {/* Large centered lyrics - takes up most of screen */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          width: '100%',
          opacity: fadeIn,
        }}
      >
        <h1 style={getTextStyles()}>
          {currentLyric ? currentLyric.text : '♪'}
        </h1>
      </div>

      {/* Thin progress line at bottom */}
      {design.layout.showProgressBar && (
        <div
          style={{
            position: 'absolute',
            bottom: 40,
            left: '10%',
            right: '10%',
            height: 2,
            background: `${design.palette.primaryColor}15`,
          }}
        >
          <div
            style={{
              width: `${overallProgress * 100}%`,
              height: '100%',
              background: design.palette.accentColor,
            }}
          />
        </div>
      )}

      {/* Song title - minimal */}
      <div
        style={{
          position: 'absolute',
          bottom: 60,
          color: design.palette.secondaryColor,
          fontSize: 14,
          letterSpacing: '0.1em',
        }}
      >
        {songTitle}
      </div>
    </div>
  );
};
