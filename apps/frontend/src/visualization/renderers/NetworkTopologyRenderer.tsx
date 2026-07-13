/**
 * NetworkTopologyRenderer — renders DistributedSystemState (NETWORK_TOPOLOGY).
 *
 * Shows:
 *   - Nodes arranged in a circle, colored by role
 *     (leader=gold, candidate=amber, follower=indigo, down=grey)
 *   - In-flight messages as animated arrows between nodes
 *   - Node role label + term number
 *   - Event description below
 */

import { useMemo } from 'react';

interface DSNodeData {
  node_id: string;
  role: string;
  term: number;
  log: string[];
  inbox: string[];
  data: string;
}

interface DSMessageData {
  msg_id: string;
  src: string;
  dst: string;
  msg_type: string;
  payload: string;
  delivered: boolean;
}

interface DistributedSystemStateData {
  nodes: DSNodeData[];
  messages: DSMessageData[];
  event: string;
  description: string;
}

interface Props {
  state: Record<string, unknown>;
}

const NODE_R = 22;
const CIRCLE_R = 130;
const CX = 220;
const CY = 200;
const W = 440;
const H = 400;

const ROLE_COLORS: Record<string, { fill: string; stroke: string; text: string }> = {
  leader:      { fill: '#78350f', stroke: '#f59e0b', text: '#fde68a' },
  candidate:   { fill: '#451a03', stroke: '#f97316', text: '#fed7aa' },
  follower:    { fill: '#1e1b4b', stroke: '#6366f1', text: '#c7d2fe' },
  coordinator: { fill: '#064e3b', stroke: '#10b981', text: '#a7f3d0' },
  participant: { fill: '#1e1b4b', stroke: '#6366f1', text: '#c7d2fe' },
  proposer:    { fill: '#78350f', stroke: '#f59e0b', text: '#fde68a' },
  acceptor:    { fill: '#1e1b4b', stroke: '#6366f1', text: '#c7d2fe' },
  learner:     { fill: '#064e3b', stroke: '#10b981', text: '#a7f3d0' },
  down:        { fill: '#111', stroke: '#374151', text: '#4b5563' },
  crashed:     { fill: '#111', stroke: '#374151', text: '#4b5563' },
};

function roleStyle(role: string) {
  return ROLE_COLORS[role.toLowerCase()] ?? ROLE_COLORS.follower;
}

export function NetworkTopologyRenderer({ state }: Props) {
  const s = state as unknown as DistributedSystemStateData;
  const nodes = s.nodes ?? [];
  const messages = (s.messages ?? []).filter((m) => !m.delivered);

  // Position nodes in a circle
  const nodePositions = useMemo(() => {
    const n = nodes.length || 1;
    return nodes.map((node, i) => {
      const angle = (2 * Math.PI * i) / n - Math.PI / 2;
      return {
        node,
        x: CX + CIRCLE_R * Math.cos(angle),
        y: CY + CIRCLE_R * Math.sin(angle),
      };
    });
  }, [nodes]);

  const posMap = useMemo(() => {
    const m = new Map<string, { x: number; y: number }>();
    nodePositions.forEach(({ node, x, y }) => m.set(node.node_id, { x, y }));
    return m;
  }, [nodePositions]);

  return (
    <div className="flex flex-col gap-2 items-center w-full">
      {/* Event badge */}
      {s.event && (
        <span className="px-2 py-0.5 rounded-md bg-indigo-600/20 text-indigo-300 text-xs border border-indigo-500/20 font-mono">
          {s.event}
        </span>
      )}

      <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{ maxWidth: W }}>
        <defs>
          <marker id="arrow-msg" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
            <path d="M0,0 L0,6 L8,3 z" fill="#f59e0b" opacity="0.8" />
          </marker>
          <marker id="arrow-delivered" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
            <path d="M0,0 L0,6 L8,3 z" fill="#6b7280" opacity="0.4" />
          </marker>
        </defs>

        {/* Background edges (full mesh, faint) */}
        {nodePositions.map(({ node: a, x: ax, y: ay }) =>
          nodePositions.map(({ node: b, x: bx, y: by }) => {
            if (a.node_id >= b.node_id) return null;
            return (
              <line
                key={`${a.node_id}-${b.node_id}`}
                x1={ax} y1={ay} x2={bx} y2={by}
                stroke="#1f2937" strokeWidth="1"
              />
            );
          }),
        )}

        {/* In-flight messages */}
        {messages.map((msg) => {
          const src = posMap.get(msg.src);
          const dst = posMap.get(msg.dst);
          if (!src || !dst) return null;
          // Midpoint for label
          const mx = (src.x + dst.x) / 2;
          const my = (src.y + dst.y) / 2;
          // Shorten arrow to not overlap node circles
          const dx = dst.x - src.x;
          const dy = dst.y - src.y;
          const len = Math.hypot(dx, dy) || 1;
          const shrink = NODE_R + 4;
          const x1 = src.x + (dx / len) * shrink;
          const y1 = src.y + (dy / len) * shrink;
          const x2 = dst.x - (dx / len) * (shrink + 8);
          const y2 = dst.y - (dy / len) * (shrink + 8);
          return (
            <g key={msg.msg_id}>
              <line
                x1={x1} y1={y1} x2={x2} y2={y2}
                stroke="#f59e0b" strokeWidth="1.5"
                markerEnd="url(#arrow-msg)"
                strokeDasharray="5 3"
              />
              <text x={mx} y={my - 5} textAnchor="middle" fontSize="8" fill="#f59e0b" fontFamily="monospace">
                {msg.msg_type}
              </text>
            </g>
          );
        })}

        {/* Nodes */}
        {nodePositions.map(({ node, x, y }) => {
          const st = roleStyle(node.role);
          return (
            <g key={node.node_id}>
              <circle cx={x} cy={y} r={NODE_R} fill={st.fill} stroke={st.stroke} strokeWidth="2" />
              <text x={x} y={y - 5} textAnchor="middle" fontSize="9" fill={st.text} fontWeight="bold">
                {node.node_id}
              </text>
              <text x={x} y={y + 6} textAnchor="middle" fontSize="8" fill={st.text} opacity="0.8">
                {node.role}
              </text>
              <text x={x} y={y + 16} textAnchor="middle" fontSize="7" fill={st.text} opacity="0.6">
                t={node.term}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Message log */}
      {messages.length > 0 && (
        <div className="w-full rounded-lg border border-charcoal/10 bg-neutral-900/50 p-2 max-h-24 overflow-y-auto">
          {messages.map((m) => (
            <div key={m.msg_id} className="text-xs font-mono text-neutral-400 leading-relaxed">
              <span className="text-neutral-300">{m.src}</span>
              <span className="text-neutral-600"> → </span>
              <span className="text-neutral-300">{m.dst}</span>
              <span className="text-amber-500"> [{m.msg_type}]</span>
              {m.payload && <span className="text-neutral-600"> {m.payload}</span>}
            </div>
          ))}
        </div>
      )}

      {s.description && (
        <p className="text-xs text-neutral-500 font-mono text-center leading-relaxed">
          {s.description}
        </p>
      )}
    </div>
  );
}
