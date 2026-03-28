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
  BandEnergies,
} from './utils/audioUtils';
import {
  CenterStageLayout,
  CoverArtLayout,
  FullBleedLayout,
  MinimalLayout,
  SidebarLayout,
  StackedLayout,
} from './layouts';

// ─── Data types ──────────────────────────────────────────────────────────────

export interface Word {
  text: string;
  start_time: number;
  end_time: number;
}

export interface LyricLine {
  text: string;
  start_time: number;
  end_time: number;
  section: string;
  words?: Word[];
}

export interface Section {
  name: string;
  start_time: number;
  end_time: number;
  lines: string[];
}

export interface LyricsData {
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

// ─── Constants ───────────────────────────────────────────────────────────────

const NUM_BARS = 24; // total bars, upward-only (no mirror)

// ─── Component ───────────────────────────────────────────────────────────────

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

  // Async loading handles
  const [lyricsHandle] = useState(() => delayRender('Loading lyrics'));
  const [designHandle] = useState(() => delayRender('Loading design'));
  const [lyricsData, setLyricsData] = useState<LyricsData | null>(null);
  const [design, setDesign] = useState<DesignConfig | null>(null);

  // Audio data
  const audioData = useAudioData(staticFile(audioSrc));

  // ── Visualizer bar heights (per-bar attack/release smoothing) ──────────
  const prevBarHeights = useRef<number[] | null>(null);

  const barHeights: number[] = useMemo(() => {
    if (!audioData) return Array(NUM_BARS).fill(0);

    const raw = visualizeAudio({
      frame, fps, audioData, numberOfSamples: 64, smoothing: false,
    });

    // dB + A-weight + log-bin → 24 bars, no mirroring
    const bars = computeVisualizerBars(raw, NUM_BARS);

    // Heavy smoothing: slow attack (0.5), very slow release (0.992 ≈ 5× slower than before)
    const smoothed = attackReleaseSmooth(bars, prevBarHeights.current, 0.5, 0.992);
    prevBarHeights.current = smoothed;

    return smoothed;
  }, [audioData, frame, fps]);

  // ── Band energies (for motifs + background pulse) ──────────────────────
  const prevBands = useRef<number[] | null>(null);

  const bandEnergies: BandEnergies = useMemo(() => {
    if (!audioData) return { bass: 0, lowMid: 0, highMid: 0, highs: 0, overall: 0 };

    const raw = visualizeAudio({
      frame, fps, audioData, numberOfSamples: 64, smoothing: false,
    });
    const bands = extractBandEnergies(raw);
    const arr = [bands.bass, bands.lowMid, bands.highMid, bands.highs, bands.overall];
    const smoothed = attackReleaseSmooth(arr, prevBands.current, 0.12, 0.94);
    prevBands.current = smoothed;

    return {
      bass: smoothed[0], lowMid: smoothed[1], highMid: smoothed[2],
      highs: smoothed[3], overall: smoothed[4],
    };
  }, [audioData, frame, fps]);

  // ── Raw frequency data for motif components ────────────────────────────
  const prevFreq = useRef<number[] | null>(null);
  const frequencyData = useMemo(() => {
    if (!audioData) return Array(64).fill(0);
    const raw = visualizeAudio({
      frame, fps, audioData, numberOfSamples: 64, smoothing: false,
    });
    const smoothed = raw.map((v, i) => {
      const prev = prevFreq.current?.[i] ?? v;
      return prev * 0.7 + v * 0.3;
    });
    prevFreq.current = smoothed;
    return smoothed;
  }, [audioData, frame, fps]);

  // ── Data loading ───────────────────────────────────────────────────────
  const loadLyrics = useCallback(async () => {
    try {
      const res = await fetch(staticFile(lyricsDataSrc));
      setLyricsData(await res.json());
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

  // ── Lyrics state ───────────────────────────────────────────────────────
  const currentLyric = useMemo(() => {
    if (!lyricsData) return null;
    return lyricsData.lyrics.find(
      l => currentTime >= l.start_time && currentTime < l.end_time
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
      s => currentTime >= s.start_time && currentTime < s.end_time
    ) ?? null;
  }, [lyricsData, currentTime]);

  const overallProgress = lyricsData
    ? currentTime / lyricsData.audio_duration
    : frame / durationInFrames;

  const pulseOpacity = 0.3 + bandEnergies.bass * 0.4;

  // ── Layout rendering ──────────────────────────────────────────────────
  const renderLayout = () => {
    const props = {
      design: design!,
      frequencyData,
      bandEnergies,
      barHeights,
      lyricsData,
      currentLyric,
      nextLyric,
      currentSection,
      currentTime,
      overallProgress,
      songTitle,
      genre,
    };

    switch (design?.layout.variant || 'cover-art') {
      case 'center-stage': return <CenterStageLayout {...props} />;
      case 'full-bleed':   return <FullBleedLayout {...props} />;
      case 'minimal':      return <MinimalLayout {...props} />;
      case 'sidebar':      return <SidebarLayout {...props} />;
      case 'stacked':      return <StackedLayout {...props} />;
      default:             return <CoverArtLayout {...props} />;
    }
  };

  const backgroundStyle = useMemo(() => {
    if (!design) return 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)';
    return getBackgroundStyle(design.palette);
  }, [design]);

  const fontFamily = useMemo(() => {
    if (!design) return '"Noto Sans Telugu", "Noto Sans", system-ui, -apple-system, sans-serif';
    return getFontFamily(design.typography.googleFont);
  }, [design]);

  return (
    <AbsoluteFill style={{ background: backgroundStyle, fontFamily, overflow: 'hidden' }}>
      <Audio src={staticFile(audioSrc)} />

      {design && (
        <div
          style={{
            position: 'absolute', width: '100%', height: '100%',
            background: `radial-gradient(ellipse at 50% 30%, ${design.palette.glowColor}${Math.round(pulseOpacity * 255).toString(16).padStart(2, '0')} 0%, transparent 60%)`,
            opacity: 0.6, zIndex: 0,
          }}
        />
      )}

      {design != null && renderLayout()}
    </AbsoluteFill>
  );
};
