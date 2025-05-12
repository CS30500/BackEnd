from app.auth_utils import create_token

def test_log_user_location(client, db):
    # 사용자 직접 삽입
    user_id = "testuser_location"
    db.users.insert_one({"user_id": user_id, "password": "dummy"})

    # 토큰 생성
    token = create_token({"user_id": user_id})

    # 위치 기록 요청
    res = client.post("/location", json={
        "latitude": 37.56,
        "longitude": 126.97
    }, headers={"Authorization": f"Bearer {token}"})

    # 검증
    assert res.status_code == 200
    assert res.json()["message"] == "위치 기록 완료"

def test_log_location_temperature(client):
    res = client.post("/location/temperature", json={
        "latitude": 37.56,
        "longitude": 126.97,
        "temperature_c": 24.1,
        "source": "openweather"
        # timestamp 생략해도 모델에서 자동 생성됨
    })

    assert res.status_code == 200
    assert res.json()["message"] == "외부 온도 기록 완료"
