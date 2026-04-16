/**
 * Design loader - loads and validates design.json
 */

export interface DesignPalette {
  backgroundType: 'gradient' | 'mesh-gradient' | 'solid' | 'dark-noise';
  backgroundStops: Array<{ color: string; position: string }>;
  backgroundAngle: number;
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  highlightColor: string;
  glowColor: string;
}

export interface DesignTypography {
  googleFont: string;
  mainLyricSize: number;
  mainLyricWeight: number;
  mainLyricItalic: boolean;
  letterSpacing: string;
  textEffect: 'glow' | 'shadow' | 'outline' | 'none';
  sectionBadgeStyle: 'pill' | 'box' | 'minimal';
}

export interface DesignLayout {
  variant: 'cover-art' | 'cover-art-vertical' | 'center-stage' | 'full-bleed' | 'minimal' | 'sidebar' | 'stacked';
  showSectionBadge: boolean;
  showNextLyric: boolean;
  showProgressBar: boolean;
  visualizerPosition: 'bottom' | 'top' | 'hidden';
}

export interface DesignMotif {
  primary: 'particles' | 'geometric-burst' | 'aurora' | 'waveform-rings' | 'frequency-bars-only' | 'noise-field';
  secondary: string | null;
  intensity: 'low' | 'medium' | 'high';
}

export interface DesignAnimation {
  personality: 'smooth' | 'bouncy' | 'sharp' | 'dreamy' | 'aggressive';
  lyricEntrance: 'fade' | 'slide-up' | 'scale-in' | 'glitch' | 'word-by-word';
  beatReactivity: number;
}

export interface DesignConfig {
  palette: DesignPalette;
  typography: DesignTypography;
  layout: DesignLayout;
  motif: DesignMotif;
  animation: DesignAnimation;
  seed: number;
}

/**
 * Load design.json from the public folder
 */
export async function loadDesign(staticFileFn: (path: string) => string): Promise<DesignConfig> {
  try {
    const response = await fetch(staticFileFn('design.json'));
    if (!response.ok) {
      console.warn('design.json not found, using defaults');
      return validateDesign({});
    }
    const design = await response.json();
    return validateDesign(design);
  } catch (error) {
    console.warn('Failed to load design.json, using defaults:', error);
    return validateDesign({});
  }
}

/**
 * Validate and fill in defaults for design config
 */
function validateDesign(design: Partial<DesignConfig>): DesignConfig {
  return {
    palette: {
      backgroundType: design.palette?.backgroundType || 'gradient',
      backgroundStops: design.palette?.backgroundStops || [
        { color: '#1a1a2e', position: '0%' },
        { color: '#16213e', position: '100%' },
      ],
      backgroundAngle: design.palette?.backgroundAngle || 135,
      primaryColor: design.palette?.primaryColor || '#ffffff',
      secondaryColor: design.palette?.secondaryColor || '#b2bec3',
      accentColor: design.palette?.accentColor || '#74b9ff',
      highlightColor: design.palette?.highlightColor || '#ff7675',
      glowColor: design.palette?.glowColor || '#74b9ff40',
    },
    typography: {
      googleFont: design.typography?.googleFont || 'Noto Sans',
      mainLyricSize: design.typography?.mainLyricSize || 80,
      mainLyricWeight: design.typography?.mainLyricWeight || 700,
      mainLyricItalic: design.typography?.mainLyricItalic || false,
      letterSpacing: design.typography?.letterSpacing || '0.02em',
      textEffect: design.typography?.textEffect || 'glow',
      sectionBadgeStyle: design.typography?.sectionBadgeStyle || 'pill',
    },
    layout: {
      variant: design.layout?.variant || 'cover-art',
      showSectionBadge: design.layout?.showSectionBadge ?? true,
      showNextLyric: design.layout?.showNextLyric ?? true,
      showProgressBar: design.layout?.showProgressBar ?? true,
      visualizerPosition: design.layout?.visualizerPosition || 'bottom',
    },
    motif: {
      primary: design.motif?.primary || 'particles',
      secondary: design.motif?.secondary || null,
      intensity: design.motif?.intensity || 'medium',
    },
    animation: {
      personality: design.animation?.personality || 'smooth',
      lyricEntrance: design.animation?.lyricEntrance || 'slide-up',
      beatReactivity: design.animation?.beatReactivity ?? 0.8,
    },
    seed: design.seed || 12345,
  };
}

/**
 * Get CSS background string from palette
 */
export function getBackgroundStyle(palette: DesignPalette): string {
  if (palette.backgroundType === 'solid') {
    return palette.backgroundStops[0]?.color || '#1a1a2e';
  }

  const stops = palette.backgroundStops
    .map((stop) => `${stop.color} ${stop.position}`)
    .join(', ');

  return `linear-gradient(${palette.backgroundAngle}deg, ${stops})`;
}

/**
 * Get font family string with fallbacks
 */
export function getFontFamily(googleFont: string): string {
  const safeFont = googleFont.replace(/\s+/g, '+');
  // Always include Noto Sans for Indic script support
  return `"${googleFont}", "Noto Sans Telugu", "Noto Sans", system-ui, -apple-system, sans-serif`;
}

/**
 * Get easing function for animation personality
 */
export function getEasing(personality: DesignAnimation['personality']) {
  switch (personality) {
    case 'smooth':
      return [0.4, 0, 0.2, 1];
    case 'bouncy':
      return [0.68, -0.55, 0.265, 1.55];
    case 'sharp':
      return [0, 0, 1, 1]; // linear
    case 'dreamy':
      return [0.8, 0, 0.2, 1];
    case 'aggressive':
      return [0.9, 0, 0.1, 1];
    default:
      return [0.4, 0, 0.2, 1];
  }
}
