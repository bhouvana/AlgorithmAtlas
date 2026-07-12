import { useMemo, useState } from 'react';
import { Copy, Check, WrapText, Eraser } from 'lucide-react';
import { cn } from '../../../lib/utils';
import type { NormalizedResult } from './resultNormalize';

interface Props {
  result: NormalizedResult | null;
}

export function ConsoleTab({ result }: Props) {
  const [wrap, setWrap] = useState(true);
  const [cleared, setCleared] = useState(false);
  const [copied, setCopied] = useState(false);

  const log = useMemo(() => {
    if (!result) return '';
    const lines: string[] = [];
    if (result.compileOutput) {
      lines.push('$ compile');
      lines.push(result.compileOutput.trimEnd());
      lines.push('');
    }
    for (const c of result.cases) {
      lines.push(`$ run ${c.label}${c.isHidden ? ' (hidden)' : ''} -- exit ${c.exitCode ?? 'n/a'}, ${c.runtimeMs.toFixed(1)}ms`);
      if (c.isHidden) {
        lines.push('(output hidden)');
      } else {
        if (c.actual) lines.push(c.actual.trimEnd());
        if (c.stderr) lines.push(c.stderr.trimEnd());
        if (!c.actual && !c.stderr) lines.push('(no output)');
      }
      lines.push('');
    }
    return lines.join('\n').trimEnd();
  }, [result]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(log);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard API unavailable -- no-op, not worth surfacing an error for
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-shrink-0 flex items-center gap-2 px-3 py-2 border-b border-white/8">
        <span className="text-sm text-zinc-500">Execution Console</span>
        <div className="flex-1" />
        <button
          onClick={() => setWrap((w) => !w)}
          className={cn('flex items-center gap-1 text-sm px-2 py-1 rounded-lg transition-colors', wrap ? 'text-white bg-white/8' : 'text-zinc-500 hover:text-zinc-300')}
          title="Toggle line wrap"
        >
          <WrapText className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={() => setCleared((c) => !c)}
          className="flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-300 px-2 py-1 rounded-lg transition-colors"
          title="Clear local view"
        >
          <Eraser className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-300 px-2 py-1 rounded-lg transition-colors"
          title="Copy"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
        </button>
      </div>
      <div className="flex-1 overflow-auto p-3">
        {cleared || !result ? (
          <div className="text-sm text-zinc-600">
            {cleared ? 'Console cleared.' : 'No execution yet. Run or submit your code to see console output.'}
          </div>
        ) : (
          <pre className={cn('text-sm font-mono text-zinc-300', wrap ? 'whitespace-pre-wrap' : 'whitespace-pre overflow-x-auto')}>
            {log}
          </pre>
        )}
      </div>
    </div>
  );
}
