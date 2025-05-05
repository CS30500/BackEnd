from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel, Field
from app.database import get_mongodb
from app.auth_utils import verify_token
from app.models.water_log import WaterLog, DailyTarget, HydrationSummary

router = APIRouter()
db = get_mongodb()




def get_all_dates_in_month(year: int, month: int):
    first_day = datetime(year, month, 1)
    dates = []
    current = first_day
    while current.month == month:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return dates

@router.post("/log")
def add_water_log(amount: float = Query(..., gt=0), user=Depends(verify_token)):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    log = WaterLog(user_id=user["user_id"], amount_ml=amount, date=today)
    db.water_logs.insert_one(log.model_dump())
    return {"message": "음수량이 기록되었습니다."}

@router.post("/target")
def set_daily_target(target_ml: float = Query(..., gt=0), user=Depends(verify_token)):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    target = DailyTarget(user_id=user["user_id"], target_ml=target_ml, date=today)
    db.daily_targets.insert_one(target.model_dump())
    return {"message": "목표 섭취량이 설정되었습니다."}

@router.get("/today", response_model=HydrationSummary)
def get_today_summary(user=Depends(verify_token)):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    start = datetime.strptime(today, "%Y-%m-%d")
    end = start + timedelta(days=1)

    total = db.water_logs.aggregate([
        {"$match": {
            "user_id": user["user_id"],
            "timestamp": {"$gte": start, "$lt": end}
        }},
        {"$group": {"_id": None, "total": {"$sum": "$amount_ml"}}}
    ])
    total_ml = next(total, {}).get("total", 0)

    latest_target = db.daily_targets.find_one(
        {"user_id": user["user_id"], "date": today},
        sort=[("timestamp", -1)]
    )
    target_ml = latest_target["target_ml"] if latest_target else 2000.0

    return HydrationSummary(date=today, total_intake_ml=total_ml, target_ml=target_ml)

@router.get("/monthly", response_model=List[HydrationSummary])
def get_monthly_summary(user=Depends(verify_token)):
    today = datetime.utcnow()
    start = datetime(today.year, today.month, 1)
    end = (start + timedelta(days=32)).replace(day=1)

    # 하루 단위 합산
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
    results = list(db.water_logs.aggregate(pipeline))
    intake_map = {r["_id"]: r["total"] for r in results}

    # 하루 단위 목표
    targets = db.daily_targets.find({
        "user_id": user["user_id"],
        "date": {"$gte": start.strftime("%Y-%m-%d"), "$lt": end.strftime("%Y-%m-%d")}
    })
    target_map = {}
    for t in targets:
        d = t["date"]
        if d not in target_map or t["timestamp"] > target_map[d]["timestamp"]:
            target_map[d] = t

    today = datetime.utcnow()
    year, month = today.year, today.month
    all_dates = get_all_dates_in_month(year, month)
    res = [
        HydrationSummary(
            date=d,
            total_intake_ml=intake_map.get(d, 0),
            target_ml=target_map.get(d, {}).get("target_ml", 2000.0)
        )
        for d in all_dates
    ]
    # print(res)
    return res