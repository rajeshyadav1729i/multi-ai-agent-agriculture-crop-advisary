import asyncio
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.orchestration.blackboard import Blackboard
from app.database import save_advisory, update_advisory_status
from app.models.advisory import FarmerInput
from app.agents.intake_agent import IntakeAgent
from app.agents.weather_agent import WeatherAgent
from app.agents.crop_agent import CropAgent
from app.agents.market_agent import MarketAgent
from app.agents.scheme_agent import SchemeAgent
from app.agents.risk_alert_agent import RiskAlertAgent
from app.agents.advisor_coordinator import AdvisorCoordinator

logger = logging.getLogger(__name__)

class ControlRoomOrchestrator:
    """
    Central Orchestrator managing multi-agent execution pipeline.
    Enforces inter-agent dependencies while executing independent agents concurrently.
    """
    _instance = None

    def __init__(self):
        self.blackboard = Blackboard.get_instance()
        # Active workflow runs: request_id -> Dict of agent instances & metadata
        self._active_runs: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ControlRoomOrchestrator()
        return cls._instance

    def create_agent_instances(self) -> Dict[str, Any]:
        return {
            "intake_agent": IntakeAgent(),
            "weather_agent": WeatherAgent(),
            "crop_agent": CropAgent(),
            "market_agent": MarketAgent(),
            "scheme_agent": SchemeAgent(),
            "risk_alert_agent": RiskAlertAgent(),
            "advisor_coordinator": AdvisorCoordinator(),
        }

    def get_run_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        if request_id not in self._active_runs:
            return None
        run_data = self._active_runs[request_id]
        agents_dict = run_data["agents"]
        
        agent_statuses = [
            agent.get_status_info() for agent in agents_dict.values()
        ]
        
        return {
            "request_id": request_id,
            "workflow_status": run_data.get("status", "PENDING"),
            "current_stage": run_data.get("stage", "Initializing"),
            "risk_level": run_data.get("risk_level", "LOW"),
            "agents": agent_statuses,
            "created_at": run_data.get("created_at"),
            "updated_at": datetime.now().isoformat()
        }

    async def run_workflow(self, farmer_input: FarmerInput, request_id: Optional[str] = None) -> str:
        if not request_id:
            request_id = str(uuid.uuid4())

        agents = self.create_agent_instances()
        now_str = datetime.now().isoformat()

        # Initialize tracking state
        self._active_runs[request_id] = {
            "request_id": request_id,
            "farmer_input": farmer_input,
            "agents": agents,
            "status": "RUNNING",
            "stage": "Intake Validation",
            "risk_level": "LOW",
            "created_at": now_str
        }

        # Initialize record in SQLite
        save_advisory(
            request_id=request_id,
            farmer_name=farmer_input.farmer_name,
            crop_name=farmer_input.crop_name,
            location=farmer_input.location,
            crop_stage=farmer_input.crop_stage,
            land_area=farmer_input.land_area,
            irrigation_type=farmer_input.irrigation_type,
            risk_level="LOW",
            status="RUNNING"
        )

        # Launch the workflow as an asynchronous task
        asyncio.create_task(self._execute_pipeline(request_id))
        return request_id

    async def _execute_pipeline(self, request_id: str):
        run_data = self._active_runs.get(request_id)
        if not run_data:
            return
            
        agents = run_data["agents"]
        farmer_input = run_data["farmer_input"]
        bb = self.blackboard

        try:
            # -------------------------------------------------------------
            # STEP 1: Intake Agent (Validates and publishes farmer info)
            # -------------------------------------------------------------
            run_data["stage"] = "Stage 1: Farmer Data Ingestion"
            intake_agent: IntakeAgent = agents["intake_agent"]
            intake_agent.set_input(farmer_input)
            await intake_agent.execute(request_id, bb)
            await asyncio.sleep(0.4) # Smooth visual streaming

            # -------------------------------------------------------------
            # STEP 2: Concurrent Execution: Weather, Market, Scheme (RAG)
            # -------------------------------------------------------------
            run_data["stage"] = "Stage 2: Concurrent Multi-Source Retrieval"
            weather_agent: WeatherAgent = agents["weather_agent"]
            market_agent: MarketAgent = agents["market_agent"]
            scheme_agent: SchemeAgent = agents["scheme_agent"]

            await asyncio.gather(
                weather_agent.execute(request_id, bb),
                market_agent.execute(request_id, bb),
                scheme_agent.execute(request_id, bb)
            )
            await asyncio.sleep(0.4)

            # -------------------------------------------------------------
            # STEP 3: Concurrent Execution: Crop Agronomics & Risk Alert
            # -------------------------------------------------------------
            run_data["stage"] = "Stage 3: Agronomic Analysis & Risk Assessment"
            crop_agent: CropAgent = agents["crop_agent"]
            risk_alert_agent: RiskAlertAgent = agents["risk_alert_agent"]

            crop_res, risk_res = await asyncio.gather(
                crop_agent.execute(request_id, bb),
                risk_alert_agent.execute(request_id, bb)
            )
            
            risk_level = risk_res.get("risk_level", "LOW")
            run_data["risk_level"] = risk_level
            update_advisory_status(request_id, status="ANALYZING", risk_level=risk_level)
            await asyncio.sleep(0.4)

            # -------------------------------------------------------------
            # STEP 4: Advisor Coordinator (Reconciliation & Synthesis)
            # -------------------------------------------------------------
            run_data["stage"] = "Stage 4: Unified Advisory Synthesis"
            coordinator: AdvisorCoordinator = agents["advisor_coordinator"]
            final_advisory = await coordinator.execute(request_id, bb)

            # -------------------------------------------------------------
            # STEP 5: Finalize and Persist
            # -------------------------------------------------------------
            run_data["status"] = "COMPLETED"
            run_data["stage"] = "Completed"
            update_advisory_status(
                request_id=request_id,
                status="COMPLETED",
                risk_level=risk_level,
                final_advisory=final_advisory
            )
            logger.info(f"Pipeline finished successfully for request [{request_id}]")

        except Exception as e:
            logger.error(f"Pipeline error for request [{request_id}]: {e}", exc_info=True)
            run_data["status"] = "FAILED"
            run_data["stage"] = f"Failed: {str(e)}"
            update_advisory_status(request_id=request_id, status="FAILED")
