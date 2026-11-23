import time
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.database import save_blackboard_entry, get_blackboard_entries_db

class Blackboard:
    """
    Central Shared Blackboard Architecture (Control Room Memory)
    All 7 agents publish their findings and read dependencies from this shared memory.
    Every update is persisted to SQLite for complete auditability.
    """
    _instance = None

    def __init__(self):
        # In-memory board state keyed by request_id -> list of entries
        self._memory_board: Dict[str, List[Dict[str, Any]]] = {}
        # Active listeners for real-time streaming / SSE
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Blackboard()
        return cls._instance

    async def post(
        self,
        request_id: str,
        agent_name: str,
        category: str,
        output_data: Dict[str, Any],
        status: str = "COMPLETED"
    ) -> Dict[str, Any]:
        """
        Publishes an entry from an agent to the shared blackboard.
        """
        timestamp = datetime.now().isoformat()
        
        # Persist to SQLite
        entry_id = save_blackboard_entry(
            request_id=request_id,
            agent_name=agent_name,
            category=category,
            output=output_data,
            status=status
        )

        entry = {
            "id": entry_id,
            "request_id": request_id,
            "agent_name": agent_name,
            "category": category,
            "output": output_data,
            "status": status,
            "timestamp": timestamp
        }

        if request_id not in self._memory_board:
            self._memory_board[request_id] = []
        self._memory_board[request_id].append(entry)

        # Notify any active subscribers (SSE/WebSocket streams)
        if request_id in self._subscribers:
            for queue in self._subscribers[request_id]:
                await queue.put(entry)

        return entry

    def get_entries(self, request_id: str) -> List[Dict[str, Any]]:
        """
        Reads all blackboard entries for a request_id.
        """
        if request_id in self._memory_board and len(self._memory_board[request_id]) > 0:
            return self._memory_board[request_id]
        
        # Fallback to database
        db_entries = get_blackboard_entries_db(request_id)
        self._memory_board[request_id] = db_entries
        return db_entries

    def get_agent_output(self, request_id: str, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the latest output published by a specific agent.
        """
        entries = self.get_entries(request_id)
        for entry in reversed(entries):
            if entry["agent_name"].lower() == agent_name.lower():
                return entry["output"]
        return None

    def subscribe(self, request_id: str) -> asyncio.Queue:
        """
        Subscribes to live blackboard events for real-time UI updates.
        """
        if request_id not in self._subscribers:
            self._subscribers[request_id] = []
        q = asyncio.Queue()
        self._subscribers[request_id].append(q)
        return q

    def unsubscribe(self, request_id: str, queue: asyncio.Queue):
        if request_id in self._subscribers:
            if queue in self._subscribers[request_id]:
                self._subscribers[request_id].remove(queue)
