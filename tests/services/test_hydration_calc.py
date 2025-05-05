import pytest
from datetime import datetime
from app.services.hydration_calc import calculate_required_water
from app.database import get_mongodb


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

@pytest.mark.parametrize("user_id", ["testuser_calc"])
def test_calculate_required_water(user_id, db):
    insert_test_profile(user_id, db)
    insert_test_location(user_id, db)
    required = calculate_required_water(user_id)
    assert required > 0