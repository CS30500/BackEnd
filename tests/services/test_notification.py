import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from app.services.notification import run_hydration_alerts

@pytest.fixture
def setup_alert_conditions(db):
    user_id = "test_alert_user"
    now = datetime.utcnow().replace(hour=7, minute=30, second=0, microsecond=0)

    today_str = now.strftime("%Y-%m-%d")

    # 🔄 초기화
    db.fcm_tokens.delete_many({"user_id": user_id})
    db.water_logs.delete_many({"user_id": user_id})
    db.daily_targets.delete_many({"user_id": user_id})
    db.user_profiles.delete_many({"user_id": user_id})
    db.activity_logs.delete_many({"user_id": user_id})
    db.weather_forecast.delete_many({"user_id": user_id})
    db.bottle_temperatures.delete_many({"user_id": user_id})
    db.alert_logs.delete_many({"user_id": user_id})  # 🔥 중요

    # 1. FCM 토큰
    db.fcm_tokens.insert_one({"user_id": user_id, "token": "dummy_token"})

    # 2. 음수 로그 (300분 전)
    db.water_logs.insert_one({
        "user_id": user_id,
        "timestamp": now - timedelta(minutes=300),
        "amount_ml": 0
    })

    # 3. 일일 목표 미달성
    db.daily_targets.insert_one({
        "user_id": user_id,
        "date": today_str,
        "target_ml": 3000,
        "achieved": False,
        "timestamp": now
    })

    # 4. 유저 프로필
    db.user_profiles.insert_one({
        "user_id": user_id,
        "wake_time": "07:00",
        "active_hours": 12
    })

    # 5. 활동 로그
    db.activity_logs.insert_one({
        "user_id": user_id,
        "timestamp": now - timedelta(minutes=5),
        "calories": 100
    })

    # 6. 날씨 예보
    db.weather_forecast.insert_one({
        "user_id": user_id,
        "date": today_str,
        "high_temp": 34.0
    })

    # 7. 물병 온도
    db.bottle_temperatures.insert_one({
        "user_id": user_id,
        "temperature": 38.0,
        "timestamp": now
    })

    return user_id, now


@patch("app.services.notification.messaging.send")
def test_run_hydration_alerts_all_conditions(mock_send, db, setup_alert_conditions):
    user_id, now = setup_alert_conditions

    mock_send.return_value = "fcm_response_dummy"

    results = run_hydration_alerts(user_id, db, now)

    assert isinstance(results, list)
    assert len(results) == 6  # 6개의 알림 조건
    for r in results:
        assert "message" in r
        assert r["message"] in ["알림 전송됨", "FCM 토큰 없음", "최근에 전송된 알림 → 생략"]
        assert "title" in r

    # 🔍 추가 검증: alert_logs에 기록이 남았는지 확인
    assert db.alert_logs.count_documents({"user_id": user_id}) == 6