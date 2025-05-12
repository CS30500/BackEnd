import pytest
from datetime import datetime
from app.services.alert import assess_water_risk

def insert_test_bottle_temp(user_id: str, temp: float, db):
    db.bottle_temperatures.insert_one({
        "user_id": user_id,
        "temperature_c": temp,
        "timestamp": datetime.utcnow()
    })

@pytest.mark.parametrize("temp, expected", [
    (28.0, "안전")
])
def test_assess_water_risk(temp, expected, db):
    user_id = "testuser_alert"
    # 준비
    insert_test_bottle_temp(user_id, temp, db)

    # 테스트
    risk = assess_water_risk(user_id, db)
    assert risk == expected