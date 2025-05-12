from datetime import datetime, timedelta
from pymongo.database import Database

def should_notify(user_id: str, db: Database, now: datetime = None) -> bool:
    now = now or datetime.utcnow()
    today_str = now.strftime("%Y-%m-%d")
    start = datetime.strptime(today_str, "%Y-%m-%d")
    end = start + timedelta(days=1)

    logs = db.water_logs.aggregate([
        {"$match": {"user_id": user_id, "timestamp": {"$gte": start, "$lt": end}}},
        {"$group": {"_id": None, "total": {"$sum": "$amount_ml"}}}
    ])
    intake_ml = next(logs, {}).get("total", 0)

    target_doc = db.daily_targets.find_one(
        {"user_id": user_id, "date": today_str},
        sort=[("timestamp", -1)]
    )
    target_ml = target_doc["target_ml"] if target_doc else 2000.0

    hours_passed = now.hour + now.minute / 60
    expected_ratio = hours_passed / 24
    actual_ratio = intake_ml / target_ml if target_ml else 0

    return actual_ratio < expected_ratio