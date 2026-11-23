from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class FarmerInput(BaseModel):
    farmer_name: Optional[str] = Field(None, description="Farmer name (optional)")
    crop_name: str = Field(..., description="Crop name e.g. Wheat, Rice, Cotton")
    location: str = Field(..., description="District, City or State e.g. Ludhiana, Punjab")
    crop_stage: str = Field(..., description="Sowing, Vegetative, Flowering, Maturity, Harvesting")
    land_area: Optional[float] = Field(None, description="Land area in acres")
    irrigation_type: Optional[str] = Field("Canal / Tubewell", description="Canal, Tubewell, Drip, Sprinkler, Rainfed")

class AdvisoryGenerationResponse(BaseModel):
    request_id: str
    message: str
    status: str
    created_at: str

class FinalAdvisoryReport(BaseModel):
    weather_overview: Dict[str, Any]
    risk_alert: Dict[str, Any]
    field_actions: Dict[str, Any]
    mandi_analysis: Dict[str, Any]
    market_recommendation: Dict[str, Any]
    recommended_scheme: Dict[str, Any]
    eligibility_conditions: List[str]
    next_steps: List[str]
    summary_farmer_language: str
    generated_at: str
    model_used: str

class AdvisoryDetailResponse(BaseModel):
    id: str
    farmer_name: Optional[str]
    crop_name: str
    location: str
    crop_stage: str
    land_area: Optional[float]
    irrigation_type: Optional[str]
    risk_level: str
    status: str
    final_advisory: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str
