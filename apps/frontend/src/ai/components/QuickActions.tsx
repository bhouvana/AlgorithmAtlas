import type { AtlasContext, QuickAction } from '../types';

interface Props {
  context: AtlasContext;
  onAction: (message: string) => void;
  disabled: boolean;
}

function getActions(context: AtlasContext): QuickAction[] {
  switch (context.page) {
    case 'algorithm':
    case 'lesson':
      return [
        { label: 'Explain this', icon: '💡', message: 'Explain what is happening right now in the visualization' },
        { label: 'Why this frame?', icon: '🔍', message: 'Why did the algorithm make this decision at the current step?' },
        { label: 'Compare alternatives', icon: '⇄', message: 'What algorithms are commonly compared with this one? What are the trade-offs?' },
        { label: 'Challenge me', icon: '🎯', message: 'Generate a medium-difficulty challenge based on what I am studying' },
      ];
    case 'notebook':
      return [
        { label: 'Explain code', icon: '💡', message: 'Walk me through my current code line by line' },
        { label: 'Debug errors', icon: '🐛', message: 'Help me fix the error in my code' },
        { label: 'Optimize', icon: '⚡', message: 'Optimize my current code for better time and space complexity' },
        { label: 'Convert language', icon: '🔄', message: 'Convert my current code to Python' },
      ];
    case 'catalog':
    case 'learning':
      return [
        { label: 'Recommend', icon: '🗺', message: 'Based on my progress, what should I learn next?' },
        { label: 'Find algorithm', icon: '🔍', message: 'Find the best algorithm for finding the shortest path in a graph' },
        { label: 'Explain complexity', icon: '📊', message: 'What is the difference between O(n log n) and O(n²) in practice?' },
        { label: 'Start interview', icon: '🎤', message: 'Start a mock FAANG coding interview relevant to what I have studied' },
      ];
    case 'compare':
      return [
        { label: 'Compare now', icon: '⇄', message: 'What are the key differences between the two algorithms I am comparing?' },
        { label: 'When to use?', icon: '🤔', message: 'When should I use one over the other in production?' },
        { label: 'Draw diagram', icon: '🎨', message: 'Draw a diagram showing both algorithms side by side' },
      ];
    default:
      return [
        { label: 'What can you do?', icon: '✨', message: 'What can Atlas AI help me with on this platform?' },
        { label: 'Recommend learning', icon: '📚', message: 'What algorithm topics should I study to become a better engineer?' },
        { label: 'Start interview', icon: '🎤', message: 'Start a mock technical interview' },
        { label: 'Draw a diagram', icon: '🎨', message: 'Draw the recursion tree for Fibonacci(5)' },
      ];
  }
}

export function QuickActions({ context, onAction, disabled }: Props) {
  const actions = getActions(context);

  return (
    <div className="px-3 pb-2 flex flex-wrap gap-1.5">
      {actions.map((action) => (
        <button
          key={action.label}
          onClick={() => onAction(action.message)}
          disabled={disabled}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/[0.04] border border-charcoal/10 text-zinc-400 hover:text-white hover:bg-white/[0.08] hover:border-white/15 text-xs transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <span className="text-sm leading-none">{action.icon}</span>
          <span>{action.label}</span>
        </button>
      ))}
    </div>
  );
}
