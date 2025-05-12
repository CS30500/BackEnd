import pytest
from datetime import datetime, timedelta
from app.services.notification import should_notify

def insert_test_target_and_logs(user_id, db, intake_ml=800.0, target_ml=2000.0, now: datetime = None):
    now = now or datetime.utcnow().replace(hour=18, minute=0, second=0, microsecond=0)
    today_str = now.strftime("%Y-%m-%d")

    db.daily_targets.insert_one({
        "user_id": user_id,
        "date": today_str,
        "target_ml": target_ml,
        "timestamp": now
    })

    db.water_logs.insert_one({
        "user_id": user_id,
        "amount_ml": intake_ml,
        "timestamp": now
    })

    return now  # 테스트 시간 리턴 (비율 계산 검증용)

@pytest.mark.parametrize("user_id, intake_ml, target_ml, expected", [
    ("testuser_notify_1", 800.0, 2000.0, True),
    ("testuser_notify_2", 1800.0, 2000.0, False),
])
def test_should_notify(user_id, intake_ml, target_ml, expected, db):
    fixed_time = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
    insert_test_target_and_logs(user_id, db, intake_ml, target_ml, now=fixed_time)
    result = should_notify(user_id, db=db, now = fixed_time)
    assert result == expected