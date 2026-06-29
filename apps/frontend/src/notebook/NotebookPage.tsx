/**
 * NotebookPage — polyglot Monaco terminal.
 *
 * Route: /notebook
 * 10 languages, VS Code-quality editor, terminal-style run history.
 * Layout: IDE split — editor left, output right (Programiz-style).
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import Editor, { type OnMount } from '@monaco-editor/react';
import { Play, Save, ChevronDown, Trash2, X, Clock, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api, type ExperimentSummary } from '../core/api/client';
import { cn } from '../lib/utils';

// ── Language registry ──────────────────────────────────────────────────────────

interface LangDef {
  id: string;
  label: string;
  monacoId: string;
  ext: string;        // file extension for the tab
  dot: string;        // tailwind bg color class for status dot
  badge: string;      // tailwind text color class for badge text
  accentHex: string;  // raw hex for dynamic inline styles
  starter: string;
}

const LANGS: LangDef[] = [
  {
    id: 'python', label: 'Python', monacoId: 'python', ext: 'py',
    dot: 'bg-blue-400', badge: 'text-blue-400', accentHex: '#60a5fa',
    starter:
`# Python 3  —  Ctrl+Enter to run
def fibonacci(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

for i in range(10):
    print(f"fib({i:2d}) = {fibonacci(i)}")`,
  },
  {
    id: 'javascript', label: 'JavaScript', monacoId: 'javascript', ext: 'js',
    dot: 'bg-yellow-400', badge: 'text-yellow-400', accentHex: '#facc15',
    starter:
`// JavaScript (Node.js)  —  Ctrl+Enter to run
const fibonacci = (n) => {
  let [a, b] = [0, 1];
  for (let i = 0; i < n; i++) [a, b] = [b, a + b];
  return a;
};

for (let i = 0; i < 10; i++) {
  console.log(\`fib(\${i.toString().padStart(2)}) = \${fibonacci(i)}\`);
}`,
  },
  {
    id: 'typescript', label: 'TypeScript', monacoId: 'typescript', ext: 'ts',
    dot: 'bg-sky-400', badge: 'text-sky-400', accentHex: '#38bdf8',
    starter:
`// TypeScript (tsx)  —  Ctrl+Enter to run
const fibonacci = (n: number): number => {
  let [a, b] = [0, 1];
  for (let i = 0; i < n; i++) [a, b] = [b, a + b];
  return a;
};

for (let i = 0; i < 10; i++) {
  console.log(\`fib(\${String(i).padStart(2)}) = \${fibonacci(i)}\`);
}`,
  },
  {
    id: 'cpp', label: 'C++', monacoId: 'cpp', ext: 'cpp',
    dot: 'bg-violet-400', badge: 'text-violet-400', accentHex: '#a78bfa',
    starter:
`// C++17  —  Ctrl+Enter to run
#include <iostream>

int fibonacci(int n) {
    int a = 0, b = 1;
    for (int i = 0; i < n; i++) { int t = b; b = a + b; a = t; }
    return a;
}

int main() {
    for (int i = 0; i < 10; i++)
        std::cout << "fib(" << i << ") = " << fibonacci(i) << "\\n";
}`,
  },
  {
    id: 'c', label: 'C', monacoId: 'c', ext: 'c',
    dot: 'bg-zinc-400', badge: 'text-zinc-400', accentHex: '#a1a1aa',
    starter:
`/* C17  —  Ctrl+Enter to run */
#include <stdio.h>

int fibonacci(int n) {
    int a = 0, b = 1;
    for (int i = 0; i < n; i++) { int t = b; b = a + b; a = t; }
    return a;
}

int main(void) {
    for (int i = 0; i < 10; i++)
        printf("fib(%d) = %d\\n", i, fibonacci(i));
    return 0;
}`,
  },
  {
    id: 'java', label: 'Java', monacoId: 'java', ext: 'java',
    dot: 'bg-orange-400', badge: 'text-orange-400', accentHex: '#fb923c',
    starter:
`// Java  —  Ctrl+Enter to run
public class Main {
    static int fibonacci(int n) {
        int a = 0, b = 1;
        for (int i = 0; i < n; i++) { int t = b; b = a + b; a = t; }
        return a;
    }

    public static void main(String[] args) {
        for (int i = 0; i < 10; i++)
            System.out.println("fib(" + i + ") = " + fibonacci(i));
    }
}`,
  },
  {
    id: 'go', label: 'Go', monacoId: 'go', ext: 'go',
    dot: 'bg-cyan-400', badge: 'text-cyan-400', accentHex: '#22d3ee',
    starter:
`// Go  —  Ctrl+Enter to run
package main

import "fmt"

func fibonacci(n int) int {
	a, b := 0, 1
	for i := 0; i < n; i++ {
		a, b = b, a+b
	}
	return a
}

func main() {
	for i := 0; i < 10; i++ {
		fmt.Printf("fib(%d) = %d\\n", i, fibonacci(i))
	}
}`,
  },
  {
    id: 'rust', label: 'Rust', monacoId: 'rust', ext: 'rs',
    dot: 'bg-orange-600', badge: 'text-orange-500', accentHex: '#ea580c',
    starter:
`// Rust  —  Ctrl+Enter to run
fn fibonacci(n: u64) -> u64 {
    let (mut a, mut b) = (0, 1);
    for _ in 0..n { let t = b; b = a + b; a = t; }
    a
}

fn main() {
    for i in 0..10 {
        println!("fib({:2}) = {}", i, fibonacci(i));
    }
}`,
  },
  {
    id: 'shell', label: 'Shell', monacoId: 'shell', ext: 'sh',
    dot: 'bg-emerald-400', badge: 'text-emerald-400', accentHex: '#34d399',
    starter:
`# Shell (Bash / cmd)  —  Ctrl+Enter to run
echo "System info:"
echo "  OS: $(uname -s 2>/dev/null || echo Windows)"
echo "  Date: $(date)"
echo ""
for i in 1 2 3 4 5; do
  echo "  Line $i"
done`,
  },
  {
    id: 'ruby', label: 'Ruby', monacoId: 'ruby', ext: 'rb',
    dot: 'bg-red-400', badge: 'text-red-400', accentHex: '#f87171',
    starter:
`# Ruby  —  Ctrl+Enter to run
def fibonacci(n)
  a, b = 0, 1
  n.times { a, b = b, a + b }
  a
end

10.times do |i|
  puts "fib(#{i.to_s.rjust(2)}) = #{fibonacci(i)}"
end`,
  },
  {
    id: 'kotlin', label: 'Kotlin', monacoId: 'kotlin', ext: 'kt',
    dot: 'bg-purple-500', badge: 'text-purple-400', accentHex: '#a855f7',
    starter:
`// Kotlin  —  Ctrl+Enter to run
fun fibonacci(n: Int): Int {
    var a = 0; var b = 1
    repeat(n) { val t = b; b = a + b; a = t }
    return a
}

fun main() {
    for (i in 0 until 10) {
        println("fib(\${i.toString().padStart(2)}) = \${fibonacci(i)}")
    }
}`,
  },
  {
    id: 'swift', label: 'Swift', monacoId: 'swift', ext: 'swift',
    dot: 'bg-rose-400', badge: 'text-rose-400', accentHex: '#fb7185',
    starter:
`// Swift  —  Ctrl+Enter to run
func fibonacci(_ n: Int) -> Int {
    var a = 0, b = 1
    for _ in 0..<n { let t = b; b = a + b; a = t }
    return a
}

for i in 0..<10 {
    print(String(format: "fib(%2d) = %d", i, fibonacci(i)))
}`,
  },
  {
    id: 'r', label: 'R', monacoId: 'r', ext: 'r',
    dot: 'bg-blue-500', badge: 'text-blue-500', accentHex: '#3b82f6',
    starter:
`# R  —  Ctrl+Enter to run
fibonacci <- function(n) {
  a <- 0; b <- 1
  for (i in seq_len(n)) {
    temp <- b; b <- a + b; a <- temp
  }
  a
}

for (i in 0:9) {
  cat(sprintf("fib(%2d) = %d\\n", i, fibonacci(i)))
}`,
  },
  {
    id: 'csharp', label: 'C#', monacoId: 'csharp', ext: 'cs',
    dot: 'bg-fuchsia-400', badge: 'text-fuchsia-400', accentHex: '#e879f9',
    starter:
`// C#  —  Ctrl+Enter to run
using System;

class Program {
    static int Fibonacci(int n) {
        int a = 0, b = 1;
        for (int i = 0; i < n; i++) { int t = b; b = a + b; a = t; }
        return a;
    }

    static void Main() {
        for (int i = 0; i < 10; i++)
            Console.WriteLine($"fib({i,2}) = {Fibonacci(i)}");
    }
}`,
  },
  {
    id: 'php', label: 'PHP', monacoId: 'php', ext: 'php',
    dot: 'bg-indigo-400', badge: 'text-indigo-400', accentHex: '#818cf8',
    starter:
`<?php
// PHP  —  Ctrl+Enter to run
function fibonacci(int $n): int {
    $a = 0; $b = 1;
    for ($i = 0; $i < $n; $i++) {
        [$a, $b] = [$b, $a + $b];
    }
    return $a;
}

for ($i = 0; $i < 10; $i++) {
    echo sprintf("fib(%2d) = %d\\n", $i, fibonacci($i));
}`,
  },
  {
    id: 'scala', label: 'Scala', monacoId: 'scala', ext: 'scala',
    dot: 'bg-red-600', badge: 'text-red-500', accentHex: '#dc2626',
    starter:
`// Scala  —  Ctrl+Enter to run
def fibonacci(n: Int): Int = {
  var a = 0; var b = 1
  for (_ <- 0 until n) { val t = b; b = a + b; a = t }
  a
}

for (i <- 0 until 10) {
  println(f"fib($i%2d) = \${fibonacci(i)}")
}`,
  },
  {
    id: 'perl', label: 'Perl', monacoId: 'perl', ext: 'pl',
    dot: 'bg-slate-400', badge: 'text-slate-400', accentHex: '#94a3b8',
    starter:
`# Perl  —  Ctrl+Enter to run
use strict;
use warnings;

sub fibonacci {
    my ($n) = @_;
    my ($a, $b) = (0, 1);
    for (1..$n) { ($a, $b) = ($b, $a + $b) }
    return $a;
}

for my $i (0..9) {
    printf("fib(%2d) = %d\\n", $i, fibonacci($i));
}`,
  },
];

const LANG_MAP = Object.fromEntries(LANGS.map((l) => [l.id, l]));

// ── Run history ────────────────────────────────────────────────────────────────

interface RunEntry {
  id: string;
  seq: number;
  lang: string;
  source: string;
  output: string;
  error: string;
  duration_ms: number;
  ts: Date;
}

let _seq = 0;

// ── Save dialog ────────────────────────────────────────────────────────────────

function SaveDialog({
  onSave, onClose, saving,
}: { onSave: (name: string, notes: string) => void; onClose: () => void; saving: boolean }) {
  const [name, setName] = useState('Untitled Session');
  const [notes, setNotes] = useState('');
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="rounded-2xl bg-[#111113] border border-white/10 shadow-[0_24px_64px_rgba(0,0,0,0.6)] p-6 w-96">
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-white font-semibold">Save Session</h3>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-white/5 text-zinc-500 hover:text-white transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>
        <label className="block text-xs text-zinc-500 mb-1.5">Name</label>
        <input
          value={name} onChange={(e) => setName(e.target.value)} autoFocus
          className="w-full bg-[#18181B] border border-white/8 rounded-xl px-4 py-2.5 text-sm text-white mb-4 outline-none focus:border-indigo-500/50 transition-colors"
        />
        <label className="block text-xs text-zinc-500 mb-1.5">Notes</label>
        <textarea
          value={notes} onChange={(e) => setNotes(e.target.value)} rows={3}
          className="w-full bg-[#18181B] border border-white/8 rounded-xl px-4 py-2.5 text-sm text-white mb-5 outline-none focus:border-indigo-500/50 transition-colors resize-none"
          placeholder="Optional notes…"
        />
        <div className="flex justify-end gap-2">
          <button onClick={onClose} className="px-4 py-2 text-sm text-zinc-400 hover:text-white transition-colors rounded-xl hover:bg-white/5">Cancel</button>
          <button
            onClick={() => onSave(name, notes)} disabled={saving || !name.trim()}
            className="flex items-center gap-2 px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl transition-colors"
          >
            <Save className="w-3.5 h-3.5" />
            {saving ? 'Saving…' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Language dropdown ──────────────────────────────────────────────────────────

function LangPicker({ current, onChange }: { current: LangDef; onChange: (l: LangDef) => void }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#1A1A2A] border border-white/10 hover:border-white/20 transition-colors text-sm"
      >
        <span className={cn('w-2 h-2 rounded-full', current.dot)} />
        <span className="text-white font-medium">{current.label}</span>
        <ChevronDown className={cn('w-3.5 h-3.5 text-zinc-500 transition-transform', open && 'rotate-180')} />
      </button>

      {open && (
        <div className="absolute top-full mt-1 left-0 z-40 w-44 rounded-xl bg-[#1A1A2E] border border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.5)] overflow-hidden py-1">
          {LANGS.map((l) => (
            <button
              key={l.id}
              onClick={() => { onChange(l); setOpen(false); }}
              className={cn(
                'w-full flex items-center gap-2.5 px-3 py-2 text-sm transition-colors hover:bg-white/5',
                l.id === current.id ? 'text-white' : 'text-zinc-400 hover:text-white',
              )}
            >
              <span className={cn('w-2 h-2 rounded-full flex-shrink-0', l.dot)} />
              <span>{l.label}</span>
              {l.id === current.id && <span className="ml-auto text-indigo-400">✓</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Saved sessions overlay ─────────────────────────────────────────────────────

function LoadPanel({ onLoad, onClose }: { onLoad: (e: ExperimentSummary) => void; onClose: () => void }) {
  const [exps, setExps] = useState<ExperimentSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.experiments.list({ limit: 20 })
      .then((r) => setExps(r.items))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="absolute inset-y-0 right-0 w-72 bg-[#0F0F18] border-l border-white/8 flex flex-col z-20 shadow-[-8px_0_32px_rgba(0,0,0,0.4)]">
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/8">
        <span className="text-sm text-white font-medium">Saved Sessions</span>
        <button onClick={onClose} className="p-1 rounded hover:bg-white/5 text-zinc-500 hover:text-white transition-colors">
          <X className="w-4 h-4" />
        </button>
      </div>
      <div className="flex-1 overflow-y-auto divide-y divide-white/5">
        {loading && <div className="px-4 py-4 text-sm text-zinc-500">Loading…</div>}
        {!loading && exps.length === 0 && (
          <div className="px-4 py-4 text-sm text-zinc-500">No saved sessions yet.</div>
        )}
        {exps.map((e) => (
          <div key={e.id} className="flex items-center justify-between px-4 py-3 hover:bg-white/3 transition-colors">
            <div className="min-w-0">
              <p className="text-sm text-white truncate">{e.name}</p>
              <p className="text-xs text-zinc-600 mt-0.5">
                {e.cell_count} cell{e.cell_count !== 1 ? 's' : ''} · {new Date(e.created_at).toLocaleDateString()}
              </p>
            </div>
            <button
              onClick={() => { onLoad(e); onClose(); }}
              className="ml-3 flex-shrink-0 px-2.5 py-1 text-xs bg-indigo-600/20 hover:bg-indigo-600/40 border border-indigo-500/25 text-indigo-300 rounded-lg transition-colors"
            >
              Load
            </button>
          </div>
        ))}
      </div>
      <div className="px-4 py-3 border-t border-white/8">
        <Link to="/experiments" className="block text-center text-xs text-zinc-500 hover:text-indigo-400 transition-colors">
          View all experiments →
        </Link>
      </div>
    </div>
  );
}

// ── Main page ──────────────────────────────────────────────────────────────────

export function NotebookPage() {
  const [lang, setLang]         = useState<LangDef>(LANGS[0]);
  const [code, setCode]         = useState(LANGS[0].starter);
  const [runs, setRuns]         = useState<RunEntry[]>([]);
  const [running, setRunning]   = useState(false);
  const [splitPct, setSplitPct] = useState(55); // editor width %
  const [showSave, setShowSave] = useState(false);
  const [showLoad, setShowLoad] = useState(false);
  const [saving, setSaving]     = useState(false);
  const [toast, setToast]       = useState<string | null>(null);
  const editorRef   = useRef<Parameters<OnMount>[0] | null>(null);
  const outputRef   = useRef<HTMLDivElement>(null);
  const toastTimer  = useRef<ReturnType<typeof setTimeout>>();
  const dragRef     = useRef<{ startX: number; startPct: number; containerW: number } | null>(null);

  const flash = (msg: string) => {
    setToast(msg);
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 3000);
  };

  // Auto-scroll output on new run
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [runs]);

  const runCode = useCallback(async () => {
    if (running) return;
    const source = editorRef.current?.getValue() ?? code;
    if (!source.trim()) return;
    setRunning(true);
    const seq = ++_seq;
    try {
      const res = await api.notebook.run({ source, language: lang.id });
      setRuns((prev) => [
        ...prev,
        { id: `${Date.now()}-${seq}`, seq, lang: lang.id, source, ...res, ts: new Date() },
      ]);
    } catch (e) {
      setRuns((prev) => [
        ...prev,
        { id: `${Date.now()}-${seq}`, seq, lang: lang.id, source, output: '', error: String(e), duration_ms: 0, ts: new Date() },
      ]);
    } finally {
      setRunning(false);
    }
  }, [running, lang, code]);

  const handleEditorMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => { runCode(); });
    editor.focus();
  };

  const handleLangChange = (next: LangDef) => {
    const currentValue = editorRef.current?.getValue() ?? code;
    const isStarter = LANGS.some((l) => l.starter === currentValue);
    setLang(next);
    if (isStarter) {
      setCode(next.starter);
      editorRef.current?.setValue(next.starter);
    }
  };

  const handleSave = async (name: string, notes: string) => {
    setSaving(true);
    const source = editorRef.current?.getValue() ?? code;
    try {
      const exp = await api.experiments.create({ name, algorithm_slug: 'notebook', notes, seed: 0, params: { language: lang.id } });
      await api.experiments.addCell(exp.id, { source, order: 0, language: lang.id });
      setShowSave(false);
      flash(`Saved "${name}"`);
    } catch (e) {
      flash(`Save failed: ${e}`);
    } finally {
      setSaving(false);
    }
  };

  const handleLoad = async (exp: ExperimentSummary) => {
    try {
      const detail = await api.experiments.get(exp.id);
      const cell = detail.cells.sort((a: { order: number }, b: { order: number }) => a.order - b.order)[0];
      if (cell) {
        const loadedLang = LANG_MAP[cell.language] ?? LANGS[0];
        setLang(loadedLang);
        setCode(cell.source);
        editorRef.current?.setValue(cell.source);
        const model = editorRef.current?.getModel();
        if (model) {
          // @ts-expect-error — monaco is global after mount
          window.monaco?.editor.setModelLanguage(model, loadedLang.monacoId);
        }
      }
      flash(`Loaded "${exp.name}"`);
    } catch (e) {
      flash(`Load failed: ${e}`);
    }
  };

  // ── Horizontal resize handle ──────────────────────────────────────────────────
  const startHorizDrag = (e: React.MouseEvent) => {
    e.preventDefault();
    const container = (e.currentTarget as HTMLElement).parentElement!;
    dragRef.current = {
      startX: e.clientX,
      startPct: splitPct,
      containerW: container.getBoundingClientRect().width,
    };
    const onMove = (ev: MouseEvent) => {
      if (!dragRef.current) return;
      const delta = ev.clientX - dragRef.current.startX;
      const newPct = dragRef.current.startPct + (delta / dragRef.current.containerW) * 100;
      setSplitPct(Math.max(30, Math.min(75, newPct)));
    };
    const onUp = () => {
      dragRef.current = null;
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
    };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
  };

  const filename = `main.${lang.ext}`;
  const lastRun = runs[runs.length - 1];

  return (
    <div className="flex flex-col" style={{ height: 'calc(100vh - 5rem)' }}>

      {/* ── Top bar: file tab + language picker + Run button ──────────── */}
      <div className="flex items-stretch bg-[#0D0D14] border-b border-white/8 flex-shrink-0 select-none" style={{ height: 44 }}>

        {/* File tab — styled like VS Code active tab */}
        <div
          className="flex items-center gap-2 px-4 border-r border-white/8 relative"
          style={{ borderBottom: `2px solid ${lang.accentHex}` }}
        >
          <span className={cn('w-2 h-2 rounded-full flex-shrink-0', lang.dot)} />
          <span className="text-sm text-white font-mono tracking-wide">{filename}</span>
        </div>

        {/* Toast */}
        {toast && (
          <span className="flex items-center text-xs text-emerald-400 font-mono px-4 flex-shrink-0">
            {toast}
          </span>
        )}

        <div className="flex-1" />

        {/* Right cluster: lang picker + Load + Save + Run */}
        <div className="flex items-center gap-2 px-3">
          <LangPicker current={lang} onChange={handleLangChange} />

          <div className="w-px h-5 bg-white/10" />

          <button
            onClick={() => setShowLoad((v) => !v)}
            className={cn(
              'px-3 py-1.5 text-xs rounded-lg border transition-colors font-medium',
              showLoad
                ? 'bg-indigo-600/20 border-indigo-500/40 text-indigo-300'
                : 'bg-[#1A1A2A] border-white/8 text-zinc-400 hover:text-white hover:border-white/15',
            )}
          >
            Load
          </button>
          <button
            onClick={() => setShowSave(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#1A1A2A] border border-white/8 text-zinc-400 hover:text-white text-xs font-medium transition-colors hover:border-white/15"
          >
            <Save className="w-3.5 h-3.5" /> Save
          </button>

          {/* Run button — prominent, Programiz-style */}
          <button
            onClick={runCode}
            disabled={running}
            className={cn(
              'flex items-center gap-2 px-5 h-8 rounded-lg text-sm font-semibold transition-all duration-200',
              running
                ? 'bg-indigo-700/60 text-indigo-300 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-[0_0_16px_rgba(99,102,241,0.35)] hover:shadow-[0_0_22px_rgba(99,102,241,0.5)]',
            )}
          >
            {running ? (
              <>
                <span className="w-3.5 h-3.5 rounded-full border-2 border-indigo-300/40 border-t-indigo-200 animate-spin" />
                Running
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5" fill="currentColor" />
                Run
              </>
            )}
          </button>
        </div>
      </div>

      {/* ── Main area: editor (left) + output (right) ─────────────────── */}
      <div className="flex flex-1 min-h-0 relative overflow-hidden">

        {/* Editor panel */}
        <div style={{ width: `${splitPct}%` }} className="flex flex-col min-h-0 min-w-0">
          <Editor
            height="100%"
            language={lang.monacoId}
            value={code}
            theme="vs-dark"
            onMount={handleEditorMount}
            onChange={(v) => setCode(v ?? '')}
            options={{
              fontSize: 14,
              fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
              fontLigatures: true,
              lineHeight: 22,
              padding: { top: 16, bottom: 16 },
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              wordWrap: 'on',
              smoothScrolling: true,
              cursorBlinking: 'phase',
              cursorSmoothCaretAnimation: 'on',
              tabSize: 2,
              renderLineHighlight: 'all',
              bracketPairColorization: { enabled: true },
              guides: { bracketPairs: true, indentation: true },
              suggest: { showSnippets: true },
              quickSuggestions: { other: true, comments: false, strings: false },
              overviewRulerBorder: false,
              overviewRulerLanes: 0,
              hideCursorInOverviewRuler: true,
              scrollbar: { verticalScrollbarSize: 4, horizontalScrollbarSize: 4 },
              glyphMargin: false,
              folding: true,
              lineNumbers: 'on',
              lineDecorationsWidth: 8,
              lineNumbersMinChars: 3,
            }}
          />
        </div>

        {/* Horizontal resize handle */}
        <div
          onMouseDown={startHorizDrag}
          className="w-1 flex-shrink-0 cursor-col-resize bg-white/5 hover:bg-indigo-500/50 active:bg-indigo-500/70 transition-colors z-10"
        />

        {/* Output panel */}
        <div className="flex-1 min-w-0 flex flex-col bg-[#080810]">

          {/* Output header */}
          <div className="flex items-center justify-between px-4 py-2 border-b border-white/8 flex-shrink-0 bg-[#0C0C16]">
            <div className="flex items-center gap-3">
              <span className="text-xs font-mono text-zinc-500 tracking-widest uppercase">Output</span>
              {runs.length > 0 && (
                <span className="text-[10px] text-zinc-700 font-mono">
                  {runs.length} run{runs.length !== 1 ? 's' : ''}
                </span>
              )}
            </div>
            {runs.length > 0 && (
              <button
                onClick={() => setRuns([])}
                className="flex items-center gap-1 text-xs text-zinc-700 hover:text-zinc-400 transition-colors"
              >
                <Trash2 className="w-3 h-3" /> Clear
              </button>
            )}
          </div>

          {/* Output content */}
          <div ref={outputRef} className="flex-1 overflow-y-auto font-mono text-sm leading-relaxed">
            {runs.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full gap-4 text-center px-6">
                <div className="w-10 h-10 rounded-xl bg-white/3 border border-white/8 flex items-center justify-center">
                  <Play className="w-4 h-4 text-zinc-600" />
                </div>
                <div>
                  <p className="text-zinc-500 text-sm">Run your code to see output</p>
                  <p className="text-zinc-700 text-xs mt-1">
                    <kbd className="px-1.5 py-0.5 bg-white/5 rounded text-[10px]">Ctrl</kbd>
                    {' + '}
                    <kbd className="px-1.5 py-0.5 bg-white/5 rounded text-[10px]">Enter</kbd>
                    {' to run'}
                  </p>
                </div>
              </div>
            ) : (
              <div>
                {runs.map((run, idx) => {
                  const langDef = LANG_MAP[run.lang];
                  const hasError = run.error.trim().length > 0;
                  const time = run.ts.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                  const duration = run.duration_ms < 1000
                    ? `${run.duration_ms.toFixed(0)}ms`
                    : `${(run.duration_ms / 1000).toFixed(2)}s`;
                  const isLatest = idx === runs.length - 1;
                  return (
                    <div
                      key={run.id}
                      className={cn('border-b border-white/4', isLatest && 'border-b-0')}
                    >
                      {/* Run header line — terminal prompt style */}
                      <div className={cn(
                        'flex items-center gap-2 px-4 py-2 text-xs',
                        isLatest ? 'bg-white/[0.03]' : 'bg-transparent',
                      )}>
                        {hasError
                          ? <AlertCircle className="w-3 h-3 text-red-400 flex-shrink-0" />
                          : <CheckCircle2 className="w-3 h-3 text-emerald-500 flex-shrink-0" />}
                        <span className="text-zinc-500">❯</span>
                        {langDef && (
                          <span style={{ color: langDef.accentHex }} className="font-semibold">
                            {langDef.label}
                          </span>
                        )}
                        <span className="text-zinc-600 flex items-center gap-1">
                          <Clock className="w-2.5 h-2.5" />
                          {duration}
                        </span>
                        <span className="text-zinc-700 ml-auto">{time}</span>
                      </div>

                      {/* Output / error content */}
                      <div className="px-4 pb-3">
                        {run.output && (
                          <pre className="text-[#50FA7B] whitespace-pre-wrap text-xs leading-relaxed overflow-x-auto">
                            {run.output}
                          </pre>
                        )}
                        {hasError && (
                          <pre className="text-[#FF5555] whitespace-pre-wrap text-xs leading-relaxed overflow-x-auto">
                            {run.error}
                          </pre>
                        )}
                        {!run.output && !hasError && (
                          <span className="text-zinc-700 text-xs italic">(no output)</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Load panel overlay */}
        {showLoad && <LoadPanel onLoad={handleLoad} onClose={() => setShowLoad(false)} />}
      </div>

      {/* ── VS Code-style status bar ───────────────────────────────────── */}
      <div
        className="flex items-center justify-between px-4 flex-shrink-0 text-[10px] font-mono border-t border-white/5"
        style={{ height: 24, backgroundColor: lang.accentHex + '22' }}
      >
        <div className="flex items-center gap-3">
          <span className={cn('flex items-center gap-1.5 font-semibold', lang.badge)}>
            <span className={cn('w-1.5 h-1.5 rounded-full', lang.dot)} />
            {lang.label}
          </span>
          <span className="text-zinc-600">{filename}</span>
        </div>
        <div className="flex items-center gap-3 text-zinc-600">
          {lastRun && (
            <span className={cn(
              'flex items-center gap-1',
              lastRun.error.trim() ? 'text-red-500/70' : 'text-emerald-600',
            )}>
              {lastRun.error.trim() ? '✗' : '✓'}
              {' '}
              {lastRun.duration_ms < 1000 ? `${lastRun.duration_ms.toFixed(0)}ms` : `${(lastRun.duration_ms / 1000).toFixed(2)}s`}
            </span>
          )}
          <span>
            <kbd className="px-1 py-0.5 bg-white/5 rounded text-[9px]">Ctrl+Enter</kbd>
            {' run'}
          </span>
        </div>
      </div>

      {/* Dialogs */}
      {showSave && <SaveDialog onSave={handleSave} onClose={() => setShowSave(false)} saving={saving} />}
    </div>
  );
}
