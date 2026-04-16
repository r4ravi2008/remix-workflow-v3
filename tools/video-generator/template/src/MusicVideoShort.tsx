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

// ─── Data types ──────────────────────────────────────────────────────────────

interface MusicVideoShortProps {
  songTitle: string;
  audioSrc: string;
  lyricsDataSrc: string;
  genre?: string;
  clipStartTime: number;
  clipEndTime: number;
}

// ─── Constants ───────────────────────────────────────────────────────────────

const NUM_BARS = 24;
const FPS = 30;

// ─── Component ───────────────────────────────────────────────────────────────

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
  
  // Audio frame offset: Since audio is trimmed but useAudioData uses full audio,
  // we need to offset the frame when computing frequency data
  const audioFrame = frame + Math.round(clipStartTime * fps);
  
  // Current time within the clip (starts at 0)
  const currentTime = frame / fps;
  const clipDuration = clipEndTime - clipStartTime;

  // Async loading handles
  const [lyricsHandle] = useState(() => delayRender('Loading lyrics'));
  const [designHandle] = useState(() => delayRender('Loading design'));
  const [lyricsData, setLyricsData] = useState<LyricsData | null>(null);
  const [design, setDesign] = useState<DesignConfig | null>(null);

  // Audio data (uses full audio - trim is applied at render time)
  const audioData = useAudioData(staticFile(audioSrc));

  // ── Visualizer bar heights (per-bar attack/release smoothing) ──────────
  const prevBarHeights = useRef<number[] | null>(null);
  const envelopeState = useRef<EnvelopeState>(createEnvelopeState(NUM_BARS));

  const barHeights: number[] = useMemo(() => {
    if (!audioData) return Array(NUM_BARS).fill(0);

    const raw = visualizeAudio({
      frame: audioFrame, fps, audioData, numberOfSamples: 64, smoothing: false,
    });

    // Log-bin → dB → adaptive per-band normalization → 24 bars
    const bars = computeVisualizerBars(raw, NUM_BARS, envelopeState.current);

    // Snappy attack (0.3), moderate release (0.92) for more dynamic response
    const smoothed = attackReleaseSmooth(bars, prevBarHeights.current, 0.3, 0.92);
    prevBarHeights.current = smoothed;

    return smoothed;
  }, [audioData, audioFrame, fps]);

  // ── Band energies (for motifs + background pulse) ──────────────────────
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

  // ── Raw frequency data for motif components ────────────────────────────
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

  // ── Data loading ───────────────────────────────────────────────────────
  const loadLyrics = useCallback(async () => {
    try {
      const res = await fetch(staticFile(lyricsDataSrc));
      const rawLyricsData: LyricsData = await res.json();
      
      // Rebase lyrics: filter to clip window and subtract clipStartTime from timestamps
      const filteredLyrics: LyricLine[] = rawLyricsData.lyrics
        .filter(line => line.end_time > clipStartTime && line.start_time < clipEndTime)
        .map(line => ({
          ...line,
          start_time: Math.max(0, line.start_time - clipStartTime),
          end_time: Math.min(clipEndTime - clipStartTime, line.end_time - clipStartTime),
        }));
      
      // Filter sections similarly
      const filteredSections: Section[] = rawLyricsData.sections
        .filter(section => section.end_time > clipStartTime && section.start_time < clipEndTime)
        .map(section => ({
          ...section,
          start_time: Math.max(0, section.start_time - clipStartTime),
          end_time: Math.min(clipEndTime - clipStartTime, section.end_time - clipStartTime),
        }));
      
      setLyricsData({
        ...rawLyricsData,
        lyrics: filteredLyrics,
        sections: filteredSections,
        audio_duration: clipDuration,
      });
    } catch (e) {
      console.error('Failed to load lyrics:', e);
    } finally {
      continueRender(lyricsHandle);
    }
  }, [lyricsHandle, lyricsDataSrc, clipStartTime, clipEndTime, clipDuration]);

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

  const overallProgress = clipDuration > 0 ? currentTime / clipDuration : 0;

  const pulseOpacity = 0.3 + bandEnergies.bass * 0.4;

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
      {/* Audio with trimBefore and trimAfter (in frames, not seconds) */}
      <Audio
        src={staticFile(audioSrc)}
        trimBefore={Math.round(clipStartTime * fps)}
        trimAfter={Math.round(clipEndTime * fps)}
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

      {/* Directly render CoverArtVerticalLayout for shorts (bypass layout switch) */}
      {design != null && lyricsData != null && (
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
