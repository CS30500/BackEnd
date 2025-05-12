def test_login_success(client, make_unique_user):
    user = make_unique_user()
    client.post("/auth/register", json=user)
    response = client.post("/auth/login", json={
        "user_id": user["user_id"],
        "password": user["password"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client, make_unique_user):
    user = make_unique_user()
    client.post("/auth/register", json=user)
    response = client.post("/auth/login", json={
        "user_id": user["user_id"],
        "password": "wrong_password"
    })
    assert response.status_code == 401
    assert "비밀번호가 일치하지 않습니다" in response.json()["detail"]


def test_login_nonexistent_user(client):
    response = client.post("/auth/login", json={
        "user_id": "nonexistent_user",
        "password": "some_password"
    })
    assert response.status_code == 404
    assert "존재하지 않는 아이디" in response.json()["detail"]