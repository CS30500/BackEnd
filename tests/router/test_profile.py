def test_profile_registration_and_retrieval(client, make_unique_user):
    TEST_USER = make_unique_user()
    
    # 회원가입
    res = client.post("/auth/register", json=TEST_USER)
    assert res.status_code == 200

    # 로그인 → 토큰 획득
    login_data = {
        "user_id": TEST_USER["user_id"],
        "password": TEST_USER["password"]
    }
    res = client.post("/auth/login", json=login_data)
    assert res.status_code == 200
    token = res.json()["access_token"]

    # 프로필 등록
    profile_data = {
        "sex": "F",
        "age": 30,
        "height": 165.0,
        "weight": 55.5
    }
    res = client.post("/profile", json=profile_data, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["message"] == "프로필 등록 성공"

    # 프로필 조회
    res = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    returned = res.json()
    assert returned["user_id"] == TEST_USER["user_id"]
    assert returned["sex"] == "F"
    assert returned["age"] == 30
    assert returned["height"] == 165.0
    assert returned["weight"] == 55.5