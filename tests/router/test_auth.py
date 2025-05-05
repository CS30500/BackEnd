def test_register(client, make_unique_user):
    """회원가입 테스트"""

    TEST_USER = make_unique_user()
    # 회원가입 요청
    response = client.post("/auth/register", json=TEST_USER)
    assert response.status_code == 200
    assert response.json()["message"] == "회원가입 성공"
    
    # 중복 회원가입 시도
    response = client.post("/auth/register", json=TEST_USER)
    assert response.status_code == 400
    assert "이미 존재하는 아이디" in response.json()["detail"]



def test_login(client, make_unique_user):
    """로그인 테스트"""
    # 로그인 요청
    TEST_USER = make_unique_user()
    login_data = {
        "user_id": TEST_USER["user_id"],
        "password": TEST_USER["password"],
        "password_check": TEST_USER["password_check"]
    }
    response = client.post("/auth/register", json=TEST_USER)
    assert response.status_code == 200
    assert response.json()["message"] == "회원가입 성공"
    
    response = client.post("/auth/login", json=TEST_USER)
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    # 잘못된 비밀번호로 로그인 시도
    wrong_login_data = {
        "user_id": TEST_USER["user_id"],
        "password": "wrong_password"
    }
    response = client.post("/auth/login", json=wrong_login_data)
    assert response.status_code == 401
    assert "비밀번호가 일치하지 않습니다" in response.json()["detail"]
    
    # 존재하지 않는 아이디로 로그인 시도
    wrong_login_data = {
        "user_id": "non_existent_user",
        "password": "password"
    }
    response = client.post("/auth/login", json=wrong_login_data)
    assert response.status_code == 404
    assert "존재하지 않는 아이디" in response.json()["detail"]
