from datetime import datetime

def test_log_user_location(client, make_unique_user):
    user = make_unique_user()
    client.post("/auth/register", json=user)
    token = client.post("/auth/login", json={"user_id": user["user_id"], "password": user["password"]}).json()["access_token"]
    res = client.post("/location", json={"latitude": 37.56, "longitude": 126.97}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["message"] == "위치 기록 완료"

def test_log_location_temperature(client):
    res = client.post("/location/temperature", json={
        "latitude": 37.56,
        "longitude": 126.97,
        "temperature_c": 24.1,
        "source": "openweather",
        "timestamp": datetime.utcnow().isoformat()
    })
    assert res.status_code == 200
    assert res.json()["message"] == "외부 온도 기록 완료"