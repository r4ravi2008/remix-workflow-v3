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

interface StackedLayoutProps {
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

export const StackedLayout: React.FC<StackedLayoutProps> = ({
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

  const scale = interpolate(lyricProgress, [0, 0.15], [0.9, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Text effect styles
  const getTextStyles = () => {
    const baseStyles: React.CSSProperties = {
      color: design.palette.highlightColor,
      fontSize: design.typography.mainLyricSize * 1.2,
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

  // Render background motif
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
        flexDirection: 'column',
        position: 'relative',
      }}
    >
      {/* Subtle background */}
      <div style={{ position: 'absolute', inset: 0, zIndex: -1, opacity: 0.6 }}>
        {renderMotif()}
      </div>

      {/* Top section - Title & Section badge (20%) */}
      <div
        style={{
          height: '20%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px 80px',
          boxSizing: 'border-box',
        }}
      >
        <h2
          style={{
            color: design.palette.primaryColor,
            fontSize: 24,
            fontWeight: 600,
            margin: 0,
            marginBottom: 16,
            letterSpacing: '0.05em',
          }}
        >
          {songTitle}
        </h2>
        
        {design.layout.showSectionBadge && (
          <div
            style={{
              padding: '8px 24px',
              background: `${design.palette.accentColor}15`,
              borderRadius: design.typography.sectionBadgeStyle === 'pill' ? 100 : 8,
              border: `2px solid ${design.palette.accentColor}40`,
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
      </div>

      {/* Middle section - Current lyric (60%) */}
      <div
        style={{
          height: '60%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '0 120px',
          boxSizing: 'border-box',
        }}
      >
        <div
          style={{
            opacity: fadeIn,
            transform: `scale(${scale})`,
          }}
        >
          <h1 style={getTextStyles()}>
            {currentLyric ? currentLyric.text : '♪'}
          </h1>
        </div>
      </div>

      {/* Bottom section - Next lyric + Visualizer (20%) */}
      <div
        style={{
          height: '20%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px 80px',
          boxSizing: 'border-box',
          gap: 16,
        }}
      >
        {/* Next lyric preview */}
        {design.layout.showNextLyric && nextLyric && (
          <p
            style={{
              color: design.palette.secondaryColor,
              fontSize: 28,
              fontWeight: 400,
              margin: 0,
              opacity: 0.5,
              textAlign: 'center',
            }}
          >
            {nextLyric.text}
          </p>
        )}

        {/* Visualizer */}
        {design.layout.visualizerPosition === 'bottom' && (
          <FrequencyBarsVisualizer
            design={design}
            frequencyData={frequencyData}
            numBars={24}
            width={600}
            height={50}
          />
        )}

        {/* Progress bar */}
        {design.layout.showProgressBar && (
          <div
            style={{
              width: '50%',
              maxWidth: 400,
              height: 4,
              background: `${design.palette.primaryColor}15`,
              borderRadius: 2,
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                width: `${overallProgress * 100}%`,
                height: '100%',
                background: design.palette.accentColor,
                borderRadius: 2,
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
};
