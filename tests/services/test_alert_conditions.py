import pytest
from datetime import datetime, timedelta
from app.services.alert_conditions import *

# 1. inactivity
@pytest.mark.parametrize("drink_min_ago, goal_met, expect", [
    (30, False, False),    # 아직 기준 안됨
    (130, False, True),    # 기준 넘음
    (200, True, False),    # 목표 달성 시 240분 기준 → 200이면 아직 X
    (250, True, True),     # 목표 달성 + 충분히 경과
])
def test_should_alert_inactivity(db, drink_min_ago, goal_met, expect):
    user_id = "test_inactivity"
    now = datetime.utcnow()

    db.water_logs.delete_many({"user_id": user_id})
    db.daily_targets.delete_many({"user_id": user_id})

    db.water_logs.insert_one({
        "user_id": user_id,
        "timestamp": now - timedelta(minutes=drink_min_ago)
    })
    db.daily_targets.insert_one({
        "user_id": user_id,
        "date": now.strftime("%Y-%m-%d"),
        "achieved": goal_met
    })

    assert should_alert_inactivity(user_id, db, now) == expect


# 2. morning target
def test_should_alert_morning_target(db):
    user_id = "test_morning"
    now = datetime.utcnow().replace(hour=7, minute=31)
    wake_time = (now - timedelta(minutes=31)).strftime("%H:%M")

    db.user_profiles.delete_many({"user_id": user_id})
    db.user_profiles.insert_one({
        "user_id": user_id,
        "wake_time": wake_time
    })

    assert should_alert_morning_target(user_id, db, now)


# 3. high activity
def test_should_alert_high_activity(db):
    user_id = "test_activity"
    db.activity_logs.delete_many({"user_id": user_id})

    db.activity_logs.insert_one({
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        "calories": 55
    })

    assert should_alert_high_activity(user_id, db)


# 4. high temp morning
def test_should_alert_high_temp_morning(db):
    user_id = "test_temp"
    now = datetime.utcnow().replace(hour=7, minute=0)
    date_str = now.strftime("%Y-%m-%d")

    db.weather_forecast.delete_many({"user_id": user_id})
    db.weather_forecast.insert_one({
        "user_id": user_id,
        "date": date_str,
        "high_temp": 34.0
    })

    assert should_alert_high_temp_morning(user_id, db, now)


# 5. urgent rate
def test_should_alert_urgent_rate(db):
    user_id = "test_urgent"
    now = datetime.utcnow().replace(hour=17)
    today = now.strftime("%Y-%m-%d")

    db.daily_targets.delete_many({"user_id": user_id})
    db.user_profiles.delete_many({"user_id": user_id})
    db.water_logs.delete_many({"user_id": user_id})

    db.daily_targets.insert_one({
        "user_id": user_id,
        "date": today,
        "target_ml": 2000
    })

    db.user_profiles.insert_one({
        "user_id": user_id,
        "active_hours": 20
    })

    db.water_logs.insert_one({
        "user_id": user_id,
        "amount_ml": 1000,
        "timestamp": now - timedelta(hours=15)
    })

    assert should_alert_urgent_rate(user_id, db, now)


# 6. water status
@pytest.mark.parametrize("drink_min_ago, temp, expect", [
    (30, 25, False),     # 정상
    (160, 25, False),     # 오래됨
    (60, 40, False),      # 온도 높음
])
def test_should_alert_water_status(db, drink_min_ago, temp, expect):
    user_id = "test_water_status"
    now = datetime.utcnow()

    db.water_logs.delete_many({"user_id": user_id})
    db.bottle_temperatures.delete_many({"user_id": user_id})

    db.water_logs.insert_one({
        "user_id": user_id,
        "timestamp": now - timedelta(minutes=drink_min_ago)
    })
    db.bottle_temperatures.insert_one({
        "user_id": user_id,
        "temperature": temp,
        "timestamp": now
    })

    assert should_alert_water_status(user_id, db, now) == expect