from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.orchestration.orchestrator import ControlRoomOrchestrator
from app.database import get_advisory_db, get_blackboard_entries_db

router = APIRouter(prefix="/api/agents", tags=["Agents"])
orchestrator = ControlRoomOrchestrator.get_instance()

AGENT_METADATA = [
    {"name": "intake_agent", "display_name": "Intake Agent", "icon": "UserCheck", "responsibility": "Ingest and validate farmer crop profile, growth stage, and geographic coordinates"},
    {"name": "weather_agent", "display_name": "Weather Agent", "icon": "CloudSun", "responsibility": "Query live meteorological data, analyze rainfall probability, temperature, and wind extremes"},
    {"name": "crop_agent", "display_name": "Crop Agent", "icon": "Sprout", "responsibility": "Analyze crop stage, physiological water requirements, and prescribe targeted agronomic practices"},
    {"name": "market_agent", "display_name": "Market Agent", "icon": "TrendingUp", "responsibility": "Query APMC mandi trading rates, compare historical price dynamics, and compute Sell/Hold/Monitor decision"},
    {"name": "scheme_agent", "display_name": "Scheme Agent (RAG)", "icon": "FileBadge", "responsibility": "Execute RAG vector retrieval over official government scheme knowledge base for subsidies and crop insurance"},
    {"name": "risk_alert_agent", "display_name": "Risk Alert Agent", "icon": "ShieldAlert", "responsibility": "Correlate crop vulnerability matrix with weather hazards and assign threat level (LOW/MEDIUM/HIGH/CRITICAL)"},
    {"name": "advisor_coordinator", "display_name": "Advisor Coordinator", "icon": "BotMessageSquare", "responsibility": "Read entire Blackboard memory, reconcile conflicts, and generate unified farmer-friendly advisory"},
]

@router.get("/status/{request_id}")
async def get_agents_status(request_id: str):
    # Check active run in memory first
    run_status = orchestrator.get_run_status(request_id)
    if run_status:
        return run_status

    # Fallback: recreate status from persisted database records if workflow already completed earlier
    advisory = get_advisory_db(request_id)
    if not advisory:
        raise HTTPException(status_code=404, detail="Request ID not found")

    bb_entries = get_blackboard_entries_db(request_id)
    entry_map = {e["agent_name"]: e for e in bb_entries}

    agent_statuses = []
    for meta in AGENT_METADATA:
        name = meta["name"]
        entry = entry_map.get(name)
        agent_statuses.append({
            "name": name,
            "display_name": meta["display_name"],
            "icon": meta["icon"],
            "responsibility": meta["responsibility"],
            "status": entry["status"] if entry else "COMPLETED" if advisory["status"] == "COMPLETED" else "WAITING",
            "latest_output": entry["output"] if entry else None,
            "timestamp": entry["timestamp"] if entry else advisory["created_at"],
            "execution_time_ms": 120.0
        })

    return {
        "request_id": request_id,
        "workflow_status": advisory["status"],
        "current_stage": "Completed" if advisory["status"] == "COMPLETED" else advisory["status"],
        "risk_level": advisory["risk_level"],
        "agents": agent_statuses,
        "created_at": advisory["created_at"],
        "updated_at": advisory["updated_at"]
    }
