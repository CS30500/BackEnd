import pytest
from datetime import datetime
from app.services.alert import assess_water_risk
from app.database import get_mongodb


def insert_test_bottle_temp(user_id, db):
    db.bottle_temperatures.insert_one({
        "user_id": user_id,
        "temperature_c": 42.0,
        "timestamp": datetime.utcnow()
    })

@pytest.mark.parametrize("user_id", ["testuser_alert"])
def test_assess_water_risk(user_id, db):
    insert_test_bottle_temp(user_id, db)
    risk = assess_water_risk(user_id)
    assert risk in ["안전", "주의", "고위험"]