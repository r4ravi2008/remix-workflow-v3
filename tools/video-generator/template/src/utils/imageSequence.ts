export interface ImageSequenceFrame {
  id: string;
  image_path: string;
  source_timestamp: number;
  start_time: number;
  end_time: number;
  transition?: 'crossfade' | string;
}

export interface ImageSequence {
  version: number;
  source?: {
    video?: string;
    selection?: string;
    requested_count?: number;
  };
  frames: ImageSequenceFrame[];
}

function isValidFrame(frame: unknown): frame is ImageSequenceFrame {
  if (typeof frame !== 'object' || frame == null) return false;
  const candidate = frame as Partial<ImageSequenceFrame>;

  return typeof candidate.id === 'string'
    && typeof candidate.image_path === 'string'
    && typeof candidate.source_timestamp === 'number'
    && Number.isFinite(candidate.source_timestamp)
    && typeof candidate.start_time === 'number'
    && Number.isFinite(candidate.start_time)
    && typeof candidate.end_time === 'number'
    && Number.isFinite(candidate.end_time)
    && candidate.end_time > candidate.start_time;
}

export function validateImageSequence(value: unknown): ImageSequence | null {
  if (typeof value !== 'object' || value == null) return null;
  const raw = value as {version?: unknown; source?: ImageSequence['source']; frames?: unknown};
  if (raw.version !== 1 || !Array.isArray(raw.frames)) return null;

  const frames = raw.frames
    .filter(isValidFrame)
    .sort((a, b) => a.start_time - b.start_time);

  if (frames.length === 0) return null;

  return {
    version: 1,
    source: raw.source,
    frames,
  };
}

export async function loadImageSequence(staticFileFn: (path: string) => string): Promise<ImageSequence | null> {
  try {
    const response = await fetch(staticFileFn('image-sequence.json'));
    if (!response.ok) return null;
    return validateImageSequence(await response.json());
  } catch {
    return null;
  }
}
