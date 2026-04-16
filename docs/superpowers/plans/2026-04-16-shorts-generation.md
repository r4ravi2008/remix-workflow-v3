# Shorts Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Steps 10 & 11 to the Indic Song Remixer pipeline to generate a 9:16 vertical YouTube Short from the best clip segment of the full music video.

**Architecture:** Step 10 analyzes the remix audio and lyrics timestamps to auto-select the most engaging 30-second segment. Step 11 adds a second Remotion `<Composition>` (`MusicVideoShort`) with a new `CoverArtVerticalLayout` to the existing video project and renders the short. Both steps are autonomous by default, with optional manual segment selection.

**Tech Stack:** Remotion 4.x, React 18, FFmpeg (ebur128 loudness analysis), TypeScript, Node.js

**Spec:** `docs/superpowers/specs/2026-04-16-shorts-generation-design.md`

---

## File Structure

### New Files

| File | Responsibility |
|---|---|
| `tools/video-generator/template/src/MusicVideoShort.tsx` | Wrapper component: audio trim, lyrics rebase, forces vertical layout |
| `tools/video-generator/template/src/layouts/CoverArtVerticalLayout.tsx` | 9:16 vertical layout: cover art top 60%, lyrics middle 30%, visualizer bottom 10% |
| `prompts/step-10-select-short-clip.md` | Agent prompt for clip selection step |
| `prompts/step-11-generate-short-video.md` | Agent prompt for short video generation step |

### Modified Files

| File | Change |
|---|---|
| `tools/video-generator/template/src/layouts/index.ts` | Add `CoverArtVerticalLayout` export |
| `tools/video-generator/template/src/Root.tsx` | Add `MusicVideoShort` composition (conditional on `config.short`) |
| `tools/video-generator/template/src/utils/designLoader.ts` | Add `'cover-art-vertical'` to `DesignLayout.variant` union type |
| `prompts/step-0-prepare-workspace.md` | Add `shorts_clip_mode` and `shorts_duration` optional inputs |
| `prompts/references/workspace-conventions.md` | Add new files and meta.json fields |
| `prompts/README.md` | Add Steps 10 & 11 to pipeline index |
| `docs/intent.md` | Add Steps 10 & 11 to pipeline overview |

---

## Task 1: Add `cover-art-vertical` to DesignLayout type

**Files:**
- Modify: `tools/video-generator/template/src/utils/designLoader.ts:26-32`

- [ ] **Step 1: Update the DesignLayout variant union type**

In `tools/video-generator/template/src/utils/designLoader.ts`, update the `variant` field in `DesignLayout`:

```typescript
export interface DesignLayout {
  variant: 'cover-art' | 'cover-art-vertical' | 'center-stage' | 'full-bleed' | 'minimal' | 'sidebar' | 'stacked';
  showSectionBadge: boolean;
  showNextLyric: boolean;
  showProgressBar: boolean;
  visualizerPosition: 'bottom' | 'top' | 'hidden';
}
```

- [ ] **Step 2: Verify no type errors**

Run:
```bash
cd tools/video-generator/template && npx tsc --noEmit
```
Expected: No errors (the new variant is just a union addition).

- [ ] **Step 3: Commit**

```bash
git add tools/video-generator/template/src/utils/designLoader.ts
git commit -m "feat: add cover-art-vertical to DesignLayout variant type"
```

---

## Task 2: Create CoverArtVerticalLayout component

**Files:**
- Create: `tools/video-generator/template/src/layouts/CoverArtVerticalLayout.tsx`
- Modify: `tools/video-generator/template/src/layouts/index.ts`

- [ ] **Step 1: Create CoverArtVerticalLayout.tsx**

Create `tools/video-generator/template/src/layouts/CoverArtVerticalLayout.tsx` with the following content. This is a vertical adaptation of `CoverArtLayout.tsx` — same visual systems, rearranged for 9:16:

```tsx
import React, { useState, useMemo } from 'react';
import { useCurrentFrame, interpolate, staticFile, Img } from 'remotion';
import type { DesignConfig } from '../utils/designLoader';
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
}

// ─── Layout constants ────────────────────────────────────────────────────────
// Video canvas: 1080 x 1920 (9:16 vertical)
//
//  ┌──────────────────────┐
//  │                      │
//  │   cover-art.jpg      │
//  │   (inset, rounded,   │  60% (1152px)
//  │    feathered edges)   │
//  │                      │
//  │   title + genre      │
//  ├──────────────────────┤
//  │                      │
//  │   scrolling lyrics   │  30% (576px)
//  │   (active highlight) │
//  │                      │
//  ├──────────────────────┤
//  │   visualizer bars    │  10% (192px)
//  │   + progress bar     │
//  └──────────────────────┘

const COVER_ART_HEIGHT = 1152;   // 60% of 1920
const LYRICS_HEIGHT = 576;        // 30% of 1920
const VISUALIZER_HEIGHT = 192;    // 10% of 1920

const LINE_HEIGHT = 72;
const CENTER_PADDING = LYRICS_HEIGHT / 2 - LINE_HEIGHT / 2;

const ACTIVE_SIZE_RATIO = 0.55;
const INACTIVE_SIZE_RATIO = 0.32;

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
}) => {
  useCurrentFrame();
  const [coverArtError, setCoverArtError] = useState(false);

  // ── Music-reactive values ─────────────────────────────────────────────────
  const bass = bandEnergies?.bass ?? 0;
  const overall = bandEnergies?.overall ?? 0;

  const artScale = 1 + bass * 0.04;
  const vignetteOpacity = 0.2 + overall * 0.3;

  const glowIntensity = bass * 0.8;
  const glowShadow = glowIntensity > 0.05
    ? `0 0 ${30 * glowIntensity}px ${design.palette.accentColor}${Math.round(glowIntensity * 80).toString(16).padStart(2, '0')}, 0 0 ${60 * glowIntensity}px ${design.palette.highlightColor}${Math.round(glowIntensity * 40).toString(16).padStart(2, '0')}`
    : 'none';

  const titleGlowOpacity = bass * 0.7;
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
    16,
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

  // ── Radial rings behind cover art ─────────────────────────────────────────
  const NUM_RINGS = 5;
  const rings = useMemo(() => {
    return Array.from({ length: NUM_RINGS }, (_, i) => {
      const t = (i + 1) / NUM_RINGS;
      const baseRadius = 140 + t * 380;
      const breathFactor = (1 - t * 0.5) * 0.12;
      const radius = baseRadius + bass * breathFactor * baseRadius;
      const baseOpacity = 0.35 - t * 0.12;
      const opacity = baseOpacity + bass * 0.25 * (1 - t);
      const color = i % 2 === 0
        ? design.palette.accentColor
        : design.palette.highlightColor;
      return { radius, opacity: Math.min(opacity, 0.65), color, strokeWidth: 2.5 - t * 0.8 };
    });
  }, [bass, design.palette.accentColor, design.palette.highlightColor]);

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
      {/* ── Ambient blurred cover art background ── */}
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
            src={staticFile('cover-art.jpg')}
            onError={() => {}}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              objectPosition: 'center',
              filter: 'blur(60px) saturate(1.3)',
              transform: 'scale(1.15)',
            }}
          />
          <div
            style={{
              position: 'absolute',
              inset: 0,
              background: 'rgba(0, 0, 0, 0.45)',
            }}
          />
        </div>
      )}

      {/* ── Radial rings behind cover art ── */}
      <svg
        width="1080"
        height={COVER_ART_HEIGHT}
        viewBox={`0 0 1080 ${COVER_ART_HEIGHT}`}
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
          height: COVER_ART_HEIGHT,
          zIndex: 1,
          pointerEvents: 'none',
          opacity: 0.35,
        }}
      >
        <WaveformRings
          design={design}
          frequencyData={frequencyData}
          width={1080}
          height={COVER_ART_HEIGHT}
        />
      </div>

      {/* ── Top 60%: cover art + title ── */}
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
        {/* Cover art with glow ring + bass breathing */}
        <div
          style={{
            width: 'auto',
            height: '70%',
            aspectRatio: '1 / 1',
            maxWidth: 'calc(100% - 80px)',
            borderRadius: 24,
            flexShrink: 0,
            transform: `scale(${artScale})`,
            boxShadow: glowShadow,
            position: 'relative',
          }}
        >
          <div
            style={{
              width: '100%',
              height: '100%',
              borderRadius: 24,
              overflow: 'hidden',
              position: 'relative',
              maskImage:
                'radial-gradient(ellipse 96% 96% at 50% 50%, black 75%, transparent 100%)',
              WebkitMaskImage:
                'radial-gradient(ellipse 96% 96% at 50% 50%, black 75%, transparent 100%)',
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
                      width: 240,
                      height: 240,
                      borderRadius: 24,
                      background: `${design.palette.accentColor}20`,
                      border: `2px solid ${design.palette.accentColor}30`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: 100,
                      lineHeight: 1,
                      color: design.palette.primaryColor,
                    }}
                  >
                    &#9835;
                  </div>
                </div>
              </div>
            )}

            {/* Beat-reactive vignette */}
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

        {/* Song title + genre badge */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 12,
            marginTop: 16,
          }}
        >
          <span
            style={{
              fontSize: 36,
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
          padding: '0 32px',
          boxSizing: 'border-box',
          position: 'relative',
          zIndex: 2,
        }}
      >
        <div
          style={{
            width: '100%',
            height: LYRICS_HEIGHT - 40,
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
                    fontSize: 32,
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
          gap: 16,
          padding: '0 24px',
          boxSizing: 'border-box',
          position: 'relative',
          zIndex: 2,
        }}
      >
        <FrequencyBarsVisualizer
          design={design}
          barHeights={barHeights}
          width={1000}
          height={120}
        />

        {design.layout.showProgressBar && (
          <div
            style={{
              width: '80%',
              height: 4,
              background: `${design.palette.primaryColor}10`,
              borderRadius: 100,
              overflow: 'hidden',
              boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.3)',
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
```

- [ ] **Step 2: Export from layouts/index.ts**

Add to `tools/video-generator/template/src/layouts/index.ts`:

```typescript
export { CenterStageLayout } from './CenterStageLayout';
export { CoverArtLayout } from './CoverArtLayout';
export { CoverArtVerticalLayout } from './CoverArtVerticalLayout';
export { FullBleedLayout } from './FullBleedLayout';
export { MinimalLayout } from './MinimalLayout';
export { SidebarLayout } from './SidebarLayout';
export { StackedLayout } from './StackedLayout';
```

- [ ] **Step 3: Verify no type errors**

Run:
```bash
cd tools/video-generator/template && npx tsc --noEmit
```
Expected: No errors.

- [ ] **Step 4: Commit**

```bash
git add tools/video-generator/template/src/layouts/CoverArtVerticalLayout.tsx tools/video-generator/template/src/layouts/index.ts
git commit -m "feat: add CoverArtVerticalLayout for 9:16 vertical shorts"
```

---

## Task 3: Create MusicVideoShort component

**Files:**
- Create: `tools/video-generator/template/src/MusicVideoShort.tsx`

- [ ] **Step 1: Create MusicVideoShort.tsx**

Create `tools/video-generator/template/src/MusicVideoShort.tsx`. This component wraps the same audio-reactive logic as `MusicVideo.tsx` but trims audio to the clip window, rebases lyrics timestamps, and forces the vertical layout:

```tsx
import React, { useEffect, useState, useMemo, useCallback, useRef } from 'react';
import {
  AbsoluteFill,
  Audio,
  staticFile,
  useVideoConfig,
  useCurrentFrame,
  delayRender,
  continueRender,
} from 'remotion';
import { useAudioData, visualizeAudio } from '@remotion/media-utils';
import { loadDesign, getBackgroundStyle, getFontFamily, DesignConfig } from './utils/designLoader';
import {
  computeVisualizerBars,
  attackReleaseSmooth,
  extractBandEnergies,
  createEnvelopeState,
  BandEnergies,
  EnvelopeState,
} from './utils/audioUtils';
import { CoverArtVerticalLayout } from './layouts';
import type { LyricsData, LyricLine, Section } from './MusicVideo';

interface MusicVideoShortProps {
  songTitle: string;
  audioSrc: string;
  lyricsDataSrc: string;
  genre?: string;
  clipStartTime: number;
  clipEndTime: number;
}

const NUM_BARS = 24;

export const MusicVideoShort: React.FC<MusicVideoShortProps> = ({
  songTitle,
  audioSrc,
  lyricsDataSrc,
  genre = 'unknown',
  clipStartTime,
  clipEndTime,
}) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const currentTime = frame / fps;

  const [lyricsHandle] = useState(() => delayRender('Loading lyrics'));
  const [designHandle] = useState(() => delayRender('Loading design'));
  const [rawLyricsData, setRawLyricsData] = useState<LyricsData | null>(null);
  const [design, setDesign] = useState<DesignConfig | null>(null);

  const audioData = useAudioData(staticFile(audioSrc));

  // ── Rebase lyrics to clip window ──────────────────────────────────────────
  const lyricsData: LyricsData | null = useMemo(() => {
    if (!rawLyricsData) return null;

    const filteredLyrics = rawLyricsData.lyrics
      .filter(
        (line) => line.end_time > clipStartTime && line.start_time < clipEndTime
      )
      .map((line) => ({
        ...line,
        start_time: Math.max(0, line.start_time - clipStartTime),
        end_time: Math.min(clipEndTime - clipStartTime, line.end_time - clipStartTime),
        words: line.words?.map((w) => ({
          ...w,
          start_time: Math.max(0, w.start_time - clipStartTime),
          end_time: Math.min(clipEndTime - clipStartTime, w.end_time - clipStartTime),
        })),
      }));

    const filteredSections = rawLyricsData.sections
      .filter(
        (s) => s.end_time > clipStartTime && s.start_time < clipEndTime
      )
      .map((s) => ({
        ...s,
        start_time: Math.max(0, s.start_time - clipStartTime),
        end_time: Math.min(clipEndTime - clipStartTime, s.end_time - clipStartTime),
      }));

    return {
      audio_duration: clipEndTime - clipStartTime,
      sections: filteredSections,
      lyrics: filteredLyrics,
    };
  }, [rawLyricsData, clipStartTime, clipEndTime]);

  // ── Visualizer bar heights ────────────────────────────────────────────────
  const prevBarHeights = useRef<number[] | null>(null);
  const envelopeState = useRef<EnvelopeState>(createEnvelopeState(NUM_BARS));

  // We need to compute frequency data at the correct position in the audio
  // The audio is trimmed, so Remotion's frame corresponds to the trimmed position
  // but useAudioData + visualizeAudio use the untrimmed audio data.
  // We offset the frame to match the clip start position.
  const audioFrame = frame + Math.round(clipStartTime * fps);

  const barHeights: number[] = useMemo(() => {
    if (!audioData) return Array(NUM_BARS).fill(0);
    const raw = visualizeAudio({
      frame: audioFrame, fps, audioData, numberOfSamples: 64, smoothing: false,
    });
    const bars = computeVisualizerBars(raw, NUM_BARS, envelopeState.current);
    const smoothed = attackReleaseSmooth(bars, prevBarHeights.current, 0.3, 0.92);
    prevBarHeights.current = smoothed;
    return smoothed;
  }, [audioData, audioFrame, fps]);

  // ── Band energies ─────────────────────────────────────────────────────────
  const prevBands = useRef<number[] | null>(null);
  const bandEnergies: BandEnergies = useMemo(() => {
    if (!audioData) return { bass: 0, lowMid: 0, highMid: 0, highs: 0, overall: 0 };
    const raw = visualizeAudio({
      frame: audioFrame, fps, audioData, numberOfSamples: 64, smoothing: false,
    });
    const bands = extractBandEnergies(raw);
    const arr = [bands.bass, bands.lowMid, bands.highMid, bands.highs, bands.overall];
    const smoothed = attackReleaseSmooth(arr, prevBands.current, 0.12, 0.94);
    prevBands.current = smoothed;
    return {
      bass: smoothed[0], lowMid: smoothed[1], highMid: smoothed[2],
      highs: smoothed[3], overall: smoothed[4],
    };
  }, [audioData, audioFrame, fps]);

  // ── Raw frequency data ────────────────────────────────────────────────────
  const prevFreq = useRef<number[] | null>(null);
  const frequencyData = useMemo(() => {
    if (!audioData) return Array(64).fill(0);
    const raw = visualizeAudio({
      frame: audioFrame, fps, audioData, numberOfSamples: 64, smoothing: false,
    });
    const smoothed = raw.map((v, i) => {
      const prev = prevFreq.current?.[i] ?? v;
      return prev * 0.7 + v * 0.3;
    });
    prevFreq.current = smoothed;
    return smoothed;
  }, [audioData, audioFrame, fps]);

  // ── Data loading ──────────────────────────────────────────────────────────
  const loadLyrics = useCallback(async () => {
    try {
      const res = await fetch(staticFile(lyricsDataSrc));
      setRawLyricsData(await res.json());
    } catch (e) {
      console.error('Failed to load lyrics:', e);
    } finally {
      continueRender(lyricsHandle);
    }
  }, [lyricsHandle, lyricsDataSrc]);

  const loadDesignConfig = useCallback(async () => {
    setDesign(await loadDesign(staticFile));
    continueRender(designHandle);
  }, [designHandle]);

  useEffect(() => { loadLyrics(); loadDesignConfig(); }, [loadLyrics, loadDesignConfig]);

  // ── Lyrics state ──────────────────────────────────────────────────────────
  const currentLyric = useMemo(() => {
    if (!lyricsData) return null;
    return lyricsData.lyrics.find(
      (l) => currentTime >= l.start_time && currentTime < l.end_time
    ) ?? null;
  }, [lyricsData, currentTime]);

  const nextLyric = useMemo(() => {
    if (!lyricsData || !currentLyric) return null;
    const idx = lyricsData.lyrics.indexOf(currentLyric);
    return lyricsData.lyrics[idx + 1] ?? null;
  }, [lyricsData, currentLyric]);

  const currentSection = useMemo(() => {
    if (!lyricsData) return null;
    return lyricsData.sections.find(
      (s) => currentTime >= s.start_time && currentTime < s.end_time
    ) ?? null;
  }, [lyricsData, currentTime]);

  const clipDuration = clipEndTime - clipStartTime;
  const overallProgress = currentTime / clipDuration;
  const pulseOpacity = 0.3 + bandEnergies.bass * 0.4;

  const backgroundStyle = useMemo(() => {
    if (!design) return 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)';
    return getBackgroundStyle(design.palette);
  }, [design]);

  const fontFamily = useMemo(() => {
    if (!design) return '"Noto Sans Telugu", "Noto Sans", system-ui, -apple-system, sans-serif';
    return getFontFamily(design.typography.googleFont);
  }, [design]);

  // Audio trim values in frames
  const trimBeforeFrames = Math.round(clipStartTime * fps);
  const trimAfterFrames = Math.round(clipEndTime * fps);

  return (
    <AbsoluteFill style={{ background: backgroundStyle, fontFamily, overflow: 'hidden' }}>
      <Audio
        src={staticFile(audioSrc)}
        trimBefore={trimBeforeFrames}
        trimAfter={trimAfterFrames}
      />

      {design && (
        <div
          style={{
            position: 'absolute', width: '100%', height: '100%',
            background: `radial-gradient(ellipse at 50% 30%, ${design.palette.glowColor}${Math.round(pulseOpacity * 255).toString(16).padStart(2, '0')} 0%, transparent 60%)`,
            opacity: 0.6, zIndex: 0,
          }}
        />
      )}

      {design != null && (
        <CoverArtVerticalLayout
          design={design}
          frequencyData={frequencyData}
          bandEnergies={bandEnergies}
          barHeights={barHeights}
          lyricsData={lyricsData}
          currentLyric={currentLyric}
          nextLyric={nextLyric}
          currentSection={currentSection}
          currentTime={currentTime}
          overallProgress={overallProgress}
          songTitle={songTitle}
          genre={genre}
        />
      )}
    </AbsoluteFill>
  );
};
```

- [ ] **Step 2: Verify no type errors**

Run:
```bash
cd tools/video-generator/template && npx tsc --noEmit
```
Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add tools/video-generator/template/src/MusicVideoShort.tsx
git commit -m "feat: add MusicVideoShort component with audio trim and lyrics rebase"
```

---

## Task 4: Update Root.tsx to register MusicVideoShort composition

**Files:**
- Modify: `tools/video-generator/template/src/Root.tsx`

- [ ] **Step 1: Update Root.tsx**

Replace the entire contents of `tools/video-generator/template/src/Root.tsx` with:

```tsx
import { Composition } from 'remotion';
import { staticFile } from 'remotion';
import { MusicVideo } from './MusicVideo';
import { MusicVideoShort } from './MusicVideoShort';
import { useEffect, useState } from 'react';
import { delayRender, continueRender } from 'remotion';

const FPS = 30;

interface VideoConfig {
  audioDuration: number;
  songTitle: string;
  genre: string;
  short?: {
    startTime: number;
    endTime: number;
    duration: number;
  };
}

export const RemotionRoot: React.FC = () => {
  const [handle] = useState(() => delayRender('Loading video config'));
  const [config, setConfig] = useState<VideoConfig | null>(null);

  useEffect(() => {
    fetch(staticFile('video-config.json'))
      .then((r) => r.json())
      .then((data: VideoConfig) => {
        setConfig(data);
        continueRender(handle);
      })
      .catch(() => {
        setConfig({ audioDuration: 180, songTitle: 'Untitled', genre: 'unknown' });
        continueRender(handle);
      });
  }, [handle]);

  if (!config) return null;

  return (
    <>
      <Composition
        id="MusicVideo"
        component={MusicVideo}
        durationInFrames={Math.ceil(config.audioDuration * FPS)}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={{
          songTitle: config.songTitle,
          audioSrc: "audio.mp3",
          lyricsDataSrc: "lyrics-timestamps.json",
          theme: "default",
          genre: config.genre,
        }}
      />

      {config.short && (
        <Composition
          id="MusicVideoShort"
          component={MusicVideoShort}
          durationInFrames={Math.ceil(config.short.duration * FPS)}
          fps={FPS}
          width={1080}
          height={1920}
          defaultProps={{
            songTitle: config.songTitle,
            audioSrc: "audio.mp3",
            lyricsDataSrc: "lyrics-timestamps.json",
            genre: config.genre,
            clipStartTime: config.short.startTime,
            clipEndTime: config.short.endTime,
          }}
        />
      )}
    </>
  );
};
```

- [ ] **Step 2: Verify no type errors**

Run:
```bash
cd tools/video-generator/template && npx tsc --noEmit
```
Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add tools/video-generator/template/src/Root.tsx
git commit -m "feat: register MusicVideoShort composition in Root.tsx"
```

---

## Task 5: Update Step 0 prompt to collect shorts preferences

**Files:**
- Modify: `prompts/step-0-prepare-workspace.md`

- [ ] **Step 1: Add shorts inputs to the collection table**

In `prompts/step-0-prepare-workspace.md`, find the input table in section 0.1 and add two new rows:

Replace the existing table:
```markdown
| Input | Required | Default | Example |
|---|---|---|---|
| YouTube video URL | Yes | — | `https://www.youtube.com/watch?v=F-KfKbCDBIk` |
| Remix genre / style | Yes | — | `Lo-Fi`, `EDM`, `Carnatic Fusion`, `Hip-Hop` |
| Language of the song | No | Infer from video title | `Telugu`, `Hindi`, `Tamil` |
| Tempo preference | No | `medium` | `slow`, `medium`, `energetic` |
| Song length preference | No | `full` | `full`, `shortened` |
```

With:
```markdown
| Input | Required | Default | Example |
|---|---|---|---|
| YouTube video URL | Yes | — | `https://www.youtube.com/watch?v=F-KfKbCDBIk` |
| Remix genre / style | Yes | — | `Lo-Fi`, `EDM`, `Carnatic Fusion`, `Hip-Hop` |
| Language of the song | No | Infer from video title | `Telugu`, `Hindi`, `Tamil` |
| Tempo preference | No | `medium` | `slow`, `medium`, `energetic` |
| Song length preference | No | `full` | `full`, `shortened` |
| Short clip selection | No | `auto` | `auto` (best segment), `manual` (present choices) |
| Short clip duration | No | `30` | `15`, `30`, `60` (seconds) |
```

- [ ] **Step 2: Add shorts fields to meta.json template**

In the same file, find the `meta.json` template in section 0.5. Add the shorts fields.

After the `"song_length"` field, add:
```json
  "shorts_clip_mode": "<auto or manual>",
  "shorts_duration": <duration in seconds>,
```

Add to the `"status"` block:
```json
    "shorts_clip_selected": false,
    "short_video_generated": false,
```

Add to the `"files"` block:
```json
    "shorts_segments": null,
    "short_video": null
```

- [ ] **Step 3: Commit**

```bash
git add prompts/step-0-prepare-workspace.md
git commit -m "feat: add shorts preferences to Step 0 input collection"
```

---

## Task 6: Create Step 10 prompt — Select Short Clip

**Files:**
- Create: `prompts/step-10-select-short-clip.md`

- [ ] **Step 1: Write the step prompt**

Create `prompts/step-10-select-short-clip.md`:

```markdown
# Step 10: Select Short Clip

## Objective

Analyze the remix audio and lyrics timestamps to identify the most engaging segment for a
YouTube Short. By default, auto-select the best segment. If the user opted into manual mode
during Step 0, present candidates for selection.

## Prerequisites

- `workspaces/<slug>/<slug>-remix-v1.mp3` exists (or selected remix variant)
- `workspaces/<slug>/lyrics-timestamps.json` exists (produced in Step 6)
- `workspaces/<slug>/meta.json` exists with `shorts_clip_mode` and `shorts_duration`

**See also**: [Workspace Conventions](references/workspace-conventions.md) for file naming.

---

## Instructions

### 10.1 — Read Workspace State

Read `meta.json` and extract:
- `shorts_clip_mode` (default: `"auto"`)
- `shorts_duration` (default: `30`)
- `slug`
- Selected remix file path

Read `lyrics-timestamps.json` and extract all sections with their start/end times.

---

### 10.2 — Analyze Audio Energy

Run FFmpeg EBU R128 loudness analysis on the remix audio:

```bash
ffmpeg -i workspaces/<slug>/<slug>-remix-v1.mp3 -af ebur128 -f null - 2>&1
```

Parse the output to extract per-second loudness values. If `ffmpeg ebur128` fails, skip energy
analysis and rely solely on section metadata (Step 10.3).

---

### 10.3 — Generate Candidate Segments

For each section in `lyrics-timestamps.json`, generate a candidate segment:

1. If the section duration matches the target duration (within ±5s), use the section as-is
2. If the section is longer, find the loudest contiguous window of target duration within it
3. If the section is shorter, extend to include adjacent sections up to target duration

**Scoring heuristic:**

| Factor | Score |
|---|---|
| Section is Chorus | +10 |
| Section is Verse | +5 |
| Section is Bridge/Outro/Intro | +3 |
| Energy bonus (normalized EBU R128 loudness, 0-5 scale) | +0 to +5 |
| Segment starts/ends on section boundary | +1 |

Sort candidates by score descending. Keep top 5.

---

### 10.4 — Select Segment

**If `shorts_clip_mode == "auto"` (default):**

Select the highest-scoring candidate. Log the selection and continue to Step 11.

```
Auto-selected short clip segment:
  Section  : Chorus 1
  Time     : 45.2s - 75.2s (30.0s)
  Score    : 14.2
  Lyrics   : 8 lines

Proceeding to Step 11: Generate Short Video...
```

**If `shorts_clip_mode == "manual"`:**

Present all candidates to the user:

```
Short clip candidates for <slug>:

  1. Chorus 1    (45.2s - 75.2s)   Score: 14.2   8 lyrics lines
  2. Chorus 2    (120.5s - 150.5s) Score: 13.8   8 lyrics lines
  3. Verse 2     (60.0s - 90.0s)   Score: 9.5    6 lyrics lines
  4. Bridge      (100.0s - 130.0s) Score: 8.2    4 lyrics lines
  5. Intro+Verse (0.0s - 30.0s)    Score: 7.1    5 lyrics lines

Which segment? (1-5, or specify custom start time):
```

Wait for user selection before proceeding.

---

### 10.5 — Write shorts-segments.json

Save the analysis results:

**File path:** `workspaces/<slug>/shorts-segments.json`

```json
{
  "selected": {
    "start_time": 45.2,
    "end_time": 75.2,
    "duration": 30,
    "section": "Chorus 1",
    "score": 14.2,
    "lyrics_line_start": 12,
    "lyrics_line_end": 20
  },
  "candidates": [
    { "start_time": 45.2, "end_time": 75.2, "section": "Chorus 1", "score": 14.2 },
    { "start_time": 120.5, "end_time": 150.5, "section": "Chorus 2", "score": 13.8 },
    { "start_time": 0, "end_time": 30, "section": "Intro + Verse 1", "score": 7.1 }
  ],
  "config": {
    "duration": 30,
    "auto_selected": true
  }
}
```

---

### 10.6 — Update video-config.json

Merge the short clip config into the existing `video-config.json` in the Remotion project:

```bash
# Read existing video-config.json, add "short" key, write back
```

The result should look like:

```json
{
  "audioDuration": 210.5,
  "songTitle": "Meesaala Pilla",
  "genre": "Lo-Fi",
  "short": {
    "startTime": 45.2,
    "endTime": 75.2,
    "duration": 30
  }
}
```

---

### 10.7 — Update meta.json

```json
{
  "status": { "shorts_clip_selected": true },
  "files": { "shorts_segments": "workspaces/<slug>/shorts-segments.json" }
}
```

---

## Error Handling

**See**: [Error Handling Patterns](references/error-handling-patterns.md) for detailed fixes.

| Error | Solution |
|---|---|
| No chorus detected in lyrics | Fall back to loudest 30s window from FFmpeg analysis |
| All sections shorter than target duration | Merge adjacent sections to reach target |
| `ffmpeg ebur128` fails | Skip energy scoring, use section-type scoring only |
| `lyrics-timestamps.json` has no sections | Use sliding window on raw lyrics with energy scoring |
| Selected segment has no lyrics | Acceptable — short renders with visualizer only |

---

## Reference

- [Workspace Conventions](references/workspace-conventions.md) — File naming
- [Error Handling Patterns](references/error-handling-patterns.md) — Common errors
```

- [ ] **Step 2: Commit**

```bash
git add prompts/step-10-select-short-clip.md
git commit -m "feat: add Step 10 prompt for short clip selection"
```

---

## Task 7: Create Step 11 prompt — Generate Short Video

**Files:**
- Create: `prompts/step-11-generate-short-video.md`

- [ ] **Step 1: Write the step prompt**

Create `prompts/step-11-generate-short-video.md`:

```markdown
# Step 11: Generate Short Video

## Objective

Render a 9:16 vertical music video (YouTube Short) from the selected clip segment using the
existing Remotion project. The short reuses the same audio, cover art, design, and lyrics data
from the full video — no re-scaffolding required.

## Key Requirements

- **Vertical format**: 1080x1920 (9:16) — YouTube Shorts / Instagram Reels
- **Clip duration**: Uses the segment selected in Step 10 (default 30s)
- **Audio trimming**: Remotion's native `trimBefore`/`trimAfter` on `<Audio>`
- **Lyrics sync**: Only lyrics within the clip window, timestamps rebased to start at 0
- **Same visuals**: Same design.json palette, motifs, audio-reactive effects, typography
- **Cover art**: Same `cover-art.jpg` from Step 7

## Prerequisites

- `workspaces/<slug>/shorts-segments.json` exists (produced in Step 10)
- `workspaces/<slug>/video/` exists (Remotion project from Step 8)
- `workspaces/<slug>/video/public/audio.mp3` exists
- `workspaces/<slug>/video/public/lyrics-timestamps.json` exists
- `workspaces/<slug>/video/public/cover-art.jpg` exists
- `workspaces/<slug>/video/public/video-config.json` includes `short` config

**See also**: Load the `remotion-best-practices` skill when working on this step.

---

## Instructions

### 11.1 — Verify Prerequisites

Read `workspaces/<slug>/video/public/video-config.json` and verify the `short` key exists:

```json
{
  "short": {
    "startTime": 45.2,
    "endTime": 75.2,
    "duration": 30
  }
}
```

If missing, read `shorts-segments.json` and merge the selected segment into `video-config.json`.

---

### 11.2 — Verify Template Has Short Components

Check that the Remotion project has the required components:
- `src/MusicVideoShort.tsx` exists
- `src/layouts/CoverArtVerticalLayout.tsx` exists

If missing (older scaffolded project), copy them from the template:

```bash
cp tools/video-generator/template/src/MusicVideoShort.tsx workspaces/<slug>/video/src/
cp tools/video-generator/template/src/layouts/CoverArtVerticalLayout.tsx workspaces/<slug>/video/src/layouts/
```

Also update `src/layouts/index.ts` and `src/Root.tsx` if needed to include the new exports and
composition registration.

---

### 11.3 — Render Short Video

```bash
cd workspaces/<slug>/video
npx remotion render MusicVideoShort out/short.mp4
```

Expected: Renders a 1080x1920 video of the clip duration. Typical render time: 15-30 seconds
for a 30-second clip.

---

### 11.4 — Copy Output to Workspace

```bash
cp workspaces/<slug>/video/out/short.mp4 workspaces/<slug>/<slug>-short.mp4
```

---

### 11.5 — Update meta.json

```json
{
  "status": { "short_video_generated": true },
  "files": { "short_video": "workspaces/<slug>/<slug>-short.mp4" }
}
```

---

### 11.6 — Present Results

```
Short video generation complete!

Output: workspaces/<slug>/<slug>-short.mp4
  Format   : 1080x1920 (9:16 vertical)
  Duration : <duration>s
  Segment  : <section name> (<start>s - <end>s)
  Lyrics   : <n> lines synced
  Layout   : cover-art-vertical

Ready for YouTube Shorts / Instagram Reels upload.
```

---

## Error Handling

**See**: [Error Handling Patterns](references/error-handling-patterns.md) for detailed fixes.

| Problem | Fix |
|---|---|
| `MusicVideoShort` composition not found | Verify `Root.tsx` has the composition and `video-config.json` has `short` key |
| Black frames at start/end | Check `trimBefore`/`trimAfter` values are in frames (multiply seconds by fps) |
| No lyrics visible | Verify lyrics fall within `[clipStartTime, clipEndTime]` window |
| Cover art not showing | Same fix as Step 8 — ensure `cover-art.jpg` is in `video/public/` |
| Audio plays wrong segment | Verify `video-config.json` `short.startTime` and `short.endTime` match `shorts-segments.json` |
| Render fails with "composition not found" | The `short` key must exist in `video-config.json` for the composition to register |
| Template missing short components | Copy from `tools/video-generator/template/src/` (see Step 11.2) |

---

## Reference

- [Workspace Conventions](references/workspace-conventions.md) — File naming
- [Error Handling Patterns](references/error-handling-patterns.md) — Common errors
- Load `remotion-best-practices` skill for Remotion-specific guidance
```

- [ ] **Step 2: Commit**

```bash
git add prompts/step-11-generate-short-video.md
git commit -m "feat: add Step 11 prompt for short video generation"
```

---

## Task 8: Update pipeline documentation

**Files:**
- Modify: `prompts/README.md`
- Modify: `prompts/references/workspace-conventions.md`
- Modify: `docs/intent.md`

- [ ] **Step 1: Update prompts/README.md**

Add Steps 10 and 11 to the pipeline table. Find the existing table and add after the Step 9 row:

```markdown
| 10 | `step-10-select-short-clip.md` | Analyze audio + lyrics, select best clip segment | `shorts-segments.json` | Step 9 |
| 11 | `step-11-generate-short-video.md` | Render 9:16 vertical short in existing Remotion project | `<slug>-short.mp4` | Step 10 |
```

Update the sequential execution note:
```markdown
- **Sequential execution**: Steps must run 0→1→2→3→4→5→6→7→8→9→10→11
```

- [ ] **Step 2: Update prompts/references/workspace-conventions.md**

Add the new files to the directory structure listing. After the `youtube-metadata-artifact.md` line, add:

```markdown
    ├── shorts-segments.json            ← Clip segment candidates + selection
    └── <slug>-short.mp4                ← Rendered vertical short video (1080x1920)
```

Add to the Purpose Suffixes table:

```markdown
| `short` | Rendered vertical short video |
```

Add to the meta.json schema — new top-level fields after `"song_length"`:

```json
  "shorts_clip_mode": "auto",
  "shorts_duration": 30,
```

Add to `"status"` block:

```json
    "shorts_clip_selected": false,
    "short_video_generated": false,
```

Add to `"files"` block:

```json
    "shorts_segments": null,
    "short_video": null
```

- [ ] **Step 3: Update docs/intent.md**

Add Steps 10 and 11 to the pipeline overview diagram. After the Step 8 line, add:

```markdown
[Step 9] Generate YouTube Metadata  →  youtube-metadata.json
        |
        v
[Step 10] Select Short Clip  →  shorts-segments.json (auto or manual)
        |
        v
[Step 11] Generate Short Video  →  <slug>-short.mp4 (1080x1920 vertical)
```

Add to the workspace structure listing:

```markdown
    <slug>-short.mp4          # Rendered vertical short video (Step 11)
    shorts-segments.json      # Clip segment analysis (Step 10)
```

Add Step 10 and 11 descriptions in the Detailed Steps section:

```markdown
### Step 10: Select Short Clip

- Analyze lyrics-timestamps.json sections (Chorus, Verse, Bridge) and FFmpeg EBU R128 loudness
- Score candidate segments: Chorus +10, Verse +5, Bridge +3, plus energy bonus 0-5
- Auto-select highest-scoring segment (default) or present candidates if user opted into manual mode
- Save analysis to `shorts-segments.json` and merge clip config into `video-config.json`

### Step 11: Generate Short Video

- Render 9:16 vertical video using existing Remotion project's `MusicVideoShort` composition
- Audio trimmed via Remotion's native `trimBefore`/`trimAfter`
- Lyrics filtered and rebased to clip window (timestamps start at 0)
- Uses `CoverArtVerticalLayout`: cover art top 60%, lyrics middle 30%, visualizer bottom 10%
- Same design.json palette, motifs, and audio-reactive effects as full video
- Save as `<slug>-short.mp4`
```

Add to the Prompts Folder listing:

```markdown
- `step-10-select-short-clip.md` — Analyze audio and lyrics to select best short clip segment
- `step-11-generate-short-video.md` — Render 9:16 vertical short video using Remotion
```

- [ ] **Step 4: Commit**

```bash
git add prompts/README.md prompts/references/workspace-conventions.md docs/intent.md
git commit -m "docs: add Steps 10 & 11 to pipeline documentation"
```

---

## Task 9: Final verification

- [ ] **Step 1: Verify all template TypeScript compiles**

Run:
```bash
cd tools/video-generator/template && npx tsc --noEmit
```
Expected: No errors.

- [ ] **Step 2: Verify all new files exist**

Run:
```bash
ls -la tools/video-generator/template/src/MusicVideoShort.tsx
ls -la tools/video-generator/template/src/layouts/CoverArtVerticalLayout.tsx
ls -la prompts/step-10-select-short-clip.md
ls -la prompts/step-11-generate-short-video.md
```
Expected: All files exist.

- [ ] **Step 3: Verify documentation consistency**

Check that `prompts/README.md` lists Steps 10 and 11, `docs/intent.md` includes the new steps
in the pipeline diagram, and `workspace-conventions.md` includes `shorts-segments.json` and
`<slug>-short.mp4` in the directory structure.

- [ ] **Step 4: Final commit (if any remaining changes)**

```bash
git status
# If clean, nothing to do. If any stragglers:
git add -A && git commit -m "chore: final cleanup for shorts generation feature"
```
