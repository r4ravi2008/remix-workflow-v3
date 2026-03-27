import React, { useEffect, useState, useMemo, useCallback } from 'react';
import {
  AbsoluteFill,
  Audio,
  staticFile,
  useVideoConfig,
  useCurrentFrame,
  interpolate,
  Easing,
  delayRender,
  continueRender,
} from 'remotion';

interface Word {
  text: string;
  start_time: number;
  end_time: number;
}

interface LyricLine {
  text: string;
  start_time: number;
  end_time: number;
  section: string;
  words?: Word[];
}

interface Section {
  name: string;
  start_time: number;
  end_time: number;
  lines: string[];
}

interface LyricsData {
  audio_duration: number;
  sections: Section[];
  lyrics: LyricLine[];
}

interface MusicVideoProps {
  songTitle: string;
  audioSrc: string;
  lyricsDataSrc: string;
  theme?: string;
  genre?: string;
}

const themes: Record<string, {
  background: string;
  primaryColor: string;
  secondaryColor?: string;
  accentColor: string;
  highlightColor?: string;
  sectionBackground?: string;
}> = {
  lofi: {
    background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
    primaryColor: '#e8e8e8',
    secondaryColor: '#b8b8b8',
    accentColor: '#74b9ff',
    highlightColor: '#ff7675',
    sectionBackground: 'rgba(116, 185, 255, 0.15)',
  },
  chill: {
    background: 'linear-gradient(135deg, #a8e6cf 0%, #dcedc1 100%)',
    primaryColor: '#2d3436',
    accentColor: '#ff8b94',
    highlightColor: '#e17055',
    sectionBackground: 'rgba(255, 139, 148, 0.15)',
  },
  edm: {
    background: 'linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 100%)',
    primaryColor: '#ffffff',
    accentColor: '#00d2ff',
    highlightColor: '#a29bfe',
    sectionBackground: 'rgba(0, 210, 255, 0.1)',
  },
  hiphop: {
    background: 'linear-gradient(135deg, #1a1a1a 0%, #4a4a4a 100%)',
    primaryColor: '#f1f1f1',
    accentColor: '#ff6b35',
    highlightColor: '#fdcb6e',
    sectionBackground: 'rgba(255, 107, 53, 0.1)',
  },
  carnatic: {
    background: 'linear-gradient(135deg, #c9a961 0%, #8b7355 100%)',
    primaryColor: '#2c2416',
    accentColor: '#d4af37',
    highlightColor: '#8b4513',
    sectionBackground: 'rgba(212, 175, 55, 0.15)',
  },
  pop: {
    background: 'linear-gradient(135deg, #ff6b6b 0%, #feca57 50%, #48dbfb 100%)',
    primaryColor: '#2d3436',
    accentColor: '#ff9ff3',
    highlightColor: '#6c5ce7',
    sectionBackground: 'rgba(255, 159, 243, 0.15)',
  },
  default: {
    background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
    primaryColor: '#ffffff',
    secondaryColor: '#b2bec3',
    accentColor: '#74b9ff',
    highlightColor: '#ff7675',
    sectionBackground: 'rgba(116, 185, 255, 0.15)',
  },
};

export const MusicVideo: React.FC<MusicVideoProps> = ({
  songTitle,
  audioSrc,
  lyricsDataSrc,
  theme = 'default',
  genre = 'unknown',
}) => {
  const { durationInFrames, fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const currentTime = frame / fps;

  // delayRender pauses each frame capture until data is loaded.
  // Without this, async fetch completes after the frame is captured → no lyrics rendered.
  const [handle] = useState(() => delayRender('Loading lyrics'));
  const [lyricsData, setLyricsData] = useState<LyricsData | null>(null);

  const currentTheme = themes[theme] || themes.default;

  const loadLyrics = useCallback(async () => {
    try {
      const response = await fetch(staticFile(lyricsDataSrc));
      const data = await response.json();
      setLyricsData(data);
    } catch (error) {
      console.error('Failed to load lyrics:', error);
    } finally {
      continueRender(handle);
    }
  }, [handle, lyricsDataSrc]);

  useEffect(() => { loadLyrics(); }, [loadLyrics]);

  // Active lyric line
  const currentLyric = useMemo(() => {
    if (!lyricsData) return null;
    return lyricsData.lyrics.find(
      line => currentTime >= line.start_time && currentTime < line.end_time
    ) ?? null;
  }, [lyricsData, currentTime]);

  // Next lyric (preview)
  const nextLyric = useMemo(() => {
    if (!lyricsData || !currentLyric) return null;
    const idx = lyricsData.lyrics.indexOf(currentLyric);
    return lyricsData.lyrics[idx + 1] ?? null;
  }, [lyricsData, currentLyric]);

  // Active section
  const currentSection = useMemo(() => {
    if (!lyricsData) return null;
    return lyricsData.sections.find(
      s => currentTime >= s.start_time && currentTime < s.end_time
    ) ?? null;
  }, [lyricsData, currentTime]);

  // Fade-in animation for each new lyric line
  const lineProgress = useMemo(() => {
    if (!currentLyric) return 0;
    const duration = currentLyric.end_time - currentLyric.start_time;
    return Math.min((currentTime - currentLyric.start_time) / duration, 1);
  }, [currentLyric, currentTime]);

  const fadeIn = interpolate(lineProgress, [0, 0.15], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Ambient pulse
  const pulseOpacity = interpolate(frame % 60, [0, 30, 60], [0.3, 0.5, 0.3], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Overall progress
  const overallProgress = lyricsData
    ? currentTime / lyricsData.audio_duration
    : frame / durationInFrames;

  return (
    <AbsoluteFill
      style={{
        background: currentTheme.background,
        fontFamily: '"Noto Sans Telugu", "Noto Sans", system-ui, -apple-system, sans-serif',
        overflow: 'hidden',
      }}
    >
      <Audio src={staticFile(audioSrc)} />

      {/* Ambient background glow */}
      <div
        style={{
          position: 'absolute',
          width: '100%',
          height: '100%',
          background: `radial-gradient(ellipse at 50% 30%, ${currentTheme.accentColor}${Math.round(pulseOpacity * 255).toString(16).padStart(2, '0')} 0%, transparent 60%)`,
          opacity: 0.6,
        }}
      />

      {/* Main layout */}
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
          zIndex: 1,
        }}
      >
        {/* Section badge */}
        <div
          style={{
            padding: '12px 32px',
            background: currentTheme.sectionBackground ?? 'rgba(255,255,255,0.1)',
            borderRadius: 100,
            border: `2px solid ${currentTheme.accentColor}40`,
            backdropFilter: 'blur(10px)',
          }}
        >
          <span
            style={{
              color: currentTheme.accentColor,
              fontSize: 18,
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.15em',
            }}
          >
            {currentSection ? currentSection.name : '♪'}
          </span>
        </div>

        {/* Lyrics display */}
        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            width: '100%',
            maxWidth: 1200,
          }}
        >
          {/* Active line */}
          <div
            style={{
              textAlign: 'center',
              opacity: fadeIn,
              transform: `translateY(${(1 - fadeIn) * 20}px)`,
            }}
          >
            <h1
              style={{
                color: currentTheme.highlightColor ?? currentTheme.accentColor,
                fontSize: 80,
                fontWeight: 700,
                margin: 0,
                lineHeight: 1.3,
                textShadow: `0 4px 30px ${currentTheme.highlightColor ?? currentTheme.accentColor}50`,
                letterSpacing: '0.02em',
              }}
            >
              {currentLyric ? currentLyric.text : '♪'}
            </h1>
          </div>

          {/* Next line preview */}
          {nextLyric && (
            <div style={{ marginTop: 40, textAlign: 'center', opacity: 0.35 }}>
              <p
                style={{
                  color: currentTheme.secondaryColor ?? currentTheme.primaryColor,
                  fontSize: 48,
                  fontWeight: 400,
                  margin: 0,
                  lineHeight: 1.4,
                }}
              >
                {nextLyric.text}
              </p>
            </div>
          )}
        </div>

        {/* Bottom: visualizer + progress + title */}
        <div
          style={{
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 24,
          }}
        >
          {/* Visualizer bars */}
          <div style={{ display: 'flex', gap: 6, alignItems: 'flex-end', height: 80 }}>
            {[...Array(16)].map((_, i) => {
              const barHeight = interpolate(
                (frame + i * 3) % 45,
                [0, 22.5, 45],
                [30, 100, 30],
                { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
              );
              return (
                <div
                  key={i}
                  style={{
                    width: 10,
                    height: `${barHeight}%`,
                    background: `linear-gradient(to top, ${currentTheme.accentColor}, ${currentTheme.highlightColor ?? currentTheme.accentColor})`,
                    borderRadius: 5,
                    opacity: 0.8,
                  }}
                />
              );
            })}
          </div>

          {/* Progress bar */}
          <div
            style={{
              width: '60%',
              maxWidth: 600,
              height: 6,
              background: `${currentTheme.primaryColor}15`,
              borderRadius: 3,
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                width: `${overallProgress * 100}%`,
                height: '100%',
                background: `linear-gradient(to right, ${currentTheme.accentColor}, ${currentTheme.highlightColor ?? currentTheme.accentColor})`,
                borderRadius: 3,
              }}
            />
          </div>

          {/* Song info */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginTop: 4 }}>
            <span style={{ color: currentTheme.primaryColor, fontSize: 20, fontWeight: 600 }}>
              {songTitle}
            </span>
            <span
              style={{
                color: currentTheme.accentColor,
                fontSize: 16,
                fontWeight: 500,
                padding: '6px 16px',
                background: `${currentTheme.accentColor}15`,
                borderRadius: 100,
              }}
            >
              {genre}
            </span>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
