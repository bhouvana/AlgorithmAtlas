import { useEffect, useState, Suspense } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Bookmark, BookmarkCheck, CheckCircle2, Clock, ChevronRight, Trophy, Zap } from 'lucide-react';
import { getModule, getPrerequisiteModules } from './data/curriculum';
import { useProgressStore, useModuleProgress, xpForNextLevel, xpProgressPercent } from './store/progressStore';
import { GenericLesson } from './lessons/GenericLesson';
import { lessonRegistry } from './data/lessons';

const LESSON_MAP: Record<string, React.LazyExoticComponent<() => JSX.Element>> = {};

function XPBar({ xp }: { xp: number }) {
  const pct = xpProgressPercent(xp);
  const remaining = xpForNextLevel(xp);
  const level = Math.floor(xp / 200) + 1;
  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-1.5">
        <Zap size={12} className="text-amber-400" />
        <span className="text-xs font-medium text-amber-400">Lv {level}</span>
      </div>
      <div className="w-20 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-amber-400 rounded-full"
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
      <span className="text-[10px] text-zinc-500">{remaining} XP to next</span>
    </div>
  );
}

function ComingSoon({ title }: { title: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center gap-4">
      <div className="text-5xl mb-2">🚧</div>
      <h3 className="text-xl font-bold text-white">{title}</h3>
      <p className="text-zinc-400 text-sm max-w-sm">
        This lesson is being crafted with interactive visualizations and quizzes. Check back soon — it's worth the wait.
      </p>
      <div className="flex gap-2 mt-2">
        <div className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  );
}

export function LessonPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const module = id ? getModule(id) : null;
  const LessonComponent = id ? LESSON_MAP[id] : undefined;
  const lessonData = id ? lessonRegistry[id] : undefined;

  const progress = useModuleProgress(id ?? '');
  const { xp, bookmarks, toggleBookmark, startLesson, completeLesson, completeSection } = useProgressStore();
  const isBookmarked = bookmarks.includes(id ?? '');

  const [activeSection, setActiveSection] = useState(0);
  const [completed, setCompleted] = useState(false);
  const [showCompleteToast, setShowCompleteToast] = useState(false);

  const SECTIONS = [
    { id: 'concept', label: 'Concept' },
    { id: 'visualization', label: 'Visualization' },
    { id: 'examples', label: 'Examples' },
    { id: 'complexity', label: 'Complexity' },
    { id: 'video', label: 'Video' },
    { id: 'quiz', label: 'Quiz' },
  ];

  useEffect(() => {
    if (id) {
      startLesson(id);
      window.scrollTo(0, 0);
    }
  }, [id, startLesson]);

  const handleComplete = () => {
    if (!id || completed) return;
    completeSection(id, 'quiz');
    completeLesson(id, 100);
    setCompleted(true);
    setShowCompleteToast(true);
    setTimeout(() => setShowCompleteToast(false), 4000);
  };

  if (!module) {
    return (
      <div className="min-h-screen flex items-center justify-center text-zinc-400">
        Lesson not found.{' '}
        <Link to="/learning" className="text-indigo-400 underline ml-1">Back to Learning</Link>
      </div>
    );
  }

  const prerequisites = getPrerequisiteModules(module.id);
  const lessonDone = !!progress?.completedAt || completed;

  return (
    <div className="min-h-screen">
      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <div className="border-b border-white/6 bg-[#09090B]">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 min-w-0">
            <button onClick={() => navigate('/learning')} className="flex items-center gap-1.5 text-zinc-400 hover:text-white transition-colors text-sm flex-shrink-0">
              <ArrowLeft size={14} />
              <span className="hidden sm:inline">Back</span>
            </button>
            <div className="w-px h-4 bg-white/10 flex-shrink-0" />
            <div className="text-lg min-w-0">{module.icon}</div>
            <h1 className="text-sm font-medium text-white truncate">{module.title}</h1>
          </div>

          <div className="flex items-center gap-3 flex-shrink-0">
            <XPBar xp={xp} />
            <button
              onClick={() => toggleBookmark(module.id)}
              className={`p-1.5 rounded-lg transition-colors ${isBookmarked ? 'text-amber-400' : 'text-zinc-500 hover:text-zinc-300'}`}
            >
              {isBookmarked ? <BookmarkCheck size={15} /> : <Bookmark size={15} />}
            </button>
          </div>
        </div>

        {/* Section progress tabs */}
        <div className="max-w-4xl mx-auto px-4 pb-0 flex gap-1 overflow-x-auto">
          {SECTIONS.map((s, i) => (
            <button
              key={s.id}
              onClick={() => setActiveSection(i)}
              className={`px-3 py-2 text-xs font-medium whitespace-nowrap border-b-2 transition-all duration-150 ${
                activeSection === i
                  ? 'border-indigo-400 text-indigo-300'
                  : 'border-transparent text-zinc-500 hover:text-zinc-300'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* ── Main content ──────────────────────────────────────────────────── */}
      <div className="max-w-4xl mx-auto px-4 py-10">

        {/* Module meta */}
        <div className="mb-10">
          <div className="flex flex-wrap gap-2 items-center mb-4">
            <span className={`text-xs px-2.5 py-1 rounded-full border font-medium ${
              module.difficulty === 'beginner'     ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300' :
              module.difficulty === 'intermediate' ? 'border-amber-500/30 bg-amber-500/10 text-amber-300' :
                                                    'border-rose-500/30 bg-rose-500/10 text-rose-300'
            }`}>
              {module.difficulty}
            </span>
            <span className="flex items-center gap-1 text-zinc-500 text-xs">
              <Clock size={11} />{module.estimatedMinutes} min
            </span>
            {module.timeComplexity && (
              <code className="text-xs font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded">{module.timeComplexity}</code>
            )}
            {lessonDone && (
              <span className="flex items-center gap-1 text-emerald-400 text-xs ml-auto">
                <CheckCircle2 size={12} /> Completed
              </span>
            )}
          </div>

          <p className="text-zinc-400 text-sm leading-relaxed">{module.description}</p>

          {prerequisites.length > 0 && (
            <div className="mt-4 flex items-center gap-2 flex-wrap">
              <span className="text-xs text-zinc-600">Prereqs:</span>
              {prerequisites.map((p) => (
                <Link key={p.id} to={`/learning/${p.id}`} className="text-xs text-indigo-400 hover:text-indigo-300 underline underline-offset-2">
                  {p.title}
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Lesson content */}
        {LessonComponent ? (
          <Suspense fallback={
            <div className="flex items-center justify-center py-20 text-zinc-500 text-sm">
              <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mr-3" />
              Loading lesson...
            </div>
          }>
            <LessonComponent />
          </Suspense>
        ) : lessonData ? (
          <GenericLesson data={lessonData} activeSection={activeSection} lessonId={id} />
        ) : (
          <ComingSoon title={module.title} />
        )}

        {/* ── Complete Button ─────────────────────────────────────────────── */}
        {(LessonComponent || lessonData) && (
          <div className="mt-20 pt-10 border-t border-white/8">
            {lessonDone ? (
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
                    <Trophy size={18} className="text-emerald-400" />
                  </div>
                  <div>
                    <div className="text-white font-semibold text-sm">Lesson Complete!</div>
                    <div className="text-zinc-400 text-xs">+100 XP earned</div>
                  </div>
                </div>
                <Link
                  to="/learning"
                  className="flex items-center gap-2 px-5 py-2.5 bg-indigo-500 hover:bg-indigo-400 text-white text-sm font-medium rounded-xl transition-colors"
                >
                  Continue Learning <ChevronRight size={14} />
                </Link>
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                <p className="text-zinc-400 text-sm">
                  Finished reading and trying the quiz? Mark this lesson as complete to earn XP.
                </p>
                <button
                  onClick={handleComplete}
                  className="flex items-center gap-2 px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-white font-semibold text-sm rounded-xl transition-colors"
                >
                  <CheckCircle2 size={16} /> Mark Complete (+100 XP)
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* ── Completion toast ──────────────────────────────────────────────── */}
      <AnimatePresence>
        {showCompleteToast && (
          <motion.div
            initial={{ opacity: 0, y: 60, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 60, scale: 0.9 }}
            className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 px-5 py-3 bg-zinc-900 border border-emerald-500/30 rounded-2xl shadow-2xl"
          >
            <span className="text-2xl">🏆</span>
            <div>
              <div className="text-white font-semibold text-sm">Lesson Complete!</div>
              <div className="text-emerald-400 text-xs">+100 XP earned</div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
