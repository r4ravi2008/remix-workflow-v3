import React, { useState, useMemo } from 'react';
import { useCurrentFrame, interpolate, staticFile, Img } from 'remotion';
import type { DesignConfig } from '../utils/designLoader';
import type { ImageSequence, ImageSequenceFrame } from '../utils/imageSequence';
import type { LyricsData, LyricLine, Section } from '../MusicVideo';
import { FrequencyBarsVisualizer, WaveformRings } from '../components';

interface CoverArtVerticalLayoutProps {
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
  imageSequence?: ImageSequence | null;
}

// ─── Layout constants ────────────────────────────────────────────────────────
// Video canvas: 1080 x 1920 (9:16 vertical format)
//
//  +----------------------+
//  |                      |
//  |   cover-art.jpg      |
//  |   (inset, rounded,   |  60% (1152px)
//  |    feathered edges)   |
//  |                      |
//  |   title + genre      |
//  +----------------------+
//  |                      |
//  |   scrolling lyrics   |  30% (576px)
//  |   (active highlight) |
//  |                      |
//  +----------------------+
//  |   visualizer bars    |  10% (192px)
//  |   + progress bar     |
//  +----------------------+
//
// Cover art is inset by ~2.5% with rounded corners and feathered edges
// that blend smoothly into the background gradient.

const COVER_ART_HEIGHT = 1152; // 60% of 1920px
const LYRICS_HEIGHT = 576; // 30% of 1920px
const VISUALIZER_HEIGHT = 192; // 10% of 1920px

const LINE_HEIGHT = 60;
const LYRICS_CONTAINER_HEIGHT = LYRICS_HEIGHT - 40; // Slight padding
const CENTER_PADDING = LYRICS_CONTAINER_HEIGHT / 2 - LINE_HEIGHT / 2;

// Inset padding for the cover art (percentage of the panel)
const ART_INSET = '8%';

const ACTIVE_SIZE_RATIO = 0.55; // Larger than horizontal's 0.40 for vertical
const INACTIVE_SIZE_RATIO = 0.35; // Slightly larger inactive text

export const CoverArtVerticalLayout: React.FC<CoverArtVerticalLayoutProps> = ({
  design,
  frequencyData,
  bandEnergies,
  barHeights,
  lyricsData,
  currentTime,
  overallProgress,
  songTitle,
  genre,
  imageSequence,
}) => {
  useCurrentFrame();
  const [coverArtError, setCoverArtError] = useState(false);
  const [failedSequenceImagePaths, setFailedSequenceImagePaths] = useState<string[]>([]);

  // ── Music-reactive values ─────────────────────────────────────────────────
  const bass = bandEnergies?.bass ?? 0;
  const overall = bandEnergies?.overall ?? 0;

  // Cover art breathing — subtle scale on bass hits (1.0 → 1.04)
  const artScale = 1 + bass * 0.04;

  // Vignette intensity — darkens on beats (0.2 → 0.5)
  const vignetteOpacity = 0.2 + overall * 0.3;

  // Glow ring around cover art — pulses with bass
  const glowIntensity = bass * 0.8;
  const glowShadow = glowIntensity > 0.05
    ? `0 0 ${30 * glowIntensity}px ${design.palette.accentColor}${Math.round(glowIntensity * 80).toString(16).padStart(2, '0')}, 0 0 ${60 * glowIntensity}px ${design.palette.highlightColor}${Math.round(glowIntensity * 40).toString(16).padStart(2, '0')}`
    : 'none';

  // Title text glow — reactive shadow on bass
  const titleGlowOpacity = bass * 0.7;

  // Genre badge dot — scale pulse with overall energy
  const dotScale = 1 + overall * 0.6;
  const dotGlowSize = 8 + overall * 16;

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
      lineHeight: 1.4,
    };
    switch (design.typography.textEffect) {
      case 'glow':
        return {
          ...base,
          textShadow: `0 0 20px ${design.palette.glowColor}, 0 0 40px ${design.palette.glowColor}80`,
        };
      case 'shadow':
        return { ...base, textShadow: '0 2px 8px rgba(0,0,0,0.6)' };
      case 'outline':
        return {
          ...base,
          WebkitTextStroke: `1.5px ${design.palette.accentColor}`,
          color: 'transparent',
        };
      default:
        return {
          ...base,
          textShadow: '0 1px 3px rgba(0,0,0,0.3)',
        };
    }
  };

  const inactiveStyle: React.CSSProperties = {
    color: design.palette.secondaryColor,
    fontSize: inactiveFontSize,
    fontWeight: 400,
    margin: 0,
    lineHeight: 1.4,
    letterSpacing: '0.01em',
    opacity: 0.85,
  };

  // ── Radial ring geometry ────────────────────────────────────────────────
  // Persistent concentric rings centered behind the cover art, pulsing with bass.
  const NUM_RINGS = 6;
  const rings = useMemo(() => {
    return Array.from({ length: NUM_RINGS }, (_, i) => {
      const t = (i + 1) / NUM_RINGS;
      // Base radius scales from ~140px to ~450px (fills the cover art section nicely)
      const baseRadius = 140 + t * 310;
      // Rings breathe with bass — inner rings react more
      const breathFactor = (1 - t * 0.5) * 0.12; // inner: 12%, outer: 6%
      const radius = baseRadius + bass * breathFactor * baseRadius;
      // Opacity fades outward; pulses with bass
      const baseOpacity = 0.35 - t * 0.12; // 0.35 → 0.23
      const opacity = baseOpacity + bass * 0.25 * (1 - t);
      // Alternate colors between accent and highlight
      const color = i % 2 === 0
        ? design.palette.accentColor
        : design.palette.highlightColor;
      return { radius, opacity: Math.min(opacity, 0.65), color, strokeWidth: 2.5 - t * 0.8 };
    });
  }, [bass, design.palette.accentColor, design.palette.highlightColor]);

  const activeSequenceFrame: ImageSequenceFrame | null = useMemo(() => {
    const frames = imageSequence?.frames ?? [];
    const matchingFrame = frames.find((item) => currentTime >= item.start_time && currentTime < item.end_time);
    if (matchingFrame) return matchingFrame;

    return frames.reduce<ImageSequenceFrame | null>((latest, item) => {
      if (currentTime < item.start_time) return latest;
      if (!latest || item.start_time > latest.start_time) return item;
      return latest;
    }, null);
  }, [imageSequence, currentTime]);

  const activeImageSrc = activeSequenceFrame?.image_path ?? 'cover-art.jpg';
  const getSafeImageSrc = (imagePath: string) => (
    failedSequenceImagePaths.includes(imagePath) ? 'cover-art.jpg' : imagePath
  );
  const handleImageError = (imagePath: string) => {
    if (imagePath === 'cover-art.jpg') {
      setCoverArtError(true);
      return;
    }

    setFailedSequenceImagePaths((paths) => (
      paths.includes(imagePath) ? paths : [...paths, imagePath]
    ));
  };

  // ── Render ────────────────────────────────────────────────────────────────
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
      {/* ── Option A: Ambient blurred cover art background ── */}
      {!coverArtError && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            overflow: 'hidden',
            zIndex: 0,
          }}
        >
          <Img
            src={staticFile(getSafeImageSrc(activeImageSrc))}
            onError={() => handleImageError(getSafeImageSrc(activeImageSrc))}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              objectPosition: 'center',
              // Heavy blur + slight upscale to prevent edge artifacts
              filter: 'blur(60px) saturate(1.3)',
              transform: 'scale(1.15)',
            }}
          />
          {/* Dim overlay — keeps text legible while preserving color richness */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              background: 'rgba(0, 0, 0, 0.45)',
            }}
          />
        </div>
      )}

      {/* ── Option C: Radial rings behind cover art ── */}
      <svg
        width="1080"
        height="1152"
        viewBox="0 0 1080 1152"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          pointerEvents: 'none',
          zIndex: 1,
        }}
      >
        {rings.map((ring, i) => (
          <circle
            key={i}
            cx={540}
            cy={500}
            r={ring.radius}
            fill="none"
            stroke={ring.color}
            strokeWidth={ring.strokeWidth}
            opacity={ring.opacity}
          />
        ))}
      </svg>

      {/* ── Dynamic expanding rings on beat ── */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: 1080,
          height: 1920,
          zIndex: 1,
          pointerEvents: 'none',
          opacity: 0.35,
        }}
      >
        <WaveformRings
          design={design}
          frequencyData={frequencyData}
          width={1080}
          height={1920}
        />
      </div>

      {/* ── Top 60%: cover art + title below ── */}
      <div
        style={{
          width: '100%',
          height: COVER_ART_HEIGHT,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
          padding: '24px 0',
          boxSizing: 'border-box',
          position: 'relative',
          zIndex: 2,
        }}
      >
        {/* Outer wrapper for glow ring + scale (not clipped by mask) */}
        <div
          style={{
            width: 'auto',
            height: '75%',
            aspectRatio: '1 / 1',
            maxWidth: `calc(100% - 2 * ${ART_INSET})`,
            maxHeight: `calc(100% - 2 * ${ART_INSET})`,
            borderRadius: 24,
            flexShrink: 0,
            transform: `scale(${artScale})`,
            boxShadow: glowShadow,
            position: 'relative',
          }}
        >
            {/* Inner container — feathered edges mask */}
            <div
              style={{
                width: '100%',
                height: '100%',
                borderRadius: 24,
                overflow: 'hidden',
                position: 'relative',
                // Feathered edge mask: refined fade for smoother blend
                maskImage:
                  'radial-gradient(ellipse 96% 96% at 50% 50%, black 75%, transparent 100%)',
                WebkitMaskImage:
                  'radial-gradient(ellipse 96% 96% at 50% 50%, black 75%, transparent 100%)',
              }}
            >
              {!coverArtError ? (
                <Img
                  src={staticFile(getSafeImageSrc(activeImageSrc))}
                  onError={() => handleImageError(getSafeImageSrc(activeImageSrc))}
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
                      opacity: 0.75,
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

              {/* Beat-reactive vignette — darkens on hits */}
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  background:
                    `radial-gradient(ellipse at 50% 50%, transparent 55%, rgba(0,0,0,${vignetteOpacity.toFixed(2)}) 100%)`,
                  pointerEvents: 'none',
                }}
              />
            </div>
        </div>

        {/* Song title + genre badge — below cover art */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 14,
            marginTop: 20,
          }}
        >
          {/* Title with gradient text + bass-reactive glow */}
          <span
            style={{
              fontSize: 36, // Smaller than horizontal's 42px
              fontWeight: 800,
              lineHeight: 1.15,
              letterSpacing: '-0.02em',
              background: `linear-gradient(135deg, ${design.palette.primaryColor} 0%, ${design.palette.highlightColor} 100%)`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              filter: `drop-shadow(0 4px 8px rgba(0,0,0,0.5)) drop-shadow(0 0 ${12 + titleGlowOpacity * 20}px ${design.palette.highlightColor}${Math.round(titleGlowOpacity * 180).toString(16).padStart(2, '0')})`,
              textAlign: 'center',
            }}
          >
            {songTitle}
          </span>

          {/* Genre badge with refined styling */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              padding: '8px 20px',
              background: `linear-gradient(135deg, ${design.palette.accentColor}15 0%, ${design.palette.highlightColor}10 100%)`,
              border: `1.5px solid ${design.palette.accentColor}50`,
              borderRadius: 100,
              backdropFilter: 'blur(12px) saturate(180%)',
              WebkitBackdropFilter: 'blur(12px) saturate(180%)',
              boxShadow: `0 4px 15px ${design.palette.accentColor}20, inset 0 1px 0 ${design.palette.accentColor}30`,
            }}
          >
            <div
              style={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                background: design.palette.highlightColor,
                boxShadow: `0 0 ${dotGlowSize}px ${design.palette.highlightColor}`,
                transform: `scale(${dotScale})`,
              }}
            />
            <span
              style={{
                color: design.palette.accentColor,
                fontSize: 14,
                fontWeight: 600,
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
              }}
            >
              {genre}
            </span>
          </div>
        </div>
      </div>

      {/* ── Middle 30%: scrolling lyrics ── */}
      <div
        style={{
          width: '100%',
          height: LYRICS_HEIGHT,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px 32px',
          boxSizing: 'border-box',
          position: 'relative',
          zIndex: 2,
        }}
      >
        {/* Lyrics window with refined fade edges */}
        <div
          style={{
            width: '100%',
            height: LYRICS_CONTAINER_HEIGHT,
            overflow: 'hidden',
            maskImage:
              'linear-gradient(to bottom, transparent 0%, black 12%, black 88%, transparent 100%)',
            WebkitMaskImage:
              'linear-gradient(to bottom, transparent 0%, black 12%, black 88%, transparent 100%)',
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
      </div>

      {/* ── Bottom 10%: visualizer + progress bar ── */}
      <div
        style={{
          width: '100%',
          height: VISUALIZER_HEIGHT,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '0 16px',
          boxSizing: 'border-box',
          gap: 16,
          position: 'relative',
          zIndex: 2,
        }}
      >
        {/* Visualizer */}
        <FrequencyBarsVisualizer
          design={design}
          barHeights={barHeights}
          width={1000}
          height={100}
        />

        {/* Progress bar with refined styling */}
        {design.layout.showProgressBar && (
          <div
            style={{
              width: '75%',
              height: 4,
              background: `${design.palette.primaryColor}10`,
              borderRadius: 100,
              overflow: 'hidden',
              boxShadow: `inset 0 1px 2px rgba(0,0,0,0.3)`,
            }}
          >
            <div
              style={{
                width: `${overallProgress * 100}%`,
                height: '100%',
                background: `linear-gradient(90deg, ${design.palette.accentColor}, ${design.palette.highlightColor})`,
                borderRadius: 100,
                boxShadow: `0 0 10px ${design.palette.highlightColor}60`,
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
};
