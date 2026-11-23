from fastapi import APIRouter, HTTPException, Response
from typing import Dict, Any
from app.models.advisory import FarmerInput, AdvisoryGenerationResponse
from app.orchestration.orchestrator import ControlRoomOrchestrator
from app.database import get_advisory_db
from app.services.pdf_service import generate_advisory_pdf
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/advisory", tags=["Advisory"])
orchestrator = ControlRoomOrchestrator.get_instance()

@router.post("/generate", response_model=AdvisoryGenerationResponse)
async def generate_advisory(farmer_input: FarmerInput):
    request_id = str(uuid.uuid4())
    await orchestrator.run_workflow(farmer_input, request_id)
    return AdvisoryGenerationResponse(
        request_id=request_id,
        message="Multi-Agent Advisory Workflow initiated successfully.",
        status="RUNNING",
        created_at=datetime.now().isoformat()
    )

@router.get("/{request_id}")
async def get_advisory(request_id: str):
    # Check database first
    advisory = get_advisory_db(request_id)
    if not advisory:
        raise HTTPException(status_code=404, detail="Advisory request not found")

    # If run is still active in memory, merge live stage info
    run_status = orchestrator.get_run_status(request_id)
    if run_status:
        advisory["live_stage"] = run_status.get("current_stage")
        advisory["live_workflow_status"] = run_status.get("workflow_status")

    return advisory

@router.get("/{request_id}/pdf")
async def download_advisory_pdf(request_id: str):
    advisory = get_advisory_db(request_id)
    if not advisory:
        raise HTTPException(status_code=404, detail="Advisory not found")
        
    pdf_buffer = generate_advisory_pdf(advisory)
    crop_name = advisory.get("crop_name", "Crop").replace(" ", "_")
    filename = f"AgriAdvisory_{crop_name}_{request_id[:8]}.pdf"
    
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
