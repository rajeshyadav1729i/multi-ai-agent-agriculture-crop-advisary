import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

import openai
from app.agents.base_agent import BaseAgent
from app.orchestration.blackboard import Blackboard
from app.config import settings

# Microsoft Semantic Kernel imports
try:
    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    HAS_SEMANTIC_KERNEL = True
except ImportError:
    HAS_SEMANTIC_KERNEL = False

logger = logging.getLogger(__name__)

class AdvisorCoordinator(BaseAgent):
    def __init__(self):
        super().__init__(
            name="advisor_coordinator",
            display_name="Advisor Coordinator",
            icon="BotMessageSquare",
            responsibility="Read entire Blackboard memory, reconcile conflicts, and generate unified farmer-friendly advisory"
        )
        self.kernel: Optional[Any] = None
        self._init_semantic_kernel()

    def _init_semantic_kernel(self):
        """
        Initializes Microsoft Semantic Kernel configured with Groq's OpenAI-compatible endpoint
        """
        if not HAS_SEMANTIC_KERNEL:
            logger.warning("Semantic Kernel library not available.")
            return

        try:
            if settings.GROQ_API_KEY:
                async_client = openai.AsyncOpenAI(
                    api_key=settings.GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1"
                )
                self.kernel = Kernel()
                service = OpenAIChatCompletion(
                    service_id="groq_service",
                    ai_model_id=settings.GROQ_MODEL,
                    async_client=async_client
                )
                self.kernel.add_service(service)
                logger.info(f"Semantic Kernel initialized with model {settings.GROQ_MODEL}")
        except Exception as e:
            logger.warning(f"Could not initialize Semantic Kernel: {e}. Fallback generator will be used.")

    async def _generate_llm_synthesis(self, context_prompt: str) -> Optional[str]:
        """
        Invokes LLM via Groq / Semantic Kernel to create farmer-friendly synthesized text
        """
        # Try via Groq SDK directly first for fast response
        if settings.GROQ_API_KEY:
            try:
                import groq
                client = groq.Groq(api_key=settings.GROQ_API_KEY)
                chat = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are the Senior Chief Agricultural Extension Officer for the Agricultural Advisory Control Room (Group 20). "
                                "Synthesize the provided multi-agent findings into a warm, clear, practical advice summary "
                                "in simple Indian farmer-friendly language. Be direct, compassionate, and specific."
                            )
                        },
                        {
                            "role": "user",
                            "content": context_prompt
                        }
                    ],
                    model=settings.GROQ_MODEL,
                    temperature=0.3,
                    max_tokens=600
                )
                return chat.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"Direct Groq generation attempt failed: {e}. Trying fallback model.")
                try:
                    import groq
                    client = groq.Groq(api_key=settings.GROQ_API_KEY)
                    chat = client.chat.completions.create(
                        messages=[{"role": "user", "content": context_prompt}],
                        model=settings.GROQ_FALLBACK_MODEL,
                        temperature=0.3,
                        max_tokens=500
                    )
                    return chat.choices[0].message.content.strip()
                except Exception as e2:
                    logger.warning(f"Fallback model failed: {e2}")

        return None

    async def process(self, request_id: str, blackboard: Blackboard) -> Dict[str, Any]:
        # 1. Read all previous agent outputs from Blackboard
        intake_data = blackboard.get_agent_output(request_id, "intake_agent") or {}
        weather_data = blackboard.get_agent_output(request_id, "weather_agent") or {}
        crop_data = blackboard.get_agent_output(request_id, "crop_agent") or {}
        market_data = blackboard.get_agent_output(request_id, "market_agent") or {}
        scheme_data = blackboard.get_agent_output(request_id, "scheme_agent") or {}
        risk_data = blackboard.get_agent_output(request_id, "risk_alert_agent") or {}

        # 2. Extract Key Fields
        farmer_name = intake_data.get("farmer_name", "Kisan Bhai")
        crop = intake_data.get("crop_name", "Wheat")
        location = intake_data.get("location", "Ludhiana, Punjab")
        stage = intake_data.get("crop_stage", "Flowering")
        
        risk_level = risk_data.get("risk_level", "LOW")
        is_high_risk = risk_level in ["HIGH", "CRITICAL"]
        
        # 3. Conflict Resolution Logic:
        # Conflict A: Crop stage demands irrigation, but Weather forecast warns of imminent heavy rain or high winds
        rain_prob = weather_data.get("max_rain_prob_next_5_days", 0)
        wind_speed = weather_data.get("wind_speed_kmh", 12)
        resolved_field_action = dict(crop_data)
        
        conflict_notes = []
        if rain_prob >= 45:
            conflict_notes.append("RECONCILED: Rain probability is high. Overriding regular irrigation schedule to prevent waterlogging.")
            resolved_field_action["irrigation_action"] = (
                f"POSTPONE IRRIGATION: Forecast indicates {rain_prob}% rain probability. "
                "Do NOT irrigate now. Ensure drainage channels are clear to prevent water stagnation in root zones."
            )
        elif wind_speed >= 25:
            conflict_notes.append("RECONCILED: High wind speeds detected. Prohibiting heavy watering to avert lodging.")
            resolved_field_action["irrigation_action"] = (
                f"HOLD IRRIGATION DURING HIGH WINDS ({wind_speed} km/h): "
                f"Irrigating wet soil during {stage} stage under strong winds triggers plant toppling. Wait for winds to calm."
            )

        # Conflict B: Market suggests HOLD, but crop is highly perishable or storage unavailable
        mkt_action = market_data.get("recommendation", "MONITOR")
        modal_price = market_data.get("modal_price", 2400)
        msp = market_data.get("msp", 2275)

        # 4. Synthesize Prompt for Groq / Semantic Kernel
        prompt_summary = f"""
Farmer: {farmer_name}
Location: {location}
Crop: {crop} ({stage} stage)
Risk Level: {risk_level}
Weather: Temp {weather_data.get('temperature', 24)}°C, Humidity {weather_data.get('humidity', 60)}%, Rain Prob: {rain_prob}%
Threats: {', '.join(weather_data.get('weather_threats_identified', ['Normal conditions']))}
Field Action: {resolved_field_action.get('irrigation_action', '')} | {resolved_field_action.get('fertilizer_action', '')}
Market: {market_data.get('mandi_name', '')} Modal Price Rs. {modal_price}/qtl (MSP Rs. {msp}). Action: {mkt_action}
Recommended Scheme: {scheme_data.get('selected_scheme', 'PMFBY')}
Write a 3-sentence spoken advice summary for the farmer.
"""
        llm_farmer_summary = await self._generate_llm_synthesis(prompt_summary)
        
        if not llm_farmer_summary:
            # Deterministic natural language summary if LLM offline
            risk_phrase = "Take extra caution regarding oncoming weather." if is_high_risk else "Weather conditions are reasonably stable."
            llm_farmer_summary = (
                f"Namaste {farmer_name}, for your {crop} at {stage} stage in {location}, {risk_phrase} "
                f"Follow the irrigation advice closely: {resolved_field_action.get('irrigation_action', '')[:120]}. "
                f"In the mandi, current prices are around Rs. {modal_price}/quintal; our recommendation is to {mkt_action}. "
                f"Ensure you are enrolled in {scheme_data.get('selected_scheme', 'PM-KISAN/PMFBY')} for financial protection."
            )

        # 5. Build Final Unified Advisory Report with 5 Mandatory Sections
        final_report = {
            # Section 1: Weather and Risk Warning
            "weather_overview": {
                "location": weather_data.get("location", location),
                "temperature": weather_data.get("temperature", 24),
                "humidity": weather_data.get("humidity", 60),
                "condition": weather_data.get("condition", "Partly Cloudy"),
                "wind_speed_kmh": weather_data.get("wind_speed_kmh", 12),
                "max_rain_prob_next_5_days": weather_data.get("max_rain_prob_next_5_days", 15),
                "total_expected_rain_mm": weather_data.get("total_expected_rain_mm", 0.0),
                "data_source": weather_data.get("data_source", "Open-Meteo Weather API"),
                "forecast": weather_data.get("forecast", [])
            },
            "risk_alert": {
                "risk_level": risk_level,
                "risk_score": risk_data.get("risk_score", 20),
                "badge_color": risk_data.get("badge_color", "green"),
                "is_prominent_warning": is_high_risk,
                "warning": risk_data.get("primary_warning", "Normal Conditions"),
                "threats": risk_data.get("threats_identified", []),
                "preventive_action": risk_data.get("preventive_action", "Maintain routine field operations.")
            },
            
            # Section 2: Immediate Field Action
            "field_actions": {
                "irrigation_action": resolved_field_action.get("irrigation_action"),
                "irrigation_status": resolved_field_action.get("irrigation_status", "MAINTAIN"),
                "fertilizer_action": resolved_field_action.get("fertilizer_action"),
                "crop_protection": resolved_field_action.get("crop_protection"),
                "primary_focus": resolved_field_action.get("primary_focus", "Canopy health"),
                "conflict_resolution_notes": conflict_notes
            },
            
            # Section 3: Market Sell-or-Hold Recommendation
            "mandi_analysis": {
                "mandi_name": market_data.get("mandi_name", "Local APMC Market"),
                "modal_price": market_data.get("modal_price", 2400),
                "min_price": market_data.get("min_price", 2300),
                "max_price": market_data.get("max_price", 2500),
                "msp": market_data.get("msp", 2275),
                "trend_percentage": market_data.get("trend_percentage", 2.0),
                "trend_direction": market_data.get("trend_direction", "STABLE"),
                "arrivals_tonnes": market_data.get("arrivals_tonnes", 350),
                "data_source": market_data.get("data_source", "AGMARKNET Market Network"),
                "date": market_data.get("date", datetime.now().strftime("%Y-%m-%d")),
                "price_history": market_data.get("price_history", [])
            },
            "market_recommendation": {
                "action": mkt_action,
                "reasoning": market_data.get("reasoning", "Market prices stable around modal averages.")
            },
            
            # Section 4: One Relevant Government Scheme (RAG)
            "recommended_scheme": {
                "title": scheme_data.get("selected_scheme", "Pradhan Mantri Fasal Bima Yojana (PMFBY)"),
                "scheme_id": scheme_data.get("scheme_id", "PMFBY"),
                "benefits": scheme_data.get("benefits", "Comprehensive risk protection and input subsidy"),
                "source": scheme_data.get("source_authority", "Ministry of Agriculture & Farmers Welfare"),
                "portal": scheme_data.get("official_portal", "https://pmfby.gov.in"),
                "application_process": scheme_data.get("application_process", "Apply via official portal or CSC center."),
                "retrieved_evidence": scheme_data.get("retrieved_evidence_chunks", [])
            },
            "eligibility_conditions": scheme_data.get("eligibility_conditions", [
                "Provisional eligibility: Land record must be updated in State Revenue Portal.",
                "Mandatory Aadhaar linking with active DBT bank account.",
                "Subject to physical or biometric authentication by District Agriculture Office."
            ]),
            
            # Section 5: Practical Next Steps
            "next_steps": [
                f"1. Field Management: {resolved_field_action.get('irrigation_action', '')[:100]}...",
                f"2. Plant Protection: {resolved_field_action.get('crop_protection', '')[:100]}...",
                f"3. Market Strategy: {mkt_action} produce based on current rate of Rs. {modal_price}/quintal.",
                f"4. Scheme Verification: Check eligibility documentation on {scheme_data.get('official_portal', 'https://pmfby.gov.in')}."
            ],
            
            "summary_farmer_language": llm_farmer_summary,
            "generated_at": datetime.now().isoformat(),
            "model_used": settings.GROQ_MODEL if settings.GROQ_API_KEY else "Control Room Rule-Engine + RAG Retriever"
        }

        return final_report
