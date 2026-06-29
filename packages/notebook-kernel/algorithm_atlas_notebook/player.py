"""
Self-contained HTML animation player for Algorithm Atlas simulation frames.

Generates a single <div> + inline <script> that:
  - Renders SortState frames as an animated bar chart on <canvas>
  - Provides play / pause / step-back / step-forward / speed controls
  - Requires zero external dependencies (no CDN, no React)
  - Works offline in Jupyter, VS Code notebooks, and exported HTML

Each call to build_player() gets a unique DOM id so multiple cells
can show different simulations without conflicts.
"""
from __future__ import annotations

import json
import uuid
from typing import Any


def build_player(frames: list[dict[str, Any]], title: str = "") -> str:
    """
    Return a self-contained HTML string for embedding in a Jupyter cell.

    Args:
        frames: List of SimulationFrame dicts (as returned by the Python plugin or Rust engine).
        title:  Optional header shown above the player.
    """
    uid     = uuid.uuid4().hex[:8]
    n_frames = len(frames)
    frames_json = json.dumps(frames)

    return f"""
<div id="atlas-{uid}" style="font-family:ui-monospace,monospace;background:#0f0f0f;border-radius:12px;padding:16px;color:#e5e5e5;max-width:700px;">
  {"" if not title else f'<div style="font-size:13px;font-weight:600;color:#818cf8;margin-bottom:10px;">{title}</div>'}
  <canvas id="canvas-{uid}" width="660" height="220"
          style="display:block;border-radius:8px;background:#1c1c1c;"></canvas>
  <div style="margin-top:6px;font-size:11px;color:#525252;min-height:18px;" id="desc-{uid}"></div>
  <div style="display:flex;align-items:center;gap:8px;margin-top:10px;flex-wrap:wrap;">
    <button id="btn-prev-{uid}" style="{_btn_style()}">&#9664;</button>
    <button id="btn-play-{uid}" style="{_btn_style(accent=True)}">&#9654;</button>
    <button id="btn-next-{uid}" style="{_btn_style()}">&#9654;|</button>
    <input id="seek-{uid}" type="range" min="0" max="{n_frames - 1}" value="0"
           style="flex:1;min-width:80px;accent-color:#818cf8;">
    <span id="counter-{uid}" style="font-size:11px;color:#525252;white-space:nowrap;">0 / {n_frames - 1}</span>
    <label style="font-size:11px;color:#525252;display:flex;align-items:center;gap:4px;">
      speed
      <select id="speed-{uid}" style="background:#262626;color:#e5e5e5;border:1px solid #404040;border-radius:4px;font-size:11px;padding:1px 4px;">
        <option value="0.5">0.5×</option>
        <option value="1" selected>1×</option>
        <option value="2">2×</option>
        <option value="4">4×</option>
      </select>
    </label>
    <span id="stats-{uid}" style="font-size:11px;color:#404040;"></span>
  </div>
</div>
<script>
(function() {{
  const FRAMES = {frames_json};
  const uid = "{uid}";
  const canvas = document.getElementById("canvas-" + uid);
  const ctx    = canvas.getContext("2d");
  const descEl = document.getElementById("desc-" + uid);
  const countEl = document.getElementById("counter-" + uid);
  const seekEl  = document.getElementById("seek-" + uid);
  const statsEl = document.getElementById("stats-" + uid);
  const playBtn = document.getElementById("btn-play-" + uid);
  const prevBtn = document.getElementById("btn-prev-" + uid);
  const nextBtn = document.getElementById("btn-next-" + uid);
  const speedSel = document.getElementById("speed-" + uid);

  let cur = 0;
  let playing = false;
  let timerId = null;

  // Colour helpers
  function barColor(frame, idx) {{
    const s = frame.state;
    if (s.sorted_indices && s.sorted_indices.includes(idx)) return "#22c55e";
    if (s.comparing && s.comparing.includes(idx)) return "#fbbf24";
    if (s.last_swap && s.last_swap.includes(idx)) return "#f87171";
    if (s.auxiliary_indices && s.auxiliary_indices.includes(idx)) return "#818cf8";
    return "#3f3f46";
  }}

  function draw(frameIdx) {{
    const frame = FRAMES[frameIdx];
    if (!frame) return;
    const arr   = frame.state.array;
    const n     = arr.length;
    const W = canvas.width;
    const H = canvas.height;
    const maxVal = Math.max(...arr, 1);
    const barW   = Math.floor((W - 2) / n);
    const gap    = 1;

    ctx.clearRect(0, 0, W, H);
    for (let i = 0; i < n; i++) {{
      const bh   = Math.round((arr[i] / maxVal) * (H - 4));
      const x    = i * barW + gap;
      const y    = H - bh - 2;
      ctx.fillStyle = barColor(frame, i);
      ctx.fillRect(x, y, barW - gap, bh);
    }}

    // Frame counter & description
    descEl.textContent  = frame.state.description || "";
    countEl.textContent = frameIdx + " / " + (FRAMES.length - 1);
    seekEl.value        = frameIdx;
    const s = frame.state;
    if (s.comparisons !== undefined) {{
      statsEl.textContent = "cmp " + s.comparisons + "  swp " + s.swaps;
    }}
  }}

  function goTo(i) {{
    cur = Math.max(0, Math.min(FRAMES.length - 1, i));
    draw(cur);
  }}

  function togglePlay() {{
    playing = !playing;
    playBtn.textContent = playing ? "⏸" : "▶";
    if (playing) {{
      function tick() {{
        if (!playing || cur >= FRAMES.length - 1) {{
          playing = false;
          playBtn.textContent = "▶";
          return;
        }}
        goTo(cur + 1);
        const speed = parseFloat(speedSel.value);
        timerId = setTimeout(tick, Math.round(80 / speed));
      }}
      timerId = setTimeout(tick, 0);
    }} else {{
      clearTimeout(timerId);
    }}
  }}

  playBtn.addEventListener("click", togglePlay);
  prevBtn.addEventListener("click", () => {{ if (playing) togglePlay(); goTo(cur - 1); }});
  nextBtn.addEventListener("click", () => {{ if (playing) togglePlay(); goTo(cur + 1); }});
  seekEl.addEventListener("input",  () => {{ if (playing) togglePlay(); goTo(parseInt(seekEl.value)); }});

  draw(0);
}})();
</script>
"""


def _btn_style(accent: bool = False) -> str:
    bg = "#6366f1" if accent else "#262626"
    return (
        f"background:{bg};color:#e5e5e5;border:1px solid #404040;"
        "border-radius:6px;padding:4px 10px;font-size:12px;"
        "cursor:pointer;font-family:ui-monospace,monospace;"
    )
