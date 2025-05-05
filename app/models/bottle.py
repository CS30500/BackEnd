from pydantic import BaseModel, Field
from datetime import datetime

class BottleTemperature(BaseModel):
    temperature_c: float = Field(..., description="물병 내부 온도 (℃)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)