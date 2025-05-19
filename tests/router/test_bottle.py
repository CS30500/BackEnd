from app.auth_utils import create_token
from datetime import datetime

def test_log_bottle_temperature_success(client, db):
    db.users.insert_one({
        "user_id": "testuser_bottle",
        "password": "dummy"
    })
    token = create_token({"user_id": "testuser_bottle"})

    res = client.post("/bottle", json={"temperature_c": 12.5}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["message"] == "물병 온도 기록 완료"

def test_get_latest_bottle_temperature(client, db):
    user_id = "test_bottle_user"
    db.users.insert_one({"user_id": user_id, "password": "dummy"})
    token = create_token({"user_id": user_id})

    # 기록 삽입
    db.bottle_temperatures.insert_one({
        "user_id": user_id,
        "temperature": 20.5,
        "timestamp": datetime.utcnow()
    })

    res = client.get(
        "/bottle/temperature",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 200
    data = res.json()
    assert data["temperature"] == 20.5
    assert data["user_id"] == user_id