import pytest
from datetime import datetime
from app.services.hydration_calc import calculate_required_water

def insert_test_profile(user_id, db):
    db.users.insert_one({
        "user_id": user_id,
        "weight": 60,
        "height": 170,
        "sex": "M",
        "age": 25
    })

def insert_test_location(user_id, db):
    db.user_locations.insert_one({
        "user_id": user_id,
        "latitude": 37.56,
        "longitude": 126.97,
        "timestamp": datetime.utcnow()
    })
    db.location_temperatures.insert_one({
        "latitude": 37.56,
        "longitude": 126.97,
        "temperature_c": 34.0,
        "source": "test",
        "timestamp": datetime.utcnow()
    })

@pytest.mark.parametrize("user_id, weight, temp, expected", [
    ("testuser_calc", 60, 34.0, 60 * 30 * 1.2),
])
def test_calculate_required_water(user_id, weight, temp, expected, db):
    # 준비
    db.users.insert_one({
        "user_id": user_id,
        "weight": weight,
        "height": 170,
        "sex": "M",
        "age": 25
    })
    db.user_locations.insert_one({
        "user_id": user_id,
        "latitude": 37.56,
        "longitude": 126.97,
        "timestamp": datetime.utcnow()
    })
    db.location_temperatures.insert_one({
        "latitude": 37.56,
        "longitude": 126.97,
        "temperature_c": temp,
        "source": "test",
        "timestamp": datetime.utcnow()
    })

    # 실행
    result = calculate_required_water(user_id, db=db)

    # 검증
    assert round(result, 1) == round(expected, 1)