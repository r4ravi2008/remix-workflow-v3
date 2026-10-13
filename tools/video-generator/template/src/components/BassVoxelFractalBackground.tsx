import React from 'react';
import {useCurrentFrame} from 'remotion';
import type {DesignConfig} from '../utils/designLoader';
import {getBassResponse} from '../utils/bassResponse';

interface BassVoxelFractalBackgroundProps {
  design: DesignConfig;
  frequencyData: number[];
  width?: number;
  height?: number;
}

type BlueprintVoxel = {
  id: number;
  parentId: number | null;
  cluster: number;
  gx: number;
  gy: number;
  gz: number;
  scale: number;
  depth: number;
  colorIndex: number;
};

type RenderVoxel = BlueprintVoxel & {
  x: number;
  y: number;
  size: number;
  extrusion: number;
  opacity: number;
};

const FPS = 30;
const hash = (value: number) => {
  const sine = Math.sin(value * 12.9898 + 78.233) * 43758.5453;
  return sine - Math.floor(sine);
};

const CLUSTERS = [
  {x: 0.015, y: 0.20, phase: 0.4},
  {x: 0.34, y: 0.035, phase: 1.8},
  {x: 0.70, y: 0.21, phase: 3.2},
  {x: 0.12, y: 0.82, phase: 4.7},
  {x: 0.59, y: 0.84, phase: 5.6},
];

const buildBlueprint = (): BlueprintVoxel[] => {
  const voxels: BlueprintVoxel[] = [];
  let nextId = 0;
  const add = (
    cluster: number,
    parentId: number | null,
    gx: number,
    gy: number,
    gz: number,
    scale: number,
    depth: number,
    branchSeed: number,
  ) => {
    const id = nextId++;
    voxels.push({
      id,
      parentId,
      cluster,
      gx,
      gy,
      gz,
      scale,
      depth,
      colorIndex: Math.floor(hash(branchSeed * 9.17 + cluster * 3.1) * 4),
    });
    if (depth >= 2) return;

    const directions = [
      [1, 0, 1],
      [-1, 0, 0],
      [0, 1, 1],
      [0, -1, 0],
    ];
    const branchCount = depth === 0 ? 4 : 2;
    const start = Math.floor(hash(branchSeed * 5.31) * directions.length);
    for (let branch = 0; branch < branchCount; branch++) {
      const direction = directions[(start + branch) % directions.length];
      const distance = depth === 0 ? 1.0 : 0.82;
      add(
        cluster,
        id,
        gx + direction[0] * distance,
        gy + direction[1] * distance,
        gz + direction[2] * distance,
        scale * 0.58,
        depth + 1,
        branchSeed * 1.73 + branch * 7.11,
      );
    }
  };

  CLUSTERS.forEach((_, cluster) => add(cluster, null, 0, 0, 0, 1, 0, cluster + 1.37));
  return voxels;
};

const BLUEPRINT = buildBlueprint();

const withAlpha = (hex: string, alpha: number) => {
  const clean = hex.replace('#', '').slice(0, 6);
  const safe = clean.length === 6 ? clean : 'ffffff';
  return `#${safe}${Math.round(Math.max(0, Math.min(1, alpha)) * 255).toString(16).padStart(2, '0')}`;
};

export const BassVoxelFractalBackground: React.FC<BassVoxelFractalBackgroundProps> = ({
  design,
  frequencyData,
  width = 1920,
  height = 1080,
}) => {
  const frame = useCurrentFrame();
  const time = frame / FPS;
  const {level: bassLevel, kick: bassKick} = getBassResponse(design, frequencyData);
  const colors = [
    design.palette.secondaryColor,
    design.palette.primaryColor,
    design.palette.highlightColor,
    design.palette.accentColor,
  ];

  const renderVoxels: RenderVoxel[] = BLUEPRINT.map((voxel) => {
    const cluster = CLUSTERS[voxel.cluster];
    const driftX = Math.sin(time * 0.16 + cluster.phase) * 18;
    const driftY = Math.cos(time * 0.13 + cluster.phase * 0.83) * 14;
    const anchorX = cluster.x * width + driftX;
    const anchorY = cluster.y * height + driftY;
    // The whole hierarchy inhales and exhales with the eased bass level.
    // Kick adds only the final expansion, avoiding a binary threshold jump.
    const spread = 62 * (0.78 + bassLevel * 0.42 + bassKick * 0.20);
    const isoX = (voxel.gx - voxel.gy) * spread;
    const isoY = (voxel.gx + voxel.gy) * spread * 0.48 - voxel.gz * spread * 0.76;
    const radialX = cluster.x - 0.39;
    const radialY = cluster.y - 0.48;
    const radialLength = Math.max(0.001, Math.hypot(radialX, radialY));
    const hitOffset = bassKick * (36 + hash(voxel.cluster * 11.9) * 48);
    const depthFade = 1 - voxel.depth * 0.16;
    return {
      ...voxel,
      x: anchorX + isoX + radialX / radialLength * hitOffset,
      y: anchorY + isoY + radialY / radialLength * hitOffset,
      size: 42 * voxel.scale * (1 + bassLevel * 0.20),
      extrusion: 13 + voxel.scale * 19 + bassKick * (13 + voxel.depth * 4),
      opacity: (0.26 + bassLevel * 0.62) * depthFade,
    };
  }).sort((left, right) => left.y - right.y || left.depth - right.depth);

  const byId = new Map(renderVoxels.map((voxel) => [voxel.id, voxel]));

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      style={{
        position: 'absolute',
        inset: 0,
        width,
        height,
        pointerEvents: 'none',
        overflow: 'hidden',
        mixBlendMode: 'screen',
        contain: 'strict',
        maskImage: 'linear-gradient(90deg, black 0%, black 68%, rgba(0,0,0,.58) 80%, rgba(0,0,0,.10) 100%)',
        WebkitMaskImage: 'linear-gradient(90deg, black 0%, black 68%, rgba(0,0,0,.58) 80%, rgba(0,0,0,.10) 100%)',
      }}
    >
      <g opacity={0.22 + bassLevel * 0.38}>
        {renderVoxels.map((voxel) => {
          const parent = voxel.parentId === null ? null : byId.get(voxel.parentId);
          if (!parent) return null;
          return (
            <line
              key={`edge-${voxel.id}`}
              x1={parent.x}
              y1={parent.y}
              x2={voxel.x}
              y2={voxel.y}
              stroke={colors[voxel.colorIndex]}
              strokeWidth={1.1 + bassKick * 1.3}
            />
          );
        })}
      </g>

      {renderVoxels.map((voxel) => {
        const color = colors[voxel.colorIndex];
        const halfWidth = voxel.size;
        const halfHeight = voxel.size * 0.48;
        const topY = voxel.y - voxel.extrusion;
        const top = `${voxel.x},${topY - halfHeight} ${voxel.x + halfWidth},${topY} ${voxel.x},${topY + halfHeight} ${voxel.x - halfWidth},${topY}`;
        const left = `${voxel.x - halfWidth},${topY} ${voxel.x},${topY + halfHeight} ${voxel.x},${voxel.y + halfHeight} ${voxel.x - halfWidth},${voxel.y}`;
        const right = `${voxel.x + halfWidth},${topY} ${voxel.x},${topY + halfHeight} ${voxel.x},${voxel.y + halfHeight} ${voxel.x + halfWidth},${voxel.y}`;
        return (
          <g key={voxel.id} opacity={voxel.opacity}>
            <polygon points={left} fill={withAlpha(design.palette.highlightColor, 0.26)} stroke={withAlpha(color, 0.68)} strokeWidth={1.15} />
            <polygon points={right} fill={withAlpha(design.palette.secondaryColor, 0.18)} stroke={withAlpha(color, 0.74)} strokeWidth={1.15} />
            <polygon points={top} fill={withAlpha(color, 0.34)} stroke={withAlpha(design.palette.primaryColor, 0.72 + bassKick * 0.22)} strokeWidth={1.2 + bassKick * 1.0} />
          </g>
        );
      })}
    </svg>
  );
};
