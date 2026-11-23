import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db, get_all_advisories_db, save_advisory, save_blackboard_entry
from app.api.advisory_routes import router as advisory_router
from app.api.agent_routes import router as agent_router
from app.api.board_routes import router as board_router
from app.api.history_routes import router as history_router
from app.api.scheme_routes import router as scheme_router
from app.rag.retriever import SchemeRAGRetriever

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ControlRoom")

def seed_sample_data_if_empty():
    existing = get_all_advisories_db(limit=5)
    if not existing:
        logger.info("Database is empty. Seeding initial baseline scenario for demonstration...")
        demo_id = "demo-wheat-ludhiana-01"
        sample_advisory = {
            "weather_overview": {
                "location": "Ludhiana, Punjab",
                "temperature": 23.5,
                "humidity": 65,
                "condition": "Partly Cloudy",
                "wind_speed_kmh": 14.2,
                "max_rain_prob_next_5_days": 40,
                "total_expected_rain_mm": 12.5,
                "data_source": "Open-Meteo Weather API",
                "forecast": [
                    {"date": "Day 1", "max_temp": 26, "min_temp": 14, "precip_prob": 10, "precip_sum_mm": 0, "wind_max_kmh": 12, "condition": "Sunny"},
                    {"date": "Day 2", "max_temp": 27, "min_temp": 15, "precip_prob": 20, "precip_sum_mm": 1.0, "wind_max_kmh": 15, "condition": "Partly Cloudy"},
                    {"date": "Day 3", "max_temp": 25, "min_temp": 14, "precip_prob": 40, "precip_sum_mm": 11.5, "wind_max_kmh": 24, "condition": "Rain Showers"}
                ]
            },
            "risk_alert": {
                "risk_level": "MEDIUM",
                "risk_score": 35,
                "badge_color": "amber",
                "is_prominent_warning": False,
                "warning": "MODERATE RISK: Weather conditions warrant watchful field management.",
                "threats": ["Moderate rain showers predicted (40% probability, ~12.5mm rain)."],
                "preventive_action": "Postpone urea top-dressing and inspect field drainage outlets."
            },
            "field_actions": {
                "irrigation_action": "HOLD IRRIGATION: Moderate rain forecasted within 48-72 hours. Delay tubewell watering to prevent water stagnation in flowering wheat.",
                "irrigation_status": "HOLD",
                "fertilizer_action": "Foliar spray of 2% Potassium Nitrate (13:0:45) at flowering stage improves grain filling and prevents terminal heat stress.",
                "crop_protection": "Inspect flag leaves for signs of Yellow Rust (Puccinia striiformis). If orange pustules appear, spray Propiconazole 25% EC @ 1ml/litre.",
                "primary_focus": "Grain weight development and canopy temperature protection"
            },
            "mandi_analysis": {
                "mandi_name": "Ludhiana APMC Grain Market (Punjab)",
                "modal_price": 2420,
                "min_price": 2350,
                "max_price": 2480,
                "msp": 2275,
                "trend_percentage": 2.5,
                "trend_direction": "UPWARD",
                "arrivals_tonnes": 480,
                "data_source": "AGMARKNET – Directorate of Marketing & Inspection",
                "date": "2024-11-17",
                "price_history": [
                    {"date": "11 Nov", "price": 2360, "arrivals_tonnes": 410},
                    {"date": "12 Nov", "price": 2375, "arrivals_tonnes": 430},
                    {"date": "13 Nov", "price": 2390, "arrivals_tonnes": 450},
                    {"date": "14 Nov", "price": 2400, "arrivals_tonnes": 460},
                    {"date": "15 Nov", "price": 2415, "arrivals_tonnes": 470},
                    {"date": "16 Nov", "price": 2420, "arrivals_tonnes": 480}
                ]
            },
            "market_recommendation": {
                "action": "MONITOR",
                "reasoning": "Current modal price (Rs. 2420/qtl) is 6.3% above MSP (Rs. 2275). Market arrivals are steady. Maintain watchful stance."
            },
            "recommended_scheme": {
                "title": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
                "scheme_id": "PMFBY",
                "benefits": "Maximum 1.5% premium for Rabi Wheat; comprehensive yield loss coverage up to sum insured.",
                "source": "Ministry of Agriculture & Farmers Welfare, Govt of India",
                "portal": "https://pmfby.gov.in",
                "application_process": "Register on the PMFBY portal or via local cooperative bank before seasonal cut-off."
            },
            "eligibility_conditions": [
                "Provisional match: Farmer must hold updated state revenue land records (Jamabandi/Khatauni).",
                "Mandatory Aadhaar-seeded active bank account for Direct Benefit Transfer (DBT).",
                "Subject to physical or biometric authentication by District Agriculture Office."
            ],
            "next_steps": [
                "1. Field Management: POSTPONE IRRIGATION: Forecast indicates rain within 48 hours.",
                "2. Plant Protection: Inspect flag leaves for yellow rust; prepare 13:0:45 foliar spray.",
                "3. Market Strategy: MONITOR APMC rates; liquidate in tranches as prices remain above MSP.",
                "4. Scheme Verification: Check enrollment status on https://pmfby.gov.in."
            ],
            "summary_farmer_language": "Namaste Kisan Bhai. For your flowering Wheat in Ludhiana, hold off on tubewell irrigation as light to moderate rain is expected soon. Spray potassium nitrate to keep grains healthy. Mandi prices are firm at Rs. 2,420/quintal (well above MSP); we suggest monitoring prices and selling in batches.",
            "generated_at": "2024-11-17T10:30:00",
            "model_used": "Groq Llama / Multi-Agent Control Room"
        }
        
        save_advisory(
            request_id=demo_id,
            farmer_name="Sardar Gurpreet Singh",
            crop_name="Wheat",
            location="Ludhiana, Punjab",
            crop_stage="Flowering",
            land_area=8.5,
            irrigation_type="Tubewell",
            risk_level="MEDIUM",
            status="COMPLETED",
            final_advisory=sample_advisory
        )
        
        save_blackboard_entry(demo_id, "intake_agent", "intake", {"farmer_name": "Sardar Gurpreet Singh", "crop_name": "Wheat", "location": "Ludhiana, Punjab", "crop_stage": "Flowering"})
        save_blackboard_entry(demo_id, "weather_agent", "weather", sample_advisory["weather_overview"])
        save_blackboard_entry(demo_id, "crop_agent", "crop", sample_advisory["field_actions"])
        save_blackboard_entry(demo_id, "market_agent", "market", sample_advisory["mandi_analysis"])
        save_blackboard_entry(demo_id, "scheme_agent", "scheme", sample_advisory["recommended_scheme"])
        save_blackboard_entry(demo_id, "risk_alert_agent", "risk_alert", sample_advisory["risk_alert"])
        save_blackboard_entry(demo_id, "advisor_coordinator", "advisory", sample_advisory)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database & RAG Vector Store
    logger.info("Initializing SQLite database tables...")
    init_db()
    logger.info("Initializing RAG vector knowledge base...")
    retriever = SchemeRAGRetriever.get_instance()
    retriever.initialize()
    seed_sample_data_if_empty()
    logger.info("Agricultural Advisory Control Room backend initialized successfully!")
    yield
    # Shutdown
    logger.info("Agricultural Advisory Control Room shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-Grade Multi-Agent AI System with Shared Blackboard & RAG",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS Middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(advisory_router)
app.include_router(agent_router)
app.include_router(board_router)
app.include_router(history_router)
app.include_router(scheme_router)

@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "group": settings.PROJECT_GROUP,
        "version": settings.VERSION,
        "groq_configured": bool(settings.GROQ_API_KEY),
        "groq_model": settings.GROQ_MODEL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
