import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
// GitHub SVG icon (not in lucide-react)
function GitHubIcon({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844a9.59 9.59 0 0 1 2.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.02 10.02 0 0 0 22 12.017C22 6.484 17.522 2 12 2z" />
    </svg>
  );
}
import { cn } from '../../lib/utils';

const NAV_LINKS = [
  { to: '/learning', label: 'Learning' },
  { to: '/atlas-code', label: 'AtlasCode' },
  { to: '/algorithms', label: 'Catalog' },
  { to: '/compare', label: 'Compare' },
  { to: '/compiler', label: 'Compiler' },
];

export function NavBar() {
  const { pathname } = useLocation();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handler, { passive: true });
    return () => window.removeEventListener('scroll', handler);
  }, []);

  return (
    <div className="fixed top-0 left-0 right-0 z-50 pt-4 px-4 pointer-events-none">
      <div className="max-w-3xl mx-auto pointer-events-auto">
        <motion.div
          animate={{
            opacity: scrolled ? 0.95 : 1,
            scale: scrolled ? 0.99 : 1,
          }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
          className="backdrop-blur-xl bg-[#09090B]/80 border border-charcoal/10 rounded-2xl px-4 h-12 flex items-center justify-between shadow-card"
        >
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group flex-shrink-0">
            <span className="text-indigo-400 font-mono text-xl leading-none select-none group-hover:text-indigo-300 transition-colors duration-200">
              ⬡
            </span>
            <span className="text-white font-semibold text-sm group-hover:text-zinc-100 transition-colors duration-200 whitespace-nowrap">
              Algorithm Atlas
            </span>
          </Link>

          {/* Nav Links */}
          <nav className="flex items-center gap-0.5">
            {NAV_LINKS.map(({ to, label }) => {
              const isActive = pathname === to || (pathname.startsWith(to) && to !== '/');
              return (
                <Link
                  key={to}
                  to={to}
                  className={cn(
                    'relative px-3 py-1.5 text-sm rounded-xl transition-colors duration-200 z-10',
                    isActive ? 'text-white' : 'text-zinc-400 hover:text-zinc-200',
                  )}
                >
                  <AnimatePresence>
                    {isActive && (
                      <motion.span
                        layoutId="navbar-active"
                        className="absolute inset-0 bg-white/10 rounded-xl"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                      />
                    )}
                  </AnimatePresence>
                  <span className="relative z-10">{label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Right: GitHub */}
          <a
            href="https://github.com/bhouvana/AlgorithmAtlas"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center w-8 h-8 rounded-xl text-zinc-400 hover:text-white hover:bg-white/5 transition-all duration-200 flex-shrink-0"
            aria-label="View on GitHub"
          >
            <GitHubIcon size={16} />
          </a>
        </motion.div>
      </div>
    </div>
  );
}
