/**
 * TreeRenderer — hierarchical tree visualization for inorder/preorder/postorder.
 *
 * Reuses GraphTraversalState format. Nodes have hierarchical x,y positions
 * computed by the plugin. Edges are directed parent→child with arrowheads.
 *
 * Color encoding (same as GraphTraversalRenderer):
 *   amber   — current node
 *   green   — visited (in result array)
 *   indigo  — frontier (traversal stack)
 *   neutral — undiscovered
 */

import { useMemo } from 'react';
import type { RendererProps } from '../RendererRegistry';

interface TreeNode {
  node_id: string;
  label: string;
  x: number;
  y: number;
}

interface TreeEdge {
  edge_id: string;
  source: string;
  target: string;
  directed: boolean;
}

interface TreeState {
  nodes: TreeNode[];
  edges: TreeEdge[];
  visited: string[];
  frontier: string[];
  current: string | null;
  path: string[];
  description: string;
}

const VW = 600;
const VH = 400;
const PAD = 40;
const NODE_R = 18;
const IW = VW - PAD * 2;
const IH = VH - PAD * 2 - 48; // -48 for description + path bar

const C = {
  current:       { fill: '#fbbf24', stroke: '#f59e0b', text: '#1c1917' },
  visited:       { fill: '#22c55e', stroke: '#16a34a', text: '#052e16' },
  frontier:      { fill: '#818cf8', stroke: '#6366f1', text: '#1e1b4b' },
  undiscovered:  { fill: '#262626', stroke: '#525252', text: '#a3a3a3' },
  edgeVisited:   '#166534',
  edgeCurrent:   '#d97706',
  edgeFrontier:  '#4338ca',
  edgeDefault:   '#3f3f46',
  bg:            '#171717',
};

function nodeColor(nodeId: string, state: TreeState) {
  if (state.current === nodeId)          return C.current;
  if (state.visited.includes(nodeId))    return C.visited;
  if (state.frontier.includes(nodeId))   return C.frontier;
  return C.undiscovered;
}

function edgeColor(src: string, tgt: string, state: TreeState) {
  if (state.current === src || state.current === tgt)       return C.edgeCurrent;
  if (state.visited.includes(src) && state.visited.includes(tgt)) return C.edgeVisited;
  if (
    (state.visited.includes(src) && state.frontier.includes(tgt)) ||
    (state.frontier.includes(src) && state.visited.includes(tgt))
  ) return C.edgeFrontier;
  return C.edgeDefault;
}

function ArrowLine({
  x1, y1, x2, y2,
  color,
}: {
  x1: number; y1: number; x2: number; y2: number; color: string;
}) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const dist = Math.sqrt(dx * dx + dy * dy) || 1;
  const nx = dx / dist;
  const ny = dy / dist;

  // Start/end on circle edges, not centers
  const sx = x1 + nx * NODE_R;
  const sy = y1 + ny * NODE_R;
  const tipX = x2 - nx * NODE_R;
  const tipY = y2 - ny * NODE_R;

  // Arrowhead triangle
  const A = 7;
  const baseX = tipX - nx * A;
  const baseY = tipY - ny * A;
  const px = (-ny * A) / 2;
  const py = (nx * A) / 2;

  const pts = `${tipX},${tipY} ${baseX + px},${baseY + py} ${baseX - px},${baseY - py}`;

  return (
    <g>
      <line x1={sx} y1={sy} x2={baseX} y2={baseY} stroke={color} strokeWidth={1.5} strokeLinecap="round" />
      <polygon points={pts} fill={color} />
    </g>
  );
}

export function TreeRenderer({ state: rawState }: RendererProps) {
  const state = rawState as unknown as TreeState;

  const nodeMap = useMemo(() => {
    const m: Record<string, TreeNode> = {};
    for (const n of (state.nodes ?? [])) m[n.node_id] = n;
    return m;
  }, [state.nodes]);

  function toSvg(node: TreeNode) {
    return {
      cx: PAD + node.x * IW,
      cy: PAD + node.y * IH,
    };
  }

  const nodes = state.nodes ?? [];
  const edges = state.edges ?? [];
  const visitedCount = (state.visited ?? []).length;
  const frontierCount = (state.frontier ?? []).length;
  const pathLength = (state.path ?? []).length;

  return (
    <div className="flex flex-col gap-2">
      <svg
        viewBox={`0 0 ${VW} ${VH}`}
        className="w-full rounded-xl"
        style={{ background: C.bg, maxHeight: '420px' }}
        aria-label="Tree traversal visualization"
      >
        {/* Directed edges */}
        {edges.map((edge) => {
          const src = nodeMap[edge.source];
          const tgt = nodeMap[edge.target];
          if (!src || !tgt) return null;
          const { cx: x1, cy: y1 } = toSvg(src);
          const { cx: x2, cy: y2 } = toSvg(tgt);
          const color = edgeColor(edge.source, edge.target, state);
          return (
            <ArrowLine key={edge.edge_id} x1={x1} y1={y1} x2={x2} y2={y2} color={color} />
          );
        })}

        {/* Nodes */}
        {nodes.map((node) => {
          const { cx, cy } = toSvg(node);
          const colors = nodeColor(node.node_id, state);
          return (
            <g key={node.node_id}>
              <circle cx={cx} cy={cy} r={NODE_R} fill={colors.fill} stroke={colors.stroke} strokeWidth={2} />
              <text
                x={cx} y={cy}
                textAnchor="middle" dominantBaseline="central"
                fill={colors.text} fontSize={11} fontWeight="600"
                fontFamily="ui-monospace, monospace"
              >
                {node.label}
              </text>
            </g>
          );
        })}

        {/* Description bar */}
        <text
          x={VW / 2} y={VH - 28}
          textAnchor="middle" fill="#737373" fontSize={10}
          fontFamily="ui-monospace, monospace"
        >
          {state.description ?? ''}
        </text>

        {/* Traversal result path */}
        {(state.path ?? []).length > 0 && (
          <text
            x={VW / 2} y={VH - 10}
            textAnchor="middle" fill="#525252" fontSize={10}
            fontFamily="ui-monospace, monospace"
          >
            {'[' + (state.path ?? []).map((id) => nodeMap[id]?.label ?? id).join(', ') + ']'}
          </text>
        )}
      </svg>

      {/* Legend + stats */}
      <div className="flex items-center justify-between px-2">
        <div className="flex items-center gap-3 text-xs font-mono">
          <LegendDot color={C.current.fill} label="Current" />
          <LegendDot color={C.visited.fill} label="Visited" />
          <LegendDot color={C.frontier.fill} label="Stack" />
          <LegendDot color={C.undiscovered.stroke} label="Unvisited" />
        </div>
        <div className="flex items-center gap-3 text-xs font-mono text-neutral-500">
          <span>visited <span className="text-neutral-300">{visitedCount}</span></span>
          <span>stack <span className="text-neutral-300">{frontierCount}</span></span>
          <span>result <span className="text-neutral-300">{pathLength}</span></span>
        </div>
      </div>
    </div>
  );
}

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <span className="flex items-center gap-1 text-neutral-400">
      <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ background: color }} />
      {label}
    </span>
  );
}
