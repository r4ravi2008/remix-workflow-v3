import React, { useMemo } from 'react';
import { fillTextBox, fitText } from '@remotion/layout-utils';
import { Video } from '@remotion/media';
import { staticFile, useVideoConfig } from 'remotion';
import { FrequencyBarsVisualizer } from '../components';
import type { DesignConfig } from '../utils/designLoader';
import { getFontFamily } from '../utils/designLoader';
import type { LyricLine } from '../MusicVideo';

type ResolveVerticalLayoutProps = {
  design: DesignConfig;
  barHeights: number[];
  currentLyric: LyricLine | null;
  overallProgress: number;
  videoSrc: string;
  videoTrimBeforeSeconds: number;
};

const PICTURE_HEIGHT = 1536;
const LYRIC_HEIGHT = 192;
const EQUALIZER_HEIGHT = 192;
const LYRIC_WIDTH = 960;
const MAX_LYRIC_FONT_SIZE = 54;
const MIN_MOBILE_LYRIC_FONT_SIZE = 30;

const fitLyricToTwoLines = ({
  text,
  fontFamily,
  fontWeight,
}: {
  text: string;
  fontFamily: string;
  fontWeight: number;
}) => {
  const words = text.split(/\s+/).filter(Boolean);
  for (let fontSize = MAX_LYRIC_FONT_SIZE; fontSize >= MIN_MOBILE_LYRIC_FONT_SIZE; fontSize -= 1) {
    const box = fillTextBox({ maxBoxWidth: LYRIC_WIDTH, maxLines: 2 });
    const exceedsTwoLines = words.some((word) => box.add({
      text: `${word} `,
      fontFamily,
      fontSize,
      fontWeight,
    }).exceedsBox);
    if (!exceedsTwoLines) return fontSize;
  }

  // Preserve the complete lyric even when it cannot meet the preferred mobile
  // minimum. The visual review gate must then split the timed lyric into a
  // shorter phrase instead of shipping clipped text.
  return Math.min(MIN_MOBILE_LYRIC_FONT_SIZE, fitText({
    text,
    withinWidth: LYRIC_WIDTH,
    fontFamily,
    fontWeight,
  }).fontSize);
};

export const ResolveVerticalLayout: React.FC<ResolveVerticalLayoutProps> = ({
  design,
  barHeights,
  currentLyric,
  overallProgress,
  videoSrc,
  videoTrimBeforeSeconds,
}) => {
  const { fps } = useVideoConfig();
  const lyricText = currentLyric?.text.trim() ?? '';
  const fontFamily = getFontFamily(design.typography.googleFont);
  const lyricFontSize = useMemo(() => {
    if (!lyricText) return MAX_LYRIC_FONT_SIZE;
    return fitLyricToTwoLines({
      text: lyricText,
      fontFamily,
      fontWeight: design.typography.mainLyricWeight,
    });
  }, [design.typography.mainLyricWeight, fontFamily, lyricText]);

  const trimBefore = Math.round(videoTrimBeforeSeconds * fps);
  const videoStyle: React.CSSProperties = {
    position: 'absolute',
    inset: 0,
    width: '100%',
    height: '100%',
  };

  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div
        data-layout-band="picture-80"
        style={{
          width: '100%',
          height: PICTURE_HEIGHT,
          position: 'relative',
          overflow: 'hidden',
          background: '#050507',
        }}
      >
        <Video
          src={staticFile(videoSrc)}
          trimBefore={trimBefore}
          muted
          style={{
            ...videoStyle,
            objectFit: 'cover',
            filter: 'blur(32px) saturate(1.08) brightness(0.52)',
            transform: 'scale(1.08)',
          }}
        />
        <Video
          src={staticFile(videoSrc)}
          trimBefore={trimBefore}
          muted
          style={{ ...videoStyle, objectFit: 'contain' }}
        />
      </div>

      <div
        data-layout-band="lyrics-10"
        style={{
          width: '100%',
          height: LYRIC_HEIGHT,
          boxSizing: 'border-box',
          padding: '18px 60px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
          background: 'rgba(5, 5, 7, 0.92)',
        }}
      >
        <p
          style={{
            width: LYRIC_WIDTH,
            margin: 0,
            color: design.palette.highlightColor,
            fontFamily,
            fontSize: lyricFontSize,
            fontWeight: design.typography.mainLyricWeight,
            fontStyle: design.typography.mainLyricItalic ? 'italic' : 'normal',
            letterSpacing: design.typography.letterSpacing,
            lineHeight: 1.15,
            textAlign: 'center',
            textShadow: '0 2px 8px rgba(0,0,0,0.75)',
            display: '-webkit-box',
            WebkitBoxOrient: 'vertical',
            WebkitLineClamp: 2,
            overflow: 'hidden',
            overflowWrap: 'anywhere',
          }}
        >
          {lyricText || '\u266b'}
        </p>
      </div>

      <div
        data-layout-band="equalizer-10"
        style={{
          width: '100%',
          height: EQUALIZER_HEIGHT,
          boxSizing: 'border-box',
          padding: '14px 40px 18px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 12,
          background: '#050507',
        }}
      >
        <FrequencyBarsVisualizer
          design={design}
          barHeights={barHeights}
          width={1000}
          height={104}
        />
        {design.layout.showProgressBar && (
          <div
            style={{
              width: '78%',
              height: 4,
              overflow: 'hidden',
              borderRadius: 100,
              background: `${design.palette.primaryColor}18`,
            }}
          >
            <div
              style={{
                width: `${Math.max(0, Math.min(1, overallProgress)) * 100}%`,
                height: '100%',
                borderRadius: 100,
                background: `linear-gradient(90deg, ${design.palette.accentColor}, ${design.palette.highlightColor})`,
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
};
