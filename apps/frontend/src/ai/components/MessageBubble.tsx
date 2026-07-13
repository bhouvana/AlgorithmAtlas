import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Copy, Check, FileEdit } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import type { ChatMessage } from '../types';
import { WhiteboardView } from './WhiteboardView';
import { useAtlasStore } from '../store';

interface Props {
  message: ChatMessage;
  isNew?: boolean;
}

// ── Tokeniser ─────────────────────────────────────────────────────────────────

type Token =
  | { type: 'code_block'; lang: string; content: string }
  | { type: 'header'; level: number; content: string }
  | { type: 'bullet'; content: string }
  | { type: 'numbered'; n: number; content: string }
  | { type: 'hr' }
  | { type: 'text'; content: string }
  | { type: 'blank' };

function tokenise(md: string): Token[] {
  const tokens: Token[] = [];
  const codeRe = /```(\w*)\n?([\s\S]*?)```/g;
  let last = 0;
  let m: RegExpExecArray | null;

  while ((m = codeRe.exec(md)) !== null) {
    if (m.index > last) inlineTokenise(md.slice(last, m.index), tokens);
    tokens.push({ type: 'code_block', lang: m[1] || 'text', content: m[2].replace(/\n$/, '') });
    last = m.index + m[0].length;
  }
  if (last < md.length) inlineTokenise(md.slice(last), tokens);
  return tokens;
}

function inlineTokenise(text: string, out: Token[]) {
  let n = 1;
  for (const line of text.split('\n')) {
    if (/^###\s/.test(line))      out.push({ type: 'header', level: 3, content: line.slice(4) });
    else if (/^##\s/.test(line))  out.push({ type: 'header', level: 2, content: line.slice(3) });
    else if (/^#\s/.test(line))   out.push({ type: 'header', level: 1, content: line.slice(2) });
    else if (/^---+$/.test(line.trim())) out.push({ type: 'hr' });
    else if (/^\d+\.\s/.test(line)) {
      const idx = line.indexOf('. ');
      out.push({ type: 'numbered', n: n++, content: line.slice(idx + 2) });
    } else if (/^[-*]\s/.test(line)) out.push({ type: 'bullet', content: line.slice(2) });
    else if (!line.trim()) out.push({ type: 'blank' });
    else out.push({ type: 'text', content: line });
  }
}

// ── Inline renderer ───────────────────────────────────────────────────────────

function renderInline(text: string, key?: number): React.ReactNode {
  const parts: React.ReactNode[] = [];
  const re = /(\*\*(.+?)\*\*|\*(.+?)\*|`([^`]+)`|\$([^$]+)\$)/g;
  let last = 0; let k = 0; let hit;
  while ((hit = re.exec(text)) !== null) {
    if (hit.index > last) parts.push(<React.Fragment key={k++}>{text.slice(last, hit.index)}</React.Fragment>);
    if (hit[2] !== undefined) parts.push(<strong key={k++} className="font-semibold text-zinc-100">{hit[2]}</strong>);
    else if (hit[3] !== undefined) parts.push(<em key={k++} className="italic text-zinc-300">{hit[3]}</em>);
    else if (hit[4] !== undefined) parts.push(
      <code key={k++} className="px-1.5 py-0.5 rounded-md text-[0.8em] font-mono text-violet-300" style={{ background: 'rgba(139,92,246,0.12)' }}>
        {hit[4]}
      </code>
    );
    else if (hit[5] !== undefined) parts.push(
      <code key={k++} className="px-1 py-0.5 rounded text-[0.8em] font-mono text-cyan-300" style={{ background: 'rgba(34,211,238,0.1)' }}>
        {hit[5]}
      </code>
    );
    last = hit.index + hit[0].length;
  }
  if (last < text.length) parts.push(<React.Fragment key={k}>{text.slice(last)}</React.Fragment>);
  return <React.Fragment key={key}>{parts}</React.Fragment>;
}

// ── Code block with copy ──────────────────────────────────────────────────────

function CodeBlock({ lang, content }: { lang: string; content: string }) {
  const [copied, setCopied] = useState(false);
  const [written, setWritten] = useState(false);
  const { pathname } = useLocation();
  const isNotebook = pathname === '/compiler';

  const copy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  const writeToEditor = () => {
    useAtlasStore.getState().setPendingEditorWrite({ code: content, language: lang });
    setWritten(true);
    setTimeout(() => setWritten(false), 2000);
  };

  return (
    <div className="my-3 rounded-2xl overflow-hidden group" style={{
      background: 'rgba(0,0,0,0.45)',
      border: '1px solid rgba(255,255,255,0.07)',
    }}>
      <div className="flex items-center justify-between px-4 py-2" style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <span className="text-[10px] font-mono font-medium tracking-widest uppercase text-zinc-500">
          {lang !== 'text' ? lang : 'code'}
        </span>
        <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          {isNotebook && (
            <button
              onClick={writeToEditor}
              className="flex items-center gap-1 text-[10px] transition-colors"
              style={{ color: written ? '#34d399' : '#6366f1' }}
              title="Write to compiler editor"
            >
              {written ? <Check className="w-3 h-3" /> : <FileEdit className="w-3 h-3" />}
              {written ? 'Written!' : 'Write to editor'}
            </button>
          )}
          <button
            onClick={copy}
            className="flex items-center gap-1 text-[10px] text-zinc-600 hover:text-zinc-300 transition-colors"
          >
            {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        </div>
      </div>
      <pre className="px-4 py-3 overflow-x-auto text-[12.5px] leading-relaxed font-mono text-zinc-200" style={{ scrollbarWidth: 'thin' }}>
        <code>{content}</code>
      </pre>
    </div>
  );
}

// ── Token renderer ────────────────────────────────────────────────────────────

function renderTokens(tokens: Token[]): React.ReactNode {
  const nodes: React.ReactNode[] = [];
  let bulletBuf: { type: 'bullet' | 'numbered'; n?: number; content: string }[] = [];
  let key = 0;

  const flushList = () => {
    if (!bulletBuf.length) return;
    const isNumbered = bulletBuf[0].type === 'numbered';
    const Tag = isNumbered ? 'ol' : 'ul';
    nodes.push(
      <Tag key={key++} className={`my-2 space-y-1 text-[13px] text-zinc-300 leading-relaxed ${isNumbered ? 'list-decimal list-inside' : 'list-none'}`}>
        {bulletBuf.map((b, i) => (
          <li key={i} className={isNumbered ? '' : 'flex gap-2 items-start'}>
            {!isNumbered && <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-indigo-500 flex-shrink-0" />}
            <span>{renderInline(b.content)}</span>
          </li>
        ))}
      </Tag>
    );
    bulletBuf = [];
  };

  for (const tok of tokens) {
    if (tok.type !== 'bullet' && tok.type !== 'numbered') flushList();

    switch (tok.type) {
      case 'code_block':
        if (tok.lang === 'mermaid') nodes.push(<WhiteboardView key={key++} code={tok.content} />);
        else nodes.push(<CodeBlock key={key++} lang={tok.lang} content={tok.content} />);
        break;

      case 'header': {
        const styles: Record<number, string> = {
          1: 'text-[15px] font-bold text-zinc-100 mt-4 mb-2',
          2: 'text-[13px] font-semibold text-zinc-200 mt-3 mb-1.5',
          3: 'text-[11px] font-semibold text-zinc-400 mt-2 mb-1 uppercase tracking-wider',
        };
        nodes.push(<p key={key++} className={styles[tok.level] ?? styles[2]}>{renderInline(tok.content)}</p>);
        break;
      }

      case 'bullet':
      case 'numbered':
        bulletBuf.push(tok);
        break;

      case 'hr':
        nodes.push(<hr key={key++} className="my-3 border-white/8" />);
        break;

      case 'blank':
        nodes.push(<div key={key++} className="h-2" />);
        break;

      case 'text':
        nodes.push(
          <p key={key++} className="text-[13.5px] text-zinc-300 leading-relaxed">
            {renderInline(tok.content)}
          </p>
        );
        break;
    }
  }
  flushList();
  return <>{nodes}</>;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function MessageBubble({ message, isNew }: Props) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={isNew ? { opacity: 0, y: 6 } : false}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.18, ease: 'easeOut' }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      {isUser ? (
        <div
          className="max-w-[82%] px-4 py-2.5 rounded-2xl rounded-tr-md text-[13.5px] text-zinc-100 leading-relaxed"
          style={{
            background: 'linear-gradient(135deg, rgba(99,102,241,0.3), rgba(79,70,229,0.2))',
            border: '1px solid rgba(99,102,241,0.25)',
          }}
        >
          {message.content}
        </div>
      ) : (
        <div className="max-w-[96%] min-w-0">
          {renderTokens(tokenise(message.content))}
          {message.streaming && (
            <motion.span
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ duration: 0.9, repeat: Infinity }}
              className="inline-block w-[3px] h-[14px] rounded-full bg-indigo-400 ml-0.5 align-middle"
            />
          )}
        </div>
      )}
    </motion.div>
  );
}
