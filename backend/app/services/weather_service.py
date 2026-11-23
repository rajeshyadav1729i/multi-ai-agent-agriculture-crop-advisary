import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Weather code interpretations per WMO standards
WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog and depositing rime fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light",
    53: "Drizzle: Moderate",
    55: "Drizzle: Dense intensity",
    61: "Rain: Slight",
    63: "Rain: Moderate",
    65: "Rain: Heavy intensity",
    66: "Freezing Rain: Light",
    67: "Freezing Rain: Heavy",
    71: "Snow fall: Slight",
    73: "Snow fall: Moderate",
    75: "Snow fall: Heavy",
    77: "Snow grains",
    80: "Rain showers: Slight",
    81: "Rain showers: Moderate",
    82: "Rain showers: Violent",
    85: "Snow showers: Slight",
    86: "Snow showers: Heavy",
    95: "Thunderstorm: Slight or moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

class WeatherService:
    @staticmethod
    async def get_coordinates(location_name: str) -> Optional[Dict[str, Any]]:
        """
        Geocode location name using Open-Meteo Geocoding API
        """
        # Clean location query (e.g. "Ludhiana, Punjab" -> "Ludhiana")
        clean_loc = location_name.split(",")[0].strip()
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": clean_loc, "count": 1, "language": "en", "format": "json"}
        
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                res = await client.get(url, params=params)
                if res.status_code == 200:
                    data = res.json()
                    if "results" in data and len(data["results"]) > 0:
                        first = data["results"][0]
                        return {
                            "name": first.get("name"),
                            "latitude": first.get("latitude"),
                            "longitude": first.get("longitude"),
                            "country": first.get("country", "India"),
                            "admin1": first.get("admin1", ""),
                            "is_demo": False
                        }
        except Exception as e:
            logger.warning(f"Geocoding error for {location_name}: {e}")

        # Verified fallback coordinates for major agricultural hubs
        known_locations = {
            "ludhiana": {"latitude": 30.9010, "longitude": 75.8573, "admin1": "Punjab"},
            "punjab": {"latitude": 31.1471, "longitude": 75.3412, "admin1": "Punjab"},
            "karnal": {"latitude": 29.6857, "longitude": 76.9905, "admin1": "Haryana"},
            "indore": {"latitude": 22.7196, "longitude": 75.8577, "admin1": "Madhya Pradesh"},
            "nashik": {"latitude": 19.9975, "longitude": 73.7898, "admin1": "Maharashtra"},
            "agra": {"latitude": 27.1767, "longitude": 78.0081, "admin1": "Uttar Pradesh"},
            "patna": {"latitude": 25.5941, "longitude": 85.1376, "admin1": "Bihar"},
            "hyderabad": {"latitude": 17.3850, "longitude": 78.4867, "admin1": "Telangana"},
            "bengaluru": {"latitude": 12.9716, "longitude": 77.5946, "admin1": "Karnataka"},
            "jaipur": {"latitude": 26.9124, "longitude": 75.7873, "admin1": "Rajasthan"},
        }
        
        lower_loc = clean_loc.lower()
        for k, v in known_locations.items():
            if k in lower_loc or lower_loc in k:
                return {
                    "name": clean_loc.title(),
                    "latitude": v["latitude"],
                    "longitude": v["longitude"],
                    "country": "India",
                    "admin1": v["admin1"],
                    "is_demo": True
                }

        # Default fallback (Ludhiana, Punjab agricultural belt)
        return {
            "name": clean_loc.title(),
            "latitude": 30.9010,
            "longitude": 75.8573,
            "country": "India",
            "admin1": "Punjab",
            "is_demo": True
        }

    @staticmethod
    async def fetch_weather_forecast(location: str) -> Dict[str, Any]:
        """
        Retrieves real 7-day weather forecast from Open-Meteo
        """
        geo = await WeatherService.get_coordinates(location)
        lat = geo.get("latitude", 30.9010)
        lon = geo.get("longitude", 75.8573)
        loc_display = f"{geo.get('name', location)}, {geo.get('admin1', 'India')}"

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
            "timezone": "auto"
        }

        try:
            async with httpx.AsyncClient(timeout=7.0) as client:
                res = await client.get(url, params=params)
                if res.status_code == 200:
                    data = res.json()
                    current = data.get("current", {})
                    daily = data.get("daily", {})

                    weather_code = current.get("weather_code", 0)
                    condition_text = WMO_WEATHER_CODES.get(weather_code, "Partly Cloudy")

                    forecast_days = []
                    dates = daily.get("time", [])
                    max_temps = daily.get("temperature_2m_max", [])
                    min_temps = daily.get("temperature_2m_min", [])
                    precip_probs = daily.get("precipitation_probability_max", [])
                    precip_sums = daily.get("precipitation_sum", [])
                    wind_maxs = daily.get("wind_speed_10m_max", [])
                    codes = daily.get("weather_code", [])

                    for i in range(min(5, len(dates))):
                        d_code = codes[i] if i < len(codes) else 0
                        forecast_days.append({
                            "date": dates[i],
                            "max_temp": max_temps[i] if i < len(max_temps) else 28,
                            "min_temp": min_temps[i] if i < len(min_temps) else 14,
                            "precip_prob": precip_probs[i] if i < len(precip_probs) else 10,
                            "precip_sum_mm": precip_sums[i] if i < len(precip_sums) else 0.0,
                            "wind_max_kmh": wind_maxs[i] if i < len(wind_maxs) else 12.0,
                            "condition": WMO_WEATHER_CODES.get(d_code, "Pleasant")
                        })

                    max_rain_prob = max(precip_probs) if precip_probs else 0
                    total_expected_rain = sum(precip_sums) if precip_sums else 0.0

                    return {
                        "location": loc_display,
                        "latitude": lat,
                        "longitude": lon,
                        "temperature": current.get("temperature_2m", 24.5),
                        "humidity": current.get("relative_humidity_2m", 60),
                        "precipitation_now_mm": current.get("precipitation", 0.0),
                        "wind_speed_kmh": current.get("wind_speed_10m", 11.0),
                        "condition": condition_text,
                        "weather_code": weather_code,
                        "forecast": forecast_days,
                        "max_rain_prob_next_5_days": max_rain_prob,
                        "total_expected_rain_mm": round(total_expected_rain, 1),
                        "data_source": "Open-Meteo API (Live Satellite/NWP Forecast)",
                        "is_demo": False
                    }
        except Exception as e:
            logger.warning(f"Open-Meteo weather fetch failed: {e}. Utilizing labeled demo fallback.")

        # Fallback simulation if Open-Meteo is unreachable
        return {
            "location": loc_display,
            "latitude": lat,
            "longitude": lon,
            "temperature": 23.5,
            "humidity": 65,
            "precipitation_now_mm": 0.0,
            "wind_speed_kmh": 14.2,
            "condition": "Partly cloudy [DEMO]",
            "weather_code": 2,
            "forecast": [
                {"date": "Day 1", "max_temp": 26.5, "min_temp": 14.0, "precip_prob": 15, "precip_sum_mm": 0.0, "wind_max_kmh": 12.0, "condition": "Partly cloudy"},
                {"date": "Day 2", "max_temp": 27.0, "min_temp": 14.5, "precip_prob": 20, "precip_sum_mm": 0.2, "wind_max_kmh": 15.0, "condition": "Sunny"},
                {"date": "Day 3", "max_temp": 28.0, "min_temp": 15.0, "precip_prob": 45, "precip_sum_mm": 4.5, "wind_max_kmh": 22.0, "condition": "Scattered Showers"},
                {"date": "Day 4", "max_temp": 24.0, "min_temp": 13.0, "precip_prob": 70, "precip_sum_mm": 18.0, "wind_max_kmh": 32.0, "condition": "Moderate Rain"},
                {"date": "Day 5", "max_temp": 25.0, "min_temp": 13.5, "precip_prob": 30, "precip_sum_mm": 1.0, "wind_max_kmh": 14.0, "condition": "Clearing sky"}
            ],
            "max_rain_prob_next_5_days": 70,
            "total_expected_rain_mm": 23.7,
            "data_source": "Open-Meteo [DEMO FALLBACK DATA]",
            "is_demo": True
        }
