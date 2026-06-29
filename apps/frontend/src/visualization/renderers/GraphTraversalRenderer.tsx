/**
 * GraphTraversalRenderer — upgraded SVG visualization for graph/tree algorithms.
 *
 * Phase 4.4 additions:
 *   - Zoom + pan  (scroll wheel zooms toward cursor; drag to pan; dbl-click resets)
 *   - Smooth CSS transitions on edge/node color changes
 *   - Directed arrowheads (color-matched per edge state)
 *   - Path overlay (cyan line on state.path edges)
 *   - Perpendicular edge-weight labels (never overlaps the line)
 *
 * Node colors:  amber=current · green=visited · indigo=frontier · neutral=undiscovered
 * Edge colors:  cyan=path · amber=current · green=visited · indigo=frontier · neutral
 */

import { useCallback, useMemo, useRef, useState } from 'react';
import type { RendererProps } from '../RendererRegistry';

// ── Domain types ──────────────────────────────────────────────────────────────

interface GraphNode {
  node_id: string;
  label: string;
  x: number;
  y: number;
  weight: number | null;
}

interface GraphEdge {
  edge_id: string;
  source: string;
  target: string;
  weight: number | null;
  directed: boolean;
}

interface GraphState {
  nodes: GraphNode[];
  edges: GraphEdge[];
  visited: string[];
  frontier: string[];
  current: string | null;
  distances: Record<string, number | null>;
  path: string[];
  description: string;
}

// ── Layout constants ──────────────────────────────────────────────────────────

const VW = 600;
const VH = 400;
const PAD = 44;
const NODE_R = 18;
const INNER_W = VW - PAD * 2;
const INNER_H = VH - PAD * 2;

// ── Palette ───────────────────────────────────────────────────────────────────

const C = {
  current:       { fill: '#fbbf24', stroke: '#f59e0b', text: '#1c1917' },
  visited:       { fill: '#22c55e', stroke: '#16a34a', text: '#052e16' },
  frontier:      { fill: '#818cf8', stroke: '#6366f1', text: '#1e1b4b' },
  undiscovered:  { fill: '#1c1c1c', stroke: '#525252', text: '#9ca3af' },
  pathEdge:      '#22d3ee',
  edgeCurrent:   '#d97706',
  edgeVisited:   '#166534',
  edgeFrontier:  '#4338ca',
  edgeDefault:   '#3f3f46',
  bg:            '#0f0f0f',
};

type MarkerKey = 'path' | 'current' | 'visited' | 'frontier' | 'default';
const MARKER_FILL: Record<MarkerKey, string> = {
  path:     C.pathEdge,
  current:  C.edgeCurrent,
  visited:  C.edgeVisited,
  frontier: C.edgeFrontier,
  default:  C.edgeDefault,
};

// ── Color helpers ─────────────────────────────────────────────────────────────

function getNodeColors(nodeId: string, state: GraphState) {
  if (state.current === nodeId)                    return C.current;
  if ((state.visited ?? []).includes(nodeId))      return C.visited;
  if ((state.frontier ?? []).includes(nodeId))     return C.frontier;
  return C.undiscovered;
}

function getEdgeStyle(
  edge: GraphEdge,
  state: GraphState,
  pathEdgeSet: Set<string>,
): { color: string; width: number; markerKey: MarkerKey } {
  const { source: s, target: t } = edge;

  if (pathEdgeSet.has(`${s}|${t}`) || pathEdgeSet.has(`${t}|${s}`)) {
    return { color: C.pathEdge, width: 3.5, markerKey: 'path' };
  }

  const srcC = state.current === s;
  const tgtC = state.current === t;
  const srcV = (state.visited ?? []).includes(s);
  const tgtV = (state.visited ?? []).includes(t);
  const srcF = (state.frontier ?? []).includes(s);
  const tgtF = (state.frontier ?? []).includes(t);

  if (srcC || tgtC)                                   return { color: C.edgeCurrent,  width: 2.5, markerKey: 'current'  };
  if (srcV && tgtV)                                   return { color: C.edgeVisited,  width: 2,   markerKey: 'visited'  };
  if ((srcV && tgtF) || (tgtV && srcF))               return { color: C.edgeFrontier, width: 1.5, markerKey: 'frontier' };
  return                                                     { color: C.edgeDefault,  width: 1.5, markerKey: 'default'  };
}

function toSvg(node: GraphNode) {
  return { cx: PAD + node.x * INNER_W, cy: PAD + node.y * INNER_H };
}

// ── Zoom/pan hook ─────────────────────────────────────────────────────────────

interface Vb { x: number; y: number; w: number; h: number }
const DEFAULT_VB: Vb = { x: 0, y: 0, w: VW, h: VH };

function useViewBox() {
  const [vb, setVb] = useState<Vb>(DEFAULT_VB);
  const svgRef = useRef<SVGSVGElement>(null);
  const drag   = useRef({ active: false, lastX: 0, lastY: 0 });

  const handleWheel = useCallback((e: React.WheelEvent<SVGSVGElement>) => {
    e.preventDefault();
    const svg = svgRef.current;
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    setVb((v) => {
      const factor = e.deltaY > 0 ? 1.12 : 0.89;
      const newW = Math.max(80, Math.min(VW * 5, v.w * factor));
      const newH = newW * (VH / VW);
      const vbMx = v.x + (mx / rect.width)  * v.w;
      const vbMy = v.y + (my / rect.height) * v.h;
      return { x: vbMx - (mx / rect.width) * newW, y: vbMy - (my / rect.height) * newH, w: newW, h: newH };
    });
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    drag.current = { active: true, lastX: e.clientX, lastY: e.clientY };
  }, []);

  const handleMouseMove = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    if (!drag.current.active) return;
    const svg = svgRef.current;
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    setVb((v) => {
      const dx = (e.clientX - drag.current.lastX) * (v.w / rect.width);
      const dy = (e.clientY - drag.current.lastY) * (v.h / rect.height);
      drag.current.lastX = e.clientX;
      drag.current.lastY = e.clientY;
      return { ...v, x: v.x - dx, y: v.y - dy };
    });
  }, []);

  const stopDrag    = useCallback(() => { drag.current.active = false; }, []);
  const reset       = useCallback(() => setVb(DEFAULT_VB), []);
  const isZoomed    = vb.w !== DEFAULT_VB.w || vb.x !== DEFAULT_VB.x || vb.y !== DEFAULT_VB.y;
  const vbString    = `${vb.x.toFixed(1)} ${vb.y.toFixed(1)} ${vb.w.toFixed(1)} ${vb.h.toFixed(1)}`;

  return { svgRef, vbString, isZoomed, reset, handleWheel, handleMouseDown, handleMouseMove, stopDrag };
}

// ── SVG defs (arrow markers + glow filters) ───────────────────────────────────

function ArrowMarkers() {
  return (
    <defs>
      {(Object.entries(MARKER_FILL) as [MarkerKey, string][]).map(([key, fill]) => (
        <marker
          key={key}
          id={`arr-${key}`}
          markerWidth="8" markerHeight="8"
          refX="6" refY="3"
          orient="auto"
        >
          <path d="M0,0.5 L0,5.5 L7,3 z" fill={fill} />
        </marker>
      ))}
      {/* Glow filters for each node state */}
      <filter id="glow-current" x="-60%" y="-60%" width="220%" height="220%">
        <feGaussianBlur stdDeviation="5" result="blur" />
        <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
      </filter>
      <filter id="glow-visited" x="-40%" y="-40%" width="180%" height="180%">
        <feGaussianBlur stdDeviation="3" result="blur" />
        <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
      </filter>
      <filter id="glow-frontier" x="-40%" y="-40%" width="180%" height="180%">
        <feGaussianBlur stdDeviation="3" result="blur" />
        <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
      </filter>
    </defs>
  );
}

// ── Edge SVG element ──────────────────────────────────────────────────────────

interface EdgeProps {
  edge: GraphEdge;
  x1: number; y1: number;
  x2: number; y2: number;
  color: string;
  width: number;
  markerKey: MarkerKey;
}

function EdgeEl({ edge, x1, y1, x2, y2, color, width, markerKey }: EdgeProps) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const len = Math.sqrt(dx * dx + dy * dy) || 1;

  // Shorten directed edges so the arrowhead clears the target node circle
  const gap = edge.directed ? NODE_R + 6 : 0;
  const ex  = x2 - (dx / len) * gap;
  const ey  = y2 - (dy / len) * gap;

  // Weight label: perpendicular offset so it never sits on the line
  const perpX = (-dy / len) * 11;
  const perpY = ( dx / len) * 11;
  const lx = (x1 + x2) / 2 + perpX;
  const ly = (y1 + y2) / 2 + perpY;

  return (
    <g>
      <line
        x1={x1} y1={y1} x2={ex} y2={ey}
        stroke={color}
        strokeWidth={width}
        strokeLinecap="round"
        markerEnd={edge.directed ? `url(#arr-${markerKey})` : undefined}
        style={{ transition: 'stroke 0.22s ease, stroke-width 0.18s ease' }}
      />
      {edge.weight != null && (
        <text
          x={lx} y={ly}
          textAnchor="middle" dominantBaseline="central"
          fill={color}
          fontSize={9}
          fontFamily="ui-monospace, monospace"
          fontWeight="600"
          style={{ transition: 'fill 0.22s ease', pointerEvents: 'none' }}
        >
          {edge.weight % 1 === 0 ? String(edge.weight) : edge.weight.toFixed(1)}
        </text>
      )}
    </g>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export function GraphTraversalRenderer({ state: rawState }: RendererProps) {
  const state = rawState as unknown as GraphState;
  const { svgRef, vbString, isZoomed, reset, handleWheel, handleMouseDown, handleMouseMove, stopDrag } = useViewBox();

  const nodes = state.nodes ?? [];
  const edges = state.edges ?? [];
  const path  = state.path  ?? [];

  const nodeMap = useMemo(() => {
    const m: Record<string, GraphNode> = {};
    for (const n of nodes) m[n.node_id] = n;
    return m;
  }, [nodes]);

  const pathEdgeSet = useMemo(() => {
    const s = new Set<string>();
    for (let i = 0; i < path.length - 1; i++) s.add(`${path[i]}|${path[i + 1]}`);
    return s;
  }, [path]);

  return (
    <div className="flex flex-col gap-2 select-none">
      {/* Top hint + reset button */}
      <div className="flex items-center justify-between px-1 min-h-[1.25rem]">
        <span className="text-xs text-neutral-700 font-mono">scroll to zoom · drag to pan</span>
        {isZoomed && (
          <button
            onClick={reset}
            className="px-2 py-0.5 rounded text-xs text-neutral-400 hover:text-white bg-white/5 hover:bg-white/10 transition-colors"
          >
            Reset view
          </button>
        )}
      </div>

      {/* SVG canvas */}
      <svg
        ref={svgRef}
        viewBox={vbString}
        className="w-full rounded-xl"
        style={{ background: C.bg, maxHeight: '440px', cursor: 'grab' }}
        aria-label="Graph visualization"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={stopDrag}
        onMouseLeave={stopDrag}
        onDoubleClick={reset}
      >
        <ArrowMarkers />

        {/* Edges */}
        {edges.map((edge) => {
          const src = nodeMap[edge.source];
          const tgt = nodeMap[edge.target];
          if (!src || !tgt) return null;
          const { cx: x1, cy: y1 } = toSvg(src);
          const { cx: x2, cy: y2 } = toSvg(tgt);
          const { color, width, markerKey } = getEdgeStyle(edge, state, pathEdgeSet);
          return (
            <EdgeEl
              key={edge.edge_id}
              edge={edge}
              x1={x1} y1={y1} x2={x2} y2={y2}
              color={color} width={width} markerKey={markerKey}
            />
          );
        })}

        {/* Nodes */}
        {nodes.map((node) => {
          const { cx, cy } = toSvg(node);
          const colors = getNodeColors(node.node_id, state);
          const dist      = state.distances?.[node.node_id];
          const isCurrent = state.current === node.node_id;
          const isVisited = !isCurrent && (state.visited ?? []).includes(node.node_id);
          const isFrontier = !isCurrent && !isVisited && (state.frontier ?? []).includes(node.node_id);
          const r = isCurrent ? NODE_R + 2 : NODE_R;
          const filterId = isCurrent ? 'glow-current' : isVisited ? 'glow-visited' : isFrontier ? 'glow-frontier' : undefined;
          return (
            <g key={node.node_id} style={{ transition: 'all 0.3s ease' }}>
              {/* Outer pulse ring on current node — SMIL animation */}
              {isCurrent && (
                <circle cx={cx} cy={cy} r={r} fill="none" stroke={colors.stroke} strokeWidth="1.5">
                  <animate attributeName="r"       from={String(r)}   to={String(r + 20)} dur="1.3s" repeatCount="indefinite" />
                  <animate attributeName="opacity" from="0.55"        to="0"             dur="1.3s" repeatCount="indefinite" />
                </circle>
              )}
              {/* Outer ring on visited/frontier */}
              {(isVisited || isFrontier) && (
                <circle
                  cx={cx} cy={cy} r={NODE_R + 5}
                  fill="none"
                  stroke={colors.stroke}
                  strokeWidth={1}
                  opacity={0.2}
                  style={{ transition: 'opacity 0.3s ease' }}
                />
              )}
              <circle
                cx={cx} cy={cy} r={r}
                fill={colors.fill}
                stroke={colors.stroke}
                strokeWidth={isCurrent ? 2.5 : 2}
                filter={filterId ? `url(#${filterId})` : undefined}
                style={{ transition: 'fill 0.25s ease, stroke 0.25s ease, r 0.2s ease' }}
              />
              <text
                x={cx} y={cy}
                textAnchor="middle" dominantBaseline="central"
                fill={colors.text}
                fontSize={isCurrent ? 12 : 11}
                fontWeight="700"
                fontFamily="ui-monospace, monospace"
                style={{ pointerEvents: 'none', transition: 'font-size 0.2s ease' }}
              >
                {node.label}
              </text>
              {dist !== undefined && (
                <text
                  x={cx + NODE_R + 3} y={cy - NODE_R + 3}
                  fill="#6b7280"
                  fontSize={8}
                  fontFamily="ui-monospace, monospace"
                  style={{ pointerEvents: 'none' }}
                >
                  {(dist === null || dist === undefined || !isFinite(dist as number)) ? '∞' : dist}
                </text>
              )}
            </g>
          );
        })}
      </svg>

      {/* Description below SVG — always visible regardless of zoom */}
      {state.description && (
        <p className="text-center text-xs font-mono text-neutral-500 px-4 min-h-[1rem]">
          {state.description}
        </p>
      )}

      {/* Legend + stats */}
      <div className="flex items-center justify-between px-2 flex-wrap gap-2">
        <div className="flex items-center gap-3 text-xs font-mono flex-wrap">
          <LegendItem color={C.current.fill}      label="Current"       shape="dot" />
          <LegendItem color={C.visited.fill}      label="Visited"       shape="dot" />
          <LegendItem color={C.frontier.fill}     label="Frontier"      shape="dot" />
          <LegendItem color={C.undiscovered.stroke} label="Undiscovered" shape="dot" />
          {path.length > 0 && <LegendItem color={C.pathEdge} label="Path" shape="line" />}
        </div>
        <div className="flex items-center gap-3 text-xs font-mono text-neutral-500">
          <span>visited <span className="text-neutral-300">{(state.visited ?? []).length}</span></span>
          <span>frontier <span className="text-neutral-300">{(state.frontier ?? []).length}</span></span>
          <span>nodes <span className="text-neutral-300">{nodes.length}</span></span>
          <span>edges <span className="text-neutral-300">{edges.length}</span></span>
        </div>
      </div>

      {/* Path sequence */}
      {path.length > 0 && (
        <div className="px-2 text-xs font-mono truncate">
          <span className="text-neutral-600">path: </span>
          <span className="text-cyan-400">{path.join(' → ')}</span>
        </div>
      )}
    </div>
  );
}

// ── Legend ────────────────────────────────────────────────────────────────────

function LegendItem({ color, label, shape }: { color: string; label: string; shape: 'dot' | 'line' }) {
  return (
    <span className="flex items-center gap-1.5 text-neutral-400">
      {shape === 'dot'
        ? <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ background: color }} />
        : <span className="inline-block w-5 h-0.5 rounded" style={{ background: color }} />}
      {label}
    </span>
  );
}
