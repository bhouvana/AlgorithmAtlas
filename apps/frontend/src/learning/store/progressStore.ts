import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface LessonProgress {
  moduleId: string;
  completedSections: string[];
  quizScore: number | null;
  startedAt: string;
  completedAt: string | null;
  timeSpentSeconds: number;
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  earnedAt: string;
}

interface ProgressState {
  xp: number;
  level: number;
  lessons: Record<string, LessonProgress>;
  achievements: Achievement[];
  bookmarks: string[];

  // Actions
  startLesson: (moduleId: string) => void;
  completeSection: (moduleId: string, sectionId: string) => void;
  completeLesson: (moduleId: string, quizScore?: number) => void;
  addXP: (amount: number, reason: string) => void;
  toggleBookmark: (moduleId: string) => void;
  addTime: (moduleId: string, seconds: number) => void;
  unlockAchievement: (id: string, title: string, description: string, icon: string) => void;
}

const XP_PER_LEVEL = 200;

function levelFromXP(xp: number): number {
  return Math.floor(xp / XP_PER_LEVEL) + 1;
}

export const useProgressStore = create<ProgressState>()(
  persist(
    (set, get) => ({
      xp: 0,
      level: 1,
      lessons: {},
      achievements: [],
      bookmarks: [],

      startLesson: (moduleId) => {
        const { lessons } = get();
        if (!lessons[moduleId]) {
          set((s) => ({
            lessons: {
              ...s.lessons,
              [moduleId]: {
                moduleId,
                completedSections: [],
                quizScore: null,
                startedAt: new Date().toISOString(),
                completedAt: null,
                timeSpentSeconds: 0,
              },
            },
          }));
        }
      },

      completeSection: (moduleId, sectionId) => {
        const { lessons } = get();
        const lesson = lessons[moduleId];
        if (!lesson) return;
        if (lesson.completedSections.includes(sectionId)) return;
        set((s) => ({
          lessons: {
            ...s.lessons,
            [moduleId]: {
              ...lesson,
              completedSections: [...lesson.completedSections, sectionId],
            },
          },
        }));
        get().addXP(10, `Completed section ${sectionId}`);
      },

      completeLesson: (moduleId, quizScore) => {
        const { lessons } = get();
        const lesson = lessons[moduleId];
        if (!lesson) return;
        const alreadyDone = !!lesson.completedAt;
        set((s) => ({
          lessons: {
            ...s.lessons,
            [moduleId]: {
              ...lesson,
              completedAt: new Date().toISOString(),
              quizScore: quizScore ?? lesson.quizScore,
            },
          },
        }));
        if (!alreadyDone) {
          get().addXP(100, 'Completed lesson');
          const total = Object.values(get().lessons).filter((l) => l.completedAt).length;
          if (total === 1)  get().unlockAchievement('first-lesson', 'First Step', 'Completed your first lesson', '🎯');
          if (total === 5)  get().unlockAchievement('five-lessons', 'Scholar', 'Completed 5 lessons', '📚');
          if (total === 10) get().unlockAchievement('ten-lessons', 'Dedicated', 'Completed 10 lessons', '🏆');
        }
      },

      addXP: (amount) => {
        set((s) => {
          const newXP = s.xp + amount;
          const newLevel = levelFromXP(newXP);
          return { xp: newXP, level: newLevel };
        });
      },

      toggleBookmark: (moduleId) => {
        set((s) => ({
          bookmarks: s.bookmarks.includes(moduleId)
            ? s.bookmarks.filter((b) => b !== moduleId)
            : [...s.bookmarks, moduleId],
        }));
      },

      addTime: (moduleId, seconds) => {
        const { lessons } = get();
        const lesson = lessons[moduleId];
        if (!lesson) return;
        set((s) => ({
          lessons: {
            ...s.lessons,
            [moduleId]: { ...lesson, timeSpentSeconds: lesson.timeSpentSeconds + seconds },
          },
        }));
      },

      unlockAchievement: (id, title, description, icon) => {
        const { achievements } = get();
        if (achievements.find((a) => a.id === id)) return;
        set((s) => ({
          achievements: [
            ...s.achievements,
            { id, title, description, icon, earnedAt: new Date().toISOString() },
          ],
        }));
      },
    }),
    { name: 'algorithm-atlas-progress' },
  ),
);

export function useModuleProgress(moduleId: string) {
  return useProgressStore((s) => s.lessons[moduleId] ?? null);
}

export function useCompletionStats() {
  return useProgressStore((s) => {
    const total = Object.keys(s.lessons).length;
    const done = Object.values(s.lessons).filter((l) => l.completedAt).length;
    return { total, done, xp: s.xp, level: s.level };
  });
}

export function xpForNextLevel(xp: number): number {
  const level = levelFromXP(xp);
  return level * XP_PER_LEVEL - xp;
}

export function xpProgressPercent(xp: number): number {
  const level = levelFromXP(xp);
  const base = (level - 1) * XP_PER_LEVEL;
  return Math.round(((xp - base) / XP_PER_LEVEL) * 100);
}
