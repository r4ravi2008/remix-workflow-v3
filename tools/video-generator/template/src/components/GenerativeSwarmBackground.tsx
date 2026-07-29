import React from 'react';
import {useCurrentFrame} from 'remotion';
import type {DesignConfig} from '../utils/designLoader';
import {getBassResponse} from '../utils/bassResponse';

interface GenerativeSwarmBackgroundProps {
  design: DesignConfig;
  frequencyData: number[];
  width?: number;
  height?: number;
}

type Agent = {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  color: string;
  rebelStrength: number;
};

const FPS = 30;
const smoothstep = (edge0: number, edge1: number, value: number) => {
  const amount = Math.max(0, Math.min(1, (value - edge0) / Math.max(0.0001, edge1 - edge0)));
  return amount * amount * (3 - 2 * amount);
};
const hash = (value: number) => {
  const sine = Math.sin(value * 12.9898 + 78.233) * 43758.5453;
  return sine - Math.floor(sine);
};

const FAMILY_ANCHORS = [
  {x: 0.16, y: 0.22},
  {x: 0.46, y: 0.18},
  {x: 0.72, y: 0.41},
  {x: 0.34, y: 0.68},
];

/**
 * A deterministic, frame-addressable vector swarm. Unlike a stateful
 * canvas simulation it renders correctly when Remotion requests frames out of
 * order. Bass alone drives radial pressure and smooth outer-agent detachments;
 * the angular field keeps moving independently between hits. Every pigment
 * color comes from design.json.
 */
export const GenerativeSwarmBackground: React.FC<GenerativeSwarmBackgroundProps> = ({
  design,
  frequencyData,
  width = 1440,
  height = 1080,
}) => {
  const frame = useCurrentFrame();
  const time = frame / FPS;
  const intensity = design.motif.intensity === 'high' ? 1 : design.motif.intensity === 'low' ? 0.68 : 0.84;
  const agentCount = design.motif.intensity === 'high' ? 52 : design.motif.intensity === 'low' ? 30 : 42;
  const {level: bassLevel, kick: bassKick} = getBassResponse(design, frequencyData);
  const palette = [
    design.palette.secondaryColor,
    design.palette.primaryColor,
    design.palette.highlightColor,
    design.palette.accentColor,
  ];

  const positionAt = (id: number, at: number) => {
    const family = id % 4;
    const anchor = FAMILY_ANCHORS[family];
    const phase = hash(id * 7.31 + design.seed * 0.013) * Math.PI * 2;
    const direction = hash(id * 3.17) > 0.5 ? 1 : -1;
    const exchange = 0.5 + 0.5 * Math.sin(at * (0.16 + hash(id * 5.7) * 0.11) + phase * 0.7);
    const nextAnchor = FAMILY_ANCHORS[(family + 1 + (id % 2)) % 4];
    const exchangeAmount = Math.pow(exchange, 7) * 0.11;
    const centerX = (
      anchor.x + Math.sin(at * (0.12 + family * 0.013) + phase) * 0.045
    ) * (1 - exchangeAmount) + nextAnchor.x * exchangeAmount;
    const centerY = (
      anchor.y + Math.cos(at * (0.10 + family * 0.017) + phase * 0.83) * 0.039
    ) * (1 - exchangeAmount) + nextAnchor.y * exchangeAmount;
    const theta = phase + direction * at * (0.24 + hash(id * 11.9) * 0.22)
      + Math.sin(at * 0.19 + phase) * 0.42;
    const radiusX = 0.042 + hash(id * 2.9) * 0.075;
    const radiusY = 0.038 + hash(id * 4.1) * 0.062;
    const curlX = Math.sin(theta * 2.7 + at * 0.23 + family) * 0.016;
    const curlY = Math.cos(theta * 2.2 - at * 0.18 + family) * 0.015;

    // Only agents already near an archipelago's outside edge can rebel.
    // The burst phase changes slowly so the group always re-establishes a new
    // outside edge instead of permanently tagging a fixed set of agents.
    const outerAgent = hash(id * 17.23 + family * 5.1) > 0.73;
    const burstPhase = (at * (0.38 + hash(id * 1.37) * 0.14) + hash(id * 31.7)) % 1;
    const burstEnvelope = 0.5 - Math.cos(burstPhase * Math.PI * 2) * 0.5;
    const selectionPosition = at * 0.42;
    const selectionEpoch = Math.floor(selectionPosition);
    const selectionMix = smoothstep(0, 1, selectionPosition - selectionEpoch);
    const selectedNow = hash(id * 29.13 + selectionEpoch * 7.7) > 0.82 ? 1 : 0;
    const selectedNext = hash(id * 29.13 + (selectionEpoch + 1) * 7.7) > 0.82 ? 1 : 0;
    const selectionStrength = selectedNow * (1 - selectionMix) + selectedNext * selectionMix;
    const rebelStrength = outerAgent ? selectionStrength * bassKick * burstEnvelope : 0;
    const detach = rebelStrength * (0.025 + hash(id * 19.4) * 0.032);

    const localX = Math.cos(theta) * radiusX + curlX;
    const localY = Math.sin(theta * 1.13) * radiusY + curlY;
    const localLength = Math.max(0.001, Math.hypot(localX, localY));
    const tangent = (hash(id * 43.2) - 0.5) * detach * 0.55;
    const baseX = centerX + localX + localX / localLength * detach - localY / localLength * tangent;
    const baseY = centerY + localY + localY / localLength * detach + localX / localLength * tangent;
    const pulseX = baseX - 0.39;
    const pulseY = baseY - 0.47;
    const pulseLength = Math.max(0.001, Math.hypot(pulseX, pulseY));
    const radialPressure = bassKick * (0.026 + hash(id * 61.7) * 0.034);
    return {
      x: (baseX + pulseX / pulseLength * radialPressure) * width,
      y: (baseY + pulseY / pulseLength * radialPressure) * height,
      rebelStrength,
    };
  };

  const agents: Agent[] = Array.from({length: agentCount}, (_, id) => {
    const current = positionAt(id, time);
    const previous = positionAt(id, time - 1 / FPS);
    const family = id % 4;
    const colorRoll = hash(id * 13.37 + design.seed);
    const colorIndex = colorRoll < 0.46 ? 0 : colorRoll < 0.68 ? 1 : colorRoll < 0.86 ? 2 : 3;
    return {
      id,
      x: current.x,
      y: current.y,
      vx: current.x - previous.x,
      vy: current.y - previous.y,
      color: palette[colorIndex],
      rebelStrength: current.rebelStrength,
    };
  });

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
        transform: 'none',
        transformOrigin: '0 0',
        contain: 'strict',
        opacity: intensity,
        maskImage: 'linear-gradient(90deg, black 0%, black 68%, rgba(0,0,0,.62) 79%, rgba(0,0,0,.12) 100%)',
        WebkitMaskImage: 'linear-gradient(90deg, black 0%, black 68%, rgba(0,0,0,.62) 79%, rgba(0,0,0,.12) 100%)',
      }}
    >
      <defs>
        <filter id="swarm-vector-glow" x="-100%" y="-100%" width="300%" height="300%">
          <feGaussianBlur stdDeviation="3" />
        </filter>
      </defs>

      {agents.map((agent) => {
        const angle = Math.atan2(agent.vy, agent.vx) * 180 / Math.PI;
        const length = 12 + hash(agent.id * 11.23) * 18 + bassKick * 54 + agent.rebelStrength * 24;
        const weight = 1.1 + hash(agent.id * 5.7) * 1.1 + bassKick * 2.4;
        const head = 3.2 + bassKick * 4.5;
        const luminosity = 0.18 + bassLevel * 0.82;
        const railOffset = 3.5 + hash(agent.id * 17.9) * 2.5;
        return (
          <g key={agent.id} transform={`translate(${agent.x} ${agent.y}) rotate(${angle})`}>
            <line
              x1={-length}
              y1={0}
              x2={head * 0.6}
              y2={0}
              stroke={agent.color}
              strokeWidth={weight * 4.2}
              strokeLinecap="square"
              opacity={0.025 + bassKick * 0.16}
              filter="url(#swarm-vector-glow)"
            />
            <line
              x1={-length}
              y1={0}
              x2={head * 0.4}
              y2={0}
              stroke={agent.color}
              strokeWidth={weight}
              strokeLinecap="square"
              opacity={luminosity}
            />
            <line
              x1={-length * 0.62}
              y1={railOffset}
              x2={-length * 0.12}
              y2={railOffset}
              stroke={agent.color}
              strokeWidth={Math.max(0.8, weight * 0.62)}
              strokeLinecap="square"
              opacity={(0.18 + agent.rebelStrength * 0.62) * luminosity}
            />
            <polygon
              points={`${head},0 0,${head * 0.58} ${-head * 0.55},0 0,${-head * 0.58}`}
              fill={agent.id % 5 === 0 ? design.palette.primaryColor : agent.color}
              opacity={0.30 + bassLevel * 0.70}
            />
          </g>
        );
      })}
    </svg>
  );
};
