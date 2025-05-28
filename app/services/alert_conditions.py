from datetime import datetime, timedelta
from pymongo.database import Database
import math


# 1. 마지막 음수 시점 기준 N분 경과 (단, 목표 달성 시 2배)
def should_alert_inactivity(user_id: str, db: Database, now: datetime = None, threshold_min: int = 120) -> bool:
    now = now or datetime.utcnow()
    last_log = db.water_logs.find_one(
        {"user_id": user_id}, sort=[("timestamp", -1)]
    )
    if not last_log:
        return True  # 아직 마신 적 없음

    last_time = last_log["timestamp"]

    # 오늘 목표 채웠는지 확인
    today = now.strftime("%Y-%m-%d")
    target_doc = db.daily_targets.find_one({"user_id": user_id, "date": today})
    goal_met = target_doc and target_doc.get("achieved", False)

    max_elapsed = threshold_min * (2 if goal_met else 1)
    elapsed = (now - last_time).total_seconds() / 60
    return elapsed >= max_elapsed


# 2. 기상 후 30분 뒤 안내 메시지

def should_alert_morning_target(user_id: str, db: Database, now: datetime = None) -> bool:
    now = now or datetime.utcnow()
    wake_doc = db.user_profiles.find_one({"user_id": user_id})
    if not wake_doc or "wake_time" not in wake_doc:
        return False

    wake_time = datetime.strptime(now.strftime("%Y-%m-%d") + " " + wake_doc["wake_time"], "%Y-%m-%d %H:%M")
    alert_time = wake_time + timedelta(minutes=30)
    return wake_time <= now <= alert_time + timedelta(minutes=5)  # 여유 5분


# 3. 최근 10분간 칼로리 소비

def should_alert_high_activity(user_id: str, db: Database, now: datetime = None, kcal_threshold: float = 50.0) -> bool:
    now = now or datetime.utcnow()
    recent_activities = db.activity_logs.aggregate([
        {"$match": {
            "user_id": user_id,
            "timestamp": {"$gte": now - timedelta(minutes=10)}
        }},
        {"$group": {"_id": None, "total_kcal": {"$sum": "$calories"}}}
    ])
    total_kcal = next(recent_activities, {}).get("total_kcal", 0)
    return total_kcal >= kcal_threshold


# 4. 아침 시간대 (예: 오전 6~8시)에 오늘 최고기온 경고

def should_alert_high_temp_morning(user_id: str, db: Database, now: datetime = None, temp_threshold: float = 33.0) -> bool:
    now = now or datetime.utcnow()
    if not (6 <= now.hour <= 8):
        return False

    temp = db.weather_forecast.find_one({
        "user_id": user_id,
        "date": now.strftime("%Y-%m-%d")
    })
    return temp and temp.get("high_temp", 0) >= temp_threshold


# 5. 남은 물 섭취 속도가 비정상적으로 높은 경우

def should_alert_urgent_rate(user_id: str, db: Database, now: datetime = None) -> bool:
    now = now or datetime.utcnow()
    today = now.strftime("%Y-%m-%d")

    target_doc = db.daily_targets.find_one({"user_id": user_id, "date": today})
    target_ml = target_doc.get("target_ml", 2000.0) if target_doc else 2000.0

    logs = db.water_logs.aggregate([
        {"$match": {"user_id": user_id, "timestamp": {"$gte": datetime.strptime(today, "%Y-%m-%d")}}},
        {"$group": {"_id": None, "total": {"$sum": "$amount_ml"}}}
    ])
    consumed = next(logs, {}).get("total", 0)

    profile = db.user_profiles.find_one({"user_id": user_id}) or {}
    active_hours = profile.get("active_hours", 20)  # 하루 활동시간 (예: 20시간)

    start_time = datetime.strptime(today, "%Y-%m-%d")
    end_time = start_time + timedelta(hours=active_hours)
    remaining_time = (end_time - now).total_seconds() / 3600
    remaining_ml = target_ml - consumed

    if remaining_time <= 0:
        return False

    ml_per_hour = remaining_ml / remaining_time
    average_rate = target_ml / active_hours

    return ml_per_hour >= average_rate * 2


def should_alert_water_status(user_id: str, db: Database, now: datetime = None) -> bool:
    now = now or datetime.utcnow()

    drink = db.water_logs.find_one(
        {"user_id": user_id},
        sort=[("timestamp", -1)]
    )
    if not drink:
        return False  # ✔️ 문자열 대신 불리언 반환

    drink_time = drink["timestamp"]

    bottle = db.bottle_temperatures.find_one(
        {"user_id": user_id},
        sort=[("timestamp", -1)]
    )
    if not bottle:
        return False  # ✔️ 문자열 대신 불리언 반환

    temp = float(bottle["temperature"])

    base_hours = 3
    base_temp = 20
    delta = max(0, temp - base_temp)
    speed_multiplier = math.pow(1.01, delta)
    adjusted_minutes = (base_hours * 60) / speed_multiplier

    elapsed_minutes = (now - drink_time).total_seconds() / 60

    return elapsed_minutes >= adjusted_minutes  # ✔️ 불필요한 삼항 제거