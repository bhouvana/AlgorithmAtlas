"""
Simulation Engine — FrameBuffer and SimulationController.

This is the most critical module. Its correctness determines whether every
simulation feature (play, pause, step, rewind, seek, replay) works correctly.

Design decisions:
- Algorithms are generators; this engine wraps them.
- Frames are materialized lazily on demand.
- Rewind never re-runs the algorithm (O(1) access to any past frame).
- WebSocket sends are serialized through a queue to prevent concurrent-write races.
"""
from __future__ import annotations

import asyncio
import uuid
from enum import Enum
from typing import Any, Dict, Generator, List, Optional

from loguru import logger

from algorithm_atlas_sdk.types import (
    AlgorithmState,
    SimulationFrame,
    SimulationParams,
)


class SimulationStatus(str, Enum):
    CREATED = "created"
    PAUSED = "paused"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


# ---------------------------------------------------------------------------
# Frame Buffer
# ---------------------------------------------------------------------------

class FrameBuffer:
    """
    Lazy, append-only frame store backed by an algorithm generator.

    - get_frame(i) materializes frames 0..i on demand
    - Already-materialized frames are never recomputed
    - Exhaustion is detected via StopIteration from the generator
    - O(1) access to any frame index that has been materialized
    """

    MS_PER_STEP = 100  # Logical milliseconds between frames at 1x speed

    def __init__(
        self,
        generator: Generator[AlgorithmState, None, AlgorithmState],
    ) -> None:
        self._generator = generator
        self._frames: List[SimulationFrame] = []
        self._exhausted = False

    # ------------------------------------------------------------------ public

    def get_frame(self, index: int) -> SimulationFrame:
        """
        Return frame at index. Advances the generator as needed.
        Raises IndexError if index is beyond the simulation's terminal frame.
        """
        self._materialize_through(index)
        if index >= len(self._frames):
            raise IndexError(
                f"Frame {index} does not exist — "
                f"simulation has {len(self._frames)} frame(s) total."
            )
        return self._frames[index]

    def has_next(self, current_index: int) -> bool:
        """True if a frame beyond current_index exists or can be materialized."""
        next_index = current_index + 1
        if next_index < len(self._frames):
            return True
        if self._exhausted:
            return False
        self._advance()
        return next_index < len(self._frames)

    @property
    def length(self) -> int:
        return len(self._frames)

    @property
    def is_complete(self) -> bool:
        return self._exhausted

    @property
    def total_frames(self) -> Optional[int]:
        """Only available once the simulation is complete."""
        return len(self._frames) if self._exhausted else None

    # ----------------------------------------------------------------- private

    def _materialize_through(self, index: int) -> None:
        while index >= len(self._frames) and not self._exhausted:
            self._advance()

    def _advance(self) -> None:
        """Pull one state from the generator and append a SimulationFrame."""
        try:
            state = next(self._generator)
            self._append_frame(state)
        except StopIteration as exc:
            # StopIteration.value carries the terminal state
            if exc.value is not None:
                self._append_frame(exc.value)
            self._exhausted = True

    def _append_frame(self, state: AlgorithmState) -> None:
        frame = SimulationFrame(
            frame_index=len(self._frames),
            state=state,
            timestamp_ms=len(self._frames) * self.MS_PER_STEP,
            event_label=getattr(state, "description", None) or None,
        )
        self._frames.append(frame)


# ---------------------------------------------------------------------------
# Simulation Controller
# ---------------------------------------------------------------------------

class SimulationController:
    """
    Manages one active simulation session end-to-end.

    Responsibilities:
    - Owns the FrameBuffer for this session
    - Tracks playback cursor (current_frame_index)
    - Streams frames to a WebSocket via a serialized send queue
    - Responds to control messages: play, pause, step, seek, reset
    """

    def __init__(
        self,
        session_id: str,
        algorithm: Any,  # AlgorithmPlugin — avoids circular import
        params: SimulationParams,
    ) -> None:
        self.session_id = session_id
        self._algorithm = algorithm
        self._params = params
        self._status = SimulationStatus.CREATED
        self._current_frame_index = 0
        self._playback_speed = 1.0
        self._buffer: Optional[FrameBuffer] = None

    # ------------------------------------------------------------------ setup

    async def initialize(self) -> SimulationFrame:
        """
        Create the generator, wrap it in a FrameBuffer, and return frame 0.
        Must be called before any other method.
        """
        try:
            initial_state = self._algorithm.initialize(self._params)
            generator = self._algorithm.steps(initial_state)
            self._buffer = FrameBuffer(generator)
            first_frame = self._buffer.get_frame(0)
            self._current_frame_index = 0
            self._status = SimulationStatus.PAUSED
            logger.debug(f"[{self.session_id}] Initialized — frame 0 ready")
            return first_frame
        except Exception as exc:
            self._status = SimulationStatus.ERROR
            logger.error(f"[{self.session_id}] Initialization failed: {exc}")
            raise

    # -------------------------------------------------------------- navigation

    def step_forward(self) -> SimulationFrame:
        """Advance the cursor one frame. Raises IndexError at the last frame."""
        self._assert_initialized()
        next_index = self._current_frame_index + 1
        frame = self._buffer.get_frame(next_index)  # type: ignore[union-attr]
        self._current_frame_index = next_index
        if self._buffer.is_complete and next_index == self._buffer.length - 1:  # type: ignore[union-attr]
            self._status = SimulationStatus.COMPLETED
        return frame

    def step_backward(self) -> SimulationFrame:
        """Move the cursor back one frame. Raises IndexError at frame 0."""
        self._assert_initialized()
        if self._current_frame_index == 0:
            raise IndexError("Already at the first frame.")
        self._current_frame_index -= 1
        return self._buffer.get_frame(self._current_frame_index)  # type: ignore[union-attr]

    def seek(self, frame_index: int) -> SimulationFrame:
        """Jump the cursor to an arbitrary frame index."""
        self._assert_initialized()
        if frame_index < 0:
            raise ValueError(f"frame_index must be >= 0, got {frame_index}")
        frame = self._buffer.get_frame(frame_index)  # type: ignore[union-attr]
        self._current_frame_index = frame_index
        return frame

    async def reset(self) -> SimulationFrame:
        """Tear down and re-initialize the simulation from scratch."""
        self._status = SimulationStatus.CREATED
        self._buffer = None
        self._current_frame_index = 0
        return await self.initialize()

    # ------------------------------------------------------------ playback control

    def set_speed(self, speed: float) -> None:
        if not (0.1 <= speed <= 10.0):
            raise ValueError(f"Speed must be in [0.1, 10.0], got {speed}")
        self._playback_speed = speed

    def pause(self) -> None:
        if self._status == SimulationStatus.RUNNING:
            self._status = SimulationStatus.PAUSED

    def get_current_frame(self) -> SimulationFrame:
        self._assert_initialized()
        return self._buffer.get_frame(self._current_frame_index)  # type: ignore[union-attr]

    # -------------------------------------------------------------- streaming

    async def stream(self, send_queue: asyncio.Queue) -> None:
        """
        Push frames into send_queue at the configured playback speed until:
        - paused (status changes to PAUSED)
        - simulation completes (no more frames)
        - cancelled (asyncio.CancelledError)

        Callers own the send_queue and the WebSocket sender coroutine.
        This method only produces; it never calls websocket.send_json() directly.
        """
        self._assert_initialized()
        self._status = SimulationStatus.RUNNING
        base_delay = 0.5  # 500ms per frame at 1x — matches WASM playback speed

        try:
            while self._status == SimulationStatus.RUNNING:
                next_index = self._current_frame_index + 1
                try:
                    frame = self._buffer.get_frame(next_index)  # type: ignore[union-attr]
                    self._current_frame_index = next_index
                    await send_queue.put({"type": "frame", "data": frame.to_dict()})
                    await asyncio.sleep(base_delay / self._playback_speed)
                except IndexError:
                    self._status = SimulationStatus.COMPLETED
                    total = self._buffer.total_frames  # type: ignore[union-attr]
                    await send_queue.put({
                        "type": "status",
                        "status": "completed",
                        "total_frames": total,
                    })
                    break
        except asyncio.CancelledError:
            logger.debug(f"[{self.session_id}] Stream cancelled at frame {self._current_frame_index}")
            raise

    # ---------------------------------------------------------------- properties

    @property
    def status(self) -> SimulationStatus:
        return self._status

    @property
    def current_frame_index(self) -> int:
        return self._current_frame_index

    @property
    def total_frames(self) -> Optional[int]:
        return self._buffer.total_frames if self._buffer else None

    @property
    def playback_speed(self) -> float:
        return self._playback_speed

    # ----------------------------------------------------------------- internal

    def _assert_initialized(self) -> None:
        if self._buffer is None:
            raise RuntimeError(
                f"SimulationController for session '{self.session_id}' "
                "has not been initialized. Call initialize() first."
            )
