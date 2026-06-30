import { motion } from 'framer-motion';
import {
  Lightbulb, Bug, Zap, RefreshCw, TestTube2, Code2,
  Trophy, PlayCircle, Search, Pencil, BookOpen, GitCompare,
  Sparkles, BarChart2,
} from 'lucide-react';
import type { AtlasContext } from '../types';

interface Action {
  icon: React.ReactNode;
  label: string;
  desc: string;
  message: string;
  accent: string;
}

function getActions(ctx: AtlasContext): Action[] {
  switch (ctx.page) {
    case 'algorithm':
    case 'lesson':
      return [
        {
          icon: <PlayCircle className="w-4 h-4" />,
          label: 'Explain frame',
          desc: 'Walk through current step',
          message: 'Explain what is happening right now in the visualization, step by step.',
          accent: '#6366f1',
        },
        {
          icon: <Lightbulb className="w-4 h-4" />,
          label: 'Teach me',
          desc: 'Deep dive explanation',
          message: 'Teach me this algorithm from first principles. Explain the intuition, then the mechanics.',
          accent: '#f59e0b',
        },
        {
          icon: <GitCompare className="w-4 h-4" />,
          label: 'Compare variants',
          desc: 'Alternatives & trade-offs',
          message: 'Compare this algorithm with its common alternatives. When should I use each?',
          accent: '#0ea5e9',
        },
        {
          icon: <Trophy className="w-4 h-4" />,
          label: 'Interview me',
          desc: 'FAANG-style question',
          message: 'Start a FAANG-style coding interview problem related to what I am studying right now.',
          accent: '#10b981',
        },
        {
          icon: <Pencil className="w-4 h-4" />,
          label: 'Draw diagram',
          desc: 'Visual explanation',
          message: 'Draw a clear diagram that explains how this algorithm works. Use a Mermaid diagram.',
          accent: '#8b5cf6',
        },
        {
          icon: <BarChart2 className="w-4 h-4" />,
          label: 'Complexity',
          desc: 'Time & space analysis',
          message: 'Give me a detailed complexity analysis: best, average, worst case — with examples.',
          accent: '#ec4899',
        },
      ];

    case 'notebook':
      return [
        {
          icon: <Lightbulb className="w-4 h-4" />,
          label: 'Explain',
          desc: 'Line-by-line walkthrough',
          message: 'Walk me through my current code line by line. Explain what each part does.',
          accent: '#f59e0b',
        },
        {
          icon: <Bug className="w-4 h-4" />,
          label: 'Debug',
          desc: 'Find & fix issues',
          message: 'Help me debug my code. Identify the issues and suggest fixes.',
          accent: '#ef4444',
        },
        {
          icon: <Zap className="w-4 h-4" />,
          label: 'Optimize',
          desc: 'Better complexity',
          message: 'Optimize my current code for better time and space complexity. Explain the improvements.',
          accent: '#f59e0b',
        },
        {
          icon: <RefreshCw className="w-4 h-4" />,
          label: 'Translate',
          desc: 'Convert to another lang',
          message: 'Convert my current code to Python with clean, idiomatic style.',
          accent: '#0ea5e9',
        },
        {
          icon: <TestTube2 className="w-4 h-4" />,
          label: 'Generate tests',
          desc: 'Comprehensive coverage',
          message: 'Generate comprehensive test cases for my current code, including edge cases.',
          accent: '#10b981',
        },
        {
          icon: <Code2 className="w-4 h-4" />,
          label: 'Refactor',
          desc: 'Cleaner structure',
          message: 'Refactor my code to be cleaner and more maintainable while keeping the same behavior.',
          accent: '#8b5cf6',
        },
      ];

    case 'catalog':
    case 'learning':
      return [
        {
          icon: <BookOpen className="w-4 h-4" />,
          label: 'What next?',
          desc: 'Personalized path',
          message: 'Based on my learning progress, what algorithms should I study next?',
          accent: '#6366f1',
        },
        {
          icon: <Search className="w-4 h-4" />,
          label: 'Find algorithm',
          desc: 'Semantic search',
          message: 'What is the best algorithm for finding the shortest path in a weighted graph?',
          accent: '#0ea5e9',
        },
        {
          icon: <Trophy className="w-4 h-4" />,
          label: 'Mock interview',
          desc: 'FAANG-style question',
          message: 'Start a FAANG coding interview session based on my current learning level.',
          accent: '#10b981',
        },
        {
          icon: <Sparkles className="w-4 h-4" />,
          label: 'Study plan',
          desc: '30-day roadmap',
          message: 'Create a 30-day algorithm study plan for me based on my level and goals.',
          accent: '#f59e0b',
        },
      ];

    case 'compare':
      return [
        {
          icon: <GitCompare className="w-4 h-4" />,
          label: 'Compare now',
          desc: 'Key differences',
          message: 'What are the most important differences between the two algorithms I am comparing?',
          accent: '#0ea5e9',
        },
        {
          icon: <Lightbulb className="w-4 h-4" />,
          label: 'When to use?',
          desc: 'Decision guide',
          message: 'When should I use one algorithm over the other? Give me concrete use cases.',
          accent: '#f59e0b',
        },
        {
          icon: <Pencil className="w-4 h-4" />,
          label: 'Side-by-side',
          desc: 'Visual comparison',
          message: 'Draw a side-by-side diagram comparing both algorithms visually.',
          accent: '#8b5cf6',
        },
      ];

    default:
      return [
        {
          icon: <Sparkles className="w-4 h-4" />,
          label: 'Capabilities',
          desc: 'What Atlas can do',
          message: 'What can Atlas AI help me with on this platform?',
          accent: '#6366f1',
        },
        {
          icon: <BookOpen className="w-4 h-4" />,
          label: 'Learning path',
          desc: 'Algorithm roadmap',
          message: 'What algorithms should I study to become a strong engineer?',
          accent: '#f59e0b',
        },
        {
          icon: <Trophy className="w-4 h-4" />,
          label: 'Interview me',
          desc: 'Mock FAANG session',
          message: 'Start a mock technical interview',
          accent: '#10b981',
        },
        {
          icon: <Pencil className="w-4 h-4" />,
          label: 'Draw diagram',
          desc: 'Visualize a concept',
          message: 'Draw the recursion tree for Fibonacci(5)',
          accent: '#8b5cf6',
        },
      ];
  }
}

interface Props {
  context: AtlasContext;
  onAction: (msg: string) => void;
  disabled?: boolean;
  compact?: boolean;
}

export function ActionCards({ context, onAction, disabled, compact }: Props) {
  const actions = getActions(context);

  if (compact) {
    return (
      <div className="flex flex-wrap gap-1.5 px-3 pb-2">
        {actions.slice(0, 4).map((a) => (
          <button
            key={a.label}
            onClick={() => onAction(a.message)}
            disabled={disabled}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            style={{
              background: `${a.accent}10`,
              border: `1px solid ${a.accent}22`,
              color: a.accent,
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.background = `${a.accent}18`;
              (e.currentTarget as HTMLElement).style.borderColor = `${a.accent}44`;
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.background = `${a.accent}10`;
              (e.currentTarget as HTMLElement).style.borderColor = `${a.accent}22`;
            }}
          >
            {a.icon}
            <span className="font-medium text-zinc-300">{a.label}</span>
          </button>
        ))}
      </div>
    );
  }

  return (
    <div className="px-3 pb-2">
      <p className="text-[9px] font-semibold uppercase tracking-widest text-zinc-600 mb-2 px-1">
        Suggested actions
      </p>
      <div className="grid grid-cols-2 gap-2">
        {actions.map((action, i) => (
          <motion.button
            key={action.label}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.04 }}
            onClick={() => onAction(action.message)}
            disabled={disabled}
            className="flex flex-col gap-1 px-3 py-2.5 rounded-xl text-left transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            style={{
              background: 'rgba(255,255,255,0.025)',
              border: '1px solid rgba(255,255,255,0.055)',
            }}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.98 }}
            onHoverStart={(e) => {
              (e.target as HTMLElement).style.background = 'rgba(255,255,255,0.045)';
              (e.target as HTMLElement).style.borderColor = `${action.accent}35`;
            }}
            onHoverEnd={(e) => {
              (e.target as HTMLElement).style.background = 'rgba(255,255,255,0.025)';
              (e.target as HTMLElement).style.borderColor = 'rgba(255,255,255,0.055)';
            }}
          >
            <div className="flex items-center gap-2">
              <div style={{ color: action.accent }} className="flex-shrink-0">{action.icon}</div>
              <span className="text-[12px] font-semibold text-zinc-200 truncate">{action.label}</span>
            </div>
            <p className="text-[10.5px] text-zinc-600 leading-tight">{action.desc}</p>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
