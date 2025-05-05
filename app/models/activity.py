from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ActivityLog(BaseModel):
    steps: int = Field(0, description="걸음 수")
    calories: float = Field(0, description="칼로리")
    timestamp: datetime = Field(default_factory=datetime.utcnow)