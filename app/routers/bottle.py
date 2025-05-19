from fastapi import APIRouter, Depends
from datetime import datetime
from app.auth_utils import verify_token
from app.database import get_mongodb
from app.models.bottle import BottleTemperature
from pymongo.database import Database

router = APIRouter(prefix="/bottle", tags=["Bottle"])

@router.post("/")
def log_bottle_temperature(
    temp: BottleTemperature,
    user: dict = Depends(verify_token),
    db: Database = Depends(get_mongodb)
) -> dict:
    data = temp.model_dump()
    data["user_id"] = user["user_id"]
    data["timestamp"] = datetime.utcnow()  # ✅ 자동 기록
    db.bottle_temperatures.insert_one(data)
    return {"message": "물병 온도 기록 완료"}

@router.get("/temperature")
def get_latest_bottle_temperature(
    user: dict = Depends(verify_token),
    db: Database = Depends(get_mongodb)
):
    latest = db.bottle_temperatures.find_one(
        {"user_id": user["user_id"]},
        sort=[("timestamp", -1)]
    )

    if not latest:
        return {"message": "기록 없음", "temperature": None}

    return {
        "user_id": user["user_id"],
        "temperature": latest["temperature"],
        "timestamp": latest["timestamp"]
    }