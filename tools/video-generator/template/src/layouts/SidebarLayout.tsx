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
  FrequencyBarsVisualizer,
} from '../components';

interface SidebarLayoutProps {
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

export const SidebarLayout: React.FC<SidebarLayoutProps> = ({
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

  const slideX = interpolate(lyricProgress, [0, 0.15], [-20, 0], {
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
    };

    switch (design.typography.textEffect) {
      case 'glow':
        return {
          ...baseStyles,
          textShadow: `0 4px 30px ${design.palette.glowColor}`,
        };
      case 'shadow':
        return {
          ...baseStyles,
          textShadow: `4px 4px 15px rgba(0,0,0,0.5)`,
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

  // Render motif for sidebar
  const renderMotif = () => {
    const props = {
      design,
      frequencyData,
      width: 864, // 45% of 1920
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
        return <ParticleField {...props} />;
    }
  };

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        position: 'relative',
      }}
    >
      {/* Left side - Lyrics (55%) */}
      <div
        style={{
          width: '55%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          padding: '60px 80px',
          boxSizing: 'border-box',
          zIndex: 1,
        }}
      >
        {/* Section badge */}
        {design.layout.showSectionBadge && (
          <div
            style={{
              display: 'inline-block',
              padding: '10px 28px',
              background: `${design.palette.accentColor}15`,
              borderRadius: design.typography.sectionBadgeStyle === 'pill' ? 100 : 8,
              border: `2px solid ${design.palette.accentColor}40`,
              marginBottom: 40,
              alignSelf: 'flex-start',
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
            transform: `translateX(${slideX}px)`,
          }}
        >
          <h1 style={getTextStyles()}>
            {currentLyric ? currentLyric.text : '♪'}
          </h1>
        </div>

        {/* Next lyric */}
        {design.layout.showNextLyric && nextLyric && (
          <div style={{ marginTop: 30, opacity: 0.35 }}>
            <p
              style={{
                color: design.palette.secondaryColor,
                fontSize: 40,
                fontWeight: 400,
                margin: 0,
              }}
            >
              {nextLyric.text}
            </p>
          </div>
        )}

        {/* Progress bar */}
        {design.layout.showProgressBar && (
          <div
            style={{
              marginTop: 60,
              width: '80%',
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
        <div style={{ marginTop: 24, display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ color: design.palette.primaryColor, fontSize: 18, fontWeight: 500 }}>
            {songTitle}
          </span>
          <span
            style={{
              color: design.palette.accentColor,
              fontSize: 14,
              padding: '4px 12px',
              background: `${design.palette.accentColor}15`,
              borderRadius: 100,
            }}
          >
            {genre}
          </span>
        </div>
      </div>

      {/* Right side - Visual motif (45%) */}
      <div
        style={{
          width: '45%',
          height: '100%',
          position: 'relative',
          background: `${design.palette.accentColor}08`,
          overflow: 'hidden',
        }}
      >
        {renderMotif()}
      </div>
    </div>
  );
};
