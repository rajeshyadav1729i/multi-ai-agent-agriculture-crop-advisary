from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.orchestration.blackboard import Blackboard
from app.services.market_service import MarketService

class MarketAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="market_agent",
            display_name="Market Agent",
            icon="TrendingUp",
            responsibility="Query APMC mandi trading rates, compare historical price dynamics, and compute Sell/Hold/Monitor decision"
        )

    async def process(self, request_id: str, blackboard: Blackboard) -> Dict[str, Any]:
        intake_data = blackboard.get_agent_output(request_id, "intake_agent") or {}
        crop = intake_data.get("crop_name", "Wheat")
        location = intake_data.get("location", "Ludhiana, Punjab")

        market_data = MarketService.get_market_data(crop, location)
        return market_data
