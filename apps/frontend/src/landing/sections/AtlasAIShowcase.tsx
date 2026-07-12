import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles } from 'lucide-react';
import { AnimateIn } from '../../components/ui/AnimateIn';
import { Button } from '../../components/ui/Button';

interface Exchange {
  question: string;
  answer: string;
}

const EXCHANGES: Exchange[] = [
  {
    question: 'Why is my quicksort O(n²) on a sorted array?',
    answer:
      "Because you're picking the last element as the pivot. On already-sorted input, every partition splits n elements into 1 and n-1 — that's n nested passes instead of log n. Pick a random or median-of-three pivot to fix it.",
  },
  {
    question: "What's the difference between BFS and Dijkstra?",
    answer:
      'BFS finds the shortest path by edge count, assuming every edge costs 1. Dijkstra finds the shortest path by total weight, using a priority queue instead of a plain queue — it degrades to BFS when all weights are equal.',
  },
  {
    question: 'Give me a hint for Longest Increasing Subsequence.',
    answer:
      "Try dp[i] = length of the LIS ending at index i. For each j < i where nums[j] < nums[i], dp[i] = max(dp[i], dp[j] + 1). That's O(n²) — there's an O(n log n) version using binary search if you want the harder version.",
  },
];

const TYPE_MS = 16;
const HOLD_MS = 2400;

function AtlasAvatar() {
  return (
    <div className="relative w-8 h-8 rounded-full flex-shrink-0">
      <div
        className="absolute inset-0 rounded-full"
        style={{
          background:
            'linear-gradient(145deg, rgba(118,120,255,0.95) 0%, rgba(79,70,229,0.92) 55%, rgba(109,40,217,0.88) 100%)',
          boxShadow: '0 0 0 1px rgba(99,102,241,0.35), 0 4px 14px rgba(99,102,241,0.35)',
        }}
      />
      <div className="absolute inset-0 flex items-center justify-center">
        <Sparkles size={14} className="text-white" />
      </div>
    </div>
  );
}

function useTypewriter(text: string, active: boolean) {
  const [shown, setShown] = useState('');
  useEffect(() => {
    if (!active) {
      setShown('');
      return;
    }
    setShown('');
    let i = 0;
    const id = setInterval(() => {
      i++;
      setShown(text.slice(0, i));
      if (i >= text.length) clearInterval(id);
    }, TYPE_MS);
    return () => clearInterval(id);
  }, [text, active]);
  return shown;
}

export function AtlasAIShowcaseSection() {
  const [index, setIndex] = useState(0);
  const [phase, setPhase] = useState<'typing' | 'holding'>('typing');
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const exchange = EXCHANGES[index];
  const answer = useTypewriter(exchange.answer, phase === 'typing');

  useEffect(() => {
    if (phase !== 'typing') return;
    const duration = exchange.answer.length * TYPE_MS + 400;
    timerRef.current = setTimeout(() => setPhase('holding'), duration);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [phase, exchange.answer.length]);

  useEffect(() => {
    if (phase !== 'holding') return;
    timerRef.current = setTimeout(() => {
      setIndex((i) => (i + 1) % EXCHANGES.length);
      setPhase('typing');
    }, HOLD_MS);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [phase]);

  return (
    <section className="py-24 px-4">
      <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <AnimateIn direction="right">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-purple-500/30 bg-purple-500/10 text-purple-300 text-xs font-medium mb-6">
            <Sparkles size={12} />
            Atlas AI
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-5 leading-tight">
            Your algorithmic
            <br />
            co-pilot.
          </h2>
          <p className="text-zinc-400 text-lg mb-6 leading-relaxed">
            Stuck on a bug, a proof, or a Big-O question? Atlas AI sees the algorithm you're
            visualizing or the code you're running and answers in context — no tab-switching,
            no copy-pasting your problem into a generic chatbot.
          </p>
          <Link to="/algorithms">
            <Button variant="primary" size="lg" icon={<Sparkles size={16} />}>
              Ask Atlas
            </Button>
          </Link>
        </AnimateIn>

        <AnimateIn direction="left" delay={0.1}>
          <div className="rounded-2xl border border-white/10 bg-[#0D0D10] shadow-card overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5 bg-white/[0.02]">
              <AtlasAvatar />
              <span className="text-sm text-white font-medium">Atlas AI</span>
              <span className="ml-auto flex items-center gap-1.5 text-xs text-emerald-400">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-slow" />
                online
              </span>
            </div>

            <div className="p-5 min-h-[260px] flex flex-col gap-4">
              <AnimatePresence mode="wait">
                <motion.div
                  key={`q-${index}`}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="self-end max-w-[85%] rounded-2xl rounded-br-sm bg-indigo-600/90 text-white text-sm px-4 py-2.5"
                >
                  {exchange.question}
                </motion.div>
              </AnimatePresence>

              <div className="flex items-start gap-2.5 max-w-[90%]">
                <AtlasAvatar />
                <div className="rounded-2xl rounded-tl-sm bg-white/[0.04] border border-white/5 text-zinc-300 text-sm leading-relaxed px-4 py-2.5 min-h-[2.5rem]">
                  {answer}
                  {phase === 'typing' && (
                    <span className="inline-block w-1.5 h-3.5 ml-0.5 bg-indigo-400 align-text-bottom animate-pulse-slow" />
                  )}
                </div>
              </div>
            </div>
          </div>
        </AnimateIn>
      </div>
    </section>
  );
}
