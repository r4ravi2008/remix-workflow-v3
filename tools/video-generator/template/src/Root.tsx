import { Composition } from 'remotion';
import { MusicVideo } from './MusicVideo';

// Populated by init-video.js from ffprobe output on the remix audio file.
const AUDIO_DURATION_SECONDS = {{AUDIO_DURATION}};
const FPS = 30;
const DURATION_IN_FRAMES = Math.ceil(AUDIO_DURATION_SECONDS * FPS);

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MusicVideo"
        component={MusicVideo}
        durationInFrames={DURATION_IN_FRAMES}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={{
          songTitle: "{{SONG_TITLE}}",
          audioSrc: "audio.mp3",
          lyricsDataSrc: "lyrics-timestamps.json",
          theme: "default",
          genre: "{{GENRE}}",
        }}
      />
    </>
  );
};
