import { AnimateIn } from '../../components/ui/AnimateIn';

const ROW_1 = [
  'Bubble Sort', 'Quick Sort', 'Dijkstra', 'Merge Sort', 'A* Search', 'DFS', 'BFS',
  'Kruskal', 'Bellman-Ford', 'RSA', 'AES', 'Paxos', 'Radix Sort', 'Red-Black Tree', 'Skip List',
];

const ROW_2 = [
  'Floyd-Warshall', 'Knuth-Morris-Pratt', 'Fibonacci', 'Raft Consensus', 'B-Tree', 'SHA-256',
  'Ford-Fulkerson', 'Topological Sort', 'Bloom Filter', 'Levenshtein', 'Huffman Coding',
  'Sieve of Eratosthenes', 'AVL Tree', 'Tarjan SCC',
];

const LANGUAGES = [
  'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C', 'C#', 'Rust', 'Go', 'Kotlin',
  'Swift', 'Ruby', 'PHP', 'R', 'Scala', 'Perl', 'Shell',
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

export function AlgorithmMarqueeSection() {
  return (
    <section className="py-24 overflow-hidden">
      <AnimateIn className="text-center mb-12 px-4">
        <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
          The complete catalog
        </h2>
        <p className="text-zinc-400 text-lg max-w-lg mx-auto">
          From classic sorting to cutting-edge distributed consensus, every algorithm visualized.
        </p>
      </AnimateIn>

      <div className="flex flex-col gap-3 mb-16">
        <MarqueeRow items={ROW_1} direction="left" />
        <MarqueeRow items={ROW_2} direction="right" />
      </div>

      <AnimateIn className="text-center mb-8 px-4">
        <p className="text-zinc-500 text-sm uppercase tracking-widest font-medium">
          Judged in 17 languages
        </p>
      </AnimateIn>
      <MarqueeRow items={LANGUAGES} direction="left" />
    </section>
  );
}
