import { Users, GitFork, ShieldCheck, Code2, CheckCircle2, Loader2, Circle } from 'lucide-react';
import { AnimateIn } from '../../components/ui/AnimateIn';

const COMMUNITY_POINTS = [
  {
    icon: GitFork,
    title: 'Open plugin directory',
    detail: 'Any algorithm can ship as a self-contained plugin — manifest, implementation, and tests — reviewed via a real PR checklist.',
  },
  {
    icon: ShieldCheck,
    title: 'Validate before you submit',
    detail: 'scripts/validate_plugin.py checks structure, manifest schema, and import safety locally — no waiting on CI to find a typo.',
  },
  {
    icon: Code2,
    title: 'Embed anywhere',
    detail: 'Every algorithm gets a drop-in <iframe> with seed, size, and autoplay as query params.',
  },
];

// Reflects PROGRESS.md phase history + the live AtlasCode dual-mode ledger —
// kept in sync with docs/atlascode-resume.md and docs/atlascode-complete-matrix.md,
// not aspirational marketing copy. Language coverage % should be refreshed from
// docs/atlascode-complete-matrix.json (regenerate via
// `python scripts/generate_honest_matrix_report.py`) whenever this is updated.
const ROADMAP = [
  { status: 'done' as const, title: '250 algorithms, 19 categories', detail: 'Phase 2 & 7 — full catalog with 13 visualization types, all wired.' },
  { status: 'done' as const, title: 'WASM + Rust execution engine', detail: 'Phase 3 & 4 — browser-native sort simulation, zero server round-trip.' },
  { status: 'done' as const, title: 'Polyglot notebook kernel', detail: 'Phase 5 — compile and visualize C, C++, Java, C#, and Python inline.' },
  { status: 'done' as const, title: 'Community platform + embeds', detail: 'Phase 6 — plugin directory, embed widget, synchronized comparison.' },
  { status: 'done' as const, title: 'All 216 AtlasCode problems complete', detail: 'Every problem has a canonical implementation, a working judge, and a verified reference solution — solvable today.' },
  { status: 'done' as const, title: 'Atlas AI is mode- and language-aware', detail: "Knows whether you're in LeetCode Mode or Codeforces Mode and never gives the wrong kind of advice (no \"read from stdin\" hints inside a function-only problem, or vice versa) — verified live across languages. Runs on a 3-key resilient pool (Groq + 2 Ollama Cloud keys) with automatic failover, wired into the Render deployment." },
  { status: 'active' as const, title: 'AtlasCode language coverage', detail: 'LeetCode Mode + Codeforces Mode across 17 languages, tracked cell-by-cell — 48.81% verified and growing. Additional languages per problem are an enhancement, not a completion blocker.' },
  { status: 'next' as const, title: 'Submit workflow in the AtlasCode UI', detail: 'Hidden-test scoring, submission history, and runtime/memory percentiles are backend-complete — surfacing them in the workspace UI is next.' },
];

export function RoadmapCommunitySection() {
  return (
    <section className="py-24 px-4">
      <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16">
        {/* Community */}
        <AnimateIn direction="right">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-teal-500/30 bg-teal-500/10 text-teal-300 text-xs font-medium mb-6">
            <Users size={12} />
            Community
          </div>
          <h2 className="text-3xl font-bold tracking-tight mb-8">Built in the open.</h2>

          <div className="flex flex-col gap-6">
            {COMMUNITY_POINTS.map((p) => {
              const Icon = p.icon;
              return (
                <div key={p.title} className="flex gap-4">
                  <div className="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center flex-shrink-0">
                    <Icon size={17} className="text-teal-400" />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold text-sm mb-1">{p.title}</h3>
                    <p className="text-zinc-400 text-sm leading-relaxed">{p.detail}</p>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-8 rounded-xl border border-white/10 bg-[#0D0D10] p-4 font-mono text-xs text-zinc-400 overflow-x-auto">
            <span className="text-zinc-600">{'<iframe '}</span>
            <span className="text-emerald-400">src</span>
            <span className="text-zinc-600">=</span>
            <span className="text-amber-300">"/embed/quick-sort?autoplay=1"</span>
            <span className="text-zinc-600">{' />'}</span>
          </div>
        </AnimateIn>

        {/* Roadmap */}
        <AnimateIn direction="left" delay={0.1}>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-xs font-medium mb-6">
            Roadmap
          </div>
          <h2 className="text-3xl font-bold tracking-tight mb-8">Shipped, and still shipping.</h2>

          <div className="relative flex flex-col gap-6">
            <div className="absolute left-[15px] top-2 bottom-2 w-px bg-white/10" />
            {ROADMAP.map((r) => (
              <div key={r.title} className="relative flex gap-4">
                <div className="relative z-10 w-8 flex justify-center flex-shrink-0 pt-0.5">
                  {r.status === 'done' && <CheckCircle2 size={18} className="text-emerald-400 bg-[#09090B]" />}
                  {r.status === 'active' && <Loader2 size={18} className="text-indigo-400 bg-[#09090B] animate-spin" style={{ animationDuration: '2.5s' }} />}
                  {r.status === 'next' && <Circle size={16} className="text-zinc-600 bg-[#09090B]" />}
                </div>
                <div>
                  <h3 className={`font-semibold text-sm mb-1 ${r.status === 'next' ? 'text-zinc-400' : 'text-white'}`}>
                    {r.title}
                  </h3>
                  <p className="text-zinc-500 text-sm leading-relaxed">{r.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </AnimateIn>
      </div>
    </section>
  );
}
