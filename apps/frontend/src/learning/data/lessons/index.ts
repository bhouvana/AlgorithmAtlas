import type { LessonData } from '../../lessons/GenericLesson';
import { foundationsLessons } from './foundations';
import { sortingLessons } from './sorting';
import { searchingTreesLessons } from './searching_trees';
import { graphsDpLessons } from './graphs_dp';
import { greedyBacktrackingAdvancedLessons } from './greedy_backtracking_advanced';
import { realWorldLessons } from './real_world';
import { thinkingLessons } from './thinking';
import { patternsLessons } from './patterns';

export const lessonRegistry: Record<string, LessonData> = {
  ...foundationsLessons,
  ...sortingLessons,
  ...searchingTreesLessons,
  ...graphsDpLessons,
  ...greedyBacktrackingAdvancedLessons,
  ...realWorldLessons,
  ...thinkingLessons,
  ...patternsLessons,
};
