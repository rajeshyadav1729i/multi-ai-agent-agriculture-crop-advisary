from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.orchestration.blackboard import Blackboard

class RiskAlertAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="risk_alert_agent",
            display_name="Risk Alert Agent",
            icon="ShieldAlert",
            responsibility="Correlate crop vulnerability matrix with weather hazards and assign threat level (LOW/MEDIUM/HIGH/CRITICAL)"
        )

    async def process(self, request_id: str, blackboard: Blackboard) -> Dict[str, Any]:
        intake_data = blackboard.get_agent_output(request_id, "intake_agent") or {}
        weather_data = blackboard.get_agent_output(request_id, "weather_agent") or {}
        crop_data = blackboard.get_agent_output(request_id, "crop_agent") or {}

        crop = intake_data.get("crop_name", "Wheat")
        stage = intake_data.get("crop_stage", "Flowering")
        rain_prob = weather_data.get("max_rain_prob_next_5_days", 0)
        total_rain = weather_data.get("total_expected_rain_mm", 0.0)
        temp = weather_data.get("temperature", 24)
        wind_speed = weather_data.get("wind_speed_kmh", 12)

        risk_score = 10 # Baseline low risk
        threats_list = []
        preventive_actions = []

        # 1. Rain and Waterlogging Evaluation
        if rain_prob >= 70 or total_rain >= 35.0:
            risk_score += 45
            threats_list.append(f"Severe precipitation event anticipated ({rain_prob}% probability, {total_rain}mm expected).")
            preventive_actions.append("Clear field boundary trenches and unblock runoff outlets immediately to prevent water accumulation.")
        elif rain_prob >= 40 or total_rain >= 15.0:
            risk_score += 25
            threats_list.append(f"Moderate rainfall alert ({rain_prob}% probability, {total_rain}mm rain).")
            preventive_actions.append("Suspend planned chemical fertilizer applications and overhead sprinkler irrigation.")

        # 2. Wind Hazard & Crop Lodging (Sensitivity is heightened at Flowering/Maturity)
        if wind_speed >= 30:
            risk_score += 35
            threats_list.append(f"High wind velocity ({wind_speed} km/h) posing imminent crop lodging risk.")
            preventive_actions.append("Refrain strictly from irrigating soil to prevent heavy saturated soil from uprooting tall plants.")
        elif wind_speed >= 22 and stage in ["Flowering", "Heading", "Maturity"]:
            risk_score += 20
            threats_list.append(f"Moderate-to-high winds ({wind_speed} km/h) during sensitive {stage} growth stage.")
            preventive_actions.append("Postpone flood irrigation until wind speed diminishes below 15 km/h.")

        # 3. Temperature Extremes (Terminal Heat or Frost)
        if temp >= 35 and "wheat" in crop.lower() and stage in ["Flowering", "Heading"]:
            risk_score += 30
            threats_list.append(f"Terminal Heat Stress: Temperature ({temp}°C) exceeds optimum flowering threshold for {crop}.")
            preventive_actions.append("Spray 0.2% Boron or 2% Potassium Nitrate (13:0:45) in the evening to protect pollination fertility.")
        elif temp <= 4.0:
            risk_score += 30
            threats_list.append(f"Ground Frost Alert: Temperatures dipping to ({temp}°C).")
            preventive_actions.append("Provide a light irrigation in late afternoon and create localized smoke barriers on field borders.")

        # Determine Risk Level Category
        if risk_score >= 65:
            risk_level = "CRITICAL"
            badge_color = "red"
            primary_warning = "CRITICAL WEATHER RISK DETECTED: Imminent threat to crop yield."
        elif risk_score >= 40:
            risk_level = "HIGH"
            badge_color = "orange"
            primary_warning = "HIGH RISK WARNING: Action required to avert potential crop damage."
        elif risk_score >= 25:
            risk_level = "MEDIUM"
            badge_color = "amber"
            primary_warning = "MODERATE RISK: Weather conditions warrant watchful field management."
        else:
            risk_level = "LOW"
            badge_color = "green"
            primary_warning = "LOW RISK: Weather parameters are favorable for regular crop operations."

        if not threats_list:
            threats_list.append("No immediate catastrophic weather threat detected for the upcoming 5 days.")
            preventive_actions.append("Maintain standard scheduled field inspections and irrigation calendar.")

        return {
            "risk_level": risk_level,
            "risk_score": min(risk_score, 100),
            "badge_color": badge_color,
            "is_high_risk": risk_level in ["HIGH", "CRITICAL"],
            "primary_warning": primary_warning,
            "threats_identified": threats_list,
            "preventive_action": " ".join(preventive_actions),
            "crop_evaluated": f"{crop} ({stage})"
        }
