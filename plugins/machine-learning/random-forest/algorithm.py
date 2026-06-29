"""Random Forest plugin for Algorithm Atlas."""
from __future__ import annotations

import math
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_N_TREES = 8
_MAX_DEPTH = 3


def _gen_data(seed):
    """Generate binary classification dataset (2 features, 20 points)."""
    rng = seed * 1103515245 + 12345
    points = []
    labels = []
    for i in range(20):
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        x1 = (rng % 80) + 10
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        x2 = (rng % 80) + 10
        # Simple linear decision boundary: label=1 if x1+x2 > 110 else 0
        label = 1 if (x1 + x2) > 110 else 0
        points.append((x1, x2))
        labels.append(label)
    return points, labels


def _gini(labels):
    if not labels:
        return 0.0
    n = len(labels)
    p1 = sum(labels) / n
    return 1.0 - p1 ** 2 - (1 - p1) ** 2


def _best_split(points, labels, feature_indices):
    best_gini = float('inf')
    best_feat, best_thresh = None, None
    for feat in feature_indices:
        vals = sorted(set(p[feat] for p in points))
        for i in range(len(vals) - 1):
            thresh = (vals[i] + vals[i + 1]) / 2.0
            left = [labels[k] for k, p in enumerate(points) if p[feat] <= thresh]
            right = [labels[k] for k, p in enumerate(points) if p[feat] > thresh]
            if not left or not right:
                continue
            g = (len(left) * _gini(left) + len(right) * _gini(right)) / len(labels)
            if g < best_gini:
                best_gini = g
                best_feat = feat
                best_thresh = thresh
    return best_feat, best_thresh, best_gini


def _build_tree(points, labels, depth, rng, n_features=1):
    if depth == 0 or len(set(labels)) == 1 or not points:
        majority = int(sum(labels) > len(labels) / 2)
        return majority

    # Random feature subset
    rng[0] = (rng[0] * 1103515245 + 12345) & 0x7FFFFFFF
    feat_idx = rng[0] % 2  # 0 or 1
    feat, thresh, g = _best_split(points, labels, [feat_idx])

    if feat is None:
        return int(sum(labels) > len(labels) / 2)

    left_pts = [points[k] for k in range(len(points)) if points[k][feat] <= thresh]
    left_lbl = [labels[k] for k in range(len(labels)) if points[k][feat] <= thresh]
    right_pts = [points[k] for k in range(len(points)) if points[k][feat] > thresh]
    right_lbl = [labels[k] for k in range(len(labels)) if points[k][feat] > thresh]

    return {
        'feat': feat,
        'thresh': thresh,
        'gini': g,
        'left': _build_tree(left_pts, left_lbl, depth - 1, rng),
        'right': _build_tree(right_pts, right_lbl, depth - 1, rng),
    }


def _predict_tree(tree, point):
    if isinstance(tree, int):
        return tree
    if point[tree['feat']] <= tree['thresh']:
        return _predict_tree(tree['left'], point)
    return _predict_tree(tree['right'], point)


def _bootstrap(points, labels, seed):
    rng = [seed]
    n = len(points)
    idxs = []
    for _ in range(n):
        rng[0] = (rng[0] * 1103515245 + 12345) & 0x7FFFFFFF
        idxs.append(rng[0] % n)
    return [points[i] for i in idxs], [labels[i] for i in idxs]


class RandomForestSimulation(AlgorithmPlugin):
    """Random forest ensemble training visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="random-forest",
            name="Random Forest",
            category="machine-learning",
            visualization_type="ARRAY_BARS",
            description="Ensemble of decision trees via bootstrap + random features.",
            intuition=(
                f"Build {_N_TREES} trees, each on a bootstrap sample. "
                "Random feature subset prevents correlation. "
                "Bar height = accuracy of each tree vs. ensemble."
            ),
            complexity_time_best="O(n·trees·log n)",
            complexity_time_average="O(n·trees·log n)",
            complexity_time_worst="O(n²·trees)",
            complexity_space="O(trees·depth)",
            tags=("machine-learning", "random-forest", "ensemble", "decision-tree", "bagging"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        arr = tuple(50 for _ in range(_N_TREES))
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"RandomForest seed={params.seed} trees={_N_TREES}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        seed = int(re.search(r"seed=(\d+)", initial_state.description).group(1))
        points, labels = _gen_data(seed)
        n = len(points)

        trees = []
        tree_accuracies = []

        for t in range(_N_TREES):
            # Bootstrap sample
            bp, bl = _bootstrap(points, labels, seed + t * 31337)
            # Build tree
            rng = [seed + t]
            tree = _build_tree(bp, bl, _MAX_DEPTH, rng)
            trees.append(tree)

            # Evaluate this tree and ensemble so far
            tree_preds = [_predict_tree(tree, p) for p in points]
            tree_acc = sum(1 for i in range(n) if tree_preds[i] == labels[i]) / n
            tree_accuracies.append(tree_acc)

            # Ensemble prediction (majority vote so far)
            ensemble_preds = []
            for p in points:
                votes = [_predict_tree(tr, p) for tr in trees]
                ensemble_preds.append(1 if sum(votes) > len(votes) / 2 else 0)
            ensemble_acc = sum(1 for i in range(n) if ensemble_preds[i] == labels[i]) / n

            arr = tuple(max(1, min(99, int(a * 99))) for a in tree_accuracies) + \
                  tuple(50 for _ in range(_N_TREES - len(tree_accuracies)))

            yield SortState(
                array=arr,
                comparing=(t, t),
                last_swap=(t, t) if tree_acc >= ensemble_acc else None,
                sorted_indices=frozenset(i for i in range(len(trees)) if tree_accuracies[i] >= 0.8),
                comparisons=t + 1,
                swaps=int(ensemble_acc * 100),
                description=f"Tree {t+1}: acc={tree_acc:.0%} | Ensemble: {ensemble_acc:.0%}",
            )

        # Final ensemble accuracy
        ensemble_preds = []
        for p in points:
            votes = [_predict_tree(tr, p) for tr in trees]
            ensemble_preds.append(1 if sum(votes) > len(votes) / 2 else 0)
        final_acc = sum(1 for i in range(n) if ensemble_preds[i] == labels[i]) / n

        arr = tuple(max(1, min(99, int(a * 99))) for a in tree_accuracies)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(_N_TREES)),
            comparisons=_N_TREES,
            swaps=int(final_acc * 100),
            description=f"Forest of {_N_TREES} trees. Final accuracy={final_acc:.0%}",
        )
