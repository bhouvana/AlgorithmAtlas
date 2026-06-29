"""
Simulation session endpoints and WebSocket handler.

POST /api/v1/simulations               — create a session
GET  /api/v1/simulations/{id}          — get session status
DELETE /api/v1/simulations/{id}        — destroy session
WS   /ws/v1/simulations/{id}           — real-time simulation stream
"""
from __future__ import annotations

import asyncio
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from loguru import logger
from pydantic import BaseModel, Field, field_validator

from algorithm_atlas.plugins.registry import AlgorithmNotFound, get_registry
from algorithm_atlas.simulation.engine import SimulationController, SimulationStatus
from algorithm_atlas.simulation.session_store import get_session_store
from algorithm_atlas_sdk.types import SimulationParams

router = APIRouter(tags=["simulations"])

# ──────────────────────────────────────────────────────────────────────────────
# Request / Response models
# ──────────────────────────────────────────────────────────────────────────────

class CreateSimulationRequest(BaseModel):
    algorithm_slug: str
    params: dict = Field(default_factory=dict)
    seed: int = Field(default=42, ge=0)


class CreateSimulationResponse(BaseModel):
    session_id: str
    algorithm_slug: str
    status: str
    seed: int


class SimulationStatusResponse(BaseModel):
    session_id: str
    status: str
    current_frame: int
    total_frames: Optional[int]
    playback_speed: float


# ──────────────────────────────────────────────────────────────────────────────
# REST endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/api/v1/simulations", response_model=CreateSimulationResponse, status_code=201)
async def create_simulation(body: CreateSimulationRequest):
    registry = get_registry()
    try:
        registered = registry.get(body.algorithm_slug)
    except AlgorithmNotFound:
        raise HTTPException(status_code=404, detail=f"Algorithm '{body.algorithm_slug}' not found")

    session_id = str(uuid.uuid4())
    params = SimulationParams(
        seed=body.seed,
        inputs=body.params,
        config={},
    )

    algorithm = registered.instantiate()
    controller = SimulationController(
        session_id=session_id,
        algorithm=algorithm,
        params=params,
    )

    # Initialize eagerly to surface errors immediately
    await controller.initialize()

    store = get_session_store()
    store.put(controller)

    logger.info(f"Session {session_id} created for algorithm '{body.algorithm_slug}'")
    return CreateSimulationResponse(
        session_id=session_id,
        algorithm_slug=body.algorithm_slug,
        status=controller.status.value,
        seed=body.seed,
    )


@router.get("/api/v1/simulations/{session_id}", response_model=SimulationStatusResponse)
async def get_simulation(session_id: str):
    store = get_session_store()
    controller = store.get(session_id)
    if not controller:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return SimulationStatusResponse(
        session_id=session_id,
        status=controller.status.value,
        current_frame=controller.current_frame_index,
        total_frames=controller.total_frames,
        playback_speed=controller.playback_speed,
    )


@router.delete("/api/v1/simulations/{session_id}", status_code=204)
async def delete_simulation(session_id: str):
    store = get_session_store()
    if not store.get(session_id):
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    store.delete(session_id)


# ──────────────────────────────────────────────────────────────────────────────
# WebSocket handler
# ──────────────────────────────────────────────────────────────────────────────

@router.websocket("/ws/v1/simulations/{session_id}")
async def simulation_websocket(websocket: WebSocket, session_id: str):
    """
    Real-time simulation stream.

    Architecture:
    - send_queue serializes all outgoing WebSocket messages
    - sender_task drains send_queue to the WebSocket (no concurrent sends)
    - stream_task pushes frames into send_queue at the playback speed
    - receive loop handles client control messages and manages task lifecycle
    """
    store = get_session_store()
    controller = store.get(session_id)

    await websocket.accept()

    if not controller:
        await websocket.send_json({
            "type": "error",
            "code": "SESSION_NOT_FOUND",
            "message": f"Session '{session_id}' not found or expired",
        })
        await websocket.close(code=4404)
        return

    # Send the initial frame immediately on connection
    initial_frame = controller.get_current_frame()
    await websocket.send_json({
        "type": "frame",
        "data": initial_frame.to_dict(),
    })
    await websocket.send_json({
        "type": "status",
        "status": controller.status.value,
        "total_frames": controller.total_frames,
        "current_frame": controller.current_frame_index,
    })

    # Serialized send queue — prevents concurrent WebSocket write races
    send_queue: asyncio.Queue = asyncio.Queue(maxsize=256)

    async def sender():
        """Drain send_queue and write to WebSocket. Stops on None sentinel."""
        while True:
            msg = await send_queue.get()
            if msg is None:
                break
            try:
                await websocket.send_json(msg)
            except Exception:
                break

    sender_task = asyncio.create_task(sender())
    stream_task: Optional[asyncio.Task] = None

    try:
        while True:
            msg = await websocket.receive_json()
            msg_type = msg.get("type")

            if msg_type == "play":
                speed = float(msg.get("speed", 1.0))
                controller.set_speed(speed)
                if stream_task and not stream_task.done():
                    stream_task.cancel()
                    try:
                        await stream_task
                    except asyncio.CancelledError:
                        pass
                stream_task = asyncio.create_task(controller.stream(send_queue))

            elif msg_type == "pause":
                controller.pause()
                if stream_task and not stream_task.done():
                    stream_task.cancel()
                await send_queue.put({"type": "status", "status": "paused"})

            elif msg_type == "step_forward":
                if stream_task and not stream_task.done():
                    stream_task.cancel()
                try:
                    frame = controller.step_forward()
                    await send_queue.put({"type": "frame", "data": frame.to_dict()})
                except IndexError:
                    await send_queue.put({"type": "status", "status": "completed"})

            elif msg_type == "step_backward":
                if stream_task and not stream_task.done():
                    stream_task.cancel()
                try:
                    frame = controller.step_backward()
                    await send_queue.put({"type": "frame", "data": frame.to_dict()})
                except IndexError:
                    await send_queue.put({
                        "type": "error",
                        "code": "AT_FIRST_FRAME",
                        "message": "Already at the first frame",
                    })

            elif msg_type == "seek":
                if stream_task and not stream_task.done():
                    stream_task.cancel()
                frame_index = int(msg.get("frame_index", 0))
                try:
                    frame = controller.seek(frame_index)
                    await send_queue.put({"type": "frame", "data": frame.to_dict()})
                except (IndexError, ValueError) as exc:
                    await send_queue.put({
                        "type": "error",
                        "code": "SEEK_OUT_OF_BOUNDS",
                        "message": str(exc),
                    })

            elif msg_type == "reset":
                if stream_task and not stream_task.done():
                    stream_task.cancel()
                frame = await controller.reset()
                await send_queue.put({"type": "frame", "data": frame.to_dict()})
                await send_queue.put({"type": "status", "status": "paused", "current_frame": 0})

            elif msg_type == "set_speed":
                speed = float(msg.get("speed", 1.0))
                try:
                    controller.set_speed(speed)
                    await send_queue.put({"type": "status", "status": controller.status.value})
                except ValueError as exc:
                    await send_queue.put({
                        "type": "error",
                        "code": "INVALID_SPEED",
                        "message": str(exc),
                    })

            elif msg_type == "ping":
                await send_queue.put({"type": "pong"})

    except WebSocketDisconnect:
        logger.info(f"[{session_id}] WebSocket disconnected")
    except Exception as exc:
        logger.exception(f"[{session_id}] Unexpected WebSocket error: {exc}")
    finally:
        if stream_task and not stream_task.done():
            stream_task.cancel()
        await send_queue.put(None)  # Signal sender to stop
        await sender_task
        logger.debug(f"[{session_id}] WebSocket handler cleaned up")
