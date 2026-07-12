import { Component, Fragment, type ErrorInfo, type ReactNode } from 'react';
import { Link, useParams } from 'react-router-dom';

// Route-level safety net for the AtlasCode workspace: if anything in
// ProblemPage's tree throws during render (a stale/malformed API shape, a
// draft persisted under an old schema, etc), the user must see a recoverable
// screen instead of a blank black page. Fixing root causes always comes
// first (see supportsFunctionMode/starterFor hardening + resolveMode in
// atlasCodeStore.ts) -- this exists as a last-resort backstop, not a
// substitute for those fixes.
interface Props {
  children: ReactNode;
  slug?: string;
}

interface State {
  error: Error | null;
  retryCount: number;
}

class ProblemErrorBoundaryInner extends Component<Props, State> {
  state: State = { error: null, retryCount: 0 };

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // Structured context for debugging -- never a raw stack trace shown to
    // the user in production, but always logged for whoever's watching.
    // eslint-disable-next-line no-console
    console.error('[AtlasCode] workspace crashed', {
      slug: this.props.slug,
      message: error.message,
      componentStack: info.componentStack,
    });
  }

  handleRetry = () => {
    // Bump retryCount so the child tree remounts fresh (a new key) rather
    // than re-rendering the same instance that just crashed -- important
    // when the crash came from stale local component state, not just a
    // one-off render glitch.
    this.setState((s) => ({ error: null, retryCount: s.retryCount + 1 }));
  };

  render() {
    if (this.state.error) {
      return (
        <div className="min-h-screen pt-20 flex flex-col items-center justify-center gap-4 text-center px-4">
          <div className="text-lg text-white font-medium">AtlasCode workspace could not initialize.</div>
          <div className="text-sm text-zinc-500 max-w-md">
            Something went wrong loading this problem. This has been logged; you can retry or go back to the catalog.
          </div>
          {import.meta.env.DEV && (
            <pre className="text-xs text-rose-400/80 bg-rose-500/5 border border-rose-500/20 rounded-lg p-3 max-w-xl overflow-x-auto text-left">
              {this.state.error.message}
            </pre>
          )}
          <div className="flex items-center gap-3 mt-2">
            <button
              onClick={this.handleRetry}
              className="text-sm bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Retry
            </button>
            <Link
              to="/atlas-code/catalog"
              className="text-sm text-zinc-400 hover:text-white px-4 py-2 rounded-lg border border-white/10 hover:border-white/20 transition-colors"
            >
              Back to Catalog
            </Link>
          </div>
        </div>
      );
    }
    return <Fragment key={this.state.retryCount}>{this.props.children}</Fragment>;
  }
}

// Wrapper so the class component can read the route param for logging
// without the route needing to pass it explicitly.
export function ProblemErrorBoundary({ children }: { children: ReactNode }) {
  const { slug } = useParams<{ slug: string }>();
  return <ProblemErrorBoundaryInner slug={slug}>{children}</ProblemErrorBoundaryInner>;
}
