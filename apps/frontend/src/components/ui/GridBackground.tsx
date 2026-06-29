import { useEffect, useRef } from 'react';

// ── SVG tile helpers ──────────────────────────────────────────────────────────
// Each tile is a rounded-corner square outline drawn with SVG <rect rx>.
// This produces the characteristic Higgsfield "curved cell" look where corners
// arc inward at every intersection.

const CELL = 68;   // px — tile size
const RX   = 12;   // px — corner radius (≈18% of cell = natural Higgsfield ratio)

function makeTile(stroke: string): string {
  const svg =
    `<svg xmlns="http://www.w3.org/2000/svg" width="${CELL}" height="${CELL}">` +
    `<rect x="0.5" y="0.5" width="${CELL - 1}" height="${CELL - 1}" ` +
    `rx="${RX}" ry="${RX}" fill="none" stroke="${stroke}" stroke-width="1"/>` +
    `</svg>`;
  return `url("data:image/svg+xml;base64,${btoa(svg)}")`;
}

const DIM_TILE    = makeTile('rgba(255,255,255,0.018)');         // near-invisible base
const BRIGHT_TILE = makeTile('rgba(148,163,252,0.40)');          // indigo-300, cursor-revealed

// ── Component ─────────────────────────────────────────────────────────────────

export function GridBackground() {
  const brightRef = useRef<HTMLDivElement>(null);
  const glowRef   = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let rafId: number;
    let tx = -9999, ty = -9999;   // target (raw mouse)
    let cx = -9999, cy = -9999;   // current (lerped)
    let ready = false;

    const onMove = (e: MouseEvent) => {
      if (!ready) { cx = e.clientX; cy = e.clientY; ready = true; }
      tx = e.clientX;
      ty = e.clientY;
    };

    const tick = () => {
      // Lerp — 0.10 gives a gentle, natural trail without feeling sluggish
      cx += (tx - cx) * 0.10;
      cy += (ty - cy) * 0.10;

      const x = Math.round(cx);
      const y = Math.round(cy);

      if (brightRef.current) {
        // Mask reveals bright tiles only within radius of cursor
        const m = `radial-gradient(220px circle at ${x}px ${y}px, black 0%, transparent 100%)`;
        brightRef.current.style.maskImage       = m;
        brightRef.current.style.webkitMaskImage = m;
      }

      if (glowRef.current) {
        // Large soft indigo halo — no hard edges
        glowRef.current.style.background =
          `radial-gradient(400px circle at ${x}px ${y}px, rgba(99,102,241,0.07) 0%, transparent 70%)`;
      }

      rafId = requestAnimationFrame(tick);
    };

    window.addEventListener('mousemove', onMove, { passive: true });
    rafId = requestAnimationFrame(tick);
    return () => {
      window.removeEventListener('mousemove', onMove);
      cancelAnimationFrame(rafId);
    };
  }, []);

  const tileSize = `${CELL}px ${CELL}px`;

  return (
    <>
      {/* Layer 1 — dim rounded grid, always visible */}
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-0"
        style={{ zIndex: 0, backgroundImage: DIM_TILE, backgroundSize: tileSize }}
      />

      {/* Layer 2 — bright indigo rounded grid, revealed by cursor mask */}
      <div
        ref={brightRef}
        aria-hidden="true"
        className="pointer-events-none fixed inset-0"
        style={{
          zIndex: 0,
          backgroundImage: BRIGHT_TILE,
          backgroundSize: tileSize,
          maskImage:       `radial-gradient(220px circle at -9999px -9999px, black 0%, transparent 100%)`,
          WebkitMaskImage: `radial-gradient(220px circle at -9999px -9999px, black 0%, transparent 100%)`,
        }}
      />

      {/* Layer 3 — soft indigo ambient glow */}
      <div
        ref={glowRef}
        aria-hidden="true"
        className="pointer-events-none fixed inset-0"
        style={{ zIndex: 0 }}
      />
    </>
  );
}
