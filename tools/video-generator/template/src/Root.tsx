import { Composition } from 'remotion';
import { staticFile } from 'remotion';
import { MusicVideo } from './MusicVideo';
import { useEffect, useState } from 'react';
import { delayRender, continueRender } from 'remotion';

const FPS = 30;

interface VideoConfig {
  audioDuration: number;
  songTitle: string;
  genre: string;
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
        // Fallback defaults for local dev
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
    </>
  );
};
