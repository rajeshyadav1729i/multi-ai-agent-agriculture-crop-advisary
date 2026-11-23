from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.orchestration.blackboard import Blackboard
from app.models.advisory import FarmerInput

class IntakeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="intake_agent",
            display_name="Intake Agent",
            icon="UserCheck",
            responsibility="Ingest and validate farmer crop profile, growth stage, and geographic coordinates"
        )
        self.farmer_input_data: Dict[str, Any] = {}

    def set_input(self, farmer_input: FarmerInput):
        self.farmer_input_data = farmer_input.model_dump()

    async def process(self, request_id: str, blackboard: Blackboard) -> Dict[str, Any]:
        # Validate critical fields
        crop_name = self.farmer_input_data.get("crop_name", "").strip()
        location = self.farmer_input_data.get("location", "").strip()
        crop_stage = self.farmer_input_data.get("crop_stage", "").strip()
        farmer_name = self.farmer_input_data.get("farmer_name") or "Farmer"
        land_area = self.farmer_input_data.get("land_area")
        irrigation_type = self.farmer_input_data.get("irrigation_type", "Canal / Tubewell")

        if not crop_name:
            raise ValueError("Crop name is required for advisory processing.")
        if not location:
            raise ValueError("Location is required for weather and mandi lookups.")
        if not crop_stage:
            crop_stage = "Vegetative"

        payload = {
            "farmer_name": farmer_name,
            "crop_name": crop_name.title(),
            "location": location.title(),
            "crop_stage": crop_stage.title(),
            "land_area_acres": land_area,
            "irrigation_type": irrigation_type,
            "validation_status": "VALIDATED",
            "message": f"Farmer profile accepted for {crop_name.title()} at {location.title()} ({crop_stage.title()} stage)."
        }
        return payload
