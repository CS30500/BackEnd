from fastapi import APIRouter, Depends
from pymongo.database import Database
from app.auth_utils import verify_token
from app.database import get_mongodb
from app.models.location import UserLocation, LocationTemperature
from datetime import datetime

router = APIRouter(prefix="/location", tags=["Location"])

@router.post("/")
def log_user_location(
    loc: UserLocation,
    user: dict = Depends(verify_token),
    db: Database = Depends(get_mongodb)
) -> dict:
    data = loc.model_dump()
    data["user_id"] = user["user_id"]
    data["timestamp"] = datetime.utcnow()  # ✅ 위치기록 시간
    db.user_locations.insert_one(data)
    return {"message": "위치 기록 완료"}

@router.post("/temperature")
def log_external_temperature(
    temp: LocationTemperature,
    db: Database = Depends(get_mongodb)
) -> dict:
    data = temp.model_dump()
    data["timestamp"] = datetime.utcnow()  # ✅ 외부 온도 기록 시간
    db.location_temperatures.insert_one(data)
    return {"message": "외부 온도 기록 완료"}