from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class BlackboardEntry(BaseModel):
    id: Optional[int] = None
    request_id: str
    agent_name: str
    category: str
    output: Dict[str, Any]
    status: str = "COMPLETED"
    timestamp: str

class AgentStatus(BaseModel):
    name: str
    display_name: str
    icon: str
    responsibility: str
    status: str = "WAITING" # WAITING, RUNNING, COMPLETED, FAILED
    latest_output: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    execution_time_ms: Optional[float] = None

class ControlRoomStatus(BaseModel):
    request_id: str
    workflow_status: str
    overall_risk_level: str
    agents: List[AgentStatus]
    blackboard_entries_count: int
    updated_at: str
