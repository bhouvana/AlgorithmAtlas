/**
 * TimelineRenderer — renders DistributedSystemState as a Lamport-style
 * space-time diagram (TIMELINE).
 *
 * Each node gets a horizontal lane. Events (derived from the message log)
 * appear as points; causality arrows connect sends to receives.
 *
 * Also usable for DistributedSystemState when the TIMELINE type is preferred
 * over NETWORK_TOPOLOGY (e.g. for Vector Clocks, Lamport Clocks).
 */

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

const LANE_H = 52;
const LANE_PAD = 24;
const LEFT_PAD = 60;
const RIGHT_PAD = 20;
const TOP_PAD = 16;
const DOT_R = 5;

export function TimelineRenderer({ state }: Props) {
  const s = state as unknown as DistributedSystemStateData;
  const nodes = s.nodes ?? [];
  const messages = s.messages ?? [];

  const W = Math.max(400, LEFT_PAD + messages.length * 36 + RIGHT_PAD + 60);
  const H = TOP_PAD + nodes.length * LANE_H + LANE_PAD;

  // Map node_id → lane index
  const laneMap = new Map(nodes.map((n, i) => [n.node_id, i]));

  // Position each message send/receive along the time axis
  const msgSlots = messages.map((m, i) => ({ msg: m, slot: i }));

  const timeX = (slot: number) => LEFT_PAD + slot * Math.max(32, (W - LEFT_PAD - RIGHT_PAD) / Math.max(messages.length, 1));
  const laneY = (nodeId: string) => {
    const idx = laneMap.get(nodeId) ?? 0;
    return TOP_PAD + idx * LANE_H + LANE_H / 2;
  };

  const ROLE_COLOR: Record<string, string> = {
    leader: '#f59e0b', candidate: '#f97316', follower: '#6366f1',
    coordinator: '#10b981', participant: '#818cf8', down: '#374151',
  };
  const nodeColor = (role: string) => ROLE_COLOR[role.toLowerCase()] ?? '#6366f1';

  return (
    <div className="flex flex-col gap-2 items-center w-full overflow-x-auto">
      {s.event && (
        <span className="px-2 py-0.5 rounded-md bg-indigo-600/20 text-indigo-300 text-xs border border-indigo-500/20 font-mono">
          {s.event}
        </span>
      )}

      <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{ maxWidth: W, minWidth: 320 }}>
        {/* Lane lines */}
        {nodes.map((node) => {
          const y = laneY(node.node_id);
          const color = nodeColor(node.role);
          return (
            <g key={node.node_id}>
              {/* Node label */}
              <text x={LEFT_PAD - 8} y={y + 4} textAnchor="end" fontSize="10"
                fill={color} fontFamily="monospace" fontWeight="bold">
                {node.node_id}
              </text>
              <text x={LEFT_PAD - 8} y={y + 14} textAnchor="end" fontSize="8" fill={color} opacity={0.6}>
                {node.role} t{node.term}
              </text>
              {/* Timeline lane */}
              <line x1={LEFT_PAD} y1={y} x2={W - RIGHT_PAD} y2={y}
                stroke={color} strokeWidth="1" opacity="0.25" />
            </g>
          );
        })}

        {/* Messages as arrows */}
        {msgSlots.map(({ msg, slot }) => {
          const srcY = laneY(msg.src);
          const dstY = laneY(msg.dst);
          const x = timeX(slot);
          const isDel = msg.delivered;
          const color = isDel ? '#4b5563' : '#f59e0b';
          const opacity = isDel ? 0.4 : 0.9;

          return (
            <g key={msg.msg_id} opacity={opacity}>
              {/* Arrow */}
              <defs>
                <marker id={`arr-${slot}`} markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                  <path d="M0,0 L0,6 L6,3 z" fill={color} />
                </marker>
              </defs>
              <line
                x1={x} y1={srcY} x2={x} y2={dstY > srcY ? dstY - DOT_R - 2 : dstY + DOT_R + 2}
                stroke={color} strokeWidth="1.5"
                markerEnd={`url(#arr-${slot})`}
                strokeDasharray={isDel ? '3 2' : undefined}
              />
              {/* Send dot */}
              <circle cx={x} cy={srcY} r={DOT_R} fill={color} />
              {/* Receive dot */}
              <circle cx={x} cy={dstY} r={DOT_R} fill={color} opacity="0.6" />
              {/* Message type label */}
              <text
                x={x + 4} y={Math.min(srcY, dstY) - 4}
                fontSize="7" fill={color} fontFamily="monospace"
                transform={`rotate(-30 ${x + 4} ${Math.min(srcY, dstY) - 4})`}
              >
                {msg.msg_type}
              </text>
            </g>
          );
        })}

        {/* Node dot on their current time position (right end) */}
        {nodes.map((node) => {
          const y = laneY(node.node_id);
          const x = W - RIGHT_PAD - 4;
          const color = nodeColor(node.role);
          return (
            <circle key={node.node_id} cx={x} cy={y} r={6}
              fill={color} stroke="#0a0a0f" strokeWidth="1.5" />
          );
        })}
      </svg>

      {s.description && (
        <p className="text-xs text-neutral-500 font-mono text-center leading-relaxed">
          {s.description}
        </p>
      )}
    </div>
  );
}
