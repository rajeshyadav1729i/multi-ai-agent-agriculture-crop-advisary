from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.database import get_all_advisories_db, get_db_connection

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("")
async def get_history():
    advisories = get_all_advisories_db(limit=100)
    return {
        "total": len(advisories),
        "advisories": advisories
    }

@router.get("/stats")
async def get_dashboard_stats():
    advisories = get_all_advisories_db(limit=200)
    total_advisories = len(advisories)
    high_risk_count = sum(1 for a in advisories if a.get("risk_level") in ["HIGH", "CRITICAL"])
    
    # Crop breakdown
    crop_counts: Dict[str, int] = {}
    for a in advisories:
        c = a.get("crop_name", "Unknown").title()
        crop_counts[c] = crop_counts.get(c, 0) + 1

    crop_distribution = [
        {"crop": k, "count": v} for k, v in crop_counts.items()
    ]

    return {
        "total_advisories": total_advisories,
        "active_agents": 7, # 7 specialized agents
        "high_risk_alerts": high_risk_count,
        "schemes_retrieved": 6, # 6 indexed government schemes
        "crop_distribution": crop_distribution,
        "recent_advisories": advisories[:5]
    }

@router.delete("/{request_id}")
async def delete_history_item(request_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blackboard_entries WHERE request_id = ?", (request_id,))
    cursor.execute("DELETE FROM advisories WHERE id = ?", (request_id,))
    conn.commit()
    conn.close()
    return {"message": f"Advisory {request_id} deleted successfully."}
