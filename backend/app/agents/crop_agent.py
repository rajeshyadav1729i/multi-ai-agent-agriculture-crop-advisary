from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.orchestration.blackboard import Blackboard

class CropAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="crop_agent",
            display_name="Crop Agent",
            icon="Sprout",
            responsibility="Analyze crop stage, physiological water requirements, and prescribe targeted agronomic practices"
        )

    async def process(self, request_id: str, blackboard: Blackboard) -> Dict[str, Any]:
        intake_data = blackboard.get_agent_output(request_id, "intake_agent") or {}
        weather_data = blackboard.get_agent_output(request_id, "weather_agent") or {}

        crop = intake_data.get("crop_name", "Wheat").title()
        stage = intake_data.get("crop_stage", "Flowering").title()
        irrigation_type = intake_data.get("irrigation_type", "Canal / Tubewell")

        max_rain_prob = weather_data.get("max_rain_prob_next_5_days", 0)
        temp = weather_data.get("temperature", 24)
        wind_speed = weather_data.get("wind_speed_kmh", 12)

        # 1. Irrigation Recommendation
        if max_rain_prob >= 50:
            irrigation_action = (
                f"POSTPONE IRRIGATION: Forecast shows {max_rain_prob}% rain probability. "
                "Delay planned irrigation by 3-4 days to prevent water stagnation and root suffocation. "
                "Ensure drainage channels are cleared."
            )
            irrigation_status = "HOLD"
        elif wind_speed > 25:
            irrigation_action = (
                f"AVOID IRRIGATION DURING HIGH WINDS ({wind_speed} km/h): "
                f"Applying heavy irrigation in {stage} stage under strong winds causes crop lodging (toppling), "
                "drastically lowering yield. Wait for wind to subside."
            )
            irrigation_status = "CAUTION"
        else:
            if stage in ["Flowering", "Heading"]:
                irrigation_action = (
                    f"CRITICAL IRRIGATION REQUIRED: {crop} at {stage} stage has peak evapotranspiration demand. "
                    f"Apply a light irrigation using {irrigation_type} during calm evening hours."
                )
                irrigation_status = "RECOMMENDED"
            elif stage in ["Maturity", "Harvesting"]:
                irrigation_action = (
                    "WITHHOLD IRRIGATION: Crop is approaching physiological maturity. "
                    "Cease irrigation to facilitate grain hardening and timely combine harvesting."
                )
                irrigation_status = "STOP"
            else:
                irrigation_action = (
                    f"STANDARD IRRIGATION: Maintain adequate root zone moisture based on soil appearance. "
                    f"Irrigate every 10-14 days through {irrigation_type}."
                )
                irrigation_status = "MAINTAIN"

        # 2. Stage-Specific Agronomic & Fertilizer Advisory
        crop_lower = crop.lower()
        if "wheat" in crop_lower:
            if "flower" in stage.lower() or "head" in stage.lower():
                fertilizer_action = "Foliar spray of 2% Potassium Nitrate (13:0:45) at flowering stage improves grain filling and prevents terminal heat stress."
                crop_protection = "Inspect flag leaves for signs of Yellow Rust (Puccinia striiformis). If orange pustules appear, spray Propiconazole 25% EC @ 1ml/litre."
                primary_focus = "Grain weight development and canopy temperature protection"
            elif "sow" in stage.lower():
                fertilizer_action = "Apply 55 kg DAP + 20 kg MOP + 10 kg Zinc Sulphate (21%) per acre as basal dose at time of drilling."
                crop_protection = "Seed treatment with Trichoderma viride @ 4g/kg seed or Carbendazim @ 2g/kg seed."
                primary_focus = "Uniform seedling emergence and root establishment"
            elif "veg" in stage.lower():
                fertilizer_action = "First top-dressing of Urea (45 kg/acre) before 1st irrigation (CRI stage, 21 days after sowing)."
                crop_protection = "Manage broadleaf and grassy weeds using Clodinafop + Metsulfuron methyl within 30-35 DAS."
                primary_focus = "Crown root initiation and maximum tillering"
            else:
                fertilizer_action = "No chemical fertilizer application required at maturity stage."
                crop_protection = "Monitor for storage pests; clean gunny bags and sun-dry harvesting threshers."
                primary_focus = "Grain desiccation and moisture reduction"
        elif "rice" in crop_lower or "paddy" in crop_lower:
            fertilizer_action = f"Apply balanced Nitrogen split. At {stage} stage, avoid excess urea that invites sheath blight."
            crop_protection = "Monitor for stem borer and Brown Planthopper (BPH) at base of tillers."
            primary_focus = "Panicle initiation and water table management"
        elif "cotton" in crop_lower:
            fertilizer_action = "Spray 1% Magnesium Sulphate + 1% 19:19:19 to prevent leaf reddening."
            crop_protection = "Install yellow sticky traps and pheromone traps for pink bollworm surveillance."
            primary_focus = "Square formation and boll retention"
        else:
            fertilizer_action = f"Apply recommended NPK split doses suitable for {crop} at {stage} stage."
            crop_protection = "Regular field scouting for sucking pests and fungal blights."
            primary_focus = f"Optimal physiological development for {stage} stage"

        return {
            "crop": crop,
            "crop_stage": stage,
            "irrigation_action": irrigation_action,
            "irrigation_status": irrigation_status,
            "fertilizer_action": fertilizer_action,
            "crop_protection": crop_protection,
            "primary_focus": primary_focus,
            "stage_guidance": f"{crop} is currently in its {stage} growth stage, requiring targeted moisture and nutrient oversight."
        }
