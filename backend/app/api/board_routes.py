import asyncio
import json
from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse
from typing import List, Dict, Any

from app.orchestration.blackboard import Blackboard
from app.database import get_blackboard_entries_db

router = APIRouter(prefix="/api/blackboard", tags=["Blackboard"])
blackboard = Blackboard.get_instance()

@router.get("/{request_id}")
async def get_blackboard_entries(request_id: str):
    entries = blackboard.get_entries(request_id)
    return {
        "request_id": request_id,
        "total_entries": len(entries),
        "entries": entries
    }

@router.get("/{request_id}/stream")
async def stream_blackboard_events(request_id: str):
    """
    Server-Sent Events (SSE) stream for live Blackboard updates
    """
    queue = blackboard.subscribe(request_id)

    async def event_generator():
        # First send any existing entries
        existing = blackboard.get_entries(request_id)
        for entry in existing:
            yield {
                "event": "entry",
                "data": json.dumps(entry)
            }

        try:
            while True:
                entry = await asyncio.wait_for(queue.get(), timeout=20.0)
                yield {
                    "event": "entry",
                    "data": json.dumps(entry)
                }
                if entry.get("agent_name") == "advisor_coordinator" and entry.get("status") in ["COMPLETED", "FAILED"]:
                    yield {
                        "event": "done",
                        "data": json.dumps({"status": "FINISHED"})
                    }
                    break
        except asyncio.TimeoutError:
            yield {
                "event": "ping",
                "data": json.dumps({"status": "alive"})
            }
        finally:
            blackboard.unsubscribe(request_id, queue)

    return EventSourceResponse(event_generator())
