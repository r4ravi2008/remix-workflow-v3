import React, { useState } from 'react';
import { useCurrentFrame, interpolate, staticFile, Img } from 'remotion';
import type { DesignConfig } from '../utils/designLoader';
import type { LyricsData, LyricLine, Section } from '../MusicVideo';
import { FrequencyBarsVisualizer } from '../components';

interface CoverArtLayoutProps {
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

// ─── Layout constants ────────────────────────────────────────────────────────
// Video canvas: 1920 x 1080
//
//  ┌─────────────────────────────────┬──────────────────┐
//  │  ┌───────────────────────────┐  │                  │
//  │  │                           │  │  ┌────────────┐  │
//  │  │   cover-art.jpg (inset)   │  │  │  lyrics     │  │
//  │  │   rounded + feathered     │  │  └────────────┘  │
//  │  │                           │  │  ┌────────────┐  │
//  │  └───────────────────────────┘  │  │ visualizer  │  │
//  │     title + genre badge         │  └────────────┘  │
//  └─────────────────────────────────┴──────────────────┘
//         75% (1440px)                    25% (480px)
//
// Cover art is inset by ~5% with rounded corners and feathered edges
// that blend smoothly into the background gradient.

const LINE_HEIGHT = 60;
const CONTAINER_HEIGHT = 270; // 25% of 1080px
const CENTER_PADDING = CONTAINER_HEIGHT / 2 - LINE_HEIGHT / 2;

// Inset padding for the cover art (percentage of the panel)
const ART_INSET = '5%';

const ACTIVE_SIZE_RATIO = 0.40;
const INACTIVE_SIZE_RATIO = 0.26;

export const CoverArtLayout: React.FC<CoverArtLayoutProps> = ({
  design,
  barHeights,
  lyricsData,
  currentTime,
  overallProgress,
  songTitle,
  genre,
}) => {
  useCurrentFrame();
  const [coverArtError, setCoverArtError] = useState(false);

  // ── Scrolling lyrics ──────────────────────────────────────────────────────
  const lyrics = lyricsData?.lyrics ?? [];

  let activeIndex = -1;
  for (let i = 0; i < lyrics.length; i++) {
    if (lyrics[i].start_time <= currentTime) activeIndex = i;
    else break;
  }

  let scrollY = 0;
  if (lyrics.length >= 2) {
    const times = lyrics.map((l) => l.start_time);
    const targets = lyrics.map((_, i) => i * LINE_HEIGHT);
    scrollY = interpolate(currentTime, times, targets, {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
  }

  // ── Text styles ───────────────────────────────────────────────────────────
  const activeFontSize = Math.round(
    design.typography.mainLyricSize * ACTIVE_SIZE_RATIO
  );
  const inactiveFontSize = Math.max(
    14,
    Math.round(design.typography.mainLyricSize * INACTIVE_SIZE_RATIO)
  );

  const getActiveStyle = (): React.CSSProperties => {
    const base: React.CSSProperties = {
      color: design.palette.highlightColor,
      fontSize: activeFontSize,
      fontWeight: design.typography.mainLyricWeight,
      fontStyle: design.typography.mainLyricItalic ? 'italic' : 'normal',
      letterSpacing: design.typography.letterSpacing,
      margin: 0,
      lineHeight: 1.35,
    };
    switch (design.typography.textEffect) {
      case 'glow':
        return {
          ...base,
          textShadow: `0 2px 16px ${design.palette.glowColor}`,
        };
      case 'shadow':
        return { ...base, textShadow: '2px 2px 6px rgba(0,0,0,0.5)' };
      case 'outline':
        return {
          ...base,
          WebkitTextStroke: `1px ${design.palette.accentColor}`,
          color: 'transparent',
        };
      default:
        return base;
    }
  };

  const inactiveStyle: React.CSSProperties = {
    color: design.palette.secondaryColor,
    fontSize: inactiveFontSize,
    fontWeight: 400,
    margin: 0,
    lineHeight: 1.35,
    letterSpacing: design.typography.letterSpacing,
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'row',
        position: 'relative',
      }}
    >
      {/* ── Left 75%: cover art with inset + feathered edges ── */}
      <div
        style={{
          width: '75%',
          height: '100%',
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
        }}
      >
        {/* Cover art container — inset with feathered edges */}
        <div
          style={{
            position: 'absolute',
            top: ART_INSET,
            left: ART_INSET,
            right: ART_INSET,
            bottom: ART_INSET,
            borderRadius: 24,
            overflow: 'hidden',
            // Feathered edge mask: fades out on all sides so the image
            // blends smoothly into the background gradient
            maskImage:
              'radial-gradient(ellipse 92% 92% at 45% 50%, black 60%, transparent 100%)',
            WebkitMaskImage:
              'radial-gradient(ellipse 92% 92% at 45% 50%, black 60%, transparent 100%)',
          }}
        >
          {!coverArtError ? (
            <Img
              src={staticFile('cover-art.jpg')}
              onError={() => setCoverArtError(true)}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                objectPosition: 'center',
              }}
            />
          ) : (
            /* Fallback placeholder if cover art fails */
            <div
              style={{
                width: '100%',
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: `${design.palette.accentColor}08`,
              }}
            >
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 32,
                  opacity: 0.35,
                }}
              >
                <div
                  style={{
                    width: 320,
                    height: 320,
                    borderRadius: 24,
                    background: `${design.palette.accentColor}20`,
                    border: `2px solid ${design.palette.accentColor}30`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 120,
                    lineHeight: 1,
                    color: design.palette.primaryColor,
                  }}
                >
                  &#9835;
                </div>
              </div>
            </div>
          )}

          {/* Subtle vignette inside the image for depth */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              background:
                'radial-gradient(ellipse at 50% 50%, transparent 50%, rgba(0,0,0,0.35) 100%)',
              pointerEvents: 'none',
            }}
          />
        </div>

        {/* Song title + genre badge at bottom-left */}
        <div
          style={{
            position: 'absolute',
            bottom: 48,
            left: 48,
            display: 'flex',
            flexDirection: 'column',
            gap: 12,
            zIndex: 2,
          }}
        >
          <span
            style={{
              color: design.palette.primaryColor,
              fontSize: 36,
              fontWeight: 700,
              textShadow: '0 2px 12px rgba(0,0,0,0.7)',
              maxWidth: 900,
              lineHeight: 1.2,
            }}
          >
            {songTitle}
          </span>
          <span
            style={{
              color: design.palette.accentColor,
              fontSize: 18,
              fontWeight: 500,
              padding: '6px 20px',
              background: 'rgba(0,0,0,0.45)',
              border: `1px solid ${design.palette.accentColor}60`,
              borderRadius: 100,
              backdropFilter: 'blur(8px)',
              alignSelf: 'flex-start',
            }}
          >
            {genre}
          </span>
        </div>
      </div>

      {/* ── Right 25%: lyrics + visualizer, centred as a group ── */}
      <div
        style={{
          width: '25%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '0 16px',
          boxSizing: 'border-box',
          gap: 28,
        }}
      >
        {/* Lyrics window */}
        <div
          style={{
            width: '100%',
            height: CONTAINER_HEIGHT,
            overflow: 'hidden',
            maskImage:
              'linear-gradient(to bottom, transparent 0%, black 15%, black 85%, transparent 100%)',
            WebkitMaskImage:
              'linear-gradient(to bottom, transparent 0%, black 15%, black 85%, transparent 100%)',
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
                <span
                  style={{
                    color: design.palette.primaryColor,
                    fontSize: 28,
                  }}
                >
                  &#9835;
                </span>
              </div>
            ) : (
              lyrics.map((line, i) => {
                const isActive = i === activeIndex;
                const absDistance = Math.abs(i - activeIndex);
                const opacity = isActive
                  ? 1
                  : absDistance === 1
                  ? 0.5
                  : absDistance === 2
                  ? 0.3
                  : 0.15;
                const lineStyle = isActive ? getActiveStyle() : inactiveStyle;

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
                    }}
                  >
                    <p style={{ ...lineStyle, margin: 0 }}>{line.text}</p>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Visualizer */}
        <FrequencyBarsVisualizer
          design={design}
          barHeights={barHeights}
          width={400}
          height={100}
        />

        {/* Progress bar */}
        {design.layout.showProgressBar && (
          <div
            style={{
              width: '80%',
              height: 3,
              background: `${design.palette.primaryColor}15`,
              borderRadius: 2,
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                width: `${overallProgress * 100}%`,
                height: '100%',
                background: `linear-gradient(to right, ${design.palette.accentColor}, ${design.palette.highlightColor})`,
                borderRadius: 2,
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
};
