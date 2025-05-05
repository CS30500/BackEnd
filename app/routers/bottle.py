from fastapi import APIRouter, Depends
from datetime import datetime
from app.auth_utils import verify_token
from app.database import get_mongodb
from app.models.bottle import BottleTemperature

router = APIRouter()
db = get_mongodb()

@router.post("/")
def log_bottle_temperature(temp: BottleTemperature, user=Depends(verify_token)):
    data = temp.model_dump()
    data["user_id"] = user["user_id"]
    db.bottle_temperatures.insert_one(data)
    return {"message": "물병 온도 기록 완료"}