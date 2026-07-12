import type { CustomCaseIn } from '../../api/problems';

export type RunSpec =
  | { mode: 'visible' }
  | { mode: 'selected'; indices: number[] }
  | { mode: 'custom'; cases: CustomCaseIn[] };
