import pytest
from datetime import datetime
from app.services.notification import should_notify
from app.database import get_mongodb


def insert_test_target_and_logs(user_id, db):
    now = datetime.utcnow()
    today_str = now.strftime("%Y-%m-%d")
    db.daily_targets.insert_one({
        "user_id": user_id,
        "date": today_str,
        "target_ml": 2000.0,
        "timestamp": now
    })
    db.water_logs.insert_many([
        {"user_id": user_id, "amount_ml": 300.0, "timestamp": now},
        {"user_id": user_id, "amount_ml": 500.0, "timestamp": now}
    ])

@pytest.mark.parametrize("user_id", ["testuser_notify"])
def test_should_notify(user_id, db):
    insert_test_target_and_logs(user_id, db)
    result = should_notify(user_id)
    assert isinstance(result, bool)