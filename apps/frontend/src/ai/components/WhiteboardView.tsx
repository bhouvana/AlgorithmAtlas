/**
 * WhiteboardView — renders a Mermaid diagram string as an SVG.
 * Mermaid is lazy-imported (~2MB) so it doesn't affect the main bundle.
 */
import { useEffect, useRef, useState } from 'react';

interface Props {
  code: string;
}

let mermaidLoaded = false;
let mermaidInstance: { render: (id: string, text: string) => Promise<{ svg: string }> } | null = null;

async function getMermaid() {
  if (mermaidLoaded && mermaidInstance) return mermaidInstance;
  const mod = await import('mermaid');
  const m = mod.default;
  m.initialize({
    startOnLoad: false,
    theme: 'dark',
    themeVariables: {
      background: '#09090B',
      primaryColor: '#4f46e5',
      primaryTextColor: '#e4e4e7',
      lineColor: '#52525b',
      secondaryColor: '#18181b',
      tertiaryColor: '#27272a',
    },
    fontFamily: 'JetBrains Mono, Fira Code, monospace',
    fontSize: 13,
  });
  mermaidLoaded = true;
  mermaidInstance = m;
  return m;
}

let _idCounter = 0;

export function WhiteboardView({ code }: Props) {
  const [svg, setSvg] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const idRef = useRef(`atlas-mermaid-${++_idCounter}`);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError('');

    getMermaid()
      .then((m) => m.render(idRef.current, code.trim()))
      .then(({ svg: rendered }) => {
        if (!cancelled) {
          setSvg(rendered);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(String(err));
          setLoading(false);
        }
      });

    return () => { cancelled = true; };
  }, [code]);

  if (loading) {
    return (
      <div className="flex items-center gap-2 p-3 text-zinc-500 text-xs">
        <div className="w-3.5 h-3.5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        Rendering diagram…
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-3 text-xs text-red-400 font-mono">
        Diagram error: {error}
      </div>
    );
  }

  return (
    <div
      className="rounded-xl overflow-hidden bg-[#0f0f18] border border-charcoal/10 p-4 my-2"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
