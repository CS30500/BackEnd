import pytest
from datetime import datetime
from app.services.hydration_calc import calculate_required_water

@pytest.mark.parametrize("user_id, weight, temp, expected", [
    ("testuser_calc", 60, 34.0, 3.54),
])
def test_calculate_required_water(user_id, weight, temp, expected, db):
    # 1. 사용자 프로필 삽입
    db.users.insert_one({
        "user_id": user_id,
        "weight": weight,
        "height": 170,
        "sex": "M",
        "age": 25
    })

    # 2. 위치 기록 (안 써도 되지만 일관성 위해)
    db.user_locations.insert_one({
        "user_id": user_id,
        "latitude": 37.56,
        "longitude": 126.97,
        "timestamp": datetime.utcnow()
    })

    # 3. 온도 기록 (user_id 기준)
    db.location_temperatures.insert_one({
        "user_id": user_id,  # ✅ 핵심 수정
        "temperature": temp,
        "timestamp": datetime.utcnow()
    })

    # 4. 계산 실행
    result = calculate_required_water(user_id, db=db)

    # 5. 검증
    assert round(result, 1) == round(expected, 1)