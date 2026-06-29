/**
 * StateMachineRenderer — renders CryptoState (STATE_MACHINE).
 *
 * Shows cryptographic algorithm state as:
 *   Left panel:   Variable table (name → current value), highlighted vars pulsing
 *   Right panel:  Current operation string in a monospaced box
 *   Bottom:       Step name badge + bits visualization (if present)
 */

interface CryptoStateData {
  variables: [string, string][];
  operation: string;
  step_name: string;
  highlighted: string[];
  bits: string | null;
  result: string | null;
  description: string;
}

interface Props {
  state: Record<string, unknown>;
}

export function StateMachineRenderer({ state }: Props) {
  const s = state as unknown as CryptoStateData;
  const vars = s.variables ?? [];
  const highlighted = new Set(s.highlighted ?? []);
  const bits = s.bits ?? '';

  return (
    <div className="flex flex-col gap-3 w-full font-mono text-sm">
      {/* Step name badge */}
      <div className="flex items-center gap-2">
        <span className="px-2 py-0.5 rounded-md bg-indigo-600/30 text-indigo-300 text-xs border border-indigo-500/30">
          {s.step_name || 'Step'}
        </span>
        {s.result && (
          <span className="px-2 py-0.5 rounded-md bg-emerald-600/30 text-emerald-300 text-xs border border-emerald-500/30">
            Result: {s.result}
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3">
        {/* Variable table */}
        <div className="rounded-xl border border-white/5 bg-neutral-900/60 overflow-hidden">
          <div className="px-3 py-1.5 border-b border-white/5 text-xs text-neutral-500">Variables</div>
          <div className="divide-y divide-white/5 max-h-48 overflow-y-auto">
            {vars.length === 0 && (
              <div className="px-3 py-2 text-neutral-600 text-xs">No variables yet</div>
            )}
            {vars.map(([name, value]) => {
              const isHl = highlighted.has(name);
              return (
                <div
                  key={name}
                  className={[
                    'flex items-baseline gap-2 px-3 py-1.5 text-xs transition-colors',
                    isHl ? 'bg-indigo-900/30' : '',
                  ].join(' ')}
                >
                  <span className={`min-w-[3rem] ${isHl ? 'text-indigo-300' : 'text-neutral-400'}`}>
                    {name}
                  </span>
                  <span className="text-neutral-200 break-all leading-tight">
                    {String(value).length > 24 ? `${String(value).slice(0, 24)}…` : String(value)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Operation box */}
        <div className="flex flex-col gap-2">
          <div className="rounded-xl border border-white/5 bg-neutral-900/60 p-3 flex-1">
            <div className="text-xs text-neutral-500 mb-2">Operation</div>
            <pre className="text-xs text-indigo-200 whitespace-pre-wrap break-all leading-relaxed">
              {s.operation || '—'}
            </pre>
          </div>
        </div>
      </div>

      {/* Bits visualization */}
      {bits && (
        <div className="rounded-xl border border-white/5 bg-neutral-950 p-3 overflow-x-auto">
          <div className="text-xs text-neutral-500 mb-2">Bit pattern</div>
          <div className="flex flex-wrap gap-0.5">
            {bits.split('').map((bit, i) => (
              <span
                key={i}
                className={[
                  'w-4 h-5 text-[10px] flex items-center justify-center rounded font-bold',
                  bit === '1' ? 'bg-indigo-600/50 text-indigo-200' : 'bg-white/5 text-neutral-600',
                  (i + 1) % 8 === 0 ? 'mr-1' : '',
                ].join(' ')}
              >
                {bit}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Description */}
      {s.description && (
        <p className="text-xs text-neutral-500 leading-relaxed">{s.description}</p>
      )}
    </div>
  );
}
