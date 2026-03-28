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

interface FullBleedLayoutProps {
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

export const FullBleedLayout: React.FC<FullBleedLayoutProps> = ({
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

  // Lyric entrance animation
  const lyricProgress = currentLyric
    ? Math.min((currentTime - currentLyric.start_time) / (currentLyric.end_time - currentLyric.start_time), 1)
    : 0;

  const fadeIn = interpolate(lyricProgress, [0, 0.15], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const scale = interpolate(lyricProgress, [0, 0.15], [0.95, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Text effect styles
  const getTextStyles = () => {
    const baseStyles: React.CSSProperties = {
      color: design.palette.highlightColor,
      fontSize: design.typography.mainLyricSize * 1.1,
      fontWeight: design.typography.mainLyricWeight,
      fontStyle: design.typography.mainLyricItalic ? 'italic' : 'normal',
      letterSpacing: design.typography.letterSpacing,
      margin: 0,
      lineHeight: 1.3,
      textAlign: 'center',
    };

    switch (design.typography.textEffect) {
      case 'glow':
        return {
          ...baseStyles,
          textShadow: `0 4px 60px ${design.palette.glowColor}`,
        };
      case 'shadow':
        return {
          ...baseStyles,
          textShadow: `4px 4px 20px rgba(0,0,0,0.8)`,
        };
      case 'outline':
        return {
          ...baseStyles,
          WebkitTextStroke: `3px ${design.palette.accentColor}`,
          color: 'transparent',
        };
      default:
        return baseStyles;
    }
  };

  // Render primary motif (fills background)
  const renderPrimaryMotif = () => {
    const props = {
      design,
      frequencyData,
      width: 1920,
      height: 1080,
    };

    switch (design.motif.primary) {
      case 'particles':
        return <ParticleField {...props} />;
      case 'geometric-burst':
        return <GeometricBurst {...props} />;
      case 'aurora':
        return <AuroraBackground {...props} />;
      case 'waveform-rings':
        return <WaveformRings {...props} />;
      case 'noise-field':
        return <NoiseField {...props} />;
      default:
        return <AuroraBackground {...props} />;
    }
  };

  // Render secondary motif
  const renderSecondaryMotif = () => {
    if (!design.motif.secondary) return null;

    const props = {
      design,
      frequencyData,
      width: 1920,
      height: 1080,
    };

    switch (design.motif.secondary) {
      case 'particles':
        return <ParticleField {...props} />;
      case 'geometric-burst':
        return <GeometricBurst {...props} />;
      case 'aurora':
        return <AuroraBackground {...props} />;
      case 'waveform-rings':
        return <WaveformRings {...props} />;
      case 'noise-field':
        return <NoiseField {...props} />;
      default:
        return null;
    }
  };

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'flex-end',
        padding: '60px 80px',
        boxSizing: 'border-box',
      }}
    >
      {/* Full background motif */}
      <div style={{ position: 'absolute', inset: 0, zIndex: 0 }}>
        {renderPrimaryMotif()}
        {renderSecondaryMotif()}
      </div>

      {/* Lyrics in lower third with backdrop blur */}
      <div
        style={{
          position: 'relative',
          zIndex: 1,
          background: 'rgba(0,0,0,0.4)',
          backdropFilter: 'blur(20px)',
          borderRadius: 20,
          padding: '40px 60px',
          marginBottom: 40,
          maxWidth: 1400,
          alignSelf: 'center',
        }}
      >
        {/* Section badge */}
        {design.layout.showSectionBadge && (
          <div
            style={{
              display: 'inline-block',
              padding: '8px 24px',
              background: `${design.palette.accentColor}30`,
              borderRadius: design.typography.sectionBadgeStyle === 'pill' ? 100 : 8,
              border: `2px solid ${design.palette.accentColor}60`,
              marginBottom: 20,
            }}
          >
            <span
              style={{
                color: design.palette.accentColor,
                fontSize: 16,
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.15em',
              }}
            >
              {currentSection ? currentSection.name : '♪'}
            </span>
          </div>
        )}

        {/* Active lyric */}
        <div
          style={{
            opacity: fadeIn,
            transform: `scale(${scale})`,
            transition: 'transform 0.1s ease-out',
          }}
        >
          <h1 style={getTextStyles()}>
            {currentLyric ? currentLyric.text : '♪'}
          </h1>
        </div>

        {/* Next lyric */}
        {design.layout.showNextLyric && nextLyric && (
          <div style={{ marginTop: 20, opacity: 0.5 }}>
            <p
              style={{
                color: design.palette.secondaryColor,
                fontSize: 36,
                fontWeight: 400,
                margin: 0,
                textAlign: 'center',
              }}
            >
              {nextLyric.text}
            </p>
          </div>
        )}
      </div>

      {/* Progress bar at bottom */}
      {design.layout.showProgressBar && (
        <div
          style={{
            width: '100%',
            height: 4,
            background: `${design.palette.primaryColor}20`,
            position: 'absolute',
            bottom: 0,
            left: 0,
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
    </div>
  );
};
