def test_login_success(client, make_user_in_db):
    user = make_user_in_db("testuser1")
    response = client.post("/auth/login", json=user)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client, make_user_in_db):
    user = make_user_in_db("testuser2", password="correct_pw")
    response = client.post("/auth/login", json={
        "user_id": user["user_id"],
        "password": "wrong_pw"
    })
    assert response.status_code == 401
    assert "비밀번호가 일치하지 않습니다" in response.json()["detail"]


def test_login_nonexistent_user(client):
    response = client.post("/auth/login", json={
        "user_id": "ghost_user",
        "password": "any"
    })
    assert response.status_code == 404
    assert "존재하지 않는 아이디" in response.json()["detail"]

def test_token_verify_success(client, db):
    # 1. 테스트 유저 생성
    user_id = "verify_user"
    db.users.insert_one({"user_id": user_id, "password": "dummy"})

    # 2. 토큰 발급
    from app.auth_utils import create_token
    token = create_token({"user_id": user_id})

    # 3. 검증 요청
    res = client.get(
        "/auth/verify",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 4. 결과 확인
    assert res.status_code == 200
    data = res.json()
    assert data["message"] == "토큰이 유효합니다."
    assert data["user_id"] == user_id


def test_token_verify_fail(client):
    # 잘못된 토큰 사용
    res = client.get(
        "/auth/verify",
        headers={"Authorization": "Bearer invalid.token.value"}
    )

    assert res.status_code == 401  # 인증 실패