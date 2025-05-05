from fastapi import APIRouter, Depends
from app.auth_utils import verify_token
from app.database import get_mongodb
from app.models.location import UserLocation, LocationTemperature

router = APIRouter()
db = get_mongodb()

@router.post("/")
def log_user_location(loc: UserLocation, user=Depends(verify_token)):
    data = loc.model_dump()
    data["user_id"] = user["user_id"]
    db.user_locations.insert_one(data)
    return {"message": "위치 기록 완료"}



@router.post("/temperature")
def log_external_temperature(temp: LocationTemperature):
    db.location_temperatures.insert_one(temp.model_dump())
    return {"message": "외부 온도 기록 완료"}