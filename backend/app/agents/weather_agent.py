from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.orchestration.blackboard import Blackboard
from app.services.weather_service import WeatherService

class WeatherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="weather_agent",
            display_name="Weather Agent",
            icon="CloudSun",
            responsibility="Query live meteorological data, analyze rainfall probability, temperature, and wind extremes"
        )

    async def process(self, request_id: str, blackboard: Blackboard) -> Dict[str, Any]:
        intake_data = blackboard.get_agent_output(request_id, "intake_agent")
        if not intake_data:
            raise ValueError("Weather Agent requires Intake Agent data from Blackboard.")

        location = intake_data.get("location", "Ludhiana, Punjab")
        weather_raw = await WeatherService.fetch_weather_forecast(location)

        # Identify upcoming weather threats
        threats = []
        max_rain_prob = weather_raw.get("max_rain_prob_next_5_days", 0)
        total_rain = weather_raw.get("total_expected_rain_mm", 0.0)
        temp = weather_raw.get("temperature", 25)
        wind = weather_raw.get("wind_speed_kmh", 10)

        if max_rain_prob >= 60:
            threats.append(f"High probability of precipitation ({max_rain_prob}%) with estimated {total_rain}mm rain.")
        elif max_rain_prob >= 35:
            threats.append(f"Moderate chance of rain showers ({max_rain_prob}%).")

        if temp >= 38:
            threats.append(f"Extreme heat stress conditions ({temp}°C).")
        elif temp <= 5:
            threats.append(f"Frost/low temperature hazard ({temp}°C).")

        if wind >= 28:
            threats.append(f"High wind gust warning ({wind} km/h) - lodging risk for standing crops.")

        weather_findings = {
            **weather_raw,
            "weather_threats_identified": threats,
            "has_threats": len(threats) > 0,
            "summary": f"Location: {weather_raw['location']} | Temp: {temp}°C, Humidity: {weather_raw['humidity']}%, Condition: {weather_raw['condition']}."
        }
        return weather_findings
