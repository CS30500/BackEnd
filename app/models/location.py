from pydantic import BaseModel, Field
from datetime import datetime

class UserLocation(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class LocationTemperature(BaseModel):
    latitude: float
    longitude: float
    temperature_c: float
    source: str = Field(..., description="기온 정보 출처 (예: openweather)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)