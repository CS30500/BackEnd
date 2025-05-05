def test_log_activity(client, make_unique_user):
    user = make_unique_user()
    client.post("/auth/register", json=user)
    token = client.post("/auth/login", json={"user_id": user["user_id"], "password": user["password"]}).json()["access_token"]
    res = client.post("/activity", json={"steps": 3500, "calories": 120.5}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["message"] == "운동 기록 저장 완료"