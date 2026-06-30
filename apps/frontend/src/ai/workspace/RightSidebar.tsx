import { ContextCards } from './ContextCards';
import type { AtlasContext } from '../types';

interface Props { context: AtlasContext }

export function RightSidebar({ context }: Props) {
  return (
    <div
      className="flex flex-col h-full overflow-hidden"
      style={{ borderLeft: '1px solid rgba(255,255,255,0.05)' }}
    >
      <div className="px-3 pt-3 pb-1 flex-shrink-0">
        <span className="text-[10px] font-semibold uppercase tracking-widest text-zinc-600">
          Context
        </span>
      </div>
      <div
        className="flex-1 overflow-y-auto pb-3"
        style={{ scrollbarWidth: 'thin', scrollbarColor: '#27272a transparent' }}
      >
        <ContextCards context={context} />
        <div className="px-3 pt-4">
          <div
            className="rounded-2xl p-3 text-center"
            style={{
              background: 'linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.06))',
              border: '1px solid rgba(99,102,241,0.12)',
            }}
          >
            <p className="text-[11px] text-zinc-500 leading-relaxed">
              Atlas is aware of what you're doing and will tailor its responses accordingly.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
