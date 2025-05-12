from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel, Field
from app.database import get_mongodb
from app.auth_utils import verify_token
from app.models.water_log import WaterLog, DailyTarget, HydrationSummary
from pymongo.database import Database

router = APIRouter(prefix="/hydration", tags=["Hydration"])

def get_all_dates_in_month(year: int, month: int) -> List[str]:
    dates = []
    current = datetime(year, month, 1)
    while current.month == month:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return dates

@router.post("/log")
def add_water_log(
    amount: float = Query(..., gt=0),
    user=Depends(verify_token),
    db: Database = Depends(get_mongodb)
):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    log = WaterLog(user_id=user["user_id"], amount_ml=amount, date=today)
    db.water_logs.insert_one(log.model_dump())
    return {"message": "음수량이 기록되었습니다."}

@router.post("/target")
def set_daily_target(
    target_ml: float = Query(..., gt=0),
    user=Depends(verify_token),
    db: Database = Depends(get_mongodb)
):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    target = DailyTarget(user_id=user["user_id"], target_ml=target_ml, date=today)
    db.daily_targets.insert_one(target.model_dump())
    return {"message": "목표 섭취량이 설정되었습니다."}

@router.get("/today", response_model=HydrationSummary)
def get_today_summary(
    user=Depends(verify_token),
    db: Database = Depends(get_mongodb)
):
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    start = datetime.strptime(today_str, "%Y-%m-%d")
    end = start + timedelta(days=1)

    total = db.water_logs.aggregate([
        {"$match": {
            "user_id": user["user_id"],
            "timestamp": {"$gte": start, "$lt": end}
        }},
        {"$group": {"_id": None, "total": {"$sum": "$amount_ml"}}}
    ])
    total_ml = next(total, {}).get("total", 0)

    target = db.daily_targets.find_one(
        {"user_id": user["user_id"], "date": today_str},
        sort=[("timestamp", -1)]
    )
    target_ml = target["target_ml"] if target else 2000.0

    return HydrationSummary(date=today_str, total_intake_ml=total_ml, target_ml=target_ml)

@router.get("/monthly", response_model=List[HydrationSummary])
def get_monthly_summary(
    user=Depends(verify_token),
    db: Database = Depends(get_mongodb)
):
    now = datetime.utcnow()
    start = datetime(now.year, now.month, 1)
    end = (start + timedelta(days=32)).replace(day=1)

    # 1. 날짜별 음수량 합산
    pipeline = [
        {"$match": {
            "user_id": user["user_id"],
            "timestamp": {"$gte": start, "$lt": end}
        }},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            "total": {"$sum": "$amount_ml"}
        }}
    ]
    intake_map = {
        doc["_id"]: doc["total"] for doc in db.water_logs.aggregate(pipeline)
    }

    # 2. 하루별 최신 목표
    targets = db.daily_targets.find({
        "user_id": user["user_id"],
        "date": {"$gte": start.strftime("%Y-%m-%d"), "$lt": end.strftime("%Y-%m-%d")}
    })
    target_map = {}
    for t in targets:
        d = t["date"]
        if d not in target_map or t["timestamp"] > target_map[d]["timestamp"]:
            target_map[d] = t

    # 3. 날짜별 정리
    all_dates = get_all_dates_in_month(now.year, now.month)
    result = [
        HydrationSummary(
            date=d,
            total_intake_ml=intake_map.get(d, 0),
            target_ml=target_map.get(d, {}).get("target_ml", 2000.0)
        )
        for d in all_dates
    ]
    return result