import { Link } from 'react-router-dom';

export function FooterSection() {
  return (
    <footer className="border-t border-white/5 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-8 mb-8">
          <div className="flex flex-col gap-2">
            <Link to="/" className="flex items-center gap-2 group">
              <span className="text-indigo-400 font-mono text-xl">⬡</span>
              <span className="text-white font-semibold text-sm">Algorithm Atlas</span>
            </Link>
            <p className="text-zinc-500 text-sm max-w-xs">
              The interactive encyclopedia of algorithms.
            </p>
          </div>

          <nav className="flex items-center gap-6">
            <Link to="/algorithms" className="text-zinc-400 hover:text-white text-sm transition-colors duration-200">
              Catalog
            </Link>
            <Link to="/atlas-code" className="text-zinc-400 hover:text-white text-sm transition-colors duration-200">
              AtlasCode
            </Link>
            <Link to="/learning" className="text-zinc-400 hover:text-white text-sm transition-colors duration-200">
              Learning
            </Link>
            <Link to="/compare" className="text-zinc-400 hover:text-white text-sm transition-colors duration-200">
              Compare
            </Link>
            <Link to="/notebook" className="text-zinc-400 hover:text-white text-sm transition-colors duration-200">
              Notebook
            </Link>
          </nav>
        </div>

        <div className="border-t border-white/5 pt-6 flex flex-col sm:flex-row items-center justify-between gap-3">
          <span className="text-zinc-600 text-sm">© 2026 Algorithm Atlas</span>
          <span className="text-zinc-600 text-sm">Built with React + FastAPI</span>
        </div>
      </div>
    </footer>
  );
}
