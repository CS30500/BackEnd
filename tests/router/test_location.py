from app.auth_utils import create_token
from app.auth_utils import create_token
from unittest.mock import patch, AsyncMock

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
    data = res.json()
    assert data["message"] == "위치 및 날씨 저장 완료"
    assert isinstance(data["temperature"], (int, float))  # 온도 응답 존재 여부 확인

def test_get_external_humidity(client, db):
    user_id = "real_humidity_user"
    db.users.insert_one({"user_id": user_id, "password": "dummy"})
    token = create_token({"user_id": user_id})

    res = client.post(
        "/location/humidity",
        json={"latitude": 37.56, "longitude": 126.97},  # ✅ body에 좌표 전달
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 200
    data = res.json()
    assert isinstance(data["humidity"], int)
    assert data["user_id"] == user_id


def test_get_external_temperature(client, db):
    user_id = "real_temp_user"
    db.users.insert_one({"user_id": user_id, "password": "dummy"})
    token = create_token({"user_id": user_id})

    res = client.post(
        "/location/temperature",
        json={"latitude": 37.56, "longitude": 126.97},  # ✅ body에 좌표 전달
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 200
    data = res.json()
    assert isinstance(data["temperature"], (int, float))
    assert data["user_id"] == user_id
