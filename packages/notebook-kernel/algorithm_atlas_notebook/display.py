"""
AtlasDisplay — the return type of atlas.run().

Implements IPython's rich display protocol so Jupyter renders
the embedded HTML player automatically when a cell evaluates to
an AtlasDisplay value.
"""
from __future__ import annotations

import json
import pathlib
from typing import Any

from .player import build_player


class AtlasDisplay:
    """
    Wraps a list of SimulationFrame dicts and renders them as an
    interactive HTML animation in Jupyter / VS Code notebook cells.

    Attributes:
        frames:     Raw frame dicts (same structure as the Python SDK yields).
        slug:       Algorithm identifier (e.g. "bubble-sort").
        seed:       PRNG seed used to generate the input array.
        params:     Parameter dict used for this run.

    Example (Jupyter cell):
        from algorithm_atlas_notebook import run
        run("bubble-sort", seed=42, array_size=30)
    """

    def __init__(
        self,
        frames: list[dict[str, Any]],
        slug: str,
        seed: int,
        params: dict[str, Any],
    ) -> None:
        self.frames = frames
        self.slug   = slug
        self.seed   = seed
        self.params = params

    # ── IPython display protocol ──────────────────────────────────────────────

    def _repr_html_(self) -> str:
        title = f"{self.slug}  ·  seed={self.seed}  ·  {len(self.frames)} frames"
        return build_player(self.frames, title=title)

    def _repr_json_(self) -> dict:
        return {
            "slug":   self.slug,
            "seed":   self.seed,
            "params": self.params,
            "frames": self.frames,
        }

    def __repr__(self) -> str:
        return (
            f"AtlasDisplay(slug={self.slug!r}, seed={self.seed}, "
            f"frames={len(self.frames)}, array_size={self.params.get('array_size', '?')})"
        )

    # ── Export ────────────────────────────────────────────────────────────────

    def save_html(self, path: str | pathlib.Path) -> pathlib.Path:
        """
        Export the simulation as a fully self-contained HTML file.

        The file includes the player, all frame data, and styling — no
        external resources required. Open directly in any modern browser.

        Args:
            path: Output file path (e.g. "bubble_sort_demo.html").

        Returns:
            Resolved path of the written file.
        """
        path = pathlib.Path(path)
        title = f"{self.slug} — Algorithm Atlas"
        player_html = build_player(self.frames, title=f"{self.slug}  ·  seed={self.seed}  ·  {len(self.frames)} frames")
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
  <style>
    body {{ background: #0a0a0a; display: flex; justify-content: center; padding: 40px 16px; margin: 0; }}
  </style>
</head>
<body>
{player_html}
</body>
</html>"""
        path.write_text(html, encoding="utf-8")
        return path.resolve()

    # ── Data access ───────────────────────────────────────────────────────────

    def to_json(self) -> str:
        """Serialize all frames to a JSON string."""
        return json.dumps(self._repr_json_(), indent=2)

    @property
    def array_size(self) -> int:
        return int(self.params.get("array_size", len(self.frames[0]["state"]["array"]) if self.frames else 0))

    @property
    def total_frames(self) -> int:
        return len(self.frames)

    @property
    def comparisons(self) -> int:
        if not self.frames:
            return 0
        return self.frames[-1]["state"].get("comparisons", 0)

    @property
    def swaps(self) -> int:
        if not self.frames:
            return 0
        return self.frames[-1]["state"].get("swaps", 0)
