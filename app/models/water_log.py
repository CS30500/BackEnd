from pydantic import BaseModel, Field
from datetime import datetime


class WaterLog(BaseModel):
    user_id: str
    amount_ml: float = Field(..., gt=0, description="마신 물 양 (ml)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    date: str

class DailyTarget(BaseModel):
    user_id: str
    target_ml: float = Field(..., gt=0, description="하루 목표 섭취량 (ml)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    date: str

class HydrationSummary(BaseModel):
    date: str
    total_intake_ml: float
    target_ml: float
