import { Users, GitFork, ShieldCheck, Code2, FileJson2, Lock } from 'lucide-react';
import { AnimateIn } from '../../components/ui/AnimateIn';

// Mirrors the real contributor workflow in plugins/community/README.md and
// scripts/validate_plugin.py -- not aspirational marketing copy.
const COMMUNITY_POINTS = [
  {
    icon: GitFork,
    title: 'Open plugin directory',
    detail: 'Any algorithm can ship as a self-contained plugin under plugins/community/<category>/<slug>/ — manifest, implementation, and tests, reviewed via a real PR checklist.',
  },
  {
    icon: FileJson2,
    title: 'A real manifest schema, not guesswork',
    detail: 'manifest.json is JSON-Schema-validated: category, visualization type, Big-O complexity, and a references array for the papers, books, or videos your implementation is based on.',
  },
  {
    icon: ShieldCheck,
    title: 'Validate before you submit',
    detail: 'scripts/validate_plugin.py checks structure, manifest schema, and import safety locally — no waiting on CI to find a typo. The same validator runs automatically the moment you open a PR.',
  },
  {
    icon: Lock,
    title: 'Sandboxed by design',
    detail: "Every submitted algorithm.py goes through an AST import safety scan against an explicit allowlist (algorithm_atlas_sdk, math, random, heapq, and a handful more) before it's ever imported and run.",
  },
  {
    icon: Code2,
    title: 'Embed anywhere',
    detail: 'Every algorithm — first-party or community — gets a drop-in <iframe> with seed, size, and autoplay as query params. No extra work for contributors.',
  },
];

export function RoadmapCommunitySection() {
  return (
    <section className="py-24 px-4">
      <div className="max-w-4xl mx-auto">
        <AnimateIn className="text-center mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-teal-500/30 bg-teal-500/10 text-teal-300 text-xs font-medium mb-6 mx-auto">
            <Users size={12} />
            Community
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">Built in the open.</h2>
          <p className="text-zinc-400 text-lg max-w-2xl mx-auto">
            Every algorithm in the catalog — first-party or contributed — goes through the exact
            same pipeline: a schema-checked manifest, a sandboxed import scan, and an automated
            validator that runs locally before it ever touches CI.
          </p>
        </AnimateIn>

        <div className="grid sm:grid-cols-2 gap-x-10 gap-y-8 mb-12">
          {COMMUNITY_POINTS.map((p, i) => {
            const Icon = p.icon;
            return (
              <AnimateIn key={p.title} delay={i * 0.05}>
                <div className="flex gap-4">
                  <div className="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center flex-shrink-0">
                    <Icon size={17} className="text-teal-400" />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold text-sm mb-1">{p.title}</h3>
                    <p className="text-zinc-400 text-sm leading-relaxed">{p.detail}</p>
                  </div>
                </div>
              </AnimateIn>
            );
          })}
        </div>

        <AnimateIn delay={0.2} className="max-w-xl mx-auto rounded-xl border border-white/10 bg-[#0D0D10] p-4 font-mono text-xs text-zinc-400 overflow-x-auto text-center">
          <span className="text-zinc-600">{'<iframe '}</span>
          <span className="text-emerald-400">src</span>
          <span className="text-zinc-600">=</span>
          <span className="text-amber-300">"/embed/quick-sort?autoplay=1"</span>
          <span className="text-zinc-600">{' />'}</span>
        </AnimateIn>
      </div>
    </section>
  );
}
