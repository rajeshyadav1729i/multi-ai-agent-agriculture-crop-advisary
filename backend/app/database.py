import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.config import settings

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(settings.DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Advisories table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS advisories (
        id TEXT PRIMARY KEY,
        farmer_name TEXT,
        crop_name TEXT NOT NULL,
        location TEXT NOT NULL,
        crop_stage TEXT NOT NULL,
        land_area REAL,
        irrigation_type TEXT,
        risk_level TEXT DEFAULT 'LOW',
        status TEXT DEFAULT 'PENDING',
        final_advisory TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)
    
    # Blackboard entries table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blackboard_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id TEXT NOT NULL,
        agent_name TEXT NOT NULL,
        category TEXT NOT NULL,
        output_json TEXT NOT NULL,
        status TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (request_id) REFERENCES advisories (id) ON DELETE CASCADE
    );
    """)
    
    # Create indexes for quick retrieval
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_board_request ON blackboard_entries(request_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_advisories_created ON advisories(created_at DESC);")
    
    conn.commit()
    conn.close()

# Database operations
def save_advisory(
    request_id: str,
    crop_name: str,
    location: str,
    crop_stage: str,
    farmer_name: Optional[str] = None,
    land_area: Optional[float] = None,
    irrigation_type: Optional[str] = None,
    risk_level: str = "LOW",
    status: str = "PENDING",
    final_advisory: Optional[Dict[str, Any]] = None
):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    advisory_str = json.dumps(final_advisory) if final_advisory else None
    
    cursor.execute("""
        INSERT INTO advisories (id, farmer_name, crop_name, location, crop_stage, land_area, irrigation_type, risk_level, status, final_advisory, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            risk_level = excluded.risk_level,
            status = excluded.status,
            final_advisory = excluded.final_advisory,
            updated_at = excluded.updated_at;
    """, (request_id, farmer_name, crop_name, location, crop_stage, land_area, irrigation_type, risk_level, status, advisory_str, now, now))
    
    conn.commit()
    conn.close()

def update_advisory_status(request_id: str, status: str, risk_level: Optional[str] = None, final_advisory: Optional[Dict[str, Any]] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    if final_advisory is not None and risk_level is not None:
        cursor.execute("""
            UPDATE advisories
            SET status = ?, risk_level = ?, final_advisory = ?, updated_at = ?
            WHERE id = ?
        """, (status, risk_level, json.dumps(final_advisory), now, request_id))
    elif risk_level is not None:
        cursor.execute("""
            UPDATE advisories
            SET status = ?, risk_level = ?, updated_at = ?
            WHERE id = ?
        """, (status, risk_level, now, request_id))
    else:
        cursor.execute("""
            UPDATE advisories
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (status, now, request_id))
        
    conn.commit()
    conn.close()

def save_blackboard_entry(request_id: str, agent_name: str, category: str, output: Dict[str, Any], status: str = "COMPLETED") -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    output_str = json.dumps(output)
    
    cursor.execute("""
        INSERT INTO blackboard_entries (request_id, agent_name, category, output_json, status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (request_id, agent_name, category, output_str, status, now))
    
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return entry_id

def get_blackboard_entries_db(request_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, request_id, agent_name, category, output_json, status, timestamp
        FROM blackboard_entries
        WHERE request_id = ?
        ORDER BY id ASC
    """, (request_id,))
    rows = cursor.fetchall()
    conn.close()
    
    entries = []
    for r in rows:
        try:
            output_parsed = json.loads(r["output_json"])
        except Exception:
            output_parsed = {"raw": r["output_json"]}
        entries.append({
            "id": r["id"],
            "request_id": r["request_id"],
            "agent_name": r["agent_name"],
            "category": r["category"],
            "output": output_parsed,
            "status": r["status"],
            "timestamp": r["timestamp"]
        })
    return entries

def get_advisory_db(request_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM advisories WHERE id = ?", (request_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    final_adv = None
    if row["final_advisory"]:
        try:
            final_adv = json.loads(row["final_advisory"])
        except Exception:
            final_adv = {"raw": row["final_advisory"]}
            
    return {
        "id": row["id"],
        "farmer_name": row["farmer_name"],
        "crop_name": row["crop_name"],
        "location": row["location"],
        "crop_stage": row["crop_stage"],
        "land_area": row["land_area"],
        "irrigation_type": row["irrigation_type"],
        "risk_level": row["risk_level"],
        "status": row["status"],
        "final_advisory": final_adv,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"]
    }

def get_all_advisories_db(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM advisories
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        final_adv = None
        if row["final_advisory"]:
            try:
                final_adv = json.loads(row["final_advisory"])
            except Exception:
                final_adv = {"raw": row["final_advisory"]}
        results.append({
            "id": row["id"],
            "farmer_name": row["farmer_name"],
            "crop_name": row["crop_name"],
            "location": row["location"],
            "crop_stage": row["crop_stage"],
            "land_area": row["land_area"],
            "irrigation_type": row["irrigation_type"],
            "risk_level": row["risk_level"],
            "status": row["status"],
            "final_advisory": final_adv,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        })
    return results
