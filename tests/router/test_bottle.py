def test_log_bottle_temperature(client, make_unique_user):
    user = make_unique_user()
    client.post("/auth/register", json=user)
    token = client.post("/auth/login", json={"user_id": user["user_id"], "password": user["password"]}).json()["access_token"]
    res = client.post("/bottle", json={"temperature_c": 12.5}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["message"] == "물병 온도 기록 완료"