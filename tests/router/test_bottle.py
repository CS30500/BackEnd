from app.auth_utils import create_token

def test_log_bottle_temperature_success(client, db):
    db.users.insert_one({
        "user_id": "testuser_bottle",
        "password": "dummy"
    })
    token = create_token({"user_id": "testuser_bottle"})

    res = client.post("/bottle", json={"temperature_c": 12.5}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["message"] == "물병 온도 기록 완료"