import { useEffect, useState, type ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnimateIn } from '../../components/ui/AnimateIn';
import { cn } from '../../lib/utils';

// ---------------------------------------------------------------------------
// The same algorithm (two-sum), told in six languages — proves the "write
// once, understand everywhere" idea AtlasCode + the Polyglot Notebook are
// built around. A tiny regex tokenizer fakes syntax highlighting without a
// full highlighter dependency.
// ---------------------------------------------------------------------------

const SNIPPETS: { id: string; label: string; accent: string; code: string }[] = [
  {
    id: 'python',
    label: 'Python',
    accent: '#22d3ee',
    code: `def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return seen[target - x], i
        seen[x] = i`,
  },
  {
    id: 'javascript',
    label: 'JavaScript',
    accent: '#facc15',
    code: `function twoSum(nums, target) {
  const seen = new Map();
  for (let i = 0; i < nums.length; i++) {
    const need = target - nums[i];
    if (seen.has(need)) return [seen.get(need), i];
    seen.set(nums[i], i);
  }
}`,
  },
  {
    id: 'rust',
    label: 'Rust',
    accent: '#fb923c',
    code: `fn two_sum(nums: &[i32], target: i32) -> (usize, usize) {
    let mut seen = HashMap::new();
    for (i, &x) in nums.iter().enumerate() {
        if let Some(&j) = seen.get(&(target - x)) {
            return (j, i);
        }
        seen.insert(x, i);
    }
    unreachable!()
}`,
  },
  {
    id: 'go',
    label: 'Go',
    accent: '#38bdf8',
    code: `func twoSum(nums []int, target int) (int, int) {
    seen := map[int]int{}
    for i, x := range nums {
        if j, ok := seen[target-x]; ok {
            return j, i
        }
        seen[x] = i
    }
    return -1, -1
}`,
  },
  {
    id: 'java',
    label: 'Java',
    accent: '#f87171',
    code: `static int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> seen = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        int need = target - nums[i];
        if (seen.containsKey(need)) return new int[]{seen.get(need), i};
        seen.put(nums[i], i);
    }
    return null;
}`,
  },
  {
    id: 'cpp',
    label: 'C++',
    accent: '#818cf8',
    code: `vector<int> twoSum(vector<int>& nums, int target) {
    unordered_map<int,int> seen;
    for (int i = 0; i < (int)nums.size(); i++) {
        int need = target - nums[i];
        if (seen.count(need)) return {seen[need], i};
        seen[nums[i]] = i;
    }
    return {};
}`,
  },
];

const TOKEN_RE =
  /(\/\/.*|#.*)|('(?:[^'\\]|\\.)*'|"(?:[^'"\\]|\\.)*")|\b(function|def|fn|func|static|return|if|else|for|while|let|const|var|mut|new|int|bool|true|false|struct|impl|pub|import|from|package|class|void|None|null|nil|unreachable)\b|\b(\d+)\b/g;

function highlightLine(line: string): ReactNode[] {
  const out: ReactNode[] = [];
  let last = 0;
  let key = 0;
  let m: RegExpExecArray | null;
  TOKEN_RE.lastIndex = 0;
  while ((m = TOKEN_RE.exec(line))) {
    if (m.index > last) out.push(line.slice(last, m.index));
    const [full, comment, str, kw, num] = m;
    if (comment) out.push(<span key={key++} className="text-zinc-600">{comment}</span>);
    else if (str) out.push(<span key={key++} className="text-emerald-400">{str}</span>);
    else if (kw) out.push(<span key={key++} className="text-purple-400">{kw}</span>);
    else if (num) out.push(<span key={key++} className="text-amber-300">{num}</span>);
    last = m.index + full.length;
    if (full.length === 0) TOKEN_RE.lastIndex++;
  }
  if (last < line.length) out.push(line.slice(last));
  return out;
}

const CYCLE_MS = 3200;

export function PolyglotSwitcherSection() {
  const [active, setActive] = useState(0);
  const [progressKey, setProgressKey] = useState(0);

  useEffect(() => {
    const t = setInterval(() => {
      setActive((i) => (i + 1) % SNIPPETS.length);
      setProgressKey((k) => k + 1);
    }, CYCLE_MS);
    return () => clearInterval(t);
  }, []);

  const select = (i: number) => {
    setActive(i);
    setProgressKey((k) => k + 1);
  };

  const snippet = SNIPPETS[active];

  return (
    <section className="py-24 px-4">
      <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <AnimateIn direction="right" className="order-2 lg:order-1">
          <div className="rounded-2xl border border-white/10 bg-[#0D0D10] shadow-card overflow-hidden">
            <div className="flex items-center gap-1 px-3 pt-3 flex-wrap">
              {SNIPPETS.map((s, i) => (
                <button
                  key={s.id}
                  onClick={() => select(i)}
                  className={cn(
                    'relative px-3 py-2 text-xs font-mono font-medium rounded-t-lg transition-colors duration-200',
                    i === active ? 'text-white bg-white/[0.06]' : 'text-zinc-500 hover:text-zinc-300',
                  )}
                >
                  {s.label}
                  {i === active && (
                    <motion.span
                      key={progressKey}
                      className="absolute left-0 bottom-0 h-[2px] rounded-full"
                      style={{ backgroundColor: s.accent }}
                      initial={{ width: '0%' }}
                      animate={{ width: '100%' }}
                      transition={{ duration: CYCLE_MS / 1000, ease: 'linear' }}
                    />
                  )}
                </button>
              ))}
            </div>
            <div className="border-t border-white/5 p-6 min-h-[240px]">
              <AnimatePresence mode="wait">
                <motion.pre
                  key={snippet.id}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -6 }}
                  transition={{ duration: 0.25 }}
                  className="text-[13px] leading-relaxed font-mono text-zinc-300 whitespace-pre overflow-x-auto"
                >
                  {snippet.code.split('\n').map((line, i) => (
                    <div key={i}>{highlightLine(line)}</div>
                  ))}
                </motion.pre>
              </AnimatePresence>
            </div>
          </div>
        </AnimateIn>

        <AnimateIn direction="left" delay={0.1} className="order-1 lg:order-2">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-300 text-xs font-medium mb-6">
            Polyglot Notebook
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-5 leading-tight">
            One idea.
            <br />
            Seventeen languages.
          </h2>
          <p className="text-zinc-400 text-lg mb-6 leading-relaxed">
            The same solution, expressed idiomatically in every language AtlasCode judges
            against. Learn a pattern once in Python, then see exactly how it looks in Rust,
            Go, or C++ — the calling convention, the standard library, the idioms all differ,
            but the algorithm never does.
          </p>
          <div className="flex flex-wrap gap-2">
            {SNIPPETS.map((s, i) => (
              <button
                key={s.id}
                onClick={() => select(i)}
                className={cn(
                  'w-2 h-2 rounded-full transition-all duration-300',
                  i === active ? 'w-6' : 'opacity-40 hover:opacity-70',
                )}
                style={{ backgroundColor: s.accent }}
                aria-label={`Show ${s.label}`}
              />
            ))}
          </div>
        </AnimateIn>
      </div>
    </section>
  );
}
