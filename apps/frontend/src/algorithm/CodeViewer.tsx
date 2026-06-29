/**
 * CodeViewer — displays algorithm Python source with line numbers.
 *
 * Applies keyword-based syntax coloring without external libraries
 * by tokenizing each line into spans.
 */

import { useEffect, useState } from 'react';
import { api, type AlgorithmSource } from '../core/api/client';

// ── Tokenizer ─────────────────────────────────────────────────────────────────

const KEYWORDS = new Set([
  'def', 'class', 'return', 'yield', 'from', 'import', 'as', 'if', 'else',
  'elif', 'for', 'while', 'in', 'not', 'and', 'or', 'is', 'None', 'True',
  'False', 'pass', 'break', 'continue', 'raise', 'try', 'except', 'finally',
  'with', 'lambda', 'global', 'nonlocal', 'assert', 'del', 'async', 'await',
]);

const BUILTINS = new Set([
  'int', 'str', 'list', 'dict', 'set', 'tuple', 'bool', 'float', 'len',
  'range', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'min', 'max',
  'sum', 'abs', 'round', 'print', 'type', 'isinstance', 'hasattr', 'getattr',
  'Generator', 'Optional', 'Tuple', 'List', 'Dict', 'FrozenSet', 'Any',
]);

type TokenKind = 'keyword' | 'builtin' | 'string' | 'comment' | 'number' | 'decorator' | 'plain';

interface Token {
  kind: TokenKind;
  text: string;
}

const TOKEN_COLOR: Record<TokenKind, string> = {
  keyword:   '#c792ea',
  builtin:   '#82aaff',
  string:    '#c3e88d',
  comment:   '#546e7a',
  number:    '#f78c6c',
  decorator: '#ffcb6b',
  plain:     '#d4d4d4',
};

function tokenizeLine(line: string): Token[] {
  const tokens: Token[] = [];

  // Decorator line
  if (/^\s*@\w+/.test(line)) {
    const indent = line.match(/^(\s*)/)![1];
    const rest = line.slice(indent.length);
    if (indent) tokens.push({ kind: 'plain', text: indent });
    tokens.push({ kind: 'decorator', text: rest });
    return tokens;
  }

  const commentIdx = line.search(/#(?!['"\\])/);
  const codePart = commentIdx >= 0 ? line.slice(0, commentIdx) : line;
  const commentPart = commentIdx >= 0 ? line.slice(commentIdx) : '';

  // Tokenize code portion
  let i = 0;
  while (i < codePart.length) {
    // String literals
    if (codePart[i] === '"' || codePart[i] === "'") {
      const quote = codePart[i];
      const triple = codePart.startsWith(quote.repeat(3), i);
      const end_seq = triple ? quote.repeat(3) : quote;
      const start = i;
      i += end_seq.length;
      while (i < codePart.length) {
        if (codePart[i] === '\\') { i += 2; continue; }
        if (codePart.startsWith(end_seq, i)) { i += end_seq.length; break; }
        i++;
      }
      tokens.push({ kind: 'string', text: codePart.slice(start, i) });
      continue;
    }

    // Numbers
    if (/[0-9]/.test(codePart[i]) || (codePart[i] === '-' && /[0-9]/.test(codePart[i + 1] ?? ''))) {
      const match = codePart.slice(i).match(/^-?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/);
      if (match) {
        tokens.push({ kind: 'number', text: match[0] });
        i += match[0].length;
        continue;
      }
    }

    // Words
    const wordMatch = codePart.slice(i).match(/^[A-Za-z_]\w*/);
    if (wordMatch) {
      const word = wordMatch[0];
      const kind: TokenKind = KEYWORDS.has(word) ? 'keyword' : BUILTINS.has(word) ? 'builtin' : 'plain';
      tokens.push({ kind, text: word });
      i += word.length;
      continue;
    }

    // Other chars — accumulate into plain
    const last = tokens[tokens.length - 1];
    if (last?.kind === 'plain') {
      last.text += codePart[i];
    } else {
      tokens.push({ kind: 'plain', text: codePart[i] });
    }
    i++;
  }

  if (commentPart) {
    tokens.push({ kind: 'comment', text: commentPart });
  }

  return tokens;
}

// ── Component ─────────────────────────────────────────────────────────────────

interface CodeViewerProps {
  slug: string;
}

export function CodeViewer({ slug }: CodeViewerProps) {
  const [source, setSource] = useState<AlgorithmSource | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api.algorithms.getSource(slug)
      .then((s) => { setSource(s); setLoading(false); })
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, [slug]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48 text-neutral-500 text-sm">
        Loading source…
      </div>
    );
  }

  if (error || !source) {
    return (
      <div className="text-red-400 text-sm font-mono p-4">
        {error ?? 'Source not available'}
      </div>
    );
  }

  const lines = source.source.split('\n');

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <span className="text-xs text-neutral-600 font-mono">{source.filename}</span>
        <span className="text-xs text-neutral-600 font-mono">{source.line_count} lines</span>
      </div>
      <div
        className="overflow-x-auto overflow-y-auto rounded-xl border border-white/5 bg-neutral-950"
        style={{ maxHeight: '520px' }}
      >
        <table className="text-xs font-mono w-full border-collapse" style={{ lineHeight: '1.6' }}>
          <tbody>
            {lines.map((line, idx) => (
              <tr key={idx} className="hover:bg-white/[0.02]">
                <td
                  className="select-none text-right pr-4 pl-3 text-neutral-700 border-r border-white/5"
                  style={{ minWidth: '3rem', userSelect: 'none' }}
                >
                  {idx + 1}
                </td>
                <td className="pl-4 pr-3 whitespace-pre">
                  {tokenizeLine(line).map((tok, ti) => (
                    <span key={ti} style={{ color: TOKEN_COLOR[tok.kind] }}>
                      {tok.text}
                    </span>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
