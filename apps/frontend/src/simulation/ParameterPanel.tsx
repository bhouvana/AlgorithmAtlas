/**
 * ParameterPanel — renders typed input controls from a plugin's parameter schema.
 *
 * Supported param types (matching our manifest "parameters" format):
 *   integer  → range slider + numeric input
 *   choice   → button group (radio-style)
 *   boolean  → toggle button
 *
 * Workflow:
 *   1. User adjusts controls  → local pending state updates
 *   2. "Re-run" button lights up when pending ≠ applied
 *   3. User clicks "Re-run"   → onApply(pendingValues) is called
 */

import { useState, useCallback, useEffect } from 'react';

// ── Types matching our manifest "parameters" schema ───────────────────────────

interface IntegerParam {
  type: 'integer';
  label: string;
  min?: number;
  max?: number;
  default?: number;
}

interface ChoiceParam {
  type: 'choice';
  label: string;
  choices: string[];
  default?: string;
}

interface BooleanParam {
  type: 'boolean';
  label: string;
  default?: boolean;
}

type ParamSpec = IntegerParam | ChoiceParam | BooleanParam;

export type ParameterValues = Record<string, unknown>;
export type ParameterSchema = Record<string, ParamSpec | unknown>;

// ── Helpers ───────────────────────────────────────────────────────────────────

function extractDefault(spec: ParamSpec): unknown {
  return spec.default ?? (spec.type === 'integer' ? spec.min ?? 0 : spec.type === 'boolean' ? false : '');
}

function buildDefaults(schema: ParameterSchema): ParameterValues {
  const out: ParameterValues = {};
  for (const [key, raw] of Object.entries(schema)) {
    const spec = raw as ParamSpec;
    if (spec && typeof spec === 'object' && 'type' in spec) {
      out[key] = extractDefault(spec);
    }
  }
  return out;
}

function isEqualValues(a: ParameterValues, b: ParameterValues): boolean {
  return JSON.stringify(a) === JSON.stringify(b);
}

// ── Props ─────────────────────────────────────────────────────────────────────

interface ParameterPanelProps {
  schema: ParameterSchema;
  onApply: (values: ParameterValues) => void;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function ParameterPanel({ schema, onApply }: ParameterPanelProps) {
  const defaults = buildDefaults(schema);
  const [pending, setPending] = useState<ParameterValues>(defaults);
  const [applied, setApplied] = useState<ParameterValues>(defaults);

  // Reset pending when schema changes (different algorithm)
  useEffect(() => {
    const d = buildDefaults(schema);
    setPending(d);
    setApplied(d);
  }, [JSON.stringify(schema)]);  // eslint-disable-line react-hooks/exhaustive-deps

  const isDirty = !isEqualValues(pending, applied);

  const handleApply = useCallback(() => {
    setApplied(pending);
    onApply(pending);
  }, [pending, onApply]);

  const updateField = useCallback((key: string, value: unknown) => {
    setPending((prev) => ({ ...prev, [key]: value }));
  }, []);

  const entries = Object.entries(schema).filter(([, raw]) => {
    const spec = raw as ParamSpec;
    return spec && typeof spec === 'object' && 'type' in spec && spec.type !== undefined;
  });

  if (entries.length === 0) return null;

  return (
    <div className="flex flex-col gap-3 p-4 bg-neutral-900 rounded-xl border border-charcoal/10">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-neutral-500 uppercase tracking-wider">
          Parameters
        </span>
        {isDirty && (
          <button
            onClick={handleApply}
            className="px-3 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400"
          >
            Re-run
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {entries.map(([key, raw]) => {
          const spec = raw as ParamSpec;
          return (
            <ParamControl
              key={key}
              paramKey={key}
              spec={spec}
              value={pending[key]}
              onChange={updateField}
            />
          );
        })}
      </div>
    </div>
  );
}

// ── Individual control ────────────────────────────────────────────────────────

function ParamControl({
  paramKey,
  spec,
  value,
  onChange,
}: {
  paramKey: string;
  spec: ParamSpec;
  value: unknown;
  onChange: (key: string, value: unknown) => void;
}) {
  if (spec.type === 'integer') {
    const min = spec.min ?? 0;
    const max = spec.max ?? 100;
    const current = typeof value === 'number' ? value : (spec.default ?? min);
    return (
      <div className="flex flex-col gap-1">
        <div className="flex items-center justify-between">
          <label className="text-xs text-neutral-400">{spec.label}</label>
          <span className="text-xs font-mono text-neutral-300">{current}</span>
        </div>
        <input
          type="range"
          min={min}
          max={max}
          value={current}
          onChange={(e) => onChange(paramKey, parseInt(e.target.value, 10))}
          className="w-full h-1 accent-indigo-500"
          aria-label={spec.label}
        />
      </div>
    );
  }

  if (spec.type === 'choice') {
    const current = typeof value === 'string' ? value : (spec.default ?? spec.choices[0] ?? '');
    return (
      <div className="flex flex-col gap-1">
        <label className="text-xs text-neutral-400">{spec.label}</label>
        <div className="flex flex-wrap gap-1">
          {spec.choices.map((choice) => (
            <button
              key={choice}
              onClick={() => onChange(paramKey, choice)}
              className={[
                'px-2 py-0.5 rounded text-xs font-mono transition-colors',
                current === choice
                  ? 'bg-indigo-600 text-white'
                  : 'text-neutral-400 hover:text-white hover:bg-white/10 border border-charcoal/10',
              ].join(' ')}
            >
              {choice}
            </button>
          ))}
        </div>
      </div>
    );
  }

  if (spec.type === 'boolean') {
    const current = typeof value === 'boolean' ? value : (spec.default ?? false);
    return (
      <div className="flex items-center justify-between">
        <label className="text-xs text-neutral-400">{spec.label}</label>
        <button
          onClick={() => onChange(paramKey, !current)}
          className={[
            'px-3 py-0.5 rounded text-xs font-mono transition-colors border',
            current
              ? 'bg-indigo-600 text-white border-indigo-500'
              : 'text-neutral-400 border-charcoal/10 hover:bg-white/10',
          ].join(' ')}
        >
          {current ? 'on' : 'off'}
        </button>
      </div>
    );
  }

  return null;
}
