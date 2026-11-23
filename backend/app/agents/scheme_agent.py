import re
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.orchestration.blackboard import Blackboard
from app.rag.retriever import SchemeRAGRetriever

class SchemeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="scheme_agent",
            display_name="Scheme Agent (RAG)",
            icon="FileBadge",
            responsibility="Execute RAG vector retrieval over official government scheme knowledge base for subsidies and crop insurance"
        )
        self.retriever = SchemeRAGRetriever.get_instance()

    async def process(self, request_id: str, blackboard: Blackboard) -> Dict[str, Any]:
        intake_data = blackboard.get_agent_output(request_id, "intake_agent") or {}
        weather_data = blackboard.get_agent_output(request_id, "weather_agent") or {}

        crop = intake_data.get("crop_name", "Wheat")
        location = intake_data.get("location", "Ludhiana, Punjab")
        stage = intake_data.get("crop_stage", "Flowering")
        irrigation = intake_data.get("irrigation_type", "Canal / Tubewell")
        has_weather_risk = weather_data.get("has_threats", False)

        # Formulate contextual search query for RAG
        keywords = [crop, location, stage]
        if has_weather_risk:
            keywords.append("crop insurance calamity risk damage claim")
        if "drip" in irrigation.lower() or "sprinkler" in irrigation.lower():
            keywords.append("micro irrigation subsidy")
        if "punjab" in location.lower():
            keywords.append("punjab seed diversification machinery")

        search_query = " ".join(keywords) + " eligibility benefit application guidelines"
        retrieved_chunks = self.retriever.retrieve(search_query, top_k=3)

        if not retrieved_chunks:
            # Fallback to general PMFBY / PM-KISAN
            retrieved_chunks = self.retriever.retrieve("PM-KISAN PMFBY crop insurance benefits", top_k=2)

        best_chunk = retrieved_chunks[0] if retrieved_chunks else {}
        
        # Extract structured fields from content
        content_text = best_chunk.get("content", "")
        
        # Extract benefits
        benefit_match = re.search(r"(?:FINANCIAL BENEFITS|BENEFITS|PREMIUM RATES & FINANCIAL BENEFITS|INCENTIVES)[:\n]+([^\n]+(?:\n[^\n]+){1,3})", content_text, re.IGNORECASE)
        benefits_summary = benefit_match.group(1).strip() if benefit_match else "Financial assistance and risk protection provided under guidelines."

        # Extract eligibility conditions
        eligibility_match = re.search(r"(?:ELIGIBILITY CRITERIA|ELIGIBILITY)[:\n]+([^\n]+(?:\n[^\n]+){1,4})", content_text, re.IGNORECASE)
        eligibility_summary = eligibility_match.group(1).strip() if eligibility_match else "All landholding farmers with validated revenue land records."

        # Application process
        app_match = re.search(r"(?:APPLICATION & VERIFICATION PROCESS|APPLICATION PROCESS|HOW TO OBTAIN)[:\n]+([^\n]+(?:\n[^\n]+){1,3})", content_text, re.IGNORECASE)
        app_process = app_match.group(1).strip() if app_match else "Apply online via the official scheme portal or nearest Common Service Centre (CSC)."

        return {
            "selected_scheme": best_chunk.get("title", "Pradhan Mantri Fasal Bima Yojana (PMFBY)"),
            "scheme_id": best_chunk.get("scheme_id", "PMFBY"),
            "relevance_score": best_chunk.get("relevance_score", 0.95),
            "official_portal": best_chunk.get("portal", "https://pmfby.gov.in"),
            "source_authority": best_chunk.get("source", "Ministry of Agriculture & Farmers Welfare, Govt of India"),
            "benefits": benefits_summary,
            "eligibility_conditions": [
                "Provisional match: Farmer must hold updated state revenue land records (Jamabandi/Khatauni).",
                "Mandatory Aadhaar-seeded active bank account for Direct Benefit Transfer (DBT).",
                "Final approval rests with District Agriculture Officer upon physical/e-KYC verification."
            ],
            "application_process": app_process,
            "provisional_disclaimer": "NOTE: System indicates potential scheme eligibility based on stated crop and district profile. Official enrollment requires documentary verification.",
            "retrieved_evidence_chunks": [
                {
                    "title": c.get("title"),
                    "section": c.get("section"),
                    "score": c.get("relevance_score"),
                    "snippet": c.get("content", "")[:280] + "..."
                }
                for c in retrieved_chunks
            ]
        }
