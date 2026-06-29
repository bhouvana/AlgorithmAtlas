"""Word Search (Backtracking) plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    GridState,
    SimulationParams,
)

# Cell constants
CELL_EMPTY = 0
CELL_WALL = 1
CELL_START = 2
CELL_GOAL = 3
CELL_OPEN = 4
CELL_CLOSED = 5
CELL_PATH = 6

# (grid_chars, word, path_exists)
_PUZZLES = [
    (["ABCE", "SFCS", "ADEE"], "ABCCED", True),
    (["ABCE", "SFCS", "ADEE"], "SEE", True),
    (["ABCE", "SFCS", "ADEE"], "ABCB", False),
    (["AABB", "CCDD", "EEFF"], "ABDC", True),
    (["XYZ", "WVU", "TRS"], "XYVWT", True),
]


def _make_grid(grid_chars: list[str]) -> tuple[tuple[int, ...]]:
    """Convert char grid to int grid (using char codes offset)."""
    rows = []
    for row in grid_chars:
        rows.append(tuple(ord(c) - ord('A') + 10 for c in row))
    return tuple(rows)


def _search_word(grid_chars: list[str], word: str):
    """Returns (found: bool, path: list[(row,col)] or None)."""
    rows = len(grid_chars)
    cols = len(grid_chars[0])
    grid = [list(r) for r in grid_chars]
    DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    found_path = [None]

    def dfs(r: int, c: int, idx: int, path: list) -> bool:
        if idx == len(word):
            found_path[0] = path[:]
            return True
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return False
        if grid[r][c] != word[idx]:
            return False
        original = grid[r][c]
        grid[r][c] = '#'
        path.append((r, c))
        for dr, dc in DIRS:
            if dfs(r + dr, c + dc, idx + 1, path):
                return True
        path.pop()
        grid[r][c] = original
        return False

    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0, []):
                return True, found_path[0]
    return False, None


class WordSearchSimulation(AlgorithmPlugin):
    """Word Search using backtracking DFS on a grid."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="word-search",
            name="Word Search (Backtracking)",
            category="backtracking",
            visualization_type="GRID",
            description="Find a word in a 2D character grid by DFS with backtracking.",
            intuition=(
                "Try each starting cell matching word[0]. DFS explores adjacent cells "
                "for each subsequent letter, marking cells visited to avoid reuse."
            ),
            complexity_time_best="O(m·n·4^L)",
            complexity_time_average="O(m·n·4^L)",
            complexity_time_worst="O(m·n·4^L)",
            complexity_space="O(L)",
            tags=("backtracking", "word-search", "grid", "dfs"),
        )

    def initialize(self, params: SimulationParams) -> GridState:
        idx = params.seed % len(_PUZZLES)
        grid_chars, word, exists = _PUZZLES[idx]
        int_grid = _make_grid(grid_chars)
        return GridState(
            grid=int_grid,
            current=None,
            path=tuple(),
            description=f"Search for '{word}' expected={'found' if exists else 'not found'}",
        )

    def steps(
        self, initial_state: GridState
    ) -> Generator[GridState, None, GridState]:
        desc = initial_state.description
        word = desc.split("'")[1]
        idx = next(
            i for i, (_, w, _) in enumerate(_PUZZLES) if w == word
            and (("found" in desc and _PUZZLES[i][2]) or ("not found" in desc and not _PUZZLES[i][2]))
        )
        grid_chars, _, exists = _PUZZLES[idx]

        rows = len(grid_chars)
        cols = len(grid_chars[0])
        int_grid = list(list(row) for row in initial_state.grid)
        grid_mut = [list(r) for r in grid_chars]
        DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        frames: list = []
        found_path: list = []

        def dfs(r: int, c: int, idx_: int, path: list) -> bool:
            if idx_ == len(word):
                found_path.extend(path)
                return True
            if r < 0 or r >= rows or c < 0 or c >= cols:
                return False
            if grid_mut[r][c] != word[idx_]:
                return False
            original = grid_mut[r][c]
            grid_mut[r][c] = '#'
            path.append((r, c))
            frames.append(("visit", path[:], r, c, idx_))
            for dr, dc in DIRS:
                if dfs(r + dr, c + dc, idx_ + 1, path):
                    return True
            frames.append(("backtrack", path[:], r, c, idx_))
            path.pop()
            grid_mut[r][c] = original
            return False

        found = False
        for r in range(rows):
            for c in range(cols):
                if dfs(r, c, 0, []):
                    found = True
                    break
            if found:
                break

        # Now yield the frames
        current_path: set = set()
        for action, path, r, c, letter_idx in frames:
            if action == "visit":
                current_path = set(path)
                # Build grid view
                new_grid = [list(row) for row in initial_state.grid]
                for pr, pc in current_path:
                    new_grid[pr][pc] = CELL_OPEN
                if path:
                    pr, pc = path[-1]
                    new_grid[pr][pc] = CELL_START

                yield GridState(
                    grid=tuple(tuple(row) for row in new_grid),
                    current=(r, c),
                    path=tuple(path),
                    description=f"Visiting ({r},{c})='{word[letter_idx]}' depth={letter_idx+1}",
                )
            else:  # backtrack
                current_path = set(path[:-1]) if path else set()
                new_grid = [list(row) for row in initial_state.grid]
                for pr, pc in current_path:
                    new_grid[pr][pc] = CELL_OPEN
                new_grid[r][c] = CELL_CLOSED

                yield GridState(
                    grid=tuple(tuple(row) for row in new_grid),
                    current=(r, c),
                    path=tuple(path[:-1]) if path else tuple(),
                    description=f"Backtrack from ({r},{c}), no match at depth={letter_idx+1}",
                )

        # Final state
        final_grid = [list(row) for row in initial_state.grid]
        if found and found_path:
            for pr, pc in found_path:
                final_grid[pr][pc] = CELL_PATH
        result_str = "FOUND" if found else "NOT FOUND"
        return GridState(
            grid=tuple(tuple(row) for row in final_grid),
            current=None,
            path=tuple(found_path) if found else tuple(),
            description=f"'{word}' {result_str}",
        )
