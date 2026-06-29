"""
Boids Flocking (Discrete Grid Approximation) — Algorithm Atlas Plugin

Craig Reynolds' Boids algorithm models emergent flocking behavior using three rules:
  1. Cohesion:    Steer toward the average position of nearby boids.
  2. Separation:  Steer away from boids that are too close.
  3. Alignment:   Match the average heading of nearby boids.

This is a discrete grid approximation: boids are represented as cells with
value 1 on a 2D integer grid. Positions are tracked as (row, col) integers.
Each step applies probabilistic movement rules derived from the three behaviors.

Because the grid is discrete, positions are rounded and clamped; the visualization
shows boid density on the grid.
"""
from __future__ import annotations

import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    CellularAutomataState,
    SimulationParams,
)


class Boids:
    """Discrete grid approximation of Craig Reynolds' Boids flocking algorithm."""

    _seed: int = 0

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="boids",
            name="Boids Flocking",
            category="cellular-automata",
            visualization_type="PARTICLE_FIELD",
            description=(
                "Boids is Craig Reynolds' 1987 flocking simulation. Three simple rules — "
                "cohesion (move toward the flock center), separation (avoid crowding), "
                "and alignment (match neighbors' direction) — produce realistic flocking, "
                "schooling, and herding behavior. This is a discrete 2D grid approximation."
            ),
            intuition=(
                "No central coordination exists: each boid only reacts to its local "
                "neighbors. Yet the entire flock moves with apparent collective intelligence, "
                "splitting around obstacles and reforming naturally."
            ),
            complexity_time_best="O(boids²)",
            complexity_time_average="O(boids²)",
            complexity_time_worst="O(boids²)",
            complexity_space="O(n²)",
            tags=("cellular-automata", "flocking", "simulation", "emergent", "boids"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CellularAutomataState:
        n = int(params.inputs.get("n", 40))
        num_boids = int(params.inputs.get("boids", 20))
        self._seed = params.seed
        rng = random.Random(params.seed)

        # Place boids at random positions
        positions: list[tuple[int, int]] = []
        occupied: set[tuple[int, int]] = set()
        while len(positions) < num_boids:
            r = rng.randint(0, n - 1)
            c = rng.randint(0, n - 1)
            if (r, c) not in occupied:
                positions.append((r, c))
                occupied.add((r, c))

        grid = self._positions_to_grid(positions, n)

        return CellularAutomataState(
            grid=grid,
            width=n,
            height=n,
            generation=0,
            alive_count=num_boids,
            description=f"Boids initial state — {num_boids} boids on {n}×{n} grid",
        )

    def steps(
        self,
        state: CellularAutomataState,
    ) -> Generator[CellularAutomataState, None, None]:
        n = state.width
        # Reconstruct boid positions from grid
        positions: list[list[int]] = [
            [r, c]
            for r in range(n)
            for c in range(n)
            if state.grid[r][c] == 1
        ]
        num_boids = len(positions)

        rng = random.Random(self._seed ^ 0xB01D5)

        # Per-boid velocity (dr, dc) — starts as zero
        velocities: list[list[float]] = [[0.0, 0.0] for _ in range(num_boids)]

        # Tunable parameters
        perception_radius = max(4, n // 8)
        separation_radius = 2
        cohesion_weight   = 0.01
        alignment_weight  = 0.05
        separation_weight = 0.15
        max_speed         = 1.5
        noise             = 0.3

        max_steps = 150

        for step in range(1, max_steps + 1):
            new_velocities: list[list[float]] = [[0.0, 0.0] for _ in range(num_boids)]

            for i, (pr, pc) in enumerate(positions):
                vr, vc = velocities[i]

                # Find neighbors within perception radius
                neighbors = []
                close_neighbors = []
                for j, (qr, qc) in enumerate(positions):
                    if i == j:
                        continue
                    dist = ((pr - qr) ** 2 + (pc - qc) ** 2) ** 0.5
                    if dist < perception_radius:
                        neighbors.append(j)
                    if dist < separation_radius:
                        close_neighbors.append(j)

                # Cohesion: steer toward average position of neighbors
                if neighbors:
                    avg_r = sum(positions[j][0] for j in neighbors) / len(neighbors)
                    avg_c = sum(positions[j][1] for j in neighbors) / len(neighbors)
                    vr += cohesion_weight * (avg_r - pr)
                    vc += cohesion_weight * (avg_c - pc)

                # Alignment: match average velocity of neighbors
                if neighbors:
                    avg_vr = sum(velocities[j][0] for j in neighbors) / len(neighbors)
                    avg_vc = sum(velocities[j][1] for j in neighbors) / len(neighbors)
                    vr += alignment_weight * (avg_vr - vr)
                    vc += alignment_weight * (avg_vc - vc)

                # Separation: steer away from close neighbors
                for j in close_neighbors:
                    vr -= separation_weight * (positions[j][0] - pr)
                    vc -= separation_weight * (positions[j][1] - pc)

                # Boundary repulsion (soft walls)
                border = max(2, n // 10)
                if pr < border:
                    vr += 0.5
                elif pr > n - 1 - border:
                    vr -= 0.5
                if pc < border:
                    vc += 0.5
                elif pc > n - 1 - border:
                    vc -= 0.5

                # Small random noise for variety
                vr += rng.uniform(-noise, noise)
                vc += rng.uniform(-noise, noise)

                # Clamp speed
                speed = (vr ** 2 + vc ** 2) ** 0.5
                if speed > max_speed and speed > 0:
                    vr = vr / speed * max_speed
                    vc = vc / speed * max_speed

                new_velocities[i] = [vr, vc]

            # Apply velocities → new positions (round to integer grid)
            velocities = new_velocities
            new_positions: list[list[int]] = []
            occupied: set[tuple[int, int]] = set()

            for i, (pr, pc) in enumerate(positions):
                nr = int(round(pr + velocities[i][0]))
                nc = int(round(pc + velocities[i][1]))
                # Clamp to grid
                nr = max(0, min(n - 1, nr))
                nc = max(0, min(n - 1, nc))
                # Resolve collisions: if occupied, stay put
                if (nr, nc) in occupied:
                    nr, nc = pr, pc
                if (nr, nc) in occupied:
                    # find any free adjacent cell
                    placed = False
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            cr, cc = nr + dr, nc + dc
                            if 0 <= cr < n and 0 <= cc < n and (cr, cc) not in occupied:
                                nr, nc = cr, cc
                                placed = True
                                break
                        if placed:
                            break
                occupied.add((nr, nc))
                new_positions.append([nr, nc])

            positions = new_positions

            grid = self._positions_to_grid(
                [(p[0], p[1]) for p in positions], n
            )

            yield CellularAutomataState(
                grid=grid,
                width=n,
                height=n,
                generation=step,
                alive_count=num_boids,
                description=f"Boids step {step} — {num_boids} agents flocking",
            )

    @staticmethod
    def _positions_to_grid(
        positions: list[tuple[int, int]], n: int
    ) -> Tuple[Tuple[int, ...], ...]:
        grid = [[0] * n for _ in range(n)]
        for r, c in positions:
            grid[r][c] = 1
        return tuple(tuple(row) for row in grid)
