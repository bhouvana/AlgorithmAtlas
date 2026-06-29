import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, useInView } from 'framer-motion';
import {
  Play,
  GitCompare,
  BookOpen,
  Zap,
  Library,
  Terminal,
  ChevronDown,
} from 'lucide-react';

function GitHubIcon({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844a9.59 9.59 0 0 1 2.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.02 10.02 0 0 0 22 12.017C22 6.484 17.522 2 12 2z" />
    </svg>
  );
}
import { AnimateIn } from '../components/ui/AnimateIn';
import { SpotlightCard } from '../components/ui/SpotlightCard';
import { Button } from '../components/ui/Button';

// ---------------------------------------------------------------------------
// Particle Canvas
// ---------------------------------------------------------------------------

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  opacity: number;
}

function ParticleCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);
  const particlesRef = useRef<Particle[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    // Init particles
    const count = 80;
    particlesRef.current = Array.from({ length: count }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      radius: Math.random() * 1.5 + 0.5,
      opacity: Math.random() * 0.4 + 0.1,
    }));

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const particles = particlesRef.current;

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Move
        p.x += p.vx;
        p.y += p.vy;

        // Bounce
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

        // Draw dot
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,255,255,${p.opacity})`;
        ctx.fill();

        // Draw connections
        for (let j = i + 1; j < particles.length; j++) {
          const q = particles[j];
          const dx = p.x - q.x;
          const dy = p.y - q.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 120) {
            const alpha = (1 - dist / 120) * 0.12;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(q.x, q.y);
            ctx.strokeStyle = `rgba(79,70,229,${alpha})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }

      animRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animRef.current);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none"
      style={{ opacity: 0.6 }}
    />
  );
}

// ---------------------------------------------------------------------------
// CountUp hook
// ---------------------------------------------------------------------------

function useCountUp(target: number, duration = 1500) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: '-80px' });

  useEffect(() => {
    if (!inView) return;
    let startTime: number | null = null;
    const step = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCount(Math.round(eased * target));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [inView, target, duration]);

  return { count, ref };
}

// ---------------------------------------------------------------------------
// HeroSection
// ---------------------------------------------------------------------------

const heroWords = ['Visualize.', 'Compare.', 'Experiment.', 'Master.'];

function HeroSection() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden">
      {/* Particle background */}
      <ParticleCanvas />

      {/* Radial glow blobs */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/4 left-1/3 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/3 right-1/4 w-80 h-80 bg-purple-600/8 rounded-full blur-3xl" />
        <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-cyan-500/6 rounded-full blur-3xl" />
      </div>

      {/* Content */}
      <div className="relative z-10 text-center px-4 max-w-5xl mx-auto">
        {/* Tag */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-xs font-medium mb-8"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse-slow" />
          Interactive Algorithm Visualization
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold tracking-tight leading-[1.05] mb-6"
        >
          The Interactive{' '}
          <span className="gradient-text">Atlas</span>
          <br />
          of Algorithms.
        </motion.h1>

        {/* Animated subtext */}
        <div className="flex flex-wrap justify-center gap-x-3 gap-y-1 mb-10">
          {heroWords.map((word, i) => (
            <motion.span
              key={word}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 + i * 0.1, ease: 'easeOut' }}
              className="text-xl sm:text-2xl text-zinc-400 font-light"
            >
              {word}
            </motion.span>
          ))}
        </div>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.85 }}
          className="flex flex-wrap items-center justify-center gap-3"
        >
          <Link to="/algorithms">
            <Button variant="primary" size="lg" icon={<Play size={16} />}>
              Explore Algorithms
            </Button>
          </Link>
          <a href="https://github.com" target="_blank" rel="noopener noreferrer">
            <Button variant="secondary" size="lg" icon={<GitHubIcon size={16} />}>
              View on GitHub
            </Button>
          </a>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.4, duration: 0.8 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1 text-zinc-600"
      >
        <span className="text-xs tracking-widest uppercase">Scroll</span>
        <motion.div
          animate={{ y: [0, 6, 0] }}
          transition={{ repeat: Infinity, duration: 1.6, ease: 'easeInOut' }}
        >
          <ChevronDown size={16} />
        </motion.div>
      </motion.div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// StatsSection
// ---------------------------------------------------------------------------

interface StatItem {
  value: number;
  suffix: string;
  label: string;
  color: string;
}

const STATS: StatItem[] = [
  { value: 250, suffix: '+', label: 'Algorithms', color: 'from-indigo-400 to-indigo-300' },
  { value: 19, suffix: '', label: 'Categories', color: 'from-blue-400 to-cyan-300' },
  { value: 13, suffix: '', label: 'Viz Types', color: 'from-purple-400 to-pink-300' },
  { value: 17, suffix: '', label: 'Languages', color: 'from-cyan-400 to-teal-300' },
];

function StatCard({ value, suffix, label, color }: StatItem) {
  const { count, ref } = useCountUp(value);

  return (
    <div ref={ref} className="flex flex-col items-center gap-2 p-6">
      <span
        className={`text-4xl sm:text-5xl font-bold bg-gradient-to-r ${color} bg-clip-text text-transparent tabular-nums`}
      >
        {count}
        {suffix}
      </span>
      <span className="text-zinc-400 text-sm font-medium">{label}</span>
    </div>
  );
}

function StatsSection() {
  return (
    <section className="py-20 px-4">
      <AnimateIn className="max-w-4xl mx-auto">
        <div className="rounded-2xl border border-white/8 bg-[#18181B] grid grid-cols-2 sm:grid-cols-4 divide-x divide-y sm:divide-y-0 divide-white/8 overflow-hidden shadow-card">
          {STATS.map((stat) => (
            <StatCard key={stat.label} {...stat} />
          ))}
        </div>
      </AnimateIn>
    </section>
  );
}

// ---------------------------------------------------------------------------
// FeaturesSection
// ---------------------------------------------------------------------------

interface Feature {
  icon: React.ReactNode;
  title: string;
  description: string;
  span?: 'col' | 'row' | 'both';
  color: string;
}

const FEATURES: Feature[] = [
  {
    icon: <Play size={28} />,
    title: 'Step-by-step Simulation',
    description:
      'Watch algorithms execute one operation at a time. Pause, rewind, and fast-forward through every decision with full control.',
    color: 'text-indigo-400',
  },
  {
    icon: <GitCompare size={28} />,
    title: 'Side-by-side Comparison',
    description:
      'Run two algorithms simultaneously on identical inputs. See how Quicksort and Mergesort diverge in real time.',
    color: 'text-blue-400',
    span: 'col',
  },
  {
    icon: <BookOpen size={28} />,
    title: 'Interactive Notebook',
    description:
      'Write pseudocode, annotate steps, and build your personal reference library with executable examples.',
    color: 'text-purple-400',
  },
  {
    icon: <Zap size={28} />,
    title: 'Polyglot Notebook',
    description:
      '17 languages in one IDE-style editor — Python, C++, Rust, Kotlin, Swift, Go, and more. Run code instantly.',
    color: 'text-amber-400',
  },
  {
    icon: <Library size={28} />,
    title: '250+ Algorithms',
    description:
      'Sorting, searching, graphs, dynamic programming, cryptography, distributed systems, and more — all in one place.',
    color: 'text-cyan-400',
    span: 'col',
  },
  {
    icon: <Terminal size={28} />,
    title: 'Real-time Execution',
    description:
      'WebAssembly-powered engine runs native-speed code in the browser. Zero latency, zero setup.',
    color: 'text-emerald-400',
  },
];

function FeaturesSection() {
  return (
    <section className="py-20 px-4">
      <div className="max-w-6xl mx-auto">
        <AnimateIn className="text-center mb-14">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
            Everything you need
          </h2>
          <p className="text-zinc-400 text-lg max-w-xl mx-auto">
            A complete toolkit for learning, understanding, and mastering algorithms at any depth.
          </p>
        </AnimateIn>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {FEATURES.map((feature, i) => (
            <AnimateIn
              key={feature.title}
              delay={i * 0.07}
              className={
                feature.span === 'col'
                  ? 'lg:col-span-2'
                  : feature.span === 'row'
                    ? 'lg:row-span-2'
                    : ''
              }
            >
              <SpotlightCard className="h-full p-6">
                <div className={`mb-4 ${feature.color}`}>{feature.icon}</div>
                <h3 className="text-white font-semibold text-lg mb-2">{feature.title}</h3>
                <p className="text-zinc-400 text-sm leading-relaxed">{feature.description}</p>
              </SpotlightCard>
            </AnimateIn>
          ))}
        </div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// AlgorithmMarqueeSection
// ---------------------------------------------------------------------------

const ROW_1 = [
  'Bubble Sort',
  'Quick Sort',
  'Dijkstra',
  'Merge Sort',
  'A* Search',
  'DFS',
  'BFS',
  'Kruskal',
  'Bellman-Ford',
  'RSA',
  'AES',
  'Paxos',
  'Radix Sort',
  'Red-Black Tree',
  'Skip List',
];

const ROW_2 = [
  'Floyd-Warshall',
  'Knuth-Morris-Pratt',
  'Fibonacci',
  'Raft Consensus',
  'B-Tree',
  'SHA-256',
  'Ford-Fulkerson',
  'Topological Sort',
  'Bloom Filter',
  'Levenshtein',
  'Huffman Coding',
  'Sieve of Eratosthenes',
  'AVL Tree',
  'Tarjan SCC',
];

function MarqueeRow({ items, direction }: { items: string[]; direction: 'left' | 'right' }) {
  const doubled = [...items, ...items];
  return (
    <div className="overflow-hidden">
      <div
        className={
          direction === 'left' ? 'flex gap-3 animate-marquee-left' : 'flex gap-3 animate-marquee-right'
        }
        style={{ width: 'max-content' }}
      >
        {doubled.map((name, i) => (
          <span
            key={`${name}-${i}`}
            className="glass px-4 py-2 rounded-full text-sm text-zinc-300 font-mono whitespace-nowrap flex-shrink-0"
          >
            {name}
          </span>
        ))}
      </div>
    </div>
  );
}

function AlgorithmMarqueeSection() {
  return (
    <section className="py-20 overflow-hidden">
      <AnimateIn className="text-center mb-12 px-4">
        <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
          The complete catalog
        </h2>
        <p className="text-zinc-400 text-lg max-w-lg mx-auto">
          From classic sorting to cutting-edge distributed consensus — every algorithm visualized.
        </p>
      </AnimateIn>

      <div className="flex flex-col gap-3">
        <MarqueeRow items={ROW_1} direction="left" />
        <MarqueeRow items={ROW_2} direction="right" />
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// FooterSection
// ---------------------------------------------------------------------------

function FooterSection() {
  return (
    <footer className="border-t border-white/5 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-8 mb-8">
          {/* Logo + tagline */}
          <div className="flex flex-col gap-2">
            <Link to="/" className="flex items-center gap-2 group">
              <span className="text-indigo-400 font-mono text-xl">⬡</span>
              <span className="text-white font-semibold text-sm">Algorithm Atlas</span>
            </Link>
            <p className="text-zinc-500 text-sm max-w-xs">
              The interactive encyclopedia of algorithms.
            </p>
          </div>

          {/* Links */}
          <nav className="flex items-center gap-6">
            <Link
              to="/algorithms"
              className="text-zinc-400 hover:text-white text-sm transition-colors duration-200"
            >
              Catalog
            </Link>
            <Link
              to="/compare"
              className="text-zinc-400 hover:text-white text-sm transition-colors duration-200"
            >
              Compare
            </Link>
            <Link
              to="/notebook"
              className="text-zinc-400 hover:text-white text-sm transition-colors duration-200"
            >
              Notebook
            </Link>
          </nav>
        </div>

        {/* Bottom bar */}
        <div className="border-t border-white/5 pt-6 flex flex-col sm:flex-row items-center justify-between gap-3">
          <span className="text-zinc-600 text-sm">© 2026 Algorithm Atlas</span>
          <span className="text-zinc-600 text-sm">Built with React + FastAPI</span>
        </div>
      </div>
    </footer>
  );
}

// ---------------------------------------------------------------------------
// LandingPage (root export)
// ---------------------------------------------------------------------------

export function LandingPage() {
  return (
    <div className="min-h-screen text-white">
      <HeroSection />
      <StatsSection />
      <FeaturesSection />
      <AlgorithmMarqueeSection />
      <FooterSection />
    </div>
  );
}
