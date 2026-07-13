import { Link } from 'react-router-dom';
import { ArrowRight, Code2 } from 'lucide-react';
import { AnimateIn } from '../../components/ui/AnimateIn';
import { Button } from '../../components/ui/Button';

export function FinalCTASection() {
  return (
    <section className="py-24 px-4">
      <AnimateIn className="max-w-4xl mx-auto">
        <div className="relative rounded-3xl border border-charcoal/10 bg-[#111113] overflow-hidden px-8 py-16 sm:py-20 text-center">
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute -top-24 left-1/4 w-72 h-72 bg-indigo-600/15 rounded-full blur-3xl" />
            <div className="absolute -bottom-24 right-1/4 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl" />
          </div>

          <div className="relative z-10">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-5">
              Stop reading about algorithms.
              <br />
              <span className="gradient-text">Start seeing them run.</span>
            </h2>
            <p className="text-zinc-400 text-lg max-w-lg mx-auto mb-10">
              250+ algorithms to visualize, 73 lessons to work through, 210+ challenges to
              prove it stuck. Free, no signup required to start exploring.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3">
              <Link to="/algorithms">
                <Button variant="primary" size="lg" icon={<ArrowRight size={16} />}>
                  Explore the Atlas
                </Button>
              </Link>
              <Link to="/atlas-code">
                <Button variant="secondary" size="lg" icon={<Code2 size={16} />}>
                  Try AtlasCode
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </AnimateIn>
    </section>
  );
}
