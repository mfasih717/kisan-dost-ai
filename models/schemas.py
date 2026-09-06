from pydantic import BaseModel
from typing import List, Optional


class CropPlan(BaseModel):
    crop_name: str
    season: str
    expected_yield_per_acre: float
    expected_profit_per_acre: float
    reason: str  # why this crop was recommended


class CropAdvisorResponse(BaseModel):
    recommendations: List[CropPlan]
    notes: str  # e.g. water/soil considerations


class FertilizerPlan(BaseModel):
    crop_name: str
    acres: float
    urea_bags: float
    dap_bags: float
    total_cost_pkr: float


class PestDiagnosis(BaseModel):
    pest_name: str
    treatment: str
    safe_dosage: str
    confidence_note: str  # e.g. "based on described symptoms"


class MandiPrice(BaseModel):
    crop_name: str
    district: str
    price_per_maund: float
    date_recorded: str


class MandiPriceResponse(BaseModel):
    prices: List[MandiPrice]
    best_district: Optional[str] = None  # highest price district


class ProfitEstimate(BaseModel):
    crop_name: str
    acres: float
    total_input_cost_pkr: float
    expected_revenue_pkr: float
    net_margin_pkr: float
    break_even_yield_per_acre: float


class FarmerProfile(BaseModel):
    district: Optional[str] = None
    land_size_acres: Optional[float] = None
    current_crop: Optional[str] = None

class HandoffContext(BaseModel):
    note: str